import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


class MedicalShopInventory:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Shop Inventory System")

        # Make the window size fixed
        self.root.minsize(800, 600)

        # Initialize database
        self.conn = sqlite3.connect('medical_inventory.db')
        self.create_tables()

        # Create main frames
        self.create_frames()

        # Create widgets
        self.create_inventory_widgets()
        self.create_sales_widgets()

        # Set up periodic stock check
        self.check_low_stock()

        # Handle app closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def view_stock(self):
    # Create a new window to display the stock
        stock_window = tk.Toplevel(self.root)
        stock_window.title("Current Stock")
        stock_window.geometry("500x400")
    
    # Create a Treeview widget to display the stock
        columns = ("Medicine Name", "Quantity", "Last Updated")
        tree = ttk.Treeview(stock_window, columns=columns, show="headings")
        tree.heading("Medicine Name", text="Medicine Name")
        tree.heading("Quantity", text="Quantity")
        tree.heading("Last Updated", text="Last Updated")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Fetch data from the inventory table
        cursor = self.conn.cursor()
        cursor.execute("SELECT medicine_name, quantity, last_updated FROM inventory ORDER BY medicine_name")
        rows = cursor.fetchall()
    
    # Insert data into the Treeview
        for row in rows:
            tree.insert("", tk.END, values=row)
    
    # Add a scrollbar
        scrollbar = ttk.Scrollbar(stock_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
    def view_sales(self):
    # Create a new window to display the sales report
        sales_window = tk.Toplevel(self.root)
        sales_window.title("Sales Report")
        sales_window.geometry("600x400")
    
    # Create a Treeview widget to display sales
        columns = ("Medicine Name", "Quantity Sold", "Sale Date")
        tree = ttk.Treeview(sales_window, columns=columns, show="headings")
        tree.heading("Medicine Name", text="Medicine Name")
        tree.heading("Quantity Sold", text="Quantity Sold")
        tree.heading("Sale Date", text="Sale Date")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Fetch data from the sales table
        cursor = self.conn.cursor()
        cursor.execute("SELECT medicine_name, quantity_sold, sale_date FROM sales ORDER BY sale_date DESC")
        rows = cursor.fetchall()
    
    # Insert data into the Treeview
        for row in rows:
        # Format the sale date
            sale_date = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M')
            tree.insert("", tk.END, values=(row[0], row[1], sale_date))
    
    # Add a scrollbar
        scrollbar = ttk.Scrollbar(sales_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
    
    def create_tables(self):
        cursor = self.conn.cursor()
        # Create inventory table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        # Create sales table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            quantity_sold INTEGER NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def create_frames(self):
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Left frame for inventory management
        self.inventory_frame = ttk.LabelFrame(self.root, text="Inventory Management")
        self.inventory_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Right frame for sales
        self.sales_frame = ttk.LabelFrame(self.root, text="Sales Entry")
        self.sales_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Bottom frame for low stock warnings
        self.warning_frame = ttk.LabelFrame(self.root, text="Low Stock Warnings")
        self.warning_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Create warning label
        self.warning_label = ttk.Label(self.warning_frame, text="", foreground="red")
        self.warning_label.pack(padx=5, pady=5)

    def create_inventory_widgets(self):
        # Inventory input fields
        ttk.Label(self.inventory_frame, text="Medicine Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.medicine_name = ttk.Entry(self.inventory_frame, width=30)
        self.medicine_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity = ttk.Entry(self.inventory_frame, width=30)
        self.quantity.grid(row=1, column=1, padx=5, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(self.inventory_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add/Update Stock", command=self.add_update_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Current Stock", command=self.view_stock).pack(side=tk.LEFT, padx=5)

    def create_sales_widgets(self):
        # Sales input fields
        ttk.Label(self.sales_frame, text="Select Medicine:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Medicine selection frame
        selection_frame = ttk.Frame(self.sales_frame)
        selection_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Create Listbox for selection
        self.medicine_listbox = tk.Listbox(selection_frame, width=30, height=5)
        self.medicine_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar to Listbox
        scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=self.medicine_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.medicine_listbox.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.medicine_listbox.bind('<<ListboxSelect>>', self.on_medicine_select)

        # Refresh button
        ttk.Button(selection_frame, text="Refresh", width=8, command=self.update_medicine_list).pack(side=tk.RIGHT, padx=2)

        # Selected medicine label
        self.selected_medicine_label = ttk.Label(self.sales_frame, text="Selected: None", font=('Arial', 10, 'bold'))
        self.selected_medicine_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Current stock label
        self.current_stock_label = ttk.Label(self.sales_frame, text="Current Stock: -")
        self.current_stock_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        ttk.Label(self.sales_frame, text="Quantity to Sell:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.sale_quantity = ttk.Entry(self.sales_frame, width=30)
        self.sale_quantity.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.sales_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Record Sale", command=self.record_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Sales Report", command=self.view_sales).pack(side=tk.LEFT, padx=5)

        # Initial update of medicine list
        self.update_medicine_list()

    def update_medicine_list(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT medicine_name FROM inventory ORDER BY medicine_name")
        medicines = cursor.fetchall()

        # Clear the listbox
        self.medicine_listbox.delete(0, tk.END)

        # Add medicines to listbox
        for medicine in medicines:
            self.medicine_listbox.insert(tk.END, medicine[0])

        if not medicines:
            self.warning_label.config(text="No medicines in inventory. Please add some first.")

    def on_medicine_select(self, event=None):
        if not self.medicine_listbox.curselection():
            return

        selected_index = self.medicine_listbox.curselection()[0]
        selected_medicine = self.medicine_listbox.get(selected_index)

        # Update selected medicine label
        self.selected_medicine_label.config(text=f"Selected: {selected_medicine}")

        # Update current stock label
        cursor = self.conn.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE medicine_name = ?", (selected_medicine,))
        result = cursor.fetchone()
        if result:
            self.current_stock_label.config(text=f"Current Stock: {result[0]}")

    def add_update_stock(self):
        name = self.medicine_name.get().strip()
        try:
            qty = int(self.quantity.get())
            if qty <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        if not name:
            messagebox.showerror("Invalid Input", "Medicine name cannot be empty.")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM inventory WHERE medicine_name = ?", (name,))
        result = cursor.fetchone()

        if result:
            cursor.execute('''
            UPDATE inventory
            SET quantity = quantity + ?, last_updated = ?
            WHERE medicine_name = ?
            ''', (qty, datetime.now(), name))
        else:
            cursor.execute('''
            INSERT INTO inventory (medicine_name, quantity, last_updated)
            VALUES (?, ?, ?)
            ''', (name, qty, datetime.now()))

        self.conn.commit()
        messagebox.showinfo("Success", "Stock updated successfully!")
        self.update_medicine_list()

    def record_sale(self):
        if not self.medicine_listbox.curselection():
            messagebox.showerror("Error", "Please select a medicine first.")
            return

        selected_index = self.medicine_listbox.curselection()[0]
        medicine_name = self.medicine_listbox.get(selected_index)

        try:
            quantity_sold = int(self.sale_quantity.get())
            if quantity_sold <= 0:
                messagebox.showerror("Error", "Quantity must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity to sell.")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE medicine_name = ?", (medicine_name,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Medicine not found in inventory.")
            return

        current_stock = result[0]
        if quantity_sold > current_stock:
            messagebox.showerror("Error", f"Insufficient stock! Only {current_stock} units available.")
            return

        try:
        # Record the sale in the sales table
            cursor.execute('''
                INSERT INTO sales (medicine_name, quantity_sold, sale_date)
                VALUES (?, ?, ?)
            ''', (medicine_name, quantity_sold, datetime.now()))

        # Update the inventory to reflect the sold quantity
            cursor.execute('''
                UPDATE inventory
                SET quantity = quantity - ?, last_updated = ?
                WHERE medicine_name = ?
            ''', (quantity_sold, datetime.now(), medicine_name))

            self.conn.commit()

            messagebox.showinfo("Success", "Sale recorded successfully!")

        # Refresh the selected medicine stock and clear input
            self.on_medicine_select()
            self.sale_quantity.delete(0, tk.END)

        # Check for low stock after the sale
            self.check_low_stock()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred while recording the sale: {str(e)}")

    def check_low_stock(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT medicine_name, quantity FROM inventory WHERE quantity <= 5")
        low_stock_items = cursor.fetchall()

        if low_stock_items:
            warnings = "\n".join([f"{name}: {qty} left" for name, qty in low_stock_items])
            self.warning_label.config(text=warnings)
        else:
            self.warning_label.config(text="All stocks are sufficient.")

    def on_close(self):
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalShopInventory(root)
    root.mainloop()