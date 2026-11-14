#!/usr/bin/env python3
"""把《庄子》存入 Zenodo，取一个可引用的 DOI。

用法：
  export ZENODO_TOKEN=$(~/.daokedao-vault/cred zenodo)
  python3 scripts/zenodo-deposit.py --dry-run      # 建草稿、传附件，不发布
  python3 scripts/zenodo-deposit.py --publish      # DOI 立即生效，不可撤销
"""
import argparse, json, os, urllib.request
from pathlib import Path

BASE = "https://zenodo.org/api"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ROOT = Path(__file__).resolve().parent.parent
VER = "1.33.0"

FILES = [
    ("book/润泽说 道可道之庄子.md", "daokedao-zhuangzi-v1.33.0.md"),
    ("book/润泽说 道可道之庄子.pdf", "daokedao-zhuangzi-v1.33.0.pdf"),
    ("book/润泽说 道可道之庄子.html", "daokedao-zhuangzi-reader-v1.33.0.html"),
    ("packages/apk-1.33.0-zhuangzi/道可道-庄子-1.33.0.apk", "daokedao-zhuangzi-reader-v1.33.0.apk"),
]

META = {"metadata": {
    "title": "润泽说 道可道之庄子（v1.33.0）",
    "upload_type": "publication",
    "publication_type": "book",
    "publication_date": "2026-11-14",
    "version": VER,
    "language": "zho",
    "license": "cc-by-nc-sa-4.0",
    "creators": [{"name": "润泽"}],
    "keywords": ["庄子", "道家", "先秦哲学", "字源", "内篇", "外篇", "杂篇", "中国哲学"],
    "description": (
        "<p>《庄子》内七篇全帙、外十五篇与杂六篇逐篇深解。全书 290,793 字，28 篇，"
        "另附《庄子立言之法度》一卷。</p>"
        "<p>体例：每篇七层——经文底本、本篇定位、关键字溯源、逐段落深解、故事讲读、"
        "本篇总括、附录（诠释分歧与常见误读）。底本以郭庆藩《庄子集释》为主，"
        "参王先谦《庄子集解》，异文随文出注。</p>"
        "<p>立宗：以「合与和」一对分辨为读庄主脉。合是人为的分类、命名、制度；"
        "和是差异各得其位、彼此不害。所破的是把合当成和，所守的是和。</p>"
        "<p>附件：Markdown 母本、成书 PDF（326 页）、单文件 HTML 阅读版、"
        "安卓离线包（零权限、断网可用、字体内置）。</p>"
    ),
    "related_identifiers": [
        {"relation": "isSupplementTo",
         "identifier": "https://github.com/q1z2q3-debug/daokedao-zhuangzi",
         "resource_type": "software"},
        {"relation": "isAlternateIdentifier",
         "identifier": "https://q1z2q3-debug.github.io/daokedao-zhuangzi/",
         "resource_type": "other"},
        {"relation": "isPartOf",
         "identifier": "https://q1z2q3-debug.github.io/runze-daokedao/",
         "resource_type": "other"},
    ],
    "notes": "许可 CC BY-NC-SA 4.0。引用请注明书名与版本号 v1.33.0。本书为「润泽说 道可道」系列第四部。",
}}


def call(url, token, data=None, method="POST", raw=None):
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {token}", "User-Agent": UA,
        "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("ZENODO_TOKEN") or ""
    if not token:
        raise SystemExit("缺 ZENODO_TOKEN")

    dep = call(BASE + "/deposit/depositions", token, {})
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    print("draft", dep_id, dep["links"]["html"])

    call(BASE + f"/deposit/depositions/{dep_id}", token, META, method="PUT")

    for path, name in FILES:
        data = (ROOT / path).read_bytes()
        req = urllib.request.Request(f"{bucket}/{name}", data=data, method="PUT", headers={
            "Authorization": f"Bearer {token}", "User-Agent": UA,
            "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(req, timeout=900) as r:
            j = json.load(r)
        print("  up", j.get("key"), j.get("size"))

    if a.publish:
        pub = call(BASE + f"/deposit/depositions/{dep_id}/actions/publish", token, {}, method="POST")
        print("DOI", pub.get("doi"), pub.get("links", {}).get("doi"))
    else:
        print("草稿未发布：", dep["links"]["html"])


if __name__ == "__main__":
    main()
