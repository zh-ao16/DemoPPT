#!/usr/bin/env python3
"""生成20个模板的SVG缩略图"""
import os

# 20个模板的配置: (id, name, gradient_start, gradient_end, text_color, accent_color)
TEMPLATES = [
    ("tech", "科技风", "#1a1a4e", "#00d4ff", "#ffffff", "#00d4ff"),
    ("business", "商务蓝", "#2c5282", "#ed8936", "#ffffff", "#ed8936"),
    ("enterprise", "企业蓝", "#1e3a5f", "#3182ce", "#ffffff", "#3182ce"),
    ("navy_gold", "藏金商务", "#1a365d", "#d69e2e", "#ffffff", "#d69e2e"),
    ("simple", "简约风", "#f7fafc", "#e2e8f0", "#2d3748", "#667eea"),
    ("minimal", "极简白", "#ffffff", "#edf2f7", "#2d3748", "#667eea"),
    ("gray_elegant", "灰雅风", "#2d3748", "#718096", "#ffffff", "#718096"),
    ("academic", "学术风", "#1a365d", "#2c5282", "#ffffff", "#63b3ed"),
    ("cyber", "赛博朋克", "#0f0f23", "#ff00ff", "#ffffff", "#ff00ff"),
    ("future", "未来科技", "#1a0533", "#7c3aed", "#ffffff", "#7c3aed"),
    ("gradient", "渐变风", "#ff6b6b", "#4ecdc4", "#ffffff", "#ffffff"),
    ("nature", "商务绿", "#276749", "#68d391", "#ffffff", "#68d391"),
    ("ocean", "海洋蓝", "#0077b6", "#00b4d8", "#ffffff", "#00b4d8"),
    ("elegant", "商务紫", "#553c9a", "#9f7aea", "#ffffff", "#9f7aea"),
    ("royal", "皇家紫", "#4c1d95", "#8b5cf6", "#ffffff", "#8b5cf6"),
    ("festive", "商务红", "#c53030", "#fc8181", "#ffffff", "#fc8181"),
    ("classic_blue", "经典蓝", "#2b6cb0", "#63b3ed", "#ffffff", "#63b3ed"),
    ("chinese", "中国风", "#1a202c", "#718096", "#ffffff", "#d69e2e"),
    ("ink_wash", "水墨风", "#2d3748", "#a0aec0", "#ffffff", "#718096"),
    ("red_gold", "中国红金", "#742a2a", "#d69e2e", "#ffffff", "#d69e2e"),
]

def make_svg(tid, name, g1, g2, txt, accent):
    """生成单个模板的SVG缩略图"""
    # 根据渐变决定是否加深用于标题栏
    dark_g1 = g1 if g1.startswith("#") else g1
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 135" width="240" height="135">
  <defs>
    <linearGradient id="bg{tid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{g1}"/>
      <stop offset="100%" style="stop-color:{g2}"/>
    </linearGradient>
  </defs>
  <!-- 背景 -->
  <rect width="240" height="135" fill="url(#bg{tid})" rx="6"/>
  <!-- 标题栏 -->
  <rect x="0" y="0" width="240" height="40" fill="rgba(0,0,0,0.25)" rx="6"/>
  <rect x="0" y="34" width="240" height="6" fill="rgba(0,0,0,0.25)"/>
  <!-- 标题文字 -->
  <text x="16" y="26" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="{txt}">{name}</text>
  <!-- 内容区域 - 模拟PPT布局 -->
  <!-- 左侧标题 -->
  <rect x="12" y="50" width="60" height="8" fill="rgba(255,255,255,0.7)" rx="2"/>
  <!-- 内容行 -->
  <rect x="12" y="66" width="140" height="5" fill="rgba(255,255,255,0.35)" rx="1"/>
  <rect x="12" y="76" width="120" height="5" fill="rgba(255,255,255,0.35)" rx="1"/>
  <rect x="12" y="86" width="100" height="5" fill="rgba(255,255,255,0.35)" rx="1"/>
  <rect x="12" y="96" width="130" height="5" fill="rgba(255,255,255,0.35)" rx="1"/>
  <!-- 右侧装饰块 -->
  <rect x="165" y="50" width="65" height="55" fill="rgba(255,255,255,0.12)" rx="4"/>
  <rect x="173" y="58" width="49" height="4" fill="rgba(255,255,255,0.3)" rx="1"/>
  <rect x="173" y="68" width="35" height="4" fill="rgba(255,255,255,0.2)" rx="1"/>
  <rect x="173" y="78" width="42" height="4" fill="rgba(255,255,255,0.2)" rx="1"/>
  <rect x="173" y="88" width="28" height="4" fill="rgba(255,255,255,0.2)" rx="1"/>
  <!-- 底部装饰线 -->
  <rect x="12" y="115" width="216" height="2" fill="{accent}" opacity="0.5" rx="1"/>
</svg>'''
    return svg

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "template-previews")
    os.makedirs(out_dir, exist_ok=True)
    
    for tid, name, g1, g2, txt, accent in TEMPLATES:
        svg = make_svg(tid, name, g1, g2, txt, accent)
        path = os.path.join(out_dir, f"{tid}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"✅ {tid}.svg - {name}")
    
    print(f"\n生成完成: {len(TEMPLATES)} 个缩略图 → {out_dir}")

if __name__ == "__main__":
    main()
