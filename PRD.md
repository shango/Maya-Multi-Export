# Maya Multi-Export Tool — Product Requirements Document

## Overview

A Maya 2025+ addon that lets artists export their scene to multiple formats in a single operation, with automatic folder structure creation and versioning. Installed via drag-and-drop of a single `.py` file.

The tool serves two distinct user groups via a tabbed interface:
1. **Camera trackers** — simple scenes from SynthEyes with a tracked camera and reference geo. Export to After Effects (.jsx + .obj), Maya ASCII, FBX, Alembic, and QC playblast.
2. **Matchmove/animation artists** — complex scenes with character rigs, vertex animation, and static geo. Export to Maya ASCII, FBX, Alembic, and QC playblast.

## Problem Statement

Artists in the studio need to export each scene they work on to multiple formats. This is currently a tedious manual process requiring:
- Switching export settings per format
- Manually creating folder structures
- Baking keyframes for FBX
- Remembering which objects to include/exclude per format
- Maintaining consistent versioning across formats
- Manually writing After Effects JSX scripts and exporting OBJ files for camera track handoff

## Target Users

### Camera Trackers (Tab 1 — "Camera Track Export")
- Artists who have done a camera track in SynthEyes and brought it into Maya
- Creating static reference geo, possibly adjusting scene scale/orientation
- Only camera and maybe a few objects have keyframes — no rigs, no constraints, no vertex animation
- Need to hand off to After Effects compositors

### Matchmove/Animation Artists (Tab 2 — "Matchmove Export")
- 3D animators and riggers working with full character rigs or complex vertex-animated objects
- Working with animated geo, static geo for game engines, and cameras
- Never exporting to After Effects
- Need .ma, .fbx, .abc exports with baked animation

### Platform
- Windows and macOS
- Maya 2025+

## Functional Requirements

### Installation
- **Single-file drag-and-drop install**: User drags `maya_multi_export.py` into the Maya viewport
- Automatically copies itself to Maya's user scripts directory
- Creates a custom shelf button with a distinctive icon (embedded as base64 in the .py)
- Works on both Windows and macOS
- **Module cache clearing**: On each install, deletes stale `.pyc` files from `__pycache__/` and purges the module from `sys.modules` before re-importing, ensuring the latest version always loads
- **Shelf button reload**: The shelf button command also clears `sys.modules` before importing, so launching the tool always runs the installed version

### UI — Two-Tab Layout (cmds.tabLayout)

Shared elements stay outside the tabs; only role assignments and format checkboxes go inside tabs.

```
window "Maya Multi-Export v1.2.2"
+-- columnLayout (main)
|   +-- frameLayout "Scene Info"              <-- SHARED
|   +-- frameLayout "Export Root Directory"    <-- SHARED
|   +-- tabLayout
|   |   +-- "Camera Track Export"             <-- TAB 1
|   |   |   +-- Role Assignment
|   |   |   |   +-- Camera       (Load Sel)
|   |   |   |   +-- Geo Root     (Load Sel)
|   |   |   +-- Export Formats
|   |   |       +-- Maya ASCII (.ma)
|   |   |       +-- After Effects (.jsx + .obj)
|   |   |       +-- FBX (.fbx)
|   |   |       +-- Alembic (.abc)
|   |   |       +-- Playblast QC (.mov)
|   |   +-- "Matchmove Export"                <-- TAB 2
|   |       +-- Role Assignment
|   |       |   +-- Camera       (Load Sel)
|   |       |   +-- Static Geo   (Load Sel)
|   |       |   +-- ---- separator ----
|   |       |   +-- Rig Root     (Load Sel)   \
|   |       |   +-- Geo Root     (Load Sel)   / repeatable pair
|   |       |   +-- [+] [-] buttons
|   |       +-- Export Formats
|   |           +-- Maya ASCII (.ma)
|   |           +-- FBX (.fbx)
|   |           +-- Alembic (.abc)
|   |           +-- Playblast QC (.mov)
|   |           +-- checkBox "Include T Pose" + intField (991)
|   +-- frameLayout "Frame Range"             <-- SHARED
|   |   +-- Start / End fields
|   |   +-- "Use Timeline Range" button
|   +-- progressBar + label                   <-- SHARED
|   +-- button "E X P O R T"                 <-- SHARED
|   +-- frameLayout "Log"                    <-- SHARED
|   +-- text "v1.2.2"                        <-- SHARED
```

#### Shared UI Elements
- **Scene Info**: Displays current scene name, detected version, and status
- **Export Root**: Directory picker for the base export location
- **Frame Range**: Start/end frame fields + "Use Timeline Range" button
- **Progress Bar**: Visual progress indicator with percentage label, advances per export format
- **Export Button**: Triggers the export pipeline for the active tab
- **Log Panel**: Scrollable text area showing progress and results

#### Tab 1 — Camera Track Export
- **Role Assignment**: Two fields (Camera, Geo Root) with "Load Sel" buttons
  - User selects object(s) in viewport, clicks the corresponding "Load Sel" button
  - Tool validates the object type (camera shape, transform)
- **Export Formats**: Checkboxes for Maya ASCII (.ma), After Effects (.jsx + .obj), FBX (.fbx), Alembic (.abc), Playblast QC (.mov)

#### Tab 2 — Matchmove Export
- **Role Assignment**: Camera and Static Geo are scene-level fields. Below a separator, Rig Root / Geo Root pairs can be added dynamically for multiple characters.
  - **Camera** and **Static Geo**: Single fields with "Load Sel" buttons (same as before)
  - **Rig/Geo pairs**: Each pair has a Rig Root and Geo Root field with "Load Sel" buttons. The first pair is always shown. A `[+]` button adds additional pairs (labeled "Rig Root 2" / "Geo Root 2", etc.). A `[-]` button appears when 2+ pairs exist to remove the last pair. The UI grows/shrinks vertically as pairs are added/removed.
  - Tool validates the object type (camera shape, transform)
- **Export Formats**: Checkboxes for Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), Playblast QC (.mov)
  - **Include T Pose**: Checkbox (checked by default) with an editable frame number field (default 991). When checked and "Use Timeline Range" is clicked, the start frame is set to the T-pose frame value, ensuring the T-pose frame is included in matchmove exports. Only visible/active on the Matchmove tab.

### Versioning
- Parse version from Maya filename using `_v##` pattern (e.g., `shot_v01.ma`)
- Support 2-3 digit versions (`_v01`, `_v100`)
- If multiple `_v##` patterns exist, use the last one
- If no version found: warn user, default to `v01`

### Folder Structure

Version-aware folder naming with an After Effects subfolder for Camera Track output:
```
<export_root>/
  <scene_base>_track_<version>/
    <scene>_<version>.ma
    <scene>_<version>.fbx
    <scene>_<version>.abc
    <scene>_<version>_qc.mov
    <scene_base>_track_afterEffects_<version>/
      <scene>_<version>.jsx
      <scene>_<version>_<geo1>.obj
      <scene>_<version>_<geo2>.obj
```

- Directories are created automatically if they don't exist
- **Version-aware reuse**: When re-exporting a new version, the tool finds any existing `_track_v##` folder in the export root and renames it to the current version, adding new files alongside existing ones rather than overwriting. The same applies to the After Effects subfolder.

### Export Behavior

#### Source Footage Auto-Detection (JSX and MA exports)
- If the selected camera has a Maya **image plane** attached, the source footage path is auto-detected via `cmds.listConnections(cameraShape + ".imagePlane")` and `cmds.getAttr(imagePlaneShape + ".imageName")`
- **JSX**: The footage is imported as a sequence (`ImportOptions` with `sequence = true`) and added as the bottom layer in the AE comp via `moveToEnd()`. If the file doesn't exist on the AE machine, a placeholder is created instead. Silently skipped if no image plane is found.
- **MA**: Image plane transform nodes are added to the export selection so the footage reference is preserved in the `.ma` file. Silently skipped if no image plane is found.
- If the path is incorrect or unavailable, the feature skips silently — no errors or warnings

#### Camera Rename (all formats, both tabs)
- Camera is temporarily renamed to `cam_main` before any exports begin, then restored after all exports complete
- Rename happens once at the orchestration level (not per-format)

#### Maya ASCII (.ma) — Both tabs
- **Tab 1**: Exports Camera + Geo Root
- **Tab 2**: Exports Camera + Geo Root + Rig Root + Static Geo
- No baking or special processing
- Uses `cmds.file(exportSelected=True, type="mayaAscii")`

#### FBX (.fbx) — Both tabs
- **Tab 1**: Exports Camera + Geo Root
- **Tab 2**: Exports Camera + Geo Root + Rig Root + Static Geo
- **Animation baking**: Handled by the FBX plugin's built-in `FBXExportBakeComplexAnimation` setting, which bakes internally during export without modifying the source scene. No pre-bake or undo chunk needed.
- FBX export settings overridden via MEL commands:
  - Bake complex animation: on (plugin-internal baking)
  - Quaternion: resample
  - Constraints: off
  - Cameras: on
  - Lights: off
  - Input connections: off
  - Embedded textures: off
  - Skins/Shapes: on
  - Smoothing groups: on
  - Skeleton definitions: on
  - Binary format, FBX 2020 compatibility
- Uses `mel.eval("FBXExport -f ... -s")` for fine-grained control

#### Alembic (.abc) — Both tabs
- **Tab 1**: Exports Camera + Geo Root
- **Tab 2**: Exports Camera + Geo Root + Static Geo
- Animation is baked implicitly by Alembic's frame-range sampling (no explicit `bakeResults`)
- Flags: `-uvWrite`, `-worldSpace`, `-wholeFrameGeo`, `-dataFormat ogawa`
- Uses `cmds.AbcExport(j=job_string)` with `-root` flag per assigned role

#### After Effects (.jsx + .obj) — Tab 1 only
- Generates an ExtendScript JSX file and companion OBJ files for After Effects import
- JSX header includes tool version for traceability
- **Camera**: Exported with per-frame keyframes for position, rotation, and zoom
  - Queries Maya camera shape for `focalLength` (mm) and `horizontalFilmAperture` (inches -> mm via `*25.4`)
  - AE zoom formula: `focal_length_mm * comp_width_px / film_back_width_mm`
  - Creates `comp.layers.addCamera()` with `autoOrient = NO_AUTO_ORIENT`
  - Uses direct property access (`.position`, `.rotationX`, `.rotationY`, `.rotationZ`, `.zoom`) matching SynthEyes conventions
  - Uses `setValuesAtTimes()` for batch keyframe application
- **Geo children classification** (case-insensitive name matching):
  - **"chisels"** — any child whose name contains "chisels" is skipped entirely
  - **"nulls"** — any child whose name contains "nulls" is descended into; each Maya locator found inside becomes an AE 3D null with **position-only** keyframes (representing SynthEyes tracking markers). No OBJ exported.
  - **Simple planes** — flat meshes (bounding box thinnest extent < 0.1% of largest) become AE solids via `comp.layers.addSolid()` with `threeDLayer = true` and `rotationX = -90` (lying on the ground plane XZ). Scale is computed from world bounding box extents mapped to AE pixel space. No OBJ exported.
  - **All other children** — exported as a static OBJ (frame 1) and imported into AE via `ImportOptions` + `app.project.importFile()` + `comp.layers.add()`, with position/rotation/scale applied from the world matrix.
- **OBJ export pipeline**:
  - Maya's OBJ exporter writes vertices in **world space** by default. To avoid double-offset (JSX also applies position/rotation/scale), the node's world matrix is temporarily reset to identity before export, then restored. This produces local-space OBJ vertices.
  - OBJ vertices are **not** flipped/transformed — AE's OBJ importer natively handles the standard Y-up OBJ format. (See "JSX Export Technical Reference" below for why.)
  - OBJ scale in AE: `world_scale * ae_scale * 100 / 512` (AE maps 1 OBJ unit = 512 pixels at 100% scale)
- **Static object optimization**: Geo children and locators with no `animCurve` connections are detected at export time and use a single `setValue()` call (position read once) instead of scrubbing the timeline frame-by-frame with `setValuesAtTimes()`
- **Coordinate conversion** (Maya Y-up -> AE Y-down) — see detailed "JSX Export Technical Reference" section below:
  - **Scale factor (`ae_scale`)**: `10.0 * cm_per_unit / 2.54` — unit-aware conversion matching SynthEyes's internal inch-based system
  - **Position**: From the **world** matrix translation row: `x_ae = tx * ae_scale + comp_cx`, `y_ae = -ty * ae_scale + comp_cy`, `z_ae = -tz * ae_scale`
  - **Rotation**: From the **local** (objectSpace) matrix — excludes parent group orientation. Upper-left 3x3 is normalized, the T\*R\*T coordinate transform is applied (T = diag(1, -1, -1)), and the result is decomposed as **Rx\*Ry\*Rz intrinsic XYZ** Euler angles (AE's native rotation order).
  - **Scale**: From **world** matrix column magnitudes — captures full parent-inclusive scale
  - **Timing**: Keyframe times use `(frame - start_frame + 1) / fps` so frame 1 maps to `1/fps` seconds (matching SynthEyes convention)
- **Comp settings**: Resolution and fps derived from Maya render settings (`defaultResolution`) and time unit
- JSX includes helper functions: `findComp`, `firstComp`, `deselectAll`
- JSX wraps all operations in `app.beginUndoGroup()` / `app.endUndoGroup()`

#### Playblast QC (.mov) — Both tabs
- Renders a viewport playblast through the assigned camera (`cam_main`) at **1920x1080**
- QuickTime format with **H.264** compression, quality 70
- Output filename: `<scene>_<version>_qc.mov`
- Uses `cmds.playblast()` with `format="qt"`, `compression="H.264"`, `widthHeight=[1920, 1080]`
- Finds a visible model panel for rendering (does not rely on `withFocus` since clicking Export shifts focus)
- Switches the panel to the assigned camera via `cmds.lookThru()`, restores original camera afterward
- **Display mode**: Camera track playblasts (Tab 1) use **wireframe** display. Matchmove playblasts (Tab 2) use **wireframe on shaded** (smoothShaded + wireframeOnShaded) with **polygons only** visible. All display settings are restored afterward.
- **Anti-aliasing**: Both tabs enable multisampling AA (`hardwareRenderingGlobals.multiSampleEnable`, `multiSampleCount=16`) and smooth wireframe during the playblast, restored afterward
- **Backface culling**: Enables full backface culling on all meshes during the playblast for cleaner QC review, restores original per-mesh culling values afterward
- **Selection cleared**: Viewport selection is cleared before the playblast so no highlight appears, restored afterward
- **Polygons only (Tab 2 only)**: For matchmove playblasts, all non-polygon object types are hidden (NURBS surfaces, subdivs, planes, lights, cameras, fluids, hair, nCloths, nParticles, strokes, etc.) along with rig elements (joints, nurbs curves, locators, handles, IK handles, deformers, dynamics, manipulators). Only polymeshes remain visible. All visibility settings are restored after the playblast.
- **All geo visible (Tab 1 only)**: Camera track playblasts ensure polymeshes, NURBS surfaces, and subdiv surfaces are visible
- **Platform-aware format**: Prefers `avfoundation` (macOS native) over `qt` (Windows QuickTime). If neither is available, shows a platform-appropriate popup dialog

### Progress Bar
- Visual progress bar with percentage label shown during export
- Advances once per completed export format
- JSX export counts as 2 steps (setup + timeline scrub) so the bar advances early before the slow frame-by-frame processing begins
- Hidden after export completes

### Error Handling
- Pre-flight validation before any export begins, per active tab
- Per-format try/except (one format failing doesn't block others)
- Plugin auto-loading for FBX (`fbxmaya`), Alembic (`AbcExport`), and OBJ (`objExport`)
- QuickTime availability check for playblast (popup if missing)
- Selection state saved and restored after all exports
- FBX baking delegated to the FBX plugin's internal baking (no scene modification or undo chunks)

## Non-Functional Requirements

- **Platform**: Windows and macOS
- **Maya Version**: 2025+ only
- **UI Framework**: Pure `maya.cmds` (no PySide dependency)
- **Single file**: All code in one `.py` file for simplicity
- **No external dependencies**: Only Maya built-in modules
- **String formatting**: `.format()` style (no f-strings, for broader Maya Python compatibility)

## JSX Export Technical Reference

This section documents the complete Maya-to-After Effects conversion pipeline and the critical lessons learned during development. It is intended as a reference for reproducing this work in future projects.

### Reference Materials

The conversion guide `maya_to_after_effects_worldspace.md` describes the general theory. However, several of its recommendations apply specifically to **manually constructed geometry** in AE's coordinate space (e.g., shape layers, point clouds) and do **not** apply to OBJ files imported via `ImportOptions`. The distinctions are documented below.

### Coordinate Systems

| Property       | Maya                        | After Effects                    |
|---------------|-----------------------------|----------------------------------|
| Handedness    | Right-handed                | Left-handed                      |
| Y axis        | Up                          | Down (screen origin top-left)    |
| Z axis        | Forward (camera looks -Z)   | Away from camera (looks +Z)      |
| Matrix layout | Row-major 4x4               | N/A (properties set individually)|

The axis-fix matrix that converts between them is `T = diag(1, -1, -1)`.

### Position Conversion

Position is extracted from the **world** matrix (row 3 in Maya's row-major layout: indices 12, 13, 14):

```
x_ae = tx * ae_scale + comp_cx
y_ae = -ty * ae_scale + comp_cy
z_ae = -tz * ae_scale
```

Where `comp_cx = comp_width / 2` and `comp_cy = comp_height / 2` (AE's origin is top-left; comp center offsets to match).

### Scale Factor (`ae_scale`)

```python
ae_scale = 10.0 * cm_per_unit / 2.54
```

This matches SynthEyes's internal convention where `rescale = 10` calibrated against an inch-based unit system. The `cm_per_unit` lookup converts from Maya's current linear unit (mm, cm, in, ft, yd, m) to centimeters.

### Rotation Conversion — Critical Details

This was the hardest part to get right. The rotation matrix itself is straightforward; the Euler decomposition is where things go wrong if the convention is incorrect.

**Step 1: Extract rotation from the LOCAL (objectSpace) matrix.**

Using `cmds.xform(node, query=True, objectSpace=True, matrix=True)`. This excludes parent group orientation — important because SynthEyes often wraps scene content in a tracking group that rotates the Z-up solve to Maya's Y-up convention. The world matrix would include that parent rotation, producing wrong AE rotations. Position still comes from the world matrix (correct absolute placement).

**Step 2: Normalize to remove scale.**

Extract column magnitudes from the local matrix and divide each column to get a pure rotation matrix R.

**Step 3: Apply the T\*R\*T coordinate change-of-basis.**

```
T = diag(1, -1, -1)

TRT produces (from row-major R):
  [[r00, -r01, -r02],
   [-r10, r11,  r12],
   [-r20, r21,  r22]]
```

Then transpose to get column-major `R_ae` for decomposition.

**Step 4: Decompose as Rx\*Ry\*Rz (intrinsic XYZ).**

After Effects applies rotation properties as `Rx * Ry * Rz`. This is the **critical convention** — using `Rz * Ry * Rx` (which is the other common convention) produces angles that look close but are wrong. The correct decomposition from the column-major `R_ae`:

```
ry = asin(-R_ae[2][0])         # = asin(-r20)
rx = atan2(-R_ae[2][1], R_ae[2][2])  # = atan2(-r21, r22)
rz = atan2(R_ae[1][0], R_ae[0][0])   # = atan2(r10, r00)
```

With gimbal lock handling when `cos(ry) ≈ 0`.

**Why this matters:** In our test scene, the wrong convention (`Rz*Ry*Rx`) produced rx=-18.2, ry=25.5, rz=-0.4. The correct convention (`Rx*Ry*Rz`) produced rx=-19.8, ry=24.3, rz=8.0 — matching the known-working SynthEyes export exactly. The rotation *matrix* was correct in both cases; only the Euler angle extraction differed.

### World-Space Scale

Scale is extracted from the **world** matrix column magnitudes:

```python
sx = sqrt(m[0]**2 + m[1]**2 + m[2]**2)
sy = sqrt(m[4]**2 + m[5]**2 + m[6]**2)
sz = sqrt(m[8]**2 + m[9]**2 + m[10]**2)
```

This captures the full accumulated scale (parent + local). Using `cmds.getAttr(".scaleX")` returns only the local scale attribute, which misses scale inherited from parent groups.

### OBJ Export — Do NOT Flip Vertices

The conversion guide says to flip every vertex `(x, y, z) → (x, -y, -z)`. **This applies to manually constructed geometry in AE's coordinate space, not to OBJ files imported via `ImportOptions`.**

AE's OBJ importer understands the standard Y-up OBJ format natively. The JSX position/rotation/scale properties already handle the Maya-to-AE coordinate transformation for layer placement. Flipping OBJ vertices causes a **double inversion** — the mesh appears upside-down and backwards, making the entire scene look like it's viewed from the bottom-rear.

The correct OBJ pipeline:
1. **Export in local space**: Temporarily reset the node's world matrix to identity before calling `cmds.file(exportSelected=True, type="OBJexport")`, then restore. This prevents Maya's OBJ exporter from baking world-space position into vertices (which would double-offset when AE also applies position/rotation/scale from the JSX).
2. **No vertex modification**: The OBJ file contains standard Y-up local-space geometry. AE imports it as-is.
3. **JSX applies transforms**: Position, rotation, and scale from `_world_matrix_to_ae()` position the mesh correctly in AE's 3D space.

### Simple Plane → AE Solid

Flat meshes (ground planes, cards) are better represented as AE solids than imported OBJ files. Detection uses bounding box flatness: if `min_extent / max_extent < 0.001`, the mesh is considered flat.

The solid is created at comp dimensions, rotated `rx = -90` to lie on the ground plane (AE solids default to the XY plane; `-90` rotates to XZ), and scaled to match the Maya plane's world-space extent:

```
scale_x = (plane_width * ae_scale) / comp_width * 100
scale_y = (plane_depth * ae_scale) / comp_height * 100
```

### OBJ Mesh Scale in AE

AE maps 1 OBJ unit = 512 pixels at 100% scale. The scale applied to imported OBJ layers:

```
scale = world_scale * ae_scale * 100 / 512
```

Where `world_scale` is from the world matrix column magnitudes.

### Camera Rename Safety

The camera is temporarily renamed to `cam_main` for all exports. If a previous export run crashes or is aborted mid-export, the camera may be left renamed. The code checks `cmds.objExists(camera)` before renaming, and falls back to using `cam_main` if it already exists from a prior run.

### Debugging Checklist

When the JSX output doesn't match a known-working reference (e.g., SynthEyes direct export):

1. **Compare camera frame-1 values** (position, rotation, zoom) numerically between the working JSX and your output. They should match within ~0.001.
2. **If positions match but rotations are wrong**: Check the Euler decomposition convention. AE uses `Rx*Ry*Rz`, not `Rz*Ry*Rx`. The matrix itself may be correct while the angles are wrong.
3. **If the mesh is offset from its origin**: The OBJ was likely exported in world space. Use the identity-matrix trick to export in local space.
4. **If the scene appears flipped/upside-down**: OBJ vertices are being double-flipped. Remove any vertex coordinate transformation — AE's OBJ importer handles Y-up natively.
5. **If scale is wrong on geometry**: Check whether you're reading local scale (`cmds.getAttr(".scaleX")`) vs world-space scale (matrix column magnitudes). Parent groups contribute scale that local attributes don't capture.
6. **If rotation differs slightly but consistently**: Check whether you're using the world matrix or local matrix for rotation. Parent group rotations (e.g., SynthEyes Z-up to Y-up conversion groups) should be excluded.

## Out of Scope (v2)
- Batch export of multiple scenes
- Custom FBX/Alembic settings UI
- USD export support
- Network/cloud export paths
- Automatic version incrementing (creating v02 from v01)
- Vertex animation detection/filtering for AE export (simple scenes only in Tab 1)
