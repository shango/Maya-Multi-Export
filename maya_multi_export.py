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
    "2ezbMwAAAABJRU5ErkJggg=="
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
        for fmt, ext in [("ma", ".ma"), ("fbx", ".fbx"), ("abc", ".abc")]:
            dir_path = os.path.join(
                export_root, scene_base_name, fmt, version_str
            )
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

    def export_ma(self, file_path, camera, geo_root, rig_root):
        """Export selection as Maya ASCII."""
        original_cam_name = None
        renamed_cam = None
        try:
            sel = [s for s in [camera, geo_root, rig_root] if s]
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

    def export_fbx(self, file_path, geo_root, rig_root, start_frame, end_frame):
        """Export geo + rig as FBX with baked keyframes."""
        try:
            # Ensure FBX plugin is loaded
            if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
                cmds.loadPlugin("fbxmaya")

            sel = [s for s in [geo_root, rig_root] if s]
            if not sel:
                self.log("[FBX] No geo or rig root assigned.")
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
                mel.eval("FBXExportBakeComplexAnimation -v true")
                mel.eval(
                    "FBXExportBakeComplexStart -v {}".format(int(start_frame))
                )
                mel.eval(
                    "FBXExportBakeComplexEnd -v {}".format(int(end_frame))
                )
                mel.eval("FBXExportBakeComplexStep -v 1")
                mel.eval("FBXExportInputConnections -v false")
                mel.eval("FBXExportSmoothingGroups -v true")
                mel.eval("FBXExportSmoothMesh -v false")
                mel.eval("FBXExportConstraints -v false")
                mel.eval("FBXExportCameras -v false")
                mel.eval("FBXExportLights -v false")
                mel.eval("FBXExportEmbeddedTextures -v false")
                mel.eval("FBXExportSkeletonDefinitions -v true")
                mel.eval("FBXExportInAscii -v false")
                mel.eval('FBXExportFileVersion -v "FBX202000"')

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

    def export_abc(self, file_path, geo_root, start_frame, end_frame):
        """Export geo root as Alembic cache."""
        try:
            # Ensure Alembic plugin is loaded
            if not cmds.pluginInfo("AbcExport", query=True, loaded=True):
                cmds.loadPlugin("AbcExport")

            if not geo_root:
                self.log("[ABC] No geo root assigned.")
                return False

            # Get full DAG path
            long_names = cmds.ls(geo_root, long=True)
            if not long_names:
                self.log(
                    "[ABC] Geo root '{}' not found in scene.".format(geo_root)
                )
                return False
            geo_root_dag = long_names[0]

            abc_path = file_path.replace("\\", "/")

            job_string = (
                "-frameRange {start} {end} "
                "-uvWrite "
                "-worldSpace "
                "-writeVisibility "
                "-dataFormat ogawa "
                "-root {root} "
                "-file {file}"
            ).format(
                start=int(start_frame),
                end=int(end_frame),
                root=geo_root_dag,
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
        for role_name, value in [
            ("Camera", camera),
            ("Geo Root", geo_root),
            ("Rig Root", rig_root),
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
                paths["ma"], camera, geo_root, rig_root
            )

        if do_fbx:
            self._log("Exporting FBX (baking keyframes)...")
            results["fbx"] = exporter.export_fbx(
                paths["fbx"], geo_root, rig_root, start_frame, end_frame
            )

        if do_abc:
            self._log("Exporting Alembic cache...")
            results["abc"] = exporter.export_abc(
                paths["abc"], geo_root, start_frame, end_frame
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
