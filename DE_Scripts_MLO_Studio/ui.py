import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

import app


ACCENT_CYAN = "#16e0ff"
ACCENT_MAGENTA = "#ff3cc7"
BG_DARK = "#0f1115"
BG_PANEL = "#161a20"
FG_TEXT = "#e6e6e6"


class MLOStudioUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DE Scripts MLO Studio")
        self.configure(bg=BG_DARK)
        self.geometry("1100x650")

        self.preview_photo = None
        self.latest_output_path = None
        self.latest_preview_path = None

        self._build_style()
        self._build_layout()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Header.TFrame", background=BG_PANEL
        )
        style.configure(
            "Accent.TButton",
            background=ACCENT_CYAN,
            foreground="#0a0a0a",
            padding=8,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_MAGENTA)],
        )
        style.configure(
            "Panel.TFrame",
            background=BG_PANEL,
        )
        style.configure(
            "Status.TLabel",
            background=BG_DARK,
            foreground=FG_TEXT,
        )

    def _build_layout(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x")

        logo_path = os.path.join(os.path.dirname(__file__), "assets", "de_scripts_logo.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((160, 48))
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(header, image=self.logo_photo, bg=BG_PANEL)
                logo_label.pack(side="left", padx=12, pady=12)
            except Exception:
                self.logo_photo = None
        title = tk.Label(
            header,
            text="DE Scripts MLO Studio",
            fg=FG_TEXT,
            bg=BG_PANEL,
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(side="left", padx=10, pady=12)

        body = ttk.Frame(self, style="Panel.TFrame")
        body.pack(fill="both", expand=True, padx=12, pady=12)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(body, style="Panel.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_panel = ttk.Frame(body, style="Panel.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

        prompt_label = tk.Label(
            left_panel,
            text="Describe your MLO",
            fg=FG_TEXT,
            bg=BG_PANEL,
            font=("Segoe UI", 12, "bold"),
        )
        prompt_label.pack(anchor="w", padx=10, pady=(10, 6))

        self.prompt_text = tk.Text(
            left_panel,
            height=18,
            wrap="word",
            bg="#0d1117",
            fg=FG_TEXT,
            insertbackground=ACCENT_CYAN,
            relief="flat",
            font=("Segoe UI", 11),
        )
        self.prompt_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.prompt_text.insert(
            "1.0",
            "Two-floor fire station with 3 bays, 2 offices, and 2 dorms.",
        )

        button_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        build_button = ttk.Button(
            button_frame, text="Build MLO", style="Accent.TButton", command=self._build_mlo
        )
        build_button.pack(side="left", padx=(0, 8))

        open_output_button = ttk.Button(
            button_frame, text="Open Output Folder", command=self._open_output
        )
        open_output_button.pack(side="left", padx=(0, 8))

        open_preview_button = ttk.Button(
            button_frame, text="Open Preview Image", command=self._open_preview
        )
        open_preview_button.pack(side="left")

        preview_label = tk.Label(
            right_panel,
            text="Preview",
            fg=FG_TEXT,
            bg=BG_PANEL,
            font=("Segoe UI", 12, "bold"),
        )
        preview_label.pack(anchor="w", padx=10, pady=(10, 6))

        self.preview_canvas = tk.Label(
            right_panel,
            bg="#ffffff",
            relief="flat",
            text="Build to see preview",
            font=("Segoe UI", 11),
        )
        self.preview_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready.")
        status = ttk.Label(self, textvariable=self.status_var, style="Status.TLabel")
        status.pack(fill="x", padx=12, pady=(0, 10))

    def _build_mlo(self):
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Missing Prompt", "Please enter a prompt.")
            return
        try:
            result = app.run(prompt)
        except Exception as exc:
            messagebox.showerror("Build Failed", str(exc))
            self.status_var.set("Build failed.")
            return

        self.latest_output_path = result["output_path"]
        self.latest_preview_path = result["preview_png_path"]
        self._update_preview(self.latest_preview_path)

        warnings = result.get("warnings", [])
        if warnings:
            warning_text = " ".join(warnings)
            messagebox.showwarning("Archetype Warnings", warning_text)
        self.status_var.set(f"Build complete: {result['resource_name']}")

    def _update_preview(self, preview_path: str):
        try:
            image = Image.open(preview_path)
            image.thumbnail((520, 400))
            self.preview_photo = ImageTk.PhotoImage(image)
            self.preview_canvas.configure(image=self.preview_photo, text="")
        except Exception as exc:
            self.preview_canvas.configure(text=f"Preview load failed: {exc}")

    def _open_output(self):
        if not self.latest_output_path:
            messagebox.showinfo("Output Folder", "Build an MLO first.")
            return
        _open_path(self.latest_output_path)

    def _open_preview(self):
        if not self.latest_preview_path:
            messagebox.showinfo("Preview Image", "Build an MLO first.")
            return
        _open_path(self.latest_preview_path)


def _open_path(path: str):
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform.startswith("darwin"):
        os.system(f"open '{path}'")
    else:
        os.system(f"xdg-open '{path}'")


def main():
    app_ui = MLOStudioUI()
    app_ui.mainloop()


if __name__ == "__main__":
    main()
