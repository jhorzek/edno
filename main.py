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
    dag = edno.EdnoCanvas(root, node_color="lightblue")
    dag.grid(row=0, column=0, sticky="nsew")

    # add button to print the connections
    def print_connections():
        print(dag.get_connections())

    button = ctk.CTkButton(root, text="Print connections", command=print_connections)
    button.grid(row=0, column=1, sticky="new")

    # add button to print the nodes
    def print_nodes():
        print(dag.get_node_connections())

    button = ctk.CTkButton(root, text="Print nodes", command=print_nodes)
    button.grid(row=1, column=1, sticky="new")

    root.mainloop()
