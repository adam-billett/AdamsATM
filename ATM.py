import tempfile
import tkinter as tk
from logging import root
from tkinter import messagebox
from tkinter import ttk
from tabulate import tabulate

import psycopg2
import sys
import ctypes
import random
from datetime import date, timedelta

from PIL import Image, ImageTk


class ATM:
    def __init__(self, root):
        self.selected_option = None
        self.root = root
        self.root.title("Adams ATM")

        self.show_frame = True

        self.login_frame = None

        self.login_menu()

        # Connecting to the DB using a try block
        self.connection = psycopg2.connect(
            dbname="ATM",
            user="postgres",
            password="Bearcat",
            host="localhost",
            port="5432"
        )
        self.cursor = self.connection.cursor()

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

        # HIDING FRAME METHODS

    # To hide the creation frame
    def hide_create_ui(self):
        if self.create_frame:
            self.create_frame.destroy()
        self.login_menu()

    # To hide the Login frame
    def hide_login_ui(self):
        if self.login_frame:
            self.login_frame.destroy()
        self.root.deiconify()

    def go_back_depo(self): # Go back to main menu from depo
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
            self.eye_button.config(image=self.hide_eye_icon)

    def on_close(self):  # Closing the root from any window
        self.root.quit()

        # RANDOM NUMBER GENERATORS
    def generate_rand_num(self): # Generate a random 8 digit number for the account number
        return str(random.randint(10000000, 99999999))

    def generate_card_num(self): # Generate a random card number for the user
        return str(random.randint(1000000000000000, 9999999999999999))

    def generate_exp_date(self):
        today = date.today()

        max_years = 10

        end_date = today + timedelta(days=(365 * max_years))

        random_months = random.randint(0,11)
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
            self.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            db_password = self.cursor.fetchone()

            if db_password and db_password[0] == password:
                self.current_user = username
                messagebox.showinfo("Login successful")
                self.password.delete(0, tk.END)
                self.root.withdraw()
                # Main menu display
                self.main_menu(username)
            else:
                messagebox.showerror("Invalid username or password")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create(self):  # Method to create a new user TODO: create method
        username = self.create_user_entry.get()
        password = self.create_password.get()
        full_name = self.full_name_entry.get()

        self.cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
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
        self.root.withdraw()

        # Creating the login frame
        self.login_frame = tk.Toplevel(self.root)
        self.login_frame.geometry("300x150")
        self.login_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        # Username label for login frame
        self.username_lbl = tk.Label(self.login_frame, text="Username")
        self.username_lbl.grid(row=0, column=0, padx=5, pady=5)

        # Username entry
        self.username = tk.Entry(self.login_frame)
        self.username.grid(row=0, column=1, padx=5, pady=5)

        # password label for login frame
        self.password_lbl = tk.Label(self.login_frame, text="Password")
        self.password_lbl.grid(row=1, column=0, padx=5, pady=5)

        # password entry
        self.password = tk.Entry(self.login_frame, show="*")
        self.password.grid(row=1, column=1, padx=5, pady=5)

        # setting false so the password is show as ***
        self.show_password = False

        # inserting the eye icon to toggle the password on and off
        self.eye_icon = Image.open("eye.jpg")
        self.eye_icon = self.eye_icon.resize((20, 20))
        self.eye_icon = ImageTk.PhotoImage(self.eye_icon)
        self.hide_eye_icon = Image.open("eye.jpg")
        self.hide_eye_icon = self.hide_eye_icon.resize((20, 20))
        self.hide_eye_icon = ImageTk.PhotoImage(self.hide_eye_icon)

        # eye button for show password
        self.eye_button = tk.Button(self.login_frame, image=self.eye_icon, command=self.toggle_password)
        self.eye_button.grid(row=1, column=2, padx=5, pady=5)

        # login button at the bottom to confirm login
        self.login_btn = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_btn.grid(row=2, column=1, padx=5, pady=5)

        # link to go to create user window
        self.create_win = tk.Label(self.login_frame, text="Create user", fg="blue", cursor="hand2")
        self.create_win.grid(row=3, column=1, padx=5, pady=5)
        self.create_win.bind("<Button-1>", lambda event: self.create_menu() and self.hide_login_ui())

        # Bind submit button to enter key
        self.password.bind("<Return>", lambda event: self.login())

    def create_menu(self):
        self.login_frame.withdraw()
        self.root.withdraw()
        self.create_frame = tk.Toplevel(self.root)
        self.create_frame.geometry("300x150")
        self.create_frame.protocol("WM_DELETE_WINDOW", self.on_close)


        # Full name label
        self.full_name = tk.Label(self.create_frame, text="Full name")
        self.full_name.grid(row=0, column=0, padx=3, pady=3)

        # Full name entry
        self.full_name_entry = tk.Entry(self.create_frame)
        self.full_name_entry.grid(row=0, column=1, padx=3, pady=3)

        # username create label
        self.create_user = tk.Label(self.create_frame, text="Username")
        self.create_user.grid(row=1, column=0, padx=3, pady=3)

        # create username entry
        self.create_user_entry = tk.Entry(self.create_frame)
        self.create_user_entry.grid(row=1, column=1, padx=3, pady=3)

        # create password label
        self.create_password_lbl = tk.Label(self.create_frame, text="Password")
        self.create_password_lbl.grid(row=2, column=0, padx=3, pady=3)

        # create password entry
        self.create_password = tk.Entry(self.create_frame, show="*")
        self.create_password.grid(row=2, column=1, padx=3, pady=3)

        # Create button to submit user creating
        self.create_sub = tk.Button(self.create_frame, text="create", command=self.create)
        self.create_sub.grid(row=3, column=1, padx=3, pady=3)

        # link to go back to the login frame
        self.back_login = tk.Label(self.create_frame, text="Back to Login", fg="blue", cursor="hand2")
        self.back_login.grid(row=4, column=1, padx=3, pady=3)
        self.back_login.bind("<Button-1>", lambda event: self.hide_create_ui() and self.login_menu())

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

        self.login_frame.withdraw()

        self.main_frame = tk.Toplevel(self.root)
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
        self.selected_option = tk.StringVar(self.main_frame)
        self.selected_option.set("Select an option")

        option_menu = tk.OptionMenu(self.main_frame, self.selected_option, *account_types)
        option_menu.grid(row=0, column=0, padx=3, pady=3)

        # TODO: issue with menu labels popping up as its parameters
        option_menu.bind("<ButtonRelease-1>", lambda event, arg=self.selected_option: self.on_option(event, arg))

        # Display for current user
        self.current_user_label = tk.Label(self.main_frame, text=current_user)
        self.current_user_label.grid(row=0, column=5, padx=10, pady=10)

        # check balance button
        self.bal_btn = tk.Button(self.main_frame, text="Balance", command=self.check_bal)
        self.bal_btn.grid(row=1, column=0, padx=3, pady=3)

        # Deposit button
        self.depo_btn = tk.Button(self.main_frame, text="Deposit", command=self.deposit_menu)
        self.depo_btn.grid(row=2, column=0, padx=3, pady=3)

        # Withdraw button
        self.with_btn = tk.Button(self.main_frame, text="Withdraw", command=self.withdraw_money_menu)
        self.with_btn.grid(row=3, column=0, padx=3, pady=3)

        # Transfer Button
        self.transfer_btn = tk.Button(self.main_frame, text="Transfer", command=self.transfer_menu)
        self.transfer_btn.grid(row=4, column=0, padx=3, pady=3)

        # Add a Card
        self.card_btn = tk.Button(self.main_frame, text="Add Card", command=self.add_card_menu)
        self.card_btn.grid(row=5, column=0, padx=3, pady=3)

        # Check the location's button
        self.locations_btn = tk.Button(self.main_frame, text="Locations", command=self.locations_menu)
        self.locations_btn.grid(row=6, column=0, padx=3, pady=3)

        # Open an account button
        self.account_btn = tk.Button(self.main_frame, text="Create Account", command=self.account_create_menu)
        self.account_btn.grid(row=7, column=0, padx=3, pady=3)

        # Exit/Logout button
        self.logout = tk.Button(self.main_frame, text="Logout", command=self.logout)
        self.logout.grid(row=8, column=0, padx=3, pady=3)

        # MAIN MENU METHODS

    # TODO: ALL METHODS ARE NOT FULLY FUNCTIONAL
    def check_bal(self):  # Method to check current users balance
        try:
            # Get users balance from database
            self.cursor.execute(
                "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s", # TODO: can only use once, then issues occur with drop down
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
        self.depo_frame = tk.Toplevel(self.root)
        self.depo_frame.geometry("500x500")
        self.depo_frame.protocol("WM_DELETE_WINDOW", self.on_close)
        self.amount_lbl = tk.Label(self.depo_frame, text="Amount")
        self.amount_lbl.grid(row=4, column=0, padx=3, pady=3)
        # Amount entry box
        self.amount_entry = tk.Entry(self.depo_frame)
        self.amount_entry.grid(row=4, column=1, padx=3, pady=3)
        # Get the current users id
        self.get_curr_user()

        self.submit_depo = tk.Button(self.depo_frame, text="Deposit", command=self.deposit)
        self.submit_depo.grid(row=5, column=2, padx=3, pady=3)

        self.back_arrow = tk.Button(self.depo_frame, text="Back", command=self.go_back_depo)
        self.back_arrow.grid(row=7, column=3, padx=3, pady=3)

    def deposit(self): # Method to insert the money into the current users account
        # fetch the current user
        self.get_curr_user()
        selected_type = self.selected_option.get()
        # Getting the account id from the current user
        self.cursor.execute("SELECT account_id FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s", (str(self.current_user), selected_type))
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
        self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (updated_balance, account_id))

        # Message to how it is successful
        messagebox.showinfo("Success",f"${self.amount_entry.get()} deposited into account")

        self.connection.commit()

    def withdraw_money_menu(self):  # Method to withdraw money from users account
        # Withdrawing the main window
        self.main_frame.withdraw()
        # Creating a new frame for withdrawing
        self.withdraw_frame = tk.Toplevel(self.root)
        self.withdraw_frame.geometry("300x300")
        self.withdraw_frame.protocol("WM_DELETE_WINDOW", self.on_close)
        # Get the current users id
        self.get_curr_user()

        # Amount to withdraw label
        self.withdraw_amount_lbl = tk.Label(self.withdraw_frame, text="Amount")
        self.withdraw_amount_lbl.grid(row=1, column=0, padx=3, pady=3)

        # Amount to withdraw entry
        self.withdraw_amount_entry = tk.Entry(self.withdraw_frame)
        self.withdraw_amount_entry.grid(row=1, column=1, padx=3, pady=3)

        # Withdraw button to submit the withdraw
        self.withdraw_btn = tk.Button(self.withdraw_frame, text="Withdraw", command=self.withdraw_money)
        self.withdraw_btn.grid(row=2, column=2, padx=3, pady=3)

        self.back_arrow_with = tk.Button(self.withdraw_frame, text="Back", command=self.go_back_withdraw)
        self.back_arrow_with.grid(row=3, column=3, padx=3, pady=3)

    def withdraw_money(self): # Method that actually subtracts the amount from the database
        # fetch the current user
        self.get_curr_user()
        selected_type = self.selected_option.get()
        # Getting the account id from the current user
        self.cursor.execute(
            "SELECT account_id FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s",
            (str(self.current_user), selected_type))
        account_id = self.cursor.fetchone()
        # Grabbing the current balance of the current user
        self.cursor.execute("SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND account_type = %s", (str(self.current_user), selected_type))
        balance_record = self.cursor.fetchone()

        # taking the tuple var and turning it into an int
        balance = balance_record[0]

        # putting the amount to withdraw into a variable
        amt_to_withdraw = self.withdraw_amount_entry.get()

        # Updating by subtracting the amount from the current balance
        updated_balance = balance - int(amt_to_withdraw)

        # SQL to withdraw money from the current account
        self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                            (updated_balance, account_id))

        messagebox.showinfo("Success", f"${self.withdraw_amount_entry.get()} withdrawn from account")
        self.connection.commit()

    def transfer_menu(self):  # Method to transfer funds from one account to another keep track or deposits and withdraws

        # Getting the ID of the current user
        self.get_curr_user()
        # Withdrawing the main frame
        self.main_frame.withdraw()

        # Creating a new frame for the transfer menu
        self.transfer_frame = tk.Toplevel(self.root)
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
        # Displaying the options in the drop-down menu
        option_menu = tk.OptionMenu(self.transfer_frame, self.selected_user, *user_list)
        option_menu.grid(row=0, column=0, padx=3, pady=3)

        # Binding when the user clicks to submit what they clicked
        option_menu.bind("<ButtonRelease-1>", lambda event, arg=self.selected_user: self.on_option(event, arg))

        self.amount_transfer_lbl = tk.Label(self.transfer_frame, text="Amount")
        self.amount_transfer_lbl.grid(row=1, column=1, padx=3, pady=3)

        self.amount_transfer_entry = tk.Entry(self.transfer_frame)
        self.amount_transfer_entry.grid(row=1, column=2, padx=3, pady=3)

        #TODO: ACCOUNTS DROP DOWN POPULATES BEFORE THE USER SELECTS A USER

        if self.on_option:
            selected_user = self.selected_user.get()
            print(f"{selected_user}")
            # DROP DOWN TO SELECT ACCOUNT OF THAT USER TO TRANSFER TO. CAN BE SAME USER DIFFERENT ACCOUNT Ex. user 6 from their checkings to their savings account
            self.cursor.execute("SELECT account_type FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s)", (str(selected_user),))
            accounts = self.cursor.fetchall()
            account_list = [account[0] for account in accounts]
            print(f"{account_list}")

        else:
            curr_user = self.get_curr_user
            self.cursor.execute(
                "SELECT account_type FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %)",
                (str(curr_user),))
            accounts = self.cursor.fetchall()
            account_list = [account[0] for account in accounts]
            print(f"{account_list}")

        self.selected_account = tk.StringVar(self.transfer_frame)
        self.selected_account.set("Select Account")

        options_menu = tk.OptionMenu(self.transfer_frame, self.selected_account, f"{self.selected_account}", *account_list)
        options_menu.grid(row=0, column=1, padx=3, pady=3)

        options_menu.bind("<ButtonRelease-1>", lambda event, arg=self.selected_account: self.on_option(event, arg))





    def transfer(self):
        pass
    def add_card_menu(self):  # Method to add a card to the users account
        # Withdrawing the main frame
        self.main_frame.withdraw()
        # Creating a new frame
        self.card_frame = tk.Toplevel(self.root)
        self.card_frame.geometry("300x300")
        self.card_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        # Option to get a card by the bank, or to manually enter a card they already have.
        # Manually add an existing card
        #  Card number Label
        self.card_num_lbl = tk.Label(self.card_frame, text="Card Number")
        self.card_num_lbl.grid(row=0, column=0, padx=3, pady=3)
        # Card number entry
        self.card_num_entry = tk.Entry(self.card_frame)
        self.card_num_entry.grid(row=0, column=1, padx=3, pady=3)
        # Expiration date label
        self.exp_date_lbl = tk.Label(self.card_frame, text="Expiration Date")
        self.exp_date_lbl.grid(row=1, column=0, padx=3, pady=3)
        # Expiration date entry
        self.exp_date_entry = tk.Entry(self.card_frame)
        self.exp_date_entry.grid(row=1, column=1, padx=3, pady=3)
        # ccv label
        self.ccv_lbl = tk.Label(self.card_frame, text="CCV")
        self.ccv_lbl.grid(row=2, column=0, padx=3, pady=3)
        # ccv entry
        self.ccv_entry = tk.Entry(self.card_frame)
        self.ccv_entry.grid(row=2, column=1, padx=3, pady=3)
        # Submit button to enter the info
        self.submit_card_btn = tk.Button(self.card_frame, text="Submit", command=self.add_card)
        self.submit_card_btn.grid(row=3, column=1, padx=3, pady=3)
        # Generate a bank card
        self.generate_card_btn = tk.Button(self.card_frame, text="Generate", command=self.generate_card)
        self.generate_card_btn.grid(row=4, column=1, padx=3, pady=3)

        self.back_arrow_card = tk.Button(self.card_frame, text="Back", command=self.go_back_card)
        self.back_arrow_card.grid(row=5, column=2, padx=3, pady=3)

    def add_card(self):
        try:
            # getting the id of the current user, so we can use it to add the card to their account
            self.get_curr_user()
            curr_id = self.cursor.fetchone() # id of the current user

            if curr_id:
                self.cursor.execute("INSERT INTO card (user_id, card_number, expiration_date, cvv) VALUES (%s, %s, %s, %s)", (curr_id[0], self.card_num_entry.get(), self.exp_date_entry.get(), self.ccv_entry.get()))
                self.connection.commit()

                messagebox.showinfo("Card Added")
            else:
                messagebox.showerror("Error", "idk")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_card(self):
        try:
            # Getting the current users id
            self.get_curr_user()
            curr_id = self.cursor.fetchone()

            if curr_id:
                self.cursor.execute("INSERT INTO CARD (user_id, card_number, expiration_date, cvv) VALUES (%s, %s, %s, %s)", (curr_id[0], self.generate_card_num(), self.generate_exp_date(), self.generate_ccv()))
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
        self.account_frame = tk.Toplevel(self.root)
        self.account_frame.geometry("300x300")
        self.account_frame.protocol("WM_DELETE_WINDOW", self.on_close)

        selected_option = tk.StringVar(self.account_frame)
        selected_option.set("Select an option")

        options = ["Checking", "Savings"]

        option_menu = tk.OptionMenu(self.account_frame, selected_option, *options)
        option_menu.grid(row=0, column=0, padx=3, pady=3)

        label = tk.Label(self.account_frame, textvariable=selected_option)
        label.grid(row=1, column=0, padx=3, pady=3)

        # TODO: issue with menu labels popping up as its parameters
        option_menu.bind("<ButtonRelease-1>", lambda event: self.on_option(event, selected_option))

        self.type_entry = selected_option

        self.submit_btn = tk.Button(self.account_frame, text="Submit", command=self.create_account)
        self.submit_btn.grid(row=2, column=2, padx=3, pady=3)

        self.back_account = tk.Button(self.account_frame, text="Back", command=self.go_back_account)
        self.back_account.grid(row=3, column=3, padx=3, pady=3)




    def on_option(self, event, selected_option): # Drop down
        selected_option.set(selected_option.get())


    def create_account(self):
        try:
        # Fetching the user id and balance of the current logged in user
            self.cursor.execute("SELECT user_id FROM users WHERE username = %s", (str(self.current_user),))
            curr_id = self.cursor.fetchone() # id of the current user

            if curr_id:
                # Generate a random 8-digit account number
                account_number = self.generate_rand_num()
                # Inserting their user id, the acc number, their balance, and type of account
                self.cursor.execute("INSERT INTO accounts (user_id, account_number, balance, account_type) VALUES (%s, %s, %s, %s)", (curr_id[0], account_number, 0.0, self.type_entry.get()))
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
                self.main_frame.withdraw()
                self.login_frame.deiconify()
        else:
            messagebox.showinfo("Logout fail")


def main():
    root = tk.Tk()
    atm = ATM(root)
    root.mainloop()


if __name__ == "__main__":
    main()
