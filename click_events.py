import threading
import json

import tkinter as tk

import stock_data_fetching
import gui
import email_handler


def on_entry_click(event: tk.Event,
                   entry: tk.Entry,
                   entry_default_text: str) -> None:
    if entry.get() == entry_default_text:
        entry.delete(0, tk.END)
        entry.config(fg="black")


def on_button_click_clear(frame: tk.Frame) -> None:
    for widget in frame.winfo_children():
        widget.destroy()


def on_button_click_search(entry_text: str,
                           loading_label: tk.Label,
                           frames_dict: dict) -> None:
    on_button_click_clear(frames_dict["frame_left_results"])
    threading.Thread(target=stock_data_fetching.fetch_search_results,
                     args=(entry_text,
                           loading_label,
                           frames_dict)).start()


def on_button_delete_click(stock_symbol: str,
                           frame_container: tk.Frame,
                           root: tk.Tk) -> None:
    stocks = stock_data_fetching.get_saved_stocks()["STOCKS"]
    stocks.remove(stock_symbol)
    stock_data_fetching.save_saved_stocks_to_file(stocks)

    del stock_data_fetching.STOCK_PRICES[stock_symbol]

    for widget in frame_container.winfo_children():
        widget.destroy()

    for row, stock in enumerate(stocks):
        stock_data = stock_data_fetching.STOCK_PRICES[stock][0]
        stock_data["stock_symbol"] = stock
        widgets_dict = {"frame_container": frame_container, "root": root}
        gui.display_saved_stock(widgets_dict, stock_data, row)


def on_button_add_click(stock_symbol: str,
                        frame_container: tk.Frame,
                        root: tk.Tk):
    exists = not stock_symbol not in stock_data_fetching.get_saved_stocks()["STOCKS"]
    stock_data_fetching.save_stock_locally(stock_symbol)
    if not exists:
        query = {}
        stock_data_fetching.fetch_quote(stock_symbol, query)
        saved_stocks_count = len(stock_data_fetching.get_saved_stocks()["STOCKS"])
        stock_data_fetching.STOCK_PRICES[stock_symbol] = [
            {"c": query[stock_symbol]["c"],
             "pc": query[stock_symbol]["pc"]}
        ]
        query[stock_symbol]["stock_symbol"] = stock_symbol
        widgets_dict = {"frame_container": frame_container, "root": root}
        gui.display_saved_stock(widgets_dict,
                                query[stock_symbol],
                                saved_stocks_count)


def on_button_click_save(email: str,
                         feedback_label: tk.Label) -> None:
    email_handler.save_email(email)
    feedback_label.config(text="Email saved successfully")
    feedback_label.after(2000,
                         lambda: feedback_label.config(text=""))


def on_button_click_remove(feedback_label: tk.Label) -> None:
    email_handler.save_email("")
    feedback_label.config(text="Email removed successfully")
    feedback_label.after(2000,
                         lambda: feedback_label.config(text=""))


def on_button_notify_click(stock_symbol: str, root: tk.Tk) -> None:
    gui.open_popup(root, stock_symbol)


def button_done_click(widgets_dict: dict, stock_symbol: str):
    def convert_to_positive_number(s: str) -> float:
        try:
            num = float(s)
            if num > 0:
                return num
            else:
                return None
        except ValueError:
            return None

    notification_requirement = []
    desired_price = widgets_dict["entry"].get()
    if widgets_dict["var"] != "" and convert_to_positive_number(desired_price) is not None:
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

    else:
        widgets_dict["feedback"].config(text="Invalid input")
        widgets_dict["feedback"].after(2000,
                                       lambda:
                                       widgets_dict["feedback"].config(text=""))
