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

## 8.2–8.5

Pending integration. Task 8.5 was added by the user during implementation.
No v2 gameplay assets are included in the fallback package.
