import json
import os
import tkinter as tk
from tkinter import messagebox

from exporter import export_resource
from furnishing_engine import build_furnishings
from layout_engine import build_layout
from portal_engine import build_portals
from prompt_parser import parse_prompt
from ymap_builder import build_ymap


class PromptMLOUI(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self._build_widgets()

    def _build_widgets(self) -> None:
        self.prompt_label = tk.Label(self, text="Enter MLO prompt:")
        self.prompt_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.prompt_text = tk.Text(self, height=8)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.build_button = tk.Button(self, text="Build MLO", command=self._on_build)
        self.build_button.pack(pady=(0, 10))

        self.status_label = tk.Label(self, text="Ready.")
        self.status_label.pack(anchor="w", padx=10, pady=(0, 10))

    def _on_build(self) -> None:
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Prompt required", "Please enter a prompt.")
            return

        try:
            data = parse_prompt(prompt)
            layout = build_layout(data)
            portals = build_portals(layout)
            furnishings = build_furnishings(layout)

            ymap_xml = build_ymap(layout, furnishings)
            output_path = export_resource(data["resource_name"], ymap_xml)

            with open(os.path.join(output_path, "meta.json"), "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "prompt": prompt,
                        "layout": layout,
                        "portals": portals,
                        "furnishings": furnishings,
                    },
                    handle,
                    indent=2,
                )

            self.status_label.config(text=f"Built resource: {output_path}")
            messagebox.showinfo("Success", f"Resource exported to {output_path}")
        except Exception as exc:  # pragma: no cover - UI error path
            messagebox.showerror("Build failed", str(exc))
            self.status_label.config(text="Build failed.")
