# Task 5 / 6 implementation handoff

## Task 5A — explicit exit interaction

2026-11-13 UTC. Root cause confirmed in PIE: ExitZone's mesh component used its mesh default collision (`bUseDefaultCollision`), producing BlockAll / QueryAndPhysics despite the serialized profile name NoCollision. L03 swept capsule stopped at X=1138.725 before the exit's X=1170 edge. All three ExitZone components now explicitly disable default collision and use NoCollision. Door, exit lamp and lamp shade decoration components were already non-colliding; no geometry moved.

Phase 4 no longer automatically finishes on entering ExitZone. E routes through TryInteract, with exit priority over TryCut. Completion immediately plays SFX_LevelWrap, stops motion, fades to black over 0.5 s, displays WRAP for 1.2 s, then opens the next level; the final room displays “You escaped unseen.” with Enter replay / Q quit. BP_EscapeGameInstance.LevelOrder is the sole level-order array; the default engine config selects this GameInstance.

Validation: affected Blueprints compiled. L03 capsule sweep reached X=1325; after entering the exit Phase remained 4 and CanEscape=true. TryInteract changed Phase to 6; WrapShown=true and SlateText=WRAP after 0.7 s. Runtime level index=2, final=true, next/replay=L01_FirstStep. Actual Canvas screenshot: `EU/Saved/review/task5_exit_prompt.png`. Temporary test actor removed before save. No complete playthrough, packaging, or push performed. Non-final automatic map loading was not exercised in this targeted check.
