import tkinter as tk
from .nodes import Node
from .arrow import Arrow
import customtkinter as ctk
from typing import Callable


def disallow_existing_connections(predictors_node, dependents_node, all_nodes) -> bool:
    """
    Allow all connections except for existing connections.

    Args:
        predictors_node (Node): The node that is the predictor.
        dependents_node (Node): The node that is the dependent.
        all_nodes (list[Node]): A list of all nodes in the canvas.

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


def disallow_self_loops(predictors_node, dependents_node, all_nodes) -> bool:
    """
    Allow all connection except for self-loops.

    Args:
        predictors_node (Node): The node that is the predictor.
        dependents_node (Node): The node that is the dependent.
        all_nodes (list[Node]): A list of all nodes in the canvas.

    Returns:
        bool: True if connection is allowed
    """
    return predictors_node != dependents_node


def disallow_self_and_existing(predictors_node, dependents_node, all_nodes) -> bool:
    """
    Allow all connection except for self-loops and existing connections.

    Args:
        predictors_node (Node): The node that is the predictor.
        dependents_node (Node): The node that is the dependent.
        all_nodes (list[Node]): A list of all nodes in the canvas.

    Returns:
        bool: True if connection is allowed
    """
    return disallow_existing_connections(
        predictors_node, dependents_node, all_nodes
    ) and disallow_self_loops(predictors_node, dependents_node, all_nodes)


class EdnoCanvas(tk.Canvas):
    """
    A custom canvas widget for interactive, directed graphs.

    This canvas provides functionality for drawing nodes, arrows, scrolling, and zooming.

    Args:
        form_names: dict[str, str]
            Specifies what the rectangles and ellipse are called on the canvas.
        nodes : list[Node]
            A list of Node objects representing the nodes in the canvas.
        arrows : list[Arrow]
            A list of Arrow objects representing the arrows in the canvas.
        drawing_arrow : bool
            Indicates whether the canvas is currently in arrow drawing mode.
        arrow_start_node : Node or None
            The starting node of the arrow being drawn, or None if no arrow is being drawn.
        context_menu : CanvasContextMenu or None
            The context menu currently open in the canvas, or None if no menu is open.
        canvas_context_menu : CanvasContextMenu
            The context menu for the canvas.
        model_elements_are_moving : bool
            Indicates whether the model elements (nodes, arrows) are currently being moved.
        scale_factor : float
            The current scale factor for zooming.
        font : float
            The current font for text elements in the canvas.

    Returns:
        __init__(self, root: ctk.CTk, **kwargs) -> None:
            Initialize a new EdnoCanvas.

        start_scroll(self, event: tk.Event) -> None:
            Initialize scrolling in the canvas.

        do_scroll(self, event: tk.Event) -> None:
            Perform scrolling in the canvas.

        zoom(self, event: tk.Event) -> None:
            Zoom in and out of the canvas.

        reset(self) -> None:
            Reset the entire canvas by removing existing objects.
    """

    def __init__(
        self,
        root: ctk.CTk,
        form_names: dict[str, str] = {"rectangle": "rectangle", "ellipse": "ellipse"},
        font=("Arial", 9),
        font_color="#000000",
        node_color: dict[str, str] = {
            "default": "#ADD8E6",
            "allowed": "#90E4C1",
            "not allowed": "#ffcccb",
        },
        arrow_color="#000000",
        allowed_connections: Callable = disallow_self_and_existing,
        **kwargs,
    ) -> None:
        """
        Initialize a new EdnoCanvas.

        Parameters
        ----------
        root : ctk.CTk
            The ctk.CTk root object to which the EdnoCanvas should be added.
        form_names: dict[str, str]
            Specifies what the rectangles and ellipse are called on the canvas. For example,
            {"rectangle": "manifest", "ellipse": "latent"} specifies that the rectangles will be called manifest variables and the ellipse will be called latent variables.
        font : tuple with font name and font size
        font_color: str with the color of all text elements
        node_color : dict[str, str] with keys "default", "allowed", "not allowed". default color for nodes, color for allowed connections, color for not allowed connections
        arrow_color : str with the color of all arrows
        allowed_connections : Callable  with signature (predictors_node, dependents_node, all_nodes) -> bool. This function will be called each time a user tries to connect two nodes. If the function returns True, the connection will be allowed, otherwise not. If the user hovers over a node, the color of the node will change to the allowed color if the connection is allowed, otherwise to the not allowed color.
        **kwargs : optional
            Additional arguments passed to ctk.CTk.

        Returns:
            None
        """

        super().__init__(root, kwargs)

        self.form_names = form_names
        self.node_color = node_color
        self.font_color = font_color
        self.arrow_color = arrow_color
        self.allowed_connections = allowed_connections

        # initialize nodes
        self.nodes: list[Node] = []
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
        self.canvas_context_menu = CanvasContextMenu(root, self, self.form_names)

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
        """
        Initialize scrolling in the canvas.

        Parameters
        ----------
        event : tk.Event
            The tkinter event that tells us the coordinates we are moving towards.

        Returns
        -------
        None
        """

        # when starting to scroll, close menus
        self.canvas_context_menu.release_right_click_menu(event)
        if not self.model_elements_are_moving:
            self.scan_mark(event.x, event.y)

    def do_scroll(self, event: tk.Event) -> None:
        """
        Perform scrolling in the canvas.

        Parameters
        ----------
        event : tk.Event
            The tkinter event that tells us the coordinates we are moving towards.

        Returns
        -------
        None
        """
        if not self.model_elements_are_moving:
            self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event: tk.Event) -> None:
        """
        Zoom in and out of the canvas.

        Parameters
        ----------
        event : tk.Event
            The tkinter event that tells us if we are scrolling in or out.

        Returns
        -------
        None
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
            node.update_box()
        # the arrow heads also need to be updated
        for arrow in self.arrows:
            arrow.arrow_head.update()

    def update_temporary_arrow(self, event: tk.Event) -> None:
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
        """
        Get all connections between nodes.

        Returns
        -------
        list[dict]
            A list of dictionaries representing the connections between nodes.
        """
        connections = []
        for arrow in self.arrows:
            connections.append(arrow.save())
        return connections

    def get_node_connections(self) -> dict:
        """
        Get all connections between nodes.

        Returns
        -------
        dict
            A dictionary representing the connections between nodes.
        """
        node_connections = {}
        for node in self.nodes:
            # getting the labels of the predictors and dependents is a bit complicated, as each node
            # only knows about the arrows, but not the predicting / predicted nodes themselves. So,
            # we need to first find the arrows and then get the labels of the nodes these arrows come from / go to.
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
                "depdentents": dependents,
                "predictors": predictors,
            }
        return node_connections

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
        root: ctk.CTk,
        canvas: "EdnoCanvas",
        form_names: dict[str, str] = {"rectangle": "rectangle", "ellipse": "ellipse"},
    ) -> None:
        """
        Initializes a new instance of the CanvasContextMenu class.

        Args:
            root (ctk.CTk): The root window of the GUI.
            canvas (EdnoCanvas): The canvas object associated with the context menu.
            form_names: dict[str, str]
                Specifies what the rectangles and ellipse are called on the canvas. For example,
                {"rectangle": "manifest", "ellipse": "latent"} specifies that the rectangles will be called manifest variables and the ellipse will be called latent variables.
        """
        self.canvas = canvas
        self.form_names = form_names
        self.canvas_context_menu = tk.Menu(root, tearoff=0)
        self.canvas_context_menu.add_command(
            label=f"Add {self.form_names['ellipse']}", command=self.create_ellipse
        )
        self.canvas_context_menu.add_command(
            label=f"Add {self.form_names['rectangle']}", command=self.create_rectangle
        )

        self.canvas.bind("<Button-3>", self.show_right_click_menu)
        self.canvas.bind("<Button-1>", self.release_right_click_menu)

    def create_ellipse(self) -> None:
        """
        Creates a new ellipse node on the canvas at the position of the context menu.
        """
        self.canvas.nodes.append(
            Node(
                self.canvas,
                label="",
                x=self.canvas.context_menu.position[0],
                y=self.canvas.context_menu.position[1],
                type=self.form_names["ellipse"],
                allowed_connections=self.canvas.allowed_connections,
                shape="ellipse",
                font=self.canvas.font,
                font_color=self.canvas.font_color,
                node_color=self.canvas.node_color,
                arrow_color=self.canvas.arrow_color,
            )
        )
        self.canvas.context_menu = None

    def create_rectangle(self) -> None:
        """
        Creates a new rectangle node on the canvas at the position of the context menu.
        """
        self.canvas.nodes.append(
            Node(
                self.canvas,
                label="",
                x=self.canvas.context_menu.position[0],
                y=self.canvas.context_menu.position[1],
                type=self.form_names["rectangle"],
                allowed_connections=self.canvas.allowed_connections,
                shape="rectangle",
                font=self.canvas.font,
                font_color=self.canvas.font_color,
                node_color=self.canvas.node_color,
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
            self.canvas.context_menu.tk_popup(event.x_root, event.y_root, 0)
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
