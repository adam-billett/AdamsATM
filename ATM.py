import tempfile
import tkinter as tk
from logging import root
from tkinter import messagebox
from tkinter import ttk
from tabulate import tabulate

import psycopg2
import sys
import ctypes

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
                        account_number VARCHAR,
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

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Missing Info, try again")
        else:
            self.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            db_password = self.cursor.fetchone()

            if db_password and db_password[0] == password:
                messagebox.showinfo("Login successful")
                self.root.withdraw()
                # Main menu display
            else:
                messagebox.showerror("Invalid username or password")

    def create(self):
        username = self.create_user_entry.get()
        password = self.create_password.get()

        self.cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing_user = self.cursor.fetchone()

        if existing_user:
            messagebox.showerror("Username already exists")
            return

        self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        self.connection.commit()
        messagebox.showinfo("Account created")

        self.create_frame.withdraw()
        self.root.deiconify()

        # MENU'S

    def login_menu(self):  # Login menu when first starting
        self.root.withdraw()

        # Creating the login frame
        self.login_frame = tk.Toplevel(self.root)
        self.login_frame.geometry("275x125")
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
        self.create_frame.geometry("275x125")
        self.create_frame.protocol("WM_DELETE_WINDOW", self.on_close)
        # username create label
        self.create_user = tk.Label(self.create_frame, text="Username")
        self.create_user.grid(row=0, column=0, padx=3, pady=3)
        # create username entry
        self.create_user_entry = tk.Entry(self.create_frame)
        self.create_user_entry.grid(row=0, column=1, padx=3, pady=3)
        # create password label
        self.create_password_lbl = tk.Label(self.create_frame, text="Password")
        self.create_password_lbl.grid(row=1, column=0, padx=3, pady=3)
        # create password entry
        self.create_password = tk.Entry(self.create_frame, show="*")
        self.create_password.grid(row=1, column=1, padx=3, pady=3)
        # Create button to submit user creating
        self.create_sub = tk.Button(self.create_frame, text="create", command=self.create)
        self.create_sub.grid(row=2, column=1, padx=3, pady=3)
        # link to go back to login
        self.back_login = tk.Label(self.create_frame, text="Back to Login", fg="blue", cursor="hand2")
        self.back_login.grid(row=3, column=1, padx=3, pady=3)
        self.back_login.bind("<Button-1>", lambda event: self.hide_create_ui() and self.login_menu())
        # bind enter key to submit button
        self.create_password.bind("<Return>", lambda event: self.create())

    def main_menu(self):  # screen to show when successfully logged in
        pass


def main():
    root = tk.Tk()
    atm = ATM(root)
    root.mainloop()


if __name__ == "__main__":
    main()
