# edno - **Ed**ges and **No**des using tkinter

Edno is a tkinter widget for basic directed graphs. The objective is to provide a simple to integrate framework for defining path models, such as linear regressions, path analysis, and structural equation models. Edno builds on tkinter's Canvas as well as customtkinter.

## Example

To define a minimal application with edno, first install the package. Edno can then be added to a CTk root as follows:

```{python}
import customtkinter as ctk
import edno

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.geometry("1000x850")
    # initialize a grid with two columns and one row
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)
    root.grid_rowconfigure(0, weight=1)
    dag = edno.EdnoCanvas(root)
    dag.grid(column=0, row=0, sticky="nsew")

    # Frame to combine buttons
    frame = ctk.CTkFrame(root)
    frame.grid(column=1, row=0, sticky="nsew")
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=0)

    # add button to print the connections
    def print_connections():
        print(dag.get_connections())

    bt_connections = ctk.CTkButton(
        frame, text="Print connections", command=print_connections
    )

    # add button to print the nodes
    def print_nodes():
        print(dag.get_node_connections())

    bt_nodes = ctk.CTkButton(frame, text="Print nodes", command=print_nodes)

    bt_connections.grid(row=0, column=0, sticky="new", pady=5)
    bt_nodes.grid(row=1, column=0, sticky="new", pady=5)

    root.mainloop()
```
Note that the main screen will be empty. Right-clicking allows adding nodes:

![](assets/Add_Nodes.png)

Right clicking on nodes allows adding paths:

![](assets/Add_Path.png)

Nodes can be moved around and the canvas supports rudimentary zooming:

![](assets/node_movement.gif)

Finally, there is a limited implementation of snapping: When nodes are horizontally or vertically closely aligned, they snap into perfect alignment.