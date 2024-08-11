class TextBox:
    """
    A class to create and manage a text box on a canvas, which includes both text and a background shape (rectangle or ellipse).
    """

    def __init__(
        self,
        canvas: "EdnoCanvas",
        x: int | float,
        y: int | float,
        text: str,
        font: tuple[str, int] = ("Arial", 9),
        font_color: str = "#000000",
        box_shape: str = "rectangle",
        box_color: str = "#faf9f6",
        space_around: int = 4,
    ) -> None:
        """Initializes a TextBox instance.

        Args:
            canvas (EdnoCanvas): The tkinter canvas object where the text box will be drawn.
            x (int | float): The x-coordinate of the text box's position.
            y (int | float): The y-coordinate of the text box's position.
            text (str): The text to be displayed inside the text box.
            font (tuple[str, int], optional): The font of the text (default is ("Arial", 12)).
            font_color (str, optional): The color of the text. Defaults to "#000000".
            box_shape (str, optional): The shape of the text box, either "rectangle" or "ellipse" (default is "rectangle").
            box_color (str, optional): _description_. The color of the text box (default is #faf9f6).
            space_around (int, optional): The space around the text inside the box (default is 4).
        """

        self.canvas = canvas
        self.text = text
        self.shape = box_shape
        self.space_around = space_around
        self.text_id = canvas.create_text(
            x, y, text=text, font=font, tags="text_field", fill=font_color
        )

        # For the shape, we first determine the outline of the text
        bbox = canvas.bbox(self.text_id)
        x1, y1, x2, y2 = (
            bbox[0] - space_around,
            bbox[1] - space_around,
            bbox[2] + space_around,
            bbox[3] + space_around,
        )

        if box_shape == "rectangle":
            self.shape_id = self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=box_color, outline=box_color
            )
        elif box_shape == "ellipse":
            self.shape_id = self.canvas.create_oval(
                x1, y1, x2, y2, fill=box_color, outline=box_color
            )
        else:
            raise ValueError("Shape should be rectangle or ellipse.")
        # put shape behind text
        self.canvas.tag_lower(self.shape_id, self.text_id)

    def move(self, delta_x, delta_y):
        """Moves the text box by the specified amounts.

        Args:
            delta_x (_type_): The change along the x-axis.
            delta_y (_type_): The change along the y-axis.
        """
        self.canvas.move(self.text_id, delta_x, delta_y)
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

    def delete(self) -> None:
        """Deletes the text box from the canvas."""
        self.canvas.delete(self.text_id)
        self.canvas.delete(self.shape_id)

    def set_text(self, text: str, font: tuple[str, int] = ("Arial", 9)) -> None:
        """
        Sets the text of the text box and updates its appearance.

        Args:
            text (str): The new text to display.
            font (tuple[str, int]): The font of the text (default is ("Arial", 12)).
        """
        self.text = text
        self.canvas.itemconfig(self.text_id, text=self.text, font=font)
        self.show()
        # update box
        self.update_box()

    def update_box(self) -> None:
        # update box
        """Updates the text box to fit the new text size."""
        bbox = self.canvas.bbox(self.text_id)
        x1, y1, x2, y2 = (
            bbox[0] - self.space_around,
            bbox[1] - self.space_around,
            bbox[2] + self.space_around,
            bbox[3] + self.space_around,
        )
        self.canvas.coords(self.shape_id, x1, y1, x2, y2)

    def set_color(self, color: str) -> None:
        """Sets the color of the text box.

        Args:
            color (str): The new color for the text box.
        """
        self.canvas.itemconfig(self.shape_id, text=self.text, fill=color, outline=color)

    def hide_text(self) -> None:
        """Hides the text in the text box."""
        self.canvas.itemconfigure(self.text_id, state="hidden")

    def show_text(self) -> None:
        """Shows the text in the text box."""
        self.canvas.itemconfigure(self.text_id, state="normal")

    def hide_box(self) -> None:
        """Hides the background shape of the text box."""
        self.canvas.itemconfigure(self.shape_id, state="hidden")

    def show_box(self) -> None:
        """Shows the background shape of the text box."""
        self.canvas.itemconfigure(self.shape_id, state="normal")

    def hide(self) -> None:
        """Hides both the text and the background shape of the text box."""
        self.hide_text()
        self.hide_box()

    def show(self) -> None:
        """Shows both the text and the background shape of the text box."""
        self.show_text()
        self.show_box()

    def get_location(self) -> list[float]:
        """
        Gets the coordinates of the text box.

        Returns:
            A list containing the x and y coordinates of the text box.
        """
        return self.canvas.coords(self.text_id)

    def get_outline(self) -> list[float]:
        """
        Gets the outline of the box around the text

        Returns:
            A list with the coordinates of the outlining box
        """
        return self.canvas.coords(self.shape_id)


def distance(text_box_1: TextBox, text_box_2: TextBox) -> dict[str, float]:
    """
    Calculates the distance between two text boxes.

    Args:
        text_box_1 (TextBox): The first TextBox instance.
        text_box_2 (TextBox): The second TextBox instance.

    Returns:
        A dictionary with the keys x_dist and y_dist representing the distance along the x and y axes, respectively.
    """
    p1 = text_box_1.get_location()
    p2 = text_box_2.get_location()

    return {"x_dist": (p1[0] - p2[0]), "y_dist": (p1[1] - p2[1])}
