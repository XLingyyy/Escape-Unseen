# Canvas UI source notes

Task 6 assets are in `/Game/EscapeUnseen/UI/`; the rendered UI remains in BP_EscapeHUD. `create_hud_materials.py` recreates the two project-authored UI materials through Unreal's native MaterialEditingLibrary. Run it in editor Python outside a Construction Script; a caller using a temporary construction bridge must defer the operation to a later Slate tick.

Fonts and OFL notices are in `../Fonts/`. Runtime UFonts have a 64 pt Default typeface. Helpers convert design pixels using `Size*0.75/64`, then apply viewport-height / 1080. Keep Canvas text/rect colors linear; the stamp MID receives display-encoded RGB because Canvas material output bypasses the text color conversion. Missing check/cross/triangle/dot glyphs use geometry.

The stamp mask is a 1024x256 transient render target. White Canvas text and a 6 px frame are read through the red channel, then tinted and rotated -4 degrees. The vignette uses distance from UV center with opacity capped at 0.25. Connect Saturate through its unnamed input, not a pin called Input.

For the completed implementation, native screenshots and runtime limits, see `../Docs/TASK5_6_HANDOFF.md`.
