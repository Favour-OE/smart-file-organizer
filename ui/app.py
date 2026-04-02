import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sorter import sort_files, watch_folder, reverse_sort
from config import FILE_TYPES

class FileSortApp:
  def __init__(self):
    self.source = ""
    self.dest = ""
    self.watch_mode = False
    self.watch_thread = None
    self.stop_watch = False

    self.root = tk.Tk()
    self.root.title("Smart File Organizer")
    self.root.geometry("620x580")
    self.root.resizable(False, False)
    self.root.configure(bg="#1e1e2e")

    header = tk.Frame(self.root, bg="#1e1e2e")
    header.pack(fill="x", padx=20, pady=(16, 8))
    tk.Label(header, text="FileSort", font=("Segoe UI", 18, "bold"), fg="#cdd6f4", bg="#1e1e2e").pack(anchor="w")
    tk.Label(header, text="Automatic file organizer", font=("Segoe UI", 10), fg="#6c7086", bg="#1e1e2e").pack(anchor="w")

    content = tk.Frame(self.root, bg="#1e1e2e")
    content.pack(fill="both", expand=True, padx=20, pady=8)

    def folder_row(label, row):
      tk.Label(content, text=label, font=("Segoe UI", 10), fg="#cdd6f4", bg="#1e1e2e").grid(row=row, column=0, sticky="w", pady=6)
      path_var = tk.StringVar(value="No folder selected")
      tk.Label(content, textvariable=path_var, font=("Consolas", 9), fg="#a6adc8", bg="#11111b", padx=8, pady=5, anchor="w", width=35).grid(row=row, column=1, padx=(8, 0), pady=6)
      tk.Button(content, text="Browse", command=lambda v=path_var, is_src=(row==0): self.browse(v, is_src), bg="#313244", fg="#cdd6f4", activebackground="#45475a", activeforeground="#cdd6f4", relief="flat", padx=10, cursor="hand2").grid(row=row, column=2, padx=(8, 0), pady=6)
      return path_var

    self.source_var = folder_row("Source:", 0)
    self.dest_var = folder_row("Destination:", 1)

    tk.Frame(content, bg="#1e1e2e", height=8).grid(row=2, column=0, columnspan=3)

    mode_frame = tk.Frame(content, bg="#1e1e2e")
    mode_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 8))
    tk.Label(mode_frame, text="Mode:", font=("Segoe UI", 10), fg="#cdd6f4", bg="#1e1e2e").pack(side="left")

    self.mode_var = tk.StringVar(value="sort")
    sort_rb = tk.Radiobutton(mode_frame, text="Manual Sort", variable=self.mode_var, value="sort", font=("Segoe UI", 10), fg="#cdd6f4", bg="#1e1e2e", selectcolor="#11111b", activebackground="#1e1e2e", activeforeground="#cdd6f4", command=self.on_mode_change)
    sort_rb.pack(side="left", padx=(8, 16))
    watch_rb = tk.Radiobutton(mode_frame, text="Watch Mode", variable=self.mode_var, value="watch", font=("Segoe UI", 10), fg="#cdd6f4", bg="#1e1e2e", selectcolor="#11111b", activebackground="#1e1e2e", activeforeground="#cdd6f4", command=self.on_mode_change)
    watch_rb.pack(side="left")

    toggles_frame = tk.LabelFrame(content, text="Options", font=("Segoe UI", 10), fg="#cdd6f4", bg="#1e1e2e", labelanchor="n", padx=12, pady=8)
    toggles_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 8))

    self.recursive_var = tk.BooleanVar(value=False)
    tk.Checkbutton(toggles_frame, text="Recursive (include subfolders)", variable=self.recursive_var, font=("Segoe UI", 9), fg="#cdd6f4", bg="#1e1e2e", selectcolor="#313244", activebackground="#1e1e2e", activeforeground="#89b4fa").pack(anchor="w")

    self.log_var = tk.BooleanVar(value=False)
    tk.Checkbutton(toggles_frame, text="Log to activity_log.txt", variable=self.log_var, font=("Segoe UI", 9), fg="#cdd6f4", bg="#1e1e2e", selectcolor="#313244", activebackground="#1e1e2e", activeforeground="#89b4fa").pack(anchor="w")

    self.dup_var = tk.BooleanVar(value=True)
    tk.Checkbutton(toggles_frame, text="Handle duplicates (rename if exists)", variable=self.dup_var, font=("Segoe UI", 9), fg="#cdd6f4", bg="#1e1e2e", selectcolor="#313244", activebackground="#1e1e2e", activeforeground="#89b4fa").pack(anchor="w")

    categories_frame = tk.LabelFrame(content, text="Categories", font=("Segoe UI", 10), fg="#cdd6f4", bg="#1e1e2e", labelanchor="n", padx=12, pady=8)
    categories_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 8))

    self.category_vars = {}
    for i, category in enumerate(FILE_TYPES.keys()):
      var = tk.BooleanVar(value=True)
      self.category_vars[category] = var
      tk.Checkbutton(categories_frame, text=category, variable=var, font=("Segoe UI", 9), fg="#cdd6f4", bg="#1e1e2e", selectcolor="#313244", activebackground="#1e1e2e", activeforeground="#89b4fa").pack(anchor="w", padx=(i % 2) * 80)

    btn_frame = tk.Frame(content, bg="#1e1e2e")
    btn_frame.grid(row=6, column=0, columnspan=3, pady=(4, 8))

    self.action_btn = tk.Button(btn_frame, text="Sort Now", command=self.run_action, font=("Segoe UI", 10, "bold"), bg="#89b4fa", fg="#11111b", activebackground="#74c7ec", activeforeground="#11111b", relief="flat", pady=10, cursor="hand2", width=14)
    self.action_btn.pack(side="left", padx=(0, 8))

    self.reverse_btn = tk.Button(btn_frame, text="Restore Files", command=self.run_reverse, font=("Segoe UI", 10, "bold"), bg="#cba6f7", fg="#11111b", activebackground="#b4befe", activeforeground="#11111b", relief="flat", pady=10, cursor="hand2", width=14)
    self.reverse_btn.pack(side="left")

    self.status = tk.Label(content, text="Ready", font=("Segoe UI", 10), fg="#a6e3a1", bg="#1e1e2e")
    self.status.grid(row=7, column=0, columnspan=3, pady=(0, 4))

    log_frame = tk.LabelFrame(content, text="Activity Log", font=("Segoe UI", 9), fg="#cdd6f4", bg="#1e1e2e", labelanchor="n")
    log_frame.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(4, 0))
    content.grid_rowconfigure(8, weight=1)

    self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 9), fg="#cdd6f4", bg="#11111b", insertbackground="#cdd6f4", relief="flat", height=8, width=68, state="disabled")
    self.log_text.pack(fill="both", expand=True, padx=6, pady=6)

    self.root.mainloop()

  def browse(self, path_var, is_src):
    folder = filedialog.askdirectory()
    if folder:
      path_var.set(folder)
      if is_src:
        self.source = folder
      else:
        self.dest = folder

  def on_mode_change(self):
    mode = self.mode_var.get()
    self.watch_mode = (mode == "watch")
    if self.watch_mode:
      self.action_btn.config(text="Start Watching", bg="#f9e2af", fg="#11111b", activebackground="#fab387", activeforeground="#11111b")
      self.reverse_btn.config(state="disabled")
    else:
      self.action_btn.config(text="Sort Now", bg="#89b4fa", fg="#11111b", activebackground="#74c7ec", activeforeground="#11111b")
      self.reverse_btn.config(state="normal")

  def get_selected_categories(self):
    return [cat for cat, var in self.category_vars.items() if var.get()]

  def log_message(self, msg):
    self.log_text.config(state="normal")
    self.log_text.insert("end", msg + "\n")
    self.log_text.see("end")
    self.log_text.config(state="disabled")

  def run_action(self):
    if self.watch_mode:
      self.toggle_watch()
    else:
      self.run_sort()

  def run_sort(self):
    if not self.source:
      messagebox.showerror("Error", "Please select a source folder")
      return
    if not self.dest:
      messagebox.showerror("Error", "Please select a destination folder")
      return

    categories = self.get_selected_categories()
    if not categories:
      messagebox.showerror("Error", "Please select at least one category")
      return

    self.action_btn.config(state="disabled", text="Sorting...")
    self.status.config(text="Sorting files...", fg="#f9e2af")
    self.root.update()

    try:
      counts = sort_files(
        self.source, self.dest,
        categories=categories,
        recursive=self.recursive_var.get(),
        log=self.log_var.get(),
        duplicate_handling=self.dup_var.get()
      )
      total = sum(counts.values())
      result = f"Sorted {total} file{'s' if total != 1 else ''}"
      self.status.config(text=result, fg="#a6e3a1")
      self.log_message(f"[SORT] {result}")
      for cat, cnt in counts.items():
        self.log_message(f"  {cat}: {cnt} file{'s' if cnt != 1 else ''}")
    except Exception as e:
      messagebox.showerror("Error", str(e))
      self.status.config(text="Error occurred", fg="#f38ba8")
      self.log_message(f"[ERROR] {str(e)}")

    self.action_btn.config(state="normal", text="Sort Now")
    self.reverse_btn.config(state="normal")

  def run_reverse(self):
    if not self.source:
      messagebox.showerror("Error", "Please select a source folder")
      return
    if not self.dest:
      messagebox.showerror("Error", "Please select a destination folder")
      return

    categories = self.get_selected_categories()
    if not categories:
      messagebox.showerror("Error", "Please select at least one category")
      return

    self.action_btn.config(state="disabled")
    self.reverse_btn.config(state="disabled", text="Restoring...")
    self.status.config(text="Restoring files...", fg="#f9e2af")
    self.root.update()

    try:
      counts = reverse_sort(
        self.source, self.dest,
        categories=categories,
        recursive=self.recursive_var.get(),
        log=self.log_var.get(),
        duplicate_handling=self.dup_var.get()
      )
      total = sum(counts.values())
      result = f"Restored {total} file{'s' if total != 1 else ''}"
      self.status.config(text=result, fg="#a6e3a1")
      self.log_message(f"[RESTORE] {result}")
      for cat, cnt in counts.items():
        self.log_message(f"  {cat}: {cnt} file{'s' if cnt != 1 else ''}")
    except Exception as e:
      messagebox.showerror("Error", str(e))
      self.status.config(text="Error occurred", fg="#f38ba8")
      self.log_message(f"[ERROR] {str(e)}")

    self.action_btn.config(state="normal")
    self.reverse_btn.config(state="normal", text="Restore Files")

  def toggle_watch(self):
    if self.watch_thread and self.watch_thread.is_alive():
      self.stop_watch = True
      self.action_btn.config(state="disabled", text="Stopping...")
      self.status.config(text="Stopping watch mode...", fg="#f9e2af")
      self.root.update()
      return

    if not self.source:
      messagebox.showerror("Error", "Please select a source folder")
      return
    if not self.dest:
      messagebox.showerror("Error", "Please select a destination folder")
      return

    categories = self.get_selected_categories()
    if not categories:
      messagebox.showerror("Error", "Please select at least one category")
      return

    self.stop_watch = False
    self.action_btn.config(text="Stop Watching", bg="#f38ba8", fg="#11111b", activebackground="#eba0ac", activeforeground="#11111b")
    self.status.config(text="Watching for new files...", fg="#f9e2af")
    self.log_message("[WATCH] Started watching for new files")

    self.watch_thread = threading.Thread(target=self._watch_files, args=(categories,), daemon=True)
    self.watch_thread.start()

  def _watch_files(self, categories):
    try:
      watch_folder(
        self.source, self.dest,
        categories=categories,
        recursive=self.recursive_var.get(),
        log=self.log_var.get(),
        duplicate_handling=self.dup_var.get()
      )
    except Exception as e:
      self.root.after(0, lambda: self.log_message(f"[ERROR] {str(e)}"))
      self.root.after(0, lambda: self.status.config(text="Watch error", fg="#f38ba8"))

if __name__ == "__main__":
  FileSortApp()
