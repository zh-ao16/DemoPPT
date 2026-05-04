"""
DemoPPT 预置行业知识库 + 联网搜索数据模块
- 10个行业的核心指标/框架/数据（离线可用）
- 联网搜索最新行业数据（ DuckDuckGo HTML API，客户Windows/Mac均可访问外网）
"""

import os, json, urllib.request, urllib.parse, re

# ============================================================
# 联网搜索（ DuckDuckGo HTML API，无需API Key，客户环境直接可用）
# ============================================================
def search_web(query: str, num_results: int = 5) -> list:
    """联网搜索，返回标题+摘要+链接"""
    try:
        encoded_q = urllib.parse.quote(query)
        url = f"https://www.bing.com/search?q={encoded_q}&ensearch=0"
        
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        results = []
        # 解析Bing搜索结果
        h2_pattern = re.compile(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a></h2>')
        for match in h2_pattern.finditer(html):
            link, title = match.group(1), re.sub(r'<[^>]+>', '', match.group(2)).strip()
            # 找这个h2后面的snippet
            pos = match.end()
            snippet_match = re.search(r'<p>([^<]+)</p>', html[pos:pos+500])
            snippet = snippet_match.group(1) if snippet_match else ""
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            if title and link.startswith('http'):
                results.append({"title": title[:120], "snippet": snippet[:250], "url": link})
                if len(results) >= num_results:
                    break
        
        return results
    except Exception:
        return []  # 网络失败→静默降级，不影响PPT生成

def search_industry_data(query: str, industry: str = "") -> dict:
    """搜索行业数据，自动选择最优搜索词"""
    # 构建多组搜索词，覆盖行业数据需求
    search_queries = [
        f"{query} 最新数据 2024 2025",
        f"{query} 市场规模 统计 报告",
        f"{query} 行业趋势 洞察 分析",
    ]
    
    all_results = []
    seen = set()
    
    for q in search_queries:
        results = search_web(q, num_results=4)
        for r in results:
            key = r["title"][:50]
            if key not in seen:
                seen.add(key)
                all_results.append(r)
        if len(all_results) >= 8:
            break
    
    return {
        "query": query,
        "industry": industry,
        "results": all_results,
        "has_data": len(all_results) > 0
    }

# ============================================================
# 预置行业知识库（离线可用，有数据有洞察）
# ============================================================
INDUSTRY_KB = {
    "technology": {
        "name": "科技/互联网",
        "metrics": ["市场规模(亿元)", "年增速(%)", "头部玩家市场份额(%)", "研发投入占比(%)", "用户规模(亿)"],
        "data": {
            "全球AI市场": {"2024": 6000, "2025预计": 7500, "2026预计": 9000, "增速": "年复合增长率16%"},
            "中国SaaS市场": {"2024": 1200, "2025预计": 1500, "增速": "年复合增长率25%"},
            "中国云计算市场": {"2024": 5000, "2025预计": 6200, "增速": "年复合增长率24%"},
        },
        "frameworks": ["SWOT分析", "波特五力", "PEST分析", "用户增长漏斗", "RFM模型"],
        "insights": [
            "AI大模型正在重塑各行业工作方式，企业采纳率年增速超40%",
            "中国SaaS市场渗透率仅15%，远低于美国70%，增长空间巨大",
            "头部云厂商（阿里云/华为云/腾讯云）占据75%市场份额",
        ]
    },
    "finance": {
        "name": "金融/投资",
        "metrics": ["市场规模(万亿元)", "年增速(%)", "机构数量", "从业人员(万)", "不良率(%)"],
        "data": {
            "中国资产管理": {"2024": 130, "2025预计": 145, "增速": "年增速12%"},
            "私募股权市场": {"2024": 20, "2025预计": 23, "增速": "年增速15%"},
            "公募基金": {"2024": 28, "2025预计": 33, "增速": "年增速18%"},
        },
        "frameworks": ["DCF估值", "可比公司法", "LBO模型", "风险调整收益", "组合管理理论"],
        "insights": [
            "中国居民金融资产配置中，基金占比从2019年的10%升至2024年的22%",
            "量化投资规模年增速30%，已成为私募量化核心策略",
            "注册制全面实施后，IPO市场机构化率超过85%",
        ]
    },
    "healthcare": {
        "name": "医疗健康",
        "metrics": ["市场规模(万亿元)", "年增速(%)", "医院数量(家)", "研发投入(亿元)", "医保覆盖率(%)"],
        "data": {
            "创新药市场": {"2024": 3000, "2025预计": 3600, "增速": "年增速20%"},
            "医疗器械": {"2024": 9500, "2025预计": 10500, "增速": "年增速10%"},
            "数字医疗": {"2024": 2000, "2025预计": 2600, "增速": "年增速30%"},
        },
        "frameworks": ["DCF估值", "NPV净现值", "真实世界证据RWE", "卫生技术评估HTA", "药物经济学"],
        "insights": [
            "PD-1/PD-L1市场规模超300亿，国产占比已超60%",
            "创新药出海成为主要增长引擎，License-out交易金额年增50%",
            "AI辅助诊断渗透率年增35%，核心集中在影像领域",
        ]
    },
    "education": {
        "name": "教育培训",
        "metrics": ["市场规模(万亿元)", "年增速(%)", "机构数量(万家)", "从业人员(万)", "在线渗透率(%)"],
        "data": {
            "职业教育": {"2024": 1.2, "2025预计": 1.4, "增速": "年增速17%"},
            "素质教育": {"2024": 0.6, "2025预计": 0.75, "增速": "年增速25%"},
            "教育硬件": {"2024": 0.4, "2025预计": 0.5, "增速": "年增速20%"},
        },
        "frameworks": ["用户生命周期价值LTV", "续费率模型", "课程完课率", "师资稳定性", "坪效人效"],
        "insights": [
            "职业教育赛道受政策支持，年增速超20%，考公考编需求爆发",
            "AI教育渗透率年增40%，智能学习硬件成新增长点",
            "成人职业教育复购率（35%）显著高于K12（15%）",
        ]
    },
    "retail": {
        "name": "零售/电商",
        "metrics": ["社零总额(万亿元)", "线上渗透率(%)", "门店数量(万)", "从业人员(万)", "坪效(元/㎡)"],
        "data": {
            "直播电商": {"2024": 4.9, "2025预计": 6.0, "增速": "年增速22%"},
            "即时零售": {"2024": 2.0, "2025预计": 2.8, "增速": "年增速40%"},
            "会员电商": {"2024": 1.5, "2025预计": 1.9, "增速": "年增速27%"},
        },
        "frameworks": ["人货场模型", "GMV拆解", "用户ARPU", "复购率模型", "库存周转"],
        "insights": [
            "直播电商占网购比例突破30%，头部主播马太效应加剧",
            "即时零售（美团闪购/京东到家）成为线下商超数字化主战场",
            "仓储会员店（Costco、山姆）年均增速超30%，单店效率行业最高",
        ]
    },
    "manufacture": {
        "name": "制造业",
        "metrics": ["工业增加值(万亿元)", "年增速(%)", "企业数量(万家)", "智能制造渗透率(%)", "出口额(万亿元)"],
        "data": {
            "新能源汽车": {"2024": 1280, "unit": "万辆", "增速": "同比增35%"},
            "工业机器人": {"2024": 55, "unit": "万台", "增速": "同比增25%"},
            "半导体设备": {"2024": 600, "unit": "亿元", "增速": "同比增30%"},
        },
        "frameworks": ["精益生产", "IE工程", "TPM全面生产维护", "SCOR供应链模型", "产能利用率"],
        "insights": [
            "中国新能源汽车产销量连续9年全球第一，2024年渗透率突破40%",
            "工业机器人密度年增15%，但仍仅为德国/日本的1/3",
            "半导体设备国产化率不足20%，政策驱动下年增速超30%",
        ]
    },
    "energy": {
        "name": "新能源/双碳",
        "metrics": ["装机容量(GW)", "年增速(%)", "投资额(万亿元)", "碳排放强度(gCO2/kWh)", "储能规模(GWh)"],
        "data": {
            "光伏": {"2024": 740, "unit": "GW", "增速": "同比增30%"},
            "储能": {"2024": 200, "unit": "GWh", "增速": "同比增80%"},
            "风电": {"2024": 520, "unit": "GW", "增速": "同比增20%"},
        },
        "frameworks": ["LCOE平准化度电成本", "碳足迹核算", "ESG评级", "绿色溢价", "碳交易机制"],
        "insights": [
            "光伏组件价格年跌30%，LCOE已低于火电",
            "储能成为新能源最后一公里，2024年招标量超100GWh",
            "碳中和目标驱动，绿氢/氢能重卡成为下一个万亿赛道",
        ]
    },
    "media": {
        "name": "传媒/娱乐",
        "metrics": ["市场规模(万亿元)", "年增速(%)", "用户规模(亿)", "付费率(%)", "人均消费(元)"],
        "data": {
            "短视频": {"2024": 15000, "unit": "亿元", "增速": "同比增25%"},
            "长视频": {"2024": 1200, "unit": "亿元", "增速": "同比增12%"},
            "游戏": {"2024": 3100, "unit": "亿元", "增速": "同比增8%"},
        },
        "frameworks": ["DAU/MAU比值", "用户时长", "付费转化率", "内容ROI", "IP生命周期"],
        "insights": [
            "短视频人均日使用时长突破120分钟，超越即时通讯",
            "短剧年增速超200%，成为内容行业最大增量市场",
            "AIGC渗透率年增60%，AI生成图片/视频正在颠覆内容生产流程",
        ]
    },
    "realestate": {
        "name": "房地产",
        "metrics": ["销售面积(亿㎡)", "销售额(万亿元)", "年增速(%)", "土地成交(亿元)", "新开工(亿㎡)"],
        "data": {
            "住宅": {"2024": 10, "unit": "亿㎡", "增速": "同比降8%"},
            "商办": {"2024": 2.5, "unit": "亿㎡", "增速": "同比降12%"},
            "保障房": {"2024": 0.8, "unit": "亿㎡", "增速": "同比增30%"},
        },
        "frameworks": ["IRR内部收益率", "租售比", "土地增值税", "REITs估值", "现金流折现"],
        "insights": [
            "房地产销售面积较高峰期下降35%，行业进入存量博弈时代",
            "代建/物业/租赁成为地产下半场核心利润来源",
            "城中村改造加速，2024年投资规模超万亿",
        ]
    },
    "general": {
        "name": "通用/综合",
        "metrics": ["GDP增速(%)", "CPI涨幅(%)", "城镇新增就业(万)", "居民可支配收入增速(%)", "基尼系数"],
        "data": {
            "中国经济": {"2024": "增速5%", "CPI": "2%", "就业": "1200万"},
        },
        "frameworks": ["PEST分析", "SWOT分析", "波特五力", "平衡计分卡", "OKR管理"],
        "insights": [
            "中国经济增速放缓但结构优化，消费贡献率超65%",
            "数字化转型成为企业共识，IT支出年增速保持12%",
        ]
    }
}

# ============================================================
# 联网搜索（使用 DuckDuckGo 免费API）
# ============================================================
# search_industry_data 已在上方定义

# 行业key兼容映射
_KEY_MAP = {"ecommerce": "retail", "medical": "healthcare"}

def _resolve_industry_key(industry: str) -> str:
    return _KEY_MAP.get(industry, industry)

def get_industry_context(topic: str, industry: str, web_results: list = None) -> str:
    """为PPT生成构建行业知识库上下文（本地库+联网数据）"""
    industry_key = _resolve_industry_key(industry)
    kb = INDUSTRY_KB.get(industry_key, INDUSTRY_KB["general"])
    
    parts = [f"【{kb['name']}行业知识库】"]
    
    # 核心洞察
    if kb.get("insights"):
        parts.append("核心洞察：")
        for insight in kb["insights"][:3]:
            parts.append(f"  • {insight}")
    
    # 市场规模数据
    if kb.get("data"):
        parts.append("\n关键数据：")
        for name, stats in kb["data"].items():
            stat_str = ", ".join([f"{k}={v}" for k, v in stats.items() if k != "unit"])
            unit = stats.get("unit", "")
            parts.append(f"  • {name}：{stat_str} {unit}")
    
    # 联网搜索结果（最新实时数据）
    if web_results:
        parts.append("\n【联网最新数据】")
        for r in web_results[:5]:
            parts.append(f"  • {r['title']}")
            if r.get('snippet'):
                parts.append(f"    {r['snippet'][:100]}")
    
    return "\n".join(parts)

def search_and_get_context(topic: str, industry: str) -> dict:
    """联网搜索并返回上下文（带降级）"""
    # 先获取本地知识库内容
    local_context = get_industry_context(topic, industry)
    
    # 尝试联网
    web_results = search_industry_data(topic, industry).get("results", [])
    
    # 把联网结果也格式化成文本上下文
    web_context = ""
    if web_results:
        parts = ["【联网最新数据】"]
        for r in web_results[:5]:
            parts.append(f"  • {r['title']}")
            if r.get('snippet'):
                parts.append(f"    {r['snippet'][:120]}")
        web_context = "\n".join(parts)
    
    # 完整上下文 = 本地库 + 联网数据
    full_context = local_context
    if web_context:
        full_context = local_context + "\n\n" + web_context
    
    return {
        "local_context": local_context,
        "web_context": web_context,
        "full_context": full_context,
        "web_results": web_results,
        "has_web": len(web_results) > 0,
        "local_kb": INDUSTRY_KB.get(_resolve_industry_key(industry), INDUSTRY_KB.get("general", {}))
    }
