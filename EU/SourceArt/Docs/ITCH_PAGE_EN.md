# itch.io page copy

## Title

Escape Unseen

## Short description

Direct your own prison break. Hide your props, approve two shots, and cut between them to build a way out.

## Long description

The guard watches the light. You set the scene.

**Escape Unseen** is a small, single-player puzzle platformer about staging an escape and choosing the moment to cut. Move the lamp, place your crates inside the shadows, and let them settle. The guard checks whether every part of your set is hidden. Getting a shot approved is only the beginning: you still need to turn it into a route you can climb.

Prepare Shot A and Shot B in the same room. Once both are approved, step into the scene, reach the marked spot and press **E** to cut. Your character stays in place. The props take their positions for the next shot.

Across three rooms, learn to reveal a first step, assemble a hidden staircase and make one crate serve two purposes. In the final room, use it to reach the middle ledge in Shot A, then cut to Shot B to find that same crate waiting for the last climb.

Built for the **2026 Epic AI MegaJam** theme, **Director's Cut**. The cut is yours to make, and the escape depends on how you arrange what comes before and after it.

## Controls

| Action | Input |
|---|---|
| Move | A / D or Left / Right arrows |
| Jump | W or Up arrow |
| Cut from Shot A to Shot B | E, while standing on the fixed cut mark |
| Move the lamp or placement preview | Mouse |
| Confirm placement | Left mouse button |
| Cancel preview | Right mouse button |
| Confirm the lamp / request shot approval | Enter, in the appropriate setup stage |
| Retrieve the selected crate | Delete |
| Undo the last build action | Ctrl+Z |
| Retry from Shot A | R; Enter also retries after failure |
| Return to building | Tab |
| Pause | Esc |
| Restart after the final room | Enter |
| Quit after the final room | Q |

Every placed crate must be fully hidden and settled before its shot can be approved. A valid placement preview does not itself mean that a shot has passed inspection.

## AI tools and development disclosure

Human direction and playtest feedback guided the design and revisions. **Claude Code with Unreal MCP** was used for Unreal Engine implementation and integration. **Codex** prepared external audio/model sources, processing and documentation. **GPT** supported the design-document workflow.

The source-asset workflow uses **Tripo Studio** for original static models and **fal**, including ElevenLabs Sound Effects v2 and Stable Audio 2.5, for generated sound effects and music. Python and FFmpeg handle audio processing. Final asset choices and in-game integration are made during development; the linked development log and provenance record identify what was generated and what was actually used.

An earlier written concept and pre-jam tooling records are retained and disclosed in the development log. No claim is made that revising those documents changes their original creation dates.

## Thanks

Thanks to **Epic Games** for organizing the 2026 Epic AI MegaJam, and to **Tripo** and **fal** for supporting the jam with creation tools and credits. Thanks to everyone who provided playtest feedback.

## Integration notes — omit this section from the public page

- This is ready-to-edit copy, not an uploaded page. Claude/the entrant should match the controls to the final build before publication; the table follows GDD v1.3 and the task card, not a new Codex playtest.
- The game is intended for Windows keyboard/mouse play. Add the actual build download, install instructions and known issues after packaging; no finished package is claimed here.
- Update the AI paragraph to reflect only models, music and source assets selected for the shipped build. Do not describe an unused candidate as a shipped asset.
- Add the actual public development-log link and gameplay video when the entrant publishes them. Do not publish account emails in the page body.
- Clarification of the earlier GDD's eligibility remains the entrant's responsibility; this draft does not resolve that question.
