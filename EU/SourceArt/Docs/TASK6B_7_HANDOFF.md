# Task 6B and Task 7 handoff

## Task 6B — completed 2026-11-14 UTC

Canvas HUD: top hint at Y=40, centered in X=600–1880, maximum width 1000; hidden in phases 2/3. Inspection bars are 110 px with Bebas 64 title, Courier 26 subtitle, right aligned keys and full width 4 px progress. Scene card fades during inspection. Hint/key/card opacity checks the mouse, rule lamp and character head, transitioning between 1 and .25 over .15 seconds. Wording uses crates; lamp line is “Drag the lamp. Its shadows are your hiding places.”

Title displays ENTER START and Q QUIT. Q shares the normal QuitGame branch with the final card. An actual desktop Q press in a focused title viewport ended PIE; MCP confirmed IsPIERunning=false and only the editor window remained. Slate synthetic input alone had not established gameplay focus; the successful result uses the real key path.

Validation: HUD, PC and Director compiled. Four native 1920×1080 images were visually inspected: EU/Saved/review/task6B_build.png, task6B_inspection.png, task6B_fade.png, task6B_title.png. Inspection follows actual placement and approval. The legal L01 lamp at (1050,930) projected to (1243.32,73.19), inside hint rect (772,40,936,73), with mouse outside; HintOpacity=.25. The callback sampled after .328 s; .15 s is the implemented delta-based 5/s interpolation, not a high-frame-rate measurement. Input/tick settings restored. Evidence: Saved/codex_task6b/capture_report.json and qtest_result.json. No full traversal, packaging or push.

Task 6B item 0: prior dirty text came from the Codex level-design commission and is included with its approved design/SVG. Original text line endings/BOM were preserved. Character export content matched except an editor component naming counter; ShadowService compiled functions/CDO matched, with changes limited to graph reconstruction. L01 had editor ordering/view changes and its existing NoCollision profile serialized explicitly to matching engine defaults. These three resaves are restored to HEAD with UE closed. Evidence: Saved/codex_task6b/dirty_origin.md. No unknown authored gameplay changes were found.

Delegation: ui_6b_dsl prepared offline HUD/capture source; dirty_origin traced serialized changes; level_manifest prepared Task 7 data/logic offline. Root performed UE edits and runtime verification. Canvas reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/HUD/DrawText
