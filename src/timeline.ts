// The song's story beats: sections, lyric lines, banners and special moments.
import { BAR, FINAL_HIT, PH, W, barAt, barT } from './config';

export type SceneName = 'station' | 'glitch' | 'neon' | 'map' | 'map2' | 'chaos' | 'boss';

export interface Section {
  id: string;
  /** first and last bar (inclusive) */
  a: number;
  b: number;
  scene: SceneName;
  /** scroll speed in px/s */
  speed: number;
}

/** Sections of the backing track (Suno form, 122 BPM). They drive scenes and enemy waves. */
export const SECTIONS: Section[] = [
  { id: 'intro', a: 1, b: 9, scene: 'station', speed: 110 },
  { id: 'verse1', a: 10, b: 25, scene: 'station', speed: 120 },
  { id: 'pre1', a: 26, b: 33, scene: 'glitch', speed: 130 },
  { id: 'chorus1', a: 34, b: 41, scene: 'neon', speed: 165 },
  { id: 'verse2', a: 42, b: 57, scene: 'map', speed: 145 },
  { id: 'pre2', a: 58, b: 65, scene: 'chaos', speed: 175 },
  { id: 'chorus2', a: 66, b: 73, scene: 'chaos', speed: 195 },
  { id: 'inst', a: 74, b: 76, scene: 'boss', speed: 205 },
];

export function sectionAt(t: number): Section {
  const bar = barAt(t);
  for (const s of SECTIONS) if (bar >= s.a && bar <= s.b) return s;
  return bar < 1 ? SECTIONS[0] : SECTIONS[SECTIONS.length - 1];
}

/** Measured start of the sung line that belongs to a bar (seconds). Falls back to the bar grid. */
const LINE_ON: Record<number, number> = {
  42: 80.8, 44: 84.0, 46: 87.85, 48: 91.95, 50: 95.5, 52: 98.0, 54: 100.15, 56: 102.05,
};
export const lineT = (bar: number): number => LINE_ON[bar] ?? barT(bar) - 0.3;

/**
 * «tre blå maskiner»: three ticket machines stand on the platform at Sandvika and roll past with the station.
 * The left one is Automat Victoria. When the girls pass her («Den ene har mitt navn») she gets a face and arms
 * and starts following them.
 */
export const MACHINES_T = barT(12);
/** px/s the station (platform, machines, stopped trains) moves left on screen during verse 1 */
export const STATION_VX = 70;
export const MACHINE_GAP = 24;
/** Screen x of the left edge of the leftmost machine. */
export const machinesX = (t: number): number => W + 40 - (t - MACHINES_T) * STATION_VX;
/** Centre x of platform machine k (0 = Victoria). */
export const machineCenter = (t: number, k = 0): number => machinesX(t) + k * MACHINE_GAP + 9;
export const MACHINE_WIDTH = 18;
export const MACHINE_HEIGHT = 31;
/** Indices of the stationary cabinets still present on the platform. */
export function platformMachines(t: number): number[] {
  if (t <= MACHINES_T || t >= barT(20)) return [];
  return t < VICTORIA_WAKE_T ? [0, 1, 2] : [1, 2];
}
/** Victoria wakes up when the girls reach her (the player's home spot is x = 80). */
export const VICTORIA_WAKE_T = MACHINES_T + (W + 40 + 9 - 80) / STATION_VX;
/** After waking she does a few little hops on the spot (seconds) … */
export const WAKE_HOPS = 0.9;
export const WAKE_HOP_COUNT = 3;
/** … then rises to her floating height, overshooting a little, as she starts to follow (seconds). */
export const WAKE_RISE = 0.9;

export function victoriaLift(t: number): number {
  const since = t - VICTORIA_WAKE_T;
  if (since < WAKE_HOPS) return Math.abs(Math.sin((since / WAKE_HOPS) * Math.PI * WAKE_HOP_COUNT)) * 5;
  const k = Math.min(1, (since - WAKE_HOPS) / WAKE_RISE), c = 3.2;
  return 30 * (1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2);
}
export const victoriaBob = (t: number): number => 2 * Math.min(1, Math.max(0, (t - VICTORIA_WAKE_T - WAKE_HOPS) / WAKE_RISE));

/** «Plutselig er vi ninjaer i et coin-op spill» */
export const NINJA_T = lineT(54);
/** «skjermen skifter farge» – the screen colour change (1:42, set by ear) */
export const COLOR_T = 102.0;
export const isNinja = (t: number): boolean => t >= NINJA_T;

export interface LyricLine {
  /** shown from */
  t: number;
  /** hidden at */
  e: number;
  text: string;
}

/** Show each line this long before the first syllable. */
const LEAD = 0.12;
/**
 * Sung line starts, measured with Whisper over sliding windows of the vocal stem
 * (median of several passes, see tools/timing/whisper_windows.py).
 */
const LYRICS_RAW: [number, string][] = [
  [17.5, 'Sandvika stasjon, det er kaldt i kveld'],
  [20.8, 'tre blå maskiner står og lyser for seg selv'],
  [24.61, "Den ene har mitt navn – jeg tro'kke det er sant"],
  [28.71, 'Automaten min, det er deg og meg i natt!'],
  [31.95, 'Venninnen min hvisker: «Hun er jo helt deg!»'],
  [35.88, 'Jeg tæpper på skjermen, den skriker mot meg'],
  [39.9, 'Et pip. Og et blink. Og et hjerte av stål'],
  [43.4, 'vi snakker gjennom tæpp, vi har satt vårt første mål!'],
  [47.28, 'Vi trykker fort på tekst-til-tale'],
  [50.83, 'a-a-a-automaten hakker, vi er på gli!'],
  [55.11, 'sett inn et kort. nå er. vi klare …'],
  [58.7, 'Den tar oss inn i et spill fra en annen tid'],
  [63.34, 'Ta meg med i Oslostil – (Oslostil, Oslostil)'],
  [67.4, 'tog og bane, hvor jeg vil – (Oslostil, Oslostil)'],
  [71.27, 'du og jeg, helt uten bil – (Oslostil, Oslostil)'],
  [75.07, 'sett inn kort, det blir et spill – Oslostil, Oslostil!'],
  [80.8, 'Ett trykk på et flagg – hun kan visst engelsk'],
  [84.0, '«Choose travellers» – our enemies! Hvem er det vi skal slå?'],
  [87.85, 'hele Oslo på en skjerm, hun viser våre mål'],
  [91.95, 'Vi scroller gjennom byen: hvor skal kampen vår stå?'],
  [95.5, 'Putt kort mot terminalen – et pip og et blink'],
  [98.0, '«Thank you for the purchase» – hun gir oss et wink!'],
  [100.02, 'Plutselig er vi ninjaer i et coin-op spill'],
  [102.05, 'skjermen skifter farge – vi er klar for første kill!'],
  [103.95, 'Hun blinker med lysene: «Kom, følg meg nå!»'],
  [106.0, 'gjennom brennende trikker og busser på skrå'],
  [108.0, 'Den tar oss med inn i et spill fra en annen tid'],
  [110.35, 'sett inn en mynt – vis meg hvor du vil …'],
  [114.5, 'Ta meg med i Oslostil – (Oslostil, Oslostil)'],
  [118.44, 'tog og bane, hvor jeg vil – (Oslostil, Oslostil)'],
  [122.38, 'du og jeg, helt uten bil – (Oslostil, Oslostil)'],
  [126.24, 'sett inn kort, det blir et spill – Oslostil, Oslostil!'],
  [132.1, 'Hey! Hey! Hey! Yeah!'],
  [145.3, 'Ta meg med i Oslo-STIL!'],
];

export const LYRICS: LyricLine[] = LYRICS_RAW.map(([start, text], i) => {
  const next = LYRICS_RAW[i + 1];
  const t = start - LEAD;
  return { t, text, e: next ? Math.min(next[0] - LEAD, t + 5.2) : FINAL_HIT };
});

export const lyricAt = (t: number): LyricLine | undefined => LYRICS.find((l) => t >= l.t && t < l.e);

/** [time, title, subtitle] – bilingual story beats. Only the newest one is shown. */
export type Banner = readonly [number, string, string];
export const BANNERS: Banner[] = [
  [0.3, 'PLAYER ONE', 'TEKST-TIL-TALE ER STARTET'],
  [barT(10) - 0.05, 'LEVEL 1', 'SANDVIKA STASJON'],
  [VICTORIA_WAKE_T + 0.4, 'AUTOMAT VICTORIA', 'AUTOMATEN BLIR MED!'],
  [barT(26) - 0.05, 'LEVEL 2', 'TEKST-TIL-TALE GLITCH'],
  [barT(33) - 0.05, 'INSERT CARD', '▶ ▶ ▶'],
  [barT(34) - 0.05, 'LEVEL 3', 'INN I SPILLET · OSLO NEON'],
  [lineT(42), 'LEVEL 4', 'LANGUAGE CHANGED TO ENGLISH'],
  [lineT(50), 'KORT MOT TERMINALEN', 'PIP! BLINK!'],
  [lineT(52), 'THANK YOU', 'FOR THE PURCHASE! ★★★'],
  [NINJA_T, 'NINJA MODE', 'DERE ER NINJAER!'],
  [barT(58) - 0.05, 'LEVEL 5', 'KOLLEKTIVKAOS'],
  [barT(66) - 0.05, 'FINAL WAVE', 'SISTE BØLGE'],
  [barT(70) - 0.05, 'BOSS', 'KAOS-TRIKKEN!'],
];
export const BANNER_TIME = 2.6;

/** The boss (Kaos-trikken) rolls in at bar 70 and is destroyed by the final hit. */
export const BOSS_AT = barT(70);
export const bossVisible = (t: number): boolean => t >= BOSS_AT && t < FINAL_HIT + 0.05;
export const bossX = (t: number): number => {
  const since = Math.max(0, t - BOSS_AT);
  if (since < BAR) return W + 60 + (256 - W - 60) * (since / BAR);
  return 224 + 32 * Math.cos((since - BAR) * Math.PI / (2 * BAR));
};

/** Debug jump points. */
export const JUMPS: [string, number][] = [
  ['Verse 1', barT(10) - 1.5],
  ['Pre 1', barT(26) - 1],
  ['Chorus 1', barT(34) - 1],
  ['Verse 2', barT(42) - 1],
  ['Terminal', lineT(50) - 1.5],
  ['Ninja', NINJA_T - 2.5],
  ['Farge', COLOR_T - 2.5],
  ['Pre 2', barT(58) - 1],
  ['Chorus 2', barT(66) - 1],
  ['Boss', BOSS_AT - 1],
  ['Finale', FINAL_HIT - 4],
];

export const beatPhase = (t: number, beat: number): number => (((t - PH) / beat) % 1 + 1) % 1;
