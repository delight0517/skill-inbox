#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_skill.py — 새 스킬/프로젝트 자동 GitHub 출시 (박새로이 2026-08-29)

wheel-reverse 성공 포맷을 일반화한 범용 출시기:
  - 프로젝트 폴더를 받아 README(개발자 소개+URL) 생성/보강
  - git init + commit + push
  - GitHub public repo 생성 (이름/설명/topics/homepage)
  - release/ 안의 바이너리가 있으면 GitHub Release 자동 생성
  - 이미 repo가 있으면 README/topics/homepage만 갱신 (재출시)

용법:
  python publish_skill.py <프로젝트폴더> [--name repo이름] [--desc "설명"] [--topics a,b,c] [--homepage URL] [--private]
"""
import os, sys, subprocess, json, glob, argparse, datetime

GH = r"C:\Users\user\WheelReverse\ghbin\bin\gh.exe"
if not os.path.exists(GH):
    GH = "gh"

DEV_SECTION = """
---

## ✨ 만든 사람 (Developer)

**로간 (GeunHu Kim) — "박새로이(Baksaeroyi)" 페르소나로 활동하는 자동화 엔지니어**

> "내가 안 해도 되게 만들자." — 반복되는 수동 작업은 자동화로 끝내는 걸 지향합니다.

| | |
|---|---|
| 🏠 GitHub | https://github.com/delight0517 |
| 🧠 포트폴리오 | https://delight0517.github.io/releasepilot-reports/links/ |
| ✉️ 문의 | rogan2534@gmail.com |

- macOS·Windows·iOS·Android 전 플랫폼 앱 출시 자동화
- 반복 작업 자동화, API 통합, AI 에이전트 운영
- **원격·단기 외주 환영** (풀스택 웹/앱, Python, AI API 연동)
"""

DEFAULT_TOPICS = ["windows", "tool", "automation", "utility"]

def run(cmd, cwd=None, timeout=180):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)

def has_dev_section(content):
    return ("만든 사람" in content) or ("github.com/delight0517" in content)

def ensure_readme(folder, desc):
    """README 없으면 생성, 있으면 개발자 소개 섹션만 보강."""
    rp = os.path.join(folder, "README.md")
    if os.path.exists(rp):
        old = open(rp, encoding="utf-8", errors="replace").read()
        if has_dev_section(old):
            return False
        with open(rp, "w", encoding="utf-8") as f:
            f.write(old.rstrip() + "\n" + DEV_SECTION + "\n")
        return True
    name = os.path.basename(folder.rstrip("/\\"))
    readme = f"# {name}\n\n{desc or '프로젝트 설명이 여기에 들어갑니다.'}\n"
    readme += DEV_SECTION + "\n"
    with open(rp, "w", encoding="utf-8") as f:
        f.write(readme)
    return True

def git_push(folder):
    """git init/commit/push. 이미 repo면 pull 후 push."""
    run(["git", "init", "-b", "main"], cwd=folder)
    run(["git", "add", "-A"], cwd=folder)
    # 기본 .gitignore 없으면 생성
    gi = os.path.join(folder, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("__pycache__/\n*.pyc\nbuild/\ndist/\nnode_modules/\n.env\n*.log\n")
        run(["git", "add", ".gitignore"], cwd=folder)
    # git 사용자 설정 (로컬)
    run(["git", "config", "user.name", "Rogan"], cwd=folder)
    run(["git", "config", "user.email", "rogan2534@gmail.com"], cwd=folder)
    run(["git", "commit", "-m", "init: %s (%s)" % (os.path.basename(folder), datetime.date.today().isoformat())], cwd=folder)
    # 기존 origin 있으면 pull (허브 동기화 충돌 대비)
    r = run(["git", "remote", "get-url", "origin"], cwd=folder)
    if r.returncode == 0:
        run(["git", "pull", "--rebase", "origin", "main"], cwd=folder, timeout=60)
    return True

def publish(folder, name, desc, topics, homepage, private):
    if not os.path.isdir(folder):
        print(f"❌ 폴더 없음: {folder}")
        return 1
    name = name or os.path.basename(folder.rstrip("/\\"))
    print(f"📦 출시 시작: {name} ← {folder}")

    # 1) README
    changed = ensure_readme(folder, desc)
    print(f"  README: {'작성/보강' if changed else '이미 완비'}")

    # 2) repo 존재 확인
    r = run([GH, "repo", "view", f"delight0517/{name}", "--json", "name"], timeout=60)
    exists = (r.returncode == 0)

    # 3) git push 준비
    git_push(folder)

    if not exists:
        args = [GH, "repo", "create", name, "--public" if not private else "--private",
                "--source", folder, "--push"]
        if desc:
            args += ["--description", desc]
        r = run(args, timeout=300)
        if r.returncode != 0:
            print(f"❌ repo 생성 실패: {r.stderr[:300]}")
            return 1
        print(f"  ✅ repo 생성: https://github.com/delight0517/{name}")
    else:
        # 이미 있으면 README push + 메타 갱신
        run(["git", "push", "-u", "origin", "main"], cwd=folder, timeout=120)
        print("  ✅ 기존 repo — README push 완료")

    # 4) topics + homepage
    args = [GH, "repo", "edit", f"delight0517/{name}"]
    for t in (topics or DEFAULT_TOPICS):
        args += ["--add-topic", t]
    if homepage:
        args += ["--homepage", homepage]
    if desc:
        args += ["--description", desc]
    run(args, timeout=60)
    print(f"  ✅ topics={topics or DEFAULT_TOPICS} homepage={homepage or '-'}")

    # 5) release/ 바이너리 → GitHub Release
    rel_dir = os.path.join(folder, "release")
    assets = []
    if os.path.isdir(rel_dir):
        for pat in ("*.exe", "*.dll", "*.zip", "*.msi", "*.apk", "*.dmg", "*.pkg", "*.py", "*.md"):
            assets += glob.glob(os.path.join(rel_dir, pat))
    tag = f"v1.0.0"
    # 기본 브랜치 자동 감지 (main/master)
    rb = run([GH, "repo", "view", f"delight0517/{name}", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"], timeout=60)
    branch = rb.stdout.strip() if rb.returncode == 0 and rb.stdout.strip() else "main"
    r = run([GH, "release", "view", tag, "--json", "tagName"], timeout=60)
    if assets:
        args = [GH, "release", "create", tag, "--title", f"{name} {tag}", "--notes", f"{desc or name} 배포", "--target", branch] + assets
        if r.returncode == 0:
            args = [GH, "release", "delete", tag, "--yes"]  # 재생성
            run(args, timeout=120)
            args = [GH, "release", "create", tag, "--title", f"{name} {tag}", "--notes", f"{desc or name} 배포", "--target", branch] + assets
        rr = run(args, timeout=300)
        print(f"  ✅ Release {tag} ({'OK' if rr.returncode==0 else rr.stderr[:150]})")
    print(f"🎉 완료: https://github.com/delight0517/{name}")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="프로젝트 폴더 경로")
    ap.add_argument("--name", help="GitHub repo 이름 (기본: 폴더명)")
    ap.add_argument("--desc", help="repo 설명")
    ap.add_argument("--topics", help="콤마 구분 topics")
    ap.add_argument("--homepage", help="homepage URL")
    ap.add_argument("--private", action="store_true", help="private repo로 생성")
    a = ap.parse_args()
    sys.exit(publish(a.folder, a.name, a.desc,
                     [t.strip() for t in a.topics.split(",")] if a.topics else None,
                     a.homepage, a.private))
