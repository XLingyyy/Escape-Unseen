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

## Evidence and handoff

- `PROVENANCE.csv`: per-file tool/model, full prompt, UTC time and known or estimated generation cost. Derived files explicitly share their raw source's cost, so those rows must not be added twice.
- `Audio/_work/*.json`: fal request IDs, settings, result metadata and measured output properties.
- `Models/_work/tripo_jobs.json`: model prompts, observed Studio jobs and credit deductions.
- `TOOL_SETUP.md`: connection evidence and limitations.
- `CODEX_TASKS.md`: completed handoff entries, updated as each deliverable is ready.

Codex has run the limited PIE sessions and Blueprint compilation described above. It has not packaged a build, recorded a gameplay video, uploaded the store page or submitted the jam entry. The final jam submission must be performed by the entrant.
