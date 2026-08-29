#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feedback_collect.py — 2주 1회 GitHub 반응/피드백 수집기 (박새로이 2026-08-29)

delight0517 계정의 모든 public 저장소에서:
  - 새 이슈 (요구사항·에러·피드백) — 최근 14일
  - 별(star) 수 변화
  - 포크 수
  - 최근 반응 (이슈/PR 코멘트)
수집해 사용자에게 보기 좋은 마크다운 보고서로 출력.

출력: stdout (cron이 그대로 전달). 보고서 없으면(변화 없으면) 빈 출력 → 조용히 종료.
"""
import os, sys, json, subprocess, datetime, io

GH = r"C:\Users\user\WheelReverse\ghbin\bin\gh.exe"
if not os.path.exists(GH):
    GH = "gh"

OWNER = "delight0517"
SINCE_DAYS = 14
STATE = os.path.expanduser("~/.hermes/state/feedback_collect_state.json")

def run(args, timeout=60):
    return subprocess.run([GH] + args, capture_output=True, text=True, timeout=timeout)

def api(path):
    r = run(["api", path, "--jq", "."])
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None

def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"last_run": "", "stars": {}}

def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def main():
    state = load_state()
    now = datetime.date.today()
    since = (now - datetime.timedelta(days=SINCE_DAYS)).isoformat()

    # public 저장소 목록
    r = run(["repo", "list", OWNER, "--limit", "100", "--json", "name,visibility,description,createdAt,stargazerCount,forkCount"])
    if r.returncode != 0:
        print(f"❌ repo 목록 조회 실패: {r.stderr[:200]}")
        return 1
    repos = json.loads(r.stdout)
    public = [x for x in repos if x["visibility"] == "PUBLIC"]

    out = []
    total_stars = 0
    total_issues = 0
    star_changes = []

    for repo in sorted(public, key=lambda x: x["name"]):
        name = repo["name"]
        stars = repo.get("stargazerCount", 0)
        forks = repo.get("forkCount", 0)
        total_stars += stars
        prev = state.get("stars", {}).get(name)
        if prev is not None and stars != prev:
            star_changes.append(f"  ⭐ {name}: {prev} → {stars}")
        state.setdefault("stars", {})[name] = stars

        # 새 이슈 (14일 이내, open 포함)
        issues = api(f"repos/{OWNER}/{name}/issues?state=all&since={since}&per_page=20")
        if issues:
            real = [i for i in issues if "pull_request" not in i]
            for i in real:
                total_issues += 1
                labels = ", ".join(l["name"] for l in i.get("labels", [])) or "일반"
                body = (i.get("body") or "").strip().replace("\n", " ")[:120]
                out.append(f"  🐛 [{name}] #{i['number']} ({labels}) {i['title']}\n    └ {body}")

        # 최근 이슈 코멘트 (요구사항/에러 피드백)
        comments = api(f"repos/{OWNER}/{name}/issues/comments?since={since}&per_page=10")
        if comments:
            for c in comments[:5]:
                body = (c.get("body") or "").strip().replace("\n", " ")[:120]
                out.append(f"  💬 [{name}] 댓글: {body}")

    # 최근 새 public 저장소 (지난 14일 생성)
    new_repos = [x["name"] for x in public if x.get("createdAt", "")[:10] >= since]
    if new_repos:
        out.append(f"  🆕 신규 공개 저장소: {', '.join(new_repos)}")

    state["last_run"] = now.isoformat()
    save_state(state)

    if not out and not star_changes:
        return 0  # 변화 없음 → 조용히 (스팸 방지)

    report = [f"📊 GitHub 피드백 리포트 ({now.isoformat()})",
              f"공개 저장소 {len(public)}개 · 총 ⭐ {total_stars} · 새 이슈/반응 {total_issues}건",
              ""]
    if star_changes:
        report.append("**⭐ 별 변화:**")
        report += star_changes
        report.append("")
    if out:
        report.append("**📝 요구사항·에러·피드백:**")
        report += out
    report.append("")
    report.append("_출처: https://github.com/delight0517_")
    print("\n".join(report))
    return 0

if __name__ == "__main__":
    sys.exit(main())
