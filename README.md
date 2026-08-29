# 📥 Skill Inbox — 새 스킬 자동 출시 수신함

**여기에 폴더를 push하면 → GitHub Actions가 자동으로 public 저장소로 출시합니다.** (24/7, 서버 불필요, 맥·윈도우 PC 꺼져 있어도 동작)

## 🚀 새 스킬 출시하는 법

1. 이 저장소를 clone 합니다
2. `skills/<스킬이름>/` 폴더를 만들고 소스/README를 넣습니다
3. commit + push

```bash
git clone https://github.com/delight0517/skill-inbox.git
cd skill-inbox
mkdir -p skills/my-new-skill
# ... 파일 넣기 ...
git add . && git commit -m "새 스킬: my-new-skill" && git push
```

→ 몇 분 내에 `https://github.com/delight0517/my-new-skill` 로 자동 출시됩니다 (README 개발자 소개·topics·homepage·Release 자동 포함).

## 🛠 자동화 시스템

| 워크플로우 | 일정 | 역할 |
|---|---|---|
| `skill-watcher` | 매일 09:00 / 21:00 (KST) | `skills/` 새 폴더 → GitHub 자동 출시 |
| `feedback-biweekly` | 매월 1일 / 15일 10:00 | 별점·이슈·피드백 수집 → 텔레그램 리포트 |

## ⚠️ 참고

- `skills/` 폴더만 출시 대상입니다. 루트의 자동화 파일(`.github/`, `scripts/`)은 출시되지 않습니다.
- 이미 GitHub에 있는 이름이면 스킵됩니다 (중복 방지).
- 민감/개인 폴더(harugirok, brainwire, secom 등)는 제외 목록에 있어 자동 출시되지 않습니다.

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
