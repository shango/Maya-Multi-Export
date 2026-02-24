# Export Genie

**Version 4.0**

Export Maya scenes to multiple formats (.ma, .fbx, .abc, .jsx, .mov) in a single operation with automatic folder structure and versioning. Three-tab interface serving camera trackers, matchmove/animation artists, and face track artists.

Requires **Maya 2025+**. Windows and macOS.

## Features

- Three-tab workflow for Camera Track, Matchmove, and Face Track pipelines
- Export to Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), After Effects (.jsx + .obj), and Playblast QC (.mov) in one click
- Automatic versioned folder structure based on scene filename
- Editable version number with auto-detection from `_v##` scene naming
- Camera automatically renamed to `cam_main` during export and restored afterward
- Custom shaders stripped to default lambert for .ma exports
- Image plane references preserved in .ma exports
- FBX exports with baked keyframes, skins, and blend shapes
- Alembic exports in world space with UVs
- After Effects ExtendScript export with camera, geo, tracking nulls, and source footage
- H.264 QuickTime playblast at 1920x1080 through the shot camera
- Automatic Alembic-to-blendshape conversion for Face Track FBX delivery
- Multiple character rig/geo pairs in Matchmove tab
- Multiple face mesh entries in Face Track tab
- Optional T-pose frame for Matchmove FBX and ABC exports
- Render as Raw (sRGB) playblast with OCIO bypass (on by default)
- useBackground Shader + Wireframe overlay for Camera Track QC
- QC Checker Overlay with adjustable color, scale, and opacity (Matchmove and Face Track)
- Anti-Aliasing toggle between 8x and 16x
- Use Current Viewport Settings mode for unmodified playblasts
- Automatic playblast overrides: grid hidden, backface culling, far clip extended, 2D pan/zoom disabled, selection cleared
- Isolate select, motion blur, and forced display layers for Matchmove and Face Track playblasts
- Pre-export validation for missing assignments, duplicate picks, name conflicts, and invalid ranges
- Auto-loading of required plugins (fbxmaya, AbcExport, objExport)
- Rollover tooltips on every widget
- Drag-and-drop install with automatic shelf button

## Install

1. Drag `maya_multi_export.py` into the Maya viewport.
2. A shelf button is added to your current shelf automatically.

That's it. Click the shelf button to open the tool.

## Upgrade

To update to a newer version, restart Maya, open a fresh scene, then drag the new `maya_multi_export.py` into the viewport again. It will overwrite the previous version in your scripts directory and replace the shelf button. Restart Maya after upgrading to ensure the new version is fully loaded.

## How to Use

1. Save your scene with a `_v##` version in the filename (e.g. `shot_layout_v03.ma`).
2. Click the **Export_Genie** shelf button.
3. Set the **Export Root** directory.
4. Set the **Version Num** — pre-populated from your scene filename, editable for manual override.
5. Select the appropriate tab for your workflow.
6. Assign roles by selecting objects in the viewport and clicking **Load Sel**.
7. Check the formats you want.
8. Set the **frame range** or click **Use Timeline Range**.
9. Click **EXPORT**.

All widgets have rollover tooltips describing their function.

## Three-Tab Workflow

### Tab 1 — Camera Track Export

For artists who have tracked a camera in SynthEyes (or similar) and brought it into Maya with some reference geometry. Simple scenes — no rigs, no constraints, no vertex animation.

**Export formats**: Maya ASCII (.ma), After Effects (.jsx + .obj), FBX (.fbx), Alembic (.abc), Playblast QC (.mov)

**Roles**:
- **Camera** — the tracked camera
- **Geo Group** — top-level geometry group

### Tab 2 — Matchmove Export

For animators and riggers working with full character rigs, complex vertex-animated objects, or proxy geometry. Supports multiple character rig/geo pairs.

**Export formats**: Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), Playblast QC (.mov)

**Roles**:
- **Camera** — the shot camera
- **Static Geo** — proxy/set geometry
- **Ctrl Rig Group** / **Anim Geo Group** — repeatable pairs for multiple characters or animated meshes (use +/- buttons to add or remove pairs)

**T-Pose**: An optional T-pose frame (default: 991) can be included. When enabled, FBX and ABC exports extend their frame range to include the T-pose frame. The .ma export and QC playblast keep the original timeline range.

### Tab 3 — Face Track Export

For artists working with Alembic-cached facial animation (e.g. from face tracking software or animation caches). Supports multiple face mesh entries for multi-character scenes.

**Export formats**: Maya ASCII (.ma), FBX (.fbx), Playblast QC (.mov)

**Roles**:
- **Camera** — the shot camera
- **Static Geo** — static geometry for reference
- **Face Mesh Group** — repeatable entries for face geometry groups (use +/- buttons to add or remove entries)

**Automatic blendshape conversion**: Each mesh under a Face Mesh Group is classified as vertex-animated or transform-animated. Vertex-animated meshes (facial deformation) are converted to blendshape targets with per-frame keys. Transform-animated meshes (rigid bodies) have their channels baked. The result is an FBX with blendshape-driven facial animation ready for game engines and real-time renderers.

## Features

### Export Directory and Versioning
- Browse to set your export root directory
- Version number is auto-detected from your scene filename's `_v##` pattern
- Override the version number manually to export under any version
- All exports go into a versioned folder (e.g. `shot_track_v01/`)
- New versions create new folders alongside existing ones

### Export Formats
- **Maya ASCII (.ma)** — Camera renamed to `cam_main`, custom shaders stripped to default lambert, image plane references preserved, frame range matched to UI
- **FBX (.fbx)** — Keyframes baked, skins and blend shapes preserved, cameras included
- **Alembic (.abc)** — World space, UVs included, whole-frame geo sampling (Camera Track and Matchmove tabs)
- **After Effects (.jsx + .obj)** — ExtendScript that rebuilds the 3D scene in AE with camera, geo, tracking nulls, and source footage (Camera Track tab only)
- **Playblast QC (.mov)** — H.264 QuickTime at 1920x1080 through the shot camera

### Viewport Settings (QC Playblast)

Each tab has a collapsible **Viewport Settings** section with controls for the QC render:

- **Render as Raw (sRGB)** (on by default) — Renders the playblast using the Raw color view, bypassing any OCIO tonemapping. All color management settings are restored after the render.
- **useBackground Shader + Wireframe** (Camera Track only) — Applies a useBackground shader to all geo so meshes become transparent (showing the camera plate) with wireframe edges drawn on top. Original shaders are restored after the render.
- **Anti-Aliasing 16x** — Bumps VP2.0 anti-aliasing from 8 to 16 samples. Higher quality but uses more GPU memory.
- **Use Current Viewport Settings** — Skips all viewport overrides and renders the playblast exactly as your viewport looks. Only the camera is switched to `cam_main`.
- **QC Checker Overlay** (Matchmove and Face Track tabs) — Applies a UV checker pattern over all geo with adjustable Color, Scale, and Opacity. The checker shader is created and cleaned up automatically.

### Automatic Playblast Overrides

Unless "Use Current Viewport Settings" is enabled, every QC playblast automatically:

- Hides the grid
- Enables backface culling on all meshes
- Extends the camera far clip plane so distant geometry is visible
- Disables 2D pan/zoom on the camera
- Sets anti-aliasing to 8x (or 16x with the toggle)
- Clears the selection so no highlight outlines appear
- Configures and restores color management settings

Additional overrides for Matchmove and Face Track tabs:

- Isolate select — only assigned geo, camera, and image planes are visible
- All display layers forced visible
- Smooth shaded display with no wireframe overlay
- Display textures enabled (for checker overlay)
- VP2.0 motion blur enabled

### Camera Handling
- Camera is temporarily renamed to `cam_main` during export for consistent naming downstream
- If the camera is already named `cam_main`, it is left as-is
- Original name is restored after export

### After Effects Export Details
- Creates an AE composition matching Maya's render resolution and frame rate
- Camera exported with per-frame position, rotation, and zoom keyframes
- Geo children named "nulls" become AE 3D nulls (SynthEyes tracking markers)
- Geo children named "chisels" are skipped
- Flat planes become AE solids
- All other geo exported as static OBJ files with per-frame transform keyframes
- Source footage from the camera's image plane is auto-imported as a background layer
- Run the .jsx file in After Effects via File > Scripts > Run Script File

### Validation
Before exporting, the tool checks for:
- Missing role assignments
- Duplicate picks (same node in multiple fields)
- Camera name conflicts with existing `cam_main` nodes
- OBJ filename collisions
- Empty export root or invalid frame range
- Empty version number (defaults to v01 with a warning)

Errors are shown in a popup. Warnings let you continue or cancel.

### Plugin Management
Required plugins (`fbxmaya`, `AbcExport`, `objExport`) are auto-loaded when needed. If a plugin can't be loaded, a dialog directs you to the Plug-in Manager.

## Output Folder Structure

```
<export_root>/
  shot_track_v01/
    shot_cam_v01.ma
    shot_cam_v01.fbx
    shot_cam_v01.abc
    shot_cam_qc_v01.mov
    ae_export/
      shot_v01.jsx
      shot_v01_geo1.obj
      shot_v01_geo2.obj
```
