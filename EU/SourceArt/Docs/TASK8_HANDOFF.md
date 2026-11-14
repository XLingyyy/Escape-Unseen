# Task 8 handoff

## 8.0 — v1 fallback package

Package and requested input verification complete. Source gameplay revision:
`v1-playable`, commit `6908dd9`.
No Task 8 gameplay changes are included in the fallback package.

Packaging repairs identified on 14 November 2026 UTC:

- The first Development game build succeeded with the existing MSVC toolchain.
  Cook initially requested a missing `EUEditor.target` receipt. An editor-target
  rebuild was blocked by the open editor's Live Coding session. Packaging now
  reuses the completed game build and explicitly selects the installed
  `UnrealEditor-Cmd.exe` for Cook.
- Zen cooked-output initialization stalled while establishing its oplog.
  That Cook process was stopped, and the supported `-SkipZenStore` cooker option
  selects file-based output. Project, system and network settings were not
  changed for this workaround.
- Cook then processed all game resources but failed because the GameFeatures
  subsystem required a `GameFeatureData` primary-asset rule. The enabled
  AllToolsets dependency activates this subsystem. `Config/DefaultGame.ini`
  now contains the same empty-directory registration produced by UE's own
  `AddDefaultGameDataRule()` function. This packaging configuration repair is
  the sole difference from the tagged source; the tag remains unchanged.

BuildCookRun completed with exit code 0. All nine maps were explicitly included.
Output: `F:\EU_Builds\v1\Windows\`.

- ZIP: `F:\EU_Builds\v1\EscapeUnseen_v1_Win64_Development.zip`,
  445,118,097 bytes (424.5 MiB).
- Uncompressed content: 43 files, 732,547,071 bytes (698.6 MiB).
- ZIP extracted to `F:\EU_Builds\v1\Extracted\` and its `Windows\EU.exe`
  launched. The packaged log confirms successful engine initialization and
  loading `/Game/EscapeUnseen/Maps/L00_FirstCut`; no Error/Fatal lines were
  present at that point. This does not establish input behavior.
- The user manually confirmed all three requested behaviors: Enter proceeds
  from the title into L00, Esc opens/closes pause, and Q exits from the title.

Cook also reported an obsolete dependency from L04 to the deleted temporary
bridge package. It was a display-level diagnostic and did not prevent Cook,
staging or archive completion. No bridge asset is shipped or recreated.

The user authorized the official `@oai/sky` API through a Node CLI script because
this session lacks `node_repl`. The API subsequently rejected window access with
`Computer Use requires app approval but elicitations are unavailable`. No
approval settings were changed and no alternate desktop input mechanism was
used. The user completed the actual packaged Enter, Esc and Q verification.

Local build logs and the authorized desktop helper are in
`EU/Saved/codex_task8/` (ignored work files).

## 8.1 — consistent hero model

The reported persistent L01 squash did not reproduce in the current PIE session.
Measured L01 actor scale is (1,1,1), model child scale (1,1,1), model bounds
45 x 58 x 125 cm, Squash=0 and IsFalling=false. The parent mesh only exhibits
its existing roughly 2% breathing animation. No extra scale compensation was added.

A separate, confirmed visual inconsistency was fixed: L00 and L03-derived maps
retain old instance overrides (bUseModel=false and null model/material), while
L01/L02 inherit the imported prisoner model. BP_EscapeCharacter.BuildVisual now
uses the canonical SM_Prisoner and MI_Prisoner when bEnableHeroModelFix=true
(the new default). Turning it off executes the complete previous BuildVisual
branch, including those per-instance choices. Existing animation is unchanged.
The disabled branch was observed rendering the original eight-part L00 placeholder;
the enabled branch was then checked in every map.

Nine native 1920 x 1080 standing captures:
EU/Saved/review/task8_hero_L00.png through task8_hero_L08.png.
Each runtime report confirms one SM_Prisoner component, zero falling, unit actor
and child scale, and the same mesh bounds. Images were visually inspected.
The fixture invokes StartPlay directly to expose the standing actor; these are
appearance checks, not nine solved-level playthroughs. Per-map records are in
EU/Saved/codex_task8/hero_after_*.json.

## 8.2 — horizontal light rail

Implemented in BP_ShotDirector and BP_EscapeHUD with EnableLightRail=true.
Per-map RailMinX, RailMaxX and RailZ are instance-editable. All nine maps have
four preplaced, movable rail actors: 8 cm pipe at RailZ+25, 12 cm end seats,
and a 25 cm hanging rod attached to RuleBulb. They have no collision, no
Occluder tag and no cast shadow. MI_LightRail copies MI_SetPiece with its Color
multiplied by .25; the shared original material is retained.

| Map | X range (cm) | RailZ (cm) |
|---|---:|---:|
| L00 | 1050–1400 | 1000 |
| L01 | 250–750 | 800 |
| L02 | 250–750 | 900 |
| L03 | 1050–1400 | 1000 |
| L04 | 450–950 | 1100 |
| L05 | 450–950 | 1100 |
| L06 | 600–1100 | 1080 |
| L07 | 1050–1400 | 1110 |
| L08 | 1050–1400 | 1110 |

Ranges use actual wall inner faces X=0/1500 and the existing point-to-facility
30 cm clearance rule. All reference lamp positions remain within their rails.
The lampshade Z scale is .54533 while enabled to leave 2 cm below the pipe;
logical lamp position, shade XY scale and pivot remain unchanged. The original
shade scale is stored and restored when the switch is disabled.

Directional test in L01: (-500,200) clamps to (250,800); (9999,2200) clamps to
(750,800). Disabling accepts the prior free-placement point (80,920), hides the
pipe/ends/rod and restores the shade's unit scale. Re-enabling restores the rail
and reference point (500,800). The phase-0 2 px amber rail line is visible in
EU/Saved/review/task8_rail.png. Blueprints compiled and maps saved.
Per-map bounds/placements and test results: EU/Saved/codex_task8/rail/*.json.
Prior reference-approval results are reused because shadow geometry and its
predicate are unchanged; no additional nine-map approval loop was run.

## 8.3 — physical crate pushing

Implemented in BP_Block, BP_EscapeCharacter, BP_EscapePC and BP_ShotDirector,
with bEnableCratePush=true. Only phase 4 enables crate simulation with SixDOF:
all rotations and Y translation locked, X/Z free. The nine maps retain their
existing build/approval behavior and have explicit SFX_CrateLand bindings.
Grounded side contact drives the nearest crate at 150 cm/s and the hero at
150 cm/s; ordinary walking remains 400 cm/s. StepAnim selects a 10-degree
forward lean while pushing. SFX_CratePlace repeats at pitch .65 during pushing;
the guarded native landing-hit path plays SFX_CrateLand.

Runtime inspection found the imported hero visual still had BlockAllDynamic
collision despite AddPart's SetCollisionEnabled call. Its mesh-default collision
was overriding that setting and imparting excess force to crates. In enabled
phase 4, the capsule now uses QueryOnly and visual StaticMeshComponents use the
NoCollision profile. This keeps CharacterMovement sweeps/standing support while
removing Chaos contact impulses from the hero. Disabling restores the observed
v1 capsule QueryAndPhysics and visual BlockAllDynamic settings; the existing
native enable_physics_interaction=false remains unchanged. The engine distinction
is documented in [Epic's collision reference](https://dev.epicgames.com/documentation/unreal-engine/collision-response-reference-in-unreal-engine?lang=en-US).

A native L03 PIE fixture observed actual crate X velocity near -150 cm/s,
unchanged Y and rotation, a real edge fall, and rest at floor+50 cm with velocity
(.099,0,-.022) cm/s. An airborne side-contact attempt left crate X unchanged.
Actual TryCut restored B at X=1000 and discarded moved A; Retry restored A at
X=650. Snapshot arrays remained unchanged. Master=false restored frozen crates,
hero speed 400 and the original capsule collision mode. These fixtures seed
runtime snapshots through public functions; they do not claim approval or full
level traversal. The landing audio binding and guarded arm-reset path were
observed indirectly; audio was not listened to.

Native 1920x1080 captures: EU/Saved/review/task8_push.png and task8_fall.png,
visually inspected. Detailed evidence: EU/Saved/codex_task8/push/verify_push_result.json.
The editor's background 3 FPS throttle was temporarily disabled for these
physics observations and restored without saving preferences. Blueprints compiled
and all nine maps saved.

## 8.4–8.5

Pending integration. Task 8.5 was added by the user during implementation.
No v2 gameplay assets are included in the fallback package.
