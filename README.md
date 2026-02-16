# Maya Multi-Export

**Version 2.2.0**

Export Maya scenes to multiple formats (.ma, .fbx, .abc, .jsx, .mov) in a single operation with automatic folder structure and versioning. Now with a two-tab interface serving both camera trackers and matchmove/animation artists.

Requires **Maya 2025+**. Windows and macOS.

## Install

1. Drag `maya_multi_export.py` into the Maya viewport.
2. A shelf button is added to your current shelf automatically.

That's it. Click the shelf button to open the tool.

## Upgrade

To update to a newer version, drag the new `maya_multi_export.py` into the viewport again. It will overwrite the previous version in your scripts directory and replace the shelf button. **Restart Maya** after upgrading to ensure the new version is fully loaded.

## Two-Tab Workflow

The tool has two tabs for two different workflows. In both tabs, the camera is temporarily renamed to `main_cam` during export and restored afterward.

### Tab 1 — Camera Track Export

For artists who have tracked a camera in Syntheyes (or similar) and brought it into Maya with some reference geometry. Simple scenes — no rigs, no constraints, no vertex animation.

**Available formats**: Maya ASCII (.ma), After Effects (.jsx + .obj), FBX (.fbx), Alembic (.abc), Playblast QC (.mov)

**Roles**:
- **Camera** — the tracked camera
- **Geo Root** — top-level geometry group

### Tab 2 — Matchmove Export

For animators and riggers working with full character rigs, complex vertex-animated objects, or proxy geometry. These users never export to After Effects.

**Available formats**: Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), Playblast QC (.mov)

**Roles**:
- **Camera** — the shot camera
- **Geo Root** — top-level geometry group
- **Rig Root** — top-level rig group
- **Proxy Geo** — proxy/set geometry

## Usage

1. **Save your scene** with a `_v##` version in the filename (e.g. `shot_layout_v03.ma`).
2. Click the **MultiExport** shelf button.
3. Set the **Export Root** directory.
4. Select the appropriate tab for your workflow.
5. Assign roles by selecting objects in the viewport and clicking **Load Sel**.
6. Check the formats you want.
7. Set the **frame range** or click **Use Timeline Range**.
8. Click **EXPORT**.

## Output Structure

All exports go into a single flat folder named `<scene_name>_maya_exports`. After Effects exports get their own `ae_export/` subfolder:

```
<export_root>/
  shot_layout_maya_exports/
    shot_layout_v01.ma
    shot_layout_v01.fbx
    shot_layout_v01.abc
    shot_layout_v01_qc.mov
    ae_export/
      shot_layout_v01.jsx
      shot_layout_v01_geo1.obj
      shot_layout_v01_geo2.obj
```

New versions are added alongside existing files in the same folder.

## Format Details

| Format | Tab | Includes | Notes |
|--------|-----|----------|-------|
| .ma | Both | Camera + Geo (+ Rig + Proxy in Tab 2) | Camera exported as `main_cam` |
| .jsx + .obj | Camera Track | Camera + Geo | JSX ExtendScript for AE comp import, OBJ per geo child |
| .fbx | Both | Camera + Geo (+ Rig + Proxy in Tab 2) | Camera + keyframes baked (then reverted), skins + blend shapes preserved |
| .abc | Both | Camera + Geo (+ Proxy in Tab 2) | Ogawa format, UVs, world space, whole-frame geo |
| .mov | Both | Viewport playblast through camera | H.264 QuickTime, 1920x1080, requires QuickTime |

## After Effects Export

The JSX export generates an ExtendScript file (`.jsx`) and companion OBJ files that can be run in After Effects to recreate the 3D scene:

- **Composition** is created matching Maya's render resolution and frame rate
- **Camera** is exported with per-frame position, rotation, and zoom keyframes
- **Geometry** children are classified by name (case-insensitive):
  - Children containing **"chisels"** are skipped entirely
  - Children containing **"nulls"** are expanded — each Maya locator inside becomes an AE 3D null with position-only keyframes (SynthEyes tracking markers)
  - All other children are exported as individual OBJ files (static, frame 1) and represented as 3D null layers with per-frame transform keyframes
- Coordinate system is converted from Maya Y-up to AE (Y-down, scale factor of 10)
- Keyframes use `setValuesAtTimes()` for fast batch application in AE

To use: run the `.jsx` file in After Effects via File > Scripts > Run Script File.

## Export Settings

The tool overrides your current FBX and Alembic settings during export to ensure consistency. Your existing Maya export preferences are not affected.

**FBX**: Binary FBX 2020, bake animation on, cameras on, skins + blend shapes on, quaternion resampled as Euler, no lights/embedded textures.

**Alembic**: Ogawa data format, UV write, world space, whole-frame geo. No visibility, normals, or creases written.

**OBJ**: Groups, point groups, materials, smoothing, and normals enabled.

**Playblast QC**: H.264 QuickTime (.mov), 1920x1080, quality 70, viewport ornaments visible. Renders through the assigned camera (`main_cam`). Requires Apple QuickTime to be installed — if unavailable, a popup will prompt you to install QuickTime Essentials.
