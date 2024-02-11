""""Fetch information from an API and the local JSON file used for saving data"""
import os
import threading
import json

import tkinter as tk
import finnhub

import click_events
import gui
import email_handler

finnhub_client = finnhub.Client(
    api_key="cmvoki1r01qkcvkeu40gcmvoki1r01qkcvkeu410"
)
STOCK_PRICES = {}
SAVED_STOCKS_FILE = "saved_stocks.json"


def save_saved_stocks_to_file(saved_stocks: list) -> None:
    """
    Save the list of saved stocks to the JSON file.

    Parameters:
        saved_stocks (list): The list of saved stocks to be saved.

    Returns:
        None
    """
    with open(SAVED_STOCKS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    data["STOCKS"] = saved_stocks

    with open(SAVED_STOCKS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file)


def save_stock_locally(stock_symbol: str) -> None:
    """
    Save a stock if it is not already saved.

    Parameters:
        stock_symbol (str): The symbol of the stock to be saved.

    Returns:
        None
    """
    saved_stocks = get_saved_stocks()["STOCKS"]
    if stock_symbol not in saved_stocks:
        saved_stocks.append(stock_symbol)
        save_saved_stocks_to_file(saved_stocks)


def get_saved_stocks() -> dict:
    """
    Retrieve the saved stocks, email, and notifications from the local storage.
    If the required JSON file does not exist create a new blank one.

    Returns:
        dict: A dictionary containing the saved stocks, email, and notifications.
    """
    if not os.path.isfile(SAVED_STOCKS_FILE):
        data = {
            "STOCKS": [],
            "EMAIL": "",
            "NOTIFICATIONS": {}
        }
        with open(SAVED_STOCKS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file)
    try:
        with open(SAVED_STOCKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def get_stocks_for_notifications() -> dict:
    """
    Retrieve the stocks for which notifications are set.

    Returns:
        dict: A dictionary containing the stocks for which notifications are set.
    """
    with open(SAVED_STOCKS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["NOTIFICATIONS"]


def remove_stock_notification(stock_symbol: str) -> None:
    """
    Remove a stock notification for the given stock symbol.

    Parameters:
        stock_symbol (str): The symbol of the stock for which the notification is to be removed.

    Returns:
        None
    """
    with open(SAVED_STOCKS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    del data["NOTIFICATIONS"][stock_symbol]

    with open(SAVED_STOCKS_FILE,
              "w",
              encoding="utf-8") as file:
        json.dump(data, file)


def fetch_quote(stock_symbol: str,
                query_result: dict) -> None:
    """
    Fetch the quote data for the given stock and update the query_result dict with the result.

    Parameters:
        stock_symbol (str): The symbol of the stock to fetch the quote for.
        query_result (dict): A dictionary to store the query result.

    Returns:
        None
    """
    query_result[stock_symbol] = finnhub_client.quote(stock_symbol)


def load_saved_stocks(frame_container: tk.Frame,
                      frame_expand_container: tk.Frame,
                      root: tk.Tk) -> None:
    """
    Load and display saved stocks in the GUI.

    Parameters:
        frame_container (tk.Frame): The frame to contain the saved stocks.
        frame_expand_container (tk.Frame): The frame to contain expanded details.
        root (tk.Tk): The root Tkinter window.

    Returns:
        None
    """
    stocks = get_saved_stocks()["STOCKS"]
    queries = {}

    for widget in frame_container.winfo_children():
        widget.destroy()

    threads = []

    for stock in stocks:
        thread = threading.Thread(target=fetch_quote,
                                  args=(stock, queries))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for row, stock in enumerate(stocks):
        queries[stock]["stock_symbol"] = stock
        widgets_dict = {
            "frame_container": frame_container,
            "root": root,
            "frame_expand_container": frame_expand_container}
        gui.display_saved_stock(widgets_dict,
                                queries[stock],
                                row)
        STOCK_PRICES[stock] = [
            queries[stock]
        ]


def update_prices(root: tk.Tk,
                  frame_expand_container: tk.Frame,
                  frame_container: tk.Frame) -> None:
    """
    Update stock prices in the GUI and send email notifications if triggered.

    Parameters:
        root (tk.Tk): The root Tkinter window.
        frame_expand_container (tk.Frame): The frame containing expanded details.
        frame_container (tk.Frame): The frame containing saved stocks.

    Returns:
        None
    """
    load_saved_stocks(frame_container,
                      frame_expand_container,
                      root)
    print("Updating...")

    email = email_handler.get_email()
    stocks_to_notify = get_stocks_for_notifications()

    if email != "" and stocks_to_notify != {}:
        email_body = (
            "The following stocks have reached "
            "your wanted price ranges:"
        )
        has_notification = False
        for stock in stocks_to_notify:
            if (stocks_to_notify[stock][0]
                    == ">="
                    and STOCK_PRICES[stock][0]["c"]
                    >= stocks_to_notify[stock][1]):
                email_body += (
                    f"\n{stock} has surpassed "
                    f"${stocks_to_notify[stock][1]}"
                    f" and is now valued at ${STOCK_PRICES[stock][0]["c"]}"
                )
                remove_stock_notification(stock)
                has_notification = True
            elif (stocks_to_notify[stock][0]
                    == "<="
                    and STOCK_PRICES[stock][0]["c"]
                    <= stocks_to_notify[stock][1]):
                email_body += (
                    f"\n{stock} has fallen bellow "
                    f"${stocks_to_notify[stock][1]}"
                    f" and is now valued at ${STOCK_PRICES[stock][0]["c"]}"
                )
                remove_stock_notification(stock)
                has_notification = True
        if has_notification:
            email_handler.send_email("Stock prices notification",
                                     email_body,
                                     [email])

    root.after(20000, lambda: update_prices(root,
                                            frame_expand_container,
                                            frame_container))


def fetch_search_results(entry_text: str,
                         loading_label: tk.Label,
                         frames_dict: dict) -> None:
    """
    Fetch search results based on the entry text and display them in the GUI.

    Parameters:
        entry_text (str): The text entered in the search entry.
        loading_label (tk.Label): The label used to indicate loading status.
        frames_dict (dict): A dictionary containing frames for displaying search results.

    Returns:
        None
    """
    loading_label.config(text="Loading...")

    data = finnhub_client.symbol_lookup(entry_text)
    symbols = []
    [symbols.append(symbol)
     for symbol in [entry["symbol"].split(".")[0]
                    for entry in data.get("result", [])]
     if symbol not in symbols]

    for row, symbol in enumerate(symbols):
        create_search_result(symbol,
                             row,
                             frames_dict)

    loading_label.config(text="")


def create_search_result(stock_symbol: str,
                         row: int,
                         frames_dict: dict) -> None:
    """
    Create a search result for a stock and display it in the GUI.

    Parameters:
        stock_symbol (str): The symbol of the stock.
        row (int): The row in which the search result will be displayed.
        frames_dict (dict): A dictionary containing frames for displaying search results.

    Returns:
        None
    """
    frame_temp = tk.Frame(frames_dict["frame_left_results"])
    frame_temp.grid_columnconfigure(0, weight=1)

    label_name = tk.Label(frame_temp,
                          text=stock_symbol,
                          width=10
                          )
    label_name.grid(row=0,
                    column=0,
                    sticky="ew")

    empty_label3 = tk.Label(frame_temp, width=25)
    empty_label3.grid(row=0, column=1)

    label_price = tk.Label(
        frame_temp,
        text=finnhub_client.quote(stock_symbol)["c"],
        width=10
    )
    label_price.grid(row=0,
                     column=2,
                     sticky="ew")

    button_add = tk.Button(
        frame_temp,
        command=lambda: click_events.on_button_add_click(stock_symbol,
                                                         frames_dict),
        text="Add",
        width=4,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_add.grid(row=0, column=3)

    frame_temp.grid(row=row, column=0,
                    pady=5, padx=15)


def get_other_data(stock_symbol: str) -> dict:
    """
    Retrieve additional data for a given stock symbol from the Finnhub API.

    Parameters:
        stock_symbol (str): The symbol of the stock for which additional data is required.

    Returns:
        dict: A dictionary containing additional data for the specified stock symbol.
    """
    return finnhub_client.company_profile2(symbol=stock_symbol)
