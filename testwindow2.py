import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont

def alle_ttk_widgets():
    """Zeigt alle verfügbaren TTK Widgets mit Beispielen"""
    root = tk.Tk()
    root.title("Alle TTK Widgets")
    root.geometry("700x600")
    
    # Notebook (Tabs) für Organisation
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tab 1: Eingabe Widgets
    input_frame = ttk.Frame(notebook)
    notebook.add(input_frame, text="Eingabe Widgets")
    
    # Entry
    ttk.Label(input_frame, text="Entry (Eingabefeld):").pack(anchor="w", padx=10, pady=5)
    entry = ttk.Entry(input_frame, width=30)
    entry.pack(padx=10, pady=5)
    entry.insert(0, "Beispieltext")
    
    # Combobox
    ttk.Label(input_frame, text="Combobox (Dropdown):").pack(anchor="w", padx=10, pady=5)
    combo = ttk.Combobox(input_frame, values=["Python", "Java", "C++", "JavaScript"])
    combo.pack(padx=10, pady=5)
    combo.set("Python")
    
    # Spinbox
    ttk.Label(input_frame, text="Spinbox (Zahlen):").pack(anchor="w", padx=10, pady=5)
    spinbox = ttk.Spinbox(input_frame, from_=0, to=100, width=10)
    spinbox.pack(padx=10, pady=5)
    
    # Scale
    ttk.Label(input_frame, text="Scale (Schieberegler):").pack(anchor="w", padx=10, pady=5)
    scale_var = tk.DoubleVar()
    scale = ttk.Scale(input_frame, from_=0, to=100, variable=scale_var, 
                     orient="horizontal", length=200)
    scale.pack(padx=10, pady=5)
    
    scale_label = ttk.Label(input_frame, text="Wert: 0")
    scale_label.pack(padx=10)
    
    def update_scale_label(event=None):
        scale_label.config(text=f"Wert: {scale_var.get():.1f}")
    
    scale.bind("<Motion>", update_scale_label)
    
    # Tab 2: Auswahl Widgets
    selection_frame = ttk.Frame(notebook)
    notebook.add(selection_frame, text="Auswahl Widgets")
    
    # Checkbutton
    ttk.Label(selection_frame, text="Checkbuttons:").pack(anchor="w", padx=10, pady=5)
    check_vars = []
    for i, option in enumerate(["Option A", "Option B", "Option C"]):
        var = tk.BooleanVar()
        check_vars.append(var)
        ttk.Checkbutton(selection_frame, text=option, variable=var).pack(anchor="w", padx=20)
    
    # Radiobutton
    ttk.Label(selection_frame, text="Radiobuttons:").pack(anchor="w", padx=10, pady=5)
    radio_var = tk.StringVar(value="radio1")
    for i, option in enumerate(["Rot", "Grün", "Blau"]):
        ttk.Radiobutton(selection_frame, text=option, variable=radio_var, 
                       value=f"radio{i+1}").pack(anchor="w", padx=20)
    
    # Listbox (klassisches tkinter, da TTK keine hat)
    ttk.Label(selection_frame, text="Listbox (klassisches tkinter):").pack(anchor="w", padx=10, pady=5)
    listbox = tk.Listbox(selection_frame, height=4)
    for item in ["Element 1", "Element 2", "Element 3", "Element 4"]:
        listbox.insert(tk.END, item)
    listbox.pack(padx=10, pady=5)
    
    # Tab 3: Anzeige Widgets
    display_frame = ttk.Frame(notebook)
    notebook.add(display_frame, text="Anzeige Widgets")
    
    # Label mit verschiedenen Optionen
    ttk.Label(display_frame, text="Labels:").pack(anchor="w", padx=10, pady=5)
    ttk.Label(display_frame, text="Normales Label").pack(anchor="w", padx=20)
    ttk.Label(display_frame, text="Label mit Relief", relief="raised").pack(anchor="w", padx=20, pady=2)
    
    # Progressbar
    ttk.Label(display_frame, text="Progressbar:").pack(anchor="w", padx=10, pady=5)
    progress = ttk.Progressbar(display_frame, length=200, mode='determinate')
    progress.pack(padx=10, pady=5)
    progress['value'] = 60
    
    # Indeterminate Progressbar
    progress_indeterminate = ttk.Progressbar(display_frame, length=200, mode='indeterminate')
    progress_indeterminate.pack(padx=10, pady=5)
    
    def toggle_progress():
        if progress_indeterminate.cget('value') == 0:
            progress_indeterminate.start(interval=10)
        else:
            progress_indeterminate.stop()
    
    ttk.Button(display_frame, text="Progress Animation Toggle", 
              command=toggle_progress).pack(padx=10, pady=5)
    
    # Separator
    ttk.Label(display_frame, text="Separators:").pack(anchor="w", padx=10, pady=5)
    ttk.Separator(display_frame, orient='horizontal').pack(fill='x', padx=20, pady=5)
    
    # Tab 4: Container Widgets
    container_frame = ttk.Frame(notebook)
    notebook.add(container_frame, text="Container")
    
    # LabelFrame
    labelframe = ttk.LabelFrame(container_frame, text="LabelFrame Beispiel", padding=10)
    labelframe.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(labelframe, text="Inhalt des LabelFrames").pack()
    ttk.Button(labelframe, text="Button im LabelFrame").pack(pady=5)
    
    # PanedWindow
    ttk.Label(container_frame, text="PanedWindow (verstellbare Bereiche):").pack(anchor="w", padx=10)
    paned = ttk.PanedWindow(container_frame, orient="horizontal")
    paned.pack(fill="both", expand=True, padx=10, pady=10)
    
    left_frame = ttk.Frame(paned)
    right_frame = ttk.Frame(paned)
    
    paned.add(left_frame, weight=1)
    paned.add(right_frame, weight=1)
    
    ttk.Label(left_frame, text="Linker Bereich\n(verstellbar)").pack(expand=True)
    ttk.Label(right_frame, text="Rechter Bereich\n(verstellbar)").pack(expand=True)
    
    root.mainloop()
    
alle_ttk_widgets()