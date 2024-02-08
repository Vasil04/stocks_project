import tkinter as tk
from tkinter import font
import finnhub
import threading
import json
import os


finnhub_client = finnhub.Client(api_key="cmvoki1r01qkcvkeu40gcmvoki1r01qkcvkeu410")
base_url = "https://finnhub.io/api/v1"
saved_stocks_file = "saved_stocks.json"


def on_entry_click(event):
    if entry.get() == "Enter your text here":
        entry.delete(0, tk.END)
        entry.config(fg='black')


def on_button_add_click(symbol: str):
    exists = False if symbol not in get_saved_stocks() else True
    save_stock_locally(symbol)
    if not exists:
        query = {}
        fetch_quote(symbol, query)
        length = len(get_saved_stocks())
        display_saved_stocks(symbol, query[symbol]["c"], query[symbol]["pc"],length)


def on_button_delete_click(symbol: str):
    pass


def save_stock_locally(symbol: str):
    saved_stocks = get_saved_stocks()
    if symbol not in saved_stocks:
        saved_stocks.append(symbol)
        save_saved_stocks(saved_stocks)


def save_saved_stocks(saved_stocks):
    with open(saved_stocks_file, "w") as file:
        json.dump(saved_stocks, file)


def fetch_quote(stock: str, query_result: dict):
    query_result[stock] = finnhub_client.quote(stock)


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

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # print(queries)
    for index, stock in enumerate(stocks):
        display_saved_stocks(stock, queries[stock]["c"], queries[stock]["pc"], index)


def display_saved_stocks(symbol: str, current_price: float, last_price: float, row: int):
    frame_stock = tk.Frame(frame_container)
    frame_stock.grid_columnconfigure(0, weight=1)

    label_symbol = tk.Label(frame_stock, text=symbol, width=10)
    label_symbol.grid(row=0, column=0, sticky="ew")

    empty_label4 = tk.Label(frame_stock, width=25)
    empty_label4.grid(row=0, column=1)

    label_price = tk.Label(frame_stock, text=current_price, width=10)

    button_delete = tk.Button(
        frame_stock,
        command=lambda: on_button_delete_click(symbol),
        text="Delete",
        width=6,
        height=1,
        bg="#e32245",
        fg="white", )
    button_delete.grid(row=1, column=2, pady=10)

    if current_price > last_price:
        label_price.config(fg="green")
    elif current_price < last_price:
        label_price.config(fg="red")

    label_price.grid(row=0, column=2, sticky="ew")

    frame_stock.grid(row=row, column=0)


def get_saved_stocks():
    if not os.path.isfile(saved_stocks_file):
        with open(saved_stocks_file, "w") as file:
            json.dump([], file)
    try:
        with open(saved_stocks_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def create_search_result(symbol: str, row: int):
    frame_temp = tk.Frame(frameL_results)
    frame_temp.grid_columnconfigure(0, weight=1)

    label_name = tk.Label(frame_temp, text=symbol, width=10)
    label_name.grid(row=0, column=0, sticky="ew")

    empty_label3 = tk.Label(frame_temp, width=25)
    empty_label3.grid(row=0, column=1)

    label_price = tk.Label(frame_temp, text=finnhub_client.quote(symbol)["c"], width=10)
    label_price.grid(row=0, column=2, sticky="ew")

    button_add = tk.Button(
        frame_temp,
        command=lambda: on_button_add_click(symbol),
        text="Add",
        width=4,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_add.grid(row=0, column=3)

    frame_temp.grid(row=row, column=0, pady=5, padx=15)


def fetch_search_results(entry_text):
    loading_label.config(text="Loading...")

    data = finnhub_client.symbol_lookup(entry_text)
    symbols = []
    [symbols.append(symbol) for symbol in [entry['symbol'].split('.')[0] for entry in data.get('result', [])] if
     symbol not in symbols]
    row = 0
    for symbol in symbols:
        create_search_result(symbol, row)
        row += 1
    loading_label.config(text="")


def on_button_click_search():
    on_button_click_clear()
    entry_text = entry.get()
    threading.Thread(target=fetch_search_results, args=(entry_text,)).start()


def on_button_click_clear():
    for widget in frameL_results.winfo_children():
        widget.destroy()


def update_prices():
    load_saved_stocks()
    print("Updating...")
    root.after(20000, update_prices)


def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


root = tk.Tk()
root.title("Stocks")
root.state('zoomed')


default_text = "Enter your text here"

frame_container_grande = tk.Frame(root)
frame_container_grande.grid(row=0, column=0, sticky="nsew")

frameL = tk.Frame(frame_container_grande)
frameL_results = tk.Frame(frameL)

frameM = tk.Frame(frame_container_grande)
frameM_saved_stocks = tk.Frame(frameM)

frameR = tk.Frame(frame_container_grande)

# LEFT FRAME------------------------------------------------------------------------------------
entry = tk.Entry(
    frameL,
    width=60,
    fg="grey")

entry.insert(0, default_text)
entry.bind('<FocusIn>', on_entry_click)
entry.grid(
    row=0,
    column=0,
    columnspan=2,
    padx=35,
    pady=(35, 10))

button_search = tk.Button(
    frameL,
    command=on_button_click_search,
    text="Search",
    width=10,
    height=1,
    bg="#c4c4c4",
    fg="black",)

button_search.grid(row=0, column=2, pady=(35, 10))

button_clear = tk.Button(
    frameL,
    command=on_button_click_clear,
    text="Clear",
    width=10,
    height=1,
    bg="#c4c4c4",
    fg="black",)

button_clear.grid(row=1, column=2, pady=(5, 10))

loading_label = tk.Label(frameL, text="", bg=frameL.cget("bg"))
loading_label.grid(row=1, column=0, pady=10)

frameL_results.grid(row=2, column=0)

# MIDDLE FRAME------------------------------------------------------------------------------------
times_font = font.Font(family='Times', size=20, slant='italic')

label1 = tk.Label(frameM, text="My stocks:", bg="lightgreen", font=times_font)
label1.grid(row=0, column=0)

frameM_saved_stocks.grid(row=1, column=0, pady=(20, 0), sticky="nsew")

canvas = tk.Canvas(frameM_saved_stocks)
canvas.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(frameM_saved_stocks, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

canvas.configure(yscrollcommand=scrollbar.set)

frame_container = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_container, anchor=tk.NW)

frame_container.bind("<Configure>", on_configure)

# load_saved_stocks()

# RIGHT FRAME------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
update_prices()

frameL.grid(row=0, column=0, stick="nsew")

empty_label1 = tk.Label(frame_container_grande, width=10)
empty_label1.grid(row=0, column = 1)

frameM.grid(row=0, column=2, sticky="nsew")

empty_label2 = tk.Label(frame_container_grande, width=10)
empty_label2.grid(row=0, column = 3)

frameR.grid(row=0, column=4, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frame_container_grande.grid_rowconfigure(0, weight=1)
# frame_container_grande.grid_columnconfigure(0, weight=1)

frameM.grid_rowconfigure(1, weight=1)
frameM_saved_stocks.grid_rowconfigure(0, weight=1)

root.mainloop()
