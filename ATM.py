import tempfile
import tkinter as tk
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

        # Connecting to the DB
        self.connection = psycopg2.connect(
            dbname="ATM",
            user="postgres",
            password="Bearcat",
            host="localhost",
            port="5432"
        )
        self.cursor = self.connection.cursor()
        self.connection.commit()

    def create_tables(self):
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