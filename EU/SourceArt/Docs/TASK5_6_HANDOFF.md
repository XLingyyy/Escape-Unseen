# Task 5 / 6 implementation handoff

## Task 5A — explicit exit interaction

2026-11-13 UTC. Root cause confirmed in PIE: ExitZone's mesh component used its mesh default collision (`bUseDefaultCollision`), producing BlockAll / QueryAndPhysics despite the serialized profile name NoCollision. L03 swept capsule stopped at X=1138.725 before the exit's X=1170 edge. All three ExitZone components now explicitly disable default collision and use NoCollision. Door, exit lamp and lamp shade decoration components were already non-colliding; no geometry moved.

Phase 4 no longer automatically finishes on entering ExitZone. E routes through TryInteract, with exit priority over TryCut. Completion immediately plays SFX_LevelWrap, stops motion, fades to black over 0.5 s, displays WRAP for 1.2 s, then opens the next level; the final room displays “You escaped unseen.” with Enter replay / Q quit. BP_EscapeGameInstance.LevelOrder is the sole level-order array; the default engine config selects this GameInstance.

Validation: affected Blueprints compiled. L03 capsule sweep reached X=1325; after entering the exit Phase remained 4 and CanEscape=true. TryInteract changed Phase to 6; WrapShown=true and SlateText=WRAP after 0.7 s. Runtime level index=2, final=true, next/replay=L01_FirstStep. Actual Canvas screenshot: `EU/Saved/review/task5_exit_prompt.png`. Temporary test actor removed before save. No complete playthrough, packaging, or push performed. Non-final automatic map loading was not exercised in this targeted check.

## Task 5B — room-wide lamp placement

Removed LightZoneMin/Max clamping. The lamp now uses each room's BuildMin/BuildMax inset by 30 cm, plus a 30 cm minimum Euclidean distance from the XZ bounds of fixed Occluder-tagged solids. These room bounds are per-level (L01: 1500×1000 cm; L03: 1500×1150 cm). Rejected moves leave the previous light position and shadow geometry intact, and draw a red cross at the cursor. Existing light reference positions and the shadow service's original too-near rejection remain unchanged.

Validation: Director and HUD compiled. In L01, the reference (500,800) remains legal; (80,920), far outside its former lamp zone, was accepted. X=29 was rejected. Dragging into Beam left the lamp at (80,920) and set bLightRejected=true. Occluder geometry inspected in this test includes Floor, both side walls, ExitLedge and Beam; BackWall is excluded. Actual Canvas screenshots: `task5_lamp_far.png`, `task5_lamp_reject.png`. Temporary actor removed, PIE stopped and assets saved. No reference-solution playthrough or packaging performed.

## Task 5C — pause and session settings

Esc toggles the menu through the PlayerController's mutually exclusive pause/input branches. SetGamePaused freezes world simulation and inspection timers. W/S/arrows navigate, A/D/arrows change values, Enter/E activate, and Canvas hitboxes support mouse clicks. Mouse actions wait for button release, preventing Resume from carrying a held drag into the game.

SHADOW GUIDES defaults OFF and gates only blue shadow boundaries; crate cyan/red feedback remains. MUSIC defaults to 4 (AudioComponent gain 0.45), SOUND defaults to 8. SC_Music separates the music from the Master sound class; SM_Settings changes active and future non-music sounds. Settings are held by BP_EscapeGameInstance, with no disk save. The native AudioComponent.SetVolumeMultiplier call uses an explicit declaring class because the tool's unqualified node ID also matches SynthComponent.

Validation: affected Blueprints compiled. Actual paused inspection Phase=2 retained PhaseTime=0 and StableTime=0 across elapsed wall time. Mouse MUSIC+ and Right changed 4→6 and live music gain 0.45→0.675; Down/Left changed SOUND 8→7. Resume unpaused. A real L01 exit transition opened L02 automatically; MUSIC=5, SOUND=7 and GUIDES=ON survived, L02 gain=0.5625 and menu closed. This also verifies 5A's non-final automatic travel. Default OFF screenshot retains the cyan crate preview. Screenshots: `task5_menu.png`, `task5_guides_off.png`.

Editor limitation: its default Esc shortcut stops PIE before gameplay receives the key. The game's Esc toggle branch is implemented; direct Esc testing in this editor session was intercepted. Keyboard navigation, mouse actions, pause and resume were exercised. Editor shortcut preferences were not changed. No packaged run or complete level playthrough was performed.

All Task 5 edits saved with PIE stopped and the temporary actor removed. Review remains with Claude.

## Task 6 — screenplay-style Canvas HUD

Completed 2026-11-13 UTC. BP_EscapeHUD now uses Bebas Neue for headings/keys and Courier Prime Regular/Bold for body/status text. Three Runtime UFonts and three FontFaces are saved under `/Game/EscapeUnseen/UI/Fonts/`; the original TTFs, both OFL licenses, import report and official source URLs are retained in `EU/SourceArt/Fonts/`. Provenance records the downloaded fonts and the derived assets.

The HUD implements the specified scene card/clapper strip, measured and wrapped script hint, available-key bar, projected E prompts, lamp drag/blocked indicators, explicit HIDDEN/LIT symbols, settling labels, inspection framing/progress, rotated LOCKED/RETAKE/WRAP stamps, title/end cards and pause-menu typography. All layout uses viewport-height / 1080 scaling. The inspection banner has a 72%-black backing for readability against the bright room. Preview/settling labels stay above the script hint. Missing font symbols are drawn as Canvas geometry.

Director.PreviewHidden reuses PlacementValid, inventory and ShadowService.CheckBlock(Ghost), so preview color and label agree with the inspection geometry. Ghost's actual scale is (1,1,1). In the tested L01 lamp position (500,800), (1050,50) was correctly reported exposed and (1100,50) was HIDDEN and passed actual inspection. Lamp dragging starts on the lamp hit radius; rejected moves retain Task 5B's last legal position.

`M_UIStamp` uses a runtime Canvas red-channel mask plus a tint. Canvas material draws need display-encoded tint values, whereas text/rect helpers use linear palette values; the MID values preserve the specified hex colors. `M_UIVignette` is a native UV-distance material capped at 25% opacity. Its Saturate input uses the native unnamed pin. Float loop indices are explicit in circle/ring/key geometry to avoid integer truncation.

Validation: affected Blueprints compiled and assets saved through MCP. Eight native Shot PNGs were captured at an actual 1920x1080 viewport, with no resampling. The final set was visually inspected. Inspection and LOCKED came from real RequestApproval/Commit transitions; Cut required OnMark and BClear, and the exit required CanEscape. Mark/exit screenshots use character teleport solely to position the UI fixture. The inspection screenshot briefly held Director tick after real progress; all tick/pause/drag state was restored. The original editor play-window settings were restored, PIE stopped, temporary actors were absent, and the temporary bridge asset was deleted.

Screenshots under `EU/Saved/review/`:

- `task6_L01_lamp.png`
- `task6_L01_build.png`
- `task6_inspection.png`
- `task6_locked.png`
- `task6_cut_prompt.png`
- `task6_exit_prompt.png`
- `task6_menu.png`
- `task6_title.png`

Detailed runtime states: `EU/Saved/codex_task6/_capture/capture_report.json`. Task 5's direct Esc limitation in PIE still applies. The screenshot fixture opened the pause menu through its gameplay function. RETAKE/WRAP and the final ending share the implemented rendering paths, but were not separately captured in Task 6. No complete traversal, packaged run, push or competition submission was performed. Task 7 was not started. Visual acceptance remains with Claude.

During authoring, the editor crashed after a synchronous material operation in a construction-script bridge. Saved assets were recovered; subsequent material mutation was deferred until the construction call returned. This was an editor-authoring incident, not a gameplay crash observed in the final PIE run.
