#!/usr/bin/env python3
"""
DemoPPT 自动配色系统
根据用户输入的一个主题色，自动生成专业PPT配色方案
"""

import re
import colorsys


def hex_to_rgb(hex_color: str) -> tuple:
    """HEX颜色转RGB元组"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """RGB元组转HEX字符串"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def rgb_to_hsl(rgb: tuple) -> tuple:
    """RGB转HSL (H: 0-360, S: 0-100, L: 0-100)"""
    r, g, b = rgb[0]/255, rgb[1]/255, rgb[2]/255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    """HSL转RGB (H: 0-360, S: 0-100, L: 0-100)"""
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return (int(r*255), int(g*255), int(b*255))


def generate_palette(theme_color: str, palette_type: str = "auto") -> dict:
    """
    根据主题色生成完整配色方案
    
    Args:
        theme_color: 主题色HEX值，如 '#6366f1' 或 '6366f1'
        palette_type: 配色方案类型
            - "auto": 自动分析颜色特征选择最佳配色方案
            - "complementary": 互补色方案
            - "analogous": 类似色方案  
            - "triadic": 三角色方案
            - "split": 分裂互补色方案
    
    Returns:
        dict: 包含完整配色方案的字典
    """
    theme_color = theme_color.lstrip('#')
    if not re.match(r'^[0-9A-Fa-f]{6}$', theme_color):
        raise ValueError(f"无效的颜色值: #{theme_color}")
    
    rgb = hex_to_rgb(theme_color)
    h, s, l = rgb_to_hsl(rgb)
    
    # 如果用户指定了palette_type就用它，否则根据色相自动选择
    if palette_type == "auto":
        if l > 80:  # 高亮度（浅色）
            palette_type = "light"
        elif l < 25:  # 低亮度（深色）
            palette_type = "dark"
        elif s > 70:  # 高饱和度
            palette_type = "vibrant"
        else:
            palette_type = "muted"
    
    if palette_type == "complementary":
        return _complementary_scheme(h, s, l, theme_color)
    elif palette_type == "analogous":
        return _analogous_scheme(h, s, l, theme_color)
    elif palette_type == "triadic":
        return _triadic_scheme(h, s, l, theme_color)
    elif palette_type == "split":
        return _split_complementary_scheme(h, s, l, theme_color)
    elif palette_type == "light":
        return _light_scheme(h, s, l, theme_color)
    elif palette_type == "dark":
        return _dark_scheme(h, s, l, theme_color)
    elif palette_type == "vibrant":
        return _vibrant_scheme(h, s, l, theme_color)
    elif palette_type == "muted":
        return _muted_scheme(h, s, l, theme_color)
    else:
        return _auto_scheme(h, s, l, theme_color)


def _auto_scheme(h, s, l, theme_color):
    """自动分析颜色特征选择最佳方案"""
    if s > 60 and l > 30 and l < 70:
        return _vibrant_scheme(h, s, l, theme_color)
    elif l > 75:
        return _light_scheme(h, s, l, theme_color)
    elif l < 30:
        return _dark_scheme(h, s, l, theme_color)
    else:
        return _muted_scheme(h, s, l, theme_color)


def _complementary_scheme(h, s, l, theme_color):
    """互补色方案 - 适合商务专业风格"""
    comp_h = (h + 180) % 360
    
    # 主色系（主题色）
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    primary_light = rgb_to_hex(hsl_to_rgb(h, max(s-15, 10), min(l+20, 92)))
    primary_dark = rgb_to_hex(hsl_to_rgb(h, min(s+10, 100), max(l-20, 15)))
    
    # 互补色
    comp = rgb_to_hex(hsl_to_rgb(comp_h, s, l))
    comp_light = rgb_to_hex(hsl_to_rgb(comp_h, max(s-20, 10), min(l+25, 90)))
    
    return {
        "theme_color": primary,
        "palette_type": "complementary",
        "colors": {
            "primary": primary,         # 主色
            "primary_light": primary_light,  # 主色浅
            "primary_dark": primary_dark,   # 主色深
            "accent": comp,             # 强调色（互补）
            "accent_light": comp_light, # 强调色浅
            "background": "#ffffff",    # 背景色
            "surface": "#f8fafc",       # 卡片/表面色
            "text_primary": "#1e293b",  # 主文字
            "text_secondary": "#64748b", # 次文字
            "border": "#e2e8f0",        # 边框色
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(comp),
        },
        "description": "互补色方案 - 专业商务风格，色彩对比鲜明"
    }


def _analogous_scheme(h, s, l, theme_color):
    """类似色方案 - 柔和和谐"""
    h1 = (h - 30) % 360
    h2 = (h + 30) % 360
    
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    analog1 = rgb_to_hex(hsl_to_rgb(h1, s, l))
    analog2 = rgb_to_hex(hsl_to_rgb(h2, s, l))
    
    return {
        "theme_color": primary,
        "palette_type": "analogous",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(s-20, 10), min(l+25, 92))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(s+10, 100), max(l-20, 15))),
            "accent": analog1,
            "accent_light": analog2,
            "background": "#ffffff",
            "surface": "#f1f5f9",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(analog1),
        },
        "description": "类似色方案 - 柔和和谐，适合教育培训"
    }


def _triadic_scheme(h, s, l, theme_color):
    """三角色方案 - 活力充沛"""
    h1 = (h + 120) % 360
    h2 = (h + 240) % 360
    
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    
    return {
        "theme_color": primary,
        "palette_type": "triadic",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(s-15, 10), min(l+20, 92))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(s+10, 100), max(l-20, 15))),
            "accent": rgb_to_hex(hsl_to_rgb(h1, s, l)),
            "accent_light": rgb_to_hex(hsl_to_rgb(h2, s, l)),
            "background": "#ffffff",
            "surface": "#f8fafc",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(hsl_to_rgb(h1, s, l)),
        },
        "description": "三角色方案 - 活力充沛，适合创意展示"
    }


def _split_complementary_scheme(h, s, l, theme_color):
    """分裂互补色方案 - 专业有层次"""
    h1 = (h + 150) % 360
    h2 = (h + 210) % 360
    
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    
    return {
        "theme_color": primary,
        "palette_type": "split_complementary",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(s-20, 10), min(l+25, 92))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(s+10, 100), max(l-20, 15))),
            "accent": rgb_to_hex(hsl_to_rgb(h1, s, l)),
            "accent_light": rgb_to_hex(hsl_to_rgb(h2, s, l)),
            "background": "#ffffff",
            "surface": "#f8fafc",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(hsl_to_rgb(h1, s, l)),
        },
        "description": "分裂互补色方案 - 专业有层次，适合科技互联网"
    }


def _light_scheme(h, s, l, theme_color):
    """浅色主题方案"""
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    
    return {
        "theme_color": primary,
        "palette_type": "light",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(s-30, 10), min(l+10, 95))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(s+20, 100), max(l-15, 40))),
            "accent": rgb_to_hex(hsl_to_rgb((h + 180) % 360, min(s, 60), 50)),
            "accent_light": rgb_to_hex(hsl_to_rgb((h + 180) % 360, max(s-20, 10), 70)),
            "background": "#ffffff",
            "surface": "#f1f5f9",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(hsl_to_rgb((h + 180) % 360, min(s, 60), 50)),
        },
        "description": "浅色主题方案 - 清新明亮，适合演示展示"
    }


def _dark_scheme(h, s, l, theme_color):
    """深色主题方案"""
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    
    return {
        "theme_type": "dark",
        "theme_color": primary,
        "palette_type": "dark",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(s-20, 10), min(l+30, 85))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(s+10, 100), max(l-20, 10))),
            "accent": rgb_to_hex(hsl_to_rgb((h + 30) % 360, min(s, 80), min(l+20, 70))),
            "accent_light": rgb_to_hex(hsl_to_rgb((h + 60) % 360, min(s, 70), min(l+30, 75))),
            "background": "#0f172a",
            "surface": "#1e293b",
            "text_primary": "#f1f5f9",
            "text_secondary": "#94a3b8",
            "border": "#334155",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(hsl_to_rgb((h + 30) % 360, min(s, 80), min(l+20, 70))),
        },
        "description": "深色主题方案 - 沉稳大气，适合科技演示"
    }


def _vibrant_scheme(h, s, l, theme_color):
    """高饱和度活力方案"""
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    
    return {
        "theme_color": primary,
        "palette_type": "vibrant",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(s-25, 30), min(l+15, 88))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(s+5, 100), max(l-25, 25))),
            "accent": rgb_to_hex(hsl_to_rgb((h + 120) % 360, s, l)),
            "accent_light": rgb_to_hex(hsl_to_rgb((h + 240) % 360, s, l)),
            "background": "#ffffff",
            "surface": "#f8fafc",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": rgb_to_hex(hsl_to_rgb((h + 120) % 360, s, l)),
        },
        "description": "高饱和度活力方案 - 色彩强烈，适合营销推广"
    }


def _muted_scheme(h, s, l, theme_color):
    """低饱和度雅致方案"""
    muted_s = max(s * 0.6, 20)
    primary = rgb_to_hex(hex_to_rgb(theme_color))
    
    return {
        "theme_color": primary,
        "palette_type": "muted",
        "colors": {
            "primary": primary,
            "primary_light": rgb_to_hex(hsl_to_rgb(h, max(muted_s-20, 10), min(l+25, 90))),
            "primary_dark": rgb_to_hex(hsl_to_rgb(h, min(muted_s+15, 50), max(l-20, 25))),
            "accent": rgb_to_hex(hsl_to_rgb((h + 180) % 360, muted_s, l)),
            "accent_light": rgb_to_hex(hsl_to_rgb((h + 180) % 360, max(muted_s-15, 10), min(l+20, 85))),
            "background": "#ffffff",
            "surface": "#f8fafc",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {
            "primary": hex_to_rgb(primary),
            "accent": hex_to_rgb(hsl_to_rgb((h + 180) % 360, muted_s, l)),
        },
        "description": "低饱和度雅致方案 - 沉稳优雅，适合商务洽谈"
    }


# 预设的专业配色方案（供快速选择）
PRESET_PALETTES = {
    "商务蓝": {
        "theme_color": "#2563eb",
        "colors": {
            "primary": "#2563eb",
            "primary_light": "#60a5fa",
            "primary_dark": "#1d4ed8",
            "accent": "#f59e0b",
            "accent_light": "#fbbf24",
            "background": "#ffffff",
            "surface": "#f1f5f9",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {"primary": (37, 99, 235), "accent": (245, 158, 11)},
    },
    "科技紫": {
        "theme_color": "#7c3aed",
        "colors": {
            "primary": "#7c3aed",
            "primary_light": "#a78bfa",
            "primary_dark": "#6d28d9",
            "accent": "#06b6d4",
            "accent_light": "#22d3ee",
            "background": "#ffffff",
            "surface": "#f5f3ff",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {"primary": (124, 58, 237), "accent": (6, 182, 212)},
    },
    "活力橙": {
        "theme_color": "#f97316",
        "colors": {
            "primary": "#f97316",
            "primary_light": "#fb923c",
            "primary_dark": "#ea580c",
            "accent": "#0ea5e9",
            "accent_light": "#38bdf8",
            "background": "#ffffff",
            "surface": "#fff7ed",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {"primary": (249, 115, 22), "accent": (14, 165, 233)},
    },
    "清新绿": {
        "theme_color": "#10b981",
        "colors": {
            "primary": "#10b981",
            "primary_light": "#34d399",
            "primary_dark": "#059669",
            "accent": "#f59e0b",
            "accent_light": "#fbbf24",
            "background": "#ffffff",
            "surface": "#ecfdf5",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {"primary": (16, 185, 129), "accent": (245, 158, 11)},
    },
    "玫瑰红": {
        "theme_color": "#f43f5e",
        "colors": {
            "primary": "#f43f5e",
            "primary_light": "#fb7185",
            "primary_dark": "#e11d48",
            "accent": "#8b5cf6",
            "accent_light": "#a78bfa",
            "background": "#ffffff",
            "surface": "#fff1f2",
            "text_primary": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
        },
        "rgb": {"primary": (244, 63, 94), "accent": (139, 92, 246)},
    },
    "深空蓝": {
        "theme_color": "#1e3a8a",
        "colors": {
            "primary": "#1e3a8a",
            "primary_light": "#3b82f6",
            "primary_dark": "#1e40af",
            "accent": "#06b6d4",
            "accent_light": "#22d3ee",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text_primary": "#f1f5f9",
            "text_secondary": "#94a3b8",
            "border": "#334155",
        },
        "rgb": {"primary": (30, 58, 138), "accent": (6, 182, 212)},
        "theme_type": "dark",
    },
}


def get_preset_palette(name: str) -> dict:
    """获取预设配色方案"""
    return PRESET_PALETTES.get(name)


def list_preset_palettes() -> list:
    """列出所有预设配色方案"""
    return [
        {
            "name": name,
            "theme_color": data["theme_color"],
            "description": data.get("description", ""),
            "theme_type": data.get("theme_type", "light"),
        }
        for name, data in PRESET_PALETTES.items()
    ]
