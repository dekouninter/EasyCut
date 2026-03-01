# -*- coding: utf-8 -*-
"""
EasyCut Icon Renderer v2.0
High-quality Feather SVG → PIL → PhotoImage rendering

Renders Feather SVGs as crisp, colored, anti-aliased icons using Pillow.
Supports:
- Any Feather icon by name (287 icons)
- Custom colors (hex)
- Custom sizes (12–64px)
- Canvas-aware caching
- Automatic recoloring on theme change

Author: Deko Costa
"""

import re
import math
from pathlib import Path
from typing import Dict, Tuple, Optional
from functools import lru_cache

try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ═══════════════════════════════════════════════════════════════════
#  FEATHER SVG PARSER (lightweight — no external deps)
# ═══════════════════════════════════════════════════════════════════

# Regex patterns for SVG path data
_RE_LINE = re.compile(r'<line\s+x1="([^"]+)"\s+y1="([^"]+)"\s+x2="([^"]+)"\s+y2="([^"]+)"')
_RE_RECT = re.compile(r'<rect\s+([^/]*?)/?>')
_RE_CIRCLE = re.compile(r'<circle\s+cx="([^"]+)"\s+cy="([^"]+)"\s+r="([^"]+)"')
_RE_POLYLINE = re.compile(r'<polyline\s+points="([^"]+)"')
_RE_POLYGON = re.compile(r'<polygon\s+points="([^"]+)"')
_RE_PATH = re.compile(r'<path\s+d="([^"]+)"')
_RE_ATTR = re.compile(r'(\w+)="([^"]+)"')


def _parse_points(pts_str: str):
    """Parse SVG points string → list of (x,y) tuples"""
    pts = pts_str.strip().replace(',', ' ').split()
    coords = []
    for i in range(0, len(pts) - 1, 2):
        coords.append((float(pts[i]), float(pts[i+1])))
    return coords


def _parse_path_d(d: str):
    """Parse SVG path 'd' attribute into drawable segments.
    Supports: M, L, H, V, C, S, Q, T, A, Z (absolute only for now)
    Returns list of ('line', [(x,y),...]) or ('arc', params) segments.
    """
    segments = []
    current = []
    cx, cy = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    
    # Tokenize
    tokens = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)
    
    i = 0
    cmd = ''
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue
        
        if cmd in ('M', 'm'):
            x, y = float(tokens[i]), float(tokens[i+1])
            if cmd == 'm':
                x += cx; y += cy
            if current:
                segments.append(('line', list(current)))
                current = []
            cx, cy = x, y
            start_x, start_y = x, y
            current.append((x, y))
            cmd = 'L' if cmd == 'M' else 'l'  # subsequent coords are lines
            i += 2
        
        elif cmd in ('L', 'l'):
            x, y = float(tokens[i]), float(tokens[i+1])
            if cmd == 'l':
                x += cx; y += cy
            cx, cy = x, y
            current.append((x, y))
            i += 2
        
        elif cmd in ('H', 'h'):
            x = float(tokens[i])
            if cmd == 'h':
                x += cx
            cx = x
            current.append((cx, cy))
            i += 1
        
        elif cmd in ('V', 'v'):
            y = float(tokens[i])
            if cmd == 'v':
                y += cy
            cy = y
            current.append((cx, cy))
            i += 1
        
        elif cmd in ('C', 'c'):
            # Cubic bezier — approximate with line segments
            x1, y1 = float(tokens[i]), float(tokens[i+1])
            x2, y2 = float(tokens[i+2]), float(tokens[i+3])
            x3, y3 = float(tokens[i+4]), float(tokens[i+5])
            if cmd == 'c':
                x1 += cx; y1 += cy
                x2 += cx; y2 += cy
                x3 += cx; y3 += cy
            # Approximate cubic bezier
            for t_val in [j/12.0 for j in range(1, 13)]:
                u = 1 - t_val
                px = u*u*u*cx + 3*u*u*t_val*x1 + 3*u*t_val*t_val*x2 + t_val*t_val*t_val*x3
                py = u*u*u*cy + 3*u*u*t_val*y1 + 3*u*t_val*t_val*y2 + t_val*t_val*t_val*y3
                current.append((px, py))
            cx, cy = x3, y3
            i += 6
        
        elif cmd in ('S', 's'):
            x2, y2 = float(tokens[i]), float(tokens[i+1])
            x3, y3 = float(tokens[i+2]), float(tokens[i+3])
            if cmd == 's':
                x2 += cx; y2 += cy
                x3 += cx; y3 += cy
            # Reflect: x1 = 2*cx - prev_x2 (simplified — use cx)
            x1, y1 = cx, cy
            for t_val in [j/12.0 for j in range(1, 13)]:
                u = 1 - t_val
                px = u*u*u*cx + 3*u*u*t_val*x1 + 3*u*t_val*t_val*x2 + t_val*t_val*t_val*x3
                py = u*u*u*cy + 3*u*u*t_val*y1 + 3*u*t_val*t_val*y2 + t_val*t_val*t_val*y3
                current.append((px, py))
            cx, cy = x3, y3
            i += 4
        
        elif cmd in ('Q', 'q'):
            x1, y1 = float(tokens[i]), float(tokens[i+1])
            x2, y2 = float(tokens[i+2]), float(tokens[i+3])
            if cmd == 'q':
                x1 += cx; y1 += cy
                x2 += cx; y2 += cy
            for t_val in [j/10.0 for j in range(1, 11)]:
                u = 1 - t_val
                px = u*u*cx + 2*u*t_val*x1 + t_val*t_val*x2
                py = u*u*cy + 2*u*t_val*y1 + t_val*t_val*y2
                current.append((px, py))
            cx, cy = x2, y2
            i += 4
        
        elif cmd in ('A', 'a'):
            # Arc — simplified: just draw line to endpoint
            # Full SVG arc is complex; most Feather icons don't use complex arcs
            rx = float(tokens[i])
            ry = float(tokens[i+1])
            rotation = float(tokens[i+2])
            large_arc = int(float(tokens[i+3]))
            sweep = int(float(tokens[i+4]))
            ex, ey = float(tokens[i+5]), float(tokens[i+6])
            if cmd == 'a':
                ex += cx; ey += cy
            
            # Approximate arc with bezier-like segments
            if rx > 0 and ry > 0:
                # Calculate center and angles for proper arc rendering
                dx2 = (cx - ex) / 2.0
                dy2 = (cy - ey) / 2.0
                cos_r = math.cos(math.radians(rotation))
                sin_r = math.sin(math.radians(rotation))
                x1p = cos_r * dx2 + sin_r * dy2
                y1p = -sin_r * dx2 + cos_r * dy2
                
                # Generate arc points  
                mid_x = (cx + ex) / 2
                mid_y = (cy + ey) / 2
                steps = 12
                for s in range(1, steps + 1):
                    t_val = s / steps
                    px = cx + (ex - cx) * t_val
                    py = cy + (ey - cy) * t_val
                    # Add curvature
                    bulge = math.sin(t_val * math.pi) * min(rx, ry) * 0.5
                    if not sweep:
                        bulge = -bulge
                    # Perpendicular direction
                    dx = ex - cx
                    dy = ey - cy
                    length = math.sqrt(dx*dx + dy*dy) or 1
                    nx = -dy / length
                    ny = dx / length
                    px += nx * bulge
                    py += ny * bulge
                    current.append((px, py))
            
            cx, cy = ex, ey
            i += 7
        
        elif cmd in ('Z', 'z'):
            current.append((start_x, start_y))
            cx, cy = start_x, start_y
            if current:
                segments.append(('line', list(current)))
                current = []
            i += 1
        else:
            i += 1
    
    if current:
        segments.append(('line', list(current)))
    
    return segments


# ═══════════════════════════════════════════════════════════════════
#  RENDERER — Feather SVG → PIL Image → PhotoImage
# ═══════════════════════════════════════════════════════════════════

_FEATHER_DIR = Path(__file__).parent.parent / "assets" / "feather-main" / "icons"
_CACHE: Dict[str, 'ImageTk.PhotoImage'] = {}


def _hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
    """Convert hex color to RGBA tuple"""
    h = hex_color.lstrip('#')
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    elif len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    return (200, 200, 200, 255)


def render_feather_icon(name: str, size: int = 20, color: str = "#ECEEF3",
                        stroke_width: float = 2.0) -> Optional['ImageTk.PhotoImage']:
    """Render a Feather SVG icon as a colored PIL PhotoImage.
    
    Args:
        name: Feather icon name (e.g. "download", "settings")
        size: Output size in pixels (square)
        color: Hex color for the icon strokes
        stroke_width: Width of strokes (default 2.0, Feather standard)
    
    Returns:
        ImageTk.PhotoImage or None on failure
    """
    if not HAS_PIL:
        return None
    
    cache_key = f"{name}_{size}_{color}_{stroke_width}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    
    svg_path = _FEATHER_DIR / f"{name}.svg"
    if not svg_path.exists():
        return None
    
    try:
        svg_content = svg_path.read_text(encoding='utf-8')
    except Exception:
        return None
    
    # Feather icons are 24×24 viewBox
    scale = size / 24.0
    # Render at 2x for anti-aliasing then downscale
    render_size = size * 2
    render_scale = render_size / 24.0
    sw = stroke_width * render_scale
    
    img = Image.new('RGBA', (render_size, render_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rgba = _hex_to_rgba(color)
    
    def scaled(x, y):
        return x * render_scale, y * render_scale
    
    # Parse and draw lines
    for m in _RE_LINE.finditer(svg_content):
        x1, y1 = float(m.group(1)), float(m.group(2))
        x2, y2 = float(m.group(3)), float(m.group(4))
        sx1, sy1 = scaled(x1, y1)
        sx2, sy2 = scaled(x2, y2)
        draw.line([(sx1, sy1), (sx2, sy2)], fill=rgba, width=max(1, int(sw)))
    
    # Parse and draw circles
    for m in _RE_CIRCLE.finditer(svg_content):
        cx_val, cy_val, r = float(m.group(1)), float(m.group(2)), float(m.group(3))
        scx, scy = scaled(cx_val, cy_val)
        sr = r * render_scale
        bbox = [scx - sr, scy - sr, scx + sr, scy + sr]
        draw.ellipse(bbox, outline=rgba, width=max(1, int(sw)))
    
    # Parse and draw rectangles
    for m in _RE_RECT.finditer(svg_content):
        attrs_str = m.group(1)
        attrs = dict(_RE_ATTR.findall(attrs_str))
        x = float(attrs.get('x', '0'))
        y = float(attrs.get('y', '0'))
        w = float(attrs.get('width', '0'))
        h = float(attrs.get('height', '0'))
        rx_val = float(attrs.get('rx', '0'))
        if w > 0 and h > 0:
            sx, sy = scaled(x, y)
            sw2, sh = w * render_scale, h * render_scale
            if rx_val > 0:
                srx = rx_val * render_scale
                draw.rounded_rectangle(
                    [sx, sy, sx + sw2, sy + sh],
                    radius=srx, outline=rgba, width=max(1, int(sw))
                )
            else:
                draw.rectangle(
                    [sx, sy, sx + sw2, sy + sh],
                    outline=rgba, width=max(1, int(sw))
                )
    
    # Parse and draw polylines
    for m in _RE_POLYLINE.finditer(svg_content):
        points = _parse_points(m.group(1))
        if len(points) >= 2:
            scaled_pts = [scaled(px, py) for px, py in points]
            draw.line(scaled_pts, fill=rgba, width=max(1, int(sw)), joint="curve")
    
    # Parse and draw polygons  
    for m in _RE_POLYGON.finditer(svg_content):
        points = _parse_points(m.group(1))
        if len(points) >= 3:
            scaled_pts = [scaled(px, py) for px, py in points]
            draw.polygon(scaled_pts, outline=rgba, width=max(1, int(sw)))
    
    # Parse and draw paths
    for m in _RE_PATH.finditer(svg_content):
        d = m.group(1)
        segments = _parse_path_d(d)
        for seg_type, seg_points in segments:
            if seg_type == 'line' and len(seg_points) >= 2:
                scaled_pts = [scaled(px, py) for px, py in seg_points]
                draw.line(scaled_pts, fill=rgba, width=max(1, int(sw)), joint="curve")
    
    # Downscale with LANCZOS for crisp anti-aliased result
    img = img.resize((size, size), Image.LANCZOS)
    
    photo = ImageTk.PhotoImage(img)
    _CACHE[cache_key] = photo
    return photo


def clear_icon_cache():
    """Clear the icon cache (call on theme change)"""
    _CACHE.clear()


# ═══════════════════════════════════════════════════════════════════
#  GRADIENT IMAGE GENERATOR
# ═══════════════════════════════════════════════════════════════════

def create_gradient_image(width: int, height: int,
                          color1: str, color2: str,
                          direction: str = "horizontal") -> Optional['ImageTk.PhotoImage']:
    """Create a gradient PhotoImage for backgrounds/accent bars.
    
    Args:
        width, height: Image dimensions
        color1, color2: Start/end hex colors
        direction: "horizontal", "vertical", or "diagonal"
    
    Returns:
        ImageTk.PhotoImage
    """
    if not HAS_PIL:
        return None
    
    cache_key = f"grad_{width}_{height}_{color1}_{color2}_{direction}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    
    r1, g1, b1, a1 = _hex_to_rgba(color1)
    r2, g2, b2, a2 = _hex_to_rgba(color2)
    
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            if direction == "horizontal":
                t = x / max(width - 1, 1)
            elif direction == "vertical":
                t = y / max(height - 1, 1)
            else:  # diagonal
                t = (x + y) / max(width + height - 2, 1)
            
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            a = int(a1 + (a2 - a1) * t)
            pixels[x, y] = (r, g, b, a)
    
    photo = ImageTk.PhotoImage(img)
    _CACHE[cache_key] = photo
    return photo


def create_glow_border(width: int, height: int, color: str,
                       glow_size: int = 4, corner_radius: int = 8) -> Optional['ImageTk.PhotoImage']:
    """Create a glowing border effect image.
    
    Args:
        width, height: Frame dimensions
        color: Glow color (hex)
        glow_size: Glow spread in pixels
        corner_radius: Corner radius
    
    Returns:
        ImageTk.PhotoImage with glow effect
    """
    if not HAS_PIL:
        return None
        
    from PIL import ImageFilter
    
    cache_key = f"glow_{width}_{height}_{color}_{glow_size}_{corner_radius}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    
    total_w = width + glow_size * 2
    total_h = height + glow_size * 2
    
    rgba = _hex_to_rgba(color)
    
    # Draw shape
    img = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle(
        [glow_size, glow_size, total_w - glow_size, total_h - glow_size],
        radius=corner_radius,
        outline=rgba,
        width=2
    )
    
    # Apply gaussian blur for glow
    img = img.filter(ImageFilter.GaussianBlur(radius=glow_size))
    
    photo = ImageTk.PhotoImage(img)
    _CACHE[cache_key] = photo
    return photo
