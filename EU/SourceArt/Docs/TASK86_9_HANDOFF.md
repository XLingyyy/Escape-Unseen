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

Completed after Task 8.6 (commit `714910d`). All changed Blueprints compiled and saved. Task 10 mainline layouts and LevelOrder are unchanged.

### Delivered behavior and integration

- New `BP_MovingPlatform`: movable solid steel body, 200×280×30 cm, MI_SetPiece color ×0.35, two weak amber 6 cm warning strips. Body has BlockAll collision and casts shadows; Actor tags are Occluder and MovingOccluder. The 280 cm depth leaves 10 cm clearance from the existing back wall.
- Instance-editable `TravelOffset`, `Vertical`, `AverageSpeed` and `InitialPhase` select a signed world X/Z path, up to 400 cm, average speed 100–150 cm/s, and initial cycle phase 0–1. Each endpoint holds for 0.6 seconds; travel uses a half-cosine curve. A 400 cm path at 125 cm/s takes 3.2 seconds each way and 7.6 seconds per cycle.
- Construction records the placed center as Endpoint0 without moving it. BeginPlay applies InitialPhase once. Tick runs independently of Director phase; StartPlay, cut and retry do not reset it. Blocking freezes both position and cycle time until the obstacle leaves.
- Full-body sweep and a separate based-character clearance sweep prevent crushing. Native CharacterMovement carries a standing character. `GetSweepBounds()` returns the raw union of endpoint body bounds; Director adds 10 cm for placement exclusion and returns red BLOCKED.
- ShadowService caches fixed geometry in BaseShadowPts/BaseShadowCounts. CheckBlock, CheckPoint and DrawShadows refresh moving occluders from their current bounds on every query. Approval, patrol, head/chest exposure, spawn ghost, crate preview and guides share these entry points.
- During approval inspection, the first failed InspectOK immediately calls FailInspection. Settling remains separate. The existing patrol interval already runs from the guard's full departure until the next inspection (10–20 seconds, including the five-second warning), so no timer rewrite was needed.
- HUD draws endpoint shadow outlines in amber, 2 physical pixels wide, with 12-pixel dashes/gaps. Their convex intersection uses 15% Cyan via MI_PlatformShadowPreview. These appear in phase 0 or whenever ShadowGuides is enabled, using the current light position.
- Maps wider than 1500 cm use UpdateWideCamera: phase 4 follows Hero X with a total 300 cm deadzone and FInterpTo speed 6; phases 0/1 pan at 800 cm/s from A/D or the outer 60 physical mouse pixels. Bounds use the actual perspective lens and room limits. Small-map camera behavior is preserved. Existing off-screen guard-window suppression already leaves only the top warning banner.

**Placement contract:** the Cube root's scale `(2, 2.8, 0.3)` is part of the platform dimensions. Preserve this scale when placing Task 10 instances; do not overwrite it with unit scale. Platform endpoint coordinates are body centers. Strip transforms compensate for the root scale.

New assets: `Core/BP_MovingPlatform`, `Materials/MI_MovingPlatform`, `MI_MovingPlatformStripe`, `MI_PlatformShadowPreview`, and `Tests/L_Task9_Mechanics`. Modified assets: `Core/BP_ShadowService`, `BP_ShotDirector`, `BP_EscapeHUD`, `BP_EscapePC`. Paths are beneath `EU/Content/EscapeUnseen/`. Task 9's incidental L03 editor resave was restored to the committed Task 8.6 state.

### Actual validation

Two completed native PIE fixtures are recorded in `EU/Saved/codex_task9/verify/verify_motion_result.json` and `verify_visibility_result.json`; both have no cleanup errors. They use natural world/platform time, controlled runtime placements and public methods. No Phase or platform clock was assigned. PC Tick and patrol were temporarily isolated; all altered settings were restored. These runs do not represent manual traversal or keyboard input.

| Check | Observed result |
| --- | --- |
| Horizontal/vertical motion | Both completed the natural 7.6 s cycle. Sampled endpoint holds were 0.596/0.585 s, consistent with configured 0.6 s at frame resolution. |
| Cut/retry continuity | StartPlay, TryCut and Retry preserved platform position and phase. |
| Collision waiting | Crate and Hero separately stopped the horizontal platform; position and phase stayed fixed during each 0.3 s observation, then resumed when the obstacle was removed. |
| Standing rider | During 0.658 s, the vertical platform rose 67.03 cm and Hero rose 67.99 cm; Hero remained grounded and based on the platform. |
| Camera | 800 cm/s pan, actual left/right mouse-edge routing, 300 cm deadzone, smooth follow, lens-based bounds and small-map preservation passed. |
| Current moving shadow | At opposite horizontal endpoints, the same crate, point, Hero and spawn ghost changed between hidden and exposed; ghost color changed and the fixed baseline arrays stayed unchanged. |
| Build exclusion | A crate centered at X=545, Z=500 was rejected by the 10 cm padding; X=535 was accepted. BLOCKED preview was captured. |
| Endpoint preview | The vertical platform's native endpoint intersection had four vertices and area 60,968.36 cm²; amber outlines and Cyan fill were visually confirmed. |
| Continuous approval | With temporary StableWindow=4 s and PhaseTimeout=8 s, natural platform movement exposed the crate. RETAKE occurred 0.02482 s after the first observed exposed frame (0.04709 s after the last hidden sample); ApprovedA stayed false. Defaults were restored. |

Four native 1920×1080 captures were inspected: `EU/Saved/review/task9_platform_ride.png`, `task9_platform_shadow_preview.png`, `task9_platform_blocked.png`, `task9_approval_dynamic_retake.png`. Preview capture includes transient motion blur from the fixture's camera placement; outlines and fill remain visible.

The development map is 2400×1150 cm and is outside LevelOrder. Horizontal endpoints are `(700,0,500)` and `(1100,0,500)`. Final vertical endpoints are `(1450,0,200)` and `(1450,0,600)`; it was moved from X=1800 after the motion run to make the endpoint shadow overlap visible. Both use speed 125 and phase 0. The inherited scene title is a fixture label, not a new mainline level.

No additional manual A/D input, horizontal riding, overhead-obstacle scenario, full timed patrol with platforms, light dragging, guide-toggle UI, level traversal, audio listening or package build was run. Shared query wiring and existing off-screen warning logic were inspected; these are distinct from the runtime checks above.

### Resolved integration findings and final state

Initial full-depth platforms touched the back wall. Native HitResult confirmed initial overlap against BackWall; reducing actual body depth from 300 to 280 cm fixed it without shrinking the sweep relative to the body. A Blueprint reinstance attempted inside the bridge ConstructionScript caused an editor assertion; saved assets were recovered on restart and the structural edit completed through a deferred post-tick callback. Do not compile/reinstance actor classes inside that bridge's ConstructionScript.

Fixture-only fixes included copying Vector2D values before temporary camera-bound edits, using public SetCursor, unpacking IntersectPolygons' Python return as `(A, B, Poly)`, and delaying first capture until one second of natural game time. The previous first-frame Shot request was consumed by the editor viewport; the final captures show the actual PIE HUD at 1920×1080.

Bounded agents prepared platform/HUD/camera bodies, validation and documentation offline. The root agent performed all UE writes, compilation, native integration, screenshot inspection and acceptance. Final cleanup stopped PIE, removed the temporary bridge, restored play-window settings, saved assets and returned the editor to L00. No push, package or competition submission was performed; Task 10 has not started.
