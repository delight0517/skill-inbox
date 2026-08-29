#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
skill_watcher.py — 새 스킬/프로젝트 감시 → 자동 GitHub 출시 (박새로이 2026-08-29)

사용자 요청: "새로운 스킬이나 독보적 스킬이 생길 때마다 GitHub 출시 (세콤처럼 자동)"

감시 대상 폴더 (없으면 자동 생성):
  C:\Users\user\Desktop\appDev        ← 새 스킬을 여기 두면 자동 출시
  C:\Users\user\Desktop\근후's appdev\apps  ← 기존 프로젝트 (이미 GitHub 있는 것 스킵)

규칙:
  - 폴더가 git repo이고 origin이 GitHub(delight0517/*)면 → 이미 출시됨 → 스킵
  - 폴더에 소스/산출물이 있으면 → publish_skill.py로 자동 출시
  - 출시 결과를 stdout으로 출력 (cron이 사용자에게 전달)
"""
import os, sys, subprocess, json, datetime

PUBLISHER = r"C:\Users\user\WheelReverse\publish_skill.py"
GH = r"C:\Users\user\WheelReverse\ghbin\bin\gh.exe"
if not os.path.exists(GH):
    GH = "gh"

WATCH_DIRS = []
_env_dirs = os.environ.get("SKILL_WATCH_DIRS", "")
if _env_dirs:
    WATCH_DIRS = [d.strip() for d in _env_dirs.split(";") if d.strip()]
if not WATCH_DIRS:
    WATCH_DIRS = [
        "C:/Users/user/Desktop/appDev",
        "C:/Users/user/Desktop/근후's appdev/apps",
    ]
STATE = os.path.expanduser("~/.hermes/state/skill_watcher_state.json")

# 출시 제외 패턴 (시스템/중복 폴더)
SKIP_NAMES = {".git", "__pycache__", "node_modules", "dist", "build", "dl", "ghbin",
              "release", "scripts", "폴더 정리할것들", "geunhu-appdev", "launchpad",
              "releasepilot", "delete-fix"}
# 출시 제외 — 민감/개인
SKIP_SENSITIVE = {"harugirok", "brainwire", "secom", "auth", "private", "creds"}

def run(args, timeout=180):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)

def is_published(folder):
    """폴더 자체가 git repo이고 origin이 delight0517 GitHub면 이미 출시."""
    # 상위 repo(skill-inbox 등)의 remote를 물려받지 않도록,
    # 폴더 자신이 git repo의 루트인지 먼저 확인 (rev-parse --show-toplevel)
    r = run(["git", "-C", folder, "rev-parse", "--show-toplevel"], timeout=30)
    if r.returncode != 0:
        return False
    toplevel = r.stdout.strip()
    if not toplevel:
        return False
    # toplevel이 이 폴더 자신이 아니면 → 상위 repo에 속한 일반 폴더 → 미출시
    if os.path.normcase(os.path.abspath(toplevel)) != os.path.normcase(os.path.abspath(folder)):
        return False
    r2 = run(["git", "-C", folder, "remote", "-v"], timeout=30)
    return "github.com/delight0517" in r2.stdout or "github.com/Rogan" in r2.stdout

def looks_like_project(folder):
    """소스/산출물이 있는 진짜 프로젝트인지."""
    for f in os.listdir(folder):
        if f.startswith("."):
            continue
        p = os.path.join(folder, f)
        if os.path.isfile(p) and f.lower().endswith((".py", ".js", ".ts", ".dart", ".html",
                                                      ".md", ".exe", ".dll", ".apk", ".json", ".yaml", ".yml")):
            return True
    return False

def main():
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    results = []
    published = 0
    skipped = 0

    # 디버그 (env가 제대로 왔는지)
    import sys
    print(f"[debug] WATCH_DIRS={WATCH_DIRS!r}", file=sys.stderr)
    print(f"[debug] GH={GH!r}", file=sys.stderr)

    for base in WATCH_DIRS:
        os.makedirs(base, exist_ok=True)
        entries = sorted(os.listdir(base))
        print(f"[debug] base={base!r} entries={entries!r}", file=sys.stderr)
        for entry in entries:
            folder = os.path.join(base, entry)
            if not os.path.isdir(folder):
                continue
            if entry in SKIP_NAMES or any(s in entry.lower() for s in SKIP_SENSITIVE):
                skipped += 1
                continue
            if entry.startswith("."):
                continue
            if is_published(folder):
                skipped += 1
                continue
            if not looks_like_project(folder):
                continue
            # 출시!
            r = run(["python", PUBLISHER, folder, "--name", entry],
                    timeout=300)
            if r.returncode == 0:
                published += 1
                url = f"https://github.com/delight0517/{entry}"
                results.append(f"🆕 스킬 자동 출시: {entry} → {url}")
                if r.stdout.strip():
                    results.append("   " + r.stdout.strip().splitlines()[-1])
            else:
                err = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "?"
                results.append(f"⚠️ {entry} 출시 실패: {err}")

    if results:
        print("📦 [스킬 자동 출시 감시]\n" + "\n".join(results) +
              f"\n(출시 {published}건 · 스킵 {skipped}건)")
    # 변화 없으면 빈 출력 → cron이 조용히 종료
    return 0

if __name__ == "__main__":
    sys.exit(main())
