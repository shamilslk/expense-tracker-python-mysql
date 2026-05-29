import tkinter as tk
from tkinter import ttk
import mysql.connector
import tkinter.messagebox as messagebox
from datetime import date
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv

def search_expenses(event = None):
    keyword = search_entry.get()

    query = """
    SELECT * FROM expenses
    WHERE title LIKE %s OR category LIKE %s
    """

    values = (f"%{keyword}%", f"%{keyword}%")

    cursor.execute(query, values)

    rows = cursor.fetchall()

    # CLEAR OLD DATA
    for row in expense_table.get_children():
        expense_table.delete(row)

    for row in rows:
        expense_table.insert("", tk.END, values=row)

def export_csv():

    cursor.execute("SELECT * FROM expenses")

    rows = cursor.fetchall()

    with open("expenses.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(
            ["ID", "Title", "Amount", "Category", "Date"]
        )

        writer.writerows(rows)

def show_pie_chart():

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)

    data = cursor.fetchall()

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    # Clear previous chart
    for widget in chart_frame.winfo_children():
        widget.destroy()

    fig = Figure(
    figsize=(3.5,3.5),
    dpi=100,
    facecolor="#f0f0f0"
)
    fig.tight_layout()

    ax = fig.add_subplot(111)
    ax.set_facecolor("#f0f0f0")

    ax.pie(
    amounts,
    labels=categories,
    autopct="%1.1f%%",
    wedgeprops={"width": 0.6, "edgecolor": "w"},
    textprops={"color": "#333333", "fontsize": 10}
)

    ax.set_title("Expenses by Category")

    canvas = FigureCanvasTkAgg(
        fig,
        master=chart_frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack()

sort_by={
    "ID": "id",
    "Amount (Low to High)": "amount ASC",
    "Amount (High to Low)": "amount DESC",
    "Date (Newest)": "expense_date DESC",
    "Date (Oldest)": "expense_date ASC"
}
selected_expense_id = None
total_expenses = 0

def update_stats():

    cursor.execute(
        "SELECT SUM(amount) FROM expenses"
    )

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    total_label.config(
        text=f"Total Expense: ₹{total}"
    )

    cursor.execute(
        "SELECT COUNT(amount) FROM expenses"
    )

    count = cursor.fetchone()[0]

    if count is None:
        count = 0

    count_label.config(
        text=f"Number of Expenses: {count}"
    )

    cursor.execute(
        "SELECT MAX(amount) FROM expenses"
    )

    max_amount = cursor.fetchone()[0]

    if max_amount is None:
        max_amount = 0

    max_amount_label.config(
        text=f"Max Expense: ₹{max_amount}"
    )

    cursor.execute(
        "SELECT AVG(amount) FROM expenses"
    )

    avg_amount = cursor.fetchone()[0]

    if avg_amount is None:
        avg_amount = 0

    avg_amount_label.config(
        text=f"AVG Expense: ₹{avg_amount:.2f}"
    )

def update_expense():

    global selected_expense_id

    if selected_expense_id is None:

        messagebox.showwarning(
            "Warning",
            "Select an expense first"
        )

        return

    title = title_entry.get()
    amount = amount_entry.get()
    category = category_select.get()
    expense_date = date_entry.get()

    query = """
    UPDATE expenses
    SET title=%s,
        amount=%s,
        category=%s,
        expense_date=%s
    WHERE id=%s
    """

    values = (
        title,
        amount,
        category,
        expense_date,
        selected_expense_id
    )

    cursor.execute(query, values)

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Expense Updated Successfully"
    )

    show_pie_chart()
    update_stats()
    load_expenses()

def select_expense(event):

    global selected_expense_id

    selected_item = expense_table.selection()

    if not selected_item:
        return

    item = expense_table.item(selected_item)

    row = item["values"]

    selected_expense_id = row[0]

    # CLEAR OLD INPUTS
    title_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_select.set("Other")
    date_entry.delete(0, tk.END)

    # INSERT SELECTED VALUES
    title_entry.insert(0, row[1])
    amount_entry.insert(0, row[2])
    category_select.set(row[3])
    date_entry.insert(0, row[4])

def load_expenses():

    # CLEAR OLD DATA
    for row in expense_table.get_children():
        expense_table.delete(row)
    if category_filter.get() == "All":

        query = f"SELECT * FROM expenses ORDER BY {sort_by[sort.get()]}"

        cursor.execute(query)

    else:

        query = f"SELECT * FROM expenses WHERE category = %s ORDER BY {sort_by[sort.get()]}"

        values = (category_filter.get(),)

        cursor.execute(query, values)

    rows = cursor.fetchall()

    for row in rows:
        expense_table.insert("", tk.END, values=row)

    
    


def add_expense():

    title = title_entry.get()
    amount = amount_entry.get()
    category = category_select.get()
    expense_date = date_entry.get()

    query = """
    INSERT INTO expenses (title, amount, category, expense_date)
    VALUES (%s, %s, %s, %s)
    """

    values = (title, amount, category, expense_date)

    cursor.execute(query, values)

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Expense Added Successfully"
    )

    title_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_select.set("Other")
    date_entry.delete(0, tk.END)
    date_entry.insert(0, date.today())

    show_pie_chart()
    update_stats()
    load_expenses()

def delete_expense():

    selected_item = expense_table.selection()

    if not selected_item:
        messagebox.showwarning(
            "Warning",
            "Select an expense first"
        )
        return

    item = expense_table.item(selected_item)

    expense_id = item["values"][0]

    query = "DELETE FROM expenses WHERE id = %s"

    values = (expense_id,)

    cursor.execute(query, values)

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Expense Deleted Successfully"
    )

    show_pie_chart()
    load_expenses()
    update_stats()

def reload_expenses():
    show_pie_chart()
    load_expenses()
    update_stats()
def filter_expenses(event):
    load_expenses()


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="expense_tracker"
)

cursor = conn.cursor()

window = tk.Tk()

window.title("Expense Tracker")
window.geometry("1200x700")

# =====================
# TOP SECTION
# =====================
title = tk.Label(
    window,
    text="Expense Tracker Dashboard",
    font=("Consolas", 20, "bold"),
    fg="#333333"
)

title.pack(pady=10)

top_frame = tk.Frame(window)
top_frame.pack(pady=1)

form_frame = tk.Frame(top_frame)
form_frame.pack(side="left", padx=30)

stats_frame = tk.LabelFrame(
    top_frame,
    text="Statistics",
    padx=5,
    pady=5
)
stats_frame.pack(side="left", padx=40)

chart_frame = tk.Frame(top_frame)
chart_frame.pack(pady=1)


# =====================
# FORM
# =====================


title_label = tk.Label(form_frame, text="Title")
title_label.grid(row=0, column=0, padx=5, pady=5)

title_entry = tk.Entry(form_frame)
title_entry.grid(row=0, column=1, padx=5, pady=5)

amount_label = tk.Label(form_frame, text="Amount")
amount_label.grid(row=1, column=0, padx=5, pady=5)

amount_entry = tk.Entry(form_frame)
amount_entry.grid(row=1, column=1, padx=5, pady=5)

category_label = tk.Label(form_frame, text="Category")
category_label.grid(row=2, column=0, padx=5, pady=5)

category_select = ttk.Combobox(
    form_frame,
    values=["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]
)
category_select.set("Other")
category_select.grid(row=2, column=1, padx=5, pady=5)

date_label = tk.Label(form_frame, text="Date")
date_label.grid(row=3, column=0, padx=5, pady=5)

date_entry = tk.Entry(form_frame)
date_entry.grid(row=3, column=1, padx=5, pady=5)

date_entry.insert(0, str(date.today()))

# =====================
# BUTTONS
# =====================

add_button = tk.Button(
    form_frame,
    text="Add Expense",
    command=add_expense
)
add_button.grid(row=4, column=0, pady=10)

update_button = tk.Button(
    form_frame,
    text="Update Expense",
    command=update_expense
)
update_button.grid(row=4, column=1, pady=10)

delete_button = tk.Button(
    form_frame,
    text="Delete Expense",
    command=delete_expense
)
delete_button.grid(row=5, column=0, pady=10)

reload_button = tk.Button(
    form_frame,
    text="Reload Expenses",
    command=reload_expenses
)
reload_button.grid(row=5, column=1, pady=10)

# =====================
# STATISTICS
# =====================

total_label = tk.Label(
    stats_frame,
    text="Total Expense: ₹0",
    font=("Arial", 14)
)
total_label.pack(anchor="w", pady=5)

count_label = tk.Label(
    stats_frame,
    text="Number of Expenses: 0",
    font=("Arial", 14)
)
count_label.pack(anchor="w", pady=5)

max_amount_label = tk.Label(
    stats_frame,
    text="Max Expense: ₹0",
    font=("Arial", 14)
)
max_amount_label.pack(anchor="w", pady=5)

avg_amount_label = tk.Label(
    stats_frame,
    text="AVG Expense: ₹0",
    font=("Arial", 14)
)
avg_amount_label.pack(anchor="w", pady=5)

# =====================
# FILTER
# =====================

filter_frame = tk.Frame(window)
filter_frame.pack(pady=10)

filter_label = tk.Label(filter_frame, text="Filter")
filter_label.grid(row=0, column=0, padx=10, pady=5)

category_filter = ttk.Combobox(
    filter_frame,
    values=["All", "Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]
)

category_filter.set("All")
category_filter.grid(row=1, column=0, padx=10)

category_filter.bind(
    "<<ComboboxSelected>>",
    filter_expenses
)

sort_label = tk.Label(filter_frame, text="Sort By")
sort_label.grid(row=0, column=1, padx=10, pady=5)

sort = ttk.Combobox(
    filter_frame,
    values=["ID",
        "Amount (Low to High)",
        "Amount (High to Low)",
        "Date (Newest)",
        "Date (Oldest)"]
)

sort.set("ID")
sort.grid(row=1, column=1, padx=10)

sort.bind(
    "<<ComboboxSelected>>",
    filter_expenses
)

search_label = tk.Label(filter_frame, text="Search")
search_label.grid(row=0, column=3, padx=10, pady=5)

search_entry = tk.Entry(filter_frame)
search_entry.grid(row=1, column=3, padx=5, pady=5)

search_entry.bind(
    "<KeyRelease>",
    search_expenses
)

csv_button = tk.Button(
    form_frame,
    text="Export to CSV",
    command=export_csv
)

csv_button.grid(row=4, column=3, columnspan=2, pady=10)

# =====================
# TABLE
# =====================

expense_table = ttk.Treeview(
    window,
    columns=("ID", "Title", "Amount", "Category", "Date"),
    show="headings"
)

expense_table.heading("ID", text="ID")
expense_table.heading("Title", text="Title")
expense_table.heading("Amount", text="Amount")
expense_table.heading("Category", text="Category")
expense_table.heading("Date", text="Date")

expense_table.column("ID", width=60)
expense_table.column("Title", width=250)
expense_table.column("Amount", width=120)
expense_table.column("Category", width=150)
expense_table.column("Date", width=150)

expense_table.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

expense_table.bind(
    "<<TreeviewSelect>>",
    select_expense
)
window.mainloop()
