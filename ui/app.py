import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sorter import sort_files

class FileSortApp:
  def __init__(self):
    self.source = ""
    self.dest = ""
    
    self.root = tk.Tk()
    self.root.title("Smart File Organizer")
    self.root.geometry("480x320")
    self.root.resizable(False, False)
    self.root.configure(bg="#1e1e2e")
    
    header = tk.Frame(self.root, bg="#1e1e2e")
    header.pack(fill="x", padx=24, pady=(20, 8))
    tk.Label(header, text="FileSort", font=("Segoe UI", 18, "bold"), fg="#cdd6f4", bg="#1e1e2e").pack(anchor="w")
    tk.Label(header, text="Automatic file organizer", font=("Segoe UI", 10), fg="#6c7086", bg="#1e1e2e").pack(anchor="w")
    
    content = tk.Frame(self.root, bg="#1e1e2e")
    content.pack(fill="both", expand=True, padx=24, pady=12)
    
    def folder_row(label, row):
      tk.Label(content, text=label, font=("Segoe UI", 11), fg="#cdd6f4", bg="#1e1e2e").grid(row=row, column=0, sticky="w", pady=8)
      path_var = tk.StringVar(value="No folder selected")
      tk.Label(content, textvariable=path_var, font=("Consolas", 10), fg="#a6adc8", bg="#11111b", padx=8, pady=6, anchor="w", width=32).grid(row=row, column=1, padx=(8, 0), pady=8)
      tk.Button(content, text="Browse", command=lambda: self.browse(path_var), bg="#313244", fg="#cdd6f4", activebackground="#45475a", activeforeground="#cdd6f4", relief="flat", padx=12, cursor="hand2").grid(row=row, column=2, padx=(8, 0), pady=8)
      return path_var
    
    self.source_var = folder_row("Source:", 0)
    self.dest_var = folder_row("Destination:", 1)
    
    tk.Frame(content, bg="#1e1e2e", height=12).grid(row=2, column=0, columnspan=3)
    
    self.sort_btn = tk.Button(content, text="Sort Now", command=self.run_sort, font=("Segoe UI", 11, "bold"), bg="#89b4fa", fg="#11111b", activebackground="#74c7ec", activeforeground="#11111b", relief="flat", pady=10, cursor="hand2", width=20)
    self.sort_btn.grid(row=3, column=0, columnspan=3, pady=(4, 0))
    
    self.status = tk.Label(content, text="", font=("Segoe UI", 10), fg="#a6e3a1", bg="#1e1e2e")
    self.status.grid(row=4, column=0, columnspan=3, pady=12)
    
    self.root.mainloop()
  
  def browse(self, path_var):
    folder = filedialog.askdirectory()
    if folder:
      path_var.set(folder)
      if path_var == self.source_var:
        self.source = folder
      else:
        self.dest = folder
  
  def run_sort(self):
    if not self.source:
      messagebox.showerror("Error", "Please select a source folder")
      return
    if not self.dest:
      messagebox.showerror("Error", "Please select a destination folder")
      return
    
    self.sort_btn.config(state="disabled", text="Sorting...")
    self.status.config(text="Sorting files...")
    self.root.update()
    
    try:
      counts = sort_files(self.source, self.dest)
      total = sum(counts.values())
      self.status.config(text=f"Sorted {total} file{'s' if total != 1 else ''}")
    except Exception as e:
      messagebox.showerror("Error", str(e))
      self.status.config(text="Error occurred")
    
    self.sort_btn.config(state="normal", text="Sort Now")

if __name__ == "__main__":
  FileSortApp()
