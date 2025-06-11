import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont

# ========== 1. GRUNDLAGEN: TK vs TTK ==========

def tk_vs_ttk_vergleich():
    """Zeigt den Unterschied zwischen tk und ttk Widgets"""
    root = tk.Tk()
    root.title("TK vs TTK Vergleich")
    root.geometry("600x400")
    
    # Linke Seite: Klassische TK Widgets
    tk_frame = tk.Frame(root, bg="lightgray", relief="raised", bd=2)
    tk_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    tk.Label(tk_frame, text="Klassische TK Widgets", font=("Arial", 14, "bold"), 
             bg="lightgray").pack(pady=10)
    
    tk.Label(tk_frame, text="Normales Label", bg="lightgray").pack(pady=5)
    tk.Button(tk_frame, text="TK Button").pack(pady=5)
    tk.Entry(tk_frame, width=20).pack(pady=5)
    
    # Progressbar gibt es nur in TTK
    tk.Label(tk_frame, text="(Keine Progressbar in TK)", 
             bg="lightgray", fg="red").pack(pady=5)
    
    # Rechte Seite: TTK Widgets (modern und themed)
    ttk_frame = ttk.Frame(root, relief="raised", borderwidth=2)
    ttk_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    ttk.Label(ttk_frame, text="Moderne TTK Widgets", 
              font=("Arial", 14, "bold")).pack(pady=10)
    
    ttk.Label(ttk_frame, text="TTK Label (themed)").pack(pady=5)
    ttk.Button(ttk_frame, text="TTK Button").pack(pady=5)
    ttk.Entry(ttk_frame, width=20).pack(pady=5)
    
    # TTK spezifische Widgets
    progress = ttk.Progressbar(ttk_frame, length=150, mode='determinate')
    progress.pack(pady=5)
    progress['value'] = 70
    
    ttk.Separator(ttk_frame, orient='horizontal').pack(fill='x', pady=10)
    
    # Combobox (nur in TTK)
    combo = ttk.Combobox(ttk_frame, values=["Option 1", "Option 2", "Option 3"])
    combo.pack(pady=5)
    combo.set("Wähle eine Option")
    
    root.mainloop()
    
tk_vs_ttk_vergleich()