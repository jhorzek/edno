import tkinter as tk
import customtkinter as ctk
from math import inf
from typing import Callable, Any
from .Arrow import Arrow
from .TextBox import TextBox, get_polygon_points


def allow_all_connections(
    predictors_node: int, dependents_node: int, all_nodes: list["Node"]
) -> bool:
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


def create_label(nodes: list["Node"], base: str = "node_") -> str:
    """
    Create a valid label for a node

    Nodes must have unique labels. This function generates a valid label for a new node.

    Args:
        nodes (list[Node]): List with all nodes contained in the canvas
        base (string): base specifies the first par of the label. The default is "node_"
    """
    for i in range(1, 1000):
        new_label = f"{base}{i}"
        if check_label(new_label, nodes):
            break
    return new_label


def check_label(new_label: str, nodes: list["Node"]) -> bool:
    """
    Check if a label is valid

    Nodes must have unique labels. This function checks if a suggested label is valid.

    Args:
    new_label (str): Suggested new node label
    nodes (list[Node]): List with all nodes contained in the canvas
    """
    for nd in nodes:
        if new_label == nd.get_label():
            return False
    return True


def get_line_line_intersection(
    line1: list[float], line2: list[float]
) -> list[float] | None:
    """
    Calculate the intersection point of two lines.

    Args:
        line1 (list[float]): The coordinates of the first line.
        line2 (list[float]): The coordinates of the second line.

    Returns:
        list[float] | None: The coordinates of the intersection point or None if the lines are parallel.
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # check if both lines are parallel
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        return None
    p_x = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    p_x /= denominator
    p_y = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    p_y /= denominator

    return [p_x, p_y]


class NodeMenu(tk.Menu):
    """NodeMenu is a right-click menu for nodes. It allows adding paths, renaming nodes, and deleting nodes."""

    def __init__(self, canvas: "EdnoCanvas", node_id: int) -> None:
        """_summary_

        Args:
            canvas (EdnoCanvas): EdnoCanvas that contains the node. Necessary to show the menu.
            node_id (int): Id of the node. Necessary to remove, etc the node.
        """
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
            width=2,
            arrow=tk.LAST,
            fill=self.canvas.arrow_color,
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
            # get current node and change label
            self.canvas.get_node_with_id(self.node_id).set_label(new_label)
        # close context menu
        self.canvas.context_menu = None

    def delete(self) -> None:
        """
        Delete the node from the canvas.
        """
        self.canvas.get_node_with_id(self.node_id).delete()


def find_closest_node_xy(node: "Node", nodes: list["Node"]) -> dict[str, float]:
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
        dist = node.distance(nd)
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


class PolyNode(TextBox):
    """
    A class to create and manage a node on a canvas. This class creates a polygon around the node label, but can also be used as the basis for classes with other shapes. In this case, all functions referring to the shape must be replaced.
    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        x: int | float,
        y: int | float,
        label: str,
        font: tuple[str, int] = ("Arial", 9),
        font_color: str = "#000000",
        polygon_sides: int = 4,
        node_color: dict[str, str] = {
            "default": "#ADD8E6",
            "allowed": "#90E4C1",
            "not allowed": "#ffcccb",
        },
        arrow_color: str = "#000000",
        allowed_connections: Callable = allow_all_connections,
        NodeMenuClass: Callable = NodeMenu,
        linked_objects: Any = None,
    ) -> None:
        """Initializes a basic node instance.

        Args:
            canvas (EdnoCanvas): The tkinter canvas object where the node box will be drawn.
            x (int | float): The x-coordinate of the node's position.
            y (int | float): The y-coordinate of the node's position.
            label (str): The label to be displayed inside the node.
            font (tuple[str, int], optional): The font of the text (default is ("Arial", 12)).
            font_color (str, optional): The color of the text. Defaults to "#000000".
            polygon_sides (int, optional): The number of sides of the polygon around the text (default is 4).
            node_color (str, optional): The color of the text box (default is #faf9f6).
            arrow_color (str, optional): The color of the arrows. Defaults to "#000000".
            allowed_connections (Callable, optional): this function will be called every time a user tries creating a new node. The function should return False if the user tries to create a non-allowed connection. Defaults to allow_all_connections. See allow_all_connections for the signature of these functions.
            NodeMenuClass (Callable, optional): The right-click menu for the node. Defaults to NodeMenu.
            linked_objects (Any, optional): linked_objects allows linking other objects to the node. This could, for example, be an R squared value that is shown above the node. These objects must implement the following methods: move(delta_x, delta_y), delete(), hide(), show(). Defaults to None.
        """

        if label == "":
            label = create_label(canvas.nodes)

        super().__init__(
            canvas=canvas,
            x=x,
            y=y,
            label=label,
            font=font,
            font_color=font_color,
            polygon_sides=polygon_sides,
            node_color=node_color["default"],
            linked_objects=linked_objects,
        )

        self.node_color = node_color

        self.arrow_color = arrow_color
        self.allowed_connections = allowed_connections

        # dependents_arrow_id and predictors_arrow_id will save the ids of the ARROWS of predictor and
        # dependent nodes
        self.dependents_arrow_id: list[int] = []
        self.predictors_arrow_id: list[int] = []

        self.add_drag_drop_actions()
        self.add_right_click_menu(NodeMenuClass)
        self.add_label_actions()
        self.add_shape_actions()

    def add_drag_drop_actions(self) -> None:
        """Add all actions required to drag and drop the
        node on the canvas using the mouse
        """
        self.canvas.tag_bind(self.node_id, "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind(self.node_id, "<ButtonRelease-1>", self.on_stop_drag)
        self.canvas.tag_bind(self.node_id, "<B1-Motion>", self.on_drag)

        self.canvas.tag_bind(self.shape_id, "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind(self.shape_id, "<ButtonRelease-1>", self.on_stop_drag)
        self.canvas.tag_bind(self.shape_id, "<B1-Motion>", self.on_drag)

    def add_right_click_menu(self, node_menu: Callable = NodeMenu) -> None:
        """Add a right click menu to the node.

        Args:
            node_menu (Callable, optional): The right-click menu for the node. Defaults to NodeMenu.
        """
        self.context_menu = NodeMenu(self.canvas, self.node_id)
        self.canvas.tag_bind(self.node_id, "<Button-3>", self.context_menu_show)
        self.canvas.tag_bind(self.shape_id, "<Button-3>", self.context_menu_show)

    def add_label_actions(self) -> None:
        """
        Add the right-click, left-click, etc. actions to the label of a node.
        """
        # Hover effect: Used to change color of the node when hovering over it in arrow drawing mode
        self.canvas.tag_bind(self.node_id, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.node_id, "<Leave>", self.on_leave)

    def add_shape_actions(self) -> None:
        """Add the right-click, left-click, etc. actions to the shape of a node."""
        # Hover effect: Used to change color of the node when hovering over it in arrow drawing mode
        self.canvas.tag_bind(self.shape_id, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.shape_id, "<Leave>", self.on_leave)
        # right click menu
        self.canvas.tag_bind(self.shape_id, "<Button-3>", self.context_menu_show)

    def on_start_drag(self, event: tk.Event) -> None:
        """
        Move node on left-click-drag

        Args
            event (tk.Event): tkinter event.
        """
        # ensure that the canvas is not moving as well:
        self.canvas.model_elements_are_moving = True
        self.draw_arrow(event)
        self.drag_data = {"x": event.x, "y": event.y}

    def on_stop_drag(self, event: tk.Event) -> None:
        """
        Move node on left-click-drag

        Args
            event (tk.Event): tkinter event.
        """
        # ensure that the canvas is not moving as well:
        self.canvas.model_elements_are_moving = False
        self.drag_data = None

    def on_drag(self, event: tk.Event) -> None:
        """
        Move node on left-click-drag

        Args
            event (tk.Event): tkinter event.
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

    def on_enter(self, event: tk.Event) -> None:
        """
        Change color of node when hovering over it in arrow drawing mode

        Args
            event (tk.Event): tkinter event.
        """
        if self.canvas.drawing_arrow:
            if self.allowed_connections(
                predictors_node=self.canvas.arrow_start_node,
                dependents_node=self.node_id,
                all_nodes=self.canvas.nodes,
            ):
                self.canvas.itemconfig(self.shape_id, fill=self.node_color["allowed"])
            else:
                self.canvas.itemconfig(
                    self.shape_id, fill=self.node_color["not allowed"]
                )

    def on_leave(self, event: tk.Event) -> None:
        """
        Change color of node back to normal when leaving it in arrow drawing mode

        Args
            event (tk.Event): tkinter event.
        """
        self.canvas.itemconfig(self.shape_id, fill=self.node_color["default"])

    def context_menu_show(self, event: tk.Event) -> None:
        """
        Add right-click menu to the node.

        Args
            event (tk.Event): tkinter event to get the position of the click.
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

    def move(self, delta_x: float, delta_y: float):
        """Moves the text and shape of the node by the specified amounts.

        Args:
            delta_x (float): The change along the x-axis.
            delta_y (float): The change along the y-axis.
        """
        self.move_text(delta_x, delta_y)
        self.move_shape(delta_x, delta_y)
        self.move_linked_objects(delta_x, delta_y)
        self.move_arrows(delta_x, delta_y)

    def move_arrows(self, delta_x: float, delta_y: float):
        """Move all arrows by the specified amounts.

        Args:
            delta_x (float): The change along the x-axis.
            delta_y (float): The change along the y-axis.
        """
        for out in self.dependents_arrow_id:
            for arr in self.canvas.arrows:
                if arr.id == out:
                    arr.update_position()
        for inc in self.predictors_arrow_id:
            for arr in self.canvas.arrows:
                if arr.id == inc:
                    arr.update_position()

    def move_to(self, x: int | float, y: int | float) -> None:
        """
        Moves the text box to the specified location.

        Args:
            x (int | float): The new location on the x-axis.
            y (int | float): The new location on the y-axis.
        """
        raise ValueError("Cannot use move_to for class Node. Only move is allowed.")

    def draw_arrow(self, event, arrow_type="directed") -> None:
        """
        Draw an arrow between nodes.

        Args:
            event: Required for use with tkinter events.
        """
        if self.canvas.drawing_arrow:
            start_node_id = self.canvas.arrow_start_node
            end_node_id = self.node_id
            if self.allowed_connections(
                predictors_node=start_node_id,
                dependents_node=end_node_id,
                all_nodes=self.canvas.nodes,
            ):
                new_arrow = Arrow(
                    self.canvas,
                    predictors_id=start_node_id,
                    dependents_id=end_node_id,
                    arrow_color=self.arrow_color,
                )

                self.canvas.arrows.append(new_arrow)
            else:
                self.canvas.drawing_arrow = False
                self.canvas.arrow_start_node = None
                if self.canvas.temporary_arrow is not None:
                    self.canvas.delete(self.canvas.temporary_arrow)
                    self.canvas.temporary_arrow = None
                tk.messagebox.showerror(
                    title="Connection not allowed",
                    message="The connection you selected is not allowed.",
                )
        for nd in self.canvas.nodes:
            if self.canvas.drawing_arrow:
                if nd.node_id == start_node_id:
                    nd.dependents_arrow_id.append(new_arrow.id)
                if nd.node_id == end_node_id:
                    nd.predictors_arrow_id.append(new_arrow.id)
        self.canvas.drawing_arrow = False
        self.canvas.arrow_start_node = None
        if self.canvas.temporary_arrow is not None:
            self.canvas.delete(self.canvas.temporary_arrow)
            self.canvas.temporary_arrow = None

    def save(self) -> dict[str, str]:
        """
        Save the node to a dictionary that allows reproducing the node.

        Returns:
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
            "position": self.canvas.coords(self.node_id),
            "predictors": predictor_nodes,
            "dependents": dependent_nodes,
        }

        return node_dict

    def get_line_intersection(self, line_coords: list[float]) -> list[float]:
        """In order to draw an arrow between two nodes, we have to find out where the arrow has to end. In edno, arrows are always drawn from the center of one form to the center of another form. This method is used to find the intersection point of a line that goes through both centers with the the outline of the shape. It is given the coordinates of the line_coords and should return the coordinates of the intersection point."""
        # the polygon is made up of single lines. The following is inefficient, but simple: We check, for each line, if it intersects with the line_coords and if the intersection point is between the two points of the polygon line. If so, we return the intersection point.
        min_dist = inf
        intersection = None

        # each polygon line is made up of two points. In the polygon points,
        # these are following the pattern [x1, y1, x2, y2, ...]. To simplify the
        # point selection, we convert the list to a list of lists, where each sublist
        # represents a single point
        center = self.get_location()
        text_bbox = self.canvas.bbox(self.node_id)
        width = 1.5 * (text_bbox[2] - text_bbox[0])
        height = 2 * (text_bbox[3] - text_bbox[1])
        polygon_points = get_polygon_points(
            x=center[0],
            y=center[1],
            height=height,
            width=width,
            sides=self.polygon_sides,
        )
        poly_points = []
        for i in range(0, len(polygon_points), 2):
            poly_points.append(polygon_points[i : (i + 2)])

        def point_distance(x1, y1, x2, y2):
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        # now we can check for each combination of subsequent points if the line
        # between the points intersects the line_coords.
        for i in range(len(poly_points)):
            # using modulo to also take the line from the last point to the
            # first point into account:
            current_line = poly_points[i].copy()
            current_line.extend(poly_points[(i + 1) % len(poly_points)])
            intersection_point = get_line_line_intersection(line_coords, current_line)
            if intersection_point is None:
                continue
            # if the intersection point i is between the two points of the polygon p1 and p2, then the
            # length p1-p2 is identical to p1-intersection + intersection-p2
            if (
                abs(
                    point_distance(*current_line)
                    - (
                        point_distance(*current_line[:2], *intersection_point)
                        + point_distance(*current_line[2:], *intersection_point)
                    )
                )
                < 0.0001
            ):
                current_dist = point_distance(*line_coords[:2], *intersection_point)
                if current_dist < min_dist:
                    min_dist = current_dist
                    intersection = intersection_point
        if intersection is None:
            return line_coords[2:]
        return intersection

    def delete(self) -> None:
        """
        Delete the node from the canvas
        """
        self.canvas.delete(self.node_id)
        self.canvas.delete(self.shape_id)
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
        if self.linked_objects is not None:
            self.linked_objects.delete()


def PolyNode_factory(polygon_sides: int) -> Callable:
    """Creates a PolyNode with a specific number of sides.

    Args:
        polygon_sides (int): Number of sides of the polygon.

    Returns:
        Callable: Class that creates a PolyNode with the specified number of sides.
    """

    class PolyNodeSubClass(PolyNode):
        def __init__(
            self,
            canvas: "EdnoCanvas",
            x: int | float,
            y: int | float,
            label: str,
            font: tuple[str, int] = ("Arial", 9),
            font_color: str = "#000000",
            node_color: str = "#faf9f6",
            arrow_color: str = "#000000",
            allowed_connections: Callable = allow_all_connections,
            NodeMenuClass: Callable = NodeMenu,
            linked_objects: Any = None,
        ) -> None:
            """Initializes a basic node instance.

            Args:
                canvas (EdnoCanvas): The tkinter canvas object where the node box will be drawn.
                x (int | float): The x-coordinate of the node's position.
                y (int | float): The y-coordinate of the node's position.
                label (str): The label to be displayed inside the node.
                font (tuple[str, int], optional): The font of the text (default is ("Arial", 12)).
                font_color (str, optional): The color of the text. Defaults to "#000000".
                node_color (str, optional): The color of the text box (default is #faf9f6).
                arrow_color (str, optional): The color of the arrows. Defaults to "#000000".
                allowed_connections (Callable, optional): this function will be called every time a user tries creating a new node. The function should return False if the user tries to create a non-allowed connection. Defaults to allow_all_connections. See allow_all_connections for the signature of these functions.
                NodeMenuClass (Callable, optional): The right-click menu for the node. Defaults to NodeMenu.
                linked_objects (Any, optional): linked_objects allows linking other objects to the node. This could, for example, be an R squared value that is shown above the node. These objects must implement the following methods: move(delta_x, delta_y), delete(), hide(), show(). Defaults to None.
            """
            super().__init__(
                canvas=canvas,
                x=x,
                y=y,
                label=label,
                font=font,
                font_color=font_color,
                polygon_sides=polygon_sides,
                node_color=node_color,
                arrow_color=arrow_color,
                allowed_connections=allowed_connections,
                NodeMenuClass=NodeMenuClass,
                linked_objects=linked_objects,
            )

    return PolyNodeSubClass
