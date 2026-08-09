# Exercise demonstration GIFs — sourcing and licensing

**Status:** 37 of the 50 `exercises` rows have a real, visually-verified demo GIF. The
remaining 13 have none — no honest match existed, and no substitute was forced.

## Why this needed a real decision, not just a download

Item 5 of the post-Module-16 feature plan ("visual workout animations... guide users on
how to perform the exercises") called for sourcing a **real** dataset, the same rigor as
Module 8's body-image dataset work — no fabricated or auto-generated content passed off
as real.

Research before touching any files (see chat history for the full trail): the one
option with unambiguous, official open licensing — **wger.de** (AGPL-3.0 code, CC-BY-SA
4.0 data) — only has static photos, not animated GIFs, and the project owner explicitly
chose true animated GIFs over that safer static-image option, accepting the licensing
risk described below.

## Source

- **Data/media**: [`omercotkd/exercises-gifs`](https://github.com/omercotkd/exercises-gifs)
  on GitHub — a community backup of the Kaggle dataset
  [`edoardoba/fitness-exercises-with-animations`](https://www.kaggle.com/datasets/edoardoba/fitness-exercises-with-animations)
  (the original dataset's GIF URLs stopped resolving; this repo re-hosts the same files).
- **License**: the backup repo's own code/wrapper is MIT-licensed, but its README is
  explicit that this does **not** cover the media: *"I do not own any of the content in
  this repository. All rights belong to the original creators and dataset owner."*
  The underlying rights holder and original license terms are not otherwise stated
  anywhere in the chain (Kaggle dataset → backup repo). **This is a real, disclosed
  licensing gap, not an oversight** — the project owner was told exactly this trade-off
  (vs. the CC-BY-SA-clean but static-only wger.de alternative) and chose it anyway for
  this non-commercial academic FYP. If this project is ever deployed commercially or
  redistributed, these 37 files need a licensing review or replacement first.
- 1,323 exercises total in the source CSV (`id`, `name`, `bodyPart`, `equipment`,
  `target`, `secondaryMuscles`, `instructions`), GIFs named `<id>.gif`.

## Matching methodology

Exact/fuzzy name matching alone was **not** trusted blindly — an early automated pass
produced real false positives (e.g. a naive substring check matched "Squats" against an
unrelated compound exercise because "squat" happens to appear inside a much longer name;
"crunches" was matched to a "run" entry because "run" is a literal substring of
"c-RUN-ches"). The final process was:

1. Normalize + word-boundary-aware matching (not raw substring), preferring the
   candidate whose word count is closest to the target name.
2. Cross-check the source row's `equipment` field against our own `exercises.equipment`
   column to prefer the right variant (e.g. dumbbell vs. barbell vs. bodyweight) when
   multiple candidates tied.
3. **Excluded outright** — not force-matched — whenever the closest available candidate
   was a different movement pattern, not just a different equipment variant:
   Jumping Jacks, Superman, Box Jumps, Face Pulls, Reverse Lunges, Scissors Kicks, Prone
   Cobras, Resistance Band Pull-Aparts, Wall Angels, Bird Dogs, Dragon Flags, Frog Jumps,
   Windshield Wipers.
4. For the most ambiguous accepted candidates, **the actual GIF was downloaded and
   visually inspected** before being finalized — not just judged by name. This caught a
   real mismatch: the only "flag"-named entry for Dragon Flags turned out, on inspection,
   to depict a **Human Flag** (gripping a vertical pole) — a different exercise entirely
   from a Dragon Flag (lying on a bench). It was excluded rather than mislabeled.

A small number of accepted matches use a different equipment variant than our row
specifies (e.g. `exercise_id=2` Squats → a resistance-band squat GIF, since no
unqualified bodyweight "squat" exists in the source data) where the fundamental movement
pattern is still correctly represented — these are a disclosed approximation, not an
error.

## Files

- `frontend/public/exercise-gifs/<exercise_id>.gif` — 37 files, ~11 MB total, named by
  **our** `exercises.exercise_id`, not the source dataset's id.
- No backend or database changes — these are static reference assets looked up by a
  predictable filename, the same pattern already used for the app's hero background
  images (`frontend/public`/`src/assets`), just keyed per-exercise instead of per-page.
  The frontend requests `/exercise-gifs/<exercise_id>.gif` and falls back to a "no demo
  available yet" state on a 404 for the other 13.

## Full mapping (our id → source id → source name)

| # | Our exercise | Source id | Source name | Notes |
|---|---|---|---|---|
| 1 | Push-ups | 0662 | push-up | exact |
| 2 | Squats | 1004 | band squat | equipment differs, movement correct |
| 3 | Lunges | 1460 | walking lunge | |
| 4 | Burpees | 1160 | burpee | exact |
| 5 | Mountain Climbers | 0630 | mountain climber | exact |
| 6 | Jumping Jacks | — | — | no match in source data |
| 7 | Bicycle Crunches | 0972 | band bicycle crunch | equipment differs, movement correct |
| 8 | Dips | 0251 | chest dip | |
| 9 | Pull-ups | 0652 | pull-up | exact |
| 10 | Russian Twists | 0687 | russian twist | exact |
| 11 | Leg Raises | 0620 | lying leg raise flat bench | |
| 12 | Deadlifts | 0032 | barbell deadlift | equipment matches |
| 13 | Bench Press | 0025 | barbell bench press | equipment matches |
| 14 | Rows | 0027 | barbell bent over row | equipment matches |
| 15 | Shoulder Press | 0405 | dumbbell seated shoulder press | equipment matches |
| 16 | Calf Raises | 1373 | bodyweight standing calf raise | equipment matches |
| 17 | Tricep Extensions | 0430 | dumbbell standing triceps extension | equipment matches |
| 18 | Lateral Raises | 0334 | dumbbell lateral raise | equipment matches |
| 19 | Glute Bridges | 3013 | low glute bridge on floor | equipment matches |
| 20 | Superman | — | — | only "superman push-up" exists (different exercise) |
| 21 | Box Jumps | — | — | only a jump-down/stabilize variant (wrong emphasis) |
| 22 | Kettlebell Swings | 0549 | kettlebell swing | exact |
| 23 | Step-ups | 0431 | dumbbell step-up | |
| 24 | Face Pulls | — | — | no match in source data |
| 25 | Lat Pulldowns | 2330 | cable lat pulldown full range of motion | equipment matches |
| 26 | Reverse Lunges | — | — | only "reverse crunch" (different exercise) |
| 27 | Plyo Squats | 0371 | dumbbell plyo squat | |
| 28 | Scissors Kicks | — | — | only "scissor jumps" (different movement) |
| 29 | Tricep Dips | 0814 | triceps dip | exact |
| 30 | Seated Rows | 0861 | cable seated row | equipment matches |
| 31 | Flutter Kicks | 0459 | flutter kicks | exact |
| 32 | Inverted Rows | 0499 | inverted row | exact |
| 33 | Bulgarian Split Squats | 2368 | split squats | generic split squat, not the rear-elevated variant |
| 34 | Prone Cobras | — | — | no honest match |
| 35 | Resistance Band Pull-Aparts | — | — | no match in source data |
| 36 | Wall Angels | — | — | no match in source data |
| 37 | Bird Dogs | — | — | no match in source data |
| 38 | Plyometric Push-ups | 1306 | plyo push up | |
| 39 | Decline Push-ups | 0279 | decline push-up | exact |
| 40 | Incline Push-ups | 0493 | incline push-up | exact |
| 41 | Dead Bugs | 0276 | dead bug | exact |
| 42 | Pistol Squats | 1759 | single leg squat (pistol) male | equipment matches |
| 43 | Zottman Curls | 0439 | dumbbell zottman curl | equipment matches |
| 44 | Dragon Flags | — | — | visually confirmed the only candidate is a Human Flag |
| 45 | Renegade Rows | 0521 | kettlebell alternating renegade row | equipment differs, movement correct |
| 46 | Frog Jumps | — | — | no honest match |
| 47 | Turkish Get-ups | 0551 | kettlebell turkish get up (squat style) | equipment matches |
| 48 | Bear Crawls | 3360 | bear crawl | exact |
| 49 | Windshield Wipers | — | — | only "isometric wipers" (targets pectorals, wrong exercise) |
| 50 | Thrusters | 3305 | barbell thruster | equipment matches |
