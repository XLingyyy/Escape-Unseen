# Escape Unseen — Task 6.1 fonts

Downloaded from the official Google Fonts GitHub repository on 2026-11-13 UTC. The TTF files are unmodified. Both families use SIL Open Font License 1.1; their original OFL.txt files are included beside the fonts. PROVENANCE.csv remains root's integration responsibility; use fonts_sources.json for the three source rows.

| File | Size | Font version | Intended role |
| --- | ---: | --- | --- |
| BebasNeue/BebasNeue-Regular.ttf | 61,400 bytes | 2.000 | Titles, phase names, keys, banners |
| CourierPrime/CourierPrime-Regular.ttf | 71,188 bytes | 3.018 | Body text and instructions |
| CourierPrime/CourierPrime-Bold.ttf | 72,856 bytes | 3.018 | Bold status labels |

Primary sources: [Bebas Neue font and metadata](https://github.com/google/fonts/tree/main/ofl/bebasneue), [Bebas Neue license](https://github.com/google/fonts/blob/main/ofl/bebasneue/OFL.txt), [Courier Prime font and metadata](https://github.com/google/fonts/tree/main/ofl/courierprime), [Courier Prime license](https://github.com/google/fonts/blob/main/ofl/courierprime/OFL.txt). The licenses permit font embedding and bundling with software, with copyright/license notices retained. Preserve these two license files in the shipped third-party notices. No font modification or renaming of the font family itself is performed; UE asset names are separate.

## Import handoff

`import_runtime_fonts.py` is an offline-prepared native Unreal Python script. It has **not been run against UE by this worker**. Stop PIE, then root can invoke it from the existing temporary editor Blueprint bridge's ConstructionScript ExecuteConsoleCommand:

```text
py "F:/Escape Unseen/EU/SourceArt/Fonts/import_runtime_fonts.py"
```

The script uses the actual 5.8 `unreal.FontFileImportFactory` class; there is no `FontFaceFactory` class in the inspected UnrealEd sources. Set `batch_create_font_asset = unreal.BatchCreateFontAsset.YES` and import the TTF through an automated `AssetImportTask`. The native factory creates a FontFace plus a Runtime UFont using `UFontFactory`, then inserts a `Default` typeface entry containing `FFontData(FontFace)`. This avoids attempting to assign the private FFontData.FontFaceAsset property from Python. The auto-created `<face>_Font` is renamed to the requested target before final save.

Final target assets under `/Game/EscapeUnseen/UI/Fonts/`:

| Runtime UFont | Referenced FontFace |
| --- | --- |
| F_BebasNeue | FF_BebasNeue |
| F_CourierPrime_Regular | FF_CourierPrime_Regular |
| F_CourierPrime_Bold | FF_CourierPrime_Bold |

Every UFont receives FontCacheType=Runtime, RuntimeFontSource=Asset, LegacyFontName=Default and **LegacyFontSize=64**. Every FontFace uses Inline loading and Metrics layout. The roughly 205 KB of font data is carried by the assets; runtime rendering does not depend on the SourceArt paths. The script uses `EditorAssetLibrary.save_loaded_asset(asset, False)` for both the face and font and records its actual saved assets in import_runtime_fonts_report.json when executed. Repeated bridge construction reuses the target face/font assets instead of importing another copy. It does not alter maps or HUD graphs.

The import factory's auto-created UFont names are temporary. The native rename may leave redirects at `FF_*_Font` if the editor decides a redirect is required; no gameplay reference should use those names. The final HUD must reference the three `F_*` objects above. No speculative redirector cleanup or broad asset scan is part of this script.

## Canvas sizes and measurement

`AHUD.DrawText` and `Canvas.K2_DrawText` accept UFont and use its legacy font size/name. **Font size is in points.** Unreal's Slate renderer uses 96 DPI, converting point size by `96/72`; at DPI scale 1, LegacyFontSize 64 corresponds to a nominal 85.333 px em, rounded internally by the rasterizer. Visible cap height and line height depend on each font's metrics.

If the task's design font sizes are interpreted as pixel em sizes, root's Label helper should use:

```text
viewScale = ViewportHeight / 1080
textScale = DesignSize * 0.75 / 64 * viewScale
```

For example, design size 120 uses scale 1.40625 at 1080p; 84 uses 0.984375; 32 uses 0.375; 24 uses 0.28125. If DesignSize is intentionally interpreted as Slate point size, omit the 0.75 factor. Use one interpretation across HUD and render-target stamp drawing.

For K2_DrawText, pass `(textScale, textScale)` as Scale; pass the same Font and Scale to `Canvas.K2_TextSize`. For AHUD.DrawText, pass scalar textScale and `bScalePosition=false`; use `AHUD.GetTextSize` with the same font and scale. Position and panel dimensions already receive viewScale separately. K2_DrawText's `bCentreX/bCentreY` can center text using its own measurement path. Avoid fixed character-count width estimates: Bebas is proportional, and even Courier requires the correct actual size/spacing. Canvas measurement returns advance/line metrics, not a tight visible-ink rectangle, and may round to integer pixels.

Runtime Canvas text uses the font cache at LegacyFontSize and then applies the requested Scale to its glyph quads. LegacyFontSize 64 keeps the largest 140 px title's magnification around 1.64x and gives one stable denominator for all three fonts. Use the actual engine render for final visual acceptance; the worker has not measured fonts through a live Canvas.

## Required symbol coverage

fontTools inspection of the downloaded TTF cmap tables found the same coverage in all three faces:

| Symbol | Codepoint | Present |
| --- | --- | --- |
| ✓ | U+2713 | No |
| ✕ | U+2715 | No |
| ▶ | U+25B6 | No |
| ● | U+25CF | No |
| ‹ and › | U+2039 / U+203A | Yes |
| … | U+2026 | Yes |
| · | U+00B7 | Yes |
| − | U+2212 | Yes |

Keep status words such as HIDDEN, LIT and BLOCKED in their requested fonts, and draw the four missing symbols as Canvas geometry:

- Check: two connected strokes, e.g. `(-5,0) -> (-1,4) -> (7,-5)`, thickness 2 at 1080p.
- Cross: two diagonal strokes from `(-5,-5)` to `(5,5)` and `(-5,5)` to `(5,-5)`.
- Selection triangle: a filled Canvas triangle with vertices `(-5,-7), (6,0), (-5,7)`.
- Inspection dot: a filled Canvas polygon (e.g. 20 sides, radius 7) or a triangle fan. Modulate its alpha slowly for the requested pulse.

Scale all symbol dimensions with viewScale and place them on the same intended line center as the text. This preserves the requested symbol-plus-word communication without relying on an engine or OS fallback font. No extra symbol font or unlicensed dependency is required.

## Local source evidence

All paths below are relative to `G:/UnrealEngine/UE_5.8/Engine/Source/`:

- `Editor/UnrealEd/Private/Factories/EditorFactories.cpp:5119`: UFontFactory creates a Font with Runtime cache.
- `Editor/UnrealEd/Private/Factories/EditorFactories.cpp:5133`: FontFileImportFactory imports TTF/OTF into FontFace; `5161` handles automated imports; `5224–5247` constructs the Runtime Font and Default CompositeFont entry.
- `Editor/UnrealEd/Classes/Factories/FontFileImportFactory.h:15–48`: BatchCreateFontAsset enum and reflected setting.
- `Runtime/Engine/Classes/Engine/Font.h:176–187`: LegacyFontSize/Name and reflected CompositeFont property. CompositeFont's direct C++ access is deprecated in 5.7+, while the native factory uses the supported mutable accessor.
- `Runtime/Engine/Private/Font.cpp:379`: GetLegacySlateFontInfo uses the UFont's LegacyFontSize and LegacyFontName.
- `Runtime/SlateCore/Public/Fonts/SlateFontInfo.h:15`: RenderDPI=96; `Private/Fonts/FontCacheFreeType.cpp:119–134` converts points to pixels.
- `Runtime/Engine/Private/HUD.cpp:931–950`: GetTextSize and DrawText pass the selected UFont and scale to Canvas.
- `Runtime/Engine/Private/UserInterface/Canvas.cpp:2216–2229,2315–2324`: K2_DrawText and K2_TextSize use the supplied UFont and scale.
- `Runtime/Engine/Private/UserInterface/CanvasItem.cpp:995–999,1193–1213`: Runtime measurement uses the legacy font info and Scale; drawing uses the font cache and scales the glyph layout.

Epic's [Font Asset and Editor documentation](https://dev.epicgames.com/documentation/unreal-engine/font-asset-and-editor-in-unreal-engine) describes Runtime composite fonts, reusable FontFace assets and Inline loading. The implementation decisions above use the installed 5.8 source as the version-specific authority.

Validation completed offline: TTF parsing, font version/weight metadata, required symbol cmap coverage and exact OFL source-file inclusion. No checksums were computed. No UE import, compilation, rendering, PIE or package run was performed by this worker.
