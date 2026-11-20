"""Check daily.json before pushing. Exit code 1 and a list of problems if anything is wrong.
Usage: python3 scripts/validate.py
"""
import json, re, sys, datetime

LEVELS = ["k", "p1", "p2", "m"]
problems = []

def bad(msg):
    problems.append(msg)

try:
    data = json.load(open("daily.json", encoding="utf-8"))
except Exception as e:
    print("daily.json 無法讀取：", e); sys.exit(1)

days = data.get("days")
if not isinstance(days, list) or not days:
    bad("days 必須是非空的陣列")
    days = []

dates = [d.get("date") for d in days]
if dates != sorted(dates, reverse=True):
    bad("days 必須依日期由新到舊排列")
if len(set(dates)) != len(dates):
    bad("days 裡有重複的日期")
if len(days) > 14:
    bad("days 最多保留 14 天")
if data.get("updated") != (dates[0] if dates else None):
    bad("updated 必須等於最新一天的日期")

seen_today = set()
for d in days:
    try:
        datetime.date.fromisoformat(d["date"])
    except Exception:
        bad(f"日期格式錯誤：{d.get('date')}")
    picks = d.get("picks", {})
    for lv in LEVELS:
        v = picks.get(lv)
        where = f"{d.get('date')} / {lv}"
        if not v:
            bad(f"{where}：缺少影片"); continue
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", v.get("id", "")):
            bad(f"{where}：影片 ID 格式錯誤 {v.get('id')}")
        for key in ("title", "channel", "topic", "why"):
            if not str(v.get(key, "")).strip():
                bad(f"{where}：缺少 {key}")
        if d is days[0]:
            if v.get("id") in seen_today:
                bad(f"{where}：同一天重複使用影片 {v.get('id')}")
            seen_today.add(v.get("id"))
        quiz = v.get("quiz", [])
        if len(quiz) != 3:
            bad(f"{where}：quiz 必須剛好 3 題（目前 {len(quiz)}）")
        for i, q in enumerate(quiz, 1):
            if q.get("type") not in ("fact", "open"):
                bad(f"{where} 第{i}題：type 必須是 fact 或 open")
            if not str(q.get("q", "")).strip():
                bad(f"{where} 第{i}題：缺少題目 q")
            if q.get("type") == "fact":
                if not q.get("keywords") or not all(isinstance(k, str) and k for k in q["keywords"]):
                    bad(f"{where} 第{i}題：fact 題必須有 keywords")
                for key in ("answer", "hint"):
                    if not str(q.get(key, "")).strip():
                        bad(f"{where} 第{i}題：fact 題缺少 {key}")
            if q.get("type") == "open" and not str(q.get("sample", "")).strip():
                bad(f"{where} 第{i}題：open 題缺少 sample")

if problems:
    print("發現問題：")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print(f"daily.json 檢查通過：{len(days)} 天，最新 {dates[0]}")
