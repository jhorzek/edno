import tkinter as tk
import customtkinter as ctk
import math
from typing import Any


def get_polygon_points(
    x: float,
    y: float,
    sides: int,
    width: float,
    height: float,
) -> list[int]:
    """
    Get the points of a polygon with a given number of sides, radius, and center.

    Args:
        x (float): The x-coordinate of the center of the polygon.
        y (float): The y-coordinate of the center of the polygon.
        sides (int): The number of sides of the polygon.
        width (float): The width of the polygon.
        height (float): The height of the polygon.

    Returns:
        list[int]: A list of the x and y coordinates of the points of the polygon.
    """
    # We want all points of the polygon to be outside of the ellipse defined by the width and height.
    # This ensures that the text will fit in the polygon. The implementation is adapted from
    # user2554330 at
    # https://stackoverflow.com/questions/76221986/how-to-approximate-an-ellipse-from-the-exterior

    if sides < 3:
        raise ValueError("A polygon must have at least 3 sides.")

    if sides == 4:
        # A rectangle is a special case, as we can calculate the points directly.
        return [
            x - 0.5 * width,
            y - 0.5 * height,
            x + 0.5 * width,
            y - 0.5 * height,
            x + 0.5 * width,
            y + 0.5 * height,
            x - 0.5 * width,
            y + 0.5 * height,
        ]

    if sides % 2 == 1:
        angle = 90
    else:
        angle = 0.0001
    # the algorithm uses one element more than there are sides
    sides += 1
    angle = math.radians(angle)
    theta = [(i * 2 * math.pi / (sides - 1)) for i in range(sides)]
    theta.append(0.0)

    slopes = [
        (
            -0.5 * height * math.sin(th) * math.sin(angle)
            + 0.5 * width * math.cos(th) * math.cos(angle)
        )
        / (
            -0.5 * height * math.sin(th) * math.cos(angle)
            - 0.5 * width * math.cos(th) * math.sin(angle)
        )
        for th in theta
    ]

    crds_0 = [
        0.5 * height * math.cos(th) * math.cos(angle)
        - 0.5 * width * math.sin(th) * math.sin(angle)
        + x
        for th in theta
    ]
    crds_1 = [
        0.5 * height * math.cos(th) * math.sin(angle)
        + 0.5 * width * math.sin(th) * math.cos(angle)
        + y
        for th in theta
    ]
    intercepts = [crds_1[i] - slopes[i] * crds_0[i] for i in range(sides)]

    x_points = [
        (intercepts[i] - intercepts[i + 1]) / (slopes[i + 1] - slopes[i])
        for i in range(sides - 1)
    ]
    y_points = [slopes[i] * x_points[i] + intercepts[i] for i in range(sides - 1)]

    # combine to x1, y1, x2, y2, ...
    points = [pt[i] for i in range(sides - 1) for pt in (x_points, y_points)]
    return points


class TextBox:
    """
    A class to create and manage a text box on a canvas, which includes both text and a background shape (rectangle).
    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        x: int | float,
        y: int | float,
        label: str,
        font: tuple[str, int] = ("Arial", 9),
        font_color: str = "#000000",
        node_color: str = "#faf9f6",
        polygon_sides: int = 4,
        width_height_multiplier: tuple[int, int] = (1.5, 2),
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
            polygon_sides (int, optional): The number of sides of the polygon around the text (default is 4).
            width_height_multiplier (tuple[int, int], optional): The width and height of the polygon around the text are calculated as the width of the text times the first element of this tuple and the height of the text times the second element of this tuple. Defaults to (1.5, 2).
            linked_objects (Any, optional): linked_objects allows linking other objects to the node. This could, for example, be an R squared value that is shown above the node. These objects must implement the following methods: move(delta_x, delta_y), delete(), hide(), show(). Defaults to None.
        """
        self.canvas = canvas
        self.label = label
        self.width_height_multiplier = width_height_multiplier
        self.node_id = self.create_text(x, y, font=font, font_color=font_color)
        self.node_color = node_color
        self.polygon_sides = polygon_sides
        self.shape_id = self.create_shape()
        self.linked_objects = linked_objects

    def create_text(
        self, x: int, y: int, font: tuple[str, int], font_color: str
    ) -> int:

        id = self.canvas.create_text(
            x, y, text=self.label, font=font, tags="text_field", fill=font_color
        )
        return id

    def create_shape(self) -> int:
        """Create a polygon around the text.

        Returns:
            int: The id of the shape on the canvas.
        """
        center = self.get_location()
        text_bbox = self.canvas.bbox(self.node_id)
        width = self.width_height_multiplier[0] * (text_bbox[2] - text_bbox[0])
        height = self.width_height_multiplier[1] * (text_bbox[3] - text_bbox[1])
        polygon_points = get_polygon_points(
            x=center[0],
            y=center[1],
            height=height,
            width=width,
            sides=self.polygon_sides,
        )

        id = self.canvas.create_polygon(
            polygon_points, fill=self.node_color, tags="shape"
        )
        self.canvas.tag_lower(id, self.node_id)
        return id

    def get_label(self) -> str:
        return self.label

    def move(self, delta_x: float, delta_y: float):
        """Moves the text and shape of the node by the specified amounts.

        Args:
            delta_x (float): The change along the x-axis.
            delta_y (float): The change along the y-axis.
        """
        self.move_text(delta_x, delta_y)
        self.move_shape(delta_x, delta_y)
        self.move_linked_objects(delta_x, delta_y)

    def move_linked_objects(self, delta_x: float, delta_y: float):
        """Moves objects linked to the text box by the specified amounts.

        Args:
            delta_x (float): The change along the x-axis.
            delta_y (float): The change along the y-axis.
        """
        if self.linked_objects is not None:
            self.linked_objects.move(delta_x, delta_y)

    def move_text(self, delta_x: float, delta_y: float):
        """Moves the text box by the specified amounts.

        Args:
            delta_x (float): The change along the x-axis.
            delta_y (float): The change along the y-axis.
        """
        self.canvas.move(self.node_id, delta_x, delta_y)

    def move_shape(self, delta_x: float, delta_y: float):
        """Moves the shape by the specified amounts.

        Args:
            delta_x (float): The change along the x-axis.
            delta_y (float): The change along the y-axis.
        """
        self.canvas.move(self.shape_id, delta_x, delta_y)

    def move_to(self, x: int | float, y: int | float) -> None:
        """Moves the text box to the specified location.

        Args:
            x (int | float): The location on the x-axis.
            y (int | float): The location on the y-axis.
        """
        current_location = self.get_location()
        delta_x = x - current_location[0]
        delta_y = y - current_location[1]
        self.move(delta_x, delta_y)
        if self.linked_objects is not None:
            self.linked_objects.move(delta_x, delta_y)

    def delete(self) -> None:
        """Deletes the text box from the canvas."""
        self.canvas.delete(self.node_id)
        self.canvas.delete(self.shape_id)
        if self.linked_objects is not None:
            self.linked_objects.delete()

    def set_label(self, label: str, font: tuple[str, int] = ("Arial", 9)) -> None:
        """
        Sets the label of the text box and updates its appearance.

        Args:
            label (str): The new text to display.
            font (tuple[str, int]): The font of the text (default is ("Arial", 12)).
        """
        self.label = label
        self.canvas.itemconfig(self.node_id, text=self.label, font=font)
        self.show()
        # update box
        self.update_shape()

    def update_shape(self) -> None:
        # update box
        """Updates the shape around the text. This has to be implemented for all nodes with shapes."""
        center = self.get_location()
        text_bbox = self.canvas.bbox(self.node_id)
        if text_bbox is None:
            # happens if label = ""
            return
        width = self.width_height_multiplier[0] * (text_bbox[2] - text_bbox[0])
        height = self.width_height_multiplier[1] * (text_bbox[3] - text_bbox[1])
        polygon_points = get_polygon_points(
            x=center[0],
            y=center[1],
            height=height,
            width=width,
            sides=self.polygon_sides,
        )
        self.canvas.coords(self.shape_id, polygon_points)

    def hide_text(self) -> None:
        """Hides the text in the text box."""
        self.canvas.itemconfigure(self.node_id, state="hidden")

    def show_text(self) -> None:
        """Shows the text in the text box."""
        self.canvas.itemconfigure(self.node_id, state="normal")

    def hide_shape(self) -> None:
        """Hides the background shape of the text box."""
        self.canvas.itemconfigure(self.shape_id, state="hidden")

    def show_shape(self) -> None:
        """Shows the background shape of the text box."""
        self.canvas.itemconfigure(self.shape_id, state="normal")

    def hide(self) -> None:
        """Hides both the text and the background shape of the text box."""
        self.hide_text()
        self.hide_shape()
        if self.linked_objects is not None:
            self.linked_objects.hide()

    def show(self) -> None:
        """Shows both the text and the background shape of the text box."""
        self.show_text()
        self.show_shape()
        if self.linked_objects is not None:
            self.linked_objects.show()

    def get_location(self) -> list[float]:
        """
        Gets the coordinates of the text box.

        Returns:
            A list containing the x and y coordinates of the text box.
        """
        return self.canvas.coords(self.node_id)

    def distance(self, other_node: "TextBox") -> dict[str, float]:
        """
        Calculates the distance between two nodes.

        Args:
            other_node (Node): The other node to calculate the distance to.

        Returns:
            A dictionary with the keys x_dist and y_dist representing the distance along the x and y axes, respectively.
        """
        p1 = self.get_location()
        p2 = other_node.get_location()

        return {"x_dist": (p1[0] - p2[0]), "y_dist": (p1[1] - p2[1])}
