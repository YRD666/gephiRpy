"""Project and workspace management: save/open .gephi files, multi-workspace."""

import os
from .core import start_jvm, get_project_controller


def new_project():
    """Create a new empty project."""
    start_jvm()
    pc = get_project_controller()
    pc.newProject()
    ws = pc.getCurrentWorkspace()
    return {
        "action": "new_project",
        "workspace": str(ws),
    }


def open_project(file_path):
    """Open a .gephi project file."""
    start_jvm()
    import java.io
    pc = get_project_controller()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Project file not found: {file_path}")

    f = java.io.File(os.path.abspath(file_path))
    pc.openProject(f)

    ws = pc.getCurrentWorkspace()
    return {
        "action": "open_project",
        "file": file_path,
        "workspace": str(ws),
    }


def save_project(file_path):
    """Save current project to a .gephi file."""
    start_jvm()
    import java.io
    pc = get_project_controller()

    out_dir = os.path.dirname(os.path.abspath(file_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    f = java.io.File(os.path.abspath(file_path))
    pc.saveProject(pc.getCurrentProject(), f)

    return {
        "action": "save_project",
        "file": file_path,
    }


def new_workspace():
    """Create a new workspace in the current project.

    Returns the workspace object (can be passed to other functions).
    """
    start_jvm()
    pc = get_project_controller()
    ws = pc.newWorkspace(pc.getCurrentProject())
    pc.openWorkspace(ws)
    return ws


def duplicate_workspace():
    """Duplicate the current workspace.

    Returns the new workspace object.
    """
    start_jvm()
    pc = get_project_controller()
    ws = pc.duplicateWorkspace(pc.getCurrentWorkspace())
    pc.openWorkspace(ws)
    return ws


def delete_workspace(workspace=None):
    """Delete a workspace (current if not specified)."""
    start_jvm()
    pc = get_project_controller()
    ws = workspace or pc.getCurrentWorkspace()
    pc.deleteWorkspace(ws)
    return {"action": "delete_workspace"}


def rename_workspace(name, workspace=None):
    """Rename the current workspace."""
    start_jvm()
    pc = get_project_controller()
    ws = workspace or pc.getCurrentWorkspace()
    pc.renameWorkspace(ws, str(name))
    return {"action": "rename_workspace", "name": name}


def list_workspaces():
    """List all workspaces in the current project."""
    start_jvm()
    pc = get_project_controller()
    project = pc.getCurrentProject()
    if project is None:
        return {"workspaces": []}

    workspaces = []
    current = pc.getCurrentWorkspace()
    for ws in project.getWorkspaces():
        workspaces.append({
            "name": str(ws),
            "is_current": ws == current,
        })
    return {"workspaces": workspaces}


def switch_workspace(index):
    """Switch to a workspace by index (0-based)."""
    start_jvm()
    pc = get_project_controller()
    project = pc.getCurrentProject()
    if project is None:
        raise ValueError("No project is currently open")
    ws_list = list(project.getWorkspaces())
    if not ws_list:
        raise ValueError("No workspaces in current project")

    if index < 0 or index >= len(ws_list):
        raise ValueError(f"Workspace index {index} out of range (0-{len(ws_list)-1})")

    pc.openWorkspace(ws_list[index])
    return {
        "action": "switch_workspace",
        "index": index,
        "workspace": str(ws_list[index]),
    }
