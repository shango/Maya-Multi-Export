# Export Genie — v6 to v7 Changelog

## UE5 FBX Conformance

- FBX exports now use Z-up axis (`FBXExportUpAxis z`) so cameras import into UE5 without the -90 X rotation offset
- Explicit centimeter unit metadata (`FBXExportConvertUnitString cm`, `FBXExportScaleFactor 1`) so UE5 imports at correct scene scale
- Camera animation is now baked during Matchmove UE5 prep, ensuring reliable camera export with axis conversion

## H.264 (.mp4) via ffmpeg

- New "H.264 (.mp4 Win)" playblast format on all three tabs
- Playblasts to a temporary PNG sequence, then encodes to H.264 .mp4 using a bundled ffmpeg.exe (Windows only)
- No QuickTime installation required — ffmpeg is included in the distribution and auto-installed during drag-and-drop setup
- Temp PNGs are automatically cleaned up after successful encoding; preserved on failure for debugging
- If ffmpeg is not installed, the tool shows a clear error dialog with the expected file path

## Playblast Improvements

- HUD elements are now hidden in all playblasts (`showOrnaments=False`)
- Playblast color management now uses the dedicated playblast output transform setting instead of changing the main viewport view transform
- Raw (sRGB) view is detected dynamically by querying available OCIO views for any name starting with "Raw" — handles "Raw", "Raw (Legacy)", and other variants across Maya versions

## Export Naming

- Export files now use tab-specific naming tags: `cam` (Camera Track), `charMM` (Matchmove), `KTHead` (Face Track)
- QC playblast files always use `track` as their naming tag, regardless of tab
- Folder name remains `<scene>_track_<version>/` for all tabs
- Example: Camera Track exports `shot_cam_v01.ma` + `shot_track_v01.mov` into `shot_track_v01/`

## UI Changes

- "Ctrl Rig Group" renamed to "Rig Group"
- "Anim Geo Group" renamed to "Mesh Group"
- Frame range auto-populates when a camera is loaded — start set to 1001, end set to the camera's last keyframe (queries both transform and shape channels)
- Default start frame is now 1001, even if the Maya timeline starts earlier
- "Use Timeline Range" clamps the start frame to a minimum of 1001
