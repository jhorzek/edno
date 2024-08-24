import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import edno

if __name__ == "__main__":

    root = ttk.Window()
    root.geometry("1000x850")
    # initialize a grid with two columns and one row
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)
    root.grid_rowconfigure(0, weight=1)
    dag = edno.EdnoCanvas(
        root,
        font_color=root.style.colors.fg,
        node_color={
            "default": root.style.colors.primary,
            "allowed": root.style.colors.success,
            "not allowed": root.style.colors.danger,
        },
        arrow_color=root.style.colors.fg,
    )
    dag.grid(column=0, row=0, sticky="nsew")

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

    root.mainloop()
