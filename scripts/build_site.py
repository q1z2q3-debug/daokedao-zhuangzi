#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 book/润泽说 道可道之庄子.md 生成 docs/ 静态站（首页、全书页、逐篇页、sitemap、llms.txt）。

用法：python3 scripts/build_site.py
产物：docs/index.html、docs/book.html、docs/chapters/*.html
"""
from pathlib import Path
import html as H
import json
import re

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SRC = ROOT / "book" / "润泽说 道可道之庄子.md"
SITE = "https://q1z2q3-debug.github.io/daokedao-zhuangzi"
SERIES = "润泽说 道可道"
TITLE = "润泽说 道可道之庄子"
VER = "1.33.0"
DOI = "10.5281/zenodo.24217537"

# 篇目：(卷次, 组, 篇名, slug)
P_SLUG = {
    "逍遥游": "xiaoyaoyou", "齐物论": "qiwulun", "养生主": "yangshengzhu",
    "人间世": "renjianshi", "德充符": "dechongfu", "大宗师": "dazongshi",
    "应帝王": "yingdiwang", "骈拇": "pianmu", "马蹄": "mati", "胠箧": "quqie",
    "在宥": "zaiyou", "天地": "tiandi", "天道": "tiandao", "天运": "tianyun",
    "刻意": "keyi", "缮性": "shanxing", "秋水": "qiushui", "至乐": "zhile",
    "达生": "dasheng", "山木": "shanmu", "田子方": "tianzifang", "知北游": "zhibeiyou",
    "庚桑楚": "gengsangchu", "徐无鬼": "xuwugui", "则阳": "zeyang",
    "外物": "waiwu", "寓言": "yuyan", "天下": "tianxia", "庄子立言之法度": "fadu",
}

CSS = """
:root{--paper:#F7F4EE;--paper2:#F1ECE2;--ink:#1B1917;--muted:#6B6152;--line:#DCD3C4;--accent:#8C3A2E}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:16px;line-height:1.9;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(140,58,46,.28)}
a:hover{border-bottom-color:var(--accent)}
.wrap{max-width:900px;margin:0 auto;padding:0 28px}
header.top{border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9;background:rgba(247,244,238,.94)}
header.top .wrap{display:flex;align-items:baseline;justify-content:space-between;gap:14px;padding:14px 0;flex-wrap:wrap}
.brand{font-size:15px;letter-spacing:.12em;border:0;white-space:nowrap}
nav{display:flex;flex-wrap:wrap;column-gap:16px;row-gap:2px;justify-content:flex-end}
nav a{font-size:13px;color:var(--muted);border:0;white-space:nowrap;font-family:"Noto Sans SC",sans-serif;letter-spacing:.04em}
nav a.on,nav a:hover{color:var(--accent)}
main{padding:52px 0 40px}
.eyebrow{font-family:"Noto Sans SC",sans-serif;font-size:12px;letter-spacing:.22em;color:var(--muted)}
h1{font-size:38px;line-height:1.32;font-weight:600;margin:14px 0 8px}
h2{font-size:21px;font-weight:600;margin:48px 0 16px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:17px;font-weight:600;margin:24px 0 8px}
p{margin:0 0 14px}
.lede{font-size:17.5px;color:#3A342C;max-width:730px}
.small{font-size:13.5px;color:var(--muted);font-family:"Noto Sans SC",sans-serif;line-height:1.8}
.list{border-top:1px solid var(--line)}
.row{display:grid;grid-template-columns:56px 1fr 150px;gap:18px;padding:18px 0;border-bottom:1px solid var(--line);align-items:start}
.row .no{font-family:"Noto Sans SC",sans-serif;font-size:12px;color:var(--muted);letter-spacing:.1em;padding-top:6px}
.row h3{margin:0 0 4px;font-size:18px}
.row .go{text-align:right;font-size:13px}
article{border-top:1px solid var(--line);padding-top:26px}
article h3{font-size:18px;letter-spacing:.04em;color:var(--accent)}
article h4{font-size:15.5px;margin:20px 0 6px}
article p{text-align:justify}
blockquote{margin:22px 0;padding:4px 0 4px 18px;border-left:2px solid var(--accent);color:#3A342C}
ul{margin:0 0 14px 18px;padding:0}
.prevnext{display:flex;justify-content:space-between;gap:16px;margin:44px 0 0;padding-top:18px;border-top:1px solid var(--line);font-size:14px}
footer{border-top:1px solid var(--line);padding:30px 0 56px;margin-top:44px}
footer .wrap{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
@media(max-width:720px){
 .brand{font-size:13px;letter-spacing:.06em}nav{column-gap:10px}nav a{font-size:11.5px;letter-spacing:.02em}
 h1{font-size:28px}main{padding-top:34px}.row{grid-template-columns:1fr;gap:4px}.row .no{display:none}.row .go{text-align:left}
 .prevnext{flex-direction:column;gap:6px}
}
"""

NAV = [("/", "首页", "home"), ("/book.html", "全书", "book"), ("/chapters/", "篇目", "chapters"), ("/downloads/", "下载", "downloads")]


def head(title, desc, path, jsonld=None, act="home"):
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))
    nav = "".join(f'<a href="{SITE}{p}" class="{"on" if a == act else ""}">{n}</a>' for p, n, a in NAV)
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SERIES}">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/favicon.svg">
<meta name="author" content="润泽">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{SITE}/"><b>润泽说</b> · 道可道</a>
<nav>{nav}</nav>
</div></header>
"""


def foot():
    return f"""<footer><div class="wrap">
<div class="small">{SERIES}之庄子　·　v{VER}　·　CC BY-NC-SA 4.0<br><a href="{SITE}/llms.txt">llms.txt</a>　·　<a href="{SITE}/sitemap.xml">sitemap</a></div>
<div class="small"><a href="https://github.com/q1z2q3-debug/daokedao-zhuangzi">GitHub</a>　·　<a href="https://doi.org/{DOI}">DOI</a>　·　<a href="https://q1z2q3-debug.github.io/runze-daokedao/">系列总站</a></div>
</div></footer>
</body></html>
"""


def inline(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def md2html(src):
    out, bufq, bufl = [], [], []

    def flush():
        nonlocal bufq, bufl
        if bufq:
            out.append("<blockquote>" + "".join(f"<p>{x}</p>" for x in bufq) + "</blockquote>"); bufq = []
        if bufl:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in bufl) + "</ul>"); bufl = []

    for raw in src.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        if line.startswith("### "):
            flush(); out.append(f"<h4>{inline(H.escape(line[4:]))}</h4>"); continue
        if line.startswith("## "):
            flush(); out.append(f"<h3>{inline(H.escape(line[3:]))}</h3>"); continue
        if line == "---" or line == ">":
            flush(); continue
        if line.startswith(">"):
            if bufl: flush()
            t = line[1:].lstrip()
            if t: bufq.append(inline(H.escape(t)))
            continue
        if line.startswith("- "):
            if bufq: flush()
            bufl.append(inline(H.escape(line[2:])))
            continue
        flush(); out.append(f"<p>{inline(H.escape(line))}</p>")
    flush()
    return "".join(out)


def parse():
    """切出各篇：[(组, 序, 篇名, 正文 md)]，另返回前言等前置节。"""
    lines = SRC.read_text(encoding="utf-8").split("\n")
    secs, cur = [], None
    for ln in lines:
        if ln.startswith("# "):
            secs.append([ln[2:].strip(), []])
            cur = secs[-1]
        elif cur:
            cur[1].append(ln)
    arts, front = [], []
    for title, body in secs:
        body = "\n".join(body).strip()
        m = re.match(r"第(一|二|三|四|五|六|七)篇｜(.+)", title)
        if m:
            arts.append(["内篇", m.group(2).strip(), body]); continue
        m = re.match(r"外篇(一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五)｜(.+)", title)
        if m:
            arts.append(["外篇", m.group(2).strip(), body]); continue
        m = re.match(r"杂篇(一|二|三|四|五|六)｜(.+)", title)
        if m:
            arts.append(["杂篇", m.group(2).strip(), body]); continue
        m = re.match(r"附\s*录｜(.+)", title)
        if m:
            arts.append(["附录", m.group(1).strip(), body]); continue
        if title.replace(" ", "") in ("外篇选读", "杂篇选读", "目录", "封底"):
            continue
        front.append((title, body))
    return front, arts


def build():
    front, arts = parse()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "chapters").mkdir(exist_ok=True)

    # ---- 逐篇页 ----
    recs = []
    for i, (grp, name, body) in enumerate(arts, 1):
        slug = P_SLUG.get(name, f"p{i}")
        fn = f"{i:02d}-{slug}.html"
        wc = len(re.sub(r"\s", "", body))
        desc = f"《庄子》{name}：经文底本、字源溯源、逐段深解、常见误读。{wc} 字。"
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"{name}｜润泽说 道可道之庄子",
              "url": f"{SITE}/chapters/{fn}", "inLanguage": "zh-Hans", "wordCount": wc,
              "author": {"@type": "Person", "name": "润泽"},
              "isPartOf": {"@type": "Book", "@id": f"{SITE}/book.html#book", "name": TITLE},
              }
        prev = nxt = ""
        if i > 1:
            p = arts[i - 2]
            prev = f'<a href="{SITE}/chapters/{i-1:02d}-{P_SLUG.get(p[1], f"p{i-1}")}.html">← {p[1]}</a>'
        if i < len(arts):
            n = arts[i]
            nxt = f'<a href="{SITE}/chapters/{i+1:02d}-{P_SLUG.get(n[1], f"p{i+1}")}.html">{n[1]} →</a>'
        body_html = f"""<main><div class="wrap">
<p class="eyebrow">{grp}　·　第 {i} 篇　·　{wc} 字</p>
<h1>{H.escape(name)}</h1>
<p class="small">底本：郭庆藩《庄子集释》校王先谦《庄子集解》，异文随文出注　·　<a href="{SITE}/book.html">全书阅读版</a>　·　<a href="{SITE}/chapters/">篇目</a>　·　<a href="https://doi.org/{DOI}">DOI {DOI}</a></p>
<article>{md2html(body)}</article>
<div class="prevnext">{prev}<a href="{SITE}/chapters/">篇目</a>{nxt}</div>
</div></main>"""
        (DOCS / "chapters" / fn).write_text(head(f"{name}｜{TITLE}", desc, f"/chapters/{fn}", ld, act="chapters") + body_html + foot(), encoding="utf-8")
        recs.append(dict(i=i, grp=grp, name=name, fn=fn, wc=wc))

    # ---- 篇目 ----
    secs = []
    for g, label in (("内篇", "内篇七篇"), ("外篇", "外篇十五篇"), ("杂篇", "杂篇六篇"), ("附录", "附录")):
        grp = [r for r in recs if r["grp"] == g]
        if not grp:
            continue
        secs.append(f"<h2>{label}　<span class='small'>{len(grp)} 篇</span></h2><div class='list'>")
        for r in grp:
            secs.append(f"""<div class="row"><div class="no">{r['i']:02d}</div>
<div><h3><a href="{SITE}/chapters/{r['fn']}">{r['name']}</a></h3>
<p class="small" style="margin:0;">{r['wc']} 字</p></div>
<div class="go"><a href="{SITE}/chapters/{r['fn']}">读这一篇</a></div></div>""")
        secs.append("</div>")
    idx_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "庄子篇目",
              "url": f"{SITE}/chapters/", "inLanguage": "zh-Hans",
              "isPartOf": {"@type": "Book", "@id": f"{SITE}/book.html#book"}}
    (DOCS / "chapters" / "index.html").write_text(
        head(f"篇目｜{TITLE}",
             "《庄子》二十八篇全目：内七篇、外十五篇、杂六篇，另附立言法度一卷。一篇一页，可单独引用。",
             "/chapters/", idx_ld, act="chapters") +
        f"""<main><div class="wrap">
<p class="eyebrow">庄子 · 二十八篇</p>
<h1>一篇一页，二十八篇</h1>
<p class="lede">内七篇全帙，外十五篇、杂六篇逐篇成文，末附《庄子立言之法度》一卷。每篇同构：经文底本、本篇定位、关键字溯源、逐段落深解、故事讲读、本篇总括、诠释分歧与常见误读。</p>
<p class="small">全书 {sum(r['wc'] for r in recs):,} 字　·　<a href="{SITE}/book.html">全书阅读版</a>　·　<a href="{SITE}/downloads/">下载</a></p>
{''.join(secs)}
</div></main>""" + foot(), encoding="utf-8")

    # ---- 首页 ----
    up = [s for s in front if s[0].replace(" ", "") == "总序"]
    lead = up[0][1][:600] if up else ""
    home_ld = {"@context": "https://schema.org", "@type": "Book", "@id": f"{SITE}/book.html#book",
               "name": TITLE, "alternateName": ["道可道之庄子", "庄子读本"], "author": {"@type": "Person", "name": "润泽"},
               "inLanguage": "zh-Hans", "version": VER, "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
               
               "description": "内七篇全帙、外十五篇与杂六篇逐篇深解，以「合与和」一对分辨为主脉，字源与底本校勘先行。"}
    (DOCS / "index.html").write_text(
        head(TITLE, "《庄子》内七篇全帙、外十五篇与杂六篇逐篇深解：字源溯源、底本校勘、逐段拆解，以「合与和」一对分辨读庄。全书 29.8 万字。",
             "/", home_ld, act="home") +
        f"""<main><div class="wrap">
<p class="eyebrow">{SERIES}</p>
<h1>道可道之庄子</h1>
<p class="lede">万物皆客，你我皆自主。内七篇全帙，外十五篇、杂六篇逐篇成文，末附立言法度一卷。全书 {sum(r['wc'] for r in recs):,} 字。</p>
<p class="small">v{VER}　·　28 篇 + 附录　·　CC BY-NC-SA 4.0　·　<a href="https://doi.org/{DOI}">DOI {DOI}</a></p>

<h2>怎么读</h2>
<div class="list">
<div class="row"><div class="no">01</div><div><h3><a href="{SITE}/book.html">全书一页 · 阅读版</a></h3>
<p class="small" style="margin:0;">单文件自包含，封面、目录、全篇都在一页，断网可读</p></div>
<div class="go"><a href="{SITE}/book.html">打开</a></div></div>
<div class="row"><div class="no">02</div><div><h3><a href="{SITE}/chapters/">篇目 · 一篇一页</a></h3>
<p class="small" style="margin:0;">内七、外十五、杂六，逐篇独立成页，可单独引用</p></div>
<div class="go"><a href="{SITE}/chapters/">篇目</a></div></div>
<div class="row"><div class="no">03</div><div><h3><a href="{SITE}/downloads/">下载 · PDF 与安卓包</a></h3>
<p class="small" style="margin:0;">成书 PDF（19.7 MB）与离线 APK（3.7 MB，零权限）</p></div>
<div class="go"><a href="{SITE}/downloads/">下载</a></div></div>
</div>

<h2>这本书主张什么</h2>
<p>古今解庄者多落三途：读作消极避世，读作权谋养生，或止于逐字考据。本书立一对分辨为读庄主脉——<b>合与和</b>：合是人为的分类、命名、制度，和是差异各得其位、彼此不害。庄子所破的是把合当成和，所守的是和。</p>
<p>三言法度、天倪天均、物化生死诸题，皆以此辨贯穿；关键字回到先秦字形与用例，底本以《庄子集释》为主，异文两存，不强行统一。</p>

<h2>体例</h2>
<p>每篇七层：经文底本、本篇定位（时代与处境）、关键字溯源、逐段落深解、故事讲读、本篇总括、附录（诠释分歧与常见误读）。</p>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 下载页 ----
    (DOCS / "downloads").mkdir(exist_ok=True)
    (DOCS / "downloads" / "index.html").write_text(
        head(f"下载｜{TITLE}", "《庄子》成书 PDF（704 页级 A5）与离线安卓包 APK，零权限、断网可用。", "/downloads/", None, act="downloads") +
        f"""<main><div class="wrap">
<p class="eyebrow">下载</p>
<h1>三种拿法</h1>
<p class="lede">要印，取 PDF；要在手机上看，取 APK；要在浏览器里翻，直接用<a href="{SITE}/book.html">全书页</a>。</p>
<div class="list">
<div class="row"><div class="no">PDF</div><div><h3><a href="https://github.com/q1z2q3-debug/daokedao-zhuangzi/blob/main/book/润泽说 道可道之庄子.pdf">成书 PDF</a></h3>
<p class="small" style="margin:0;">19.7 MB，A5 版式，可直接印制</p></div><div class="go"><a href="https://github.com/q1z2q3-debug/daokedao-zhuangzi/blob/main/book/润泽说 道可道之庄子.pdf">GitHub</a></div></div>
<div class="row"><div class="no">APK</div><div><h3><a href="{SITE}/downloads/道可道-庄子-1.33.0.apk">安卓离线包 v{VER}</a></h3>
<p class="small" style="margin:0;">3.7 MB，包名 com.daokedao.zhuangzi，无任何权限，字体已内置</p></div><div class="go"><a href="{SITE}/downloads/道可道-庄子-1.33.0.apk">下载</a></div></div>
<div class="row"><div class="no">MD</div><div><h3><a href="https://github.com/q1z2q3-debug/daokedao-zhuangzi/blob/main/book/润泽说 道可道之庄子.md">Markdown 母本</a></h3>
<p class="small" style="margin:0;">873 KB，可 diff、可再加工</p></div><div class="go"><a href="https://github.com/q1z2q3-debug/daokedao-zhuangzi/blob/main/book/润泽说 道可道之庄子.md">GitHub</a></div></div>
</div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 全书页 ----
    (DOCS / "book.html").write_text((ROOT / "book" / "润泽说 道可道之庄子.html").read_text(encoding="utf-8"), encoding="utf-8")

    # ---- 机器可读 ----
    (DOCS / "llms.txt").write_text(f"""# {TITLE}

> 润泽（润泽博士）《道可道》系列第三部。以「合与和」一对分辨读庄：合是人为的分类、命名、制度，和是差异各得其位、彼此不害。全书 {sum(r['wc'] for r in recs):,} 字，v{VER}。

## 读本
- 全书一页（阅读版，单文件）：{SITE}/book.html
- 篇目（28 篇 + 附录，一篇一页）：{SITE}/chapters/
- 下载（PDF / APK / Markdown 母本）：{SITE}/downloads/
- 仓库：https://github.com/q1z2q3-debug/daokedao-zhuangzi
- DOI：https://doi.org/{DOI}

## 篇目
""" + "\n".join(f"- {r['name']}：{SITE}/chapters/{r['fn']}（{r['wc']} 字）" for r in recs) + f"""

## 事实
- 结构：内七篇、外十五篇、杂六篇，另附《庄子立言之法度》一卷。
- 体例：经文底本、本篇定位、关键字溯源、逐段落深解、故事讲读、本篇总括、诠释分歧与常见误读。
- 底本：郭庆藩《庄子集释》，参王先谦《庄子集解》，异文随文出注。
- 许可：CC BY-NC-SA 4.0。
- 系列：道德经 v3.0.1（https://q1z2q3-debug.github.io/runze-daodejing/）、易传 v1.50.0（https://q1z2q3-debug.github.io/daokedao-yijing/）、心经 v1.0.0（https://q1z2q3-debug.github.io/daokedao-xinjing/）。

## 引用
润泽. {TITLE}：v{VER}. 2026. https://doi.org/{DOI} 
""", encoding="utf-8")

    (DOCS / "robots.txt").write_text("User-agent: *\nAllow: /\n\n" +
                                     "".join(f"User-agent: {b}\nAllow: /\n" for b in
                                             ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "Bytespider"]) +
                                     f"\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    urls = ["/", "/book.html", "/chapters/", "/downloads/"] + [f"/chapters/{r['fn']}" for r in recs]
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      "".join(f"<url><loc>{SITE}{u}</loc><lastmod>2026-11-14</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")

    # ---- favicon ----
    (DOCS / "favicon.svg").write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#F7F4EE"/><rect x="6" y="6" width="52" height="52" fill="none" stroke="#8C3A2E" stroke-width="2"/>
<text x="32" y="43" text-anchor="middle" font-family="serif" font-size="30" fill="#1B1917">庄</text></svg>""", encoding="utf-8")

    print(f"built {len(list(DOCS.rglob('*.html')))} html pages, {len(recs)} chapters")


if __name__ == "__main__":
    build()
