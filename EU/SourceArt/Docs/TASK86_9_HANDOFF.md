# Task 8.6 / Task 9 handoff

## Task 8.6 — actor visibility during patrol

Completed and compiled: BP_ShadowService, BP_ShotDirector, BP_EscapeHUD, BP_SpawnMark. No level geometry or reference solution changed. L00's loaded Director instance was migrated to the new enabled default; L03 was saved after the temporary bridge was removed. Other maps inherit the enabled class default on load.

- ShadowService.CheckPoint reuses the existing ExposedFragments subtraction and Margin=0.5 cm. Head/chest are at current capsule feet Z+120/+85 cm; either exposed point fails. Hero has no Occluder tag. Approval does not check Hero.
- PatrolInspectionTick checks Hero first each frame, then crates. Both exposed records ACTOR SEEN; crate-only records CRATE SEEN. Existing RETAKE, 1.2-second restart and approved snapshots remain in use. bEnableActorPatrolCheck is instance editable, default true; false restores crate-only patrol and hides the added feedback.
- The world-anchored Canvas eye is about 44 design pixels, head+45 cm, amber/open/pulsing when exposed and Paper/closed/60% alpha when hidden. It fades over 0.2 seconds. Failure reason is Paper Courier Prime 28 under RETAKE; the culprit's projected collision bounds flash amber in three 0.1-second pulses within 0.6 seconds.
- Planning phases 0/1/2/3 query the same two points for the spawn ghost. Exposure changes it to amber with START · IN LIGHT; tape stays Paper. Existing breathing and action fade remain.
- L00's current TutorialMessage had no patrol line. The actual visible DrawContextHint warning branch now shows `Footsteps! Hide yourself and every crate.` under the warning banner, only when TutorialEnabled and actor checking are enabled. Task 10 tutorial events are not implemented here.

### Actual validation

Two fresh L03 native 1920×1080 PIE runs, with the public interval bounds temporarily fixed to 12 seconds and restored. No Phase, countdown, inspection elapsed or failure timestamp was assigned. Runtime placement and snapshot seeding supplied controlled stimuli; this was not full level traversal.

- Exposed Hero plus hidden crate passed one real approval. Eye was absent during approval.
- Natural warning count 3 showed the exposed/open eye; hidden subjects began inspection safely. At inspection elapsed >=0.25 seconds, both Hero and crate were exposed together. Failure was recorded 0.020723 seconds later with ACTOR SEEN and Hero as target. Existing StartPlay restarted A after 1.2 seconds with snapshots unchanged.
- Hidden Hero and crate passed a full natural patrol inspection; eye alpha reached zero after the exit fade.
- On the next natural visit, disabling actor checking ignored exposed Hero, while an exposed crate still triggered CRATE SEEN and RETAKE.
- Hero's actor tags exclude Occluder. Point-function checks cover altered feet height; actual jumping was not performed in this fixture.
- All four requested native screenshots were visually inspected: `EU/Saved/review/task8_6_eye_exposed.png`, `task8_6_eye_hidden.png`, `task8_6_actor_seen.png`, `task8_6_ghost_lit.png`.
- Evidence: `EU/Saved/codex_task86/verify/verify_exposed_result.json` and `verify_hidden_result.json`, both complete with no cleanup errors. No package build or audio listening was performed.

### Integration findings

The EditorToolset caches node menus per owning Blueprint graph and does not invalidate HUD caches when Marker interfaces change. Targeted HUD `_BlueprintCache.invalidate` exposed the new SpawnExposed property. Actor object parameters are unsupported by add_function_param, so the outline helper reads the existing Director failure target directly. Generic string equality inferred an incompatible float pin; the reason branch now uses an explicit string operation. A stopped batch initially omitted two function bodies; native validation exposed the empty eye updater, both missing bodies were installed, compiled, and the two runs above completed. Line/Rect alpha is carried in the actual color, preserving the eye fade.

Bounded agents prepared HUD/spawn bodies and the fixture offline. The root agent performed all UE writes, integration, compile, native runs, screenshot inspection and acceptance.

## Task 9

Implementation follows Task 8.6. No Task 10 level construction is included in this authorization.
