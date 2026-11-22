#!/usr/bin/env python3
"""Measure when each lyric line is sung.

Runs Whisper (small, multilingual, via sherpa-onnx) over overlapping 15 s windows of the vocal stem,
then clusters the segment start times across windows. The medians are what LYR_RAW in src/game.js uses.

Setup:
  pip install sherpa-onnx numpy
  curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2
  tar xjf sherpa-onnx-whisper-small.tar.bz2
Usage:
  python3 whisper_windows.py <vocal.wav> <model-dir>
"""
import json, subprocess, sys
import numpy as np, sherpa_onnx

wav, mdir = sys.argv[1], sys.argv[2].rstrip('/') + '/'
raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=mdir + 'small-encoder.int8.onnx', decoder=mdir + 'small-decoder.int8.onnx',
                                                 tokens=mdir + 'small-tokens.txt', language='no', enable_segment_timestamps=True)
dur = len(x) / 16000
segs = []
for a in np.arange(12, dur - 5, 2.5):
    b = min(a + 15, dur)
    s = rec.create_stream(); s.accept_waveform(16000, x[int(a * 16000):int(b * 16000)]); rec.decode_stream(s); r = s.result
    for t, txt in zip(r.segment_timestamps, r.segment_texts):
        if t > 0.2 and b - (a + t) > 1.5:          # skip segments cut by the window edges
            segs.append((float(a + t), txt.strip()))
segs.sort()
clusters = []
for s in segs:
    if clusters and s[0] - clusters[-1][-1][0] < 0.7: clusters[-1].append(s)
    else: clusters.append([s])
out = [{'t': round(float(np.median([c[0] for c in cl])), 2), 'n': len(cl), 'text': cl[len(cl) // 2][1]} for cl in clusters]
for o in out: print(f"{o['t']:7.2f}  n={o['n']:2d}  {o['text']}")
json.dump(out, open('line_starts.json', 'w'), ensure_ascii=False, indent=1)
