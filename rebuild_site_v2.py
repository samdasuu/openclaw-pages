#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent
PAGES_JSON = REPO / "pages.json"

SLATE50 = "#f8fafc"
SLATE800 = "#1f2937"
SLATE500 = "#64748b"
BLUE600 = "#2563eb"
BORDER = "#e2e8f0"
CARD = "#ffffff"


def parse_title_and_desc(html_text: str):
    title = None
    desc = None
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.I | re.S)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(
        r"<meta[^>]+name=['\"]description['\"][^>]+content=['\"]([^'\"]+)['\"]",
        html_text,
        flags=re.I,
    )
    if m:
        desc = m.group(1).strip()
    return title, desc


def extract_body_inner(html_text: str):
    m = re.search(r"<body[^>]*>(.*)</body>", html_text, flags=re.I | re.S)
    if m:
        return m.group(1).strip()
    return html_text


def infer_date_from_filename(fname: str):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})__", fname)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return datetime.now().strftime("%Y-%m-%d")


def category_from_old(old):
    tags = old.get("tags") or []
    if any(t in tags for t in ["dev", "openclaw", "config", "telegram", "session"]):
        return "개발"
    if any(t in tags for t in ["logs", "travel", "itinerary", "singapore"]):
        return "분석"
    if any(t in tags for t in ["summary", "eopla", "startup", "marketing"]):
        return "분석"
    return "분석"


def sanitize_inner(html: str):
    html = re.sub(r"<!doctype.*", "", html, flags=re.I | re.S).strip()
    html = re.sub(r"<head.*?</head>", "", html, flags=re.I | re.S).strip()
    html = re.sub(r"</?html[^>]*>", "", html, flags=re.I).strip()
    html = re.sub(r"</?body[^>]*>", "", html, flags=re.I).strip()
    return html


def build_new_html(*, title: str, date: str, tags, summary_lines, body_inner: str, footer_repo: str):
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in (tags or []))
    summary_html = "".join(f"<p>{ln}</p>" for ln in summary_lines if ln.strip())
    if not summary_html:
        summary_html = "<p>요약을 준비 중입니다.</p>"

    return """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{TITLE}}</title>
  <meta name="description" content="{{DESCRIPTION}}" />
  <style>
    :root {
      --bg: {{SLATE50}};
      --card: {{CARD}};
      --fg: {{SLATE800}};
      --muted: {{SLATE500}};
      --border: {{BORDER}};
      --accent: {{BLUE600}};
      --maxw: 900px;
    }
    html,body { margin:0; padding:0; background:var(--bg); color:var(--fg); font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",Segoe UI,Roboto,Arial,sans-serif; line-height:1.65; }
    a { color: var(--accent); text-decoration:none; }
    a:hover { text-decoration:underline; }
    main { max-width: var(--maxw); margin: 24px auto; padding: 0 16px; }
    .card { background: var(--card); border:1px solid var(--border); border-radius: 14px; padding: 16px 18px; }
    header.card { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; }
    .back { display:inline-block; padding:8px 10px; border:1px solid var(--border); border-radius: 10px; background:#fff; font-size: 14px; }
    h1 { margin: 0 0 4px; font-size: 22px; }
    .meta { color: var(--muted); font-size: 13px; }
    .tags { margin-top: 10px; display:flex; gap:6px; flex-wrap:wrap; }
    .tag { border:1px solid var(--border); background:#fff; border-radius: 999px; padding:2px 9px; font-size: 12px; color: var(--muted); }

    .summary { margin-top: 14px; }
    .summary .card { border-left: 4px solid var(--accent); }
    .summary p { margin: 6px 0; }

    .content { margin-top: 14px; }
    .content h2 { margin: 22px 0 10px; padding-top: 14px; border-top:1px solid var(--border); font-size: 18px; }
    .content h3 { margin: 16px 0 8px; font-size: 15px; }

    .code { margin-top: 14px; }
    pre, code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
    pre { margin:0; background:#0b1020; color:#e5e7eb; border-radius: 12px; padding: 14px; overflow-x:auto; border:1px solid #111827; }

    footer.card { margin-top: 14px; color: var(--muted); font-size: 13px; }
  </style>
</head>
<body>
  <main>
    <header class="card">
      <div>
        <a class="back" href="./">← 목록으로</a>
      </div>
      <div style="flex:1">
        <h1>{{TITLE}}</h1>
        <div class="meta">작성일: {{DATE}}</div>
        <div class="tags">{{TAGS}}</div>
      </div>
    </header>

    <section class="summary">
      <div class="card">
        <strong>요약</strong>
        {{SUMMARY}}
      </div>
    </section>

    <section class="content">
      <div class="card">
        <h2>본문</h2>
        {{BODY}}
      </div>
    </section>

    <section class="code">
      <div class="card">
        <h2>Code / Data</h2>
        <pre><code><!-- 필요 시 프롬프트/명령/데이터를 여기에 추가 --></code></pre>
      </div>
    </section>

    <footer class="card">
      <div>Project: OpenClaw Pages</div>
      <div>Repo: <a href="{{REPO}}" target="_blank" rel="noreferrer">{{REPO}}</a></div>
    </footer>
  </main>
</body>
</html>
""".replace("{{TITLE}}", title) \
      .replace("{{DESCRIPTION}}", title) \
      .replace("{{DATE}}", date) \
      .replace("{{TAGS}}", tags_html) \
      .replace("{{SUMMARY}}", summary_html) \
      .replace("{{BODY}}", body_inner) \
      .replace("{{REPO}}", footer_repo) \
      .replace("{{SLATE50}}", SLATE50) \
      .replace("{{SLATE800}}", SLATE800) \
      .replace("{{SLATE500}}", SLATE500) \
      .replace("{{BLUE600}}", BLUE600) \
      .replace("{{BORDER}}", BORDER) \
      .replace("{{CARD}}", CARD)


def build_index_html(site, repo_url):
    return """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{SITE_TITLE}}</title>
  <meta name="description" content="{{SITE_SUBTITLE}}" />
  <style>
    :root { --fg:{{SLATE800}}; --muted:{{SLATE500}}; --bg:{{SLATE50}}; --card:{{CARD}}; --border:{{BORDER}}; --link:{{BLUE600}}; }
    html,body { margin:0; padding:0; background:var(--bg); color:var(--fg); font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",Segoe UI,Roboto,Arial,sans-serif; line-height:1.55; }
    main { max-width: 980px; margin: 24px auto; padding: 0 16px; }
    a { color:var(--link); text-decoration:none; }
    a:hover { text-decoration:underline; }
    header { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }
    h1 { margin:0 0 6px; font-size: 22px; }
    .sub { margin:0; color:var(--muted); }
    .toolbar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top: 14px; }
    .input { border:1px solid var(--border); border-radius:10px; padding:10px 12px; min-width:260px; font-size:0.95rem; background:#fff; }
    .pill { border:1px solid var(--border); background:#fff; padding:6px 10px; border-radius:999px; font-size:0.9rem; cursor:pointer; }
    .pill[aria-pressed="true"] { border-color:#93c5fd; background:#eff6ff; }
    .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:14px; margin-top:14px; }
    .card { border:1px solid var(--border); border-radius:12px; padding:14px 16px; background:var(--card); }
    .card h2 { margin:0 0 6px; font-size:1.05rem; }
    .card p { margin:0 0 10px; color:var(--muted); }
    .meta { color:var(--muted); font-size: 13px; }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1 id="siteTitle">{{SITE_TITLE}}</h1>
        <p class="sub" id="siteSubtitle">{{SITE_SUBTITLE}}</p>
      </div>
      <div class="meta" style="text-align:right;">
        <div>repo: <a id="repoLink" href="{{REPO}}">{{REPO}}</a></div>
        <div class="sub">base: <a id="baseLink" href="./">{{BASE}}</a></div>
      </div>
    </header>

    <div class="toolbar">
      <input class="input" id="q" placeholder="검색 (제목/요약/카테고리)" />
      <div id="catBar" style="display:flex; gap:8px; flex-wrap:wrap;"></div>
    </div>

    <div id="status" class="meta" style="margin-top:10px;"></div>
    <div class="grid" id="grid"></div>

    <script>
      async function boot() {
        const res = await fetch('./pages.json', {cache:'no-store'});
        const data = await res.json();
        const pages = data.pages || [];

        const q = document.getElementById('q');
        const grid = document.getElementById('grid');
        const status = document.getElementById('status');
        const catBar = document.getElementById('catBar');

        const cats = Array.from(new Set(pages.map(p => p.category).filter(Boolean)));
        const state = { cat: 'ALL', q: '' };

        function mkPill(label, value) {
          const b = document.createElement('button');
          b.className = 'pill';
          b.textContent = label;
          b.dataset.value = value;
          b.setAttribute('aria-pressed', value === state.cat ? 'true' : 'false');
          b.onclick = () => {
            state.cat = value;
            render();
            for (const el of catBar.querySelectorAll('button')) {
              el.setAttribute('aria-pressed', el.dataset.value === state.cat ? 'true' : 'false');
            }
          };
          return b;
        }

        catBar.appendChild(mkPill('ALL', 'ALL'));
        for (const c of cats) catBar.appendChild(mkPill(c, c));

        q.oninput = () => { state.q = q.value.trim().toLowerCase(); render(); };

        function render() {
          grid.innerHTML = '';
          let filtered = pages;
          if (state.cat !== 'ALL') filtered = filtered.filter(p => p.category === state.cat);
          if (state.q) {
            filtered = filtered.filter(p => {
              const hay = `${p.title||''} ${p.description||''} ${p.category||''} ${p.date||''} ${p.id||''}`.toLowerCase();
              return hay.includes(state.q);
            });
          }
          status.textContent = `${filtered.length} / ${pages.length} 보고서`;
          for (const p of filtered) {
            const card = document.createElement('div');
            card.className = 'card';
            const h2 = document.createElement('h2');
            const a = document.createElement('a');
            a.href = `./${p.href}`;
            a.textContent = p.title;
            h2.appendChild(a);
            const desc = document.createElement('p');
            desc.textContent = p.description || '';
            const meta = document.createElement('div');
            meta.className = 'meta';
            meta.textContent = `${p.category || ''} · ${p.date || ''} · ${p.id || ''}`;
            card.appendChild(h2);
            card.appendChild(desc);
            card.appendChild(meta);
            grid.appendChild(card);
          }
        }

        render();
      }
      boot();
    </script>
  </main>
</body>
</html>
""".replace("{{SITE_TITLE}}", site.get("title", "OpenClaw Reports")) \
      .replace("{{SITE_SUBTITLE}}", site.get("subtitle", "리포트 목록")) \
      .replace("{{REPO}}", site.get("repo", repo_url)) \
      .replace("{{BASE}}", site.get("baseUrl", "./")) \
      .replace("{{SLATE50}}", SLATE50) \
      .replace("{{SLATE800}}", SLATE800) \
      .replace("{{SLATE500}}", SLATE500) \
      .replace("{{BLUE600}}", BLUE600) \
      .replace("{{BORDER}}", BORDER) \
      .replace("{{CARD}}", CARD)


def main():
    data = json.loads(PAGES_JSON.read_text(encoding="utf-8"))
    site = data.get("site", {})
    repo_url = site.get("repo", "https://github.com/samdasuu/openclaw-pages")

    old_pages = data.get("pages", [])

    counters = {}
    new_pages = []

    for p in old_pages:
        href = p.get("href", "")
        fname = href.replace("./", "")
        if fname == "index.html" or not fname.endswith(".html"):
            continue
        html_path = REPO / fname
        if not html_path.exists():
            continue

        raw = html_path.read_text(encoding="utf-8", errors="ignore")
        title, desc_meta = parse_title_and_desc(raw)
        title = title or p.get("title") or fname

        date = infer_date_from_filename(fname)
        date_compact = date.replace("-", "")
        counters.setdefault(date_compact, 0)
        counters[date_compact] += 1
        rid = f"{date_compact}-{counters[date_compact]:02d}"

        category = category_from_old(p)

        description = p.get("desc") or p.get("description") or desc_meta or ""
        description = re.sub(r"\s+", " ", description).strip()
        if not description or description == "Published via OpenClaw":
            description = desc_meta or title

        tags = p.get("tags") or []
        summary_lines = [description]

        body_inner = sanitize_inner(extract_body_inner(raw))

        new_html = build_new_html(
            title=title,
            date=date,
            tags=tags,
            summary_lines=summary_lines,
            body_inner=body_inner,
            footer_repo=repo_url,
        )
        html_path.write_text(new_html, encoding="utf-8")

        new_pages.append(
            {
                "id": rid,
                "title": title,
                "description": description,
                "category": category,
                "date": date,
                "href": fname,
            }
        )

    (REPO / "index.html").write_text(build_index_html(site, repo_url), encoding="utf-8")

    out = {"site": site, "pages": new_pages}
    PAGES_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"rebuilt: pages={len(new_pages)}")


if __name__ == "__main__":
    main()
