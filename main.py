"""Docstring, empty for now as further changes in the code are expected"""
import tkinter as tk

import gui

root = tk.Tk()
root.title("Stocks")
root.state("zoomed")

gui.setup_gui(root)

root.mainloop()
