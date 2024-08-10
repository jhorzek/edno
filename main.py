import customtkinter as ctk
import edno

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme(
        "blue"
    )

    root = ctk.CTk()
    root.geometry("1000x850")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    dag = edno.EdnoCanvas(root, node_color="lightblue")
    dag.grid(row=0, column=0, sticky="nsew")
    root.mainloop()