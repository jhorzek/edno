import customtkinter as ctk
import tkinter as tk
from .TextBox import TextBox
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
        node_color (str, optional): The color of the estimate's background box. Defaults to "#faf9f6".
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
        node_color="#faf9f6",
        value: float | None = None,
        significance: str | None = None,
    ) -> None:

        super().__init__(
            canvas=canvas,
            x=x,
            y=y,
            label="",
            font=font,
            font_color=font_color,
            node_color=node_color,
            width_height_multiplier=(1.1, 1.1),
        )
        self.parameter_label = label
        self.value = value
        self.significance = significance
        self.update_text()

    def update_text(self) -> None:
        """Update the text shown on the canvas. This combines the label, value, and significance."""
        # Case 1: We have a parameter label and a value for the estimate:
        if (
            self.parameter_label is not None and self.parameter_label != ""
        ) and self.value is not None:
            text = f"{self.parameter_label}={self.value:.2f}{self.significance}"
        # Case 2: We have a parameter label but no value for the estimate:
        elif (
            self.parameter_label is not None or self.parameter_label != ""
        ) and self.value is None:
            text = f"{self.parameter_label}"
        # Case 3: We have no parameter label, but a value for the estimate:
        elif (
            self.parameter_label is None or self.parameter_label == ""
        ) and self.value is not None:
            text = f"{self.value:.2f}{self.significance}"
        else:
            text = ""
        self.set_label(label=text)

    def rename(self) -> None:
        """
        Change the parameter label.

        This will open a dialog in the GUI for users to rename the nodes
        """
        input = ctk.CTkInputDialog(text="Parameter label:", title="Rename Parameter")
        new_label = input.get_input()  # opens the dialog
        if (new_label is not None) and (len(new_label) > 0):
            self.parameter_label = new_label

            self.update_text()

        # close context menu
        self.canvas.context_menu = None


class Arrow:
    """Arrows connect nodes in the model. The arrow can be used to show the direction of the relationship between the nodes. The arrow can also display the estimate and significance of the relationship."""

    def __init__(
        self,
        canvas: "EdnoCanvas",
        dependents_id: int,
        predictors_id: int,
        arrow_type="directed",
        font=("Arial", 9),
        font_color: str = "#000000",
        arrow_color="#000000",
        additional_information: None | dict[Any, Any] = None,
    ) -> None:
        """Initialize an Arrow object. Note: The class expects that a line has already been added to the canvas. Given the line id, this class will add an arrow head as well as additional information (e.g., on predictors and dependents).

        Args:
            canvas (EdnoCanvas): The canvas where the arrow is drawn.
            dependents_id (int): The canvas-id of the node where the arrow has its head (the dependent)
            predictors_id (int): The canvas-id of the node that the arrow has its origin in (the predictor)
            font (tuple, optional): The font of the estimate shown on the arrow. Defaults to ("Arial", 9).
            font_color (str, optional): The color of the estimate. Defaults to "#000000".
            arrow_color (str, optional): The color of the arrow. Defaults to "#000000".
            additional_information (None | dict[Any, Any], optional): Optional additional information saved with the arrow. Defaults to None.
        """

        self.canvas = canvas
        self.font = font
        self.font_color = font_color
        self.arrow_color = arrow_color
        self.dependents_id = dependents_id
        self.predictors_id = predictors_id
        self.arrow_type = arrow_type

        # initialize arrow
        if arrow_type == "directed":
            arrow_head = tk.LAST
        elif arrow_type == "undirected":
            arrow_head = tk.NONE
        elif arrow_type == "bidirected":
            arrow_head = tk.BOTH

        if dependents_id == predictors_id:
            target_coords = self.canvas.get_node_with_id(
                dependents_id
            ).get_self_loop_coords()
            third_point = get_curved_arrow_points(target_coords[:2], target_coords[2:])
        else:
            target_coords = self.get_target_coordinates()
            third_point = []

        # draw arrow: In case of self-loops we draw a curved line
        if dependents_id == predictors_id:
            self.id = self.canvas.create_line(
                *target_coords[:2],
                *third_point,
                *target_coords[2:],
                fill=self.arrow_color,
                arrow=arrow_head,
                width=self.canvas.arrow_width,
                activefill=self.canvas.arrow_color_on_hover,
                smooth=True,
                splinesteps=50,
            )
        else:
            self.id = self.canvas.create_line(
                *target_coords,
                fill=self.arrow_color,
                arrow=arrow_head,
                width=self.canvas.arrow_width,
                activefill=self.canvas.arrow_color_on_hover,
            )

        # bidirected arrows are dotted
        if arrow_type == "bidirected":
            self.canvas.itemconfig(self.id, dash=(5, 5))

        # self.canvas.tag_lower(self.id)

        self.additional_information = additional_information
        self.add_estimate()

        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete)
        self.context_menu.add_command(label="Rename", command=self.estimate.rename)

        # Add right click menu
        self.canvas.tag_bind(self.id, "<Button-3>", self.context_menu_show)

    def get_target_coordinates(self) -> list[float]:
        """The arrow connects two nodes. This method returns the x and y coordinates of points where the arrow contacts the outline of the target nodes.

        Returns:
            list[float]: A list with x1, y1, x2, y2 coordinates.
        """
        # get intersection points of the line between the nodes with the shapes
        # get center of start and end node:
        start_node = self.canvas.get_node_with_id(self.predictors_id)
        end_node = self.canvas.get_node_with_id(self.dependents_id)

        x1, y1 = start_node.get_location()
        x2, y2 = end_node.get_location()

        # find intersection point of line between centers and the outline of the shape
        # We have to pass in the coordinates of the points in a different order for the
        # start intersection and the end intersection because the get_line_intersection
        # function will otherwise draw the arrow on the wrong side of the node.
        start_intersection = start_node.get_line_intersection([x2, y2, x1, y1])
        end_intersection = end_node.get_line_intersection([x1, y1, x2, y2])
        return start_intersection + end_intersection

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
        # in case of bidirected arrows, we have to get the center of the curved arrow
        if len(line_coord) == 6:
            # curved arrow
            return line_coord[2:4]
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
            node_color="#faf9f6",
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

    def update_position(self) -> None:
        """Update the position of the arrow. This is necessary when the nodes moves."""

        if self.dependents_id == self.predictors_id:
            target_coords = self.canvas.get_node_with_id(
                self.dependents_id
            ).get_self_loop_coords()
        else:
            target_coords = self.get_target_coordinates()

        if self.dependents_id == self.predictors_id:
            third_point = get_curved_arrow_points(target_coords[:2], target_coords[2:])
            self.canvas.coords(
                self.id,
                *target_coords[:2],
                *third_point,
                *target_coords[2:],
            )
        else:
            self.canvas.coords(
                self.id,
                *target_coords,
            )
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
        self.canvas.delete(self.estimate.delete())
        self.canvas.delete(self.id)
        self.canvas.context_menu = None
        self.canvas.arrows = [arr for arr in self.canvas.arrows if arr.id != self.id]

    def update_box(self) -> None:
        """Update the size of the estimate box"""
        self.estimate.update_shape()

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
            "arrow_type": self.arrow_type,
            "text": self.estimate.label,
            "parameter_label": self.estimate.parameter_label,
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


def get_curved_arrow_points(
    point_1: list[float], point_2: list[float], shift_upwards: float = 3000
) -> list[float]:
    """This function creates a third point between point_1 and point_2 such that a curved arrow can be drawn between the two points. The third point is located at the midpoint between point_1 and point_2 and is shifted upwards by shift_upwards pixels.

    Args:
        point_1 (list[float]): starting point of the arrow
        point_2 (list[float]): ending point of the arrow
        shift_upwards (float, optional): The distance the third point should be shifted upwards. Defaults to 20.
    """
    # get midpoint
    midpoint = [(point_1[0] + point_2[0]) / 2, (point_1[1] + point_2[1]) / 2]
    # get direction
    direction = [point_2[0] - point_1[0], point_2[1] - point_1[1]]
    arrow_length = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
    if arrow_length < 1e-5:
        arrow_length = 1e-5
    # get normal vector

    normal = [-direction[1], direction[0]]

    # normalize normal vector
    length = (normal[0] ** 2 + normal[1] ** 2) ** 0.5
    if length < 1e-5:
        length = 1e-5
    normal = [
        normal[0] / length,
        normal[1] / length,
    ]
    # get third point
    third_point = [
        midpoint[0] - min(50, (shift_upwards / arrow_length)) * normal[0],
        midpoint[1] - min(50, (shift_upwards / arrow_length)) * normal[1],
    ]
    return third_point
