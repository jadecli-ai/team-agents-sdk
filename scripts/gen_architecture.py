"""Generate ARCHITECTURE.html from codebase introspection.

depends_on:
  - semantic/*.yaml
  - src/**/*.py
  - app/**/*.ts, app/**/*.tsx
  - lib/**/*.ts
depended_by:
  - .github/workflows/architecture.yml
semver: patch

Scans all source files, extracts frontmatter dependency metadata,
traces imports, and emits an interactive HTML architecture diagram.

Usage:
    python scripts/gen_architecture.py              # write ARCHITECTURE.html
    python scripts/gen_architecture.py --check      # exit 1 if stale
    python scripts/gen_architecture.py --json       # dump JSON graph to stdout
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── File discovery ──────────────────────────────────────────────────

SCAN_PATTERNS = [
    "src/**/*.py",
    "app/**/*.ts",
    "app/**/*.tsx",
    "lib/**/*.ts",
    "semantic/*.yaml",
    "scripts/*.py",
    "tests/*.py",
    ".github/workflows/*.yml",
]

IGNORE = {
    "__pycache__",
    ".venv",
    "node_modules",
    ".next",
    "dist",
    ".pytest_cache",
}


def discover_files() -> list[Path]:
    files = []
    for pattern in SCAN_PATTERNS:
        for p in ROOT.glob(pattern):
            if any(part in IGNORE for part in p.parts):
                continue
            files.append(p.relative_to(ROOT))
    return sorted(set(files))


# ── Layer classification ────────────────────────────────────────────


def classify_layer(path: Path) -> str:
    s = str(path)
    if s.startswith("semantic/"):
        return "schema"
    if s.startswith("src/models/") or s.startswith("src/db/"):
        return "backend"
    if s.startswith("src/hooks/") or s.startswith("src/sync/"):
        return "middleware"
    if s.startswith("src/"):
        return "backend"
    if s.startswith("app/") or s.startswith("lib/"):
        return "frontend"
    if s.startswith("tests/"):
        return "test"
    if s.startswith("scripts/"):
        return "infra"
    if s.startswith(".github/"):
        return "ci"
    return "other"


LAYER_COLORS = {
    "schema": "#f59e0b",
    "backend": "#3b82f6",
    "middleware": "#8b5cf6",
    "frontend": "#10b981",
    "test": "#6b7280",
    "infra": "#ef4444",
    "ci": "#ec4899",
    "other": "#9ca3af",
}

LAYER_ORDER = ["schema", "backend", "middleware", "frontend", "test", "infra", "ci"]

# ── Dependency extraction ───────────────────────────────────────────

_PY_IMPORT = re.compile(r"^\s*(?:from|import)\s+(src\.\S+|lib\.\S+)", re.MULTILINE)
_TS_IMPORT = re.compile(r"""from\s+["'](@/|\.\.?/)([^"']+)["']""", re.MULTILINE)
_FRONTMATTER_DEPENDS = re.compile(r"depends_on:\s*\n((?:\s+-\s+.+\n)*)", re.MULTILINE)
_FRONTMATTER_DEPBY = re.compile(r"depended_by:\s*\n((?:\s+-\s+.+\n)*)", re.MULTILINE)
_FRONTMATTER_SEMVER = re.compile(r"semver:\s*(\w+)")
_FRONTMATTER_SCHEMA = re.compile(r"(?:schema|@schema):\s*(.+)")
_LIST_ITEM = re.compile(r"-\s+(.+)")


def _extract_list(match: re.Match | None) -> list[str]:
    if not match:
        return []
    return [m.group(1).strip() for m in _LIST_ITEM.finditer(match.group(1))]


def extract_metadata(path: Path) -> dict:
    """Extract dependency info from a file's frontmatter and imports."""
    full = ROOT / path
    try:
        content = full.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    meta: dict = {
        "path": str(path),
        "layer": classify_layer(path),
        "depends_on": [],
        "depended_by": [],
        "semver": None,
        "schema": None,
        "imports": [],
    }

    # Frontmatter
    meta["depends_on"] = _extract_list(_FRONTMATTER_DEPENDS.search(content))
    meta["depended_by"] = _extract_list(_FRONTMATTER_DEPBY.search(content))

    sv = _FRONTMATTER_SEMVER.search(content)
    if sv:
        meta["semver"] = sv.group(1)

    sc = _FRONTMATTER_SCHEMA.search(content)
    if sc:
        meta["schema"] = sc.group(1).strip()

    # Python imports
    if path.suffix == ".py":
        for m in _PY_IMPORT.finditer(content):
            mod = m.group(1).replace(".", "/")
            # src.models.task -> src/models/task
            candidate = mod + ".py"
            if (ROOT / candidate).exists():
                meta["imports"].append(candidate)

    # TypeScript imports
    if path.suffix in (".ts", ".tsx"):
        for m in _TS_IMPORT.finditer(content):
            prefix, rest = m.group(1), m.group(2)
            if prefix == "@/":
                candidate = rest
            else:
                candidate = str(
                    (path.parent / (prefix + rest)).resolve().relative_to(ROOT.resolve())
                )
            # try with extensions
            for ext in ("", ".ts", ".tsx", "/index.ts"):
                if (ROOT / (candidate + ext)).exists():
                    meta["imports"].append(candidate + ext)
                    break

    return meta


# ── Graph assembly ──────────────────────────────────────────────────


def build_graph() -> dict:
    files = discover_files()
    nodes = []
    edges = []
    seen_edges = set()

    for f in files:
        meta = extract_metadata(f)
        if not meta:
            continue
        nodes.append(
            {
                "id": str(f),
                "layer": meta["layer"],
                "semver": meta.get("semver"),
                "schema": meta.get("schema"),
            }
        )

        # Edges from depends_on
        for dep in meta.get("depends_on", []):
            key = (dep, str(f))
            if key not in seen_edges:
                edges.append({"source": dep, "target": str(f), "type": "depends_on"})
                seen_edges.add(key)

        # Edges from imports
        for imp in meta.get("imports", []):
            key = (imp, str(f))
            if key not in seen_edges:
                edges.append({"source": imp, "target": str(f), "type": "import"})
                seen_edges.add(key)

    # External services
    services = [
        {"id": "Neon Postgres", "layer": "external"},
        {"id": "Vercel", "layer": "external"},
        {"id": "GitHub API", "layer": "external"},
        {"id": "Claude Agent SDK", "layer": "external"},
        {"id": "MLflow", "layer": "external"},
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": _get_version(),
        "org": "jadecli-ai",
        "repo": "team-agents-sdk",
        "nodes": nodes,
        "services": services,
        "edges": edges,
        "layers": {k: v for k, v in LAYER_COLORS.items()},
        "layer_order": LAYER_ORDER,
        "stats": {
            "total_files": len(nodes),
            "total_edges": len(edges),
            "by_layer": {
                layer: sum(1 for n in nodes if n["layer"] == layer) for layer in LAYER_ORDER
            },
        },
    }


def _get_version() -> str:
    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    return "0.0.0"


# ── HTML generation ─────────────────────────────────────────────────


def generate_html(graph: dict) -> str:
    graph_json = json.dumps(graph, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Architecture — jadecli-ai/team-agents-sdk</title>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8;
    --schema: #f59e0b; --backend: #3b82f6; --middleware: #8b5cf6;
    --frontend: #10b981; --test: #6b7280; --infra: #ef4444;
    --ci: #ec4899; --external: #06b6d4;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'SF Mono', 'Fira Code', monospace; background: var(--bg); color: var(--text); }}
  .header {{
    padding: 1.5rem 2rem; border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }}
  .header h1 {{ font-size: 1.1rem; font-weight: 600; }}
  .header .meta {{ color: var(--muted); font-size: 0.75rem; }}
  .controls {{
    padding: 1rem 2rem; border-bottom: 1px solid var(--border);
    display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center;
  }}
  .controls button {{
    padding: 0.35rem 0.75rem; border: 1px solid var(--border); border-radius: 4px;
    background: var(--surface); color: var(--text); cursor: pointer;
    font-family: inherit; font-size: 0.75rem; transition: all 0.15s;
  }}
  .controls button:hover {{ border-color: var(--text); }}
  .controls button.active {{ border-color: currentColor; font-weight: 700; }}
  .controls .sep {{ width: 1px; height: 1.5rem; background: var(--border); margin: 0 0.5rem; }}
  .main {{ display: flex; height: calc(100vh - 120px); }}
  .sidebar {{
    width: 280px; border-right: 1px solid var(--border); overflow-y: auto; padding: 1rem;
    flex-shrink: 0;
  }}
  .sidebar h3 {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin: 1rem 0 0.5rem; }}
  .sidebar .file {{
    padding: 0.3rem 0.5rem; border-radius: 3px; cursor: pointer;
    font-size: 0.72rem; display: flex; align-items: center; gap: 0.4rem;
    transition: background 0.1s;
  }}
  .sidebar .file:hover {{ background: var(--surface); }}
  .sidebar .file.selected {{ background: var(--surface); font-weight: 700; }}
  .sidebar .dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
  .canvas {{ flex: 1; position: relative; overflow: hidden; }}
  svg {{ width: 100%; height: 100%; }}
  .node {{ cursor: pointer; transition: opacity 0.2s; }}
  .node rect {{ rx: 4; stroke-width: 1.5; transition: all 0.15s; }}
  .node:hover rect {{ stroke-width: 2.5; filter: brightness(1.2); }}
  .node text {{ fill: var(--text); font-size: 10px; font-family: inherit; pointer-events: none; }}
  .edge {{ stroke-width: 1; opacity: 0.3; fill: none; transition: opacity 0.2s; }}
  .edge.highlighted {{ opacity: 0.9; stroke-width: 2; }}
  .detail {{
    position: absolute; top: 1rem; right: 1rem; width: 320px; background: var(--surface);
    border: 1px solid var(--border); border-radius: 6px; padding: 1rem;
    font-size: 0.75rem; display: none; z-index: 10;
  }}
  .detail.visible {{ display: block; }}
  .detail h4 {{ font-size: 0.85rem; margin-bottom: 0.5rem; }}
  .detail .label {{ color: var(--muted); font-size: 0.65rem; text-transform: uppercase; margin-top: 0.75rem; }}
  .detail .dep {{ padding: 0.15rem 0; cursor: pointer; }}
  .detail .dep:hover {{ text-decoration: underline; }}
  .detail .badge {{
    display: inline-block; padding: 0.1rem 0.4rem; border-radius: 3px;
    font-size: 0.65rem; font-weight: 600;
  }}
  .stats {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.5rem; padding: 1rem 2rem; border-bottom: 1px solid var(--border);
  }}
  .stat {{ text-align: center; }}
  .stat .num {{ font-size: 1.5rem; font-weight: 700; }}
  .stat .lbl {{ font-size: 0.65rem; color: var(--muted); text-transform: uppercase; }}
  .legend {{ display: flex; gap: 1rem; padding: 0 2rem; align-items: center; }}
  .legend .item {{ display: flex; align-items: center; gap: 0.3rem; font-size: 0.7rem; }}
  .legend .swatch {{ width: 10px; height: 10px; border-radius: 2px; }}
  .org-context {{
    padding: 0.75rem 2rem; border-bottom: 1px solid var(--border);
    font-size: 0.72rem; color: var(--muted);
    display: flex; gap: 2rem; align-items: center;
  }}
  .org-context .repo {{ color: var(--frontend); font-weight: 600; }}
</style>
</head>
<body>

<div class="header">
  <h1>jadecli-ai / team-agents-sdk</h1>
  <div class="meta" id="meta"></div>
</div>

<div class="org-context">
  <span>Org: <strong>jadecli-ai</strong></span>
  <span class="repo">team-agents-sdk</span>
  <span>Semantic YAML &rarr; Pydantic + Drizzle &rarr; Neon Postgres &rarr; Vercel Dashboard</span>
</div>

<div class="stats" id="stats"></div>

<div class="controls" id="controls">
  <button class="active" data-layer="all">All</button>
  <div class="sep"></div>
</div>

<div class="main">
  <div class="sidebar" id="sidebar"></div>
  <div class="canvas">
    <svg id="graph"></svg>
    <div class="detail" id="detail"></div>
  </div>
</div>

<script>
const DATA = {graph_json};

// ── Render metadata ───────────────────────────────────────────────
document.getElementById('meta').textContent =
  `v${{DATA.version}} | Generated ${{new Date(DATA.generated_at).toLocaleDateString()}} | ${{DATA.stats.total_files}} files, ${{DATA.stats.total_edges}} edges`;

// ── Stats ─────────────────────────────────────────────────────────
const statsEl = document.getElementById('stats');
for (const [layer, count] of Object.entries(DATA.stats.by_layer)) {{
  if (count === 0) continue;
  const div = document.createElement('div');
  div.className = 'stat';
  div.innerHTML = `<div class="num" style="color: ${{DATA.layers[layer]}}">${{count}}</div><div class="lbl">${{layer}}</div>`;
  statsEl.appendChild(div);
}}

// ── Controls (layer filters) ──────────────────────────────────────
const controlsEl = document.getElementById('controls');
for (const layer of DATA.layer_order) {{
  if (!DATA.stats.by_layer[layer]) continue;
  const btn = document.createElement('button');
  btn.dataset.layer = layer;
  btn.style.color = DATA.layers[layer];
  btn.textContent = layer;
  btn.onclick = () => filterLayer(layer);
  controlsEl.appendChild(btn);
}}

let activeLayer = 'all';
function filterLayer(layer) {{
  activeLayer = activeLayer === layer ? 'all' : layer;
  controlsEl.querySelectorAll('button').forEach(b => {{
    b.classList.toggle('active', b.dataset.layer === activeLayer);
  }});
  renderGraph();
  renderSidebar();
}}

// ── Sidebar ───────────────────────────────────────────────────────
const sidebarEl = document.getElementById('sidebar');
let selectedNode = null;

function renderSidebar() {{
  sidebarEl.innerHTML = '';
  const grouped = {{}};
  for (const n of DATA.nodes) {{
    if (activeLayer !== 'all' && n.layer !== activeLayer) continue;
    (grouped[n.layer] = grouped[n.layer] || []).push(n);
  }}
  for (const layer of DATA.layer_order) {{
    if (!grouped[layer]) continue;
    const h3 = document.createElement('h3');
    h3.textContent = `${{layer}} (${{grouped[layer].length}})`;
    h3.style.color = DATA.layers[layer];
    sidebarEl.appendChild(h3);
    for (const n of grouped[layer]) {{
      const div = document.createElement('div');
      div.className = 'file' + (selectedNode === n.id ? ' selected' : '');
      div.innerHTML = `<span class="dot" style="background:${{DATA.layers[n.layer]}}"></span>${{n.id.split('/').pop()}}`;
      div.title = n.id;
      div.onclick = () => selectNode(n.id);
      sidebarEl.appendChild(div);
    }}
  }}
}}

// ── Detail panel ──────────────────────────────────────────────────
const detailEl = document.getElementById('detail');

function selectNode(id) {{
  selectedNode = selectedNode === id ? null : id;
  renderSidebar();
  renderGraph();
  if (!selectedNode) {{
    detailEl.classList.remove('visible');
    return;
  }}
  const node = DATA.nodes.find(n => n.id === id);
  if (!node) return;

  const incoming = DATA.edges.filter(e => e.target === id).map(e => e.source);
  const outgoing = DATA.edges.filter(e => e.source === id).map(e => e.target);

  let html = `<h4>${{id}}</h4>`;
  html += `<span class="badge" style="background:${{DATA.layers[node.layer]}}33;color:${{DATA.layers[node.layer]}}">${{node.layer}}</span>`;
  if (node.semver) html += ` <span class="badge" style="background:#33415533;color:var(--muted)">${{node.semver}}</span>`;
  if (node.schema) html += `<div class="label">Schema</div><div>${{node.schema}}</div>`;
  if (incoming.length) {{
    html += `<div class="label">Depends on (${{incoming.length}})</div>`;
    incoming.forEach(d => html += `<div class="dep" onclick="selectNode('${{d}}')">${{d}}</div>`);
  }}
  if (outgoing.length) {{
    html += `<div class="label">Depended by (${{outgoing.length}})</div>`;
    outgoing.forEach(d => html += `<div class="dep" onclick="selectNode('${{d}}')">${{d}}</div>`);
  }}
  detailEl.innerHTML = html;
  detailEl.classList.add('visible');
}}

// ── Graph rendering (force-directed) ──────────────────────────────
const svg = document.getElementById('graph');
const ns = 'http://www.w3.org/2000/svg';

function renderGraph() {{
  svg.innerHTML = '';
  const rect = svg.getBoundingClientRect();
  const W = rect.width, H = rect.height;

  const visibleNodes = DATA.nodes.filter(n =>
    activeLayer === 'all' || n.layer === activeLayer
  );
  const visibleIds = new Set(visibleNodes.map(n => n.id));
  const visibleEdges = DATA.edges.filter(e =>
    visibleIds.has(e.source) && visibleIds.has(e.target)
  );

  // Layout: group by layer in horizontal bands
  const layerNodes = {{}};
  visibleNodes.forEach(n => (layerNodes[n.layer] = layerNodes[n.layer] || []).push(n));

  const positions = {{}};
  const activeLayers = DATA.layer_order.filter(l => layerNodes[l]);
  const bandH = H / (activeLayers.length + 1);

  activeLayers.forEach((layer, li) => {{
    const nodes = layerNodes[layer];
    const bandW = W / (nodes.length + 1);
    nodes.forEach((n, ni) => {{
      positions[n.id] = {{
        x: bandW * (ni + 1),
        y: bandH * (li + 1),
      }};
    }});
  }});

  // Add service nodes along the right
  DATA.services.forEach((s, i) => {{
    positions[s.id] = {{ x: W - 80, y: 60 + i * 50 }};
  }});

  // Draw edges
  const edgeGroup = document.createElementNS(ns, 'g');
  visibleEdges.forEach(e => {{
    const s = positions[e.source], t = positions[e.target];
    if (!s || !t) return;
    const line = document.createElementNS(ns, 'line');
    line.setAttribute('x1', s.x); line.setAttribute('y1', s.y);
    line.setAttribute('x2', t.x); line.setAttribute('y2', t.y);
    line.setAttribute('class', 'edge');
    line.setAttribute('stroke', DATA.layers[visibleNodes.find(n => n.id === e.source)?.layer] || '#666');
    line.dataset.source = e.source;
    line.dataset.target = e.target;
    if (selectedNode && (e.source === selectedNode || e.target === selectedNode)) {{
      line.classList.add('highlighted');
    }}
    edgeGroup.appendChild(line);
  }});
  svg.appendChild(edgeGroup);

  // Draw nodes
  const nodeGroup = document.createElementNS(ns, 'g');
  visibleNodes.forEach(n => {{
    const pos = positions[n.id];
    if (!pos) return;
    const g = document.createElementNS(ns, 'g');
    g.setAttribute('class', 'node');
    g.setAttribute('transform', `translate(${{pos.x - 60}},${{pos.y - 12}})`);
    g.onclick = () => selectNode(n.id);

    const r = document.createElementNS(ns, 'rect');
    const label = n.id.split('/').pop();
    const w = Math.max(label.length * 6.5 + 16, 80);
    r.setAttribute('width', w); r.setAttribute('height', 24);
    r.setAttribute('fill', DATA.layers[n.layer] + '22');
    r.setAttribute('stroke', DATA.layers[n.layer]);
    if (selectedNode === n.id) {{
      r.setAttribute('stroke-width', '3');
      r.setAttribute('fill', DATA.layers[n.layer] + '44');
    }}
    g.appendChild(r);

    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', 8); t.setAttribute('y', 16);
    t.textContent = label;
    g.appendChild(t);

    nodeGroup.appendChild(g);
  }});
  svg.appendChild(nodeGroup);

  // Draw service nodes
  DATA.services.forEach(s => {{
    const pos = positions[s.id];
    if (!pos) return;
    const g = document.createElementNS(ns, 'g');
    g.setAttribute('class', 'node');
    g.setAttribute('transform', `translate(${{pos.x - 50}},${{pos.y - 12}})`);

    const r = document.createElementNS(ns, 'rect');
    r.setAttribute('width', 100); r.setAttribute('height', 24);
    r.setAttribute('fill', '#06b6d422'); r.setAttribute('stroke', '#06b6d4');
    r.setAttribute('stroke-dasharray', '4 2');
    g.appendChild(r);

    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', 8); t.setAttribute('y', 16);
    t.setAttribute('fill', '#06b6d4');
    t.textContent = s.id;
    g.appendChild(t);

    nodeGroup.appendChild(g);
  }});
}}

// ── Init ──────────────────────────────────────────────────────────
renderSidebar();
renderGraph();
window.addEventListener('resize', renderGraph);
</script>
</body>
</html>"""


# ── CLI ─────────────────────────────────────────────────────────────


def main():
    graph = build_graph()

    if "--json" in sys.argv:
        print(json.dumps(graph, indent=2))
        return

    html = generate_html(graph)
    out = ROOT / "ARCHITECTURE.html"

    if "--check" in sys.argv:
        if not out.exists():
            print("ARCHITECTURE.html missing. Run: make architecture")
            sys.exit(1)
        existing = out.read_text()
        # Compare graph data, stripping generated_at timestamp
        _ts_re = re.compile(r'"generated_at":\s*"[^"]+"')
        existing_data = (
            _ts_re.sub("", existing.split("const DATA = ")[1].split(";\n")[0])
            if "const DATA = " in existing
            else ""
        )
        new_data = _ts_re.sub("", html.split("const DATA = ")[1].split(";\n")[0])
        if existing_data != new_data:
            print("ARCHITECTURE.html is stale. Run: make architecture")
            sys.exit(1)
        print("ARCHITECTURE.html is up to date.")
        return

    out.write_text(html)
    print(
        f"Generated {out} ({graph['stats']['total_files']} files, {graph['stats']['total_edges']} edges)"
    )


if __name__ == "__main__":
    main()
