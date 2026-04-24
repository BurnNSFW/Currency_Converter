import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise Exception("API_KEY не найден в файле .env")

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("1020x420")

        #Переменные
        self.from_currency = tk.StringVar(value="USD")
        self.to_currency = tk.StringVar(value="EUR")
        self.amount_var = tk.StringVar()

        #Окно
        self.setup_ui()
        self.history = load_history()
        self.update_history_table()

    def setup_ui(self):
        tk.Label(self.root, text="From:").grid(row=0, column=0, padx=10, pady=10)
        from_combo = ttk.Combobox(self.root, textvariable=self.from_currency, values=["USD", "EUR", "RUB"])
        from_combo.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="To:").grid(row=0, column=2, padx=10, pady=10)
        to_combo = ttk.Combobox(self.root, textvariable=self.to_currency, values=["USD", "EUR", "RUB"])
        to_combo.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(self.root, text="Amount:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.amount_var).grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Convert", command=self.convert).grid(row=1, column=2, padx=10, pady=10)

        columns = ("From", "To", "Amount", "Result", "Rate")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=20)

        tk.Button(self.root, text="Clear History", command=self.clear_history).grid(row=4, column=0, columnspan=4, pady=10)

    def convert(self):
        amount_str = self.amount_var.get()
        if not validate_amount(amount_str):
            messagebox.showerror("Error", "Введите положительное число.")
            return

        amount = float(amount_str)
        base = self.from_currency.get()
        target = self.to_currency.get()

        try:
            rate = get_exchange_rate(base, target, API_KEY)
            result = round(amount * rate, 2)

            entry = {"from": base, "to": target, "amount": amount, "result": result, "rate": rate}
            self.history.append(entry)
            save_history(self.history)

            self.update_history_table()

            messagebox.showinfo("Result", f"{amount} {base} = {result} {target}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.history:
            self.tree.insert("", "end", values=(item["from"], item["to"], item["amount"], item["result"], item["rate"]))

    def clear_history(self):
        self.history = []
        save_history(self.history)
        self.update_history_table()


def get_exchange_rate(base_currency, target_currency, api_key):
    url = "https://api.currencybeacon.com/v1/latest"
    params = {
        'api_key': api_key,
        'base': base_currency,
        'symbols': target_currency
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        rate = data['rates'][target_currency]
        return rate
    else:
        raise Exception(f"Ошибка API: {response.status_code}, {response.text}")


def validate_amount(s):
    try:
        value = float(s)
        return value > 0
    except ValueError:
        return False


def save_history(history):
    with open('history.json', 'w') as f:
        json.dump(history, f, indent=2)


def load_history():
    try:
        with open('history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()