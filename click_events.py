"""Handles click events for buttons and entries."""
import threading
import json

import tkinter as tk

import stock_data_fetching
import gui
import email_handler


def on_entry_click(event: tk.Event,
                   entry: tk.Entry,
                   entry_default_text: str) -> None:
    """
    Clear the Entry widget text if it matches the default text.

    Parameters:
        event (tk.Event): The click event triggering the function.
        entry (tk.Entry): The Entry widget.
        entry_default_text (str): The default text for the Entry widget.

    Returns:
        None
    """
    if entry.get() == entry_default_text:
        entry.delete(0, tk.END)
        entry.config(fg="black")


def on_button_click_clear(frame: tk.Frame) -> None:
    """
    Clear all widgets from the specified Tkinter frame.

    Parameters:
        frame (tk.Frame): The Tkinter frame containing widgets to be cleared.

    Returns:
        None
    """
    for widget in frame.winfo_children():
        widget.destroy()


def on_button_click_search(entry_text: str,
                           loading_label: tk.Label,
                           frames_dict: dict) -> None:
    """
    Fetches stocks from an API using the provided text as search keyword.

    Parameters:
        entry_text (str): The text to search for.
        loading_label (tk.Label): The label to display loading status.
        frames_dict (dict): Dictionary containing frames.

    Returns:
        None
    """
    on_button_click_clear(frames_dict["frame_left_results"])
    threading.Thread(target=stock_data_fetching.fetch_search_results,
                     args=(entry_text,
                           loading_label,
                           frames_dict)).start()


def on_button_delete_click(stock_symbol: str,
                           widget_dict: dict) -> None:
    """
    Delete a saved stock and update the UI accordingly.

    Parameters:
        stock_symbol (str): The symbol of the stock to delete.
        widget_dict (dict): Dictionary containing widgets.

    Returns:
        None
    """
    stocks = stock_data_fetching.get_saved_stocks()["STOCKS"]
    stocks.remove(stock_symbol)
    stock_data_fetching.save_saved_stocks_to_file(stocks)

    del stock_data_fetching.STOCK_PRICES[stock_symbol]

    for widget in widget_dict["frame_container"].winfo_children():
        widget.destroy()

    for row, stock in enumerate(stocks):
        stock_data = stock_data_fetching.STOCK_PRICES[stock][0]
        stock_data["stock_symbol"] = stock
        widgets_dict = {
            "frame_container": widget_dict["frame_container"],
            "root": widget_dict["root"]}
        gui.display_saved_stock(widgets_dict, stock_data, row)


def on_button_click_clear_right(frame_container: tk.Frame) -> None:
    """
    Clear all widgets from the expanded data frame.

    Parameters:
        frame_container (tk.Frame):
        The Tkinter frame containing widgets to be cleared.

    Returns:
        None
    """
    for widget in frame_container.winfo_children():
        widget.destroy()


def on_button_add_click(stock_symbol: str,
                        widget_dict: dict):
    """
    Add a stock and display its details if it's not already saved.

    Parameters:
        stock_symbol (str): The symbol of the stock to add.
        widget_dict (dict): Dictionary containing widgets.

    Returns:
        None
    """
    exists = (
        not stock_symbol
        not in stock_data_fetching.get_saved_stocks()["STOCKS"]
    )
    stock_data_fetching.save_stock_locally(stock_symbol)
    if not exists:
        query = {}
        stock_data_fetching.fetch_quote(stock_symbol, query)
        saved_stocks_count = (
            len(stock_data_fetching.get_saved_stocks()["STOCKS"])
        )
        stock_data_fetching.STOCK_PRICES[stock_symbol] = [
            {"c": query[stock_symbol]["c"],
             "pc": query[stock_symbol]["pc"]}
        ]
        query[stock_symbol]["stock_symbol"] = stock_symbol
        gui.display_saved_stock(widget_dict,
                                query[stock_symbol],
                                saved_stocks_count)


def on_button_click_save(email: str,
                         feedback_label: tk.Label) -> None:
    """
    Save the provided email address and give feedback for the action.

    Parameters:
        email (str): The email address to save.
        feedback_label (tk.Label): The label to provide feedback.

    Returns:
        None
    """
    email_handler.save_email(email)
    feedback_label.config(text="Email saved successfully")
    feedback_label.after(2000,
                         lambda: feedback_label.config(text=""))


def on_button_click_remove(feedback_label: tk.Label) -> None:
    """
    Remove the saved email address and give feedback for the action.

    Parameters:
        feedback_label (tk.Label): The label to provide feedback.

    Returns:
        None
    """
    email_handler.save_email("")
    feedback_label.config(text="Email removed successfully")
    feedback_label.after(2000,
                         lambda: feedback_label.config(text=""))


def on_button_notify_click(stock_symbol: str, root: tk.Tk) -> None:
    """
    Open a popup window to configure a notification about the stock.

    Parameters:
        stock_symbol (str): The symbol of the stock to notify about.
        root (tk.Tk): The root Tkinter window.

    Returns:
        None
    """
    gui.open_popup(root, stock_symbol)


def button_done_click(widgets_dict: dict, stock_symbol: str):
    """
    Handle button click event to save notification requirements for a stock.
    If the configuration is incorrect provide feedback.

    Parameters:
        widgets_dict (dict): A dictionary containing widgets.
        stock_symbol (str): The symbol of the stock.

    Returns:
        None
    """
    def convert_to_positive_number(s: str) -> float:
        """
        Check if a string is a positive number and if so convert it.

        Parameters:
            s (str): The input string to convert.

        Returns:
            float:
             The converted positive float number if successful,
              or None if conversion fails.
        """
        try:
            num = float(s)
            if num > 0:
                return num
            return None
        except ValueError:
            return None

    notification_requirement = []
    desired_price = widgets_dict["entry"].get()
    if (
        widgets_dict["var"] != ""
        and convert_to_positive_number(desired_price) is not None
    ):
        notification_requirement.extend(
            [widgets_dict["var"].get(),
             convert_to_positive_number(desired_price)]
        )

        with open(stock_data_fetching.SAVED_STOCKS_FILE,
                  "r",
                  encoding="utf-8") as file:
            data = json.load(file)

        data["NOTIFICATIONS"][stock_symbol] = notification_requirement
        with open(stock_data_fetching.SAVED_STOCKS_FILE,
                  "w",
                  encoding="utf-8") as file:
            json.dump(data, file)
        widgets_dict["popup"].destroy()

    else:
        widgets_dict["feedback"].config(text="Invalid input")
        (widgets_dict["feedback"].
         after(2000,
               lambda:
               widgets_dict["feedback"].config(text=""))
         )


def on_button_expand_click(
        stock_symbol: str,
        frame_expand_container: tk.Frame) -> None:
    """
    Handle button click event to provide more details for a stock.

    Parameters:
        stock_symbol (str):
         The symbol of the stock.
        frame_expand_container (tk.Frame):
         The frame to display expanded details.

    Returns:
        None
    """
    for widget in frame_expand_container.winfo_children():
        widget.destroy()
    gui.setup_expanded_container(stock_symbol,
                                 frame_expand_container)


def on_button_remove_notify_click(stock_symbol: str) -> None:
    """
    Handle button click event to remove notification for a stock.

    Parameters:
        stock_symbol (str): The symbol of the stock.

    Returns:
        None
    """
    stock_data_fetching.remove_stock_notification(stock_symbol)
