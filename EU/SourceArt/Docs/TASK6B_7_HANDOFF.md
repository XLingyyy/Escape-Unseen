# Task 6B and Task 7 handoff

## Task 6B — completed 2026-11-14 UTC

Canvas HUD: top hint at Y=40, centered in X=600–1880, maximum width 1000; hidden in phases 2/3. Inspection bars are 110 px with Bebas 64 title, Courier 26 subtitle, right aligned keys and full width 4 px progress. Scene card fades during inspection. Hint/key/card opacity checks the mouse, rule lamp and character head, transitioning between 1 and .25 over .15 seconds. Wording uses crates; lamp line is “Drag the lamp. Its shadows are your hiding places.”

Title displays ENTER START and Q QUIT. Q shares the normal QuitGame branch with the final card. An actual desktop Q press in a focused title viewport ended PIE; MCP confirmed IsPIERunning=false and only the editor window remained. Slate synthetic input alone had not established gameplay focus; the successful result uses the real key path.

Validation: HUD, PC and Director compiled. Four native 1920×1080 images were visually inspected: EU/Saved/review/task6B_build.png, task6B_inspection.png, task6B_fade.png, task6B_title.png. Inspection follows actual placement and approval. The legal L01 lamp at (1050,930) projected to (1243.32,73.19), inside hint rect (772,40,936,73), with mouse outside; HintOpacity=.25. The callback sampled after .328 s; .15 s is the implemented delta-based 5/s interpolation, not a high-frame-rate measurement. Input/tick settings restored. Evidence: Saved/codex_task6b/capture_report.json and qtest_result.json. No full traversal, packaging or push.

Task 6B item 0: prior dirty text came from the Codex level-design commission and is included with its approved design/SVG. Original text line endings/BOM were preserved. Character export content matched except an editor component naming counter; ShadowService compiled functions/CDO matched, with changes limited to graph reconstruction. L01 had editor ordering/view changes and its existing NoCollision profile serialized explicitly to matching engine defaults. These three resaves are restored to HEAD with UE closed. Evidence: Saved/codex_task6b/dirty_origin.md. No unknown authored gameplay changes were found.

Delegation: ui_6b_dsl prepared offline HUD/capture source; dirty_origin traced serialized changes; level_manifest prepared Task 7 data/logic offline. Root performed UE edits and runtime verification. Canvas reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/HUD/DrawText

## Task 7 — L00 First Cut, completed 2026-11-14 UTC

L00_FirstCut duplicates L03 through AssetTools; all four facilities are preplaced and saved with exact design/collision bounds. One editable crate is reused in A/B. BudgetA/B preserve zero-value fallback on old maps. TutorialMessage supplies the current tutorial line; normal Message remains available for inspection/failure feedback. StartPlay respects StartPoint yaw. Startup maps now select L00; LevelOrder currently contains completed L00–L03, with scene numbering matching array indices.

Reference lamp (1300,1000), A crate (350,50), B crate (900,250): both approvals passed, one request per shot. Tutorial first/light-lock/A-build/B-build/approval/action text observed. Actual action spawn (150,0,67), yaw0. Camera retained at (750,2000,560), pitch−2/yaw−90, FOV58: door, exit lamp, highest facility and rule lamp/shade bounds fully in viewport. Native 1920×1080 screenshots: Saved/review/task7_L00.png and task7_L00_tutorial_first.png. Evidence: Saved/codex_task7/task7_L00_report.json. No jump traversal performed.

During initial map duplication, a Python World reference prevented garbage collection on load and crashed UE. The duplicated file survived; temporary references were released before map load, unsaved Blueprint edits were reapplied/compiled/saved, and L00 was completed from the saved duplicate. No fixed geometry is generated at BeginPlay.

## Task 7 — L04 Double Duty, completed 2026-11-14 UTC

Map `Content/EscapeUnseen/Maps/L04_DoubleDuty.umap` follows design L04; 3 fixed facilities are editor-preplaced with shared visible/collision/shadow bounds. Inventory A=3, B=3, pool=3; A is editable. Reference XZ coordinates in cm: lamp (700, 1100); A: #01 (350, 50), #02 (450, 50), #03 (450, 150); B: #01 (750, 350), #02 (850, 350), #03 (850, 450). Both reference approvals passed.

Action spawn (150, 0, 67), yaw0; the editor spawn includes 2cm contact clearance. Door scale 1, bottom Z600, top Z840.00; exit-lamp top Z866.00. Guard (300, -150, 650), scale1.4, window XZ bounds (216, 643, 384, 769); minimum facility clearance 184.71cm and horizontal reference-lamp gap 316.00cm.

Camera (750, 2000, 560), rotation (-2, -90, 0); position/rotation retained from L03, FOV58 changed to 62. Door, exit lamp, highest facility (Shade Bar), rule lamp and shade bounds are fully inside the viewport. Initial FOV58 clipped RuleBulb, Decor_LampShade; a camera-only recapture at FOV62 fixed framing and reused the completed A/B approvals. Native screenshots: Saved/review/task7_L04.png. Evidence: Saved/codex_task7/task7_L04_report.json, Saved/codex_task7/task7_L04_camera_report.json. No jump traversal, packaging or push was performed.
