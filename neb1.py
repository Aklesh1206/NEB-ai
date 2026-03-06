import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt

DB_PATH = "neb_assistant.db"

# ---------------------- DATABASE ----------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        password_hash BLOB NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def create_user(login_id, display_name, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (login_id, display_name, password_hash) VALUES (?, ?, ?)",
            (login_id, display_name, password_hash),
        )
        conn.commit()
        messagebox.showinfo("Success", "User created successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "User already exists.")
    finally:
        conn.close()

def authenticate(login_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, display_name, password_hash FROM users WHERE login_id = ?", (login_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, display_name, password_hash = user
        if bcrypt.checkpw(password.encode(), password_hash):
            return {"id": user_id, "display_name": display_name}
    return None

# ---------------------- GUI APP ----------------------

class NebAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neb AI")
        self.root.geometry("500x600")
        self.root.configure(bg="#121212")

        self.user = None
        self.active = False
        self.wake_word = "hey neb"

        self.show_login()

    # ---------------- LOGIN SCREEN ----------------

    def show_login(self):
        self.clear_screen()

        tk.Label(self.root, text="Neb AI", font=("Arial", 24, "bold"),
                 bg="#121212", fg="#00ffcc").pack(pady=20)

        tk.Label(self.root, text="Login ID", bg="#121212", fg="white").pack()
        self.login_entry = tk.Entry(self.root, bg="#1e1e1e", fg="white", insertbackground="white")
        self.login_entry.pack(pady=5)

        tk.Label(self.root, text="Password", bg="#121212", fg="white").pack()
        self.password_entry = tk.Entry(self.root, show="*", bg="#1e1e1e", fg="white", insertbackground="white")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", bg="#00ffcc", fg="black",
                  command=self.login).pack(pady=10)

        tk.Button(self.root, text="Signup", bg="#333333", fg="white",
                  command=self.show_signup).pack()

    def show_signup(self):
        self.clear_screen()

        tk.Label(self.root, text="Create Account", font=("Arial", 20),
                 bg="#121212", fg="#00ffcc").pack(pady=20)

        self.new_login = tk.Entry(self.root, bg="#1e1e1e", fg="white", insertbackground="white")
        self.new_login.pack(pady=5)
        self.new_login.insert(0, "Login ID")

        self.new_name = tk.Entry(self.root, bg="#1e1e1e", fg="white", insertbackground="white")
        self.new_name.pack(pady=5)
        self.new_name.insert(0, "Display Name")

        self.new_password = tk.Entry(self.root, show="*", bg="#1e1e1e", fg="white", insertbackground="white")
        self.new_password.pack(pady=5)
        self.new_password.insert(0, "Password")

        tk.Button(self.root, text="Create", bg="#00ffcc", fg="black",
                  command=self.signup).pack(pady=10)

        tk.Button(self.root, text="Back", bg="#333333", fg="white",
                  command=self.show_login).pack()

    def login(self):
        login_id = self.login_entry.get()
        password = self.password_entry.get()

        user = authenticate(login_id, password)
        if user:
            self.user = user
            self.show_assistant()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def signup(self):
        create_user(self.new_login.get(), self.new_name.get(), self.new_password.get())
        self.show_login()

    # ---------------- ASSISTANT SCREEN ----------------

    def show_assistant(self):
        self.clear_screen()

        tk.Label(self.root, text=f"Neb AI",
                 font=("Arial", 22, "bold"),
                 bg="#121212", fg="#00ffcc").pack(pady=10)

        tk.Label(self.root,
                 text=f"Welcome {self.user['display_name']}",
                 bg="#121212", fg="white").pack()

        self.chat_box = tk.Text(self.root, bg="#1e1e1e", fg="white", height=20)
        self.chat_box.pack(padx=10, pady=10, fill="both", expand=True)

        self.input_entry = tk.Entry(self.root, bg="#1e1e1e", fg="white", insertbackground="white")
        self.input_entry.pack(fill="x", padx=10, pady=5)
        self.input_entry.bind("<Return>", self.process_input)

        self.chat_box.insert("end", "Neb AI ready. Say 'Hey Neb' to activate.\n")

    def process_input(self, event):
        user_input = self.input_entry.get()
        self.input_entry.delete(0, "end")

        self.chat_box.insert("end", f"You: {user_input}\n")

        text = user_input.lower()

        if not self.active:
            if self.wake_word in text:
                self.active = True
                self.chat_box.insert("end", f"Neb AI: Yes {self.user['display_name']}? I'm listening...\n")
            return

        if "your name" in text:
            response = "I am Neb AI, your assistant."
        elif "my name" in text:
            response = f"Your name is {self.user['display_name']}."
        elif "sleep" in text:
            response = "Going back to sleep."
            self.active = False
        else:
            response = "Processing... (LLM can be connected here)"

        self.chat_box.insert("end", f"Neb AI: {response}\n")
        self.chat_box.see("end")

    # ---------------- UTIL ----------------

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# ---------------------- RUN ----------------------

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = NebAIApp(root)
    root.mainloop()