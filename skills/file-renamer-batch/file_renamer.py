#!/usr/bin/env python3
"""file_renamer_batch.py — 규칙 기반 파일 일괄 이름 변경"""
import os, sys, argparse, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="대상 폴더")
    ap.add_argument("--prefix", default="", help="접두사")
    ap.add_argument("--suffix", default="", help="접미사")
    ap.add_argument("--start", type=int, default=1, help="시작 번호")
    ap.add_argument("--dry-run", action="store_true", help="실제 변경 없이 미리보기")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.dir)
                   if os.path.isfile(os.path.join(a.dir, f)) and not f.startswith("."))
    used = set()
    for i, f in enumerate(files, start=a.start):
        name, ext = os.path.splitext(f)
        new = f"{a.prefix}-{i:03d}{ext}" if a.prefix else f"{i:03d}{ext}"
        while new in used:
            i += 1
            new = f"{a.prefix}-{i:03d}{ext}" if a.prefix else f"{i:03d}{ext}"
        used.add(new)
        old = os.path.join(a.dir, f)
        dst = os.path.join(a.dir, new)
        print(f"  {f} → {new}")
        if not a.dry_run:
            os.rename(old, dst)
    print(f"\n{'[dry-run] ' if a.dry_run else ''}완료: {len(files)}개 파일")

if __name__ == "__main__":
    main()
