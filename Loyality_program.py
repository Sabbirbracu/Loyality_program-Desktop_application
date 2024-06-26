import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import datetime, timedelta
import tkinter
from tkinter import filedialog
import webbrowser

# Database connection function
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="EasyMove2024",
        database="loyalty_program"
    )

# Function to load and display points of a customer
def load_points(phone):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, points FROM customers WHERE phone_number = %s", (phone,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result
    else:
        return None  # Return None if no account is found

# Function to handle the confirm button click
def confirm_purchase():
    conn = create_connection()
    cursor = conn.cursor()

    phone = phone_entry.get().strip()
    purchase_amount = purchase_entry.get().strip()
    redeem_points = redeem_points_entry.get().strip()

    if phone:
        customer_data = load_points(phone)
        if customer_data is None:
            messagebox.showerror("Account Error", "Oops! There is no account associated with this phone number.")
            return
        
        customer_id, current_points = customer_data

        # Show warning if purchase amount is not provided
        if not purchase_amount:
            update_summary_label(phone, 0, 0, 0, current_points, 0)
            return

        try:
            purchase_amount = float(purchase_amount)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid purchase amount.")
            return
        
        # Handle redeem points input
        if redeem_points:
            try:
                redeem_points = float(redeem_points)
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid redeem points amount.")
                return
        else:
            redeem_points = 0

        if redeem_points > current_points or (int(redeem_points) > 0 and int(redeem_points) < 100):
            messagebox.showerror("Points Error", "You don't have enough points to redeem.")
            return
        
        cursor.execute("SELECT SUM(purchase_amount) FROM purchases WHERE customer_id = %s", (customer_id,))
        total_purchase_amount = cursor.fetchone()[0]

        if total_purchase_amount is None:
            total_purchase_amount = 0
        
        if total_purchase_amount <= 10000:
            points_earned = purchase_amount * 0.01
        else:
            points_earned = purchase_amount * 0.02
        
        total_points = current_points - redeem_points + points_earned
        payable_amount = purchase_amount - redeem_points
        
        # Update the database with new points
        cursor.execute("INSERT INTO purchases (customer_id, purchase_amount, Redeem_Points, Get_Points, purchase_date) VALUES (%s, %s, %s, %s, %s)", 
                       (customer_id, payable_amount, redeem_points, points_earned, datetime.now()))

        cursor.execute("UPDATE customers SET points = %s WHERE id = %s", (total_points, customer_id))
        conn.commit()
        cursor.close()
        conn.close()

        # Update the summary label with the purchase summary
        update_summary_label(phone, purchase_amount, points_earned, redeem_points, total_points, payable_amount)

        # clear_entries()  # Clear the input fields after showing the messagebox
    else:
        messagebox.showwarning("Input Error", "Please enter the phone number.")



# Function to update the summary label
def update_summary_label(phone, purchase_amount, points_earned, redeem_points, total_points, payable_amount):
    conn = create_connection()
    cursor = conn.cursor()

    # Retrieve customer's name and total purchase amount
    cursor.execute("SELECT name, points FROM customers WHERE phone_number = %s", (phone,))
    customer_data = cursor.fetchone()
    customer_name = customer_data[0]
    total_points = customer_data[1]

    cursor.execute("SELECT SUM(purchase_amount) FROM purchases WHERE customer_id = (SELECT id FROM customers WHERE phone_number = %s)", (phone,))
    total_purchase_amount = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    summary_text = f"Customer Summary:\n\n" \
                   f"Name: {customer_name}\n" \
                   f"Phone Number: {phone}\n" \
                   f"Today's Purchase Amount: {purchase_amount}\n" \
                   f"Points Earned from Today's Purchase: {points_earned}\n" \
                   f"Redeemed Points: {redeem_points}\n" \
                   f"Total Purchase Amount: {total_purchase_amount}\n" \
                   f"Total Points: {total_points}\n"\
                   f"Payable Amount: {payable_amount}"
    
    summary_label.configure(text=summary_text,font=("Helvetica", 15, "bold"))
    summary_label.pack(pady=10)

    close_button.pack(pady=10)

# Function to clear phone number and purchase amount entries
def clear_entries():
    phone_entry.delete(0, ctk.END)
    purchase_entry.delete(0, ctk.END)
    redeem_points_entry.delete(0, ctk.END)

# Function to clear signup entries
def clear_signup_entries():
    signup_phone_entry.delete(0, ctk.END)
    signup_name_entry.delete(0, ctk.END)


# Function to handle account creation
def create_account():
    clear_entries()
    phone = signup_phone_entry.get()
    name = signup_name_entry.get()
    if phone and name:
        conn = create_connection()
        cursor = conn.cursor()

        # Check if the phone number already exists
        cursor.execute("SELECT id FROM customers WHERE phone_number = %s", (phone,))
        result = cursor.fetchone()
        if result:
            messagebox.showerror("Account Error", "Already have an account with this number.")
            return

        cursor.execute("INSERT INTO customers (phone_number, name, points) VALUES (%s, %s, %s)", (phone, name, 0))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Account Created", "Account successfully created.")
        clear_signup_entries()  # Clear the signup entries after account creation
        switch_to_main(phone)
    else:
        messagebox.showwarning("Input Error", "Please enter both phone number and name.")

def switch_to_signup():
    """Switch to the signup frame."""
    signup_frame.pack(pady=20, padx=20)
    main_frame.pack_forget()
    sell_summary_frame.pack_forget()
    customer_summary_frame.pack_forget()
    bind_enter_key(create_account)  # Bind Enter key to create_account


def bind_enter_key(func):
    """Bind the Enter key to the given function."""
    root.bind('<Return>', lambda event: func())

def switch_to_main(phone=None):
    """Switch to the main frame."""
    main_frame.pack(fill="both", expand=True)
    if phone:
        phone_entry.insert(0, phone)
    signup_frame.pack_forget()
    sell_summary_frame.pack_forget()
    customer_summary_frame.pack_forget()
    bind_enter_key(confirm_purchase)  # Bind Enter key to confirm_purchase

# Function to handle the close button click
def close_summary():
    summary_label.pack_forget()
    clear_entries()
    close_button.pack_forget()

def switch_to_sell_summary():
    """Switch to the sell summary frame."""
    sell_summary_frame.pack(pady=20, padx=20)
    main_frame.pack_forget()
    signup_frame.pack_forget()
    customer_summary_frame.pack_forget()
    bind_enter_key(search_sell_summary)  # Bind Enter key to search_sell_summary

# Function to search sell summary between two dates
def search_sell_summary():
    from_date = from_date_entry.get()
    to_date = to_date_entry.get()

    # Convert the to_date to include all times on the to_date
    to_date = (datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, purchase_amount, Get_Points, Redeem_Points, purchase_date FROM purchases WHERE purchase_date >= %s AND purchase_date < %s",
                   (from_date, to_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for i in sell_result_table.get_children():
        sell_result_table.delete(i)

    for row in results:
        sell_result_table.insert("", "end", values=row)

def switch_to_customer_summary():
    """Switch to the customer summary frame."""
    customer_summary_frame.pack(pady=20, padx=20)
    main_frame.pack_forget()
    signup_frame.pack_forget()
    sell_summary_frame.pack_forget()
    bind_enter_key(search_customer_summary)  # Bind Enter key to search_customer_summary

# Function to search customer summary by phone number
def search_customer_summary():
    phone_number = customer_phone_entry.get()

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT c.name, p.purchase_amount, p.Get_Points, p.Redeem_Points, c.points, p.purchase_date FROM customers c "
                   "JOIN purchases p ON c.id = p.customer_id WHERE c.phone_number = %s", (phone_number,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for i in customer_result_table.get_children():
        customer_result_table.delete(i)

    for row in results:
        customer_result_table.insert("", "end", values=row)


def hide_all_frames():
    for frame in (main_frame, signup_frame, sell_summary_frame, customer_summary_frame):
        frame.pack_forget()

def resize_window(size="3/4"):
    if size == "full":
        root.attributes('-fullscreen', True)
    else:
        root.attributes('-fullscreen', False)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.95)
        root.geometry(f"{window_width}x{window_height}")

def main():
    global root, phone_entry, purchase_entry, redeem_points_entry, summary_label, close_button
    global signup_phone_entry, signup_name_entry, from_date_entry, to_date_entry, sell_result_table
    global customer_phone_entry, customer_result_table, main_frame, signup_frame, sell_summary_frame, customer_summary_frame
    root = ctk.CTk()
    root.title("Customer Loyalty Program")
    resize_window(size="3/4")  # Default window size to 3/4

    # Create frames for different sections
    main_frame = ctk.CTkFrame(root)
    signup_frame = ctk.CTkFrame(root)
    sell_summary_frame = ctk.CTkFrame(root)
    customer_summary_frame = ctk.CTkFrame(root)

    # Add footer to each frame
    add_footer(main_frame)
    add_footer(signup_frame)
    add_footer(sell_summary_frame)
    add_footer(customer_summary_frame)

    # Main frame widgets
    heading_label = ctk.CTkLabel(main_frame, text="Welcome to the Customer Loyalty Program", font=("Helvetica", 20, "bold"), fg_color="blue")
    heading_label.pack(pady=20)

    phone_label = ctk.CTkLabel(main_frame, text="Phone Number:", font=("Helvetica", 15, "bold"))
    phone_label.pack(pady=5)
    phone_entry = ctk.CTkEntry(main_frame, placeholder_text="Type customer phone number", width=200)
    phone_entry.pack(pady=5)

    purchase_label = ctk.CTkLabel(main_frame, text="Purchase Amount:", font=("Helvetica", 15, "bold"))
    purchase_label.pack(pady=5)
    purchase_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter the amount", width=200)
    purchase_entry.pack(pady=5)

    redeem_points_label = ctk.CTkLabel(main_frame, text="Redeem Points:", font=("Helvetica", 15, "bold"))
    redeem_points_label.pack(pady=5)
    redeem_points_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter points if you have", width=200)
    redeem_points_entry.pack(pady=5)

    confirm_button = ctk.CTkButton(main_frame, text="Confirm", command=confirm_purchase)
    confirm_button.pack(pady=10)

    summary_label = ctk.CTkLabel(main_frame, text="", wraplength=400)
    close_button = ctk.CTkButton(main_frame, text="Close", command=close_summary)

    # Buttons for Sell Summary and Customer Summary
    summary_buttons_frame = ctk.CTkFrame(main_frame)
    summary_buttons_frame.pack(pady=10)

    switch_to_sell_summary_button = ctk.CTkButton(summary_buttons_frame, text="Sell Summary", font=("Helvetica", 15, "bold"), command=switch_to_sell_summary, fg_color="red")
    switch_to_sell_summary_button.grid(row=0, column=0, padx=5, pady=5)

    switch_to_customer_summary_button = ctk.CTkButton(summary_buttons_frame, text="Customer Summary", font=("Helvetica", 15, "bold"), command=switch_to_customer_summary, fg_color="green")
    switch_to_customer_summary_button.grid(row=0, column=1, padx=5, pady=5)

    # Pack the frame containing the buttons
    summary_buttons_frame.pack()

    switch_to_signup_button = ctk.CTkButton(root, text="Create Account", command=switch_to_signup)
    switch_to_signup_button.pack(pady=5, padx=10, anchor="ne")
    # Sign up frame widgets
    signup_label = ctk.CTkLabel(signup_frame, text="Create a New Account", font=("Helvetica", 18))
    signup_label.pack(pady=10)

    signup_phone_label = ctk.CTkLabel(signup_frame, text="Phone Number:")
    signup_phone_label.pack(pady=5)
    signup_phone_entry = ctk.CTkEntry(signup_frame, placeholder_text="Enter Customer Phone number")
    signup_phone_entry.pack(pady=5)

    signup_name_label = ctk.CTkLabel(signup_frame, text="Name:")
    signup_name_label.pack(pady=5)
    signup_name_entry = ctk.CTkEntry(signup_frame, placeholder_text="Enter Customer Name")
    signup_name_entry.pack(pady=5)

    create_account_button = ctk.CTkButton(signup_frame, text="Create Account", command=create_account)
    create_account_button.pack(pady=10)

    back_button = ctk.CTkButton(signup_frame, text="Back", command=switch_to_main)
    back_button.pack(pady=5)

    # Back button in the top-left corner of the window
    back_button = ctk.CTkButton(sell_summary_frame, text="Back", command=switch_to_main)
    back_button.pack(side="top", anchor="nw", padx=10, pady=10)

    # Sell summary frame widgets
    sell_summary_label = ctk.CTkLabel(sell_summary_frame, text="The Selling Summary", font=("Helvetica", 26, "bold"), text_color="Light Blue")
    sell_summary_label.pack(pady=10)

    # Create a new frame within sell_summary_frame for grid management
    date_frame = ctk.CTkFrame(sell_summary_frame)
    date_frame.pack(pady=10)

    from_date_label = ctk.CTkLabel(date_frame, text="From Date (YYYY-MM-DD):", font=("Helvetica", 13, "bold"))
    from_date_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")

    from_date_entry = ctk.CTkEntry(date_frame)
    from_date_entry.grid(row=0, column=1, pady=5, padx=5)

    to_date_label = ctk.CTkLabel(date_frame, text="To Date (YYYY-MM-DD):", font=("Helvetica", 13, "bold"))
    to_date_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")

    to_date_entry = ctk.CTkEntry(date_frame)
    to_date_entry.grid(row=1, column=1, pady=5, padx=5)

    search_button = ctk.CTkButton(sell_summary_frame, text="Search", command=search_sell_summary)
    search_button.pack(pady=10)

    # Add the "Print" button
    print_button = ctk.CTkButton(sell_summary_frame, text="Print", command=download_csv)
    print_button.pack(pady=10)

    # Define styles for the sell table
    sell_style = ttk.Style()
    sell_style.configure("sell.Treeview.Heading",
                         background="lightgreen",
                         foreground="grey",
                         relief="flat",
                         font=("Helvetica", 14, "bold"))  # Increased font size for headings
    sell_style.configure("sell.Treeview",
                         font=("Helvetica", 12))  # Increased font size for data rows

    Column_name = ("Customer ID", "Purchase Amount", "Got Points", "Redeem Points", "Purchase Date")
    sell_result_table = ttk.Treeview(sell_summary_frame, style="sell.Treeview", columns=Column_name, show="headings", height=20)
    sell_result_table.heading("Customer ID", text="Customer ID")
    sell_result_table.heading("Purchase Amount", text="Purchase Amount")
    sell_result_table.heading("Got Points", text="Got Points")
    sell_result_table.heading("Redeem Points", text="Redeem Points")
    sell_result_table.heading("Purchase Date", text="Purchase Date")

    # Align the content of each column in the center
    for col in Column_name:
        sell_result_table.column(col, anchor="center")

    sell_result_table.pack(fill=tkinter.BOTH, expand=True, pady=10)

    # Back button in the top-left corner of the window
    back_button = ctk.CTkButton(customer_summary_frame, text="Back", command=switch_to_main)
    back_button.pack(side="top", anchor="nw", padx=10, pady=10)

    # Customer summary frame widgets
    customer_summary_label = ctk.CTkLabel(customer_summary_frame, text="Customer Summary", font=("Helvetica", 26, "bold"), text_color="Light Blue")
    customer_summary_label.pack(pady=10)

    customer_phone_label = ctk.CTkLabel(customer_summary_frame, text="Phone Number:", font=("Helvetica", 13, "bold"))
    customer_phone_label.pack(pady=5)
    customer_phone_entry = ctk.CTkEntry(customer_summary_frame, placeholder_text="Enter Customer Phone number")
    customer_phone_entry.pack(pady=5)

    search_customer_button = ctk.CTkButton(customer_summary_frame, text="Search", command=search_customer_summary)
    search_customer_button.pack(pady=10)


# Define styles for the customer table
    customer_style = ttk.Style()
    customer_style.configure("customer.Treeview.Heading",
                             background="lightgreen",
                             foreground="grey",
                             relief="flat",
                             font=("Helvetica", 14, "bold"))  # Increased font size for headings
    customer_style.configure("customer.Treeview",
                             font=("Helvetica", 12))  # Increased font size for data rows

    customer_table_columns = ("Name", "Purchase Amount", "Get Points", "Redeem Points", "Total Points", "Purchase Date")
    customer_result_table = ttk.Treeview(customer_summary_frame, style="customer.Treeview", columns=customer_table_columns, show="headings", height=20)
    customer_result_table.heading("Name", text="Name")
    customer_result_table.heading("Purchase Amount", text="Purchase Amount")
    customer_result_table.heading("Get Points", text="Get Points")
    customer_result_table.heading("Redeem Points", text="Redeem Points")
    customer_result_table.heading("Total Points", text="Total Points")
    customer_result_table.heading("Purchase Date", text="Purchase Date")

    # Align the content of each column in the center
    for col in customer_table_columns:
        customer_result_table.column(col, anchor="center")

    customer_result_table.pack(fill=tkinter.BOTH, expand=True, pady=10)

    # Start with the main frame visible
    switch_to_main()

    root.mainloop()

def download_csv():
    import csv

    # Open a file dialog to choose the destination file
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if filename:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write the header row
            writer.writerow(["Customer ID", "Purchase Amount", "Get Points", "Redeem Points", "Purchase Date"])

            # Write the data rows
            for row_id in sell_result_table.get_children():
                row_data = sell_result_table.item(row_id)["values"]
                writer.writerow(row_data)

        messagebox.showinfo("CSV Saved", "CSV file saved successfully.")

def download_csv_customer_summary():
    import csv
    # Ask for a file path to save the CSV
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if filename:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Purchase Amount", "Get Points", "Redeem Pints", "Total Points", "Purchase Date"])  # Write headers

            # Write customer summary data
            for row in customer_result_table.get_children():
                row_data = customer_result_table.item(row)["values"]
                writer.writerow(row_data)

def add_footer(frame):
    footer_frame = ctk.CTkFrame(frame)
    footer_frame.pack(side="bottom", pady=5, fill="x")
    # Contact information
    contact_label = ctk.CTkLabel(footer_frame, text="Contact us at: sabbirahmad653@gmail.com", font=("Helvetica", 13, "italic", "bold"))
    contact_label.pack(side="left", padx=10)

    # Privacy policy
    privacy_label = ctk.CTkLabel(footer_frame, text="Privacy Policy", font=("Helvetica", 13, "italic", "bold"))
    privacy_label.pack(side="left", padx=10)

    # Version number
    version_label = ctk.CTkLabel(footer_frame, text="Version 1.0", font=("Helvetica", 13, "italic", "bold"))
    version_label.pack(side="right", padx=10)

    # Social media links (assuming you have icons for these)
    social_media_frame = ctk.CTkFrame(footer_frame)
    social_media_frame.pack(side="right", padx=10)

    linkedin_icon = ctk.CTkLabel(social_media_frame, text="LinkedIn", width=20, height=20, fg_color="blue")
    linkedin_icon.pack(side="left", padx=5)
    linkedin_icon.bind("<Button-1>", lambda e: open_linkedin())

    # Developed by Qullia
    developed_by_label = ctk.CTkLabel(footer_frame, text="Developed by Qullia", font=("Helvetica", 13, "italic","bold"))
    developed_by_label.pack(side="right", padx=10)

def open_linkedin():
    webbrowser.open("https://www.linkedin.com/company/qullia/?originalSubdomain=bd")

if __name__ == "__main__":
    main()
