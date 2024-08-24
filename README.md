# edno - **Ed**ges and **No**des using tkinter

Edno is a tkinter widget for basic directed graphs. The objective is to provide a simple to integrate framework for defining path models, such as linear regressions, path analysis, and structural equation models. Edno builds on tkinter's Canvas as well as customtkinter.

## Example

To define a minimal application with edno, first install the package. Edno can then be added to a CTk root as follows:

```{python}
root = ttk.Window(themename="darkly")
root.geometry("1000x850")
# initialize a grid with two columns and one row
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)
root.grid_rowconfigure(0, weight=1)

# We can now initialize the actual canvas on which we 
# will draw the arrow. Below, we are also changing some default arguments
# to make the canvas a bit more appealing and in-line with the ttkbootstrap
# theme.
dag = edno.EdnoCanvas(
    root,
    # we change the color of all text elements:
    font_color=root.style.colors.fg,
    # and we change the color of the nodes. "default"
    # is the default color of the nodes, "allowed"
    # is the color that is shown when connecting nodes and
    # the connection is allowed, and disallowed otherwise.
    node_color={
        "default": root.style.colors.primary,
        "allowed": root.style.colors.success,
        "not allowed": root.style.colors.danger,
    },
    # finally, we adapt the arrow color:
    arrow_color=root.style.colors.fg,
)
# add the canvas to our window:
dag.grid(column=0, row=0, sticky="nsew")

# With the elements above, we can already manipulate the canvas 
# and build our model. The following two buttons can be used to
# look under the hood and see how we could later on use the nodes
# and connections to define our model.

# Frame to combine buttons
frame = tk.Frame(root)
frame.grid(column=1, row=0, sticky="nsew")
frame.grid_rowconfigure(0, weight=0)
frame.grid_rowconfigure(1, weight=0)

# add button to print the connections
def print_connections():
    print(dag.get_connections())

bt_connections = ttk.Button(
    frame, text="Print connections", command=print_connections
)

# add button to print the nodes
def print_nodes():
    print(dag.get_node_connections())

bt_nodes = ttk.Button(frame, text="Print nodes", command=print_nodes)

bt_connections.grid(row=0, column=0, sticky="new", pady=5)
bt_nodes.grid(row=1, column=0, sticky="new", pady=5)

# start the app:
root.mainloop()
```
Note that the main screen will be empty. Right-clicking allows adding nodes:

![](assets/Add_Nodes.png)

Right clicking on nodes allows adding paths:

![](assets/Add_Path.png)

Nodes can be moved around and the canvas supports rudimentary zooming:

![](assets/node_movement.gif)

Finally, there is a limited implementation of snapping: When nodes are horizontally or vertically closely aligned, they snap into perfect alignment.