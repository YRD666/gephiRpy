"""Core module: JVM initialization and Gephi workspace management."""

import os
import jpype
import jpype.imports

_JAR_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib", "gephi-toolkit-0.10.1-all.jar")


def start_jvm(extra_args=None, jar_path=None):
    """Start the JVM with gephi-toolkit on the classpath.

    Args:
        extra_args: List of additional JVM arguments (e.g. ["-Xmx4g"])
        jar_path: Override gephi-toolkit JAR path (default: lib/gephi-toolkit-0.10.1-all.jar)
    """
    if jpype.isJVMStarted():
        return
    jar = jar_path or _JAR_PATH
    if not os.path.exists(jar):
        raise FileNotFoundError(f"gephi-toolkit JAR not found: {jar}")
    args = [
        # Required for Java 17+ module access (gephi-toolkit internals)
        "--add-opens=java.base/java.net=ALL-UNNAMED",
        "--add-opens=java.base/java.lang=ALL-UNNAMED",
        "--add-opens=java.base/java.util=ALL-UNNAMED",
        "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
        "--add-opens=java.desktop/sun.awt=ALL-UNNAMED",
        "--add-opens=java.prefs/java.util.prefs=ALL-UNNAMED",
        "--enable-native-access=ALL-UNNAMED",
    ]
    if extra_args:
        args.extend(extra_args)
    jpype.startJVM(*args, classpath=[jar])


def stop_jvm():
    """Shutdown the JVM."""
    if jpype.isJVMStarted():
        jpype.shutdownJVM()


def get_project_controller():
    start_jvm()
    from org.gephi.project.api import ProjectController
    from org.openide.util import Lookup
    pc = Lookup.getDefault().lookup(ProjectController)
    if pc is None:
        raise RuntimeError("ProjectController service not available. Check gephi-toolkit JAR.")
    return pc


def init_workspace():
    """Initialize a new Gephi project and workspace, return the workspace."""
    pc = get_project_controller()
    pc.newProject()
    return pc.getCurrentWorkspace()


def get_graph_model(workspace=None):
    start_jvm()
    from org.gephi.graph.api import GraphController
    from org.openide.util import Lookup
    gc = Lookup.getDefault().lookup(GraphController)
    if workspace:
        return gc.getGraphModel(workspace)
    return gc.getGraphModel()


def get_appearance_model(workspace=None):
    start_jvm()
    from org.gephi.appearance.api import AppearanceController
    from org.openide.util import Lookup
    ac = Lookup.getDefault().lookup(AppearanceController)
    if workspace:
        return ac.getModel(workspace)
    return ac.getModel()


def get_attribute_model(workspace=None):
    """Get the graph model (attributes are accessed via GraphModel in gephi-toolkit 0.10.1).

    In 0.10.1, AttributeModel was removed. Use GraphModel.getNodeTable()
    and GraphModel.getEdgeTable() to access attributes.
    """
    return get_graph_model(workspace)
