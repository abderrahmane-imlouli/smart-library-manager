import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3,os

# ===== DATABASE =====

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# ===== OOP MODELS =====

class Book:
    def __init__(self, code, title, author, copies, borrowed):
        self.code = code
        self.title = title
        self.author = author
        self.copies = copies
        self.borrowed = borrowed


class Library:
    def __init__(self):
        self.books = {}
        self.load_books()

    # Load from SQLite
    def load_books(self):
        cursor.execute("SELECT * FROM books")
        data = cursor.fetchall()

        for row in data:
            book = Book(row[0], row[1], row[2], row[3], row[4])
            self.books[row[0]] = book

    # Add book
    def add_book(self, code, title, author, copies):

        cursor.execute("""
        INSERT OR IGNORE INTO books
        VALUES (?,?,?,?,0)
        """, (code, title, author, copies))

        conn.commit()
        self.load_books()

    # Borrow
    def borrow_book(self, code):

        if code not in self.books:
            return " Book not found"

        book = self.books[code]

        if book.copies <= 0:
            return " No copies available"

        book.copies -= 1
        book.borrowed += 1

        cursor.execute("""
        UPDATE books
        SET copies=?, borrowed=?
        WHERE code=?
        """,(book.copies, book.borrowed, code))

        conn.commit()
        return " Borrowed successfully"

    # Return
    def return_book(self, code):

        if code not in self.books:
            return " Book not found"

        book = self.books[code]

        book.copies += 1
        book.borrowed -= 1

        cursor.execute("""
        UPDATE books
        SET copies=?, borrowed=?
        WHERE code=?
        """,(book.copies,book.borrowed,code))

        conn.commit()
        return " Returned successfully"

    # Search
    def search(self, keyword):

        cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))

        results = []

        for row in cursor.fetchall():
            results.append(Book(*row))

        return results

    # Statistics
    def statistics(self):

        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(copies) FROM books")
        copies = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(borrowed) FROM books")
        borrowed = cursor.fetchone()[0] or 0

        return total_books, copies, borrowed


# ===== GUI =====

library = Library()

root = tk.Tk()
# root.iconbitmap("library.ico")
icon_path = os.path.join(os.path.dirname(__file__), "library.ico")
root.iconbitmap(icon_path)
root.title(" Smart Library Manager (SQLite)")
root.geometry("850x600")

# ------ Frames ------

add_frame = tk.LabelFrame(root, text="Add Book")
add_frame.pack(fill="x", padx=10, pady=5)

borrow_frame = tk.LabelFrame(root, text="Borrow / Return")
borrow_frame.pack(fill="x", padx=10, pady=5)

search_frame = tk.LabelFrame(root, text="Search / Statistics")
search_frame.pack(fill="x", padx=10, pady=5)

table_frame = tk.LabelFrame(root, text="Library Books")
table_frame.pack(fill="both", padx=10, pady=5, expand=True)

# ------ Add Book UI ------

tk.Label(add_frame,text="Code").grid(row=0,column=0)
tk.Label(add_frame,text="Title").grid(row=0,column=1)
tk.Label(add_frame,text="Author").grid(row=0,column=2)
tk.Label(add_frame,text="Copies").grid(row=0,column=3)

code_e = tk.Entry(add_frame)
title_e = tk.Entry(add_frame)
author_e = tk.Entry(add_frame)
copies_e = tk.Entry(add_frame)

code_e.grid(row=1,column=0)
title_e.grid(row=1,column=1)
author_e.grid(row=1,column=2)
copies_e.grid(row=1,column=3)

def add_gui():
    try:
        library.add_book(
            code_e.get(),
            title_e.get(),
            author_e.get(),
            int(copies_e.get())
        )
        refresh_table()
        messagebox.showinfo("Done"," Book added successfully")

    except:
        messagebox.showerror("Error"," Invalid input")

tk.Button(add_frame,text="ADD",command=add_gui).grid(row=1,column=4,padx=10)

# ------ Borrow UI ------

tk.Label(borrow_frame,text="Book Code").grid(row=0,column=0)
borrow_e = tk.Entry(borrow_frame)
borrow_e.grid(row=0,column=1)

tk.Button(borrow_frame,text="Borrow",
          command=lambda:action_gui(library.borrow_book)).grid(row=0,column=2)

tk.Button(borrow_frame,text="Return",
          command=lambda:action_gui(library.return_book)).grid(row=0,column=3)

def action_gui(func):
    msg = func(borrow_e.get())
    refresh_table()
    messagebox.showinfo("Info",msg)

# ------ Search ------

search_e = tk.Entry(search_frame)
search_e.pack(side="left",padx=5)

def search_gui():
    results = library.search(search_e.get())
    refresh_table(results)

tk.Button(search_frame,text="Search",command=search_gui).pack(side="left")

tk.Button(search_frame,text="Show All",command=lambda: refresh_table()).pack(side="left")

# ----- Statistics -----

def show_stats():
    t,c,b = library.statistics()

    messagebox.showinfo("Statistics",
        f" Total Books: {t}\n"
        f" Available Copies: {c}\n"
        f" Borrowed: {b}"
    )

tk.Button(search_frame,text="Statistics",command=show_stats).pack(side="right")

# ------ Table ------

cols=("Code","Title","Author","Copies","Borrowed")

tree = ttk.Treeview(table_frame,columns=cols, show="headings")

for col in cols:
    tree.heading(col, text=col)
    tree.column(col,width=150)

tree.pack(fill="both",expand=True)

# ------ Refresh ------

def refresh_table(books=None):

    tree.delete(*tree.get_children())

    if books is None:
        books = library.books.values()

    for b in books:
        tree.insert("","end", values=(
            b.code,
            b.title,
            b.author,
            b.copies,
            b.borrowed
        ))

refresh_table()

root.mainloop()