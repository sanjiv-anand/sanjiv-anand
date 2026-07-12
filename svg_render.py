"""
svg_render.py

Builds the dark-mode and light-mode 'About Sanjiv' SVG window images
(macOS-style, landscape, avatar sidebar + system-info panel).

Used by generate_readme.py, which fills in live GitHub stats and writes
the resulting SVGs to assets/dark_mode.svg and assets/light_mode.svg.
"""

import base64
import os

THEMES = {
    "dark": {
        "window_bg": "#1e1e1e",
        "titlebar_bg": "#2c2c2e",
        "menu_bg": "#252527",
        "divider": "#3a3a3c",
        "text_primary": "#f5f5f7",
        "text_secondary": "#9a9a9e",
        "text_label": "#8e8e93",
        "accent": "#0a84ff",
        "chip_bg": "#2c2c2e",
        "chip_border": "#48484a",
        "window_border": "#000000",
        "traffic_red": "#ff5f57",
        "traffic_yellow": "#febc2e",
        "traffic_green": "#28c840",
        "shadow_opacity": "0.55",
    },
    "light": {
        "window_bg": "#f5f5f7",
        "titlebar_bg": "#e8e8ea",
        "menu_bg": "#eeeeef",
        "divider": "#d1d1d6",
        "text_primary": "#1c1c1e",
        "text_secondary": "#6e6e73",
        "text_label": "#6e6e73",
        "accent": "#0066cc",
        "chip_bg": "#ffffff",
        "chip_border": "#d1d1d6",
        "window_border": "#c7c7cc",
        "traffic_red": "#ff5f57",
        "traffic_yellow": "#febc2e",
        "traffic_green": "#28c840",
        "shadow_opacity": "0.15",
    },
}

FONT = "SF Mono, Menlo, Consolas, 'Courier New', monospace"

WIDTH = 900
HEIGHT = 440
SIDEBAR_W = 260


def _load_avatar_data_uri(avatar_path):
    if not avatar_path or not os.path.exists(avatar_path):
        return None
    with open(avatar_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _text_line(x, y, label, value, colors, label_width=150):
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="13" '
        f'fill="{colors["text_label"]}">{label}</text>'
        f'<text x="{x + label_width}" y="{y}" font-family="{FONT}" font-size="13" '
        f'fill="{colors["text_primary"]}">{value}</text>'
    )


def _section_header(x, y, w, title, colors):
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="13" font-weight="700" '
        f'fill="{colors["text_primary"]}">{title}</text>'
        f'<line x1="{x}" y1="{y + 8}" x2="{x + w}" y2="{y + 8}" '
        f'stroke="{colors["divider"]}" stroke-width="1" />'
    )


def build_svg(theme_name, avatar_path, stats):
    """
    stats: dict with keys
      repos, contributed, stars, commits, followers, loc, loc_add, loc_del
    """
    colors = THEMES[theme_name]
    avatar_uri = _load_avatar_data_uri(avatar_path)

    right_x = SIDEBAR_W + 40
    content_w = WIDTH - right_x - 30

    avatar_size = 150
    avatar_cx = SIDEBAR_W / 2
    avatar_cy = 130

    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    # Drop shadow filter
    svg_parts.append(
        f'<defs>'
        f'<filter id="winshadow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="8" stdDeviation="18" flood-opacity="{colors["shadow_opacity"]}"/>'
        f'</filter>'
        f'<clipPath id="winclip"><rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="14" ry="14"/></clipPath>'
        f'</defs>'
    )

    # Full background (transparent outside window, so it composites onto page)
    svg_parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="none"/>')

    # Window with shadow
    svg_parts.append(
        f'<g filter="url(#winshadow)">'
        f'<rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="14" ry="14" '
        f'fill="{colors["window_bg"]}" stroke="{colors["window_border"]}" stroke-width="1"/>'
        f'</g>'
    )

    # Everything below is clipped to window rounded corners
    svg_parts.append(f'<g clip-path="url(#winclip)">')

    # Title bar
    svg_parts.append(
        f'<rect x="0" y="0" width="{WIDTH}" height="40" fill="{colors["titlebar_bg"]}"/>'
        f'<circle cx="24" cy="20" r="6.5" fill="{colors["traffic_red"]}"/>'
        f'<circle cx="46" cy="20" r="6.5" fill="{colors["traffic_yellow"]}"/>'
        f'<circle cx="68" cy="20" r="6.5" fill="{colors["traffic_green"]}"/>'
        f'<text x="{WIDTH/2}" y="25" font-family="{FONT}" font-size="13" font-weight="600" '
        f'fill="{colors["text_primary"]}" text-anchor="middle">About Sanjiv</text>'
    )

    # Menu row
    svg_parts.append(
        f'<rect x="0" y="40" width="{WIDTH}" height="30" fill="{colors["menu_bg"]}"/>'
        f'<text x="20" y="60" font-family="{FONT}" font-size="13" fill="{colors["text_secondary"]}">'
        f'\uF8FF&#160;&#160;&#160;File&#160;&#160;&#160;Edit&#160;&#160;&#160;View&#160;&#160;&#160;Special</text>'
        f'<line x1="0" y1="70" x2="{WIDTH}" y2="70" stroke="{colors["divider"]}" stroke-width="1"/>'
    )

    # Sidebar divider
    svg_parts.append(
        f'<line x1="{SIDEBAR_W}" y1="70" x2="{SIDEBAR_W}" y2="{HEIGHT}" '
        f'stroke="{colors["divider"]}" stroke-width="1"/>'
    )

    # Avatar
    if avatar_uri:
        svg_parts.append(
            f'<clipPath id="avatarclip"><circle cx="{avatar_cx}" cy="{avatar_cy + 70}" r="{avatar_size/2}"/></clipPath>'
            f'<image href="{avatar_uri}" x="{avatar_cx - avatar_size/2}" y="{avatar_cy + 70 - avatar_size/2}" '
            f'width="{avatar_size}" height="{avatar_size}" clip-path="url(#avatarclip)" '
            f'preserveAspectRatio="xMidYMid slice"/>'
            f'<circle cx="{avatar_cx}" cy="{avatar_cy + 70}" r="{avatar_size/2}" fill="none" '
            f'stroke="{colors["divider"]}" stroke-width="2"/>'
        )
    else:
        svg_parts.append(
            f'<circle cx="{avatar_cx}" cy="{avatar_cy + 70}" r="{avatar_size/2}" '
            f'fill="{colors["chip_bg"]}" stroke="{colors["divider"]}" stroke-width="2"/>'
        )

    # Chip below avatar
    chip_y = avatar_cy + 70 + avatar_size / 2 + 30
    svg_parts.append(
        f'<rect x="{avatar_cx - 85}" y="{chip_y}" width="170" height="46" rx="8" '
        f'fill="{colors["chip_bg"]}" stroke="{colors["chip_border"]}" stroke-width="1"/>'
        f'<text x="{avatar_cx}" y="{chip_y + 19}" font-family="{FONT}" font-size="12" font-weight="700" '
        f'text-anchor="middle" fill="{colors["text_primary"]}">\u2318 SANJIV</text>'
        f'<text x="{avatar_cx}" y="{chip_y + 36}" font-family="{FONT}" font-size="11" '
        f'text-anchor="middle" fill="{colors["text_secondary"]}">OS 5.0</text>'
    )

    svg_parts.append(
        f'<text x="{avatar_cx}" y="{chip_y + 66}" font-family="{FONT}" font-size="10" '
        f'text-anchor="middle" fill="{colors["text_label"]}">booted from Cupertino</text>'
    )

    # Right panel content
    y = 105
    svg_parts.append(_section_header(right_x, y, content_w, "System Report", colors))
    y += 26
    svg_parts.append(_text_line(right_x, y, "Model Name:", "Sanjiv Anand", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "Model Identifier:", "RoboticsEngineer,1", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "Chip:", "AI-Native Full-Stack Dev", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "Memory:", "iOS \u00b7 Robotics \u00b7 AI/ML", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "Serial Number:", "SRJV-2018-XXXXXXX", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "System Version:", "SanjivOS 5.0", colors)); y += 32

    svg_parts.append(_section_header(right_x, y, content_w, "Built-In", colors))
    y += 26
    svg_parts.append(_text_line(right_x, y, "Languages:", "Swift, Python, Kotlin, JS, C++", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "AI Tools:", "Claude, GPT, LangChain", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "Hardware:", "Arduino, Raspberry Pi, ESP32", colors)); y += 20
    svg_parts.append(_text_line(right_x, y, "Currently:", "Gesture-Controlled Robotic Arm", colors)); y += 32

    svg_parts.append(_section_header(right_x, y, content_w, "GitHub Stats (live)", colors))
    y += 26
    repos_val = f'{stats.get("repos", "\u2014")} {{Contributed: {stats.get("contributed", "\u2014")}}} \u00b7 Stars: {stats.get("stars", "\u2014")}'
    svg_parts.append(_text_line(right_x, y, "Repos:", repos_val, colors)); y += 20
    commits_val = f'{stats.get("commits", "\u2014")} \u00b7 Followers: {stats.get("followers", "\u2014")}'
    svg_parts.append(_text_line(right_x, y, "Commits:", commits_val, colors)); y += 20
    loc_val = f'{stats.get("loc", "\u2014")} ( +{stats.get("loc_add", "\u2014")}, -{stats.get("loc_del", "\u2014")} )'
    svg_parts.append(_text_line(right_x, y, "Lines of Code:", loc_val, colors)); y += 20

    svg_parts.append(f'</g>')  # end clip group

    svg_parts.append('</svg>')
    return "".join(svg_parts)


if __name__ == "__main__":
    # Quick manual test
    demo_stats = {
        "repos": 12, "contributed": 5, "stars": 34, "commits": 512,
        "followers": 28, "loc": "48,200", "loc_add": "40,100", "loc_del": "8,100",
    }
    for theme in ("dark", "light"):
        svg = build_svg(theme, "assets/avatar.png", demo_stats)
        out = f"assets/{theme}_mode.svg"
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", out)
