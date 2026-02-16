"""
maya_multi_export.py  v1.2.0
Maya Multi-Export Tool — Export scenes to .ma, .fbx, .abc with auto versioning.

Drag and drop this file into Maya's viewport to install.
Compatible with Maya 2025+.
"""

import math
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
TOOL_VERSION = "1.2.0"
WINDOW_NAME = "multiExportWindow"
SHELF_BUTTON_LABEL = "MultiExport"
ICON_FILENAME = "maya_multi_export.png"

# Tab identifiers
TAB_CAMERA_TRACK = "camera_track"
TAB_MATCHMOVE = "matchmove"


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
            dict: {"ma": path, "fbx": path, "abc": path, "mov": path}
        """
        paths = {}
        dir_name = "{}_track_{}".format(scene_base_name, version_str)
        dir_path = os.path.join(export_root, dir_name)
        for fmt, ext in [("ma", ".ma"), ("fbx", ".fbx"), ("abc", ".abc")]:
            file_name = "{base}_{ver}{ext}".format(
                base=scene_base_name, ver=version_str, ext=ext
            )
            paths[fmt] = os.path.join(dir_path, file_name)
        # QC playblast gets a _qc suffix
        qc_name = "{base}_{ver}_qc.mov".format(
            base=scene_base_name, ver=version_str
        )
        paths["mov"] = os.path.join(dir_path, qc_name)
        return paths

    @staticmethod
    def ensure_directories(paths):
        """Create all necessary directories for the given paths."""
        for fmt, file_path in paths.items():
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    @staticmethod
    def build_ae_export_paths(export_root, scene_base_name, version_str, geo_names):
        """Build export paths for AE JSX + OBJ files.

        Args:
            export_root: Base export directory.
            scene_base_name: Scene name without version/extension.
            version_str: Version string e.g. "v01".
            geo_names: List of geometry child names for OBJ files.

        Returns:
            dict: {"jsx": full_path, "obj": {geo_name: full_path, ...}}
        """
        main_dir_name = "{}_track_{}".format(
            scene_base_name, version_str
        )
        ae_dir_name = "{}_track_afterEffects_{}".format(
            scene_base_name, version_str
        )
        ae_dir = os.path.join(export_root, main_dir_name, ae_dir_name)
        jsx_name = "{base}_{ver}.jsx".format(
            base=scene_base_name, ver=version_str
        )
        paths = {"jsx": os.path.join(ae_dir, jsx_name), "obj": {}}
        for geo_name in geo_names:
            obj_name = "{base}_{ver}_{geo}.obj".format(
                base=scene_base_name, ver=version_str, geo=geo_name
            )
            paths["obj"][geo_name] = os.path.join(ae_dir, obj_name)
        return paths

    @staticmethod
    def ensure_ae_directories(ae_paths):
        """Create the AE subfolder if needed."""
        ae_dir = os.path.dirname(ae_paths["jsx"])
        if not os.path.exists(ae_dir):
            os.makedirs(ae_dir)

    @staticmethod
    def resolve_versioned_dir(export_root, scene_base_name, version_str):
        """Find or create the versioned export directory.

        If an older version folder exists (e.g. _track_v01), rename it
        to the current version. Existing files inside are preserved.

        Returns:
            str: Path to the export directory.
        """
        target_name = "{}_track_{}".format(scene_base_name, version_str)
        target_dir = os.path.join(export_root, target_name)
        if os.path.isdir(target_dir):
            return target_dir

        # Search for an existing _track_v## folder to rename
        prefix = scene_base_name + "_track_v"
        try:
            for entry in sorted(os.listdir(export_root)):
                if (entry.startswith(prefix)
                        and os.path.isdir(
                            os.path.join(export_root, entry))):
                    old_dir = os.path.join(export_root, entry)
                    os.rename(old_dir, target_dir)
                    return target_dir
        except OSError:
            pass

        return target_dir

    @staticmethod
    def resolve_ae_dir(parent_dir, scene_base_name, version_str):
        """Find or create the versioned AE export subdirectory.

        If an older version AE folder exists inside *parent_dir*,
        rename it to the current version.

        Returns:
            str: Path to the AE directory.
        """
        target_name = "{}_track_afterEffects_{}".format(
            scene_base_name, version_str
        )
        target_dir = os.path.join(parent_dir, target_name)
        if os.path.isdir(target_dir):
            return target_dir

        prefix = scene_base_name + "_track_afterEffects_v"
        try:
            for entry in sorted(os.listdir(parent_dir)):
                if (entry.startswith(prefix)
                        and os.path.isdir(
                            os.path.join(parent_dir, entry))):
                    old_dir = os.path.join(parent_dir, entry)
                    os.rename(old_dir, target_dir)
                    return target_dir
        except OSError:
            pass

        return target_dir


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------
class Exporter(object):
    """Handles exporting to each format."""

    def __init__(self, log_callback):
        self.log = log_callback

    @staticmethod
    def _is_descendant_of(node, ancestor):
        """Return True if *node* is the same as or a descendant of *ancestor*."""
        if not node or not ancestor:
            return False
        node_long = cmds.ls(node, long=True)
        ancestor_long = cmds.ls(ancestor, long=True)
        if not node_long or not ancestor_long:
            return False
        # A node's long name starts with the ancestor's long name + "|"
        return (node_long[0] == ancestor_long[0]
                or node_long[0].startswith(ancestor_long[0] + "|"))

    def export_ma(self, file_path, camera, geo_roots, rig_roots, proxy_geo):
        """Export selection as Maya ASCII.

        Camera should already be renamed to 'cam_main' by the caller.
        Namespaces are stripped so exported nodes have clean names.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            rig_roots: list of rig root transforms (or empty list).
        """
        try:
            geo_roots = geo_roots or []
            rig_roots = rig_roots or []
            # Skip camera if it's a descendant of any geo root
            cam_under_geo = any(
                self._is_descendant_of(camera, gr)
                for gr in geo_roots if gr
            )
            effective_cam = None if cam_under_geo else camera
            sel = [s for s in [effective_cam, proxy_geo] if s]
            sel.extend(geo_roots)
            sel.extend(rig_roots)
            # Include image plane transforms so the source footage
            # reference is preserved in the exported .ma file.
            if camera:
                sel.extend(self._get_image_plane_transforms(camera))
            if not sel:
                self.log("[MA] Nothing to export — no roles assigned.")
                return False

            # Strip namespaces inside an undo chunk so we can revert
            cmds.undoInfo(
                openChunk=True, chunkName="multi_export_ma_ns"
            )
            try:
                # Import file references so their namespaces become removable
                for ref_node in cmds.ls(type="reference") or []:
                    try:
                        if cmds.referenceQuery(ref_node, isLoaded=True):
                            ref_file = cmds.referenceQuery(
                                ref_node, filename=True
                            )
                            cmds.file(ref_file, importReference=True)
                    except Exception:
                        pass

                # Remove non-default namespaces
                default_ns = {"UI", "shared"}
                all_ns = (
                    cmds.namespaceInfo(
                        listOnlyNamespaces=True, recurse=True
                    ) or []
                )
                # Process deepest namespaces first
                for ns in reversed(sorted(all_ns, key=len)):
                    if ns not in default_ns:
                        try:
                            cmds.namespace(
                                removeNamespace=ns,
                                mergeNamespaceWithRoot=True,
                            )
                        except Exception:
                            pass

                # Re-resolve selection (names may have changed)
                resolved = []
                for s in sel:
                    # Strip namespace prefix if present
                    short = s.rsplit(":", 1)[-1] if ":" in s else s
                    if cmds.objExists(short):
                        resolved.append(short)
                    elif cmds.objExists(s):
                        resolved.append(s)

                cmds.select(resolved, replace=True)
                cmds.file(
                    file_path,
                    exportSelected=True,
                    type="mayaAscii",
                    force=True,
                    preserveReferences=False,
                )
                self.log("[MA] Exported: " + file_path)
                return True
            finally:
                cmds.undoInfo(closeChunk=True)
                cmds.undo()
        except Exception as e:
            self.log("[MA] FAILED: " + str(e))
            return False

    def export_fbx(self, file_path, camera, geo_roots, rig_roots, proxy_geo,
                   start_frame, end_frame):
        """Export camera + geo + rig + proxy geo as FBX with baked keyframes.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            rig_roots: list of rig root transforms (or empty list).
        """
        try:
            geo_roots = geo_roots or []
            rig_roots = rig_roots or []
            # Ensure FBX plugin is loaded
            if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
                try:
                    cmds.loadPlugin("fbxmaya")
                except Exception:
                    self.log("[FBX] fbxmaya plugin is not available.")
                    cmds.confirmDialog(
                        title="FBX Plugin Not Found",
                        message=(
                            "The FBX plugin (fbxmaya) could not be loaded.\n\n"
                            "To enable it, go to:\n"
                            "Windows > Settings/Preferences > Plug-in Manager\n\n"
                            "Find 'fbxmaya' in the list and check 'Loaded'."
                        ),
                        button=["OK"],
                    )
                    return False

            # Skip camera if it's a descendant of any geo root
            cam_under_geo = any(
                self._is_descendant_of(camera, gr)
                for gr in geo_roots if gr
            )
            effective_cam = None if cam_under_geo else camera
            sel = [s for s in [effective_cam, proxy_geo] if s]
            sel.extend(geo_roots)
            sel.extend(rig_roots)
            if not sel:
                self.log("[FBX] Nothing to export — no roles assigned.")
                return False

            # Open undo chunk so we can revert baking
            cmds.undoInfo(openChunk=True, chunkName="multi_export_fbx_bake")
            try:
                # Collect bake targets: camera, joints, and constrained transforms
                bake_targets = []

                # Camera always gets baked (has animation) — even if under geo_root
                if camera:
                    bake_targets.append(cmds.ls(camera, long=True)[0])

                # Rig roots: bake ALL joints and transforms.
                # Rigs use constraints, expressions, IK, set-driven keys,
                # motion paths, etc. — any transform could be driven by
                # any mechanism, so bake everything to be safe.
                for rig_root in rig_roots:
                    if not rig_root:
                        continue
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
                    all_transforms = (
                        cmds.listRelatives(
                            rig_root,
                            allDescendents=True,
                            type="transform",
                            fullPath=True,
                        )
                        or []
                    )
                    all_transforms.insert(
                        0, cmds.ls(rig_root, long=True)[0]
                    )
                    bake_targets.extend(all_transforms)

                # Geo/proxy roots: only bake transforms that have
                # animation curves (e.g. object-tracked geo).
                for root in geo_roots + [proxy_geo]:
                    if not root:
                        continue
                    descendants = (
                        cmds.listRelatives(
                            root,
                            allDescendents=True,
                            type="transform",
                            fullPath=True,
                        )
                        or []
                    )
                    descendants.insert(0, cmds.ls(root, long=True)[0])
                    for tfm in descendants:
                        anim_curves = cmds.listConnections(
                            tfm, type="animCurve"
                        )
                        if anim_curves:
                            bake_targets.append(tfm)

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
                mel.eval("FBXExportInputConnections -v false")
                mel.eval("FBXExportEmbeddedTextures -v false")
                # Animation
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
                mel.eval("FBXExportCameras -v true")
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

    def export_abc(self, file_path, camera, geo_roots, proxy_geo,
                   start_frame, end_frame):
        """Export camera + geo roots + proxy geo as Alembic cache.

        Args:
            geo_roots: list of geo root transforms (or empty list).
        """
        try:
            geo_roots = geo_roots or []
            # Ensure Alembic plugin is loaded
            if not cmds.pluginInfo("AbcExport", query=True, loaded=True):
                try:
                    cmds.loadPlugin("AbcExport")
                except Exception:
                    self.log("[ABC] AbcExport plugin is not available.")
                    cmds.confirmDialog(
                        title="Alembic Plugin Not Found",
                        message=(
                            "The Alembic plugin (AbcExport) could not be loaded.\n\n"
                            "To enable it, go to:\n"
                            "Windows > Settings/Preferences > Plug-in Manager\n\n"
                            "Find 'AbcExport' in the list and check 'Loaded'."
                        ),
                        button=["OK"],
                    )
                    return False

            if not camera and not geo_roots and not proxy_geo:
                self.log("[ABC] Nothing to export — no roles assigned.")
                return False

            # Strip namespaces inside an undo chunk for clean export
            cmds.undoInfo(
                openChunk=True, chunkName="multi_export_abc_ns"
            )
            try:
                # Import file references so their namespaces become removable
                for ref_node in cmds.ls(type="reference") or []:
                    try:
                        if cmds.referenceQuery(ref_node, isLoaded=True):
                            ref_file = cmds.referenceQuery(
                                ref_node, filename=True
                            )
                            cmds.file(ref_file, importReference=True)
                    except Exception:
                        pass

                default_ns = {"UI", "shared"}
                all_ns = (
                    cmds.namespaceInfo(
                        listOnlyNamespaces=True, recurse=True
                    ) or []
                )
                for ns in reversed(sorted(all_ns, key=len)):
                    if ns not in default_ns:
                        try:
                            cmds.namespace(
                                removeNamespace=ns,
                                mergeNamespaceWithRoot=True,
                            )
                        except Exception:
                            pass

                # Build root flags (re-resolve after namespace strip)
                cam_under_geo = any(
                    self._is_descendant_of(camera, gr)
                    for gr in geo_roots if gr
                )
                root_flags = ""
                root_nodes = [camera] + geo_roots + [proxy_geo]
                for node in root_nodes:
                    if not node:
                        continue
                    if node == camera and cam_under_geo:
                        continue
                    # Resolve short name after namespace strip
                    short = node.rsplit(":", 1)[-1] if ":" in node else node
                    resolved = short if cmds.objExists(short) else node
                    long_names = cmds.ls(resolved, long=True)
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
                    "-stripNamespaces "
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
            finally:
                cmds.undoInfo(closeChunk=True)
                cmds.undo()
        except Exception as e:
            self.log("[ABC] FAILED: " + str(e))
            return False

    # --- OBJ Export ---

    def export_obj(self, file_path, geo_node):
        """Export a single Maya object as OBJ in local space.

        Maya's OBJ exporter writes vertices in world space.  To avoid a
        double-offset in After Effects (where the JSX also sets position/
        rotation/scale), we temporarily reset the node's world matrix to
        identity so vertices are written in local (object) space.

        Args:
            file_path: Output .obj path.
            geo_node: Maya transform node to export.

        Returns:
            bool: True on success.
        """
        try:
            if not cmds.pluginInfo("objExport", query=True, loaded=True):
                cmds.loadPlugin("objExport")

            # Save the current world matrix and reset to identity so the
            # OBJ exporter writes vertices in local space.
            orig_m = cmds.xform(geo_node, query=True,
                                worldSpace=True, matrix=True)
            identity = [1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
            cmds.xform(geo_node, worldSpace=True, matrix=identity)

            try:
                cmds.select(geo_node, replace=True)
                cmds.file(
                    file_path,
                    exportSelected=True,
                    type="OBJexport",
                    force=True,
                    options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1",
                )
            finally:
                # Always restore the original transform.
                cmds.xform(geo_node, worldSpace=True, matrix=orig_m)

            self.log("[OBJ] Exported: " + file_path)
            return True
        except Exception as e:
            self.log("[OBJ] FAILED: " + str(e))
            return False

    @staticmethod
    def _is_simple_plane(node):
        """Return True if *node* is a flat/planar mesh (suitable for AE solid).

        Checks whether the world-space bounding box is effectively flat
        along one axis (thinnest extent < 0.1 % of the largest).  This
        catches simple quads as well as subdivided planes.
        """
        shapes = cmds.listRelatives(node, shapes=True, type="mesh") or []
        if not shapes:
            return False
        try:
            bbox = cmds.exactWorldBoundingBox(node)
            extents = [bbox[3] - bbox[0],
                       bbox[4] - bbox[1],
                       bbox[5] - bbox[2]]
            max_ext = max(extents)
            if max_ext < 1e-9:
                return False
            min_ext = min(extents)
            return min_ext / max_ext < 0.001
        except Exception:
            return False

    def export_playblast(self, file_path, camera, start_frame, end_frame,
                         hide_rig_elements=False):
        """Export a QC playblast as H.264 .mov via QuickTime at 1920x1080.

        Args:
            hide_rig_elements: If True, hides joints, nurbs curves,
                locators, and handles in the viewport so only skin
                geometry and static geo are visible (Matchmove tab).
        """
        try:
            # Check .mov format availability:
            #   macOS: "avfoundation" (native)
            #   Windows: "qt" (requires Apple QuickTime Essentials)
            available_formats = cmds.playblast(
                format=True, query=True
            ) or []
            if "avfoundation" in available_formats:
                pb_format = "avfoundation"
            elif "qt" in available_formats:
                pb_format = "qt"
            else:
                self.log("[Playblast] No .mov format available.")
                cmds.confirmDialog(
                    title="QuickTime Not Found",
                    message=(
                        "No .mov playblast format is available.\n\n"
                        "Windows: Install Apple QuickTime Essentials "
                        "and restart Maya.\n"
                        "macOS: AVFoundation should be built-in — "
                        "check Maya's Plug-in Manager."
                    ),
                    button=["OK"],
                )
                return False

            # Find a visible model panel for the playblast.
            # Cannot rely on withFocus — clicking EXPORT shifts focus
            # to the tool window, not a model panel.
            model_panel = None
            for panel in (cmds.getPanel(visiblePanels=True) or []):
                if cmds.getPanel(typeOf=panel) == "modelPanel":
                    model_panel = panel
                    break
            if not model_panel:
                # Fallback to any model panel
                panels = cmds.getPanel(type="modelPanel") or []
                if panels:
                    model_panel = panels[0]

            original_cam = None
            if camera and model_panel:
                original_cam = cmds.modelPanel(
                    model_panel, query=True, camera=True
                )
                cmds.lookThru(model_panel, camera)

            # Set viewport display mode:
            #   Matchmove -> wireframe on shaded, AA on, polygons only
            #   Camera track -> wireframe
            original_display = None
            original_wos = None
            original_aa = None
            target_display = "smoothShaded" if hide_rig_elements else "wireframe"
            if model_panel:
                original_display = cmds.modelEditor(
                    model_panel, query=True, displayAppearance=True
                )
                if original_display != target_display:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        displayAppearance=target_display,
                    )
                if hide_rig_elements:
                    original_wos = cmds.modelEditor(
                        model_panel, query=True, wireframeOnShaded=True
                    )
                    cmds.modelEditor(
                        model_panel, edit=True, wireframeOnShaded=True
                    )

            # Enable anti-aliasing for matchmove playblasts
            if hide_rig_elements:
                try:
                    original_aa = cmds.getAttr(
                        "hardwareRenderingGlobals.multiSampleEnable"
                    )
                    cmds.setAttr(
                        "hardwareRenderingGlobals.multiSampleEnable", True
                    )
                except Exception:
                    pass

            # Matchmove: hide all non-polygon object types and rig elements
            # so only skin geometry and static geo are visible.
            original_rig_vis = {}
            if hide_rig_elements and model_panel:
                for flag in ("joints", "nurbsCurves", "locators",
                             "handles", "ikHandles", "deformers",
                             "dynamics", "manipulators",
                             "nurbsSurfaces", "subdivSurfaces",
                             "planes", "lights", "cameras",
                             "controlVertices", "hulls",
                             "fluids", "hairSystems", "follicles",
                             "nCloths", "nParticles", "nRigids",
                             "strokes", "motionTrails",
                             "dimensions", "pivots", "grid"):
                    try:
                        original_rig_vis[flag] = cmds.modelEditor(
                            model_panel, query=True, **{flag: True})
                        cmds.modelEditor(
                            model_panel, edit=True, **{flag: False})
                    except Exception:
                        pass
                # Ensure polymeshes are visible
                try:
                    original_rig_vis["polymeshes"] = cmds.modelEditor(
                        model_panel, query=True, polymeshes=True)
                    cmds.modelEditor(
                        model_panel, edit=True, polymeshes=True)
                except Exception:
                    pass

            # Enable backface culling (Full) on all meshes for cleaner QC
            all_meshes = cmds.ls(type="mesh", long=True) or []
            original_culling = {}
            for mesh in all_meshes:
                try:
                    original_culling[mesh] = cmds.getAttr(
                        mesh + ".backfaceCulling"
                    )
                    cmds.setAttr(mesh + ".backfaceCulling", 3)
                except Exception:
                    pass

            try:
                # Strip .mov — playblast appends extension automatically
                path_no_ext = file_path
                if path_no_ext.lower().endswith(".mov"):
                    path_no_ext = path_no_ext[:-4]

                cmds.playblast(
                    filename=path_no_ext,
                    format=pb_format,
                    compression="H.264",
                    startTime=start_frame,
                    endTime=end_frame,
                    forceOverwrite=True,
                    sequenceTime=False,
                    clearCache=True,
                    viewer=False,
                    showOrnaments=True,
                    framePadding=4,
                    percent=100,
                    quality=70,
                    widthHeight=[1920, 1080],
                )
                self.log("[Playblast] Exported: " + file_path)
                return True
            finally:
                # Restore original backface culling values
                for mesh, val in original_culling.items():
                    try:
                        if cmds.objExists(mesh):
                            cmds.setAttr(mesh + ".backfaceCulling", val)
                    except Exception:
                        pass
                # Restore viewport object type visibility
                for flag, val in original_rig_vis.items():
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True, **{flag: val})
                    except Exception:
                        pass
                # Restore anti-aliasing
                if original_aa is not None:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals.multiSampleEnable",
                            original_aa)
                    except Exception:
                        pass
                # Restore wireframe on shaded
                if original_wos is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            wireframeOnShaded=original_wos)
                    except Exception:
                        pass
                # Restore original display appearance
                if original_display and original_display != target_display:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        displayAppearance=original_display,
                    )
                # Restore original camera in panel
                if original_cam and model_panel:
                    cmds.lookThru(model_panel, original_cam)
        except Exception as e:
            self.log("[Playblast] FAILED: " + str(e))
            return False

    # --- JSX Helper Methods ---

    @staticmethod
    def _get_fps():
        """Map Maya's current time unit to FPS float."""
        unit = cmds.currentUnit(query=True, time=True)
        fps_map = {
            "game": 15.0,
            "film": 24.0,
            "pal": 25.0,
            "ntsc": 30.0,
            "show": 48.0,
            "palf": 50.0,
            "ntscf": 60.0,
            "23.976fps": 23.976,
            "29.97fps": 29.97,
            "29.97df": 29.97,
            "47.952fps": 47.952,
            "59.94fps": 59.94,
            "44100fps": 44100.0,
            "48000fps": 48000.0,
        }
        return fps_map.get(unit, 24.0)

    @staticmethod
    def _sanitize_jsx_var(name):
        """Clean a name for use as a JavaScript variable name."""
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if sanitized and sanitized[0].isdigit():
            sanitized = "obj_" + sanitized
        return sanitized or "unnamed"

    @staticmethod
    def _escape_jsx_string(name):
        """Escape a name for use in a JavaScript string literal."""
        return name.replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def _jsx_header(scene_name):
        """Generate JSX file header lines."""
        lines = []
        lines.append("// Auto-generated JSX from Maya Multi-Export v{}".format(
            TOOL_VERSION))
        lines.append("// Scene: {}".format(scene_name))
        lines.append("// Coordinate system: Maya Y-up converted to AE")
        lines.append("")
        lines.append("app.activate();")
        lines.append("")
        return lines

    @staticmethod
    def _jsx_helpers():
        """Generate JSX helper functions."""
        lines = []
        lines.append("function findComp(nm) {")
        lines.append("    var i, n, prjitm;")
        lines.append("")
        lines.append("    prjitm = app.project.items;")
        lines.append("    n = prjitm.length;")
        lines.append("    for (i = 1; i <= n; i++) {")
        lines.append("        if (prjitm[i].name == nm)")
        lines.append("            return prjitm[i];")
        lines.append("    }")
        lines.append("    return null;")
        lines.append("}")
        lines.append("")
        lines.append("function firstComp() {")
        lines.append("    var i, n, prjitm;")
        lines.append("")
        lines.append("    if (app.project.activeItem.typeName == \"Composition\")")
        lines.append("        return app.project.activeItem;")
        lines.append("")
        lines.append("    prjitm = app.project.items;")
        lines.append("    n = prjitm.length;")
        lines.append("    for (i = 1; i <= n; i++) {")
        lines.append("        if (prjitm[i].typeName == \"Composition\")")
        lines.append("            return prjitm[i];")
        lines.append("    }")
        lines.append("    return null;")
        lines.append("}")
        lines.append("")
        lines.append("function deselectAll(items) {")
        lines.append("    var i, itm;")
        lines.append("")
        lines.append("    for (i = 1; i <= items.length; i++) {")
        lines.append("        itm = items[i];")
        lines.append("        if (itm instanceof FolderItem)")
        lines.append("            deselectAll(itm.items);")
        lines.append("        itm.selected = false;")
        lines.append("    };")
        lines.append("}")
        lines.append("")
        return lines

    @staticmethod
    def _jsx_footer():
        """Generate JSX file footer lines."""
        lines = []
        lines.append("// Open comp in viewer")
        lines.append("comp.selected = true;")
        lines.append("deselectAll(app.project.items);")
        lines.append("comp.selected = true;")
        lines.append("comp.openInViewer();")
        lines.append("")
        lines.append("app.endUndoGroup();")
        lines.append("alert('Scene import complete!');")
        lines.append("")
        lines.append("} // End SceneImportFunction")
        lines.append("")
        lines.append("SceneImportFunction();")
        return lines

    # --- JSX Coordinate Conversion ---

    @staticmethod
    def _compute_ae_scale(camera):
        """Compute the Maya-to-AE-pixel scale.

        SynthEyes uses rescale = 10, calibrated for its internal inch-based
        unit system. We convert from whatever Maya's linear unit is to
        match that convention.
        """
        unit = cmds.currentUnit(query=True, linear=True)
        cm_per_unit = {
            'mm': 0.1, 'cm': 1.0, 'in': 2.54,
            'ft': 30.48, 'yd': 91.44, 'm': 100.0,
        }
        cmu = cm_per_unit.get(unit, 1.0)
        return 10.0 * cmu / 2.54

    @staticmethod
    def _get_image_plane_path(camera):
        """Return the file path from the camera's image plane, or None.

        Silently returns None if there is no image plane, no file path,
        or any error occurs.
        """
        try:
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            if not cam_shapes:
                return None
            img_planes = cmds.listConnections(
                cam_shapes[0] + ".imagePlane", type="imagePlane") or []
            if not img_planes:
                return None
            path = cmds.getAttr(img_planes[0] + ".imageName")
            if path and path.strip():
                return path.strip()
            return None
        except Exception:
            return None

    @staticmethod
    def _get_image_plane_transforms(camera):
        """Return transform nodes for image planes connected to *camera*.

        Returns an empty list on failure or if no image planes exist.
        """
        try:
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            if not cam_shapes:
                return []
            img_planes = cmds.listConnections(
                cam_shapes[0] + ".imagePlane", type="imagePlane") or []
            transforms = []
            for ip in img_planes:
                parents = cmds.listRelatives(ip, parent=True) or []
                if parents:
                    transforms.append(parents[0])
            return transforms
        except Exception:
            return []

    @staticmethod
    def _world_matrix_to_ae(node, ae_scale, comp_cx, comp_cy):
        """Convert a Maya node's world-space transform to AE position + rotation.

        Position comes from the world matrix (correct absolute placement).
        Rotation comes from the *local* (object-space) matrix so that any
        parent-group orientation (e.g. a SynthEyes tracking group that
        converts Z-up to Y-up) is excluded — matching the behaviour of
        direct SynthEyes-to-AE exports.
        World-space scale is also returned (from the world matrix) so
        callers can account for parent scale.

        Returns:
            tuple: ((x, y, z), (rx_deg, ry_deg, rz_deg), (sx, sy, sz))
        """
        m = cmds.xform(node, query=True, worldSpace=True, matrix=True)

        # Position from world matrix translation (row 3, Maya row-major)
        tx = m[12]
        ty = m[13]
        tz = m[14]
        x_ae = tx * ae_scale + comp_cx
        y_ae = -ty * ae_scale + comp_cy
        z_ae = -tz * ae_scale

        # World-space scale from world matrix column magnitudes
        sx = math.sqrt(m[0] ** 2 + m[1] ** 2 + m[2] ** 2)
        sy = math.sqrt(m[4] ** 2 + m[5] ** 2 + m[6] ** 2)
        sz = math.sqrt(m[8] ** 2 + m[9] ** 2 + m[10] ** 2)

        # --- Rotation from LOCAL matrix (excludes parent group rotation) ---
        ml = cmds.xform(node, query=True, objectSpace=True, matrix=True)

        lsx = math.sqrt(ml[0] ** 2 + ml[1] ** 2 + ml[2] ** 2)
        lsy = math.sqrt(ml[4] ** 2 + ml[5] ** 2 + ml[6] ** 2)
        lsz = math.sqrt(ml[8] ** 2 + ml[9] ** 2 + ml[10] ** 2)
        if lsx < 1e-9:
            lsx = 1.0
        if lsy < 1e-9:
            lsy = 1.0
        if lsz < 1e-9:
            lsz = 1.0

        # Normalized local rotation matrix rows
        r00 = ml[0] / lsx;  r01 = ml[1] / lsx;  r02 = ml[2] / lsx
        r10 = ml[4] / lsy;  r11 = ml[5] / lsy;  r12 = ml[6] / lsy
        r20 = ml[8] / lsz;  r21 = ml[9] / lsz;  r22 = ml[10] / lsz

        # Apply coordinate transform T * R * T  (T = diag(1, -1, -1))
        # TRT_row = [[r00, -r01, -r02], [-r10, r11, r12], [-r20, r21, r22]]
        # R_ae_col = transpose(TRT_row):
        #   [[r00, -r10, -r20], [-r01, r11, r21], [-r02, r12, r22]]
        #
        # AE applies rotation as Rx * Ry * Rz (intrinsic XYZ).
        # Decompose R_ae_col as Rx(a)*Ry(b)*Rz(g):
        #   R[0][2] = sin(b)  = -r20  -> b = asin(-r20)
        #   R[1][2] = -sa*cb  =  r21  -> a = atan2(-r21, r22)
        #   R[0][1] = -cb*sg  = -r10  -> g = atan2( r10, r00)
        ry_ae = math.asin(max(-1.0, min(1.0, -r20)))
        cos_ry = math.cos(ry_ae)
        if abs(cos_ry) > 1e-6:
            rx_ae = math.atan2(-r21, r22)
            rz_ae = math.atan2(r10, r00)
        else:
            rx_ae = 0.0
            rz_ae = math.atan2(-r01, r11)

        rx_deg = math.degrees(rx_ae)
        ry_deg = math.degrees(ry_ae)
        rz_deg = math.degrees(rz_ae)

        return (x_ae, y_ae, z_ae), (rx_deg, ry_deg, rz_deg), (sx, sy, sz)

    # --- JSX Camera ---

    def _jsx_camera(self, camera, start_frame, end_frame, fps,
                    comp_width, comp_height, ae_scale):
        """Generate JSX lines for a camera with per-frame keyframes."""
        jsx = []
        shapes = cmds.listRelatives(camera, shapes=True, type="camera") or []
        if not shapes:
            self.log("[JSX] '{}' has no camera shape.".format(camera))
            return jsx
        cam_shape = shapes[0]

        focal_length = cmds.getAttr(cam_shape + ".focalLength")
        h_aperture_inches = cmds.getAttr(cam_shape + ".horizontalFilmAperture")
        h_aperture_mm = h_aperture_inches * 25.4
        ae_zoom = focal_length * comp_width / h_aperture_mm

        layer_var = "camera_{}".format(self._sanitize_jsx_var(camera))
        layer_name = self._escape_jsx_string(camera)

        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        jsx.append("var {var} = comp.layers.addCamera('{name}', [0, 0]);".format(
            var=layer_var, name=layer_name))
        jsx.append("{}.autoOrient = AutoOrientType.NO_AUTO_ORIENT;".format(layer_var))
        jsx.append("")
        jsx.append("var timesArray = new Array();")
        jsx.append("var posArray = new Array();")
        jsx.append("var rotXArray = new Array();")
        jsx.append("var rotYArray = new Array();")
        jsx.append("var rotZArray = new Array();")

        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame)
            pos, rot, _ = self._world_matrix_to_ae(
                camera, ae_scale, comp_cx, comp_cy
            )

            time_sec = (frame - start_frame + 1) / fps

            jsx.append("timesArray.push({:.10f});".format(time_sec))
            jsx.append("posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                pos[0], pos[1], pos[2]))
            jsx.append("rotXArray.push({:.10f});".format(rot[0]))
            jsx.append("rotYArray.push({:.10f});".format(rot[1]))
            jsx.append("rotZArray.push({:.10f});".format(rot[2]))

        jsx.append("")
        jsx.append("{v}.position.setValuesAtTimes(timesArray, posArray);".format(v=layer_var))
        jsx.append("{v}.rotationX.setValuesAtTimes(timesArray, rotXArray);".format(v=layer_var))
        jsx.append("{v}.rotationY.setValuesAtTimes(timesArray, rotYArray);".format(v=layer_var))
        jsx.append("{v}.rotationZ.setValuesAtTimes(timesArray, rotZArray);".format(v=layer_var))
        jsx.append("{v}.zoom.setValue({z:.10f});".format(v=layer_var, z=ae_zoom))
        jsx.append("")
        return jsx

    # --- JSX Source Footage ---

    @staticmethod
    def _jsx_footage(image_path, fps, duration, comp_width, comp_height):
        """Generate JSX lines to import source footage as background layer.

        The footage is imported as a sequence and added to the comp.
        If the file doesn't exist on the AE machine, a placeholder is
        created instead.  The layer is moved to the bottom of the stack.
        """
        jsx = []
        # Normalise path separators for JSX (forward slashes)
        jsx_path = image_path.replace("\\", "/")

        jsx.append("// Source footage")
        jsx.append("var footageFile = File('{}');".format(jsx_path))
        jsx.append("var srcFootage;")
        jsx.append("if (!footageFile.exists) {")
        jsx.append("    srcFootage = app.project.importPlaceholder("
                   "'SourcePH', {w}, {h}, {fps}, {dur});".format(
                       w=comp_width, h=comp_height, fps=fps, dur=duration))
        jsx.append("} else {")
        jsx.append("    var footageOpts = new ImportOptions();")
        jsx.append("    footageOpts.file = footageFile;")
        jsx.append("    footageOpts.sequence = true;")
        jsx.append("    footageOpts.importAs = ImportAsType.FOOTAGE;")
        jsx.append("    srcFootage = app.project.importFile(footageOpts);")
        jsx.append("};")
        jsx.append("srcFootage.pixelAspect = 1;")
        jsx.append("srcFootage.mainSource.conformFrameRate = {};".format(fps))
        jsx.append("var bkgLayer = comp.layers.add(srcFootage, {});".format(
            duration))
        jsx.append("srcFootage.selected = false;")
        jsx.append("bkgLayer.startTime = {};".format(1.0 / fps))
        jsx.append("bkgLayer.moveToEnd();")
        jsx.append("")
        return jsx

    # --- JSX Solid from Plane ---

    def _jsx_solid_from_plane(self, geo_child, start_frame, end_frame,
                              fps, comp_width, comp_height, ae_scale):
        """Generate JSX that creates an AE solid to represent a Maya plane.

        A simple quad in Maya becomes a 3-D solid in AE (matching the
        SynthEyes direct-export behaviour).  The solid is created at comp
        dimensions, rotated rx=-90 to lie on the ground plane, and scaled
        to match the Maya plane's world-space extent.
        """
        jsx = []
        layer_var = "solid_{}".format(self._sanitize_jsx_var(geo_child))
        layer_name = self._escape_jsx_string(geo_child)
        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        # Plane world-space bounding box → dimensions
        bbox = cmds.exactWorldBoundingBox(geo_child)
        plane_w = abs(bbox[3] - bbox[0])  # X extent
        plane_d = abs(bbox[5] - bbox[2])  # Z extent

        # Solid scale: map comp-sized solid to Maya-plane AE dimensions
        ae_w = plane_w * ae_scale
        ae_d = plane_d * ae_scale
        scale_x = ae_w / comp_width * 100.0
        scale_y = ae_d / comp_height * 100.0
        scale_z = 100.0

        jsx.append(
            "var {v} = comp.layers.addSolid("
            "[0.5, 0.5, 0.5], '{nm}', {w}, {h}, 1.0, comp.duration);".format(
                v=layer_var, nm=layer_name, w=comp_width, h=comp_height))
        jsx.append("{v}.threeDLayer = true;".format(v=layer_var))
        jsx.append("")

        pos, rot, _ = self._world_matrix_to_ae(
            geo_child, ae_scale, comp_cx, comp_cy
        )
        # Solid starts in XY; rx=-90 puts it on the ground (XZ).
        # Compose with any local rotation the plane may have.
        rx_final = rot[0] - 90.0

        jsx.append("{v}.position.setValue([{x:.10f}, {y:.10f}, {z:.10f}]);".format(
            v=layer_var, x=pos[0], y=pos[1], z=pos[2]))
        jsx.append("{v}.rotationX.setValue({:.10f});".format(rx_final, v=layer_var))
        jsx.append("{v}.rotationY.setValue({:.10f});".format(rot[1], v=layer_var))
        jsx.append("{v}.rotationZ.setValue({:.10f});".format(rot[2], v=layer_var))
        jsx.append("{v}.scale.setValue([{:.10f}, {:.10f}, {:.10f}]);".format(
            scale_x, scale_y, scale_z, v=layer_var))
        jsx.append("")
        return jsx

    # --- JSX Mesh from Geo (OBJ Import) ---

    def _jsx_mesh_from_geo(self, geo_child, obj_filename, start_frame,
                           end_frame, fps, comp_width, comp_height, ae_scale):
        """Generate JSX lines that import an OBJ file into the AE comp.

        Uses ImportOptions + importFile() + layers.add() so the actual
        3-D geometry is visible in After Effects, rather than a bare null.
        """
        jsx = []
        layer_var = "mesh_{}".format(self._sanitize_jsx_var(geo_child))
        footage_var = "objFootage_{}".format(
            self._sanitize_jsx_var(geo_child))
        layer_name = self._escape_jsx_string(geo_child)
        obj_fn_escaped = self._escape_jsx_string(obj_filename)

        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        # AE maps 1 OBJ unit = 512 pixels at 100 % scale.
        scale_factor = ae_scale * 100.0 / 512.0

        # Import the OBJ file from the same directory as the JSX script.
        jsx.append("var importOptions = new ImportOptions();")
        jsx.append(
            "importOptions.file = File("
            "new File($.fileName).parent.fsName + '/{fn}');".format(
                fn=obj_fn_escaped))
        jsx.append(
            "var {fv} = app.project.importFile(importOptions);".format(
                fv=footage_var))
        jsx.append("{fv}.selected = false;".format(fv=footage_var))
        jsx.append("app.beginSuppressDialogs();")
        jsx.append(
            "var {lv} = comp.layers.add({fv}, comp.duration);".format(
                lv=layer_var, fv=footage_var))
        jsx.append("{lv}.name = '{nm}';".format(
            lv=layer_var, nm=layer_name))
        jsx.append("app.endSuppressDialogs(true);")
        jsx.append("")

        is_animated = bool(
            cmds.listConnections(geo_child, type="animCurve")
        )

        if is_animated:
            jsx.append("var timesArray = new Array();")
            jsx.append("var posArray = new Array();")
            jsx.append("var rotXArray = new Array();")
            jsx.append("var rotYArray = new Array();")
            jsx.append("var rotZArray = new Array();")
            jsx.append("var scaleArray = new Array();")

            for frame in range(int(start_frame), int(end_frame) + 1):
                cmds.currentTime(frame)
                pos, rot, ws = self._world_matrix_to_ae(
                    geo_child, ae_scale, comp_cx, comp_cy
                )
                sx = ws[0] * scale_factor
                sy = ws[1] * scale_factor
                sz = ws[2] * scale_factor

                time_sec = (frame - start_frame + 1) / fps

                jsx.append("timesArray.push({:.10f});".format(time_sec))
                jsx.append("posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                    pos[0], pos[1], pos[2]))
                jsx.append("rotXArray.push({:.10f});".format(rot[0]))
                jsx.append("rotYArray.push({:.10f});".format(rot[1]))
                jsx.append("rotZArray.push({:.10f});".format(rot[2]))
                jsx.append("scaleArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                    sx, sy, sz))

            jsx.append("")
            jsx.append("{v}.position.setValuesAtTimes(timesArray, posArray);".format(v=layer_var))
            jsx.append("{v}.rotationX.setValuesAtTimes(timesArray, rotXArray);".format(v=layer_var))
            jsx.append("{v}.rotationY.setValuesAtTimes(timesArray, rotYArray);".format(v=layer_var))
            jsx.append("{v}.rotationZ.setValuesAtTimes(timesArray, rotZArray);".format(v=layer_var))
            jsx.append("{v}.scale.setValuesAtTimes(timesArray, scaleArray);".format(v=layer_var))
        else:
            pos, rot, ws = self._world_matrix_to_ae(
                geo_child, ae_scale, comp_cx, comp_cy
            )
            sx = ws[0] * scale_factor
            sy = ws[1] * scale_factor
            sz = ws[2] * scale_factor

            jsx.append("{v}.position.setValue([{:.10f}, {:.10f}, {:.10f}]);".format(
                pos[0], pos[1], pos[2], v=layer_var))
            jsx.append("{v}.rotationX.setValue({:.10f});".format(rot[0], v=layer_var))
            jsx.append("{v}.rotationY.setValue({:.10f});".format(rot[1], v=layer_var))
            jsx.append("{v}.rotationZ.setValue({:.10f});".format(rot[2], v=layer_var))
            jsx.append("{v}.scale.setValue([{:.10f}, {:.10f}, {:.10f}]);".format(
                sx, sy, sz, v=layer_var))

        jsx.append("")
        return jsx

    def _jsx_null_from_locator(self, locator_node, start_frame, end_frame,
                               fps, comp_width, comp_height, ae_scale):
        """Generate JSX for a Maya locator as a position-only 3D null in AE.

        Used for SynthEyes tracking markers — no OBJ, no rotation/scale.
        """
        jsx = []
        layer_var = "loc_{}".format(self._sanitize_jsx_var(locator_node))
        layer_name = self._escape_jsx_string(locator_node)
        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        jsx.append("var {var} = comp.layers.addNull();".format(var=layer_var))
        jsx.append("{var}.name = '{name}';".format(
            var=layer_var, name=layer_name))
        jsx.append("{var}.threeDLayer = true;".format(var=layer_var))
        jsx.append(
            "{var}.property('Anchor Point')"
            ".setValue([0, 0, 0]);".format(var=layer_var)
        )
        jsx.append("")

        is_animated = bool(
            cmds.listConnections(locator_node, type="animCurve")
        )

        if is_animated:
            jsx.append("var timesArray = new Array();")
            jsx.append("var posArray = new Array();")

            for frame in range(int(start_frame), int(end_frame) + 1):
                cmds.currentTime(frame)
                pos, _, _ = self._world_matrix_to_ae(
                    locator_node, ae_scale, comp_cx, comp_cy
                )
                time_sec = (frame - start_frame + 1) / fps

                jsx.append("timesArray.push({:.10f});".format(time_sec))
                jsx.append(
                    "posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                        pos[0], pos[1], pos[2]
                    )
                )

            jsx.append("")
            jsx.append(
                "{v}.position"
                ".setValuesAtTimes(timesArray, posArray);".format(
                    v=layer_var)
            )
        else:
            pos, _, _ = self._world_matrix_to_ae(
                locator_node, ae_scale, comp_cx, comp_cy
            )
            jsx.append(
                "{v}.position"
                ".setValue([{x:.10f}, {y:.10f}, {z:.10f}]);".format(
                    v=layer_var, x=pos[0], y=pos[1], z=pos[2])
            )
        jsx.append("")
        return jsx

    # --- JSX Orchestrator ---

    def export_jsx(self, jsx_path, obj_paths, camera, geo_root,
                   start_frame, end_frame):
        """Export After Effects JSX + OBJ files.

        Args:
            jsx_path: Output .jsx file path.
            obj_paths: dict of {geo_child_name: obj_file_path}.
            camera: Maya camera transform (or None).
            geo_root: Maya geo root transform (or None).
            start_frame: First frame.
            end_frame: Last frame.

        Returns:
            bool: True on success.
        """
        try:
            fps = self._get_fps()
            comp_width = cmds.getAttr("defaultResolution.width")
            comp_height = cmds.getAttr("defaultResolution.height")
            duration = (end_frame - start_frame + 1) / fps
            ae_scale = self._compute_ae_scale(camera) if camera else 1.0

            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            scene_base = VersionParser.get_scene_base_name(scene_short)

            jsx_lines = []

            # Header
            jsx_lines.extend(self._jsx_header(scene_base))

            # Helpers
            jsx_lines.extend(self._jsx_helpers())

            # Main function
            jsx_lines.append("function SceneImportFunction() {")
            jsx_lines.append("")
            jsx_lines.append("app.exitAfterLaunchAndEval = false;")
            jsx_lines.append("")
            jsx_lines.append("app.beginUndoGroup('Scene Import');")
            jsx_lines.append("")

            # Create composition
            jsx_lines.append(
                "var comp = app.project.items.addComp('{name}', {w}, {h}, 1.0, {dur}, {fps});".format(
                    name=scene_base, w=comp_width, h=comp_height,
                    dur=duration, fps=fps
                )
            )
            jsx_lines.append("comp.displayStartFrame = 1;")
            jsx_lines.append("")

            # Camera
            if camera:
                self.log("[JSX] Processing camera: {}".format(camera))
                cam_jsx = self._jsx_camera(
                    camera, start_frame, end_frame, fps,
                    comp_width, comp_height, ae_scale
                )
                jsx_lines.extend(cam_jsx)

            # Export OBJs and generate null layers
            if geo_root:
                children = cmds.listRelatives(
                    geo_root, children=True, type="transform"
                ) or []
                if not children:
                    # geo_root itself is the only geo
                    children = [geo_root]
                # Skip camera (and its parent groups) from geo children
                if camera:
                    children = [
                        c for c in children
                        if not self._is_descendant_of(camera, c)
                    ]
                for child in children:
                    child_lower = child.lower()

                    # Skip chisels groups entirely
                    if "chisels" in child_lower:
                        self.log("[JSX] Skipping chisels group: {}".format(
                            child))
                        continue

                    # Nulls groups: each locator becomes a position-only null
                    if "nulls" in child_lower:
                        self.log(
                            "[JSX] Processing tracker nulls group: {}".format(
                                child)
                        )
                        locator_transforms = cmds.listRelatives(
                            child, children=True, type="transform"
                        ) or []
                        for loc_tfm in locator_transforms:
                            shapes = (
                                cmds.listRelatives(
                                    loc_tfm, shapes=True, type="locator"
                                ) or []
                            )
                            if not shapes:
                                continue
                            self.log(
                                "[JSX] Processing locator: {}".format(loc_tfm)
                            )
                            loc_jsx = self._jsx_null_from_locator(
                                loc_tfm, start_frame, end_frame,
                                fps, comp_width, comp_height, ae_scale
                            )
                            jsx_lines.extend(loc_jsx)
                        continue

                    # Simple planes → AE solid (no OBJ needed)
                    if self._is_simple_plane(child):
                        self.log("[JSX] Processing plane as solid: {}".format(
                            child))
                        geo_jsx = self._jsx_solid_from_plane(
                            child, start_frame, end_frame,
                            fps, comp_width, comp_height, ae_scale
                        )
                        jsx_lines.extend(geo_jsx)
                        continue

                    # Regular geo: OBJ import
                    if child not in obj_paths:
                        continue
                    obj_path = obj_paths[child]
                    obj_filename = os.path.basename(obj_path)

                    self.log("[JSX] Processing geo: {}".format(child))
                    self.export_obj(obj_path, child)

                    geo_jsx = self._jsx_mesh_from_geo(
                        child, obj_filename, start_frame, end_frame,
                        fps, comp_width, comp_height, ae_scale
                    )
                    jsx_lines.extend(geo_jsx)

            # Source footage (from camera image plane, added last = bottom layer)
            if camera:
                img_path = self._get_image_plane_path(camera)
                if img_path:
                    self.log("[JSX] Including source footage: {}".format(
                        img_path))
                    jsx_lines.extend(self._jsx_footage(
                        img_path, fps, duration, comp_width, comp_height))

            # Footer
            jsx_lines.extend(self._jsx_footer())

            # Write JSX file
            with open(jsx_path, "w") as f:
                f.write("\n".join(jsx_lines))

            self.log("[JSX] Exported: " + jsx_path)
            return True
        except Exception as e:
            self.log("[JSX] FAILED: " + str(e))
            return False


# ---------------------------------------------------------------------------
# MultiExportUI
# ---------------------------------------------------------------------------
class MultiExportUI(object):
    """Main UI window built with maya.cmds — two-tab layout."""

    def __init__(self):
        self.window = None
        self.tab_layout = None
        # Shared
        self.scene_info_text = None
        self.version_text = None
        self.export_root_field = None
        self.start_frame_field = None
        self.end_frame_field = None
        self.tpose_checkbox = None
        self.tpose_frame_field = None
        self.log_field = None
        self.progress_bar = None
        self.progress_label = None
        # Camera Track tab (ct_)
        self.ct_camera_field = None
        self.ct_geo_root_field = None
        self.ct_ma_checkbox = None
        self.ct_jsx_checkbox = None
        self.ct_fbx_checkbox = None
        self.ct_abc_checkbox = None
        self.ct_mov_checkbox = None
        # Matchmove tab (mm_)
        self.mm_camera_field = None
        self.mm_proxy_geo_field = None
        self.mm_rig_geo_pairs = []        # [{"rig_field", "geo_field", "row"}]
        self.mm_rig_geo_container = None  # columnLayout for dynamic pairs
        self.mm_btn_row = None            # +/- button row (rebuilt dynamically)
        self.mm_add_btn = None
        self.mm_minus_btn = None
        self.mm_ma_checkbox = None
        self.mm_fbx_checkbox = None
        self.mm_abc_checkbox = None
        self.mm_mov_checkbox = None

    def show(self):
        """Build and display the UI window."""
        if cmds.window(WINDOW_NAME, exists=True):
            cmds.deleteUI(WINDOW_NAME)

        self.window = cmds.window(
            WINDOW_NAME,
            title="Maya Multi-Export  v{}".format(TOOL_VERSION),
            widthHeight=(440, 660),
            sizeable=True,
        )

        cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4, columnAttach=("both", 6)
        )

        cmds.separator(height=4, style="none")

        # --- Shared: Scene Info ---
        self._build_scene_info()

        # --- Shared: Export Root ---
        self._build_export_root()

        # --- Tab Layout ---
        self.tab_layout = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        # Tab 1: Camera Track Export
        ct_tab = self._build_camera_track_tab()

        # Tab 2: Matchmove Export
        mm_tab = self._build_matchmove_tab()

        cmds.tabLayout(
            self.tab_layout,
            edit=True,
            tabLabel=((ct_tab, "Camera Track Export"), (mm_tab, "Matchmove Export")),
        )
        cmds.setParent("..")

        # --- Shared: Frame Range ---
        self._build_frame_range()

        # --- Export Button ---
        cmds.separator(height=8, style="none")
        cmds.button(
            label="E X P O R T",
            height=40,
            backgroundColor=(0.2, 0.62, 0.35),
            command=partial(self._on_export),
        )
        cmds.separator(height=4, style="none")

        # --- Progress Bar ---
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(380, 50),
            adjustableColumn=1,
        )
        self.progress_bar = cmds.progressBar(
            maxValue=100, width=380, height=20, visible=False
        )
        self.progress_label = cmds.text(
            label="", align="right", font="smallPlainLabelFont",
            visible=False,
        )
        cmds.setParent("..")

        # --- Shared: Log ---
        self._build_log()

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

    # --- UI Builders ---

    def _build_scene_info(self):
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

    def _build_export_root(self):
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

    def _build_camera_track_tab(self):
        """Build Tab 1: Camera Track Export."""
        tab_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # Role Assignment
        cmds.frameLayout(
            label="Role Assignment",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self.ct_camera_field = cmds.textFieldButtonGrp(
            label="Camera:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.ct_camera_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "ct", "camera"),
        )

        self.ct_geo_root_field = cmds.textFieldButtonGrp(
            label="Geo Root:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.ct_geo_root_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "ct", "geo"),
        )

        cmds.setParent("..")
        cmds.setParent("..")

        # Export Formats
        cmds.frameLayout(
            label="Export Formats",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.ct_ma_checkbox = cmds.checkBox(
            label="  Maya ASCII (.ma)", value=True
        )
        self.ct_jsx_checkbox = cmds.checkBox(
            label="  After Effects (.jsx + .obj)", value=True
        )
        self.ct_fbx_checkbox = cmds.checkBox(
            label="  FBX (.fbx)", value=True
        )
        self.ct_abc_checkbox = cmds.checkBox(
            label="  Alembic (.abc)", value=True
        )
        self.ct_mov_checkbox = cmds.checkBox(
            label="  Playblast QC (.mov)", value=True
        )
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.setParent("..")
        return tab_col

    def _build_matchmove_tab(self):
        """Build Tab 2: Matchmove Export."""
        tab_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # Role Assignment
        cmds.frameLayout(
            label="Role Assignment",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # --- Scene-level roles ---
        self.mm_camera_field = cmds.textFieldButtonGrp(
            label="Camera:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.mm_camera_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "mm", "camera"),
        )

        self.mm_proxy_geo_field = cmds.textFieldButtonGrp(
            label="Static Geo:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            self.mm_proxy_geo_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "mm", "proxy"),
        )

        # --- Separator ---
        cmds.separator(style="in", height=12)

        # --- Dynamic rig/geo pairs + buttons (all inside container) ---
        self.mm_rig_geo_pairs = []
        self.mm_btn_row = None
        self.mm_rig_geo_container = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4
        )
        cmds.setParent("..")  # out of container

        # Add first pair and buttons
        self._add_rig_geo_pair()

        cmds.setParent("..")  # out of inner columnLayout
        cmds.setParent("..")  # out of frameLayout "Role Assignment"

        # Export Formats
        cmds.frameLayout(
            label="Export Formats",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.mm_ma_checkbox = cmds.checkBox(
            label="  Maya ASCII (.ma)", value=True
        )
        self.mm_fbx_checkbox = cmds.checkBox(
            label="  FBX (.fbx)", value=True
        )
        self.mm_abc_checkbox = cmds.checkBox(
            label="  Alembic (.abc)", value=True
        )
        self.mm_mov_checkbox = cmds.checkBox(
            label="  Playblast QC (.mov)", value=True
        )
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.setParent("..")
        return tab_col

    def _build_frame_range(self):
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
        cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(120, 70, 1),
            columnAlign3=("left", "left", "left"),
        )
        self.tpose_checkbox = cmds.checkBox(
            label="Include T Pose",
            value=True,
            changeCommand=partial(self._on_tpose_toggled),
        )
        self.tpose_frame_field = cmds.intField(
            value=991,
            width=55,
            changeCommand=partial(self._on_tpose_frame_changed),
        )
        cmds.text(label="")
        cmds.setParent("..")
        cmds.setParent("..")
        cmds.setParent("..")

    def _build_log(self):
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

    # --- Tab Helpers ---

    def _get_active_tab(self):
        """Return TAB_CAMERA_TRACK or TAB_MATCHMOVE based on selected tab."""
        idx = cmds.tabLayout(self.tab_layout, query=True, selectTabIndex=True)
        if idx == 1:
            return TAB_CAMERA_TRACK
        return TAB_MATCHMOVE

    # --- Callbacks ---

    def _browse_export_root(self, *args):
        result = cmds.fileDialog2(
            fileMode=3, caption="Select Export Root Directory"
        )
        if result:
            cmds.textFieldButtonGrp(
                self.export_root_field, edit=True, text=result[0]
            )

    def _load_selection_into(self, target_field, role, *args):
        """Validate the current selection and load it into a field.

        Args:
            target_field: The textFieldButtonGrp widget to populate.
            role: "camera", "geo", "rig", or "proxy" — drives validation.
        """
        sel = cmds.ls(selection=True, long=False)
        if not sel:
            cmds.confirmDialog(
                title="No Selection",
                message="Nothing is selected. Please select an object first.",
                button=["OK"],
            )
            return

        obj = sel[0]

        # Validate based on role
        if role == "camera":
            shapes = cmds.listRelatives(obj, shapes=True, type="camera") or []
            if not shapes:
                if cmds.nodeType(obj) == "camera":
                    parents = cmds.listRelatives(obj, parent=True)
                    if parents:
                        obj = parents[0]
                else:
                    cmds.confirmDialog(
                        title="Invalid Selection",
                        message="'{}' is not a camera. Please select a camera.".format(obj),
                        button=["OK"],
                    )
                    return
        else:
            # geo, rig, proxy — must be a transform
            if cmds.nodeType(obj) != "transform":
                role_labels = {
                    "geo": "geo group/root",
                    "rig": "rig root",
                    "proxy": "static geo root",
                }
                cmds.confirmDialog(
                    title="Invalid Selection",
                    message="'{}' is not a transform node. Please select the {}.".format(
                        obj, role_labels.get(role, role)
                    ),
                    button=["OK"],
                )
                return

        cmds.textFieldButtonGrp(target_field, edit=True, text=obj)

    def _load_selection(self, tab_prefix, role, *args):
        """Load the current viewport selection into the appropriate field.

        Args:
            tab_prefix: "ct" for Camera Track tab, "mm" for Matchmove tab.
            role: "camera", "geo", "rig", or "proxy".
        """
        if tab_prefix == "ct":
            field_map = {
                "camera": self.ct_camera_field,
                "geo": self.ct_geo_root_field,
            }
        else:
            field_map = {
                "camera": self.mm_camera_field,
                "proxy": self.mm_proxy_geo_field,
            }

        target_field = field_map.get(role)
        if not target_field:
            return

        self._load_selection_into(target_field, role)

    def _rebuild_rig_geo_buttons(self):
        """Recreate the +/- button row at the bottom of the rig/geo container."""
        if self.mm_btn_row:
            cmds.deleteUI(self.mm_btn_row)
            self.mm_btn_row = None

        cmds.setParent(self.mm_rig_geo_container)
        self.mm_btn_row = cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(70, 30, 30),
            columnAlign3=("right", "center", "center"),
        )
        cmds.text(label="")
        self.mm_add_btn = cmds.button(
            label="+", width=26,
            command=partial(self._add_rig_geo_pair),
        )
        self.mm_minus_btn = cmds.button(
            label="-", width=26,
            visible=(len(self.mm_rig_geo_pairs) >= 2),
            command=partial(self._remove_rig_geo_pair),
        )
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")  # out of container

    def _add_rig_geo_pair(self, *args):
        """Add a new Rig Root / Geo Root pair to the matchmove tab."""
        # Remove button row so the new pair is inserted before it
        if self.mm_btn_row:
            cmds.deleteUI(self.mm_btn_row)
            self.mm_btn_row = None

        idx = len(self.mm_rig_geo_pairs) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        cmds.setParent(self.mm_rig_geo_container)
        row = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        rig_field = cmds.textFieldButtonGrp(
            label="Rig Root{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            rig_field, edit=True,
            buttonCommand=partial(self._load_selection_into, rig_field, "rig"),
        )

        geo_field = cmds.textFieldButtonGrp(
            label="Geo Root{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
        )
        cmds.textFieldButtonGrp(
            geo_field, edit=True,
            buttonCommand=partial(self._load_selection_into, geo_field, "geo"),
        )

        cmds.setParent("..")  # out of row columnLayout
        cmds.setParent("..")  # out of container

        self.mm_rig_geo_pairs.append({
            "rig_field": rig_field,
            "geo_field": geo_field,
            "row": row,
        })

        # Rebuild buttons at the bottom
        self._rebuild_rig_geo_buttons()

        # Grow window to fit new pair
        if len(self.mm_rig_geo_pairs) > 1:
            cur_h = cmds.window(self.window, query=True, height=True)
            cmds.window(self.window, edit=True, height=cur_h + 52)

    def _remove_rig_geo_pair(self, *args):
        """Remove the last Rig Root / Geo Root pair."""
        if len(self.mm_rig_geo_pairs) <= 1:
            return

        entry = self.mm_rig_geo_pairs.pop()
        cmds.deleteUI(entry["row"])

        # Rebuild buttons (updates minus visibility)
        self._rebuild_rig_geo_buttons()

        # Shrink window
        cur_h = cmds.window(self.window, query=True, height=True)
        cmds.window(self.window, edit=True, height=cur_h - 52)

    def _set_timeline_range(self, *args):
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        # If Include T Pose is checked, override start with the T-pose frame
        if cmds.checkBox(self.tpose_checkbox, query=True, value=True):
            tpose_frame = cmds.intField(
                self.tpose_frame_field, query=True, value=True
            )
            start = min(tpose_frame, start)
        cmds.intField(self.start_frame_field, edit=True, value=int(start))
        cmds.intField(self.end_frame_field, edit=True, value=int(end))

    def _on_tpose_toggled(self, checked, *args):
        """When Include T Pose is toggled, update the start frame."""
        if checked:
            tpose_frame = cmds.intField(
                self.tpose_frame_field, query=True, value=True
            )
            current_start = cmds.intField(
                self.start_frame_field, query=True, value=True
            )
            if tpose_frame < current_start:
                cmds.intField(
                    self.start_frame_field, edit=True, value=tpose_frame
                )

    def _on_tpose_frame_changed(self, value, *args):
        """When the T-pose frame number changes, update start if checked."""
        if cmds.checkBox(self.tpose_checkbox, query=True, value=True):
            current_start = cmds.intField(
                self.start_frame_field, query=True, value=True
            )
            if value < current_start:
                cmds.intField(
                    self.start_frame_field, edit=True, value=int(value)
                )

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
                    label="Version: (none detected \u2014 will default to v01)",
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
        cmds.scrollField(
            self.log_field, edit=True, insertionPosition=len(updated)
        )

    # --- Progress Bar ---

    def _reset_progress(self, total_steps):
        """Show and reset the progress bar for a new export run."""
        self._progress_total = max(total_steps, 1)
        self._progress_done = 0
        cmds.progressBar(
            self.progress_bar, edit=True, progress=0, visible=True
        )
        cmds.text(
            self.progress_label, edit=True, label="0%", visible=True
        )
        cmds.refresh(force=True)

    def _advance_progress(self):
        """Advance the progress bar by one step."""
        self._progress_done += 1
        pct = int(
            (self._progress_done / float(self._progress_total)) * 100
        )
        cmds.progressBar(
            self.progress_bar, edit=True, progress=min(pct, 100)
        )
        cmds.text(
            self.progress_label, edit=True,
            label="{}%".format(min(pct, 100))
        )
        cmds.refresh(force=True)

    def _hide_progress(self):
        """Hide the progress bar after export completes."""
        cmds.progressBar(self.progress_bar, edit=True, visible=False)
        cmds.text(self.progress_label, edit=True, visible=False)

    # --- Validation ---

    def _validate_shared(self):
        """Validate settings shared across both tabs.

        Returns:
            tuple: (errors, warnings, export_root, version_str, scene_base,
                    start_frame, end_frame)
        """
        errors = []
        warnings = []

        scene_path = cmds.file(query=True, sceneName=True)
        if not scene_path:
            errors.append("Scene has not been saved. Please save first.")

        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        if not export_root:
            errors.append("Export root directory is not set.")
        elif not os.path.isdir(export_root):
            errors.append(
                "Export root directory does not exist:\n" + export_root
            )

        start_frame = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end_frame = cmds.intField(
            self.end_frame_field, query=True, value=True
        )
        if end_frame <= start_frame:
            errors.append("End frame must be greater than start frame.")

        version_str = None
        scene_base = None
        if scene_path:
            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            version_str, _ = VersionParser.parse(scene_short)
            scene_base = VersionParser.get_scene_base_name(scene_short)
            if version_str is None:
                warnings.append(
                    "No _v## version found in filename '{}'.\n"
                    "Will default to v01.".format(scene_short)
                )

        return (errors, warnings, export_root, version_str, scene_base,
                start_frame, end_frame)

    def _validate_camera_track(self):
        """Validate Camera Track tab fields. Returns (errors, warnings)."""
        errors, warnings, export_root, version_str, scene_base, \
            start_frame, end_frame = self._validate_shared()

        do_ma = cmds.checkBox(self.ct_ma_checkbox, query=True, value=True)
        do_jsx = cmds.checkBox(self.ct_jsx_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.ct_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.ct_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.ct_mov_checkbox, query=True, value=True)
        if not (do_ma or do_jsx or do_fbx or do_abc or do_mov):
            errors.append("No export format selected.")

        camera = cmds.textFieldButtonGrp(
            self.ct_camera_field, query=True, text=True
        ).strip()
        geo_root = cmds.textFieldButtonGrp(
            self.ct_geo_root_field, query=True, text=True
        ).strip()

        if do_ma and not camera and not geo_root:
            errors.append(
                "MA export enabled but no Camera or Geo Root assigned."
            )
        if do_jsx and not camera and not geo_root:
            errors.append(
                "JSX export enabled but no Camera or Geo Root assigned."
            )
        if do_fbx and not (camera or geo_root):
            errors.append(
                "FBX export enabled but no Camera or Geo Root assigned."
            )
        if do_abc and not (camera or geo_root):
            errors.append(
                "Alembic export enabled but no Camera or Geo Root assigned."
            )

        for role_name, value in [("Camera", camera), ("Geo Root", geo_root)]:
            if value and not cmds.objExists(value):
                errors.append(
                    "{} '{}' no longer exists in the scene.".format(
                        role_name, value
                    )
                )

        return errors, warnings

    def _validate_matchmove(self):
        """Validate Matchmove tab fields. Returns (errors, warnings)."""
        errors, warnings, export_root, version_str, scene_base, \
            start_frame, end_frame = self._validate_shared()

        do_ma = cmds.checkBox(self.mm_ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.mm_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.mm_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.mm_mov_checkbox, query=True, value=True)
        if not (do_ma or do_fbx or do_abc or do_mov):
            errors.append("No export format selected.")

        camera = cmds.textFieldButtonGrp(
            self.mm_camera_field, query=True, text=True
        ).strip()
        proxy_geo = cmds.textFieldButtonGrp(
            self.mm_proxy_geo_field, query=True, text=True
        ).strip()

        # Gather rig/geo pairs
        rig_roots = []
        geo_roots = []
        for i, pair in enumerate(self.mm_rig_geo_pairs):
            r = cmds.textFieldButtonGrp(
                pair["rig_field"], query=True, text=True
            ).strip()
            g = cmds.textFieldButtonGrp(
                pair["geo_field"], query=True, text=True
            ).strip()
            if r:
                rig_roots.append(r)
            if g:
                geo_roots.append(g)
            # Validate existence
            suffix = "" if i == 0 else " {}".format(i + 1)
            if r and not cmds.objExists(r):
                errors.append(
                    "Rig Root{} '{}' no longer exists in the scene.".format(
                        suffix, r))
            if g and not cmds.objExists(g):
                errors.append(
                    "Geo Root{} '{}' no longer exists in the scene.".format(
                        suffix, g))

        if do_ma and not any(geo_roots + rig_roots + [camera]):
            errors.append(
                "MA export enabled but no roles assigned (nothing to export)."
            )
        if do_fbx and not (geo_roots or rig_roots):
            errors.append(
                "FBX export enabled but no Geo Root or Rig Root assigned."
            )
        if do_abc and not geo_roots:
            errors.append("Alembic export enabled but no Geo Root assigned.")

        for role_name, value in [
            ("Camera", camera),
            ("Static Geo", proxy_geo),
        ]:
            if value and not cmds.objExists(value):
                errors.append(
                    "{} '{}' no longer exists in the scene.".format(
                        role_name, value
                    )
                )

        return errors, warnings

    # --- Export Orchestration ---

    def _on_export(self, *args):
        """Main export callback — dispatches to active tab's export."""
        cmds.scrollField(self.log_field, edit=True, text="")

        active_tab = self._get_active_tab()
        if active_tab == TAB_CAMERA_TRACK:
            self._log("Starting Camera Track export...")
            self._export_camera_track()
        else:
            self._log("Starting Matchmove export...")
            self._export_matchmove()

    def _export_camera_track(self):
        """Export pipeline for Camera Track tab."""
        errors, warnings = self._validate_camera_track()
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

        original_sel = cmds.ls(selection=True)

        # Gather settings
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        camera = cmds.textFieldButtonGrp(
            self.ct_camera_field, query=True, text=True
        ).strip()
        geo_root = cmds.textFieldButtonGrp(
            self.ct_geo_root_field, query=True, text=True
        ).strip()
        do_ma = cmds.checkBox(self.ct_ma_checkbox, query=True, value=True)
        do_jsx = cmds.checkBox(self.ct_jsx_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.ct_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.ct_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.ct_mov_checkbox, query=True, value=True)
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

        # Resolve versioned directories (rename older version folders)
        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str
        )
        main_dir = os.path.join(
            export_root,
            "{}_track_{}".format(scene_base, version_str),
        )
        FolderManager.resolve_ae_dir(main_dir, scene_base, version_str)

        exporter = Exporter(self._log)
        results = {}
        all_paths = {}

        # Progress bar — JSX counts as 2 steps (setup + timeline scrub)
        total_formats = sum([do_ma, do_fbx, do_abc, do_mov])
        if do_jsx:
            total_formats += 2
        self._reset_progress(total_formats)

        # Rename camera to cam_main for all exports
        renamed_cam = None
        original_cam_name = camera
        try:
            if camera:
                if cmds.objExists(camera):
                    renamed_cam = cmds.rename(camera, "cam_main")
                    camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    # Previous run may have renamed without restoring
                    renamed_cam = "cam_main"
                    camera = "cam_main"
                else:
                    self._log(
                        "[WARN] Camera '{}' not found.".format(camera))
                    camera = None

            # JSX + OBJ export
            if do_jsx:
                self._log("Exporting After Effects JSX + OBJ...")
                geo_children = []
                if geo_root:
                    children = cmds.listRelatives(
                        geo_root, children=True, type="transform"
                    ) or []
                    if children:
                        geo_children = children
                    else:
                        geo_children = [geo_root]
                    # Exclude camera, chisels, and nulls from OBJ paths
                    # (nulls/locators are handled separately inside export_jsx)
                    if camera:
                        geo_children = [
                            c for c in geo_children
                            if not Exporter._is_descendant_of(camera, c)
                        ]
                    geo_children = [
                        c for c in geo_children
                        if "chisels" not in c.lower()
                        and "nulls" not in c.lower()
                    ]

                ae_paths = FolderManager.build_ae_export_paths(
                    export_root, scene_base, version_str, geo_children
                )
                FolderManager.ensure_ae_directories(ae_paths)
                all_paths["jsx"] = ae_paths["jsx"]
                self._advance_progress()  # step 1: setup complete

                results["jsx"] = exporter.export_jsx(
                    ae_paths["jsx"], ae_paths["obj"], camera, geo_root,
                    start_frame, end_frame
                )
                self._advance_progress()  # step 2: JSX scrub complete

            # MA export
            if do_ma:
                self._log("Exporting Maya ASCII...")
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str
                )
                FolderManager.ensure_directories({"ma": paths["ma"]})
                all_paths["ma"] = paths["ma"]
                geo_roots_list = [geo_root] if geo_root else []
                results["ma"] = exporter.export_ma(
                    paths["ma"], camera, geo_roots_list, [], None
                )
                self._advance_progress()

            # FBX export (camera + geo, no rig/proxy for camera track)
            if do_fbx:
                self._log("Exporting FBX...")
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str
                )
                FolderManager.ensure_directories({"fbx": paths["fbx"]})
                all_paths["fbx"] = paths["fbx"]
                geo_roots_list = [geo_root] if geo_root else []
                results["fbx"] = exporter.export_fbx(
                    paths["fbx"], camera, geo_roots_list, [], None,
                    start_frame, end_frame
                )
                self._advance_progress()

            # ABC export (camera + geo, no proxy for camera track)
            if do_abc:
                self._log("Exporting Alembic cache...")
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str
                )
                FolderManager.ensure_directories({"abc": paths["abc"]})
                all_paths["abc"] = paths["abc"]
                geo_roots_list = [geo_root] if geo_root else []
                results["abc"] = exporter.export_abc(
                    paths["abc"], camera, geo_roots_list, None,
                    start_frame, end_frame
                )
                self._advance_progress()

            # QC Playblast
            if do_mov:
                self._log("Exporting QC playblast...")
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str
                )
                FolderManager.ensure_directories({"mov": paths["mov"]})
                all_paths["mov"] = paths["mov"]
                results["mov"] = exporter.export_playblast(
                    paths["mov"], camera, start_frame, end_frame
                )
                self._advance_progress()
        finally:
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                cmds.rename(renamed_cam, original_cam_name)

        self._finish_export(results, all_paths, original_sel)

    def _export_matchmove(self):
        """Export pipeline for Matchmove tab (identical to v1.0 behavior)."""
        errors, warnings = self._validate_matchmove()
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

        original_sel = cmds.ls(selection=True)

        # Gather settings
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        camera = cmds.textFieldButtonGrp(
            self.mm_camera_field, query=True, text=True
        ).strip()
        proxy_geo = cmds.textFieldButtonGrp(
            self.mm_proxy_geo_field, query=True, text=True
        ).strip()
        rig_roots = []
        geo_roots = []
        for pair in self.mm_rig_geo_pairs:
            r = cmds.textFieldButtonGrp(
                pair["rig_field"], query=True, text=True
            ).strip()
            g = cmds.textFieldButtonGrp(
                pair["geo_field"], query=True, text=True
            ).strip()
            if r:
                rig_roots.append(r)
            if g:
                geo_roots.append(g)
        do_ma = cmds.checkBox(self.mm_ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.mm_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.mm_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.mm_mov_checkbox, query=True, value=True)
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

        # Resolve versioned directories (rename older version folders)
        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str
        )

        # Build paths and create directories
        paths = FolderManager.build_export_paths(
            export_root, scene_base, version_str
        )
        FolderManager.ensure_directories(paths)
        self._log("Folder structure created.")

        exporter = Exporter(self._log)
        results = {}

        # Progress bar
        total_formats = sum([do_ma, do_fbx, do_abc, do_mov])
        self._reset_progress(total_formats)

        # Rename camera to cam_main for all exports
        renamed_cam = None
        original_cam_name = camera
        try:
            if camera:
                if cmds.objExists(camera):
                    renamed_cam = cmds.rename(camera, "cam_main")
                    camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    renamed_cam = "cam_main"
                    camera = "cam_main"
                else:
                    self._log(
                        "[WARN] Camera '{}' not found.".format(camera))
                    camera = None

            if do_ma:
                self._log("Exporting Maya ASCII...")
                results["ma"] = exporter.export_ma(
                    paths["ma"], camera, geo_roots, rig_roots, proxy_geo
                )
                self._advance_progress()

            if do_fbx:
                self._log("Exporting FBX (baking keyframes)...")
                results["fbx"] = exporter.export_fbx(
                    paths["fbx"], camera, geo_roots, rig_roots, proxy_geo,
                    start_frame, end_frame
                )
                self._advance_progress()

            if do_abc:
                self._log("Exporting Alembic cache...")
                results["abc"] = exporter.export_abc(
                    paths["abc"], camera, geo_roots, proxy_geo,
                    start_frame, end_frame
                )
                self._advance_progress()

            if do_mov:
                self._log("Exporting QC playblast...")
                results["mov"] = exporter.export_playblast(
                    paths["mov"], camera, start_frame, end_frame,
                    hide_rig_elements=True
                )
                self._advance_progress()
        finally:
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                cmds.rename(renamed_cam, original_cam_name)

        self._finish_export(results, paths, original_sel)

    def _finish_export(self, results, paths, original_sel):
        """Log summary, restore selection, show completion dialog."""
        self._hide_progress()
        self._log("--- Export Complete ---")
        for fmt, success in results.items():
            status = "OK" if success else "FAILED"
            path = paths.get(fmt, "")
            self._log("  {}: {} -> {}".format(fmt.upper(), status, path))

        if original_sel:
            cmds.select(original_sel, replace=True)
        else:
            cmds.select(clear=True)

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
        annotation="Maya Multi-Export: Export to .ma, .fbx, .abc, .jsx",
        image1=ICON_FILENAME,
        command=(
            "import sys\n"
            "sys.modules.pop('maya_multi_export', None)\n"
            "import maya_multi_export\n"
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

    # Clear compiled .pyc cache to ensure a fresh import
    pycache_dir = os.path.join(scripts_dir, "__pycache__")
    if os.path.isdir(pycache_dir):
        for f in os.listdir(pycache_dir):
            if f.startswith(TOOL_NAME) and f.endswith(".pyc"):
                try:
                    os.remove(os.path.join(pycache_dir, f))
                except OSError:
                    pass

    # Remove stale module and re-import fresh from scripts dir
    sys.modules.pop(TOOL_NAME, None)
    mod = __import__(TOOL_NAME)

    # Create shelf button and show dialog using the freshly loaded module
    mod._create_shelf_button()

    cmds.confirmDialog(
        title="Install Complete",
        message=(
            "Maya Multi-Export v{} installed!\n\n"
            "A shelf button has been added to your current shelf.\n"
            "Click it to open the export tool."
        ).format(mod.TOOL_VERSION),
        button=["OK"],
    )


def onMayaDroppedPythonFile(*args, **kwargs):
    """Maya drag-and-drop hook — called when this file is dropped into the viewport."""
    install()
