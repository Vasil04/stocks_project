import tkinter as tk
from tkinter import font

import click_events
import stock_data_fetching

DEFAULT_TEXT = "Enter your text here"


def on_configure(event: tk.Event, canvas: tk.Canvas) -> None:
    canvas.configure(scrollregion=canvas.bbox("all"))


def display_saved_stock(frame_container: tk.Frame,
                        stock_symbol,
                        stock_data: dict,
                        row: int) -> None:
    frame_stock = tk.Frame(
        frame_container,
        highlightbackground="black",
        highlightthickness=1
    )
    frame_stock.grid_columnconfigure(0, weight=1)

    label_symbol = tk.Label(frame_stock, text=stock_symbol, width=10)
    label_symbol.grid(row=0, column=0, sticky="ew")

    empty_label4 = tk.Label(frame_stock, width=25)
    empty_label4.grid(row=0, column=1)

    label_price = tk.Label(frame_stock, text=stock_data["c"], width=10)

    button_delete = tk.Button(
        frame_stock,
        command=lambda: click_events.on_button_delete_click(stock_symbol, frame_container),
        text="Delete",
        width=6,
        height=1,
        bg="#e32245",
        fg="white", )
    button_delete.grid(row=1, column=2, pady=10)

    if stock_data["c"] > stock_data["pc"]:
        label_price.config(fg="green")
    elif stock_data["c"] < stock_data["pc"]:
        label_price.config(fg="red")

    label_price.grid(row=0, column=2, sticky="ew")

    frame_stock.grid(row=row, column=0, pady=(0, 5))


def setup_gui(root: tk.Tk) -> None:
    frame_container_grande = tk.Frame(root)
    frame_container_grande.grid(row=0, column=0, sticky="nsew")

    frame_left = tk.Frame(frame_container_grande)
    frame_left_results = tk.Frame(frame_left)

    frame_mid = tk.Frame(frame_container_grande)
    frame_mid_saved_stocks = tk.Frame(frame_mid)

    frame_right = tk.Frame(frame_container_grande)
    # LEFT FRAME---------------------------------------
    entry = tk.Entry(
        frame_left,
        width=60,
        fg="grey")

    entry.insert(0, DEFAULT_TEXT)
    entry.bind("<FocusIn>", lambda event: click_events.on_entry_click(event, entry))
    entry.grid(
        row=0,
        column=0,
        columnspan=2,
        padx=35,
        pady=(35, 10))

    button_search = tk.Button(
        frame_left,
        command=lambda: click_events.on_button_click_search(entry.get(),
                                                            frame_left_results,
                                                            loading_label,
                                                            frame_container),
        text="Search",
        width=10,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_search.grid(row=0, column=2, pady=(35, 10))

    button_clear = tk.Button(
        frame_left,
        command=lambda: click_events.on_button_click_clear(frame_left_results),
        text="Clear",
        width=10,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_clear.grid(row=1, column=2, pady=(5, 10))

    loading_label = tk.Label(frame_left, text="", bg=frame_left.cget("bg"))
    loading_label.grid(row=1, column=0, pady=10)

    frame_left_results.grid(row=2, column=0)

    # MIDDLE FRAME--------------------------------------
    times_font = font.Font(family="Times", size=20, slant="italic")

    label_header = tk.Label(frame_mid, text="My stocks:",
                            bg="lightgreen", font=times_font)
    label_header.grid(row=0, column=0)

    frame_mid_saved_stocks.grid(row=1, column=0,
                                pady=(20, 0), sticky="nsew")

    canvas = tk.Canvas(frame_mid_saved_stocks)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar = tk.Scrollbar(
        frame_mid_saved_stocks,
        orient=tk.VERTICAL,
        command=canvas.yview
    )
    scrollbar.grid(row=0, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)

    frame_container = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_container, anchor=tk.NW)

    frame_container.bind("<Configure>", lambda event: on_configure(event, canvas))

    # load_saved_stocks()

    # RIGHT FRAME-----------------------------------

    # ----------------------------------------------
    stock_data_fetching.update_prices(root, frame_container)

    frame_left.grid(row=0, column=0, stick="nsew")

    empty_label1 = tk.Label(frame_container_grande, width=10)
    empty_label1.grid(row=0, column=1)

    frame_mid.grid(row=0, column=2, sticky="nsew")

    empty_label2 = tk.Label(frame_container_grande, width=10)
    empty_label2.grid(row=0, column=3)

    frame_right.grid(row=0, column=4, sticky="nsew")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    frame_container_grande.grid_rowconfigure(0, weight=1)
    # frame_container_grande.grid_columnconfigure(0, weight=1)

    frame_mid.grid_rowconfigure(1, weight=1)
    frame_mid_saved_stocks.grid_rowconfigure(0, weight=1)