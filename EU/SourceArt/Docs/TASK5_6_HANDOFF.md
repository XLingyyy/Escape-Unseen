# Task 5 / 6 implementation handoff

## Task 5A — explicit exit interaction

2026-11-13 UTC. Root cause confirmed in PIE: ExitZone's mesh component used its mesh default collision (`bUseDefaultCollision`), producing BlockAll / QueryAndPhysics despite the serialized profile name NoCollision. L03 swept capsule stopped at X=1138.725 before the exit's X=1170 edge. All three ExitZone components now explicitly disable default collision and use NoCollision. Door, exit lamp and lamp shade decoration components were already non-colliding; no geometry moved.

Phase 4 no longer automatically finishes on entering ExitZone. E routes through TryInteract, with exit priority over TryCut. Completion immediately plays SFX_LevelWrap, stops motion, fades to black over 0.5 s, displays WRAP for 1.2 s, then opens the next level; the final room displays “You escaped unseen.” with Enter replay / Q quit. BP_EscapeGameInstance.LevelOrder is the sole level-order array; the default engine config selects this GameInstance.

Validation: affected Blueprints compiled. L03 capsule sweep reached X=1325; after entering the exit Phase remained 4 and CanEscape=true. TryInteract changed Phase to 6; WrapShown=true and SlateText=WRAP after 0.7 s. Runtime level index=2, final=true, next/replay=L01_FirstStep. Actual Canvas screenshot: `EU/Saved/review/task5_exit_prompt.png`. Temporary test actor removed before save. No complete playthrough, packaging, or push performed. Non-final automatic map loading was not exercised in this targeted check.

## Task 5B — room-wide lamp placement

Removed LightZoneMin/Max clamping. The lamp now uses each room's BuildMin/BuildMax inset by 30 cm, plus a 30 cm minimum Euclidean distance from the XZ bounds of fixed Occluder-tagged solids. These room bounds are per-level (L01: 1500×1000 cm; L03: 1500×1150 cm). Rejected moves leave the previous light position and shadow geometry intact, and draw a red cross at the cursor. Existing light reference positions and the shadow service's original too-near rejection remain unchanged.

Validation: Director and HUD compiled. In L01, the reference (500,800) remains legal; (80,920), far outside its former lamp zone, was accepted. X=29 was rejected. Dragging into Beam left the lamp at (80,920) and set bLightRejected=true. Occluder geometry inspected in this test includes Floor, both side walls, ExitLedge and Beam; BackWall is excluded. Actual Canvas screenshots: `task5_lamp_far.png`, `task5_lamp_reject.png`. Temporary actor removed, PIE stopped and assets saved. No reference-solution playthrough or packaging performed.
