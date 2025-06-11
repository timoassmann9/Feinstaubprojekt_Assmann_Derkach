import tkinter as tk

root = tk.Tk()
root.title("Mein Programm")
root.geometry("400x300")

label = tk.Label(root, text="Hallo Welt!")
label.pack(pady=5)

def button_aktion():
    print("Button wurde geklickt!")
    label.configure(text='hehehe')

def button_aktion2():
    label.configure(text='Hallo Welt!')

button = tk.Button(root, text="Klick mich!", command=button_aktion)
button.pack(pady=5)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)
entry.insert(0, "Gib hier etwas ein...")

def button_klick():
    text = entry.get()
    label.config(text=f"Du hast eingegeben: {text}")
    print(text)

button = tk.Button(root, text="Bestätigen", command=button_klick)
button.pack(pady=10)

root.mainloop()
