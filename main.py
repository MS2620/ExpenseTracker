import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from datetime import datetime
from tkcalendar import DateEntry 

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        # Create a style
        self.style = ttk.Style()

        # Create a file to store records
        self.record_file = "records.json"
        if not os.path.exists(self.record_file):
            with open(self.record_file, 'w') as file:
                json.dump([], file)

        # Create and set up the GUI components
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize a dictionary to store tree views for each month
        self.month_trees = {}
        self.total_labels = {}

        # Create tabs for each month
        for month in range(1, 13):
            month_name = datetime.strptime(str(month), "%m").strftime("%B")
            frame = ttk.Frame(self.notebook)
            tree = ttk.Treeview(frame, columns=("Type", "Amount", "Purpose", "Due Date"))
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("Type", anchor=tk.W, width=100)
            tree.column("Amount", anchor=tk.W, width=100)
            tree.column("Purpose", anchor=tk.W, width=200)
            tree.column("Due Date", anchor=tk.W, width=100)

            tree.heading("#0", text="", anchor=tk.W)
            tree.heading("Type", text="Type", anchor=tk.W)
            tree.heading("Amount", text="Amount", anchor=tk.W)
            tree.heading("Purpose", text="Purpose", anchor=tk.W)
            tree.heading("Due Date", text="Due Date", anchor=tk.W)

            tree.pack(fill=tk.BOTH, expand=True)
            self.notebook.add(frame, text=month_name)
            self.month_trees[month_name] = tree

            # Create a label for the total at the bottom right
            total_label = tk.Label(frame, text="Total: £0.00", anchor="e", font=("Helvetica", 12, "bold"), fg="green")
            total_label.pack(side=tk.BOTTOM, fill=tk.X)
            self.total_labels[month_name] = total_label

        # Set up the date picker
        self.label_due_date = tk.Label(root, text="Due Date:")
        self.label_due_date.pack(side=tk.LEFT, padx=10, pady=5)

        self.due_date_entry = DateEntry(root, date_pattern="dd-mm-yyyy")
        self.due_date_entry.pack(side=tk.LEFT, padx=10, pady=5)

        self.label_type = tk.Label(root, text="Type:")
        self.label_type.pack(side=tk.LEFT, padx=10, pady=5)

        self.type_var = tk.StringVar()
        self.type_var.set("Expense")  # Default type is Expense

        self.type_menu = tk.OptionMenu(root, self.type_var, "Expense", "Income")
        self.type_menu.pack(side=tk.LEFT, padx=10, pady=5)

        self.label_amount = tk.Label(root, text="Amount:")
        self.label_amount.pack(side=tk.LEFT, padx=10, pady=5)

        self.amount_entry = tk.Entry(root)
        self.amount_entry.pack(side=tk.LEFT, padx=10, pady=5)

        self.label_purpose = tk.Label(root, text="Purpose:")
        self.label_purpose.pack(side=tk.LEFT, padx=10, pady=5)

        self.purpose_entry = tk.Entry(root)
        self.purpose_entry.pack(side=tk.LEFT, padx=10, pady=5)

        self.add_button = tk.Button(root, text="Add Record", command=self.add_record)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Show records automatically on load
        self.show_records()

        self.remove_record_button = tk.Button(root, text="Remove Record", command=self.remove_selected_record)
        self.remove_record_button.pack()

        self.remove_all_records_button = tk.Button(root, text="Remove All Records", command=self.remove_all_records)
        self.remove_all_records_button.pack()

        # Bind double-click event to the edit_record_on_double_click function
        self.notebook.bind("<Double-1>", self.edit_record_on_double_click)

    def add_tab(self, month):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=month)

        tree = ttk.Treeview(frame)
        tree["columns"] = ("Type", "Amount", "Purpose", "Due Date")
        tree.column("#0", width=0, stretch=tk.NO)  # Hide the default column
        tree.column("Type", anchor=tk.W, width=100)
        tree.column("Amount", anchor=tk.W, width=100)
        tree.column("Purpose", anchor=tk.W, width=200)
        tree.column("Due Date", anchor=tk.W, width=100)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("Type", text="Type", anchor=tk.W)
        tree.heading("Amount", text="Amount", anchor=tk.W)
        tree.heading("Purpose", text="Purpose", anchor=tk.W)
        tree.heading("Due Date", text="Due Date", anchor=tk.W)

        tree.pack(fill=tk.BOTH, expand=True)

        setattr(self, f"tree_{month}", tree)  # Save a reference to the treeview
    
    def add_record(self):
        record_type = self.get_record_type()
        amount_text = self.amount_entry.get()
        purpose_text = self.purpose_entry.get()
        due_date_text = self.due_date_entry.get()

        if amount_text and purpose_text and due_date_text:
            try:
                amount = float(amount_text) if record_type == "Income" else -float(amount_text)
            except ValueError:
                messagebox.showwarning("Record Tracker", "Please enter a valid numeric value for Amount.")
                return

            new_record = {
                "Type": record_type,
                "Amount": amount,
                "Purpose": purpose_text,
                "Due Date": due_date_text
            }

            with open(self.record_file, 'r') as file:
                records = json.load(file)

            records.append(new_record)

            with open(self.record_file, 'w') as file:
                json.dump(records, file, indent=2)

            messagebox.showinfo("Record Tracker", "Record added successfully!")

            # Get the selected tab's text
            current_tab_text = self.notebook.tab(self.notebook.select(), "text")

            # Update the treeview for the selected tab
            current_tab_tree = self.month_trees.get(current_tab_text)
            self.update_tree(records, tree=current_tab_tree)

            self.clear_entries()
            self.update_total(records)
        else:
            messagebox.showwarning("Record Tracker", "Please fill in all fields.")

    def show_records(self):
        try:
            with open(self.record_file, 'r') as file:
                records = json.load(file)

            # Convert "Amount" values to float and filter out records with invalid values
            records = [rec for rec in records if isinstance(rec.get("Amount"), (int, float))]

            self.update_tree(records)
            self.update_total(records)
        except FileNotFoundError:
            messagebox.showwarning("Record Tracker", "No records recorded yet.")
        except json.JSONDecodeError:
            messagebox.showwarning("Record Tracker", "Error decoding JSON. Check your records file.")

    def remove_selected_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_record_id = self.tree.item(selected_item, "text")
            print(f"Selected Record ID: {selected_record_id}")

            with open(self.record_file, 'r') as file:
                records = json.load(file)

            print("All Records:")
            print(records)

            updated_records = [rec for rec in records if rec.get("ID") != selected_record_id]

            print("Updated Records:")
            print(updated_records)

            with open(self.record_file, 'w') as file:
                json.dump(updated_records, file, indent=2)

            messagebox.showinfo("Record Tracker - Remove Record", "Record removed successfully!")
            self.update_tree(updated_records)
            self.update_total(updated_records)
        else:
            messagebox.showwarning("Record Tracker - Remove Record", "Please select a record to remove.")

    # Define the edit_record_on_double_click function
    def edit_record_on_double_click(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        selected_item = self.month_trees[selected_tab].selection()
        
        if selected_item:
            selected_record = self.month_trees[selected_tab].item(selected_item, "values")
            self.set_record_type(selected_record[0])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, selected_record[1])

            self.purpose_entry.delete(0, tk.END)
            self.purpose_entry.insert(0, selected_record[2])

            self.due_date_entry.set_date(datetime.strptime(selected_record[3], "%d-%m-%Y"))

            # Remove the selected record from the Treeview
            updated_records = [rec for rec in json.load(open(self.record_file)) if list(rec.values()) != selected_record]

            with open(self.record_file, 'w') as file:
                json.dump(updated_records, file, indent=2)

            self.update_tree(updated_records, tree=self.month_trees[selected_tab])
            self.update_total(updated_records)
        else:
            messagebox.showwarning("Record Tracker - Edit Record", "Please select a record to edit.")

    def get_record_type(self):
        return self.type_var.get()

    def set_record_type(self, record_type):
        self.type_var.set(record_type)

    def update_tree(self, records=None, tree=None):
        if records is None:
            try:
                with open(self.record_file, 'r') as file:
                    records = json.load(file)
            except FileNotFoundError:
                records = []

        # Clear all tree views
        for tree in self.month_trees.values():
            tree.delete(*tree.get_children())

        if records:
            for rec in records:
                month_name = datetime.strptime(rec["Due Date"], "%d-%m-%Y").strftime("%B")
                amount = f"£{abs(float(rec['Amount'])):.2f}"
                self.month_trees[month_name].insert("", tk.END, values=(rec["Type"], amount, rec["Purpose"], rec["Due Date"]))

    def clear_entries(self):
        self.amount_entry.delete(0, tk.END)
        self.purpose_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)

    def update_total(self, records):
        for month_name, tree in self.month_trees.items():
            total = sum(float(rec["Amount"]) if rec["Due Date"] and datetime.strptime(rec["Due Date"], "%d-%m-%Y").strftime("%B") == month_name else 0 for rec in records)
            total_amount = abs(total)

            total_label_text = f"Total: £{total_amount:.2f}"

            # Set the text color based on the sign of the total
            total_label = self.total_labels.get(month_name)
            if total_label:
                if total >= 0:
                    total_label.config(text=total_label_text, fg="green")
                else:
                    total_label.config(text=total_label_text, fg="red")

    def remove_all_records(self):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to remove all records?")
        if confirmation:
            with open(self.record_file, 'w') as file:
                json.dump([], file, indent=2)

            messagebox.showinfo("Record Tracker - Remove All Records", "All records removed successfully!")
            self.update_tree([])
            self.update_total([])

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
