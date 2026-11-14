# Escape Unseen development log

Prepared on 13 November 2026 for the Epic AI MegaJam Glass Box record. This log distinguishes repository evidence, implementation reports and generated source assets. It does not claim that a packaged build has been tested or submitted.

## Earlier design and preparation

The retained GDD records an initial written concept dated 2 November, followed by v1.1 and v1.2 on 12 November. Pre-jam tooling and workflow records are retained in `2026-epic-ai-megajam-prep`. These dates remain part of the provenance; revising the document during the jam does not change when its earlier material was written. The repository's rules record leaves the eligibility of reusing the earlier detailed GDD subject to organizer clarification.

The design uses the announced theme, **Director's Cut**, as a player action: build two approved arrangements of the same room, stand on a fixed mark, and cut from Shot A to Shot B. The player remains in place while the same crate changes position.

## Repository milestones

Source: `git log --stat`, captured through commit `36cdef6`. Descriptions below summarize the commit messages and changed-file lists; Codex did not open the Unreal assets. The task card groups the core milestones under 13 November UTC. The same commits occurred on the evening of 12 November in Los Angeles.

| Los Angeles time (PST, UTC−08:00) | UTC | Commit | Recorded work |
|---|---|---|---|
| 12 Nov 08:54:03 | 12 Nov 16:54:03 | `e4c56b2` | First commit: README and empty UE 5.8.4 project. |
| 12 Nov 17:23:23 | 13 Nov 01:23:23 | `bb418b6` | Core-loop Blueprints and the first-room graybox, including the character, controller, HUD, shadow service, shot director and block assets. |
| 12 Nov 17:45:08 | 13 Nov 01:45:08 | `aa80f1c` | Second and third graybox rooms, lighting/material work, and six source texture PNGs. |
| 12 Nov 17:51:26 | 13 Nov 01:51:26 | `3b8cb5b` | Title card, per-level hints, placement validity colors and ending options. |
| 12 Nov 18:13:24 | 13 Nov 02:13:24 | `73a2efb` | Jump changed from Space to W / Up in response to playtest feedback. The feedback is documented in the commit message; this log does not reconstruct the playtest. |
| 12 Nov 18:28:19 | 13 Nov 02:28:19 | `36cdef6` | Chibi placeholder character with procedural animation, cut flash and slate cards. |

## Implementation notes reported by Claude's task card

The 13 November task card reports that geometry functions are implemented inside the `BP_ShadowService` Actor. The available MCP interface did not support creating a BlueprintFunctionLibrary or a user-defined structure. Polygon collections therefore use a flat Vector2D array plus a parallel array of polygon vertex counts. This is a limitation of the interface used for this project, not a claim that Unreal Engine itself lacks these asset types.

The same card specifies first-room title/opening presentation, Enter to restart and Q to quit after the final room, and cyan/red placement previews. The v1.3 document synchronizes these reported decisions. The opening sentence retained from the GDD still needs to be compared with the integrated game's exact wording by Claude.

## Codex source-asset production on 13 November

- Located and reused Blender 5.2.0 LTS and FFmpeg/ffprobe 6.1.1. No engine upgrade or Unreal editor operation was performed by Codex.
- Confirmed that the fal key can generate audio. Its account-billing request was denied, while pricing and an actual generation succeeded. Keys were kept out of project files.
- Replaced desktop mouse/keyboard control of Tripo with an isolated Playwright session. The user signed into the dedicated browser. Codex then navigated to the 3D workspace through page elements. The account showed 3,200 Studio credits; the task allocation remains 3,000 credits.
- Generated 25 delivery audio candidates: three clapper variants, two variants of every other required cue, and two 72-second optional music tracks using fal Stable Audio 2.5. Source requests, raw files and processing metadata are retained under `Audio/_work`; delivery WAVs are under `Audio`.
- Audio processing converts to 48 kHz, 16-bit mono, fits the specified duration and normalizes the peak to −1 dBFS. Looping ambience uses an overlap crossfade. Numerical file checks do not replace Claude's listening and in-game level adjustment.
- Delivered seven original static models from Tripo Studio: H3.1 for the guard, cell door and bucket; H3.0 for the lampshade and window bars; H2.5 for the prisoner and cot. Several H3.1/H3.0 requests remained at 99% past their displayed estimates; bounded retries used the same style prompts. All request records are retained, including unsuccessful attempts. Total Studio spend observed from requests is 625 credits.
- Through an isolated Blender MCP session on localhost port 9877, imported raw FBX, reduced each delivery mesh to 14,500 triangles, set centimeter dimensions and bottom-center pivots, oriented the front along +X, and exported static FBX with a single PNG baseColor. Blender sources and preview images are retained. Checked the lampshade underside and one representative FBX round trip; no UE import or playtest was performed.
- Revised the GDD into a separate v1.3 file, drafted the English store page and prepared a submission-material checklist. The original v1.2 remains unchanged.

## Human and tool roles

The human developer supplies design decisions, playtest feedback and final acceptance. Claude Code directs the visual design and integration. The subsequent Task 4 explicitly authorized Codex to integrate its models through Unreal MCP. Editor access is serialized using the shared UE lock. Codex also prepares source assets and documentation. GPT's design-document role is recorded in the retained GDD. Tripo generates model sources; fal hosts the audio-generation models. FFmpeg and Python process audio. Blender performed model cleanup, scaling, texture packaging, FBX export and preview rendering through MCP.

## Task 4A integration, 13 November UTC

Codex imported the guard, window bars, cell door and bucket, created the shared textured material and per-model instances, disabled Nanite and generated lightmap UVs, and limited these textures to 1024 pixels. The guard Blueprint now uses the model behind the bars; the original scan timing and angles remain. Doors, amber exit markers and buckets were saved as non-colliding, non-shadow-casting decorations in all three maps. L03's actual exit center is X=1325, so its door follows that coordinate. No gameplay actor was repositioned.

The modified guard Blueprint compiled. PIE screenshots cover each map's light-placement phase and the always-visible guard, including a crop from an actual 4x engine screenshot. The temporary always-on flag was restored to false. The extended wall mask remains visibly distinguishable from the wall and is identified for Claude's visual review. No full playthrough or packaging was performed.

## Task 4B integration, 13 November UTC

Codex imported the prisoner, lampshade and cot. The character's editable `bUseModel` switch defaults to true, with the original primitive assembly retained in the false branch. The imported model uses the existing Mesh parent and procedural animation. The modified character Blueprint compiled. The prisoner texture initially had no generated mip levels according to the engine log; its source pixels and UVs were intact. Rebuilding this texture's derived data restored its colors, which were confirmed in PIE.

Each lampshade is a saved decoration attached to its map's RuleBulb. The bulb's 0.22 scale is compensated to retain the shade's 40 cm diameter; the specified relative Z=12 therefore produces a 2.64 cm world offset. In L03, probe command 3 moved the bulb to (1050, 0, 900) and the attached shade to (1050, 0, 902.64). The changes were confined to PIE and discarded when it stopped.

The L01 cot spans X=380–570 at Y=-115, Z=0. The user explicitly approved Yaw=0 because the delivered source mesh's long axis is X. Its tint was reduced to (0.55, 0.55, 0.55), as the task card permits, to reduce its resemblance to a gameplay platform. All decorations remain non-colliding and do not cast shadows.

Required review images are in `EU/Saved/review/task4_4B_*.png`: L01 overview, standing character, jump apex and lamp follow. The jump capture invoked the existing JumpPressed function and paused the actual simulation at the first descending sample (vertical velocity -16.69 cm/s), with temporary slow motion for capture precision. Runtime pause and time scale were restored. These are scoped art/integration checks, not a complete level playthrough. Both batches were saved and committed separately; final visual acceptance remains with Claude and the human developer.

## Evidence and handoff

- `PROVENANCE.csv`: per-file tool/model, full prompt, UTC time and known or estimated generation cost. Derived files explicitly share their raw source's cost, so those rows must not be added twice.
- `Audio/_work/*.json`: fal request IDs, settings, result metadata and measured output properties.
- `Models/_work/tripo_jobs.json`: model prompts, observed Studio jobs and credit deductions.
- `TOOL_SETUP.md`: connection evidence and limitations.
- `CODEX_TASKS.md`: completed handoff entries, updated as each deliverable is ready.

Codex has run the limited PIE sessions and Blueprint compilation described above. It has not packaged a build, recorded a gameplay video, uploaded the store page or submitted the jam entry. The final jam submission must be performed by the entrant.

## Task 4C correction, 13 November UTC

Claude accepted 4A/4B and requested removal of the visible wall patch beneath the guard window. Codex duplicated M_ModelTex as the masked M_ModelTexClip and added saturate(((AbsoluteWorldPosition - ActorPositionWS).Z - ClipZ) * 1000) to OpacityMask. MI_GuardClip retains the original guard texture, tint and roughness. Measured lower-bar sections were approximately Z=0–7.07 cm; including the window component offset of -5 and actor scale 1.4 gives ClipZ=-2.05 cm. BuildGuard now has only the night backing, window mesh and clipped guard mesh. The -100 descent, scan behavior, collision and shadow settings remain unchanged.

The guard Blueprint compiled. Actual PIE captures show a continuous L01 wall, a clean sill cut at L03 Alpha=0.5000007, and the fully risen guard with its flashlight head retained. Screenshots: EU/Saved/review/task4C_L01.png, task4C_rise.png and task4C_closeup.png. The closeup is cropped from the engine high-resolution screenshot. Slomo was restored to 1, bAlwaysOn to false, PIE stopped and assets saved. No map edits, full playthrough or packaging were required.

## Task 4D correction, 13 November UTC

Claude accepted 4C and requested removal of the dark strip outside the window frame. Measurements showed that the frame and backing were already geometrically centered at local X=0. The strip came from perspective parallax across their 70 cm local depth separation. The frame opening measures approximately 99.73 cm across, so the backing width was reduced from 110 to 103.73 cm (opening plus 4). BuildGuard now compensates only the backing X position using the placed camera and guard Actor positions; L03 evaluates to -16.738 cm. The formula uses the existing front-facing camera/guard layout and computes the same screen center at the two depths. Guard, spotlight, frame and clipping settings are unchanged.

The Blueprint compiled, and the requested actual PIE closeup confirms no dark strip outside either side: EU/Saved/review/task4D_closeup.png. It is cropped from the native 4x engine screenshot. bAlwaysOn was restored to false, pause cleared, PIE stopped and assets saved. The only game asset changed is BP_GuardWindow. No additional playthrough or packaging was performed.


## Claude level-design commission, 13 November 2026

Codex delivered `Docs/GPT_LEVEL_DESIGN.md` and `Docs/GPT_LEVEL_LAYOUTS.svg` from `GPT_LEVEL_BRIEF.md` and GDD v1.3. They specify L00, five new levels L04–L08, and the order L00, L01, L02, L03, L04, L06, L05, L07, L08. The user explicitly approved four 1B tutorial jumps to preserve the requirement that both shots are necessary. The document discloses the legacy empty-A exception in L01/L02 and the impossibility of a unique legal crate coordinate under unrestricted continuous lamp placement.

Analytical work covered complete 0.005B-expanded shadow containment for 32 crate snapshots, 40 reference jump paths using a conservative capsule bounding rectangle, full base support, lamp clearance, mark clearance, and one exposed-point counterexample per new level. The reference layouts were drawn from the same data, and the diagram preview was visually inspected. This work did not connect to UE, modify Content, compile Blueprints, run Chaos/PIE, playtest or package the game. Actual movement feel and physical settling remain unverified. Asset provenance records include the brief and the user's tutorial clarification.

## 2026-11-13 — Task 5 gameplay feedback

- 5A (`ec8d0b9`): fixed ExitZone mesh-default collision, explicit E escape, 0.5-second fade and WRAP, GameInstance level order.
- 5B (`d0296a1`): room-wide lamp placement with 30 cm clearance, retain last valid position and show rejected cursor cross.
- 5C: pause/settings Canvas menu, keyboard and mouse controls, default-off shadow guides, independent music and Master-effect gain, session settings across travel.
- Targeted PIE evidence: exit sweep reaches center; no automatic escape on entry; WRAP and automatic L01→L02 travel; legal/illegal lamp moves; paused inspection timers; mouse and keyboard value changes; settings survive travel. Five Task 5 screenshots saved under Saved/review. Editor intercepted Esc as Stop PIE; game toggle branch is implemented, editor shortcut unchanged. No package or full playthrough. Details: Docs/TASK5_6_HANDOFF.md.

## 2026-11-13 — Task 6 Canvas HUD and contextual feedback

Imported the three unmodified OFL font files from official Google Fonts sources, retaining licenses and six Runtime Font/FontFace assets. Rebuilt BP_EscapeHUD with the specified scene card, script hint, key blocks, projected prompts, inspection framing, native material stamps, title/end and pause menu. BP_ShotDirector now shares the existing shadow CheckBlock predicate between ghost color and HIDDEN/LIT labels; dragging begins on the lamp. No new shadow algorithm or fixed-level reconstruction was added.

Affected Blueprints/materials compiled and saved. Eight native 1920x1080 task6 PNGs in Saved/review were visually checked. Real approvals generated inspection/LOCKED; mark and exit fixtures used teleport and checked the actual predicates. Preview at (1100,50), with lamp (500,800), was HIDDEN and passed inspection. Fixed a disconnected Saturate material pin, integer promotion in Canvas geometry, overlap between preview status and the bottom hint, and Canvas-material tint encoding. Final PIE stopped; temporary actors/bridge removed; play-window settings restored. See Docs/TASK5_6_HANDOFF.md for evidence and limits. No full traversal, packaged run, push or submission; Task 7 remains unstarted.

## 2026-11-14 — Task 6B UI corrections

Top hints, inspection letterboxes, panel overlap opacity and title Q quit are implemented and compiled. Four native 1920×1080 screenshots were visually checked; actual approval and lamp overlap (.25 opacity) were observed. Actual Q at the title exited PIE. Prior design commission files/logs are included; three binary resaves are restored with UE closed. Details: Docs/TASK6B_7_HANDOFF.md. No full traversal, packaging or push.

## 2026-11-14 — Task 7 L00 First Cut

Added editor-preplaced tutorial L00 from approved design, editable A/B crate relay, per-shot budgets, stage-specific tutorial text and spawn facing. Startup selects L00; completed-map order is L00–L03. Both reference approvals passed once; two native screenshots checked and full required geometry/lamp/door bounds are in frame at original FOV58. See Docs/TASK6B_7_HANDOFF.md. No traversal, packaging or push.
