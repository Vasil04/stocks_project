import tkinter as tk
from tkinter import font
import finnhub
import threading

finnhub_client = finnhub.Client(api_key="cmvoki1r01qkcvkeu40gcmvoki1r01qkcvkeu410")
base_url = "https://finnhub.io/api/v1"


def on_entry_click(event):
    if entry.get() == "Enter your text here":
        entry.delete(0, tk.END)
        entry.config(fg='black')


def create_search_result(symbol: str, row: int):
    frame_temp = tk.Frame(frameL_results)
    frame_temp.grid_columnconfigure(0, weight=1)

    label_name = tk.Label(frame_temp, text=symbol, width=10)
    label_name.grid(row=0, column=0, sticky="ew")

    empty_label3 = tk.Label(frame_temp, width=25)
    empty_label3.grid(row=0, column=1)

    label_price = tk.Label(frame_temp, text=finnhub_client.quote(symbol)["c"], width=10)
    label_price.grid(row=0, column=2, sticky="ew")

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


root = tk.Tk()
root.title("Stocks")
root.geometry("400x300")
root.state('zoomed')


default_text = "Enter your text here"

frameL = tk.Frame()
frameL_results = tk.Frame(frameL)
frameM = tk.Frame(bg="lightgreen")
frameR = tk.Frame()

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


# RIGHT FRAME------------------------------------------------------------------------------------

frameL.grid(row=0, column=0, sticky='nsew')

empty_label1 = tk.Label(width=10)
empty_label1.grid(row=0, column = 1)

frameM.grid(row=0, column=2, sticky='nsew')

empty_label2 = tk.Label(width=10)
empty_label2.grid(row=0, column = 3)

frameR.grid(row=0, column=4, sticky='nsew')

root.mainloop()