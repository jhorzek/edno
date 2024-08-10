import customtkinter as ctk
import tkinter as tk
from math import inf
from typing import Any, Callable
from .arrow import Arrow
from .text_box import TextBox, distance


def allow_all_connections(predictors_node, dependents_node, all_nodes) -> bool:
    """
    Allow all connections between nodes. This function is a placeholder that can be replaced with more sophisticated rules that determine if a connection is allowed or not.

    Args:
        predictors_node (Node): The node that is the predictor.
        dependents_node (Node): The node that is the dependent.
        all_nodes (list[Node]): A list of all nodes in the canvas.

    Returns:
        bool: Always True.

    """
    return True


class R2(TextBox):
    """
    A textbox that is located below the actual node. This textbox is used to show additional information, mainly the R squared in regressions.

    Args:
        canvas (EdnoCanvas): The canvas on which the R2 node is placed.
        x (int): The x-coordinate of the R2 node.
        y (int): The y-coordinate of the R2 node.
        text (str): The text displayed on the R2 node.
        font (tuple, optional): The font used for the text. Defaults to ("Arial", 9).
        box_shape (str, optional): The shape of the box surrounding the R2 node. Defaults to "rectangle".
        box_color (str, optional): The color of the box surrounding the R2 node. Defaults to "#faf9f6".
        value (float | None, optional): The value shown on the screen. Defaults to None.

    Attributes:
        value (float | None): The value shown on the screen. It will be rounded.

    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        x: int,
        y: int,
        text: str,
        font=("Arial", 9),
        box_shape: str = "rectangle",
        box_color: str = "#faf9f6",
        value: float | None = None,
    ) -> None:

        super().__init__(
            canvas=canvas,
            x=x,
            y=y,
            text=text,
            font=font,
            box_shape=box_shape,
            box_color=box_color,
        )
        self.value = value


class Node(TextBox):
    """
    Nodes are text boxes with added shapes and connections. They represent the variables within a model.

    Attributes
    ----------
    canvas : Canvas
        The apps canvas that is drawn upon
    label: int
        The id of the label object. The actual label must be extracted from the canvas
    shape: int
        The id of the shape that is drawn around the label.
    dependents_arrow_id : list
        list with ids of all dependents_arrow_id connections (connections where the node is a predictor). These are the ids of the arrows!
    predictors_arrow_id : list
        list with ids of all predictors_arrow_id connections (connections where the node is a dependent). These are the ids of the arrows!
    additional_information: dict
        Optional dict to store additional information (e.g., the name of an arrow, ...)
    context_menu : tk.Menu
        right click menu showing options to add paths, delete, ...
    r2: int
        TextBox with value of R Squared

    Methods
    -------
    add_r2()
        Adds the r2 attribute
    set_r2(r2)
        Sets the value of the r2 shown on the canvas
    add_circle()
        draws a circle around the object
    add_square():
        draws a square around the object
    add_actions():
        adds the left and right click actions to the model
    set_scale():
        specify the scale of the item
    context_menu_show(event):
        show the context menu
    move(delta_x, delta_x):
        move the node by delta_x and delta_y
    rename():
        launches a pop up to rename the node (change the label)
    get_label():
        get the actual text that is in the label
    delete():
        delete the node from the canvas.
    start_connection_mode():
        start adding a path between nodes
    draw_arrow():
        draws the actual arrow between nodes
    on_start_drag():
        used for moving the node
    on_stop_drag():
        used for moving the node
    on_drag():
        used for moving the node
    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        label: str,
        x: int,
        y: int,
        type: str,
        shape: str,
        additional_information: None | dict[Any, Any] = None,
        font = ("Arial", 9),
        node_color: str = "#cfcfcf",
    ) -> None:
        """
        Parameters
        ----------
        canvas : Canvas
            The canvas where the arrow will be added
        label: string
            The label (name) of the node. This will be shown on the canvas as the nodes name
        x : int
            The x-position of the new node on the canvas
        y : int
            The y-position of the new node on the canvas
        type : string
            "optional type.
        """
        self.shape = shape
        self.font = font

        if label == "":
            label = create_label(canvas.nodes)

        super().__init__(
            canvas=canvas,
            x=x,
            y=y,
            text=label,
            box_shape=shape,
            box_color=node_color,
            space_around=10,
            font = self.font
        )
        # the node id uniquely identifies the entire node. It is identical to the
        # text id
        self.node_id = self.text_id

        # dependents_arrow_id and predictors_arrow_id will save the ids of the ARROWS of predictor and
        # dependent nodes
        self.dependents_arrow_id: list[int] = []
        self.predictors_arrow_id: list[int] = []
        self.additional_information = additional_information
        self.type: str = type
        self.scale: Any = None

        # Right click menu for node:
        self.context_menu = NodeMenu(self.canvas, self.type, self.node_id)

        # R Squared
        # located below node
        bbox = self.canvas.bbox(self.text_id)
        self.r2 = R2(
            canvas=self.canvas,
            x=bbox[0] + 0.5 * (bbox[2] - bbox[0]),
            y=bbox[3] + 25,
            text="",
            font=self.font,
            box_color="#faf9f6",
            value=None,
        )
        self.r2.hide()

        self.add_actions()

        self.drag_data = None

    def set_r2(self, r2: float) -> None:
        """
        Specify the R Squared value of a node

        Parameters
        ----------
        r2 : float
            The R squared value.
        """
        if r2 != "":
            self.r2.value = r2
            r2_text: str = f"R\u00b2 = {r2:.2f}"
            self.r2.set_text(r2_text, font=self.font)
            self.r2.show()

    def add_actions(self) -> None:
        """
        Add the right-click, left-click, etc. actions to a node.
        """
        # Add moving on drag and drop
        self.canvas.tag_bind(self.text_id, "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind(self.shape_id, "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind(self.text_id, "<ButtonRelease-1>", self.on_stop_drag)
        self.canvas.tag_bind(self.shape_id, "<ButtonRelease-1>", self.on_stop_drag)
        self.canvas.tag_bind(self.text_id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.shape_id, "<B1-Motion>", self.on_drag)
        # Add right click menu
        self.canvas.tag_bind(self.text_id, "<Button-3>", self.context_menu_show)
        self.canvas.tag_bind(self.shape_id, "<Button-3>", self.context_menu_show)


    def context_menu_show(self, event: tk.Event) -> None:
        """
        Add right-click menu to the node.

        Parameters
        ----------
            event: tkinter event to get the position of the click.
        """
        if self.canvas.context_menu is None:
            self.canvas.context_menu = self.context_menu
        else:
            return
        # https://www.geeksforgeeks.org/right-click-menu-using-tkinter/
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.context_menu.grab_release()
            self.context_menu.position = [event.x, event.y]

    def move(self, delta_x: float, delta_y: float) -> None:
        """
        Move the node in space.

        The location of the node is given by the location of its label. This location is specified as a single
        point [x1,y1]. move() adjusts this points.

        Parameters
        ----------
        delta_x : float
            Change in x
        delta_y : float
            Change in y
        """
        self.canvas.move(self.text_id, delta_x, delta_y)
        self.canvas.move(self.shape_id, delta_x, delta_y)
        self.r2.move(delta_x, delta_y)

        for out in self.dependents_arrow_id:
            for arr in self.canvas.arrows:
                if arr.id == out:
                    arr.move(delta_x, delta_y, 0, 0)
        for inc in self.predictors_arrow_id:
            for arr in self.canvas.arrows:
                if arr.id == inc:
                    arr.move(0, 0, delta_x, delta_y)

    def move_to(self, x: int | float, y: int | float) -> None:
        """
        Moves the text box to the specified location.

        Parameters:
        - x: The location on the x-axis.
        - y: The location on the y-axis.
        """
        raise ValueError("Cannot use move_to for class Node. Only move is allowed.")

    def get_label(self) -> str:
        """
        Return the label of a node
        """
        return self.text

    def delete(self) -> None:
        """
        Delete the node from the canvas
        """
        self.canvas.delete(self.text_id)
        self.canvas.delete(self.shape_id)
        self.r2.delete()
        self.canvas.context_menu = None
        remove_arrow = []
        for out in self.dependents_arrow_id:
            remove_arrow.append(out)
        for inc in self.predictors_arrow_id:
            remove_arrow.append(inc)

        for arrs in self.canvas.arrows:
            if arrs.id in remove_arrow:
                arrs.delete()
        self.canvas.nodes = [
            nd for nd in self.canvas.nodes if nd.node_id != self.node_id
        ]

    def draw_arrow(
        self,
        event: tk.Event | None,
        check_connection_allowed: Callable = allow_all_connections,
    ) -> None:
        """
        Draw an arrow between nodes.

        Parameters
        ----------
            event: tkinter event.
        """
        if self.canvas.drawing_arrow:
            start_node = self.canvas.arrow_start_node
            end_node = self.node_id
            if check_connection_allowed(
                predictors_node=start_node,
                dependents_node=end_node,
                all_nodes=self.canvas.nodes,
            ):
                # get center of object
                bbox = self.canvas.bbox(start_node)
                x1 = bbox[0] + 0.5 * (bbox[2] - bbox[0])
                y1 = bbox[1] + 0.5 * (bbox[3] - bbox[1])
                bbox = self.canvas.bbox(end_node)
                x2 = bbox[0] + 0.5 * (bbox[2] - bbox[0])
                y2 = bbox[1] + 0.5 * (bbox[3] - bbox[1])

                # draw arrow:
                new_arrow = self.canvas.create_line(
                    x1, y1, x2, y2
                )
                self.canvas.tag_lower(new_arrow)
                self.canvas.tag_lower(new_arrow)
                self.canvas.arrows.append(
                    Arrow(
                        self.canvas,
                        new_arrow,
                        predictors_id=start_node,
                        dependents_id=end_node,
                    )
                )
            else:
                self.canvas.drawing_arrow = False
                self.canvas.arrow_start_node = None
                if self.canvas.temporary_arrow is not None:
                    self.canvas.delete(self.canvas.temporary_arrow)
                    self.canvas.temporary_arrow = None
        for nd in self.canvas.nodes:
            if self.canvas.drawing_arrow:
                if nd.node_id == start_node:
                    nd.dependents_arrow_id.append(new_arrow)
                if nd.node_id == end_node:
                    nd.predictors_arrow_id.append(new_arrow)
        self.canvas.drawing_arrow = False
        self.canvas.arrow_start_node = None
        if self.canvas.temporary_arrow is not None:
            self.canvas.delete(self.canvas.temporary_arrow)
            self.canvas.temporary_arrow = None

    def on_start_drag(self, event: tk.Event) -> None:
        """
        Move node on left-click-drag

        Parameters
        ----------
            event: tkinter event.
        """
        # ensure that the canvas is not moving as well:
        self.canvas.model_elements_are_moving = True
        self.draw_arrow(event)
        self.drag_data = {"x": event.x, "y": event.y}

    def on_stop_drag(self, event: tk.Event) -> None:
        """
        Move node on left-click-drag

        Parameters
        ----------
            event: tkinter event.
        """
        # ensure that the canvas is not moving as well:
        self.canvas.model_elements_are_moving = False
        self.drag_data = None

    def on_drag(self, event: tk.Event) -> None:
        """
        Move node on left-click-drag

        Parameters
        ----------
            event: tkinter event.
        """
        if self.drag_data is None:
            # this is just a backup in case the drag_data is not correctly
            # set by on_start_drag
            self.drag_data = {"x": event.x, "y": event.y}
            return
        delta_x: float = float(event.x - self.drag_data["x"])
        delta_y: float = float(event.y - self.drag_data["y"])
        # for snapping, we are looking for the nodes with the closest x and y distance. If this distance is lower than
        # some threshold, we simply set the current x or y location
        # to that of the closest object. Otherwise, we move the
        # object.
        snap_dist = 3
        closest_xy = find_closest_node_xy(self, self.canvas.nodes)
        if (abs(closest_xy["delta_x"]) < snap_dist) & (abs(delta_x) < snap_dist):
            delta_x = closest_xy["closest_x"] - self.get_location()[0]
        if (abs(closest_xy["delta_y"]) < snap_dist) & (abs(delta_y) < snap_dist):
            delta_y = closest_xy["closest_y"] - self.get_location()[1]

        self.move(delta_x=delta_x, delta_y=delta_y)
        self.drag_data = {"x": event.x, "y": event.y}

    def save(self) -> dict[str, str]:
        """
        Save the node to a dictionary that allows reproducing the node.

        Returns
        -------
        Returns a dictionary with

        id: int
            The numeric id of the object on the canvas
        label: string
            The label of the node
        position: list
            x and y position of the node
        predictors: list
            list with labels of predictors
        dependents: list
            list with labels of outcomes
        scale: string
            scale type of the node
        r2: float
            R squared
        """

        predictor_arrows = [
            inc_arr.predictors_id
            for inc_arr in self.canvas.arrows
            if inc_arr.id in self.predictors_arrow_id
        ]
        predictor_nodes = [
            nd.get_label() for nd in self.canvas.nodes if nd.node_id in predictor_arrows
        ]
        dependent_arrows = [
            out_arr.dependents_id
            for out_arr in self.canvas.arrows
            if out_arr.id in self.dependents_arrow_id
        ]
        dependent_nodes = [
            nd.get_label() for nd in self.canvas.nodes if nd.node_id in dependent_arrows
        ]

        node_dict = {
            "id": self.node_id,
            "label": self.get_label(),
            "type": self.type,
            "position": self.canvas.coords(self.node_id),
            "predictors": predictor_nodes,
            "dependents": dependent_nodes,
            "r2": self.r2.value,
        }

        return node_dict


def create_label(nodes: list[Node], base: str = "var_") -> str:
    """
    Create a valid label for a node

    Nodes must have unique labels. This function generates a valid label for a new node.

    Parameters
    ----------
    base : string
        base specifies the first par of the label. The default is "var_"
    nodes : list
        List with all nodes contained in the canvas
    """
    for i in range(1, 1000):
        new_label = f"{base}{i}"
        if check_label(new_label, nodes):
            break
    return new_label


def check_label(new_label: str, nodes: list[Node]) -> bool:
    """
    Check if a label is valid

    Nodes must have unique labels. This function checks if a suggested label is valid.

    Parameters
    ----------
    new_label : string
        Suggested new node label
    nodes : list
        List with all nodes contained in the canvas
    """
    for nd in nodes:
        if new_label == nd.get_label():
            return False
    return True


class NodeMenu(tk.Menu):
    """
    A custom menu class for nodes. The menu will be shown when right-clicking on a node.

    Parameters:
    - canvas: The canvas object associated with the menu.
    - type: The type of the node.
    - node_id: The ID of the node.

    Attributes:
    - canvas: The canvas object associated with the menu.
    - type: The type of the node.
    - node_id: The ID of the node.
    """

    def __init__(self, canvas: "EdnoCanvas", type: str, node_id: int) -> None:
        self.canvas = canvas
        self.node_id = node_id
        super().__init__(canvas, tearoff=0)

        self.add_command(label="Add Path", command=self.start_connection_mode)
        self.add_command(label="Rename Node", command=self.rename)
        self.add_command(label="Delete Node", command=self.delete)

    def start_connection_mode(self) -> None:
        """
        Add a path to a node. This function does not draw the arrow; it just checks if we are
        currently in a drawing-state. If not, it starts the drawing mode and allows adding a path.
        """
        node_position = self.canvas.coords(self.node_id)
        self.canvas.temporary_arrow = self.canvas.create_line(
            node_position[0],
            node_position[1],
            node_position[0],
            node_position[1],
            width=2, arrow=tk.LAST
        )
        self.canvas.tag_lower(self.canvas.temporary_arrow)
        self.canvas.drawing_arrow = True
        self.canvas.arrow_start_node = self.node_id
        # close context menu
        self.canvas.context_menu = None

    def rename(self) -> None:
        """
        Rename a node

        This will open a dialog in the GUI for users to rename the nodes
        """
        input = ctk.CTkInputDialog(text="New variable name:", title="Rename Variable")
        new_label = input.get_input()  # opens the dialog
        if (new_label is not None) and (len(new_label) > 0):
            if check_label(new_label=new_label, nodes=self.canvas.nodes):
                # get current node and change label
                [
                    nd.set_text(new_label)
                    for nd in self.canvas.nodes
                    if nd.node_id == self.node_id
                ]
            else:
                tk.messagebox.showerror(
                    title="Duplicated Variable",
                    message=f"The variable {new_label} is already in the model.",
                )
        # close context menu
        self.canvas.context_menu = None

    def delete(self) -> None:
        """
        Delete the node from the canvas.

        Returns:
            None
        """
        [nd.delete() for nd in self.canvas.nodes if nd.node_id == self.node_id]


def find_closest_node_xy(node: Node, nodes: list[Node]) -> dict[str, float]:
    """
    Finds the closest node in terms of x and y coordinates to the given node.

    Args:
        node (Node): The node for which to find the closest node.
        nodes (list[Node]): A list of nodes to search for the closest node.

    Returns:
        dict[str, float]: A dictionary containing the closest x and y coordinates
                          and the corresponding delta values.

    """
    delta_x = inf
    closest_x = inf
    delta_y = inf
    closest_y = inf
    for nd in nodes:
        if nd.node_id == node.node_id:
            continue
        dist = distance(node, nd)
        if abs(dist["x_dist"]) < abs(delta_x):
            closest_x = nd.get_location()[0]
            delta_x = dist["x_dist"]
        if abs(dist["y_dist"]) < abs(delta_y):
            closest_y = nd.get_location()[1]
            delta_y = dist["y_dist"]
    return {
        "closest_x": closest_x,
        "delta_x": delta_x,
        "closest_y": closest_y,
        "delta_y": delta_y,
    }
