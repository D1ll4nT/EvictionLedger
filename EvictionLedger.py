import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date
import calendar

class LedgerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ledger Creator")
        self.create_widgets()

    def create_widgets(self):
        # --- Scheduled Rent Charges Section ---
        scheduled_frame = ttk.LabelFrame(self.root, text="Scheduled Rent Charges", padding="10")
        scheduled_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(scheduled_frame, text="Rent Charge Amount:").grid(row=0, column=0, sticky="w")
        self.rent_amount_entry = ttk.Entry(scheduled_frame)
        self.rent_amount_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(scheduled_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.start_date_entry = ttk.Entry(scheduled_frame)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(scheduled_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        self.end_date_entry = ttk.Entry(scheduled_frame)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        generate_button = ttk.Button(scheduled_frame, text="Generate Rent Charges", command=self.generate_rent_charges)
        generate_button.grid(row=3, column=0, columnspan=2, pady=5)

        # --- Manual Transactions Section ---
        manual_frame = ttk.LabelFrame(self.root, text="Manual Transactions", padding="10")
        manual_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(manual_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.manual_date_entry = ttk.Entry(manual_frame)
        self.manual_date_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.manual_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(manual_frame, text="Description:").grid(row=1, column=0, sticky="w")
        self.manual_desc_entry = ttk.Entry(manual_frame, width=40)
        self.manual_desc_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(manual_frame, text="Amount:").grid(row=2, column=0, sticky="w")
        self.manual_amount_entry = ttk.Entry(manual_frame)
        self.manual_amount_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(manual_frame, text="Transaction Type:").grid(row=3, column=0, sticky="w")
        self.manual_type_var = tk.StringVar(value="Payment")
        type_menu = ttk.OptionMenu(manual_frame, self.manual_type_var, "Payment", "Charge", "Payment")
        type_menu.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        add_manual_button = ttk.Button(manual_frame, text="Add Transaction", command=self.add_manual_transaction)
        add_manual_button.grid(row=4, column=0, columnspan=2, pady=5)

        # --- Ledger Table ---
        self.tree = ttk.Treeview(self.root, columns=("Date", "Charge", "Description", "Payment", "Running Balance"), show="headings")
        for col in ("Date", "Charge", "Description", "Payment", "Running Balance"):
            self.tree.heading(col, text=col)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Charge", width=100, anchor="e")
        self.tree.column("Description", width=200, anchor="w")
        self.tree.column("Payment", width=100, anchor="e")
        self.tree.column("Running Balance", width=120, anchor="e")
        self.tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Save Ledger Button ---
        save_button = ttk.Button(self.root, text="Save Ledger", command=self.save_ledger)
        save_button.grid(row=3, column=0, pady=5)

    def generate_rent_charges(self):
        """
        Generate scheduled rent charges between start and end dates.
        If the lease starts mid-month, the first month is pro-rated using a 30-day month basis.
        In a single-month lease, the pro-rate is computed from the start date through the end date.
        For multi-month leases, only the first month is pro-rated.
        """
        rent_amount_str = self.rent_amount_entry.get().strip()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()

        try:
            rent_amount = float(rent_amount_str)
            if rent_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid Rent Charge Amount greater than zero.")
            return

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid Start Date. Use YYYY-MM-DD.")
            return

        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid End Date. Use YYYY-MM-DD.")
            return

        if start_date > end_date:
            messagebox.showerror("Input Error", "Start Date must be before or equal to End Date.")
            return

        # If the lease is entirely within one month, pro-rate for that period.
        if start_date.year == end_date.year and start_date.month == end_date.month:
            days_rented = end_date.day - start_date.day + 1
            pro_rate = rent_amount * (days_rented / 30.0)
            self.tree.insert("", "end", values=(
                start_date.strftime("%Y-%m-%d"),
                f"{pro_rate:.2f}",
                "Pro-Rate Rent",
                "0.00",
                "0.00"
            ))
        else:
            # Multiple-month lease:
            # --- First month (pro-rated if start_date is not the 1st) ---
            if start_date.day != 1:
                last_day = calendar.monthrange(start_date.year, start_date.month)[1]
                days_rented = last_day - start_date.day + 1
                pro_rate = rent_amount * (days_rented / 30.0)
                self.tree.insert("", "end", values=(
                    start_date.strftime("%Y-%m-%d"),
                    f"{pro_rate:.2f}",
                    "Pro-Rate Rent",
                    "0.00",
                    "0.00"
                ))
            else:
                # If the lease starts on the 1st, charge full rent.
                self.tree.insert("", "end", values=(
                    start_date.strftime("%Y-%m-%d"),
                    f"{rent_amount:.2f}",
                    "Rent",
                    "0.00",
                    "0.00"
                ))
            # --- Subsequent months: full rent charges ---
            # Start from the first day of the month following the start date.
            if start_date.day != 1:
                first_full_month = date(start_date.year, start_date.month, 1)
                first_full_month = self.next_month(first_full_month)
            else:
                first_full_month = self.next_month(start_date)

            next_date = first_full_month
            while next_date <= end_date:
                # (For simplicity, this example does full-month charges for subsequent months.)
                self.tree.insert("", "end", values=(
                    next_date.strftime("%Y-%m-%d"),
                    f"{rent_amount:.2f}",
                    "Rent",
                    "0.00",
                    "0.00"
                ))
                next_date = self.next_month(next_date)

        self.sort_tree_by_date()

    def next_month(self, date_obj):
        """Return a date representing the same day in the next month.
           If that day does not exist, use the last valid day of the next month."""
        year, month, day = date_obj.year, date_obj.month, date_obj.day
        if month == 12:
            new_year = year + 1
            new_month = 1
        else:
            new_year = year
            new_month = month + 1
        last_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(day, last_day)
        return date(new_year, new_month, new_day)

    def add_manual_transaction(self):
        date_str = self.manual_date_entry.get().strip()
        description = self.manual_desc_entry.get().strip()
        amount_str = self.manual_amount_entry.get().strip()
        trans_type = self.manual_type_var.get()

        try:
            trans_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid Date. Use YYYY-MM-DD.")
            return

        if not description:
            messagebox.showerror("Input Error", "Description cannot be empty.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid amount greater than zero.")
            return

        charge = amount if trans_type == "Charge" else 0.0
        payment = -amount if trans_type == "Payment" else 0.0

        self.tree.insert("", "end", values=(
            date_str,
            f"{charge:.2f}",
            description,
            f"{payment:.2f}",
            "0.00"
        ))
        self.sort_tree_by_date()

        self.manual_desc_entry.delete(0, tk.END)
        self.manual_amount_entry.delete(0, tk.END)

    def sort_tree_by_date(self):
        """Sort ledger entries by date and recalculate the running balance."""
        items = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            try:
                dt = datetime.strptime(values[0], "%Y-%m-%d")
            except Exception:
                dt = datetime.min
            items.append((dt, values))
        items.sort(key=lambda x: x[0])
        # Clear tree and reinsert sorted items.
        for item in self.tree.get_children():
            self.tree.delete(item)
        for dt, values in items:
            self.tree.insert("", "end", values=values)
        self.recalculate_running_balance()

    def recalculate_running_balance(self):
        running_balance = 0.0
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            running_balance += float(values[1]) + float(values[3])
            self.tree.set(item, "Running Balance", f"{running_balance:.2f}")

    def save_ledger(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Ledger Files", "*.txt"), ("All Files", "*.*")],
                                                 title="Save Ledger")
        if not file_path:
            return
        try:
            with open(file_path, "w") as file:
                headers = ["Date", "Charge", "Description", "Payment", "Running Balance"]
                file.write("\t".join(headers) + "\n")
                for item in self.tree.get_children():
                    values = self.tree.item(item, "values")
                    file.write("\t".join(values) + "\n")
            messagebox.showinfo("Save Successful", "Ledger saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save ledger:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LedgerApp(root)
    root.geometry("750x600")
    root.mainloop()
