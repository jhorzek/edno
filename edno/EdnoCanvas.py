import tkinter as tk
import ttkbootstrap as ttk
from .EllipseNode import EllipseNode
from .PolyNode import PolyNode, PolyNode_factory
from .Arrow import Arrow
from typing import Callable


def disallow_existing_connections(
    predictors_node, dependents_node, all_nodes, arrow_type
) -> bool:
    """
    Allow all connections except for existing connections.

    Args:
        predictors_node (PolyNode): The node that is the predictor.
        dependents_node (PolyNode): The node that is the dependent.
        all_nodes (list[PolyNode]): A list of all nodes in the canvas.

    Returns:
        bool: True if connection is allowed
    """
    predictor = [nd for nd in all_nodes if nd.node_id == predictors_node][0]
    dependent = [nd for nd in all_nodes if nd.node_id == dependents_node][0]
    is_connected = [
        con
        for con in predictor.dependents_arrow_id
        if con in dependent.predictors_arrow_id
    ]
    return len(is_connected) == 0


def disallow_self_loops(
    predictors_node, dependents_node, all_nodes, arrow_type
) -> bool:
    """
    Allow all connection except for self-loops.

    Args:
        predictors_node (PolyNode): The node that is the predictor.
        dependents_node (PolyNode): The node that is the dependent.
        all_nodes (list[PolyNode]): A list of all nodes in the canvas.

    Returns:
        bool: True if connection is allowed
    """
    if arrow_type == "bidirected":
        return True
    return predictors_node != dependents_node


def disallow_self_and_existing(
    predictors_node, dependents_node, all_nodes, arrow_type
) -> bool:
    """
    Allow all connection except for self-loops and existing connections.

    Args:
        predictors_node (PolyNode): The node that is the predictor.
        dependents_node (PolyNode): The node that is the dependent.
        all_nodes (list[PolyNode]): A list of all nodes in the canvas.

    Returns:
        bool: True if connection is allowed
    """
    return disallow_existing_connections(
        predictors_node, dependents_node, all_nodes, arrow_type
    ) and disallow_self_loops(predictors_node, dependents_node, all_nodes, arrow_type)


class EdnoCanvas(tk.Canvas):
    """A custom canvas widget for interactive, directed graphs.

    This canvas provides functionality for drawing nodes, arrows, scrolling, and zooming.
    """

    def __init__(
        self,
        root: tk.Tk,
        node_classes: dict[str, Callable] = {
            "Ellipse": EllipseNode,
            "Rectangle": PolyNode_factory(4),
            "Triangle": PolyNode_factory(3),
        },
        font=("Arial", 9),
        font_color="#000000",
        node_color: dict[str, str] = {
            "default": "#ADD8E6",
            "allowed": "#90E4C1",
            "not allowed": "#ffcccb",
        },
        arrow_types={
            "Effect": "directed",
            "Covariance": "bidirected",
            "Undirected": "undirected",
        },
        arrow_color="#000000",
        arrow_color_on_hover="#90E4C1",
        arrow_width=3,
        allowed_connections: Callable = disallow_self_and_existing,
        **kwargs,
    ) -> None:
        """Initialize a new EdnoCanvas.

        Args:
            root (ttk.Window): The ttk.Window root object to which the EdnoCanvas should be added.
            node_classes (dict[str, Callable], optional): A dictionary of node classes that can be added to the canvas. Defaults to {"Ellipse": EllipseNode, "Rectangle": PolyNode_factory(4), "Triangle": PolyNode_factory(3)}. The keys specify the names of the nodes on the canvas. For example, in Structural Equation Models, latent and observed variables could be represented by ellipses and rectangles, respectively ({"Latent": EllipseNode, "Observed": PolyNode_factory(4)}). New node types can be created using the PolyNode_factory function. Alternatively, nodes can be created by inheriting from PolyNode and adapting its methods.
            font (tuple, optional). Font used on the canvas. Defaults to ("Arial", 9).
            font_color (str, optional): Color of the text. Defaults to "#000000".
            node_color (_type_, optional): Color of nodes. Expects a dict with three keys: "default", "allowed", "not allowed". A default color for nodes, a color for allowed connections, and a color for disallowed connections. Defaults to { "default": "#ADD8E6", "allowed": "#90E4C1", "not allowed": "#ffcccb", }.
            arrow_types (dict[str, str], optional): The types of arrows that can be drawn. Defaults to {"Effect": "directed", "Covariance": "bidirected", "Undirected": "undirected"}. The keys specify the names of the arrows on the canvas. The values specify the type of the arrow. The arrow type can be one of "directed", "bidirected", or "undirected".
            arrow_color (str, optional): Color of all arrows. Defaults to "#000000".
            arrow_color_on_hover (str, optional): Color of arrows when hovering over the arrow with the mouse. Defaults to "#90E4C1".
            arrow_width (int, optional): Width of the arrows. Defaults to 3.
            allowed_connections (Callable, optional): Callable  with signature (predictors_node, dependents_node, all_nodes, arrow_type) -> bool. This function will be called each time a user tries to connect two nodes. If the function returns True, the connection will be allowed, otherwise not. If the user hovers over a node, the color of the node will change to the allowed color if the connection is allowed, otherwise to the not allowed color. Defaults to disallow_self_and_existing.
            kwargs: Additional keyword arguments to pass to the tk.Canvas constructor.
        """
        super().__init__(root, kwargs)

        self.node_classes = node_classes
        self.node_color = node_color
        self.font_color = font_color
        self.arrow_types = arrow_types
        self.arrow_color = arrow_color
        self.arrow_color_on_hover = arrow_color_on_hover
        self.arrow_width = arrow_width
        self.allowed_connections = allowed_connections

        # initialize nodes
        self.nodes: list[PolyNode] = []
        self.arrows: list[Arrow] = []
        # the following variables are used to indicate if we are currently
        # in an arrow drawing mode. This ensures that we are not allowing
        # for moving objects, etc. while arrows are being drawn.
        self.drawing_arrow = False
        self.arrow_start_node = None
        self.temporary_arrow = None
        # Context Menu
        # context_menu will be used to temporarily save a single
        # context menu. This makes sure that, at any point, only one
        # menu is open
        self.context_menu = None
        self.canvas_context_menu = CanvasContextMenu(root, self, self.node_classes)

        # add scrolling
        # We want to ensure that only model elements (e.g., nodes)
        # or the canvas is moving
        self.model_elements_are_moving = False
        self.bind("<ButtonPress-1>", self.start_scroll)
        self.bind("<B1-Motion>", self.do_scroll)

        # add zoom in and zoom out
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Control-MouseWheel>", self.zoom)
        self.bind("<Button-4>", self.zoom)
        self.bind("<Button-5>", self.zoom)

        # we also track mouse movement to let temporary arrows follow the mouse
        self.bind("<Motion>", self.update_temporary_arrow)

        self.scale_factor = 1.0

        self.base_font = font
        self.font = font

    def start_scroll(self, event: tk.Event) -> None:
        """Initialize scrolling in the canvas.

        Args:
            event (tk.Event): The tkinter event that tells us the coordinates we are moving towards.
        """

        # when starting to scroll, close menus
        self.canvas_context_menu.release_right_click_menu(event)
        if not self.model_elements_are_moving:
            self.scan_mark(event.x, event.y)

    def do_scroll(self, event: tk.Event) -> None:
        """
        Perform scrolling in the canvas.

        Args:
            event (tk.Event): The tkinter event that tells us the coordinates we are moving towards.
        """
        if not self.model_elements_are_moving:
            self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event: tk.Event) -> None:
        """
        Zoom in and out of the canvas.

        Args:
            event (tk.Event): The tkinter event that tells us if we are scrolling in or out.
        """
        if event.num == 4 or event.delta > 0:
            factor = 1.1
        elif event.num == 5 or event.delta < 0:
            factor = 0.9
        else:
            return

        self.scale_factor *= factor

        self.scale("all", event.x, event.y, factor, factor)
        self.configure(scrollregion=self.bbox("all"))
        # find all text elements and rescale
        text_fields = self.find_withtag("text_field")
        self.font = (
            self.base_font[0],
            max(2, int(self.base_font[1] * self.scale_factor)),
        )
        for text_field in text_fields:
            self.itemconfigure(text_field, font=self.font)

        # The boxes around the text field often do not update correctly, so
        # we need to update them manually
        for node in self.nodes:
            node.update_shape()
        # the arrow heads also need to be updated
        for arrow in self.arrows:
            arrow.update_box()

    def update_temporary_arrow(self, event: tk.Event) -> None:
        """Makes the temporary arrow follow the cursor.

        Args:
            event (tk.Event): Tkinter event that tells us the current position of the cursor.
        """
        if self.drawing_arrow:
            mouse_position = [self.canvasx(event.x), self.canvasy(event.y)]
            self.coords(
                self.temporary_arrow,
                self.coords(self.temporary_arrow)[0],
                self.coords(self.temporary_arrow)[1],
                mouse_position[0],
                mouse_position[1],
            )

    def get_connections(self) -> list[dict]:
        """Get all connections between nodes.

        Returns:
            list[dict]: A list of dictionaries representing the connections between nodes.
        """

        connections = []
        for arrow in self.arrows:
            connections.append(arrow.save())
        return connections

    def get_node_connections(self) -> dict:
        """
        Get all connections between nodes.

        Returns:
            dict: A dictionary representing the connections between nodes.
        """
        node_connections = {}
        for node in self.nodes:
            # getting the labels of the predictors and dependents is a bit complicated, as each node
            # only knows about the arrows, but not the predicting / predicted nodes themselves. So,
            # we need to first find the arrows and then get the labels of the nodes these arrows come from / go to.
            type = node.type
            incoming_arrows_id = [arrow for arrow in node.predictors_arrow_id]
            outgoing_arrows_id = [arrow for arrow in node.dependents_arrow_id]
            # given the ids, we can find the actual arrows
            dependents_ids = [
                arrow.dependents_id
                for arrow in self.arrows
                if arrow.id in outgoing_arrows_id
            ]
            predictors_ids = [
                arrow.predictors_id
                for arrow in self.arrows
                if arrow.id in incoming_arrows_id
            ]

            # finally, arrows know about the nodes the come from and the nodes they point to,
            # so we can get the labels of the nodes.
            dependents = [
                nd.get_label() for nd in self.nodes if nd.node_id in dependents_ids
            ]
            predictors = [
                nd.get_label() for nd in self.nodes if nd.node_id in predictors_ids
            ]
            node_connections[node.get_label()] = {
                "type": type,
                "dependents": dependents,
                "predictors": predictors,
            }
        return node_connections

    def get_node_with_id(self, node_id: int) -> PolyNode:
        """
        Get the node with the specified id.

        Args:
            node_id (int): The id of the node to get.

        Returns:
            PolyNode: The node with the specified id.
        """
        return [node for node in self.nodes if node.node_id == node_id][0]

    def get_node_with_label(self, label: str) -> PolyNode:
        """
        Get the node with the specified label.

        Args:
            label (str): The label of the node to get.

        Returns:
            PolyNode: The node with the specified label.
        """
        return [node for node in self.nodes if node.get_label() == label][0]

    def reset(self) -> None:
        """
        Reset the entire canvas by removing existing objects.
        """
        self.delete("all")
        self.nodes = []
        self.arrows = []
        self.temporary_arrow = None
        self.drawing_arrow = False
        self.arrow_start_node = None
        self.context_menu = None


class CanvasContextMenu:
    """
    The context menu will allow adding new constructs, observables, etc. on right click.
    """

    def __init__(
        self,
        root: ttk.Window,
        canvas: "EdnoCanvas",
        node_classes: dict[str, Callable],
    ) -> None:
        """
        Initializes a new instance of the CanvasContextMenu class.

        Args:
            root (ttk.Window): The root window of the GUI.
            canvas (EdnoCanvas): The canvas object associated with the context menu.
            node_classes: dict[str, Callable]: A dictionary of node classes that can be added to the canvas.
        """
        self.canvas = canvas
        self.node_classes = node_classes
        self.canvas_context_menu = tk.Menu(root, tearoff=0)
        for key, node_class in self.node_classes.items():
            self.canvas_context_menu.add_command(
                label=f"Add {key}",
                command=lambda node_class=node_class, key=key: self.create_node(
                    node_class, type=key
                ),
            )

        self.canvas.bind("<Button-3>", self.show_right_click_menu)
        self.canvas.bind("<Button-1>", self.release_right_click_menu)

    def create_node(self, node_class: Callable, type: str) -> None:
        """
        Creates a new node on the canvas at the position of the context menu.

        Args:
            node_class (Callable): The class of the node
            type (str): The type of the node
        """
        self.canvas.nodes.append(
            node_class(
                self.canvas,
                label="",
                x=self.canvas.context_menu.position[0],
                y=self.canvas.context_menu.position[1],
                type=type,
                allowed_connections=self.canvas.allowed_connections,
                font=self.canvas.font,
                font_color=self.canvas.font_color,
                node_color=self.canvas.node_color,
                arrow_types=self.canvas.arrow_types,
                arrow_color=self.canvas.arrow_color,
            )
        )
        self.canvas.context_menu = None

    def show_right_click_menu(self, event: tk.Event) -> None:
        """
        Displays the right-click context menu at the position of the mouse click event.

        Args:
            event (tk.Event): The mouse click event.
        """
        if self.canvas.context_menu is None:
            self.canvas.context_menu = self.canvas_context_menu
        else:
            return
        # https://www.geeksforgeeks.org/right-click-menu-using-tkinter/
        try:
            self.canvas.context_menu.tk_popup(event.x_root + 1, event.y_root + 1, 0)
        finally:
            self.canvas.context_menu.grab_release()
            # save position on canvas to add nodes at that position
            self.canvas.context_menu.position = [
                self.canvas.canvasx(event.x),
                self.canvas.canvasy(event.y),
            ]

    def release_right_click_menu(self, event: tk.Event) -> None:
        """
        Releases the right-click context menu and resets the canvas state.

        Args:
            event (tk.Event): The mouse click event.
        """
        if self.canvas.context_menu is not None:
            self.canvas.context_menu.unpost()
            self.canvas.context_menu = None
        if self.canvas.drawing_arrow:
            self.canvas.drawing_arrow = False
            self.canvas.arrow_start_node = None
            if self.canvas.temporary_arrow is not None:
                self.canvas.delete(self.canvas.temporary_arrow)
                self.canvas.temporary_arrow = None
