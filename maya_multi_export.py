"""
maya_multi_export.py
Maya Multi-Export Tool — Export scenes to .ma, .fbx, .abc with auto versioning.

Drag and drop this file into Maya's viewport to install.
Compatible with Maya 2025+.
"""

import os
import re
import sys
import shutil
import base64
from functools import partial

import maya.cmds as cmds
import maya.mel as mel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TOOL_NAME = "maya_multi_export"
TOOL_VERSION = "1.0.0"
WINDOW_NAME = "multiExportWindow"
SHELF_BUTTON_LABEL = "MultiExport"
ICON_FILENAME = "maya_multi_export.png"

# Base64-encoded 32x32 RGBA PNG icon (purple-to-cyan gradient with export arrow and badge)
ICON_DATA = (
    "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"
)

# Module-level UI instance
_ui_instance = None


# ---------------------------------------------------------------------------
# VersionParser
# ---------------------------------------------------------------------------
class VersionParser(object):
    """Parse version from Maya scene filename using _v## pattern."""

    VERSION_PATTERN = re.compile(r"_v(\d{2,3})(?=\.|$)")

    @staticmethod
    def parse(scene_name):
        """Extract version from a scene filename.

        Returns:
            tuple: (version_str, version_int) e.g. ("v01", 1)
                   or (None, None) if no version found.
        """
        matches = VersionParser.VERSION_PATTERN.findall(scene_name)
        if matches:
            digits = matches[-1]  # Use the last match
            return ("v" + digits, int(digits))
        return (None, None)

    @staticmethod
    def get_scene_base_name(scene_name):
        """Return scene name stripped of version and extension.

        e.g. "shot_v01.ma" -> "shot"
        """
        name_no_ext = os.path.splitext(scene_name)[0]
        # Remove the last _v## occurrence
        parts = VersionParser.VERSION_PATTERN.findall(name_no_ext)
        if parts:
            last_ver = "_v" + parts[-1]
            idx = name_no_ext.rfind(last_ver)
            if idx >= 0:
                return name_no_ext[:idx]
        return name_no_ext


# ---------------------------------------------------------------------------
# FolderManager
# ---------------------------------------------------------------------------
class FolderManager(object):
    """Create and manage export folder structure."""

    @staticmethod
    def build_export_paths(export_root, scene_base_name, version_str):
        """Build the full set of export paths.

        Returns:
            dict: {"ma": full_path, "fbx": full_path, "abc": full_path}
        """
        paths = {}
        dir_path = os.path.join(
            export_root, scene_base_name + "_maya_exports"
        )
        for fmt, ext in [("ma", ".ma"), ("fbx", ".fbx"), ("abc", ".abc")]:
            file_name = "{base}_{ver}{ext}".format(
                base=scene_base_name, ver=version_str, ext=ext
            )
            paths[fmt] = os.path.join(dir_path, file_name)
        return paths

    @staticmethod
    def ensure_directories(paths):
        """Create all necessary directories for the given paths."""
        for fmt, file_path in paths.items():
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------
class Exporter(object):
    """Handles exporting to each format."""

    def __init__(self, log_callback):
        self.log = log_callback

    def export_ma(self, file_path, camera, geo_root, rig_root, proxy_geo):
        """Export selection as Maya ASCII."""
        original_cam_name = None
        renamed_cam = None
        try:
            sel = [s for s in [camera, geo_root, rig_root, proxy_geo] if s]
            if not sel:
                self.log("[MA] Nothing to export — no roles assigned.")
                return False

            # Rename camera to main_cam for export
            if camera:
                original_cam_name = camera
                renamed_cam = cmds.rename(camera, "main_cam")
                sel = [renamed_cam if s == camera else s for s in sel]

            cmds.select(sel, replace=True)
            cmds.file(
                file_path,
                exportSelected=True,
                type="mayaAscii",
                force=True,
                preserveReferences=False,
            )
            self.log("[MA] Exported: " + file_path)
            return True
        except Exception as e:
            self.log("[MA] FAILED: " + str(e))
            return False
        finally:
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                cmds.rename(renamed_cam, original_cam_name)

    def export_fbx(self, file_path, geo_root, rig_root, proxy_geo, start_frame, end_frame):
        """Export geo + rig + proxy geo as FBX with baked keyframes."""
        try:
            # Ensure FBX plugin is loaded
            if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
                cmds.loadPlugin("fbxmaya")

            sel = [s for s in [geo_root, rig_root, proxy_geo] if s]
            if not sel:
                self.log("[FBX] No geo, rig, or proxy geo assigned.")
                return False

            # Open undo chunk so we can revert baking
            cmds.undoInfo(openChunk=True, chunkName="multi_export_fbx_bake")
            try:
                # Collect bake targets
                bake_targets = []
                if rig_root:
                    joints = (
                        cmds.listRelatives(
                            rig_root,
                            allDescendents=True,
                            type="joint",
                            fullPath=True,
                        )
                        or []
                    )
                    bake_targets.extend(joints)
                if geo_root:
                    transforms = (
                        cmds.listRelatives(
                            geo_root,
                            allDescendents=True,
                            type="transform",
                            fullPath=True,
                        )
                        or []
                    )
                    bake_targets.append(geo_root)
                    bake_targets.extend(transforms)

                # Bake animation
                if bake_targets:
                    cmds.bakeResults(
                        bake_targets,
                        time=(start_frame, end_frame),
                        simulation=True,
                        sampleBy=1,
                        oversamplingRate=1,
                        disableImplicitControl=True,
                        preserveOutsideKeys=False,
                        sparseAnimCurveBake=False,
                        removeBakedAttributeFromLayer=False,
                        bakeOnOverrideLayer=False,
                        minimizeRotation=True,
                    )

                # Set FBX export options
                mel.eval("FBXResetExport")
                # Include Options
                mel.eval("FBXExportInputConnections -v true")
                mel.eval("FBXExportEmbeddedTextures -v false")
                # Animation
                mel.eval("FBXExportAnimation -v true")
                mel.eval("FBXExportQuaternion -v resample")
                # Bake Animation
                mel.eval("FBXExportBakeComplexAnimation -v true")
                mel.eval(
                    "FBXExportBakeComplexStart -v {}".format(int(start_frame))
                )
                mel.eval(
                    "FBXExportBakeComplexEnd -v {}".format(int(end_frame))
                )
                mel.eval("FBXExportBakeComplexStep -v 1")
                mel.eval("FBXExportBakeResampleAnimation -v false")
                # Deformed Models
                mel.eval("FBXExportSkins -v true")
                mel.eval("FBXExportShapes -v true")
                # General
                mel.eval("FBXExportSmoothingGroups -v true")
                mel.eval("FBXExportSmoothMesh -v false")
                mel.eval("FBXExportConstraints -v false")
                mel.eval("FBXExportCameras -v false")
                mel.eval("FBXExportLights -v false")
                mel.eval("FBXExportSkeletonDefinitions -v true")
                mel.eval("FBXExportInAscii -v false")
                mel.eval('FBXExportFileVersion -v "FBX202000"')
                mel.eval("FBXExportUseSceneName -v false")

                # Select and export
                cmds.select(sel, replace=True)
                mel_path = file_path.replace("\\", "/")
                mel.eval('FBXExport -f "{}" -s'.format(mel_path))

                self.log("[FBX] Exported: " + file_path)
                return True
            finally:
                # Revert bake — restore original scene state
                cmds.undoInfo(closeChunk=True)
                cmds.undo()
        except Exception as e:
            self.log("[FBX] FAILED: " + str(e))
            return False

    def export_abc(self, file_path, geo_root, proxy_geo, start_frame, end_frame):
        """Export geo root and proxy geo as Alembic cache."""
        try:
            # Ensure Alembic plugin is loaded
            if not cmds.pluginInfo("AbcExport", query=True, loaded=True):
                cmds.loadPlugin("AbcExport")

            if not geo_root and not proxy_geo:
                self.log("[ABC] No geo root or proxy geo assigned.")
                return False

            # Build root flags for each assigned role
            root_flags = ""
            for node in [geo_root, proxy_geo]:
                if node:
                    long_names = cmds.ls(node, long=True)
                    if not long_names:
                        self.log(
                            "[ABC] '{}' not found in scene.".format(node)
                        )
                        return False
                    root_flags += "-root {} ".format(long_names[0])

            abc_path = file_path.replace("\\", "/")

            job_string = (
                "-frameRange {start} {end} "
                "-uvWrite "
                "-worldSpace "
                "-wholeFrameGeo "
                "-dataFormat ogawa "
                "{roots}"
                "-file '{file}'"
            ).format(
                start=int(start_frame),
                end=int(end_frame),
                roots=root_flags,
                file=abc_path,
            )

            cmds.AbcExport(j=job_string)
            self.log("[ABC] Exported: " + file_path)
            return True
        except Exception as e:
            self.log("[ABC] FAILED: " + str(e))
            return False


# ---------------------------------------------------------------------------
# MultiExportUI
# ---------------------------------------------------------------------------
class MultiExportUI(object):
    """Main UI window built with maya.cmds."""

    def __init__(self):
        self.window = None
        self.scene_info_text = None
        self.version_text = None
        self.export_root_field = None
        self.camera_field = None
        self.geo_root_field = None
        self.rig_root_field = None
        self.proxy_geo_field = None
        self.ma_checkbox = None
        self.fbx_checkbox = None
        self.abc_checkbox = None
        self.start_frame_field = None
        self.end_frame_field = None
        self.log_field = None

    def show(self):
        """Build and display the UI window."""
        if cmds.window(WINDOW_NAME, exists=True):
            cmds.deleteUI(WINDOW_NAME)

        self.window = cmds.window(
            WINDOW_NAME,
            title="Maya Multi-Export  v{}".format(TOOL_VERSION),
            widthHeight=(440, 600),
            sizeable=True,
        )

        cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4, columnAttach=("both", 6)
        )

        cmds.separator(height=4, style="none")

        # --- Scene Info ---
        cmds.frameLayout(
            label="Scene Info",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.scene_info_text = cmds.text(label="Scene: (none)", align="left")
        self.version_text = cmds.text(label="Version: (none)", align="left")
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Export Root ---
        cmds.frameLayout(
            label="Export Root Directory",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        self.export_root_field = cmds.textFieldButtonGrp(
            label="Path:",
            buttonLabel="Browse...",
            columnWidth3=(40, 300, 70),
        )
        cmds.textFieldButtonGrp(
            self.export_root_field,
            edit=True,
            buttonCommand=partial(self._browse_export_root),
        )
        cmds.setParent("..")

        # --- Role Assignment ---
        cmds.frameLayout(
            label="Role Assignment",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self.camera_field = cmds.textFieldButtonGrp(
            label="Camera:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.camera_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "camera"),
        )

        self.geo_root_field = cmds.textFieldButtonGrp(
            label="Geo Root:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.geo_root_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "geo"),
        )

        self.rig_root_field = cmds.textFieldButtonGrp(
            label="Rig Root:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.rig_root_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "rig"),
        )

        self.proxy_geo_field = cmds.textFieldButtonGrp(
            label="Proxy Geo:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.proxy_geo_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "proxy"),
        )

        cmds.setParent("..")
        cmds.setParent("..")

        # --- Export Formats ---
        cmds.frameLayout(
            label="Export Formats",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.ma_checkbox = cmds.checkBox(
            label="  Maya ASCII (.ma)", value=True
        )
        self.fbx_checkbox = cmds.checkBox(label="  FBX (.fbx)", value=True)
        self.abc_checkbox = cmds.checkBox(
            label="  Alembic (.abc)", value=True
        )
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Frame Range ---
        cmds.frameLayout(
            label="Frame Range",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
        cmds.rowLayout(
            numberOfColumns=5,
            columnWidth5=(60, 70, 20, 60, 70),
            columnAlign5=("right", "left", "center", "right", "left"),
        )
        cmds.text(label="Start: ")
        self.start_frame_field = cmds.intField(value=1, width=65)
        cmds.text(label="")
        cmds.text(label="End: ")
        self.end_frame_field = cmds.intField(value=100, width=65)
        cmds.setParent("..")
        cmds.button(
            label="Use Timeline Range",
            command=partial(self._set_timeline_range),
        )
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Export Button ---
        cmds.separator(height=8, style="none")
        cmds.button(
            label="E X P O R T",
            height=40,
            backgroundColor=(0.2, 0.62, 0.35),
            command=partial(self._on_export),
        )
        cmds.separator(height=4, style="none")

        # --- Log ---
        cmds.frameLayout(
            label="Log",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        self.log_field = cmds.scrollField(
            editable=False, wordWrap=True, height=120, text=""
        )
        cmds.setParent("..")

        # --- Version ---
        cmds.text(
            label="v{}".format(TOOL_VERSION),
            align="right",
            font="smallObliqueLabelFont",
        )

        # Populate scene info
        self._refresh_scene_info()
        # Auto-set timeline range
        self._set_timeline_range()

        cmds.showWindow(self.window)

    # --- Callbacks ---

    def _browse_export_root(self, *args):
        result = cmds.fileDialog2(
            fileMode=3, caption="Select Export Root Directory"
        )
        if result:
            cmds.textFieldButtonGrp(
                self.export_root_field, edit=True, text=result[0]
            )

    def _load_selection(self, role, *args):
        sel = cmds.ls(selection=True, long=False)
        if not sel:
            cmds.confirmDialog(
                title="No Selection",
                message="Nothing is selected. Please select an object first.",
                button=["OK"],
            )
            return

        obj = sel[0]

        if role == "camera":
            # Validate: the selected object should have a camera shape
            shapes = cmds.listRelatives(obj, shapes=True, type="camera") or []
            if not shapes:
                # Maybe they selected the shape directly
                if cmds.nodeType(obj) == "camera":
                    # Get the transform parent
                    parents = cmds.listRelatives(obj, parent=True)
                    if parents:
                        obj = parents[0]
                else:
                    cmds.confirmDialog(
                        title="Invalid Selection",
                        message="'{}' is not a camera. Please select a camera.".format(
                            obj
                        ),
                        button=["OK"],
                    )
                    return
            cmds.textFieldButtonGrp(
                self.camera_field, edit=True, text=obj
            )

        elif role == "geo":
            if cmds.nodeType(obj) != "transform":
                cmds.confirmDialog(
                    title="Invalid Selection",
                    message="'{}' is not a transform node. Please select the geo group/root.".format(
                        obj
                    ),
                    button=["OK"],
                )
                return
            cmds.textFieldButtonGrp(
                self.geo_root_field, edit=True, text=obj
            )

        elif role == "rig":
            if cmds.nodeType(obj) != "transform":
                cmds.confirmDialog(
                    title="Invalid Selection",
                    message="'{}' is not a transform node. Please select the rig root.".format(
                        obj
                    ),
                    button=["OK"],
                )
                return
            cmds.textFieldButtonGrp(
                self.rig_root_field, edit=True, text=obj
            )

        elif role == "proxy":
            if cmds.nodeType(obj) != "transform":
                cmds.confirmDialog(
                    title="Invalid Selection",
                    message="'{}' is not a transform node. Please select the proxy geo root.".format(
                        obj
                    ),
                    button=["OK"],
                )
                return
            cmds.textFieldButtonGrp(
                self.proxy_geo_field, edit=True, text=obj
            )

    def _set_timeline_range(self, *args):
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        cmds.intField(self.start_frame_field, edit=True, value=int(start))
        cmds.intField(self.end_frame_field, edit=True, value=int(end))

    def _refresh_scene_info(self):
        scene_path = cmds.file(query=True, sceneName=True)
        if scene_path:
            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            cmds.text(
                self.scene_info_text,
                edit=True,
                label="Scene: " + scene_short,
            )
            ver_str, _ = VersionParser.parse(scene_short)
            if ver_str:
                cmds.text(
                    self.version_text,
                    edit=True,
                    label="Version: {} (detected)".format(ver_str),
                )
            else:
                cmds.text(
                    self.version_text,
                    edit=True,
                    label="Version: (none detected — will default to v01)",
                )
        else:
            cmds.text(
                self.scene_info_text,
                edit=True,
                label="Scene: (unsaved scene)",
            )
            cmds.text(
                self.version_text,
                edit=True,
                label="Version: (save scene first)",
            )

    def _log(self, message):
        current = cmds.scrollField(self.log_field, query=True, text=True)
        if current:
            updated = current + "\n" + message
        else:
            updated = message
        cmds.scrollField(self.log_field, edit=True, text=updated)
        # Scroll to bottom
        cmds.scrollField(
            self.log_field, edit=True, insertionPosition=len(updated)
        )

    # --- Validation ---

    def _validate(self):
        """Return (errors, warnings) lists."""
        errors = []
        warnings = []

        # Scene must be saved
        scene_path = cmds.file(query=True, sceneName=True)
        if not scene_path:
            errors.append("Scene has not been saved. Please save first.")

        # Export root must be set and exist
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        if not export_root:
            errors.append("Export root directory is not set.")
        elif not os.path.isdir(export_root):
            errors.append(
                "Export root directory does not exist:\n" + export_root
            )

        # At least one format
        do_ma = cmds.checkBox(self.ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.abc_checkbox, query=True, value=True)
        if not (do_ma or do_fbx or do_abc):
            errors.append("No export format selected.")

        # Role assignments
        camera = cmds.textFieldButtonGrp(
            self.camera_field, query=True, text=True
        ).strip()
        geo_root = cmds.textFieldButtonGrp(
            self.geo_root_field, query=True, text=True
        ).strip()
        rig_root = cmds.textFieldButtonGrp(
            self.rig_root_field, query=True, text=True
        ).strip()

        if do_ma and not any([geo_root, rig_root, camera]):
            errors.append(
                "MA export enabled but no roles assigned (nothing to export)."
            )
        if do_fbx and not (geo_root or rig_root):
            errors.append(
                "FBX export enabled but no Geo Root or Rig Root assigned."
            )
        if do_abc and not geo_root:
            errors.append("Alembic export enabled but no Geo Root assigned.")

        # Verify assigned objects exist
        proxy_geo = cmds.textFieldButtonGrp(
            self.proxy_geo_field, query=True, text=True
        ).strip()
        for role_name, value in [
            ("Camera", camera),
            ("Geo Root", geo_root),
            ("Rig Root", rig_root),
            ("Proxy Geo", proxy_geo),
        ]:
            if value and not cmds.objExists(value):
                errors.append(
                    "{} '{}' no longer exists in the scene.".format(
                        role_name, value
                    )
                )

        # Frame range
        start = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end = cmds.intField(self.end_frame_field, query=True, value=True)
        if end <= start:
            errors.append("End frame must be greater than start frame.")

        # Version warning
        if scene_path:
            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            ver_str, _ = VersionParser.parse(scene_short)
            if ver_str is None:
                warnings.append(
                    "No _v## version found in filename '{}'.\n"
                    "Will default to v01.".format(scene_short)
                )

        return errors, warnings

    # --- Export Orchestration ---

    def _on_export(self, *args):
        """Main export callback."""
        # Clear log
        cmds.scrollField(self.log_field, edit=True, text="")
        self._log("Starting export...")

        # Validate
        errors, warnings = self._validate()
        if errors:
            cmds.confirmDialog(
                title="Export Errors",
                message="\n\n".join(errors),
                button=["OK"],
            )
            self._log("Export aborted due to errors.")
            return

        if warnings:
            result = cmds.confirmDialog(
                title="Warnings",
                message="\n\n".join(warnings),
                button=["Continue", "Cancel"],
                defaultButton="Continue",
                cancelButton="Cancel",
                dismissString="Cancel",
            )
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        # Save original selection
        original_sel = cmds.ls(selection=True)

        # Gather settings
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        camera = cmds.textFieldButtonGrp(
            self.camera_field, query=True, text=True
        ).strip()
        geo_root = cmds.textFieldButtonGrp(
            self.geo_root_field, query=True, text=True
        ).strip()
        rig_root = cmds.textFieldButtonGrp(
            self.rig_root_field, query=True, text=True
        ).strip()
        proxy_geo = cmds.textFieldButtonGrp(
            self.proxy_geo_field, query=True, text=True
        ).strip()
        do_ma = cmds.checkBox(self.ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.abc_checkbox, query=True, value=True)
        start_frame = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end_frame = cmds.intField(
            self.end_frame_field, query=True, value=True
        )

        # Parse version
        scene_short = cmds.file(
            query=True, sceneName=True, shortName=True
        )
        version_str, _ = VersionParser.parse(scene_short)
        if version_str is None:
            version_str = "v01"
        scene_base = VersionParser.get_scene_base_name(scene_short)

        self._log("Scene: {} | Version: {}".format(scene_base, version_str))

        # Build paths and create directories
        paths = FolderManager.build_export_paths(
            export_root, scene_base, version_str
        )
        FolderManager.ensure_directories(paths)

        self._log("Folder structure created.")

        # Run exports
        exporter = Exporter(self._log)
        results = {}

        if do_ma:
            self._log("Exporting Maya ASCII...")
            results["ma"] = exporter.export_ma(
                paths["ma"], camera, geo_root, rig_root, proxy_geo
            )

        if do_fbx:
            self._log("Exporting FBX (baking keyframes)...")
            results["fbx"] = exporter.export_fbx(
                paths["fbx"], geo_root, rig_root, proxy_geo, start_frame, end_frame
            )

        if do_abc:
            self._log("Exporting Alembic cache...")
            results["abc"] = exporter.export_abc(
                paths["abc"], geo_root, proxy_geo, start_frame, end_frame
            )

        # Summary
        self._log("--- Export Complete ---")
        for fmt, success in results.items():
            status = "OK" if success else "FAILED"
            self._log("  {}: {} -> {}".format(fmt.upper(), status, paths[fmt]))

        # Restore selection
        if original_sel:
            cmds.select(original_sel, replace=True)
        else:
            cmds.select(clear=True)

        # Show completion dialog
        failed = [k for k, v in results.items() if not v]
        if failed:
            cmds.confirmDialog(
                title="Export Complete (with errors)",
                message="Some exports failed: {}\nSee the log for details.".format(
                    ", ".join(f.upper() for f in failed)
                ),
                button=["OK"],
            )
        else:
            cmds.confirmDialog(
                title="Export Complete",
                message="All exports completed successfully!",
                button=["OK"],
            )


# ---------------------------------------------------------------------------
# Entry Points
# ---------------------------------------------------------------------------
def launch():
    """Open the Multi-Export UI. Called by the shelf button."""
    global _ui_instance
    _ui_instance = MultiExportUI()
    _ui_instance.show()


# ---------------------------------------------------------------------------
# Installer
# ---------------------------------------------------------------------------
def _get_maya_app_dir():
    """Return the user's Maya application directory."""
    return cmds.internalVar(userAppDir=True)


def _get_scripts_dir():
    """Return the user's Maya scripts directory."""
    return os.path.join(_get_maya_app_dir(), "scripts")


def _get_icons_dir():
    """Return the user's Maya icons directory (create if needed)."""
    icons_dir = os.path.join(_get_maya_app_dir(), "prefs", "icons")
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    return icons_dir


def _install_icon():
    """Decode the embedded icon and write it to Maya's icons directory."""
    icon_path = os.path.join(_get_icons_dir(), ICON_FILENAME)
    icon_bytes = base64.b64decode(ICON_DATA)
    with open(icon_path, "wb") as f:
        f.write(icon_bytes)
    return icon_path


def _create_shelf_button():
    """Create the shelf button on the currently active shelf."""
    # Install the icon file
    _install_icon()

    # Get the active shelf
    top_shelf = mel.eval("$temp = $gShelfTopLevel")
    current_shelf = cmds.shelfTabLayout(
        top_shelf, query=True, selectTab=True
    )

    # Remove existing button to avoid duplicates
    existing = cmds.shelfLayout(
        current_shelf, query=True, childArray=True
    ) or []
    for btn in existing:
        try:
            if cmds.shelfButton(btn, query=True, exists=True):
                label = cmds.shelfButton(btn, query=True, label=True)
                if label == SHELF_BUTTON_LABEL:
                    cmds.deleteUI(btn)
        except Exception:
            pass

    # Create the button
    cmds.shelfButton(
        parent=current_shelf,
        label=SHELF_BUTTON_LABEL,
        annotation="Maya Multi-Export: Export to .ma, .fbx, .abc",
        image1=ICON_FILENAME,
        command=(
            "import importlib\n"
            "import maya_multi_export\n"
            "importlib.reload(maya_multi_export)\n"
            "maya_multi_export.launch()\n"
        ),
        sourceType="python",
    )


def install():
    """Install the tool: copy to scripts dir and create shelf button."""
    source_file = os.path.abspath(__file__)
    scripts_dir = _get_scripts_dir()
    dest_file = os.path.join(scripts_dir, "maya_multi_export.py")

    # Copy self to Maya's scripts directory (if not already there)
    if os.path.normpath(source_file) != os.path.normpath(dest_file):
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        shutil.copy2(source_file, dest_file)

    # Purge cached module for clean reimport
    if TOOL_NAME in sys.modules:
        del sys.modules[TOOL_NAME]

    # Create shelf button
    _create_shelf_button()

    cmds.confirmDialog(
        title="Install Complete",
        message=(
            "Maya Multi-Export v{} installed!\n\n"
            "A shelf button has been added to your current shelf.\n"
            "Click it to open the export tool."
        ).format(TOOL_VERSION),
        button=["OK"],
    )


def onMayaDroppedPythonFile(*args, **kwargs):
    """Maya drag-and-drop hook — called when this file is dropped into the viewport."""
    install()
