from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from .planner import Placement, ShellChoice


class PreviewRenderer:
    def __init__(self, size: tuple[int, int] = (640, 480)) -> None:
        self.size = size

    def render(self, shell: ShellChoice, placements: Iterable[Placement], output_path: Path) -> None:
        img = Image.new("RGB", self.size, color="white")
        draw = ImageDraw.Draw(img)

        width = shell.footprint.get("width", 20.0)
        depth = shell.footprint.get("depth", 20.0)

        margin = 40
        scale_x = (self.size[0] - margin * 2) / max(width, 1)
        scale_y = (self.size[1] - margin * 2) / max(depth, 1)
        scale = min(scale_x, scale_y)

        center = (self.size[0] / 2, self.size[1] / 2)
        half_w = width * scale / 2
        half_d = depth * scale / 2
        shell_rect = [
            center[0] - half_w,
            center[1] - half_d,
            center[0] + half_w,
            center[1] + half_d,
        ]
        draw.rectangle(shell_rect, outline="#222222", width=3)

        font = None
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except OSError:
            font = ImageFont.load_default()

        draw.text((margin, margin - 20), f"Shell: {shell.shell_name}", fill="#111111", font=font)

        for placement in placements:
            px = center[0] + placement.position[0] * scale
            py = center[1] + placement.position[1] * scale
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill="#d62828", outline="#111111")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
