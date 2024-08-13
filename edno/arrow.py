import customtkinter as ctk
import tkinter as tk
from .text_box import TextBox
from typing import Any


class Estimate(TextBox):
    """
    Estimates are drawn on arrows. The typical use case would be to show the estimation result from a model (e.g., a regression) or the name of a parameter.

    Args:
        canvas (EdnoCanvas): The canvas on which the estimate will be displayed.
        label (str): The estimate label.
        x (int | float): The x-coordinate of the estimate's position.
        y (int | float): The y-coordinate of the estimate's position.
        font (tuple, optional): The font style of the estimate's text. Defaults to ("Arial", 9).
        box_color (str, optional): The color of the estimate's background box. Defaults to "#faf9f6".
        value (float | None, optional): The value of the estimate. Defaults to None.
        significance (str | None, optional): The significance of the estimate. Defaults to None.
    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        label: str,
        x: int | float,
        y: int | float,
        font=("Arial", 9),
        font_color: str = "#000000",
        box_color="#faf9f6",
        value: float | None = None,
        significance: str | None = None,
    ) -> None:

        super().__init__(
            canvas=canvas,
            x=x,
            y=y,
            text="",
            font=font,
            font_color=font_color,
            box_shape="rectangle",
            box_color=box_color,
            space_around=2,
        )
        self.label = label
        self.value = value
        self.significance = significance
        self.update_text()

    def update_text(self) -> None:
        """Update the text shown on the canvas. This combines the label, value, and significance."""
        if self.label is not None and self.label != "":
            text = f"{self.label}={self.value:.2f}{self.significance}"
        elif (self.label is not None or self.label != "") and self.value is not None:
            text = f"{self.value:.2f}{self.significance}"
        else:
            text = ""
        self.set_text(text=text)

    def rename(self) -> None:
        """
        Change the parameter label.

        This will open a dialog in the GUI for users to rename the nodes
        """
        input = ctk.CTkInputDialog(text="Parameter label:", title="Rename Parameter")
        new_label = input.get_input()  # opens the dialog
        if (new_label is not None) and (len(new_label) > 0):
            self.label = new_label

            self.update_text()

        # close context menu
        self.canvas.context_menu = None


class Arrow:
    """Arrows connect nodes in the model. The arrow can be used to show the direction of the relationship between the nodes. The arrow can also display the estimate and significance of the relationship."""

    def __init__(
        self,
        canvas: "EdnoCanvas",
        id: int,
        dependents_id: int,
        predictors_id: int,
        font=("Arial", 9),
        font_color: str = "#000000",
        arrow_color="#000000",
        additional_information: None | dict[Any, Any] = None,
    ) -> None:
        """Initialize an Arrow object. Note: The class expects that a line has already been added to the canvas. Given the line id, this class will add an arrow head as well as additional information (e.g., on predictors and dependents).

        Args:
            canvas (EdnoCanvas): The canvas where the arrow is drawn.
            id (int): The canvas-id of the arrow. This id uniquely identifies the arrow in the canvas object
            dependents_id (int): The canvas-id of the node where the arrow has its head (the dependent)
            predictors_id (int): The canvas-id of the node that the arrow has its origin in (the predictor)
            font (tuple, optional): The font of the estimate shown on the arrow. Defaults to ("Arial", 9).
            font_color (str, optional): The color of the estimate. Defaults to "#000000".
            arrow_color (str, optional): The color of the arrow. Defaults to "#000000".
            additional_information (None | dict[Any, Any], optional): Optional additional information saved with the arrow. Defaults to None.
        """

        self.canvas = canvas
        self.id = id
        self.font = font
        self.font_color = font_color
        self.arrow_color = arrow_color
        self.additional_information = additional_information
        self.add_estimate()
        self.dependents_id = dependents_id
        self.predictors_id = predictors_id
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete)
        self.context_menu.add_command(label="Rename", command=self.estimate.rename)

        self.arrow_head = ArrowHead(
            canvas=self.canvas,
            line_id=self.id,
            predictor_id=self.predictors_id,
            dependent_id=self.dependents_id,
            arrow_color=self.arrow_color,
        )
        # Add right click menu
        self.canvas.tag_bind(self.id, "<Button-3>", self.context_menu_show)

    def direction(self) -> list[float]:
        """Direction of the arrow

        Returns:
            list[float]: A list with x and y coordinates of the direction of the arrow. Not normalized.
        """
        line_coord = self.canvas.coords(self.id)
        # get direction
        return [line_coord[2] - line_coord[0], line_coord[3] - line_coord[1]]

    def length(self) -> float:
        """
        Get the length of the arrow.

        Returns:
            float: length of the arrow
        """
        line_dir = self.direction()
        # get line length
        line_len = (line_dir[0] ** 2 + line_dir[1] ** 2) ** 0.5
        return line_len

    def get_line_center(self) -> list[float]:
        """
        Compute x and y coordinates of the center of the line

        Returns:
            list[float]: A list containing the x and y coordinates of the center of the line.
        """
        line_coord = self.canvas.coords(self.id)
        # get line center
        x = line_coord[0] + 0.5 * (line_coord[2] - line_coord[0])
        y = line_coord[1] + 0.5 * (line_coord[3] - line_coord[1])

        return [x, y]

    def add_estimate(self) -> None:
        """Add a text field in the center of the line. This text field can be filled with the estimate using set_estimate."""
        # we will draw the estimate at the center of the line
        line_center = self.get_line_center()
        self.estimate = Estimate(
            canvas=self.canvas,
            x=line_center[0],
            y=line_center[1],
            label="",
            font=self.font,
            font_color=self.font_color,
            box_color="#faf9f6",
        )
        self.estimate.hide()

    def set_estimate(self, est: float, sig: str):
        """Specify the estimate and significance level for a path (arrow).

        Args:
            est (float): The estimate
            sig (str): string specifying the significance level (e.g., "*")
        """
        if est != "":
            self.estimate.value = est
            self.estimate.significance = sig
            self.estimate.update_text()
            self.estimate.show()
        else:
            self.estimate.value = None
            self.estimate.significance = None
            self.estimate.update_text()
            self.estimate.hide()

    def context_menu_show(self, event: tk.Event) -> None:
        """Show the arrows context menu on right click. This menu will allow for deleting arrows, etc.

        Args:
            event (tk.Event): Tkinter event object containing information about the location of the click.
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

    def move(
        self, delta_x1: float, delta_y1: float, delta_x2: float, delta_y2: float
    ) -> None:
        """Move the arrow in space.

        The location of a line on the canvas is given by two points: the start point [x1,y1] and
        the end point [x2,y2]. The arrow will show in the direction of the end point.
        move() adjusts both of these points.

        Args:
            delta_x1 (float): Change in x1
            delta_y1 (float): Change in y1
            delta_x2 (float): Change in x2
            delta_y2 (float): Change in y2
        """

        location = self.canvas.coords(self.id)
        self.canvas.coords(
            self.id,
            [
                location[0] + delta_x1,
                location[1] + delta_y1,
                location[2] + delta_x2,
                location[3] + delta_y2,
            ],
        )
        self.arrow_head.update()
        if self.estimate is not None:
            self.estimate.move_to(*self.get_line_center())

    def delete(self) -> None:
        """Remove the arrow from the canvas"""
        for nd in self.canvas.nodes:
            nd.dependents_arrow_id = [
                out for out in nd.dependents_arrow_id if out is not self.id
            ]
            nd.predictors_arrow_id = [
                inc for inc in nd.predictors_arrow_id if inc is not self.id
            ]
        self.canvas.delete(self.arrow_head.arrow_id)
        self.canvas.delete(self.estimate.delete())
        self.canvas.delete(self.id)
        self.canvas.context_menu = None
        self.canvas.arrows = [arr for arr in self.canvas.arrows if arr.id != self.id]

    def update_box(self) -> None:
        """Update the size of the estimate box"""
        self.estimate.update_box()

    def save(self) -> dict[str, float]:
        """
        Save the arrow to a dictionary that allows reproducing the arrow.

        Returns:
            Returns a dictionary with
            id: int
                The numeric id of the object on the canvas
            text: str
                The text shown on the canvas. Combines label, value, and significance.
            label: str
                The name of the parameter
            estimate: float
                The parameter estimate
            significance: string
                Stars indicating significance
            position: list[int]
                x and y positions of the arrow
            predictors: string
                label of the predictor
            dependents: string
                label of the of outcome
        """

        arrow_dict = {
            "id": self.id,
            "text": self.estimate.text,
            "label": self.estimate.label,
            "estimate": self.estimate.value,
            "significance": self.estimate.significance,
            "position": self.canvas.coords(self.id),
            "predictors": [
                nd for nd in self.canvas.nodes if nd.node_id == self.predictors_id
            ][0].get_label(),
            "dependents": [
                nd for nd in self.canvas.nodes if nd.node_id == self.dependents_id
            ][0].get_label(),
        }

        return arrow_dict


def find_line_ellipse_intersection(
    ellipse_center: list[float | int],
    ellipse_height: float | int,
    ellipse_width: float | int,
    line_start: list[float | int],
) -> list[float]:
    """Finds the point that is on an ellipse for a line that ends at the
    center of the ellipse.

    Args:
        ellipse_center (list[float | int]): list with x and y location of the center of the ellipse
        ellipse_height (float | int): height of ellipse
        ellipse_width (float | int): width of ellipse
        line_start (list[float | int]): list with x and y location of the meeting point of line and ellipse

    Returns:
        list[float]: _description_
    """

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


def find_segment_intersection(
    segment_1: list[float], segment_2: list[float]
) -> list[float] | None:
    """Finds the intersection point between two line segments.

    Args:
        segment_1 (list[float]): The coordinates of the first line segment in the format [x1, y1, x2, y2].
        segment_2 (list[float]): The coordinates of the second line segment in the format [x1, y1, x2, y2].

    Returns:
        list[float] | None: The intersection point coordinates [x, y] if the segments intersect, None otherwise.
    """

    [l1_x1, l1_y1, l1_x2, l1_y2] = segment_1
    [l2_x1, l2_y1, l2_x2, l2_y2] = segment_2

    # There are two divisions that might result in division by zero. We want
    # to make sure that we never divide by exactly zero
    div_1 = l1_x1 - l1_x2
    div_2 = (
        (l1_x1 - l1_x2) * (l2_y1 - l2_y2)
        + l1_y1 * (l2_x2 - l2_x1)
        + l1_y2 * (l2_x1 - l2_x2)
    )
    if div_1 == 0.0:
        # the segment is perfectly vertical. We will replace the difference with a very small value
        # as we don't need to be too precise here. Note: If we just replace the div_1, we will run
        # into an annoying issue, where the arrow jumps the the origin of the predictor. Therefore,
        # we need to actually change l1_x1
        l1_x1 = l1_x1 + 1
        div_1 = l1_x1 - l1_x2
        div_2 = (
            (l1_x1 - l1_x2) * (l2_y1 - l2_y2)
            + l1_y1 * (l2_x2 - l2_x1)
            + l1_y2 * (l2_x1 - l2_x2)
        )
    if div_2 == 0.0:
        # Here, we can just replace the div
        div_2 = 1.0
    t = (
        l1_x1 * (l2_y1 - l1_y2)
        + l1_y1 * (l1_x2 - l2_x1)
        - l1_x2 * l2_y1
        + l1_y2 * l2_x1
    ) / div_2
    r = (l1_x1 + (t - 1) * l2_x1 - t * l2_x2) / div_1

    if ((t >= 0) & (t <= 1.0)) & (abs(r) <= 1.0):
        # segments intersect!
        intersection = [l1_x1 + r * (l1_x2 - l1_x1), l1_y1 + r * (l1_y2 - l1_y1)]
        return intersection
    else:
        return None


def find_line_rectangle_intersection(
    line_coords: list[float], rectangle_coords: list[float]
) -> list[float]:
    """Finds the intersection point between a line and a rectangle.

    Assumed coords of the rectangle:
    x1, y2 ------- x2, y2
      |              |
    x1, y1 ------- x2, y1

    Args:
        line_coords (list[float]): The coordinates of the line in the format [x1, y1, x2, y2].
        rectangle_coords (list[float]): The coordinates of the rectangle in the format [x1, y1, x2, y2].

    Returns:
        list[float]: The coordinates of the intersection point in the format [x, y].
    """

    rectangle_segments = [
        [
            rectangle_coords[0],
            rectangle_coords[1],
            rectangle_coords[2],
            rectangle_coords[1],
        ],  # x1, y1 ------- x1, y2
        [
            rectangle_coords[0],
            rectangle_coords[3],
            rectangle_coords[2],
            rectangle_coords[3],
        ],  # x1, y2 ------- x2, y2
        [
            rectangle_coords[0],
            rectangle_coords[1],
            rectangle_coords[0],
            rectangle_coords[3],
        ],  # x1, y1 | x1 y2
        [
            rectangle_coords[2],
            rectangle_coords[1],
            rectangle_coords[2],
            rectangle_coords[3],
        ],  # x2, y1 | x2 y2
    ]
    for rectangle_segment in rectangle_segments:
        intersect = find_segment_intersection(line_coords, rectangle_segment)
        if intersect is not None:
            return intersect
    # if we can't find an intersection, the arrow is within the node. We will then just return the
    # location of the center of the node
    return [
        rectangle_coords[0] + 0.5 * (rectangle_coords[2] - rectangle_coords[0]),
        rectangle_coords[1] + 0.5 * (rectangle_coords[3] - rectangle_coords[1]),
    ]


class ArrowHead:
    def __init__(
        self,
        canvas: "EdnoCanvas",
        line_id: int,
        predictor_id: int,
        dependent_id: int,
        arrow_color: str = "#00000",
    ) -> None:
        """_summary_

        Args:
            canvas (EdnoCanvas): The canvas object on which the arrow will be drawn.
            line_id (int): The ID of the line associated with the arrow.
            predictor_id (int): The ID of the predictor node.
            dependent_id (int): The ID of the dependent node.
            arrow_color (str, optional): _description_. Defaults to "#00000".

        Raises:
            ValueError: If the number of predictor nodes is not equal to 1.
            ValueError: If the number of dependent nodes is not equal to 1.
        """

        self.canvas = canvas
        self.line_id = line_id
        # get the predictor and the dependent location
        self.predictor_node = [nd for nd in canvas.nodes if nd.node_id == predictor_id]
        self.dependents_node = [nd for nd in canvas.nodes if nd.node_id == dependent_id]
        if len(self.predictor_node) != 1:
            raise ValueError("Expected predictor nodes to be of length 1")

        if len(self.dependents_node) != 1:
            raise ValueError("Expected dependent nodes to be of length 1")

        # initialize
        coords = self.get_target_coords()
        self.arrow_id = self.canvas.create_polygon(
            coords,
            fill=arrow_color,
            outline=arrow_color,
            width=2,
        )
        self.canvas.tag_lower(self.arrow_id)

    def get_target_coords(self) -> list[float]:
        """Compute the target coordinates of the arrow head based on the predictor node
        and the dependent node.

        Raises:
            ValueError: Raises error if the shape of the dependent node is not ellipse or rectangle.

        Returns:
            list[float]: List with 6 coordinates for polygon
        """
        x1, y1 = self.predictor_node[0].get_location()
        # get coordinates of target shape s:
        s_center = self.dependents_node[0].get_location()
        [s_x1, s_y1, s_x2, s_y2] = self.dependents_node[0].get_outline()

        if self.dependents_node[0].shape == "ellipse":
            # we want the arrow to end at the collision point of line and
            # ellipse
            intersect = find_line_ellipse_intersection(
                ellipse_center=[s_center[0], s_center[1]],
                ellipse_height=0.5 * (s_x2 - s_x1),
                ellipse_width=0.5 * (s_y2 - s_y1),
                line_start=[x1, y1],
            )
        elif self.dependents_node[0].shape == "rectangle":
            intersect = find_line_rectangle_intersection(
                line_coords=self.canvas.coords(self.line_id),
                rectangle_coords=self.canvas.coords(self.dependents_node[0].shape_id),
            )
        else:
            raise ValueError("Expected shape of node to be ellipse or rectangle.")

        line_coord = self.canvas.coords(self.line_id)
        x = intersect[0]
        y = intersect[1]
        # get direction
        line_dir = [line_coord[2] - line_coord[0], line_coord[3] - line_coord[1]]
        # get line length
        line_len = (line_dir[0] ** 2 + line_dir[1] ** 2) ** 0.5
        if line_len == 0.0:
            line_len = 0.01
        # we want to go a few pixels in the direction of the dependents node
        # and a few pixels up/down
        x2 = x - (15 / line_len) * line_dir[0]
        y2 = y - (15 / line_len) * line_dir[1]
        up_x = [x2 - (5 / line_len) * line_dir[1], y2 + (5 / line_len) * line_dir[0]]
        down_x = [x2 + (5 / line_len) * line_dir[1], y2 - (5 / line_len) * line_dir[0]]

        return [x, y, up_x[0], up_x[1], down_x[0], down_x[1]]

    def update(self) -> None:
        """
        Update the coordinates of the arrow head. This is necessary when the line moves
        """
        coords = self.get_target_coords()
        self.canvas.coords(self.arrow_id, coords)
