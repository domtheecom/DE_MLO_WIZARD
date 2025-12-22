from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont


PALETTE = {
    "shell": "#cfe8ff",
    "office": "#b3f0ff",
    "dorm": "#fbd0ff",
    "stairs": "#fff0b3",
    "bay": "#d7ffd6",
    "props": "#333333",
}


def _compute_bounds(layout: dict, props: List[Dict]) -> Tuple[float, float, float, float]:
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")

    for module in layout.get("modules", []):
        x, y, _ = module["position"]
        size_x, size_y, _ = module["size"]
        min_x = min(min_x, x - size_x / 2)
        max_x = max(max_x, x + size_x / 2)
        min_y = min(min_y, y - size_y / 2)
        max_y = max(max_y, y + size_y / 2)

    for prop in props:
        x, y, _ = prop["position"]
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    if min_x == float("inf"):
        min_x = min_y = -1.0
        max_x = max_y = 1.0

    return min_x, min_y, max_x, max_y


def _world_to_canvas(x, y, bounds, canvas_size, padding):
    min_x, min_y, max_x, max_y = bounds
    width, height = canvas_size
    span_x = max(max_x - min_x, 1.0)
    span_y = max(max_y - min_y, 1.0)
    scale = min((width - padding * 2) / span_x, (height - padding * 2) / span_y)
    cx = padding + (x - min_x) * scale
    cy = padding + (y - min_y) * scale
    return cx, cy, scale


def render_preview(layout: dict, props: List[Dict], output_path: str, size=(900, 600)) -> str:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    bounds = _compute_bounds(layout, props)
    padding = 40

    for module in layout.get("modules", []):
        x, y, _ = module["position"]
        size_x, size_y, _ = module["size"]
        cx, cy, scale = _world_to_canvas(x, y, bounds, size, padding)
        half_w = (size_x / 2) * scale
        half_h = (size_y / 2) * scale
        left = cx - half_w
        right = cx + half_w
        top = cy - half_h
        bottom = cy + half_h
        color = PALETTE.get(module["kind"], "#dddddd")
        draw.rectangle([left, top, right, bottom], outline="#222222", fill=color, width=2)

    for prop in props:
        x, y, _ = prop["position"]
        cx, cy, _ = _world_to_canvas(x, y, bounds, size, padding)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=PALETTE["props"])

    legend_x = size[0] - 220
    legend_y = 20
    legend_items = ["shell", "office", "dorm", "stairs", "bay", "props"]
    draw.rectangle(
        [legend_x - 10, legend_y - 10, legend_x + 190, legend_y + 150],
        fill="#f7f7f7",
        outline="#aaaaaa",
    )

    font = ImageFont.load_default()
    for index, item in enumerate(legend_items):
        y_offset = legend_y + index * 22
        draw.rectangle(
            [legend_x, y_offset, legend_x + 16, y_offset + 16],
            fill=PALETTE[item],
            outline="#222222",
        )
        draw.text((legend_x + 24, y_offset), item.title(), fill="#222222", font=font)

    image.save(output_path, "PNG")
    return output_path


def render_preview_for_ui(layout: dict, props: List[Dict], size=(450, 300)) -> Image.Image:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    bounds = _compute_bounds(layout, props)
    padding = 20

    for module in layout.get("modules", []):
        x, y, _ = module["position"]
        size_x, size_y, _ = module["size"]
        cx, cy, scale = _world_to_canvas(x, y, bounds, size, padding)
        half_w = (size_x / 2) * scale
        half_h = (size_y / 2) * scale
        draw.rectangle(
            [cx - half_w, cy - half_h, cx + half_w, cy + half_h],
            outline="#222222",
            fill=PALETTE.get(module["kind"], "#dddddd"),
            width=2,
        )

    for prop in props:
        x, y, _ = prop["position"]
        cx, cy, _ = _world_to_canvas(x, y, bounds, size, padding)
        draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=PALETTE["props"])

    return image


__all__ = ["render_preview", "render_preview_for_ui"]
