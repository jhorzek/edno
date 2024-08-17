import tkinter as tk
import customtkinter as ctk
import math
from typing import Any


def get_polygon_points(
    x: float, y: float, sides: int, radius: float, magins: float = 1.3
) -> list[int]:
    """
    Get the points of a polygon with a given number of sides, radius, and center.

    Args:
        x (float): The x-coordinate of the center of the polygon.
        y (float): The y-coordinate of the center of the polygon.
        sides (int): The number of sides of the polygon.
        radius (float): The radius of the polygon.
        magins (float): The polygon is based on a circle. This parameter allows to increase the radius of the circle to make sure that the text fits. Defaults to 5.

    Returns:
        list[int]: A list of the x and y coordinates of the points of the polygon.
    """
    # https://math.stackexchange.com/questions/117164/calculate-coordinates-of-a-regular-polygon
    if sides < 3:
        raise ValueError("A polygon must have at least 3 sides.")

    radius = radius * magins

    points = []
    if sides == 3:
        rotate = math.radians(180)
    elif sides == 4:
        rotate = math.radians(45)
    else:
        rotate = math.radians(0)
    for i in range(sides):
        angle = (2 * math.pi * i) / sides + rotate
        points.extend(
            [
                x + (radius) * math.sin(angle),
                y + (radius) * math.cos(angle),
            ]
        )
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
            linked_objects (Any, optional): linked_objects allows linking other objects to the node. This could, for example, be an R squared value that is shown above the node. These objects must implement the following methods: move(delta_x, delta_y), delete(), hide(), show(). Defaults to None.
        """
        self.canvas = canvas
        self.label = label
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
        width = text_bbox[2] - text_bbox[0]
        polygon_points = get_polygon_points(
            center[0], center[1], self.polygon_sides, max(width / 2, 30)
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
        width = text_bbox[2] - text_bbox[0]
        polygon_points = get_polygon_points(
            center[0], center[1], self.polygon_sides, max(width / 2, 30)
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
