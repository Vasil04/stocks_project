"""Docstring, empty for now as further changes in the code are expected"""
import os
import threading
import json

import tkinter as tk
from tkinter import font
import finnhub

finnhub_client = finnhub.Client(
    api_key="cmvoki1r01qkcvkeu40gcmvoki1r01qkcvkeu410"
)
SAVED_STOCKS_FILE = "saved_stocks.json"


def on_entry_click(event):
    if entry.get() == "Enter your text here":
        entry.delete(0, tk.END)
        entry.config(fg="black")


def on_button_add_click(stock_symbol: str):
    exists = not stock_symbol not in get_saved_stocks()
    save_stock_locally(stock_symbol)
    if not exists:
        query = {}
        fetch_quote(stock_symbol, query)
        saved_stocks_count = len(get_saved_stocks())
        stock_prices[stock_symbol] = [
            {"c": query[stock_symbol]["c"], "pc": query[stock_symbol]["pc"]}
        ]
        display_saved_stock(stock_symbol, query[stock_symbol], saved_stocks_count)


def on_button_delete_click(stock_symbol: str):
    stocks = get_saved_stocks()
    stocks.remove(stock_symbol)
    save_saved_stocks_to_file(stocks)

    del stock_prices[stock_symbol]

    for widget in frame_container.winfo_children():
        widget.destroy()

    for row, stock in enumerate(stocks):
        display_saved_stock(stock, stock_prices[stock][0], row)


def save_stock_locally(stock_symbol: str):
    saved_stocks = get_saved_stocks()
    if stock_symbol not in saved_stocks:
        saved_stocks.append(stock_symbol)
        save_saved_stocks_to_file(saved_stocks)


def save_saved_stocks_to_file(saved_stocks):
    with open(SAVED_STOCKS_FILE, "w", encoding="utf-8") as file:
        json.dump(saved_stocks, file)


def fetch_quote(stock_symbol: str, query_result: dict):
    query_result[stock_symbol] = finnhub_client.quote(stock_symbol)


def load_saved_stocks():
    stocks = get_saved_stocks()
    queries = {}

    for widget in frame_container.winfo_children():
        widget.destroy()

    threads = []

    for stock in stocks:
        thread = threading.Thread(target=fetch_quote, args=(stock, queries))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for row, stock in enumerate(stocks):
        display_saved_stock(stock, queries[stock], row)
        stock_prices[stock] = [
            {"c": queries[stock]["c"], "pc": queries[stock]["pc"]}
        ]


def display_saved_stock(stock_symbol: str, stock_data: dict, row: int):
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
        command=lambda: on_button_delete_click(stock_symbol),
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


def get_saved_stocks() -> list:
    if not os.path.isfile(SAVED_STOCKS_FILE):
        with open(SAVED_STOCKS_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)
    try:
        with open(SAVED_STOCKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def create_search_result(stock_symbol: str, row: int):
    frame_temp = tk.Frame(frame_left_results)
    frame_temp.grid_columnconfigure(0, weight=1)

    label_name = tk.Label(frame_temp,
                          text=stock_symbol,
                          width=10
                          )
    label_name.grid(row=0, column=0, sticky="ew")

    empty_label3 = tk.Label(frame_temp, width=25)
    empty_label3.grid(row=0, column=1)

    label_price = tk.Label(
        frame_temp,
        text=finnhub_client.quote(stock_symbol)["c"],
        width=10
    )
    label_price.grid(row=0, column=2, sticky="ew")

    button_add = tk.Button(
        frame_temp,
        command=lambda: on_button_add_click(stock_symbol),
        text="Add",
        width=4,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_add.grid(row=0, column=3)

    frame_temp.grid(row=row, column=0, pady=5, padx=15)


def fetch_search_results(entry_text: str):
    loading_label.config(text="Loading...")

    data = finnhub_client.symbol_lookup(entry_text)
    symbols = []
    [symbols.append(symbol)
     for symbol in [entry["symbol"].split(".")[0]
                    for entry in data.get("result", [])]
     if symbol not in symbols]

    for row, symbol in enumerate(symbols):
        create_search_result(symbol, row)

    loading_label.config(text="")


def on_button_click_search():
    on_button_click_clear()
    entry_text = entry.get()
    threading.Thread(target=fetch_search_results, args=(entry_text,)).start()


def on_button_click_clear():
    for widget in frame_left_results.winfo_children():
        widget.destroy()


def update_prices():
    load_saved_stocks()
    print("Updating...")
    root.after(20000, update_prices)


def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


root = tk.Tk()
root.title("Stocks")
root.state("zoomed")


DEFAULT_TEXT = "Enter your text here"
stock_prices = {}

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
entry.bind("<FocusIn>", on_entry_click)
entry.grid(
    row=0,
    column=0,
    columnspan=2,
    padx=35,
    pady=(35, 10))

button_search = tk.Button(
    frame_left,
    command=on_button_click_search,
    text="Search",
    width=10,
    height=1,
    bg="#c4c4c4",
    fg="black",)

button_search.grid(row=0, column=2, pady=(35, 10))

button_clear = tk.Button(
    frame_left,
    command=on_button_click_clear,
    text="Clear",
    width=10,
    height=1,
    bg="#c4c4c4",
    fg="black",)

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

frame_container.bind("<Configure>", on_configure)

# load_saved_stocks()

# RIGHT FRAME-----------------------------------

# ----------------------------------------------
update_prices()

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

root.mainloop()
