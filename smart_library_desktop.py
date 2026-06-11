import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import os, sys

# -------- ICON PATH (for exe compatibility) ----------
def resource_path(rel_path):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, rel_path)

# --------------- BOOK CLASS -------------------------
class Book:
    def __init__(self, code, title, author, copies):
        self.code = code
        self.title = title
        self.author = author
        self.copies = copies

# --------------- LIBRARY CLASS ---------------------
class Library:
    def __init__(self):
        self.conn = sqlite3.connect("library.db")
        self.create_table()
        self.load_books()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                title TEXT,
                author TEXT,
                copies INTEGER
            )
        """)
        self.conn.commit()

    def load_books(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT code, title, author, copies FROM books")
        self.books = [
            Book(code, title, author, copies)
            for code, title, author, copies in cursor.fetchall()
        ]

    def add_book(self, book):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO books(code,title,author,copies) VALUES(?,?,?,?)",
                (book.code, book.title, book.author, book.copies)
            )
            self.conn.commit()
            self.load_books()
            return True
        except sqlite3.IntegrityError:
            return False

    def borrow_book(self, code):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE books SET copies = copies - 1 WHERE code=? AND copies>0",
            (code,)
        )
        self.conn.commit()
        self.load_books()
        return cursor.rowcount > 0

    def return_book(self, code):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE books SET copies = copies + 1 WHERE code=?",
            (code,)
        )
        self.conn.commit()
        self.load_books()
        return cursor.rowcount > 0

    def search(self, keyword):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT code, title, author, copies FROM books
            WHERE title LIKE ? OR author LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))
        return [
            Book(code, title, author, copies)
            for code, title, author, copies in cursor.fetchall()
        ]

    def statistics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(copies) FROM books")
        count, total = cursor.fetchone()
        return count or 0, total or 0

# ------------------ GUI APP -------------------------
class SmartLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Library Manager")

        try:
            self.root.iconbitmap(resource_path("library.ico"))
        except:
            pass

        self.library = Library()

        self.build_ui()
        self.refresh_list()

    def build_ui(self):

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        # ----------- Add book tab ------------
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Manage Books")

        ttk.Label(tab1, text="Code").grid(row=0, column=0)
        ttk.Label(tab1, text="Title").grid(row=1, column=0)
        ttk.Label(tab1, text="Author").grid(row=2, column=0)
        ttk.Label(tab1, text="Copies").grid(row=3, column=0)

        self.code_entry = ttk.Entry(tab1)
        self.title_entry = ttk.Entry(tab1)
        self.author_entry = ttk.Entry(tab1)
        self.copies_entry = ttk.Entry(tab1)

        self.code_entry.grid(row=0, column=1)
        self.title_entry.grid(row=1, column=1)
        self.author_entry.grid(row=2, column=1)
        self.copies_entry.grid(row=3, column=1)

        ttk.Button(tab1, text="Add Book", command=self.add_book).grid(row=4, column=0, columnspan=2)

        self.tree = ttk.Treeview(tab1, columns=("Code", "Title", "Author", "Copies"), show="headings")
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)

        for col in ("Code", "Title", "Author", "Copies"):
            self.tree.heading(col, text=col)

        # ------------ Borrow/Return tab ----------
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Borrow / Return")

        ttk.Label(tab2, text="Book Code").pack(pady=5)
        self.borrow_entry = ttk.Entry(tab2)
        self.borrow_entry.pack()

        ttk.Button(tab2, text="Borrow", command=self.borrow_book).pack(pady=5)
        ttk.Button(tab2, text="Return", command=self.return_book).pack(pady=5)

        # -------------- Search tab ----------------
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Search")

        self.search_entry = ttk.Entry(tab3)
        self.search_entry.pack(pady=5)

        ttk.Button(tab3, text="Search", command=self.search_books).pack()

        self.search_results = tk.Text(tab3, height=12)
        self.search_results.pack(fill="both", expand=True)

        # -------------- Statistics tab ------------
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Statistics")

        ttk.Button(tab4, text="Show Statistics", command=self.show_statistics).pack(pady=20)

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for b in self.library.books:
            self.tree.insert("", "end", values=(b.code, b.title, b.author, b.copies))

    def add_book(self):
        try:
            b = Book(
                self.code_entry.get(),
                self.title_entry.get(),
                self.author_entry.get(),
                int(self.copies_entry.get())
            )

            if self.library.add_book(b):
                self.refresh_list()
                messagebox.showinfo("Success", "Book added!")
            else:
                messagebox.showerror("Error", "Book code already exists")

        except:
            messagebox.showerror("Error", "Invalid inputs")

    def borrow_book(self):
        if self.library.borrow_book(self.borrow_entry.get()):
            self.refresh_list()
            messagebox.showinfo("Borrow", "Book borrowed")
        else:
            messagebox.showerror("Error", "Borrow failed")

    def return_book(self):
        if self.library.return_book(self.borrow_entry.get()):
            self.refresh_list()
            messagebox.showinfo("Return", "Book returned")
        else:
            messagebox.showerror("Error", "Invalid book code")

    def search_books(self):
        results = self.library.search(self.search_entry.get())
        self.search_results.delete("1.0", tk.END)

        for b in results:
            self.search_results.insert(
                tk.END,
                f"{b.code} | {b.title} | {b.author} | Copies: {b.copies}\n"
            )

    def show_statistics(self):
        count, total = self.library.statistics()
        messagebox.showinfo(
            "Statistics",
            f"Total books: {count}\nTotal copies: {total}"
        )

# ---------------- RUN --------------------
root = tk.Tk()
app = SmartLibraryApp(root)
root.mainloop()
