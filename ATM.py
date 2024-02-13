import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
import psycopg2
import random
from datetime import date, timedelta


class ATM:
    def __init__(self, app):
        ctk.set_appearance_mode("dark")
        self.app = app
        self.app.geometry("400x400")
        self.app.title("Adams ATM")

        self.show_frame = True

        self.login_frame = None

        self.login_menu()

        # Connecting to the DB using a try block
        try:
            self.connection = psycopg2.connect(
                dbname="ATM",
                user="postgres",
                password="Bearcat",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
        except psycopg2.Error as e:
            print("Error connecting to the database: ", e)

        self.create_tables()

        # SQL creating tables

    def create_tables(self):  # Creating SQL tables
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id SERIAL PRIMARY KEY,
                        username VARCHAR,
                        password VARCHAR,
                        full_name VARCHAR,
                        created_at TIMESTAMP
                    )
                ''')

        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS accounts (
                        account_id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(user_id),
                        account_number SERIAL,
                        balance DECIMAL,
                        account_type VARCHAR
                    )
                ''')

        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(user_id),
                        account_id INT REFERENCES accounts(account_id),
                        transaction_type VARCHAR,
                        amount DECIMAL,
                        transaction_date TIMESTAMP
                    )
                ''')

        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS locations (
                        location_id SERIAL PRIMARY KEY,
                        location_name VARCHAR,
                        address VARCHAR
                    )
                ''')

        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS card (
                        card_id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(user_id),
                        card_number VARCHAR,
                        expiration_date DATE,
                        cvv VARCHAR
                    )
                ''')

        self.connection.commit()

        # SQL STATEMENTS

    def get_curr_user(self):
        self.cursor.execute("SELECT user_id FROM users WHERE username = %s", (str(self.current_user),))
        return self.cursor.fetchone()

        # HIDING FRAME METHODS

    # To hide the creation frame
    def hide_create_ui(self):
        if self.create_frame:
            self.create_frame.destroy()
        self.login_menu()

    def go_back_depo(self):  # Go back to main menu from depo
        if self.depo_frame:
            self.depo_frame.destroy()
        self.main_frame.deiconify()

    def go_back_withdraw(self):
        if self.withdraw_frame:
            self.withdraw_frame.destroy()
        self.main_frame.deiconify()

    def go_back_transfer(self):
        if self.transfer_frame:
            self.transfer_frame.destroy()
        self.main_frame.deiconify()

    def go_back_card(self):
        if self.card_frame:
            self.card_frame.destroy()
        self.main_frame.deiconify()

    def go_back_account(self):
        if self.account_frame:
            self.account_frame.destroy()
        self.main_frame.deiconify()

        # LOGIC METHODS

    def toggle_password(self):  # Toggle password from hidden to shown
        self.show_password = not self.show_password
        if self.show_password:
            self.password.config(show="")
            self.eye_button.config(image=self.eye_icon)
        else:
            self.password.config(show="*")
            self.eye_button.config(image=self.eye_icon)

    def on_close(self):  # Closing the root from any window
        self.app.quit()

        # RANDOM NUMBER GENERATORS

    def generate_rand_num(self):  # Generate a random 8 digit number for the account number
        return str(random.randint(10000000, 99999999))

    def generate_card_num(self):  # Generate a random card number for the user
        return str(random.randint(1000000000000000, 9999999999999999))

    def generate_exp_date(self):
        today = date.today()

        max_years = 10

        end_date = today + timedelta(days=(365 * max_years))

        random_months = random.randint(0, 11)
        random_years = random.randint(0, max_years)

        expiration_date = today + timedelta(days=(random_years * 365 + random_months * 30))

        return expiration_date

    def generate_ccv(self):
        return str(random.randint(100, 999))

    def login(self):  # Method to login
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Missing Info, try again")
            return

        try:
            self.cursor.execute("SELECT password FROM users WHERE username = %s",
                                (username,))
            db_password = self.cursor.fetchone()

            if db_password and db_password[0] == password:
                self.current_user = username
                self.app.withdraw()
                self.password.delete(0, tk.END)

                # Main menu display
                self.main_menu(username)
            else:
                messagebox.showerror("Invalid username or password")

        except Exception as e:
            # TODO: POSSIBLE ERROR HERE DEALING WITH CTK ERROR, BAD SCREEN DISTANCE "SELECT AN OPTION"
            messagebox.showerror("HERE is the error", str(e))

    def create(self):  # Method to create a new user TODO: create method
        username = self.create_user_entry.get()
        password = self.create_password.get()
        full_name = self.full_name_entry.get()

        self.cursor.execute("SELECT username FROM users WHERE username = %s",
                            (username,))
        existing_user = self.cursor.fetchone()

        if existing_user:
            messagebox.showerror("Username already exists")
            return

        self.cursor.execute("INSERT INTO users (username, password, full_name) VALUES (%s, %s, %s)",
                            (username, password, full_name))
        self.connection.commit()
        messagebox.showinfo("Account created")

        self.create_frame.withdraw()
        self.login_menu()

        # MENU'S

    def login_menu(self):  # Login menu when first starting
        self.login_window = ctk.CTkToplevel(self.app)
        self.login_window.title("Login")
        self.login_window.geometry("325x375")
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.app.withdraw()

        # Main message for window
        self.label = ctk.CTkLabel(self.login_window, text="Welcome to Adams ATM")
        self.label.pack(pady=20)

        # Create a frame
        self.login_frame = ctk.CTkFrame(master=self.login_window)
        self.login_frame.pack(pady=20, padx=40, fill='both', expand=True)

        # Set Label inside of frame
        self.label = ctk.CTkLabel(master=self.login_frame, text="Adams ATM")
        self.label.pack(pady=12, padx=10)

        # Create text box for taking username input
        self.username = ctk.CTkEntry(master=self.login_frame, placeholder_text="Username")
        self.username.pack(pady=12, padx=10)

        # Create text box for taking password input
        self.password = ctk.CTkEntry(master=self.login_frame, placeholder_text="Password", show="*")
        self.password.pack(pady=12, padx=10)

        # Create a login button
        self.login_btn = ctk.CTkButton(master=self.login_frame, text='Login', command=self.login)
        self.login_btn.pack(pady=12, padx=10)

        # Create a create user link
        self.create_btn = ctk.CTkButton(master=self.login_frame, text='Create User', command=self.create_menu)
        self.create_btn.pack(pady=12, padx=10)

        # Bind the enter key to login
        self.password.bind("<Return>", lambda event: self.login())
        self.username.bind("<Return>", lambda event: self.login())

    def create_menu(self):
        self.login_window.withdraw()
        self.app.withdraw()
        self.create_frame = ctk.CTkToplevel(self.app)
        self.create_frame.geometry("300x225")
        self.create_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        # Full name label
        self.full_name = ctk.CTkEntry(master=self.create_frame, placeholder_text="Full Name")
        self.full_name.pack(pady=8, padx=4)

        # create username entry
        self.create_user_entry = ctk.CTkEntry(master=self.create_frame, placeholder_text="Username")
        self.create_user_entry.pack(pady=8, padx=4)

        # create password entry
        self.create_password = ctk.CTkEntry(self.create_frame, placeholder_text="Password", show="*")
        self.create_password.pack(pady=8, padx=4)

        # Create button to submit user creating
        self.create_sub = ctk.CTkButton(self.create_frame, text="create", command=self.create)
        self.create_sub.pack(pady=8, padx=4)

        # link to go back to the login frame
        self.back_login = ctk.CTkLabel(self.create_frame, text="Back to Login", cursor="hand2")
        self.back_login.pack(pady=8, padx=4)
        self.back_login.bind("<Button-1>", lambda event: self.hide_create_ui() and self.login_menu())

        # Apply styling to the back to login label
        self.back_login.configure(font=("Helvetica", 10, "underline"))

        # binds the enter key to submit button
        self.create_password.bind("<Return>", lambda event: self.create())

    def main_menu(self, current_user):  # screen to show when successfully logged in
        """1. Check balance
           2. Deposit
           3. withdraw
           4. transfer
           5. add card
           6. check locations
           0. exit
        """
        if hasattr(self, "main_frame"):
            self.main_frame.destroy()

        self.login_window.withdraw()

        self.main_frame = ctk.CTkToplevel(self.app)
        self.main_frame.geometry("500x500")
        self.main_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        self.get_curr_user()
        # Get accounts from the current user
        self.cursor.execute(
            "SELECT account_type FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s)",
            (str(self.current_user),))
        user_accounts = self.cursor.fetchall()
        account_types = [account[0] for account in user_accounts]
        # drop down to select account to deposit into

        account_types.insert(0, "Select an account")
        # TODO: POSSIBLE ERROR HERE DEALING WITH CTK ERROR, BAD SCREEN DISTANCE "SELECT AN OPTION"

        self.selected_option = tk.StringVar(self.main_frame)
        self.selected_option.set("Select an account")

        option_menu_style = ttk.Style()
        option_menu_style.configure("Custom.TMenubutton", background="grey", padding=5)
        option_menu_style.configure("Custom.TMenubutton.TButton", relief="flat")

        option_menu = ttk.OptionMenu(self.main_frame, self.selected_option, *account_types, style="Custom.TMenubutton")
        option_menu.pack(pady=8, padx=4)

        option_menu.bind("<ButtonRelease-1>",
                         lambda event, arg=self.selected_option: self.on_option(event, self.selected_option))

        # Display for current user
        self.current_user_label = ctk.CTkLabel(master=self.main_frame, text=current_user)
        self.current_user_label.pack(pady=8, padx=4)

        # check balance button
        self.bal_btn = ctk.CTkButton(master=self.main_frame, text="Balance", command=self.check_bal)
        self.bal_btn.pack(pady=8, padx=4)

        # Deposit button
        self.depo_btn = ctk.CTkButton(master=self.main_frame, text="Deposit", command=self.deposit_menu)
        self.depo_btn.pack(pady=8, padx=4)

        # Withdraw button
        self.with_btn = ctk.CTkButton(master=self.main_frame, text="Withdraw", command=self.withdraw_money_menu)
        self.with_btn.pack(pady=8, padx=4)

        # Transfer Button
        self.transfer_btn = ctk.CTkButton(master=self.main_frame, text="Transfer", command=self.transfer_menu)
        self.transfer_btn.pack(pady=8, padx=4)

        # Add a Card
        self.card_btn = ctk.CTkButton(master=self.main_frame, text="Add Card", command=self.add_card_menu)
        self.card_btn.pack(pady=8, padx=4)

        # Check the location's button
        self.locations_btn = ctk.CTkButton(master=self.main_frame, text="Locations", command=self.locations_menu)
        self.locations_btn.pack(pady=8, padx=4)

        # Open an account button
        self.account_btn = ctk.CTkButton(master=self.main_frame, text="Create Account",
                                         command=self.account_create_menu)
        self.account_btn.pack(pady=8, padx=4)

        # Exit/Logout button
        self.logout = ctk.CTkButton(master=self.main_frame, text="Logout", command=self.logout)
        self.logout.pack(pady=8, padx=4)

        # MAIN MENU METHODS

    # TODO: ALL METHODS ARE NOT FULLY FUNCTIONAL
    def check_bal(self):  # Method to check current users balance
        try:
            # Get users balance from database
            self.cursor.execute(
                "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
                # TODO: can only use once, then issues occur with drop down
                (str(self.current_user), self.selected_option.get()))
            user_balance = self.cursor.fetchone()

            if user_balance:
                # Display the-users balance
                messagebox.showinfo("Balance", f"Your current balance: ${user_balance[0]:.2f}")
            else:
                messagebox.showerror("Error", "Unable to retrieve")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def deposit_menu(self):  # Method to deposit money into users account
        # Deposit to display on main frame
        self.main_frame.withdraw()
        # Creating a new frame for deposit
        self.depo_frame = ctk.CTkToplevel(self.app)
        self.depo_frame.geometry("500x500")
        self.depo_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        # Amount entry box
        self.amount_entry = ctk.CTkEntry(master=self.depo_frame, placeholder_text="Amount")
        self.amount_entry.pack(pady=8, padx=4)
        # Get the current users id
        self.get_curr_user()

        self.submit_depo = ctk.CTkButton(master=self.depo_frame, text="Deposit", command=self.deposit)
        self.submit_depo.pack(pady=8, padx=4)

        self.back_arrow = ctk.CTkButton(master=self.depo_frame, text="Back", command=self.go_back_depo)
        self.back_arrow.pack(pady=8, padx=4)

    def deposit(self):  # Method to insert the money into the current users account
        # fetch the current user
        self.get_curr_user()
        selected_type = self.selected_option.get()
        # Getting the account id from the current user
        self.cursor.execute(
            "SELECT account_id FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(self.current_user), selected_type))
        account_id = self.cursor.fetchone()
        # SQL to grab the current balance from user
        self.cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(self.current_user), selected_type))
        balance_record = self.cursor.fetchone()
        # taking the tuple and moving it into an int variable
        balance = balance_record[0]

        # putting the amount to deposit into a variable
        depo_amt = self.amount_entry.get()

        # Updating by adding the amount from the current balance
        updated_balance = balance + int(depo_amt)

        # SQL to update the balance
        self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                            (updated_balance, account_id))

        # Message to how it is successful
        messagebox.showinfo("Success", f"${self.amount_entry.get()} deposited into account")

        # Insert transaction into the transaction table
        self.cursor.execute(
            "INSERT INTO transactions (user_id, account_id, transaction_type, amount) VALUES (%s, %s, %s, %s)",
            (self.get_curr_user(), (account_id), ("Deposit"), (depo_amt)))

        self.connection.commit()

    def withdraw_money_menu(self):  # Method to withdraw money from users account
        # Withdrawing the main window
        self.main_frame.withdraw()
        # Creating a new frame for withdrawing
        self.withdraw_frame = ctk.CTkToplevel(self.app)
        self.withdraw_frame.geometry("300x300")
        self.withdraw_frame.protocol("WM_DELETE_WINDOW", self.on_close)
        # Get the current users id
        self.get_curr_user()

        # Amount to withdraw label

        # Amount to withdraw entry
        self.withdraw_amount_entry = ctk.CTkEntry(self.withdraw_frame, placeholder_text="Amount")
        self.withdraw_amount_entry.pack(pady=8, padx=4)

        # Withdraw button to submit the withdraw
        self.withdraw_btn = ctk.CTkButton(self.withdraw_frame, text="Withdraw", command=self.withdraw_money)
        self.withdraw_btn.pack(pady=8, padx=4)

        self.back_arrow_with = ctk.CTkButton(self.withdraw_frame, text="Back", command=self.go_back_withdraw)
        self.back_arrow_with.pack(pady=8, padx=4)

    def withdraw_money(self):  # Method that actually subtracts the amount from the database
        # fetch the current user
        self.get_curr_user()
        selected_type = self.selected_option.get()
        # Getting the account id from the current user
        self.cursor.execute(
            "SELECT account_id FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(self.current_user), selected_type))
        account_id = self.cursor.fetchone()
        # Grabbing the current balance of the current user
        self.cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(self.current_user), selected_type))
        balance_record = self.cursor.fetchone()

        # taking the tuple var and turning it into an int
        balance = balance_record[0]

        # putting the amount to withdraw into a variable
        amt_to_withdraw = self.withdraw_amount_entry.get()

        # Updating by subtracting the amount from the current balance
        if int(amt_to_withdraw) > balance:
            messagebox.showerror("Insufficient funds", "Cannot take out more than what you have")
        else:
            updated_balance = balance - int(amt_to_withdraw)

            # SQL to withdraw money from the current account
            self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                                (updated_balance, account_id))

            messagebox.showinfo("Success", f"${self.withdraw_amount_entry.get()} withdrawn from account")

            # Insert the transaction into the transactions table
            self.cursor.execute(
                "INSERT INTO transactions (user_id, account_id, transaction_type, amount) VALUES (%s, %s, %s, %s)",
                (self.get_curr_user(), account_id, "Withdraw", self.withdraw_amount_entry.get()))

            self.connection.commit()

    def transfer_menu(
            self):  # Method to transfer funds from one account to another keep track or deposits and withdraws

        # Getting the ID of the current user
        self.get_curr_user()
        # Withdrawing the main frame
        self.main_frame.withdraw()

        # Creating a new frame for the transfer menu
        self.transfer_frame = ctk.CTkToplevel(self.app)
        self.transfer_frame.geometry('300x300')
        self.transfer_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        # Drop down menu to select a user to transfer money to, OR drop down to transfer from one account to another
        self.cursor.execute("SELECT username FROM users")
        users = self.cursor.fetchall()
        # taking the tuple and putting it into a list the menu can use
        user_list = [user[0] for user in users]
        # Drop down menu

        self.selected_user = tk.StringVar(self.transfer_frame)
        self.selected_user.set("Select a user")

        option_menu_style = ttk.Style()
        option_menu_style.configure("Custom.TMenubutton", background="grey", padding=5)
        option_menu_style.configure("Custom.TMenubutton.TButton", relief="flat")

        # Displaying the options in the drop-down menu
        option_menu = ttk.OptionMenu(self.transfer_frame, self.selected_user, *user_list, style="Custom.TMenubutton")
        option_menu.pack(pady=8, padx=4)

        self.selected_account = tk.StringVar(self.transfer_frame)
        self.selected_account.set("Select Account")

        options_menu = ttk.OptionMenu(self.transfer_frame, self.selected_account, "Select Account",
                                      style="Custom.TMenubutton")
        options_menu.pack(pady=8, padx=4)

        # Store a reference to the OptionMenu
        self.option_menu_account = options_menu

        # Bind trace to selected_user
        self.selected_user.trace_add("write", self.update_account_drop)

        self.transfer_amt_entry = ctk.CTkEntry(self.transfer_frame, placeholder_text="Amount")
        self.transfer_amt_entry.pack(pady=8, padx=4)

        self.submit_transfer = ctk.CTkButton(self.transfer_frame, text="Submit", command=self.transfer)
        self.submit_transfer.pack(pady=8, padx=4)

        self.back_btn = ctk.CTkButton(self.transfer_frame, text="Back", command=self.go_back_transfer)
        self.back_btn.pack(pady=8, padx=4)

    def update_account_drop(self, *args):
        # Get the selected user from the dropdown
        selected_user = self.selected_user.get()

        if selected_user != "Select a user":
            # Execute SQL query to fetch accounts for the selected user
            self.cursor.execute(
                "SELECT account_type FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s)",
                (str(selected_user),))
            accounts = self.cursor.fetchall()
            account_list = [account[0] for account in accounts]

            # Reset the "Select Account" option
            self.selected_account.set("Select Account")

            # Populate account dropdown with the retreived account_list
            self.populate_account_drop(account_list)
        else:
            # If "Select a user" is chosen, fetch accounts for current user
            curr_user = self.get_curr_user()
            self.cursor.execute(
                "SELECT account_type FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s)",
                (str(curr_user),))
            accounts = self.cursor.fetchall()
            account_list = [account[0] for account in accounts]

            # Reseting
            self.selected_account.set("Select Account")

            # Populating with new account_list
            self.populate_account_drop(account_list)

    def populate_account_drop(self, account_list):
        # Access the menu of the OptionMenu widget
        menu = self.option_menu_account["menu"]

        # Delete existing options in the menu
        menu.delete(0, "end")

        # Add new account option to the menu
        for account in account_list:
            # User lambda to set teh selected_account var when an account is chosen
            menu.add_command(label=account, command=lambda value=account: self.selected_account.set(value))

    def transfer(self):
        current_user = self.get_curr_user()  # Get the logged-in user
        selected_user = self.selected_user.get()  # Get the selected user
        selected_account = self.selected_account.get()  # Get the selected account
        transfer_amt = self.transfer_amt_entry.get()  # Get the amount to transfer
        selected_type = self.selected_option.get()  # Get the account they selected on the main menu

        # Get ID of the current account
        self.cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (self.get_curr_user()))
        account_id = self.cursor.fetchone()

        # Get current users balance
        self.cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(self.current_user), selected_type))
        curr_bal = self.cursor.fetchone()  # logged-in users balance
        # taking the tuple and making it a var that is usable
        current_balance = curr_bal[0]

        # Get the selected users balance from the selected account
        self.cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(selected_user), selected_account))
        sel_balance = self.cursor.fetchone()  # Selected users balance
        # Moving tuple
        selected_bal = sel_balance[0]

        # If else to ensure they have the funds to transfer
        if current_balance > int(transfer_amt):
            # Take amount out of current user and add it to the selected account and user
            current_balance -= int(transfer_amt)
            selected_bal += int(transfer_amt)
            self.cursor.execute(
                "UPDATE accounts SET balance = %s WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
                (current_balance, str(self.current_user), selected_type))
            self.cursor.execute(
                "UPDATE accounts SET balance = %s WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
                (selected_bal, str(selected_user), selected_account))
            messagebox.showinfo("Success", "Funds transferred")

            # Inputing transaction into the database
            self.cursor.execute(
                "INSERT INTO transactions (user_id, account_id, transaction_type, amount) VALUES (%s, %s, %s, %s)",
                (self.get_curr_user(), account_id, "Transfer", transfer_amt))
            self.connection.commit()
        else:
            messagebox.showerror("Error", "Do not have the funds to transfer (Will not let you transfer down to 0")

    def add_card_menu(self):  # Method to add a card to the users account
        # Withdrawing the main frame
        self.main_frame.withdraw()
        # Creating a new frame
        self.card_frame = ctk.CTkToplevel(self.app)
        self.card_frame.geometry("300x300")
        self.card_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        # Option to get a card by the bank, or to manually enter a card they already have.
        # Manually add an existing card

        # Card number entry
        self.card_num_entry = ctk.CTkEntry(self.card_frame, placeholder_text="Card Number")
        self.card_num_entry.pack(pady=8, padx=4)

        # Expiration date entry
        self.exp_date_entry = ctk.CTkEntry(self.card_frame, placeholder_text="Expiration Date")
        self.exp_date_entry.pack(pady=8, padx=4)

        # ccv entry
        self.ccv_entry = ctk.CTkEntry(self.card_frame, placeholder_text="CVV")
        self.ccv_entry.pack(pady=8, padx=4)
        # Submit button to enter the info
        self.submit_card_btn = ctk.CTkButton(self.card_frame, text="Submit", command=self.add_card)
        self.submit_card_btn.pack(pady=8, padx=4)
        # Generate a bank card
        self.generate_card_btn = ctk.CTkButton(self.card_frame, text="Generate", command=self.generate_card)
        self.generate_card_btn.pack(pady=8, padx=4)

        self.back_arrow_card = ctk.CTkButton(self.card_frame, text="Back", command=self.go_back_card)
        self.back_arrow_card.pack(pady=8, padx=4)

    def add_card(self):
        try:
            # getting the id of the current user, so we can use it to add the card to their account
            curr_id = self.get_curr_user()

            if curr_id:
                self.cursor.execute(
                    "INSERT INTO card (user_id, card_number, expiration_date, cvv) VALUES (%s, %s, %s, %s)",
                    (curr_id[0], self.card_num_entry.get(), self.exp_date_entry.get(), self.ccv_entry.get()))

                # Inserting into transaction table
                self.cursor.execute("INSERT INTO transactions (user_id, transaction_type) VALUES (%s, %s)",
                                    (self.get_curr_user(), "Add Card"))
                self.connection.commit()

                messagebox.showinfo("Card Added")
            else:
                messagebox.showerror("Error", "idk")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_card(self):
        try:
            # Getting the current users id
            curr_id = self.get_curr_user()

            print(f"{curr_id}")

            if curr_id:
                self.cursor.execute(
                    "INSERT INTO CARD (user_id, card_number, expiration_date, cvv) VALUES (%s, %s, %s, %s)",
                    (curr_id[0], self.generate_card_num(), self.generate_exp_date(), self.generate_ccv()))

                # Adding transaction to transactions table
                self.cursor.execute("INSERT INTO transactions (user_id, transaction_type) VALUES (%s, %s)",
                                    (self.get_curr_user(), "Card Generate"))
                self.connection.commit()

                messagebox.showinfo("Card is on its way")
            else:
                messagebox.showerror("Error", "idk")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def locations_menu(self):  # Method to display ATM locations TODO: IDK WTF TO DO HERE
        pass

    def account_create_menu(self):  # Method to open an account within the logged-in user
        # withdrawing the main frame
        self.main_frame.withdraw()
        # creating a new frame for the account creation
        self.account_frame = ctk.CTkToplevel(self.app)
        self.account_frame.geometry("300x300")
        self.account_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        selected_option = tk.StringVar(self.account_frame)
        selected_option.set("Select an option")

        options = ["Select an option", "Checking", "Savings"]

        option_menu_style = ttk.Style()
        option_menu_style.configure("Custom.TMenubutton", background="grey", padding=5)
        option_menu_style.configure("Custom.TMenubutton.TButton", relief="flat")

        option_menu = ttk.OptionMenu(self.account_frame, selected_option, *options, style="Custom.TMenubutton")
        option_menu.pack(pady=8, padx=4)

        option_menu.bind("<ButtonRelease-1>", lambda event: self.on_option(event, selected_option))

        self.type_entry = selected_option

        self.submit_btn = ctk.CTkButton(self.account_frame, text="Submit", command=self.create_account)
        self.submit_btn.pack(pady=8, padx=4)

        self.back_account = ctk.CTkButton(self.account_frame, text="Back", command=self.go_back_account)
        self.back_account.pack(pady=8, padx=4)

    def on_option(self, event, selected_option):  # Drop down
        selected_option = self.selected_option

    def create_account(self):
        try:
            # Fetching the user id and balance of the current logged-in user
            self.cursor.execute("SELECT user_id FROM users WHERE username = %s",
                                (str(self.current_user),))
            curr_id = self.cursor.fetchone()  # id of the current user

            if curr_id:
                # Generate a random 8-digit account number
                account_number = self.generate_rand_num()
                # Inserting their user id, the acc number, their balance, and type of account
                self.cursor.execute(
                    "INSERT INTO accounts (user_id, account_number, balance, account_type) VALUES (%s, %s, %s, %s)",
                    (curr_id[0], account_number, 0.0, self.type_entry.get()))
                self.connection.commit()

                messagebox.showinfo("Account Created")
            else:
                messagebox.showerror("Error", "some sort of error")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def logout(self):  # Method to log out the current user
        # todo: BUG FIX CAN ONLY LOGOUT ONCE THEN THE BUTTON STOPS WORKING
        if self.current_user:
            self.current_user = None
            if self.main_frame:
                self.main_frame.destroy()
                self.login_menu()
        else:
            messagebox.showinfo("Logout fail")


def main():
    root = ctk.CTk()
    atm = ATM(root)
    root.mainloop()


if __name__ == "__main__":
    main()
