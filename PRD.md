# Maya Multi-Export Tool — Product Requirements Document

## Overview

A Maya 2025+ addon that lets artists export their scene to multiple formats (.ma, .fbx, .abc) in a single operation, with automatic folder structure creation and versioning. Installed via drag-and-drop of a single `.py` file.

## Problem Statement

Artists in the studio need to export each scene they work on to multiple formats (Maya ASCII, FBX, Alembic). This is currently a tedious manual process requiring:
- Switching export settings per format
- Manually creating folder structures
- Baking keyframes for FBX
- Remembering which objects to include/exclude per format
- Maintaining consistent versioning across formats

## Target Users

- 3D animators and riggers working in Maya 2025+
- Artists on Windows and macOS

## Functional Requirements

### Installation
- **Single-file drag-and-drop install**: User drags `maya_multi_export.py` into the Maya viewport
- Automatically copies itself to Maya's user scripts directory
- Creates a custom shelf button with a distinctive, flashy icon (embedded as base64 in the .py)
- Works on both Windows and macOS

### UI — Shelf Button + Options Panel
- Shelf button on the active shelf opens a `maya.cmds`-based options window
- **Scene Info**: Displays current scene name, detected version, and status
- **Export Root**: Directory picker for the base export location
- **Role Assignment**: Three fields (Camera, Geo Root, Rig Root) with "Load Selection" buttons
  - User selects object(s) in viewport, clicks the corresponding "Load Sel" button
  - Tool validates the object type (camera shape, transform, etc.)
- **Export Formats**: Checkboxes to enable/disable each format (.ma, .fbx, .abc)
- **Frame Range**: Start/end frame fields + "Use Timeline Range" button
- **Export Button**: Triggers the export pipeline
- **Log Panel**: Scrollable text area showing progress and results

### Versioning
- Parse version from Maya filename using `_v##` pattern (e.g., `shot_v01.ma`)
- Support 2–3 digit versions (`_v01`, `_v100`)
- If multiple `_v##` patterns exist, use the last one
- If no version found: warn user, default to `v01`

### Folder Structure
Per-format directories with version subfolders:
```
<export_root>/
  <scene_base_name>/
    ma/
      v01/
        scene_v01.ma
    fbx/
      v01/
        scene_v01.fbx
    abc/
      v01/
        scene_v01.abc
```
Directories are created automatically if they don't exist.

### Export Behavior

#### Maya ASCII (.ma)
- Exports all assigned roles (camera, geo root, rig root) as selected
- No baking or special processing
- Uses `cmds.file(exportSelected=True, type="mayaAscii")`

#### FBX (.fbx)
- Exports **Geo Root + Rig Root** (no camera)
- **Bakes all keyframes** on joints and constrained transforms before export
- Bake is performed inside an undo-chunk and reverted after export (scene stays clean)
- FBX export settings overridden via MEL commands:
  - Bake complex animation: on
  - Constraints: off (baked already)
  - Cameras/Lights: off
  - Embedded textures: off
  - Smoothing groups: on
  - Skeleton definitions: on
  - Binary format, FBX 2020 compatibility
- Uses `mel.eval("FBXExport -f ... -s")` for fine-grained control

#### Alembic (.abc)
- Exports **Geo Root only** (no rig)
- Animation is baked implicitly by Alembic's frame-range sampling (no explicit `bakeResults`)
- Flags: `-uvWrite`, `-worldSpace`, `-writeVisibility`, `-dataFormat ogawa`
- Uses `cmds.AbcExport(j=job_string)` with `-root` flag

### Error Handling
- Pre-flight validation before any export begins
- Per-format try/except (one format failing doesn't block others)
- Plugin auto-loading for FBX (`fbxmaya`) and Alembic (`AbcExport`)
- Selection state saved and restored after all exports
- Undo-chunk safety with try/finally for FBX bake operations

## Non-Functional Requirements

- **Platform**: Windows and macOS
- **Maya Version**: 2025+ only
- **UI Framework**: Pure `maya.cmds` (no PySide dependency)
- **Single file**: All code in one `.py` file for simplicity
- **No external dependencies**: Only Maya built-in modules

## Out of Scope (v1)
- Batch export of multiple scenes
- Custom FBX/Alembic settings UI
- Progress bar for long bake operations
- USD export support
- Network/cloud export paths
- Automatic version incrementing (creating v02 from v01)
