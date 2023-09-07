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

from PIL import Image, ImageTk


class ATM:
    def __init__(self, root):
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

    def generate_rand_num(self): # Generate a random 8 digit number
        return str(random.randint(10000000, 99999999))

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

        # Display for current user
        self.current_user_label = tk.Label(self.main_frame, text=current_user)
        self.current_user_label.grid(row=0, column=1, padx=10, pady=10)

        # check balance button
        self.bal_btn = tk.Button(self.main_frame, text="Balance", command=self.check_bal)
        self.bal_btn.grid(row=0, column=0, padx=3, pady=3)

        # Deposit button
        self.depo_btn = tk.Button(self.main_frame, text="Deposit", command=self.deposit)
        self.depo_btn.grid(row=1, column=0, padx=3, pady=3)

        # Withdraw button
        self.with_btn = tk.Button(self.main_frame, text="Withdraw", command=self.withdraw)
        self.with_btn.grid(row=2, column=0, padx=3, pady=3)

        # Transfer Button
        self.transfer_btn = tk.Button(self.main_frame, text="Transfer", command=self.transfer)
        self.transfer_btn.grid(row=3, column=0, padx=3, pady=3)

        # Add a Card
        self.card_btn = tk.Button(self.main_frame, text="Add Card", command=self.add_card)
        self.card_btn.grid(row=4, column=0, padx=3, pady=3)

        # Check the location's button
        self.locations_btn = tk.Button(self.main_frame, text="Locations", command=self.locations)
        self.locations_btn.grid(row=5, column=0, padx=3, pady=3)

        # Open an account button
        self.account_btn = tk.Button(self.main_frame, text="Create Account", command=self.account_create_menu)
        self.account_btn.grid(row=6, column=0, padx=3, pady=3)

        # Exit/Logout button
        self.logout = tk.Button(self.main_frame, text="Logout", command=self.logout)
        self.logout.grid(row=7, column=0, padx=3, pady=3)

        # MAIN MENU METHODS

    # TODO: ALL METHODS ARE NOT FULLY FUNCTIONAL
    def check_bal(self):  # Method to check current users balance
        try:
            # Get users balance from database
            self.cursor.execute(
                "SELECT balance FROM accounts WHERE user_id = (SELECT user_id FROM users WHERE username = %s)",
                (str(self.current_user),))
            user_balance = self.cursor = self.cursor.fetchone()

            if user_balance:
                # Display the-users balance
                messagebox.showinfo("Balance", f"Your current balance: ${user_balance[0]:.2f}")
            else:
                messagebox.showerror("Error", "Unable to retrieve")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def deposit(self):  # Method to deposit money into users account
        # Deposit to display on main frame
        self.main_frame.withdraw()
        # Creating a new frame for deposit
        self.depo_frame = tk.Toplevel(self.root)
        self.depo_frame.geometry("500x500")
        self.depo_frame.protocol("WM_DELETE_WINDOW", self.on_close)
        self.amount_lbl = tk.Label(self.depo_frame, text="Amount")
        self.amount_lbl.grid(row=4, column=0, padx=3, pady=3)

        self.amount_entry = tk.Entry(self.depo_frame)
        self.amount_entry.grid(row=4, column=1, padx=3, pady=3)

    def withdraw(self):  # Method to withdraw money from users account
        pass

    def transfer(self):  # Method to transfer funds from one account to another
        pass

    def add_card(self):  # Method to add a card to the users account
        pass

    def locations(self):  # Method to display ATM locations

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
        option_menu.bind("<Configure>", lambda event: self.on_option(event, selected_option.get()))

        self.type_entry = selected_option

        self.submit_btn = tk.Button(self.account_frame, text="Submit", command=self.create_account)
        self.submit_btn.grid(row=2, column=2, padx=3, pady=3)
        print(f"account type is {selected_option}")

    def on_option(self, event, selected_option): # Drop down
        selected_option.set(event)

    def create_account(self):
        print("account being created")
        try:
        # Fetching the user id and balance of the current logged in user
            print(f"Username: {self.current_user}")
            self.cursor.execute("SELECT user_id FROM users WHERE username = %s", (str(self.current_user),))
            curr_id = self.cursor.fetchone() # id of the current user
            print(f"Current user (curr_id): {curr_id}")

            if curr_id:
                # Generate a random 8-digit account number
                print("before acc num")
                account_number = self.generate_rand_num()
                print("after acc num")
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
        print("Logout")
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
