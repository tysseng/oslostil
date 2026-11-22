# Oslo-stil – stage design

Nov 22, 2026 · Joakim

> Planning document. Exported from the Claude doc «Oslo-stil – stage design»; if both are edited, keep them in sync.

## Overview

Oslo-stil has 8 stages that follow the song «Oslostil» (122 BPM, 2:27.6) bar by bar, from the bus terminal at Sandvika to the Kaos-trikken boss. Every stage is a section of the backing track: it sets the scene, the scroll speed and the enemy waves, and every enemy reaches the player exactly on a beat.

- **Now** = built and in the game today (`src/timeline.ts`, `src/schedule.ts`, `src/render/scenes.ts`).
- **Proposed** = from `IDEAS.md` or gaps found while writing this; nothing here is decided until Joakim says so.
- Times are song time (m:ss); bars follow the backing track, so vocal beats can sit a little off the bar grid.

## Purpose and how to play

Oslo-stil is a playable music video: the song always plays to the end, and the player's job is to move through it in rhythm and score as high as possible.

**Purpose**

- **A music video you play.** The lyrics are the story, and the gameplay makes you feel the beat.
- **Short and replayable.** One run is 2:28 with no game over; the stakes are the score, the PERFECT count and (proposed) a high-score list.
- **Local in-jokes.** Sandvika, ticket machines, ticket categories, trams and Oslo place names are things Oslo commuters recognise.

**How to play**

1. **Listen.** Every enemy arrives on a beat, so the music tells you when to act.
2. **Collect tickets at Sandvika.** They are the only ammo for the whole song: you start with 3, and 78 are placed in stages 0–1, so the 60-HP boss needs most of them.
3. **Act on the beat.** Hit (X) or throw (C) within 90 ms of a beat for PERFECT and double points.
4. **Dodge.** Jump or double jump over things on the ground, slide under things in the air, and jump onto trams to ride them.
5. **Keep the combo.** Every 8 hits in a row raise the multiplier, up to ×5; taking a hit resets it.
6. **Survive.** You have 5 hearts. Losing them costs time and combo, not the run: you drop back in with 3 hearts and the song goes on.
7. **Beat the boss.** Empty Kaos-trikken's 60 HP with throws before the final hit for a 3,000 bonus.

**Scoring**

| Event | Points |
| --- | --- |
| Kill: most enemies / ninja / bot | 100 / 150 / 200 |
| PERFECT (on the beat) | ×2 |
| Combo multiplier | ×1 to ×5 (one step per 8 hits) |
| Boss hit | 30 |
| Final hit | 2,000, plus 3,000 if the boss is at 0 HP |

**What makes each stage interesting**

| Stage | The hook | Skill it tests | Proposed twist |
| --- | --- | --- | --- |
| 0 · Intro | Calm warm-up: the first suitcases and tickets | Timing a jump | Street fixtures to climb on |
| 1 · Sandvika | Ticket hunt: patterns reward double jumps and route choice; Victoria wakes up | Movement and collecting; this sets your ammo for the whole song | Jump on Victoria to reach the highest tickets |
| 2 · Glitch | The screen works against you: glitch bars and blobs | Reading the beat through visual noise | Platforms that blink on the beat |
| 3 · Neon | First real fight and first tram ride; speed jumps to 165 | Combat and riding | A new flying enemy instead of drones |
| 4 · Map | Longest stage (16 bars): 2-HP bots, the triple-throw power-up and the ninja transformation | Spending ammo wisely | Subway section, rooftop running |
| 5 · Kollektivkaos | Fastest yet (175), fire you can't destroy, two trams | Surviving under pressure | Giant ape, Eplehuset crash |
| 6 · Final wave | Two enemies on every beat | Holding the combo | Escalating fire and sky |
| 7 · Boss | A target that fires back on the beat | Precision, and saving tickets for it | Weak points on the eyes and the core |

The main design tension is ammo: tickets only exist at Sandvika, so what you collect in the first 50 seconds decides how hard the boss fight is.

## Stage map

The song runs through 8 stages in 2:27.6; speed rises from 110 to 205 px/s as the story heats up.

| # | Stage (banner) | Song part | Bars | Time | Location | Scroll (px/s) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | PLAYER ONE | Intro | 1–9 | 0:00–0:17.7 | Bus terminal outside Sandvika | 110 |
| 1 | LEVEL 1 · Sandvika stasjon | Verse 1 | 10–25 | 0:17.7–0:49.2 | Sandvika station platform | 120 |
| 2 | LEVEL 2 · Tekst-til-tale glitch | Pre-chorus 1 | 26–33 | 0:49.2–1:05.0 | Sandvika, glitching | 130 |
| 3 | LEVEL 3 · Inn i spillet · Oslo neon | Chorus 1 | 34–41 | 1:05.0–1:20.7 | Neon coin-op Oslo | 165 |
| 4 | LEVEL 4 · Language changed | Verse 2 | 42–57 | 1:20.7–1:52.2 | «Hele Oslo på en skjerm»: the city map | 145 |
| 5 | LEVEL 5 · Kollektivkaos | Pre-chorus 2 | 58–65 | 1:52.2–2:07.9 | Burning trams and buses | 175 |
| 6 | FINAL WAVE · Siste bølge | Chorus 2 | 66–69 | 2:07.9–2:15.8 | Chaos city | 195 |
| 7 | BOSS · Kaos-trikken | Chorus 2 end + instrumental | 70–76 | 2:15.8–2:27.6 | Burning city, then neon city with a red sun | 195–205 |

After the final hit on «Oslo-STIL!» at 2:27.6, the win screen follows 2.2 s later.

## Storyline

Two girls waiting for a train at Sandvika befriend a ticket machine that shares the singer's name, get pulled into a retro arcade version of Oslo, turn into ninjas and end by defeating Kaos-trikken. Each beat is tied to a lyric line.

1. **Intro, cold evening.** The girls walk through the bus terminal towards the station. «PLAYER ONE · TEKST-TIL-TALE ER STARTET».
2. **Sandvika stasjon.** «tre blå maskiner står og lyser for seg selv»: three ticket machines on the platform. The left one is called Victoria. When the girls reach her at 0:26.4, she wakes up, gets a face and arms, and follows them as a companion.
3. **The glitch.** They talk to her through text-to-speech, and «a-a-a-automaten hakker»: the world starts to glitch. «Sett inn et kort», and the banner «INSERT CARD» pulls them in.
4. **Inside the game.** Chorus 1: Oslo turns into a neon coin-op world (Holmenkollen, a barcode skyline). The first ninjas and trams appear.
5. **Choose travellers.** Victoria switches to English («Language changed»). The ticket categories (CHILD, ADULT, STUDENT, SENIOR) become enemies, and the city map is the battlefield. Card on the terminal at bar 49–50: «PIP! BLINK!», «Thank you for the purchase», and a triple-throw power-up.
6. **Ninja mode (1:40.15).** «Plutselig er vi ninjaer i et coin-op spill»: white flash, the girls become ninjas, and tickets turn into shurikens. At 1:42.0 the screen changes colour (map turns red).
7. **Kollektivkaos.** «gjennom brennende trikker og busser på skrå»: the city is on fire and the public transport has turned against them.
8. **Final wave and boss.** Chorus 2 brings the biggest wave, tagged KAOS. At bar 70 Kaos-trikken walks in and fires its coupler cannon on the beat until the final hit on «Oslo-STIL!».
9. **Win.** Victoria cheers on the win screen.

The story is told through banners (bilingual Norwegian and English) and lyric subtitles; there are no cutscenes.

## Stages in detail

Each stage below lists what is in the game now and what is proposed; the Proposed column is the planning backlog.

### 0 · Intro: bus terminal (bars 1–9, 0:00–0:17.7)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Bus terminal just before Sandvika stasjon, evening | — |
| Background | Night sky with snow, houses with lit windows, low terminal roof (no signs); green, red and green buses waiting at the stops, a red bus driving through right to left | Remove the snow for now; a pixel Entur billboard on a building |
| Foreground | The two girls | Fixtures to jump on: benches, bins, light poles, signs, a kiosk |
| Enemies | Suitcases and snow piles on every other beat; ticket patterns from bar 2 | Suitcases crumble when jumped on (higher bounce); a hit makes the girls stumble without damage; a slide kicks the suitcase away to the right |
| Platforms and mechanics | Flat ground; collect tickets as ammo (start with 3) | Bus roofs as platforms? |
| Transition | The terminal roof's last section rises to station height, the station canopy scrolls in and the green train arrives; banner «LEVEL 1 · SANDVIKA STASJON» at bar 10 | The girls walk out through the terminal onto the platform; a departure board flips to «LEVEL 1» |

### 1 · Sandvika stasjon (bars 10–25, 0:17.7–0:49.2)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Sandvika station platform | — |
| Background | Higher station canopy in sections with «OSLO S» boards; green local train overtakes, brakes and stops at the machines; tomato-soup train at 0:50; houses and snow behind | Someone installing a new ticket machine in the background; the squirrel from the machine's screen as an easter egg |
| Foreground | Three ticket machines roll in at 0:21.7; Victoria (left) wakes at 0:26.4, hops three times and follows | Turn around and jump on Victoria to reach high things |
| Enemies | Suitcases or snow on the downbeat (75 %), pigeons on beat 3 (55 %); lots of tickets at 12–70 px height | Pigeons bob up and down but never below slide height |
| Platforms and mechanics | Tickets are the only ammo source in the game: low rows, jump arcs, staircases, double-jump pairs | Benches, bins and the machines themselves as platforms |
| Transition | Cut to the glitch effects at bar 26 with «LEVEL 2 · TEKST-TIL-TALE GLITCH»; the station stays | The glitch starts on Victoria's screen and spreads over the whole picture during one bar |

### 2 · Tekst-til-tale glitch (bars 26–33, 0:49.2–1:05.0)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Sandvika, breaking up | — |
| Background | Station scene with pink and cyan glitch bars and a blinking «A-A-A-AUTOMAT» | Glitch that grows towards «INSERT CARD» at bar 33 |
| Foreground | Girls and Victoria | Victoria's screen shows text-to-speech bubbles |
| Enemies | Glitch blobs on beats 1 and 3, pigeons in between; one suitcase at bar 32 | — |
| Platforms and mechanics | Flat ground | Glitching platforms that flicker in and out on the beat |
| Transition | «INSERT CARD ▶ ▶ ▶» at bar 33, then a cut to neon Oslo at bar 34 | The player taps a card on Victoria; the camera dives into her screen and comes out in the neon world |

### 3 · Inn i spillet: Oslo neon (bars 34–41, 1:05.0–1:20.7)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Neon coin-op Oslo | Vippetangen and Rådhusgata as recognisable spots |
| Background | Pink sun, barcode skyline, Holmenkollen jump line, neon grid floor | Pixel Oslo landmarks (Holmenkollen, Munch) from `inspiration/` |
| Foreground | Girls and Victoria; the friend's assist starts here | — |
| Enemies | Ninja on beats 1 and 3, drone on 2 and 4; coins; trams at bars 36 and 40 | Replace the drones («this is not Ukraine»); ninjas the same size as the girls with richer animation |
| Platforms and mechanics | Tram as a full-length moving platform (roof at 31 px): ride it or die on a side hit | A tram hit bounces the player out to the left instead of killing at once |
| Transition | Cut to the map at bar 42 with «LANGUAGE CHANGED · TO ENGLISH · LEVEL 4» | Victoria taps the flag; the neon city flattens into a map of Oslo |

### 4 · Language changed: the city map (bars 42–57, 1:20.7–1:52.2)

|  | Now | Proposed |
| --- | --- | --- |
| Location | «Hele Oslo på en skjerm»: Oslo as a map | Lines spreading out from the centre along T-bane and train routes |
| Background | Teal map grid with place signs (Tjuvholmen, Kampen, Skullerud, Vulkan, Torshov, Valhall, Ormøya, Sinsen); turns red at 1:42.0 | A subway section here («tog og bane»); buildings to jump on |
| Foreground | Girls and Victoria; ninja mode at 1:40.15 | Banner «YOU'RE A NINJA!» instead of «PLUTSELIG NINJAER!» |
| Enemies | Ticket-category bots (CHILD, ADULT, STUDENT, SENIOR, 2 hp), drones, coins; trams at bars 46 and 54 | Bots that look like the categories (pram, briefcase, backpack, walking stick) |
| Platforms and mechanics | Terminal pickup at bar 49: card on the terminal gives triple throws for 8 bars; tickets become shurikens in ninja mode | Platforms on roofs and map lines |
| Transition | Inside the stage: white flash into ninja mode at 1:40.15, the map turns red at 1:42.0. Out: cut to the burning city at bar 58 with «LEVEL 5 · KOLLEKTIVKAOS» | The red map catches fire and burns away to show the burning city |

### 5 · Kollektivkaos (bars 58–65, 1:52.2–2:07.9)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Burning city | Eplehuset (the Apple store) for the tram crash |
| Background | Tilted red and blue burning trams and buses, flames, embers | A Rampage-style giant ape crushing trams and throwing a bus; trams get holes and crumble; a tram crashing into Eplehuset if hit at the right moment |
| Foreground | Ninja girls and Victoria | — |
| Enemies | Ninjas, drones, fire hazards (solid, jump them); trams at bars 60 and 64 | Thrown buses and falling debris on the beat |
| Platforms and mechanics | Tram roofs | Wrecked trams as platforms |
| Transition | Same scene; banner «FINAL WAVE · SISTE BØLGE» at bar 66 | The giant ape throws one last bus and leaves; the sky turns redder |

### 6 · Final wave (bars 66–69, 2:07.9–2:15.8)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Chaos city | — |
| Background | Same as Kollektivkaos | Escalating: more fire, red sky |
| Foreground | Ninja girls and Victoria | Victoria cheers on the chorus calls (built) |
| Enemies | KAOS bots and ninjas on every beat, plus drones or ninjas on the off-beat; tram at bar 68 | — |
| Platforms and mechanics | Tram roof | — |
| Transition | «BOSS · KAOS-TRIKKEN!» at bar 70; the boss walks in over one bar while the wave continues | The ground shakes on the beat before it appears |

### 7 · Boss: Kaos-trikken (bars 70–76, 2:15.8–2:27.6)

|  | Now | Proposed |
| --- | --- | --- |
| Location | Burning city until bar 73, then the neon city with a red sun (bars 74–76) | — |
| Background | Kollektivkaos fires, then the boss version of the neon scene | — |
| Foreground | Kaos-trikken walks in over one bar and stands at the right; 16-frame sprite (walk, idle, attack, hit) | — |
| Enemies | The boss fires on the beat: shots (jump) and fireballs (stay low); waves continue until bar 73 | Boss attack patterns that change with the bar: stomp, arm swipe, eye laser |
| Platforms and mechanics | Boss has 60 HP; every thrown ticket hit takes 1; the final hit scores 2,000, plus 3,000 if HP is 0 | Weak points: the red eyes and the chest core |
| Transition | Final hit on «Oslo-STIL!» at 2:27.6: bursts and screen shake, win screen 2.2 s later with Victoria cheering | Kaos-trikken falls apart into an ordinary tram that drives off; enter 3-letter initials for the high-score list |

## Characters

The foreground cast is the two girls and Automat Victoria; everyone else is an enemy or background.

| Character | Role | Appears | Now | Proposed |
| --- | --- | --- | --- | --- |
| The singer (player) | Runs, jumps, slides, hits, throws | Whole song | 24×32 sprite sheet, 10 poses; ninja version from 1:40.15; no headbands before ninja mode | Ponytails that bounce when running, hang down when rising and fly up when falling; fix the legs |
| Her friend | Follows and helps | Whole song; assist from chorus 1 | Same size, own palette | — |
| Automat Victoria | Companion ticket machine | Wakes at 0:26.4, then follows | Front-facing machine with blue edges, face and arms; hops, floats, talks on lyrics about her, cheers on chorus calls and at the win | A step the player can jump on; squirrel on her screen |
| Platform machines | The other two «blå maskiner» | Sandvika, 0:21.7–0:37 | Same style, no face or arms | — |
| Kaos-trikken | Boss | Bar 70 to the end | Light-blue tram robot facing left, red tail-light eyes, coupler cannon | — |
| Background people | Atmosphere | — | None | A worker installing a new ticket machine at Sandvika |

## Enemies and obstacles

There are 14 kinds, all scheduled on the beat; heights are px above the ground (a single jump reaches about 50, a double jump about 85).

| Kind | Stages | Height | HP | How to beat it | Proposed |
| --- | --- | --- | --- | --- | --- |
| Suitcase | 0, 1, 2 | 0 | 1 | Jump or hit | Crumbles when jumped on and bounces you higher; a hit makes you stumble without damage; a slide kicks it away |
| Snow pile | 0, 1 | 0 | 1 | Jump or hit | Remove for now (no snow) |
| Pigeon | 1, 2 | 26 | 1 | Duck under, hit or throw | Bobs up and down, never below slide height |
| Glitch blob | 2 | 0 | 1 | Jump or hit | — |
| Ninja | 3, 5, 6 | 0 | 1 | Hit or throw | Same size as the girls, richer animation |
| Drone | 3–7 | 30 | 1 | Stay low or throw | Remove; needs a replacement flying enemy |
| Tram | 3, 4, 5, 6 | Platform, roof at 31 | — | Jump onto the roof and ride it; a side hit kills | Bounces the player off to the left instead |
| Bot | 4 (CHILD, ADULT, STUDENT, SENIOR), 6 (KAOS) | 0 | 2 | Two hits or throws | Look like their ticket category |
| Fire | 5 | 0, solid | — | Jump over | — |
| Boss shot | 7 | 6 | 1 | Jump | — |
| Boss fireball | 7 | 28 | 1 | Stay low or slide | — |

**Pickups**

| Pickup | Stages | Height | Effect |
| --- | --- | --- | --- |
| Ticket | 0, 1 only | 12–70 | +1 throw (the only ammo in the game) |
| Coin | 3, 4 | 34–46 | Points |
| Terminal | 4 (bar 49) | 30 | Triple throw for 8 bars, «PIP! ★★★» |

## Platforms and mechanics

Today the only platforms are the ground and the tram roof; the main gameplay gap is things to climb on.

**Core mechanics (now)**

- **Auto-run on the song clock.** The world scrolls at the stage speed; ← → move across the whole screen width.
- **Jump and double jump** (Space or ↑), about 50 and 85 px. **Slide** (↓) under low-flying things, or fast fall in the air.
- **Hit** (X) up close; **throw** (C) a ticket, or a shuriken in ninja mode. Each throw costs a ticket; with none left you get «TOM! · EMPTY».
- **Rhythm scoring.** A hit within 90 ms of a beat is PERFECT; hits build a combo.
- **Hearts and respawn.** Losing the last heart, or a tram side hit, makes the player burst; she drops back in from above (onto a tram roof if one is passing) and flashes white while invincible.
- **Tram riding.** Land on the roof and ride it; standing still carries you back to the left edge, and you fall off when the tail passes.
- **Power-up.** The terminal at bar 49 gives triple throws for 8 bars.
- **Companions.** The friend's assist starts in chorus 1; Victoria follows and reacts but doesn't fight.

**Proposed platforms and mechanics**

| Idea | Stage | Notes |
| --- | --- | --- |
| Street fixtures to jump on: benches, bins, light poles, signs, kiosks | 0, 1 | Gives the ticket patterns something to sit on |
| Jump on Victoria to reach high things | 1 onwards | Turn around, she works as a step |
| Suitcase bounce pads | 0–2 | Crumble on landing, extra-high bounce |
| Glitching platforms that blink on the beat | 2 | Fits «automaten hakker» |
| Jump on buildings and map lines | 4 | Roof-top running in the map scene |
| Subway section | 3 or 4 | Underground with trains on both sides |
| Wrecked trams and thrown buses | 5 | From the Rampage-style ape |
| Tram crash into Eplehuset | 5 | Timed hit triggers the crash |
| Tram hit bounces you off to the left | 3–6 | Replaces the instant death |
| Boss weak points (eyes, chest core) | 7 | Extra damage for precise throws |

**Around the game:** a central high-score list with 3-letter initials (top list on the title screen, top 10 in the pause screen), and all sound effects made from the ticket-machine samples.

## Open questions

- [ ] **Drones:** what replaces them as the flying enemy in stages 3–7? Pigeons, seagulls, flying ticket stubs?
- [ ] **Snow:** if snow goes, what replaces the snow piles at Sandvika? Bins, prams, scooters?
- [ ] **Subway section:** where does it fit? Inside stage 4 («tog og bane»), or as its own stage that splits stage 3 or 5?
- [ ] **Vippetangen and Rådhusgata:** which stage do they belong to: neon Oslo (3) or the map (4)?
- [ ] **Map scene:** keep place signs on a grid, or redraw it as T-bane and train lines spreading from the centre?
- [ ] **Entur billboard:** the art rule bans company logos on vehicles; is a pixel Entur logo on a building OK, and does the same go for the Short Shift easter egg?
- [ ] **Rampage ape vs. Kaos-trikken:** two giant creatures back to back (stages 5 and 7). Keep both, or let the ape be the stage 5 mini-boss?
- [ ] **Vocal vs. backing timing:** pre-chorus 2 and chorus 2 are sung earlier than the backing sections; stage changes follow the backing today. Keep as is?
- [ ] **«INSERT CARD» at bar 33:** IDEAS says to replace «insert coin»; does the card banner count, or should it change too?
