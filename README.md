# Maya Multi-Export

**Version 1.0.0**

Export Maya scenes to multiple formats (.ma, .fbx, .abc) in a single operation with automatic folder structure and versioning.

Requires **Maya 2025+**. Windows and macOS.

## Install

1. Drag `maya_multi_export.py` into the Maya viewport.
2. A shelf button is added to your current shelf automatically.

That's it. Click the shelf button to open the tool.

## Upgrade

To update to a newer version, just drag the new `maya_multi_export.py` into the viewport again. It will overwrite the previous version in your scripts directory and replace the shelf button.

## Usage

1. **Save your scene** with a `_v##` version in the filename (e.g. `shot_layout_v03.ma`).
2. Click the **MultiExport** shelf button.
3. Set the **Export Root** directory.
4. Assign roles by selecting objects in the viewport and clicking **Load Sel**:
   - **Camera** — the shot camera (exported in .ma as `main_cam`)
   - **Geo Root** — top-level geometry group (used by .ma, .fbx, .abc)
   - **Rig Root** — top-level rig group (used by .ma, .fbx)
   - **Proxy Geo** — proxy/set geometry for set objects (used by .ma, .fbx, .abc)
5. Check the formats you want (.ma, .fbx, .abc).
6. Set the **frame range** or click **Use Timeline Range**.
7. Click **EXPORT**.

## Output Structure

All exports go into a single flat folder named `<scene_name>_maya_exports`:

```
<export_root>/
  shot_layout_maya_exports/
    shot_layout_v01.ma
    shot_layout_v01.fbx
    shot_layout_v01.abc
    shot_layout_v02.ma
    shot_layout_v02.fbx
    shot_layout_v02.abc
```

New versions are added alongside existing files in the same folder.

## Format Details

| Format | Includes | Notes |
|--------|----------|-------|
| .ma | Camera + Geo + Rig + Proxy | Camera renamed to `main_cam` on export |
| .fbx | Geo + Rig + Proxy | Keyframes baked (then reverted), skins + blend shapes preserved |
| .abc | Geo + Proxy | Ogawa format, UVs, world space, whole-frame geo |

## Export Settings

The tool overrides your current FBX and Alembic settings during export to ensure consistency. Your existing Maya export preferences are not affected.

**FBX**: Binary FBX 2020, bake animation on, skins + blend shapes on, quaternion resampled as Euler, no cameras/lights/embedded textures.

**Alembic**: Ogawa data format, UV write, world space, whole-frame geo. No visibility, normals, or creases written.
