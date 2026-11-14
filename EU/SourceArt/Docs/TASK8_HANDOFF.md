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

## 8.1–8.4

8.1 runtime diagnosis is underway. No v2 gameplay assets are included in the fallback package.
