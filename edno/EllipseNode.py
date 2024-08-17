from .PolyNode import PolyNode, allow_all_connections, NodeMenu, create_label
from typing import Any, Callable


class EllipseNode(PolyNode):
    """
    A class to create and manage a node on a canvas. This class creates an ellipse around the node label.
    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        x: int | float,
        y: int | float,
        label: str,
        font: tuple[str, int] = ("Arial", 9),
        font_color: str = "#000000",
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
            node_color=node_color,
            arrow_color=arrow_color,
            allowed_connections=allowed_connections,
            NodeMenuClass=NodeMenuClass,
            linked_objects=linked_objects,
        )

    def create_shape(self) -> int:
        """Create an ellipse around the text.

        Returns:
            int: The id of the shape on the canvas.
        """
        # For the shape, we first determine the outline of the text
        x1, y1, x2, y2 = self.canvas.bbox(self.node_id)
        height = y2 - y1
        width = x2 - x1
        id = self.canvas.create_oval(
            x1 - 0.3 * width,
            y1 - 0.5 * height,
            x2 + 0.3 * width,
            y2 + 0.5 * height,
            fill=self.node_color,
            outline=self.node_color,
            tags="shape",
        )
        self.canvas.tag_lower(id, self.node_id)
        return id

    def update_shape(self) -> None:
        # update box
        """Updates the ellipse around the text."""
        x1, y1, x2, y2 = self.canvas.bbox(self.node_id)
        height = y2 - y1
        width = x2 - x1
        id = self.canvas.coords(
            self.shape_id,
            x1 - 0.3 * width,
            y1 - 0.5 * height,
            x2 + 0.3 * width,
            y2 + 0.5 * height,
        )

    def get_line_intersection(self, line_coords: list[float]) -> list[float]:
        """In order to draw an arrow between two nodes, we have to find out where the arrow has to end. In edno, arrows are always drawn from the center of one form to the center of another form. This method is used to find the intersection point of a line that goes through both centers with the the outline of the shape. It is given the coordinates of the line_coords and should return the coordinates of the intersection point."""
        ellipse_center = self.get_location()
        [s_x1, s_y1, s_x2, s_y2] = self.canvas.bbox(self.shape_id)
        ellipse_height = 0.5 * (s_x2 - s_x1)
        ellipse_width = 0.5 * (s_y2 - s_y1)

        line_start = line_coords[:2]

        h: float
        k: float
        p1: float
        p2: float
        t: float
        contact_point: list[float]

        h, k = ellipse_center
        p1, p2 = line_start

        div = (
            (ellipse_height**2) * ((k - p2) ** 2) + (ellipse_width**2) * (h - p1) ** 2
        ) ** 0.5

        if abs(div) < 1e-5:
            div = 1e-5
        t = (ellipse_height * ellipse_width) / div
        contact_point = [h + t * (p1 - h), k + t * (p2 - k)]

        return contact_point
