import customtkinter as ctk
import edno

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme(
        "blue"
    )

    root = ctk.CTk()
    root.geometry("1000x850")
    edno.EdnoCanvas(root)
    root.mainloop()