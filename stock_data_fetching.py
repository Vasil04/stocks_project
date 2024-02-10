import os
import threading
import json

import tkinter as tk
import finnhub

import click_events
import gui

finnhub_client = finnhub.Client(
    api_key="cmvoki1r01qkcvkeu40gcmvoki1r01qkcvkeu410"
)
STOCK_PRICES = {}
SAVED_STOCKS_FILE = "saved_stocks.json"


def save_saved_stocks_to_file(saved_stocks):
    with open(SAVED_STOCKS_FILE, "w", encoding="utf-8") as file:
        json.dump(saved_stocks, file)


def save_stock_locally(stock_symbol: str):
    saved_stocks = get_saved_stocks()
    if stock_symbol not in saved_stocks:
        saved_stocks.append(stock_symbol)
        save_saved_stocks_to_file(saved_stocks)


def get_saved_stocks() -> list:
    if not os.path.isfile(SAVED_STOCKS_FILE):
        with open(SAVED_STOCKS_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)
    try:
        with open(SAVED_STOCKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def fetch_quote(stock_symbol: str, query_result: dict) -> None:
    query_result[stock_symbol] = finnhub_client.quote(stock_symbol)


def load_saved_stocks(frame_container: tk.Frame) -> None:
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
        gui.display_saved_stock(frame_container, stock, queries[stock], row)
        STOCK_PRICES[stock] = [
            {"c": queries[stock]["c"], "pc": queries[stock]["pc"]}
        ]


def update_prices(root: tk.Tk, frame_container: tk.Frame) -> None:
    load_saved_stocks(frame_container)
    print("Updating...")
    root.after(20000, lambda: update_prices(root, frame_container))


def fetch_search_results(entry_text: str,
                         loading_label: tk.Label,
                         frame_left_results: tk.Frame,
                         frame_container: tk.Frame) -> None:
    loading_label.config(text="Loading...")

    data = finnhub_client.symbol_lookup(entry_text)
    symbols = []
    [symbols.append(symbol)
     for symbol in [entry["symbol"].split(".")[0]
                    for entry in data.get("result", [])]
     if symbol not in symbols]

    for row, symbol in enumerate(symbols):
        create_search_result(symbol, row, frame_left_results, frame_container)

    loading_label.config(text="")


def create_search_result(stock_symbol: str,
                         row: int,
                         frame_left_results: tk.Frame,
                         frame_container: tk.Frame) -> None:
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
        command=lambda: click_events.on_button_add_click(stock_symbol, frame_container),
        text="Add",
        width=4,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_add.grid(row=0, column=3)

    frame_temp.grid(row=row, column=0, pady=5, padx=15)
