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
        )
        self.parameter_label = label
        self.value = value
        self.significance = significance
        self.update_text()

    def update_text(self) -> None:
        """Update the text shown on the canvas. This combines the label, value, and significance."""
        if self.parameter_label is not None and self.parameter_label != "":
            text = f"{self.parameter_label}={self.value:.2f}{self.significance}"
        elif (
            self.parameter_label is not None or self.parameter_label != ""
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
            list[float]: List with 2 coordinates for the intersection point
        """
        # get coordinates of target shape s:
        line_coord = self.canvas.coords(self.line_id)
        intersect = self.dependents_node[0].get_line_intersection(
            line_coords=line_coord
        )

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
