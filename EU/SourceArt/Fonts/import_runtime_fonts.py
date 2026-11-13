"""Task 6.1 editor-only import. Prepared offline; execute only through root's UE bridge.

Console command (from an editor-world ConstructionScript, with PIE stopped):
    py "F:/Escape Unseen/EU/SourceArt/Fonts/import_runtime_fonts.py"

The native FontFileImportFactory builds CompositeFont/FFontData correctly.
This script does not attempt to write FFontData's private reflected fields.
"""
from pathlib import Path
import json
import unreal

SOURCE = Path(__file__).resolve().parent
DESTINATION = "/Game/EscapeUnseen/UI/Fonts"
LEGACY_FONT_SIZE = 64
SPECS = [
    ("BebasNeue/BebasNeue-Regular.ttf", "FF_BebasNeue", "F_BebasNeue"),
    ("CourierPrime/CourierPrime-Regular.ttf", "FF_CourierPrime_Regular", "F_CourierPrime_Regular"),
    ("CourierPrime/CourierPrime-Bold.ttf", "FF_CourierPrime_Bold", "F_CourierPrime_Bold"),
]


def main():
    if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
        raise RuntimeError("Stop PIE before importing/saving Task 6 fonts.")

    asset_library = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_library.make_directory(DESTINATION)
    tasks = []
    for relative, face_name, font_name in SPECS:
        face_path = DESTINATION + "/" + face_name
        if asset_library.does_asset_exist(face_path):
            continue
        filename = SOURCE / relative
        if not filename.is_file():
            raise FileNotFoundError(filename)
        factory = unreal.FontFileImportFactory()
        factory.set_editor_property("batch_create_font_asset", unreal.BatchCreateFontAsset.YES)
        factory.set_editor_property("edit_after_new", False)
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(filename))
        task.set_editor_property("destination_path", DESTINATION)
        task.set_editor_property("destination_name", face_name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("save", False)
        task.set_editor_property("factory", factory)
        tasks.append(task)
    if tasks:
        asset_tools.import_asset_tasks(tasks)

    report = []
    for relative, face_name, font_name in SPECS:
        face_path = DESTINATION + "/" + face_name
        font_path = DESTINATION + "/" + font_name
        generated_font_path = face_path + "_Font"
        face = asset_library.load_asset(face_path)
        if not isinstance(face, unreal.FontFace):
            raise RuntimeError("Expected imported FontFace: " + face_path)

        # BatchCreateFontAsset.Yes creates this UFont through UFontFactory and
        # inserts the face as the native Default CompositeFont typeface entry.
        if not asset_library.does_asset_exist(font_path):
            generated_font = asset_library.load_asset(generated_font_path)
            if not isinstance(generated_font, unreal.Font):
                raise RuntimeError("Native factory did not create: " + generated_font_path)
            if not asset_library.rename_asset(generated_font_path, font_path):
                raise RuntimeError("Could not name runtime font: " + font_path)
        font = asset_library.load_asset(font_path)
        if not isinstance(font, unreal.Font):
            raise RuntimeError("Expected runtime Font: " + font_path)

        # All three faces total about 205 KB; inline data avoids source-path or
        # external font-file dependencies when the game is cooked.
        face.set_editor_property("loading_policy", unreal.FontLoadingPolicy.INLINE)
        face.set_editor_property("hinting", unreal.FontHinting.DEFAULT)
        face.set_editor_property("layout_method", unreal.FontLayoutMethod.METRICS)
        font.set_editor_property("font_cache_type", unreal.FontCacheType.RUNTIME)
        font.set_editor_property("runtime_font_source", unreal.RuntimeFontSource.ASSET)
        font.set_editor_property("legacy_font_size", LEGACY_FONT_SIZE)
        font.set_editor_property("legacy_font_name", unreal.Name("Default"))

        # Explicit force-save: the root observed only_if_dirty can skip writes.
        if not asset_library.save_loaded_asset(face, False):
            raise RuntimeError("Failed to save FontFace: " + face_path)
        if not asset_library.save_loaded_asset(font, False):
            raise RuntimeError("Failed to save Font: " + font_path)
        report.append({
            "source": str(SOURCE / relative),
            "font_face": face.get_path_name(),
            "font": font.get_path_name(),
            "cache_type": str(font.get_editor_property("font_cache_type")),
            "legacy_font_size": font.get_editor_property("legacy_font_size"),
            "legacy_font_name": str(font.get_editor_property("legacy_font_name")),
            "font_loading_policy": str(face.get_editor_property("loading_policy")),
            "saved": True,
        })
    result = SOURCE / "import_runtime_fonts_report.json"
    result.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unreal.log("Task 6.1: imported/saved three Runtime Fonts; report: " + str(result))


main()
