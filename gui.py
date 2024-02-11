"""Creates the graphical elements for the tkinter window"""
import tkinter as tk
from tkinter import font

import click_events
import stock_data_fetching


def on_configure(event: tk.Event,
                 canvas: tk.Canvas) -> None:
    """
    Adjust the scroll region of a canvas to fit its contents.

    Parameters:
        event (tk.Event): The event triggering the function.
        canvas (tk.Canvas): The canvas to adjust.

    Returns:
        None
    """
    canvas.configure(scrollregion=canvas.bbox("all"))


def open_popup(root: tk.Tk, stock_symbol: str) -> None:
    """
    Open a popup window to configure notification settings for a stock.

    Parameters:
        root (tk.Tk): The root Tkinter window.
        stock_symbol (str): The symbol of the stock.

    Returns:
        None
    """
    popup = tk.Toplevel(root)
    popup.geometry("400x200")
    popup.title("Notification pop-up")

    label = tk.Label(popup, text="Customise your notification")
    label.pack(padx=20, pady=20)

    var = tk.StringVar()

    var.set("")

    radio_button1 = tk.Radiobutton(
        popup, text="Notify me if the price goes above or equals",
        variable=var,
        value=">="
    )
    radio_button2 = tk.Radiobutton(
        popup, text="Notify me if the price goes below or equals",
        variable=var,
        value="<="
    )

    radio_button1.pack(anchor=tk.W)
    radio_button2.pack(anchor=tk.W)

    entry_desired_price = tk.Entry(popup,
                                   fg="grey")
    entry_desired_price.insert(0, "Desired price")
    entry_desired_price.bind("<FocusIn>",
                             lambda event:
                             click_events.on_entry_click(event,
                                                         entry_desired_price,
                                                         "Desired price"))
    entry_desired_price.pack(anchor=tk.W, padx=5, pady=5)

    feedback_label = tk.Label(popup)
    feedback_label.pack()

    button_done = tk.Button(
        popup,
        command=lambda: click_events.button_done_click(
            {
                "entry": entry_desired_price,
                "feedback": feedback_label,
                "var": var,
                "popup": popup
            },
            stock_symbol
        ),
        text="Done",
        width=5,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_done.pack(anchor=tk.W, padx=5, pady=5)


def display_saved_stock(widgets_dict: dict,
                        stock_data: dict,
                        row: int) -> None:
    """
    Display information for a saved stock in a frame.

    Parameters:
        widgets_dict (dict): A dictionary containing required widgets.
        stock_data (dict): A dictionary containing stock data.
        row (int): The row index for the frame placement.

    Returns:
        None
    """
    frame_stock = tk.Frame(
        widgets_dict["frame_container"],
        highlightbackground="black",
        highlightthickness=1
    )
    frame_stock.grid_columnconfigure(0, weight=1)

    label_symbol = tk.Label(frame_stock,
                            text=stock_data["stock_symbol"],
                            width=10)
    label_symbol.grid(row=0,
                      column=0,
                      sticky="ew")

    empty_label4 = tk.Label(frame_stock, width=20)
    empty_label4.grid(row=0, column=1)

    label_price = tk.Label(frame_stock,
                           text=stock_data["c"],
                           width=10)

    label_price.grid(row=0,
                     column=3,
                     sticky="ew")

    button_expand = tk.Button(
        frame_stock,
        command=lambda: click_events.on_button_expand_click(
            stock_data["stock_symbol"],
            widgets_dict["frame_expand_container"]),
        text="Expand",
        width=6,
        height=1,
        bg="#c4c4c4",
        fg="black",)
    button_expand.grid(row=1, column=0, pady=10, sticky="e")

    button_notify = tk.Button(
        frame_stock,
        command=lambda: click_events.on_button_notify_click(
            stock_data["stock_symbol"],
            widgets_dict["root"]),
        text="Notify",
        width=6,
        height=1,
        bg="#41cc66",
        fg="white", )
    button_notify.grid(row=1, column=1, pady=10, sticky="e", padx=10)

    button_remove_notify = tk.Button(
        frame_stock,
        command=lambda: click_events.on_button_remove_notify_click(
            stock_data["stock_symbol"]),
        text="Remove n",
        width=8,
        height=1,
        bg="#e32245",
        fg="white", )
    button_remove_notify.grid(row=1, column=2, pady=10, sticky="we")

    button_delete = tk.Button(
        frame_stock,
        command=lambda: click_events.on_button_delete_click(
            stock_data["stock_symbol"],
            widgets_dict),
        text="Delete",
        width=6,
        height=1,
        bg="#e32245",
        fg="white", )
    button_delete.grid(row=1, column=3, pady=10)

    if stock_data["c"] > stock_data["pc"]:
        label_price.config(fg="green")
    elif stock_data["c"] < stock_data["pc"]:
        label_price.config(fg="red")

    frame_stock.grid(row=row,
                     column=0,
                     pady=(0, 5))


def setup_expanded_container(stock_symbol: str,
                             frame_container: tk.Frame) -> None:
    """
    Set up an expanded container to display detailed stock information.

    Parameters:
        stock_symbol (str): The symbol of the stock.
        frame_container (tk.Frame): The frame to contain the expanded details.

    Returns:
        None
    """
    prices = stock_data_fetching.STOCK_PRICES[stock_symbol][0]
    other_stock_data = (stock_data_fetching.
                        get_other_data(stock_symbol))

    if other_stock_data != {}:
        label_company_name = tk.Label(frame_container,
                                      text=other_stock_data["name"])
        label_company_name.grid(row=0, column=0, sticky="w")

        label_company_country = tk.Label(
            frame_container,
            text=f"This company's headquarters are in "
            f"{other_stock_data["country"]}")
        label_company_country.grid(row=1, column=0, sticky="w")

        label_company_currency = tk.Label(
            frame_container,
            text=f"This company's stocks are traded in "
            f"{other_stock_data["currency"]} on the "
            f"{other_stock_data["exchange"]}")
        label_company_currency.grid(row=2, column=0, sticky="w")

        label_company_cap = tk.Label(
            frame_container,
            text=f"Market capitalization: "
            f"{other_stock_data["marketCapitalization"]}")
        label_company_cap.grid(row=3, column=0, sticky="w")

    label_current_price = tk.Label(
        frame_container,
        text=f"Current price: $"
        f"{prices["c"]}")
    label_current_price.grid(row=4, column=0, sticky="w")

    label_previous_close_price = tk.Label(
        frame_container,
        text=f"Previous close price: $"
        f"{prices["pc"]}")
    label_previous_close_price.grid(row=5, column=0, sticky="w")

    label_percent_change = tk.Label(
        frame_container,
        text=f"Percent change: "
        f"{prices["d"]}%")
    label_percent_change.grid(row=6, column=0, sticky="w")

    label_high_price = tk.Label(
        frame_container,
        text=f"High price of the day: $"
        f"{prices["h"]}")
    label_high_price.grid(row=7, column=0, sticky="w")

    label_low_price = tk.Label(
        frame_container,
        text=f"Low price of the day: $"
        f"{prices["l"]}")
    label_low_price.grid(row=8, column=0, sticky="w")

    label_open_price = tk.Label(
        frame_container,
        text=f"open price of the day: $"
        f"{prices["l"]}")
    label_open_price.grid(row=9, column=0, sticky="w")

    button_clear = tk.Button(
        frame_container,
        command=lambda:
        click_events.on_button_click_clear_right(frame_container),
        text="Clear",
        width=10,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_clear.grid(row=9,
                      column=2,
                      pady=(0, 5),
                      sticky="e")


def setup_gui(root: tk.Tk) -> None:
    """
    Set up the main graphical user interface (GUI) for the application.

    Parameters:
        root (tk.Tk): The Tkinter root window.

    Returns:
        None
    """
    frame_container_grande = tk.Frame(root)
    frame_container_grande.grid(row=0,
                                column=0,
                                sticky="nsew")

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

    entry.insert(0, "Find stocks")
    entry.bind("<FocusIn>",
               lambda event: click_events.on_entry_click(event,
                                                         entry,
                                                         "Find stocks")
               )
    entry.grid(
        row=0,
        column=0,
        columnspan=2,
        padx=35,
        pady=(35, 10))

    button_search = tk.Button(
        frame_left,
        command=lambda: click_events.on_button_click_search(
            entry.get(),
            loading_label,
            {"frame_left_results": frame_left_results,
             "frame_container": frame_container,
             "root": root,
             "frame_expand_container": frame_extended_data_container}),
        text="Search",
        width=10,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_search.grid(row=0,
                       column=2,
                       pady=(35, 10))

    button_clear = tk.Button(
        frame_left,
        command=lambda: click_events.on_button_click_clear(frame_left_results),
        text="Clear",
        width=10,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_clear.grid(row=1,
                      column=2,
                      pady=(5, 10))

    loading_label = tk.Label(frame_left,
                             text="",
                             bg=frame_left.cget("bg"))

    loading_label.grid(row=1,
                       column=0,
                       pady=10)

    frame_left_results.grid(row=2, column=0)

    # MIDDLE FRAME--------------------------------------
    times_font = font.Font(family="Times",
                           size=20,
                           slant="italic")

    label_header = tk.Label(frame_mid, text="My stocks:",
                            bg="lightgreen", font=times_font)

    label_header.grid(row=0, column=0)

    frame_mid_saved_stocks.grid(row=1, column=0,
                                pady=(20, 0), sticky="nsew")

    canvas = tk.Canvas(frame_mid_saved_stocks)
    canvas.grid(row=0,
                column=0,
                sticky="nsew")

    scrollbar = tk.Scrollbar(
        frame_mid_saved_stocks,
        orient=tk.VERTICAL,
        command=canvas.yview
    )
    scrollbar.grid(row=0,
                   column=1,
                   sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)

    frame_container = tk.Frame(canvas)
    canvas.create_window((0, 0),
                         window=frame_container,
                         anchor=tk.NW)

    frame_container.bind("<Configure>",
                         lambda event: on_configure(event, canvas))

    # RIGHT FRAME-----------------------------------
    entry_email = tk.Entry(
        frame_right,
        width=60,
        fg="grey")
    entry_email_text = (
        "Enter an email where you would like "
        "to receive notifications"
    )
    entry_email.insert(0, entry_email_text)
    entry_email.bind(
        "<FocusIn>",
        lambda event: click_events.on_entry_click(
            event,
            entry_email,
            entry_email_text
        )
    )
    entry_email.grid(
        row=0,
        column=0,
        columnspan=2,
        padx=5,
        pady=(35, 10))

    empty_label_right = tk.Label(frame_right, width=5)
    empty_label_right.grid(row=0, column=2)

    email_feedback_label = tk.Label(frame_right,
                                    text="",
                                    bg=frame_left.cget("bg"))

    email_feedback_label.grid(row=1,
                              column=0,
                              pady=10)

    button_save = tk.Button(
        frame_right,
        command=lambda: click_events.on_button_click_save(
            entry_email.get(),
            email_feedback_label
        ),
        text="Save",
        width=10,
        height=1,
        bg="#c4c4c4",
        fg="black", )

    button_save.grid(row=0,
                     column=3,
                     pady=(35, 10))

    button_remove = tk.Button(
        frame_right,
        command=lambda: click_events.on_button_click_remove(
            email_feedback_label
        ),
        text="Remove",
        width=10,
        height=1,
        bg="#e32245",
        fg="white", )

    button_remove.grid(row=1,
                       column=3,
                       pady=(5, 10))

    frame_extended_data_container = tk.Frame(frame_right,
                                             highlightbackground="black",
                                             highlightthickness=1
                                             )
    frame_extended_data_container.grid(row=2,
                                       column=0,
                                       columnspan=4,
                                       sticky="nsew",
                                       pady=10)

    # ----------------------------------------------
    stock_data_fetching.update_prices(
        root,
        frame_extended_data_container,
        frame_container)

    frame_left.grid(row=0,
                    column=0,
                    stick="nsew")

    empty_label1 = tk.Label(frame_container_grande,
                            width=10)

    empty_label1.grid(row=0, column=1)

    frame_mid.grid(row=0,
                   column=2,
                   sticky="nsew")

    empty_label2 = tk.Label(frame_container_grande,
                            width=2)

    empty_label2.grid(row=0, column=3)

    frame_right.grid(row=0,
                     column=4,
                     sticky="nsew")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    frame_container_grande.grid_rowconfigure(0, weight=1)
    # frame_container_grande.grid_columnconfigure(0, weight=1)

    frame_mid.grid_rowconfigure(1, weight=1)
    frame_mid_saved_stocks.grid_rowconfigure(0, weight=1)
