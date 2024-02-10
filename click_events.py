import threading

import tkinter as tk

import stock_data_fetching
import gui


def on_entry_click(event: tk.Event, entry: tk.Entry) -> None:
    if entry.get() == "Enter your text here":
        entry.delete(0, tk.END)
        entry.config(fg="black")


def on_button_click_clear(frame: tk.Frame) -> None:
    for widget in frame.winfo_children():
        widget.destroy()


def on_button_click_search(entry_text: str,
                           frame: tk.Frame,
                           loading_label: tk.Label,
                           frame_container: tk.Frame) -> None:
    on_button_click_clear(frame)
    threading.Thread(target=stock_data_fetching.fetch_search_results,
                     args=(entry_text, loading_label,
                           frame, frame_container)).start()


def on_button_delete_click(stock_symbol: str, frame_container: tk.Frame) -> None:
    stocks = stock_data_fetching.get_saved_stocks()
    stocks.remove(stock_symbol)
    stock_data_fetching.save_saved_stocks_to_file(stocks)

    del stock_data_fetching.STOCK_PRICES[stock_symbol]

    for widget in frame_container.winfo_children():
        widget.destroy()

    for row, stock in enumerate(stocks):
        gui.display_saved_stock(frame_container, stock, stock_data_fetching.STOCK_PRICES[stock][0], row)


def on_button_add_click(stock_symbol: str, frame_container: tk.Frame):
    exists = not stock_symbol not in stock_data_fetching.get_saved_stocks()
    stock_data_fetching.save_stock_locally(stock_symbol)
    if not exists:
        query = {}
        stock_data_fetching.fetch_quote(stock_symbol, query)
        saved_stocks_count = len(stock_data_fetching.get_saved_stocks())
        stock_data_fetching.STOCK_PRICES[stock_symbol] = [
            {"c": query[stock_symbol]["c"], "pc": query[stock_symbol]["pc"]}
        ]
        gui.display_saved_stock(frame_container, stock_symbol, query[stock_symbol], saved_stocks_count)

