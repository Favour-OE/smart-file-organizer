import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    from sorter import sort_files, watch_folder, reverse_sort
    from config import FILE_TYPES
except ImportError:

    def sort_files(*a, **kw):
        return {"Images": 2, "Documents": 1}

    def reverse_sort(*a, **kw):
        return {"Images": 1}

    def watch_folder(*a, **kw):
        pass

    FILE_TYPES = {
        "Images": [],
        "Documents": [],
        "Videos": [],
        "Audio": [],
        "Archives": [],
        "Code": [],
    }


BG = "#0D0F14"  
PANEL = "#13161E"
BORDER = "#1E2330"
ACCENT = "#00D4B4"
ACCENT_DIM = "#00A892" 
ACCENT_BG = "#0D2E2A"  
TEXT = "#E8EAF0"  
TEXT_SUB = "#6B7280"
SUCCESS = "#22C796"
WARNING = "#F59E0B"
ERROR = "#F43F5E"
PILL_BG = "#1A1D27"
SEL_BG = "#162625"

FONT_TITLE = ("Helvetica Neue", 18, "bold")
FONT_SUB = ("Helvetica Neue", 9)
FONT_LABEL = ("Helvetica Neue", 9, "bold")
FONT_BODY = ("Helvetica Neue", 9)
FONT_MONO = ("Courier New", 9)
FONT_BTN = ("Helvetica Neue", 9, "bold")



def flat_btn(parent, text, command, bg=PANEL, fg=TEXT, width=None, **kw):
    cfg = dict(
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=ACCENT_DIM,
        activeforeground=BG,
        relief="flat",
        bd=0,
        font=FONT_BTN,
        cursor="hand2",
        padx=16,
        pady=8,
    )
    if width:
        cfg["width"] = width
    cfg.update(kw)
    b = tk.Button(parent, **cfg)
    b.bind("<Enter>", lambda e: b.config(bg=ACCENT if bg == ACCENT else BORDER))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def section_label(parent, text, row, col=0, span=3, pady=(14, 4)):
    lbl = tk.Label(
        parent,
        text=text.upper(),
        font=("Helvetica Neue", 7, "bold"),
        fg=ACCENT,
        bg=BG,
        lettersp=2,
    )
    lbl.grid(row=row, column=col, columnspan=span, sticky="w", pady=pady)
    return lbl


def hline(parent, row, span=3, pady=(0, 6)):
    f = tk.Frame(parent, bg=BORDER, height=1)
    f.grid(row=row, column=0, columnspan=span, sticky="ew", pady=pady)


class TogglePill(tk.Frame):
    """Two-option pill toggle."""

    def __init__(self, parent, options, variable, command=None, **kw):
        super().__init__(parent, bg=PILL_BG, **kw)
        self._var = variable
        self._cmd = command
        self._btns = {}

        self.configure(highlightbackground=BORDER, highlightthickness=1)
        for val, label in options:
            b = tk.Label(
                self,
                text=label,
                font=FONT_BTN,
                bg=PILL_BG,
                fg=TEXT_SUB,
                padx=18,
                pady=6,
                cursor="hand2",
            )
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, v=val: self._select(v))
            self._btns[val] = b

        self._refresh()

    def _select(self, val):
        self._var.set(val)
        self._refresh()
        if self._cmd:
            self._cmd()

    def _refresh(self):
        cur = self._var.get()
        for val, b in self._btns.items():
            if val == cur:
                b.config(bg=ACCENT, fg=BG)
            else:
                b.config(bg=PILL_BG, fg=TEXT_SUB)


class ModCheck(tk.Frame):
    def __init__(self, parent, text, variable, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._var = variable
        self._box = tk.Label(
            self,
            width=2,
            font=FONT_LABEL,
            bg=PANEL,
            fg=ACCENT,
            cursor="hand2",
            relief="flat",
            bd=0,
            padx=2,
            pady=1,
        )
        self._box.pack(side="left")
        tk.Label(self, text=text, font=FONT_BODY, fg=TEXT, bg=BG).pack(
            side="left", padx=(6, 0)
        )
        self._box.bind("<Button-1>", self._toggle)
        self.bind("<Button-1>", self._toggle)
        self._refresh()

    def _toggle(self, e=None):
        self._var.set(not self._var.get())
        self._refresh()

    def _refresh(self):
        if self._var.get():
            self._box.config(text="✓", bg=ACCENT, fg=BG)
        else:
            self._box.config(text=" ", bg=PANEL, fg=ACCENT)



class PathRow(tk.Frame):
    def __init__(self, parent, label, browse_cb, **kw):
        super().__init__(parent, bg=BG, **kw)
        tk.Label(
            self, text=label, font=FONT_LABEL, fg=TEXT_SUB, bg=BG, width=12, anchor="w"
        ).pack(side="left")

        self._path_var = tk.StringVar(value="No folder selected")
        path_box = tk.Frame(
            self, bg=PANEL, highlightbackground=BORDER, highlightthickness=1
        )
        path_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(
            path_box,
            textvariable=self._path_var,
            font=FONT_MONO,
            fg=TEXT,
            bg=PANEL,
            anchor="w",
            padx=10,
            pady=7,
        ).pack(fill="x")

        btn = tk.Label(
            self,
            text="Browse →",
            font=FONT_BTN,
            fg=ACCENT,
            bg=PANEL,
            padx=12,
            pady=7,
            cursor="hand2",
            highlightbackground=ACCENT,
            highlightthickness=1,
        )
        btn.pack(side="left")
        btn.bind("<Button-1>", lambda e: browse_cb(self._path_var))
        btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT, fg=BG))
        btn.bind("<Leave>", lambda e: btn.config(bg=PANEL, fg=ACCENT))

    @property
    def path_var(self):
        return self._path_var


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class FileSortApp:
    def __init__(self):
        self.source = ""
        self.dest = ""
        self.watch_mode = False
        self.watch_thread = None
        self.stop_watch = False

        self.root = tk.Tk()
        self.root.title("FileSort — Smart File Organizer")
        self.root.geometry("640x720")
        self.root.minsize(600, 660)
        self.root.configure(bg=BG)
        self._build_ui()
        self.root.mainloop()

    # ── Build UI ────────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── HEADER ──────────────────────────────
        hdr = tk.Frame(root, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(22, 0))

        left_hdr = tk.Frame(hdr, bg=BG)
        left_hdr.pack(side="left", fill="y")

        tk.Label(
            left_hdr,
            text="FileSort",
            font=("Helvetica Neue", 22, "bold"),
            fg=TEXT,
            bg=BG,
        ).pack(anchor="w")
        tk.Label(
            left_hdr,
            text="Smart File Organizer",
            font=("Helvetica Neue", 9),
            fg=TEXT_SUB,
            bg=BG,
        ).pack(anchor="w")

        # status badge (top-right)
        self._status_badge = tk.Label(
            hdr,
            text="● READY",
            font=("Helvetica Neue", 8, "bold"),
            fg=SUCCESS,
            bg=ACCENT_BG,
            padx=10,
            pady=4,
        )
        self._status_badge.pack(side="right", anchor="ne")

        # ── thin accent bar ──────────────────────
        tk.Frame(root, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(10, 0))

        # ── SCROLL CONTAINER ────────────────────
        outer = tk.Frame(root, bg=BG)
        outer.pack(fill="both", expand=True, padx=28, pady=12)

        # ── FOLDERS SECTION ─────────────────────
        tk.Label(
            outer, text="FOLDERS", font=("Helvetica Neue", 7, "bold"), fg=ACCENT, bg=BG
        ).pack(anchor="w", pady=(0, 4))

        src_row = PathRow(outer, "Source", self._browse_source)
        src_row.pack(fill="x", pady=(0, 6))
        self.source_var = src_row.path_var

        dst_row = PathRow(outer, "Destination", self._browse_dest)
        dst_row.pack(fill="x")
        self.dest_var = dst_row.path_var

        # ── MODE SECTION ────────────────────────
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(16, 10))
        tk.Label(
            outer, text="MODE", font=("Helvetica Neue", 7, "bold"), fg=ACCENT, bg=BG
        ).pack(anchor="w", pady=(0, 6))

        self.mode_var = tk.StringVar(value="sort")
        pill = TogglePill(
            outer,
            [("sort", "Manual Sort"), ("watch", "Watch Mode")],
            self.mode_var,
            command=self.on_mode_change,
        )
        pill.pack(anchor="w")

        # ── OPTIONS ─────────────────────────────
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(16, 10))
        tk.Label(
            outer, text="OPTIONS", font=("Helvetica Neue", 7, "bold"), fg=ACCENT, bg=BG
        ).pack(anchor="w", pady=(0, 6))

        opts_grid = tk.Frame(outer, bg=BG)
        opts_grid.pack(fill="x")
        opts_grid.columnconfigure((0, 1), weight=1)

        self.recursive_var = tk.BooleanVar(value=False)
        self.log_var = tk.BooleanVar(value=False)
        self.dup_var = tk.BooleanVar(value=True)

        ModCheck(opts_grid, "Recursive (include subfolders)", self.recursive_var).grid(
            row=0, column=0, sticky="w", pady=3
        )
        ModCheck(opts_grid, "Log to activity_log.txt", self.log_var).grid(
            row=1, column=0, sticky="w", pady=3
        )
        ModCheck(opts_grid, "Handle duplicates (rename)", self.dup_var).grid(
            row=0, column=1, sticky="w", pady=3
        )

        # ── CATEGORIES ──────────────────────────
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(16, 10))
        tk.Label(
            outer,
            text="CATEGORIES",
            font=("Helvetica Neue", 7, "bold"),
            fg=ACCENT,
            bg=BG,
        ).pack(anchor="w", pady=(0, 8))

        cat_grid = tk.Frame(outer, bg=BG)
        cat_grid.pack(fill="x")
        self.category_vars = {}

        cats = list(FILE_TYPES.keys())
        cols = 3
        for i, cat in enumerate(cats):
            var = tk.BooleanVar(value=True)
            self.category_vars[cat] = var
            chip = self._make_chip(cat_grid, cat, var)
            chip.grid(row=i // cols, column=i % cols, padx=(0, 8), pady=3, sticky="w")

        # ── ACTION BUTTONS ──────────────────────
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(16, 10))

        btn_row = tk.Frame(outer, bg=BG)
        btn_row.pack(fill="x")

        self.action_btn = tk.Button(
            btn_row,
            text="Sort Now",
            command=self.run_action,
            font=FONT_BTN,
            bg=ACCENT,
            fg=BG,
            activebackground=ACCENT_DIM,
            activeforeground=BG,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=24,
            pady=10,
        )
        self.action_btn.pack(side="left", padx=(0, 8))
        self.action_btn.bind("<Enter>", lambda e: self.action_btn.config(bg=ACCENT_DIM))
        self.action_btn.bind("<Leave>", lambda e: self.action_btn.config(bg=ACCENT))

        self.reverse_btn = tk.Button(
            btn_row,
            text="Restore Files",
            command=self.run_reverse,
            font=FONT_BTN,
            bg=PANEL,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=24,
            pady=10,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        self.reverse_btn.pack(side="left")
        self.reverse_btn.bind("<Enter>", lambda e: self.reverse_btn.config(bg=BORDER))
        self.reverse_btn.bind("<Leave>", lambda e: self.reverse_btn.config(bg=PANEL))

        # ── ACTIVITY LOG ────────────────────────
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(16, 10))

        log_hdr = tk.Frame(outer, bg=BG)
        log_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(
            log_hdr,
            text="ACTIVITY LOG",
            font=("Helvetica Neue", 7, "bold"),
            fg=ACCENT,
            bg=BG,
        ).pack(side="left")
        clr = tk.Label(
            log_hdr,
            text="Clear",
            font=("Helvetica Neue", 7, "bold"),
            fg=TEXT_SUB,
            bg=BG,
            cursor="hand2",
        )
        clr.pack(side="right")
        clr.bind("<Button-1>", self._clear_log)
        clr.bind("<Enter>", lambda e: clr.config(fg=ACCENT))
        clr.bind("<Leave>", lambda e: clr.config(fg=TEXT_SUB))

        log_wrap = tk.Frame(
            outer, bg=PANEL, highlightbackground=BORDER, highlightthickness=1
        )
        log_wrap.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_wrap,
            font=FONT_MONO,
            fg=TEXT,
            bg=PANEL,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            height=8,
            state="disabled",
            selectbackground=ACCENT_BG,
        )
        self.log_text.pack(fill="both", expand=True, padx=12, pady=10)

        # colour tags
        self.log_text.tag_config("sort", foreground=SUCCESS)
        self.log_text.tag_config("restore", foreground="#60A5FA")
        self.log_text.tag_config("watch", foreground=WARNING)
        self.log_text.tag_config("error", foreground=ERROR)
        self.log_text.tag_config("indent", foreground=TEXT_SUB)

    # ── CHIP widget (category toggle) ───────────
    def _make_chip(self, parent, label, var):
        frame = tk.Frame(parent, bg=BG)

        def refresh():
            if var.get():
                box.config(
                    text=label,
                    bg=ACCENT_BG,
                    fg=ACCENT,
                    highlightbackground=ACCENT,
                    highlightthickness=1,
                )
            else:
                box.config(
                    text=label,
                    bg=PANEL,
                    fg=TEXT_SUB,
                    highlightbackground=BORDER,
                    highlightthickness=1,
                )

        box = tk.Label(
            frame,
            text=label,
            font=("Helvetica Neue", 8, "bold"),
            padx=10,
            pady=5,
            cursor="hand2",
            bg=ACCENT_BG,
            fg=ACCENT,
            highlightbackground=ACCENT,
            highlightthickness=1,
        )
        box.pack()

        def toggle(e=None):
            var.set(not var.get())
            refresh()

        box.bind("<Button-1>", toggle)
        refresh()
        return frame

    # ── STATUS BADGE ────────────────────────────
    def _set_status(self, text, color):
        self._status_badge.config(text=f"● {text.upper()}", fg=color)

    # ── BROWSE ──────────────────────────────────
    def _browse_source(self, path_var):
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(self._truncate(folder))
            self.source = folder

    def _browse_dest(self, path_var):
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(self._truncate(folder))
            self.dest = folder

    def _truncate(self, path, maxlen=48):
        return path if len(path) <= maxlen else "…" + path[-(maxlen - 1) :]

    # ── MODE TOGGLE ─────────────────────────────
    def on_mode_change(self):
        mode = self.mode_var.get()
        self.watch_mode = mode == "watch"
        if self.watch_mode:
            self.action_btn.config(
                text="Start Watching", bg=WARNING, fg=BG, activebackground="#CA8A04"
            )
            self.action_btn.bind(
                "<Enter>", lambda e: self.action_btn.config(bg="#CA8A04")
            )
            self.action_btn.bind(
                "<Leave>", lambda e: self.action_btn.config(bg=WARNING)
            )
            self.reverse_btn.config(state="disabled", fg=TEXT_SUB)
        else:
            self.action_btn.config(
                text="Sort Now", bg=ACCENT, fg=BG, activebackground=ACCENT_DIM
            )
            self.action_btn.bind(
                "<Enter>", lambda e: self.action_btn.config(bg=ACCENT_DIM)
            )
            self.action_btn.bind("<Leave>", lambda e: self.action_btn.config(bg=ACCENT))
            self.reverse_btn.config(state="normal", fg=TEXT)

    # ── CATEGORIES ──────────────────────────────
    def get_selected_categories(self):
        return [cat for cat, var in self.category_vars.items() if var.get()]

    # ── LOG ─────────────────────────────────────
    def log_message(self, msg):
        self.log_text.config(state="normal")
        tag = "indent"
        if "[SORT]" in msg:
            tag = "sort"
        elif "[RESTORE]" in msg:
            tag = "restore"
        elif "[WATCH]" in msg:
            tag = "watch"
        elif "[ERROR]" in msg:
            tag = "error"
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _clear_log(self, e=None):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # ── VALIDATE ────────────────────────────────
    def _validate(self):
        if not self.source:
            messagebox.showerror("Error", "Please select a source folder")
            return False
        if not self.dest:
            messagebox.showerror("Error", "Please select a destination folder")
            return False
        if not self.get_selected_categories():
            messagebox.showerror("Error", "Please select at least one category")
            return False
        return True

    # ── RUN ACTION ──────────────────────────────
    def run_action(self):
        if self.watch_mode:
            self.toggle_watch()
        else:
            self.run_sort()

    def run_sort(self):
        if not self._validate():
            return

        self.action_btn.config(state="disabled", text="Sorting…")
        self.reverse_btn.config(state="disabled")
        self._set_status("Sorting…", WARNING)
        self.root.update()

        try:
            counts = sort_files(
                self.source,
                self.dest,
                categories=self.get_selected_categories(),
                recursive=self.recursive_var.get(),
                log=self.log_var.get(),
                duplicate_handling=self.dup_var.get(),
            )
            total = sum(counts.values())
            result = f"Sorted {total} file{'s' if total != 1 else ''}"
            self._set_status(result, SUCCESS)
            self.log_message(f"[SORT] {result}")
            for cat, cnt in counts.items():
                if cnt:
                    self.log_message(f"  {cat}: {cnt} file{'s' if cnt != 1 else ''}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._set_status("Error", ERROR)
            self.log_message(f"[ERROR] {e}")

        self.action_btn.config(state="normal", text="Sort Now")
        self.reverse_btn.config(state="normal")

    def run_reverse(self):
        if not self._validate():
            return

        self.action_btn.config(state="disabled")
        self.reverse_btn.config(state="disabled", text="Restoring…")
        self._set_status("Restoring…", WARNING)
        self.root.update()

        try:
            counts = reverse_sort(
                self.source,
                self.dest,
                categories=self.get_selected_categories(),
                recursive=self.recursive_var.get(),
                log=self.log_var.get(),
                duplicate_handling=self.dup_var.get(),
            )
            total = sum(counts.values())
            result = f"Restored {total} file{'s' if total != 1 else ''}"
            self._set_status(result, SUCCESS)
            self.log_message(f"[RESTORE] {result}")
            for cat, cnt in counts.items():
                if cnt:
                    self.log_message(f"  {cat}: {cnt} file{'s' if cnt != 1 else ''}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._set_status("Error", ERROR)
            self.log_message(f"[ERROR] {e}")

        self.action_btn.config(state="normal")
        self.reverse_btn.config(state="normal", text="Restore Files")

    def toggle_watch(self):
        if self.watch_thread and self.watch_thread.is_alive():
            self.stop_watch = True
            self.action_btn.config(state="disabled", text="Stopping…")
            self._set_status("Stopping…", WARNING)
            self.root.update()
            return

        if not self._validate():
            return

        self.stop_watch = False
        self.action_btn.config(
            text="Stop Watching", bg=ERROR, fg=TEXT, activebackground="#BE123C"
        )
        self.action_btn.bind("<Enter>", lambda e: self.action_btn.config(bg="#BE123C"))
        self.action_btn.bind("<Leave>", lambda e: self.action_btn.config(bg=ERROR))
        self._set_status("Watching…", WARNING)
        self.log_message("[WATCH] Started watching for new files")

        self.watch_thread = threading.Thread(
            target=self._watch_files,
            args=(self.get_selected_categories(),),
            daemon=True,
        )
        self.watch_thread.start()

    def _watch_files(self, categories):
        try:
            watch_folder(
                self.source,
                self.dest,
                categories=categories,
                recursive=self.recursive_var.get(),
                log=self.log_var.get(),
                duplicate_handling=self.dup_var.get(),
            )
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"[ERROR] {e}"))
            self.root.after(0, lambda: self._set_status("Watch Error", ERROR))


if __name__ == "__main__":
    FileSortApp()
