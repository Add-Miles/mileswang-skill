# Portable V10 semantic editing contract

## Result

The result is a semantic explanation system over real talking-head footage:

1. Speech is divided when the meaning changes, not at arbitrary fixed seconds.
2. Captions provide readability; they are not the primary visual treatment.
3. Main cards compress the current claim into a title, explanation, tags, and
   optional evidence meter.
4. Screen media is preferred when it provides real evidence. Reconstructed
   media must be labeled by provenance; missing required media blocks rendering.
5. Micro-effects punctuate only selected semantic moments.
6. Main cards, screen media, micro-effects, face region, and lower caption safe
   zone are spatially scheduled rather than stacked blindly.

## Required storyboard behavior

- Cover the full source duration with ordered, non-overlapping semantic beats.
- Every beat contains `claim`, `title`, `detail`, `tags`, `treatment`, `slot`,
  and `reason`.
- `reason` explains what the visual adds beyond repeating spoken words.
- Captions remain within the source duration and use the caption lane.
- Events start 0.4–0.6 seconds before their semantic cue when an anticipatory
  entrance is appropriate; event timing still remains inside its owning beat.
- Events on one lane never overlap. Auxiliary events may not use `lower` slot,
  which is reserved for captions.
- A beat may set a project-specific `top` position after inspecting real source
  frames. This is how the card avoids watermarks, faces, and embedded captions;
  placement must not be hard-coded from another person's video.
- Real-media requests use `provided`, `reconstructed`, or `missing`. Only
  actually read media can be `provided`; `missing` required media is blocking.

## Human usefulness gate

Machine checks prove portability, timing, layout constraints, and media
structure. Miles must still compare the same protected input against V10 and
approve semantic beats, explanatory value, material choice, visual crowding,
rhythm, captions, and overall publishability.
