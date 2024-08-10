import tkinter as tk
from .nodes import Node
from .arrow import Arrow
import customtkinter as ctk

class EdnoCanvas(tk.Canvas):
    """
    A custom canvas widget for interactive, directed graphs.

    This canvas provides functionality for drawing nodes, arrows, scrolling, and zooming.

    Attributes
    ----------
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
    font_size : float
        The current font size for text elements in the canvas.

    Methods
    -------
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

    def __init__(self, root: ctk.CTk, 
                 form_names: dict[str, str] = {"rectangle": "rectangle",
                                                    "ellipse": "ellipse"}, 
                                                    **kwargs) -> None:
        """
        Initialize a new EdnoCanvas.

        Parameters
        ----------
        root : ctk.CTk
            The ctk.CTk root object to which the EdnoCanvas should be added.
        form_names: dict[str, str]
            Specifies what the rectangles and ellipse are called on the canvas. For example, 
            {"rectangle": "manifest", "ellipse": "latent"} specifies that the rectangles will be called manifest variables and the ellipse will be called latent variables.
        **kwargs : optional
            Additional arguments passed to ctk.CTk.

        Returns
        -------
        None
        """        
    
        super().__init__(root, kwargs)

        self.form_names = form_names

        # initialize nodes
        self.nodes: list[Node] = []
        self.arrows: list[Arrow] = []
        # the following variables are used to indicate if we are currently
        # in an arrow drawing mode. This ensures that we are not allowing
        # for moving objects, etc. while arrows are being drawn.
        self.drawing_arrow = False
        self.arrow_start_node = None
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

        self.scale_factor = 1.0

        self.font_size = 9.0

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
        self.font_size = self.font_size * factor
        for text_field in text_fields:
            font = self.itemcget(text_field, 'font').split(" ")[0]
            self.itemconfigure(text_field, font = (font, int(self.font_size)))

            #txt = canvas.itemcget(typed_value, 'text')

    def reset(self) -> None:
        """
        Reset the entire canvas by removing existing objects.
        """
        self.delete("all")
        self.nodes = []
        self.arrows = []
        self.drawing_arrow = False
        self.arrow_start_node = None
        self.context_menu = None

class CanvasContextMenu:
    """
    The context menu will allow adding new constructs, observables, etc. on right click.
    """

    def __init__(self, root: ctk.CTk, canvas: "EdnoCanvas", form_names: dict[str, str] = {"rectangle": "rectangle",
                                                    "ellipse": "ellipse"},) -> None:
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
        self.canvas_context_menu = tk.Menu(root, tearoff=0)
        self.canvas_context_menu.add_command(label=f"Add {self.form_names['ellipse']}",
                                              command=self.create_ellipse)
        self.canvas_context_menu.add_command(label=f"Add {self.form_names['ellipse']}",
                                              command=self.create_rectangle)
        
        self.canvas.bind("<Button-3>", self.show_right_click_menu)
        self.canvas.bind("<Button-1>", self.release_right_click_menu)

    def create_ellipse(self) -> None:
        """
        Creates a new ellipse node on the canvas at the position of the context menu.
        """
        self.canvas.nodes.append(Node(self.canvas,
                   label="",
                   x=self.canvas.context_menu.position[0],
                   y=self.canvas.context_menu.position[1],
                   type=self.form_names['ellipse']))
        self.canvas.context_menu = None
    
    def create_rectangle(self) -> None:
        """
        Creates a new rectangle node on the canvas at the position of the context menu.
        """
        self.canvas.nodes.append(Node(self.canvas,
                   label="",
                   x=self.canvas.context_menu.position[0],
                   y=self.canvas.context_menu.position[1],
                   type=self.form_names['rectangle']))
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
            self.canvas.context_menu.position = [event.x, event.y]

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
            for nd in self.canvas.nodes: 
                self.canvas.itemconfig(nd.shape, fill='white')
