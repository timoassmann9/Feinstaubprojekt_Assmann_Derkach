import tkinter as tk
from tkinter import ttk

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do Liste")
        self.root.geometry("400x300")

        # Haupt-Frame
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky="NSEW")

        # Eingabe
        self.task_entry = ttk.Entry(frame, width=30)
        self.task_entry.grid(row=0, column=0, padx=5, pady=5)
        self.task_entry.bind("<Return>", self.add_task)

        add_button = ttk.Button(frame, text="Hinzufügen", command=self.add_task)
        add_button.grid(row=0, column=1, padx=5, pady=5)

        # Aufgabenliste (Treeview)
        self.tree = ttk.Treeview(frame, columns=("Aufgabe",), show="headings", height=10)
        self.tree.heading("Aufgabe", text="Aufgabe")
        self.tree.grid(row=1, column=0, columnspan=2, pady=10, sticky="NSEW")

        # Löschen-Button
        delete_button = ttk.Button(frame, text="Ausgewählte löschen", command=self.delete_task)
        delete_button.grid(row=2, column=0, columnspan=2, pady=5)

    def add_task(self, event=None):
        aufgabe = self.task_entry.get().strip()
        if aufgabe:
            self.tree.insert("", "end", values=(aufgabe,))
            self.task_entry.delete(0, tk.END)

    def delete_task(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            self.tree.delete(item)

# Hauptprogramm starten
if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
