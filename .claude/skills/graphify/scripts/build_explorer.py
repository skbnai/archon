#!/usr/bin/env python3
"""
Generate _meta/knowledge-graph-explorer.html from _meta/graph.json.

Updates since v1:
- Tool/technology nodes (node_type="tool") shown as diamonds with a fixed
  amber colour, separate from the domain-colour page nodes.
- mentions edges (page → tool) shown as dashed cyan lines with a toggle.
- part_of edges (page → sidebar category) shown with a soft green toggle.
- Headline stat updated to include tool count and mentions count.
- Legend updated.

Usage:
    python build_explorer.py [--graph _meta/graph.json] [--out _meta/knowledge-graph-explorer.html]
"""
import argparse
import json
import sys
import os

TEMPLATE_BEFORE_DATA = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Archon — Knowledge Graph Explorer</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
  :root {
    --bg: #0f1115; --panel: #171a21; --border: #262b36; --text: #e6e8ec;
    --muted: #8b93a7; --accent: #5b8cff; --dup: #ff5c72; --overlap: #ffb648;
    --related: #4fd1c5; --link: #6b7280; --mention: #c084fc; --tool: #f59e0b;
  }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); overflow: hidden; }
  #app { display: flex; height: 100vh; }
  #sidebar { width: 300px; min-width: 300px; background: var(--panel); border-right: 1px solid var(--border);
             padding: 16px; overflow-y: auto; }
  #sidebar h1 { font-size: 15px; margin: 0 0 4px; }
  #sidebar .sub { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
  label { display: block; font-size: 12px; color: var(--muted); margin: 14px 0 4px; }
  input[type=text] { width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--border);
                      background: #0c0e12; color: var(--text); font-size: 13px; }
  input[type=range] { width: 100%; }
  select { width: 100%; padding: 6px; border-radius: 6px; border: 1px solid var(--border);
           background: #0c0e12; color: var(--text); font-size: 13px; }
  .legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; margin: 4px 0; color: var(--muted); }
  .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  .diamond { width: 10px; height: 10px; transform: rotate(45deg); display: inline-block; background: var(--tool); }
  .stat { font-size: 12px; color: var(--muted); margin-top: 2px; }
  .stat b { color: var(--text); }
  #results { margin-top: 10px; max-height: 220px; overflow-y: auto; border-top: 1px solid var(--border); padding-top: 8px; }
  .result-item { font-size: 12px; padding: 5px 6px; border-radius: 4px; cursor: pointer; color: var(--text); }
  .result-item:hover { background: #202634; }
  .result-item .rt { color: var(--muted); font-size: 11px; }
  #main { flex: 1; position: relative; }
  svg { width: 100%; height: 100%; display: block; }
  #tooltip { position: absolute; pointer-events: none; background: #0c0e12; border: 1px solid var(--border);
             border-radius: 8px; padding: 10px 12px; font-size: 12px; max-width: 340px; display: none; z-index: 10; }
  #tooltip .tt-title { font-weight: 600; margin-bottom: 4px; }
  #tooltip .tt-meta { color: var(--muted); }
  .toggle-row { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); margin: 6px 0; }
  a.node-link { color: var(--accent); }
  #reset { margin-top: 10px; width: 100%; padding: 7px; border-radius: 6px; border: 1px solid var(--border);
           background: #202634; color: var(--text); font-size: 12px; cursor: pointer; }
  #reset:hover { background: #262c3a; }
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <h1>Archon — Knowledge Graph Explorer</h1>
    <div class="sub" id="headline">loading…</div>

    <label>Search pages, tools, or tags</label>
    <input type="text" id="search" placeholder="e.g. langgraph, mcp, kubernetes…">
    <div id="results"></div>

    <label>Min similarity for "similar_to" edges: <span id="simVal">0.6</span></label>
    <input type="range" id="simSlider" min="0.35" max="1" step="0.01" value="0.6">

    <label>Edge visibility</label>
    <div class="toggle-row"><input type="checkbox" id="toggleLinks"> Show hyperlink edges</div>
    <div class="toggle-row"><input type="checkbox" id="toggleMentions" checked> Show tool-mention edges</div>
    <div class="toggle-row"><input type="checkbox" id="toggleIsolated" checked> Hide isolated nodes</div>

    <label>Filter by domain</label>
    <select id="domainFilter"><option value="">— all domains —</option></select>

    <label>Filter by tool category</label>
    <select id="toolCatFilter"><option value="">— all tools —</option></select>

    <label>Stats</label>
    <div class="stat" id="statNodes">–</div>
    <div class="stat" id="statEdges">–</div>

    <label>Legend</label>
    <div class="legend-item"><span class="diamond"></span> Technology / Tool node</div>
    <div class="legend-item"><span class="dot" style="background:var(--related)"></span> Similarity edge</div>
    <div class="legend-item"><span class="dot" style="background:var(--link)"></span> Hyperlink edge</div>
    <div class="legend-item"><span class="dot" style="background:var(--mention)"></span> Tool-mention edge</div>
    <div class="legend-item"><span class="dot" style="background:var(--dup)"></span> Near-duplicate</div>
    <div class="legend-item"><span class="dot" style="background:var(--overlap)"></span> Heavy overlap</div>

    <button id="reset">Reset view</button>
  </div>
  <div id="main">
    <svg></svg>
    <div id="tooltip"></div>
  </div>
</div>
<script>
"""

TEMPLATE_AFTER_DATA = r"""
const domainColor = d3.scaleOrdinal(d3.schemeTableau10);
const domains = [...new Set(DATA.nodes.filter(n => n.node_type !== 'tool').map(n => n.domain))].sort();
domainColor.domain(domains);

const domainFilterEl = document.getElementById('domainFilter');
domains.forEach(d => {
  const opt = document.createElement('option');
  opt.value = d; opt.textContent = d;
  domainFilterEl.appendChild(opt);
});

const toolCategories = [...new Set(DATA.nodes.filter(n => n.node_type === 'tool').map(n => n.category))].sort();
const toolCatFilterEl = document.getElementById('toolCatFilter');
toolCategories.forEach(c => {
  const opt = document.createElement('option');
  opt.value = c; opt.textContent = c;
  toolCatFilterEl.appendChild(opt);
});

const pageCount = DATA.nodes.filter(n => n.node_type !== 'tool').length;
const toolCount = DATA.nodes.filter(n => n.node_type === 'tool').length;
const mentionCount = DATA.edges.filter(e => e.ty === 'mentions').length;
document.getElementById('headline').textContent =
  `${pageCount} pages · ${toolCount} tools · ${DATA.edges.filter(e=>e.ty==='similar_to').length} similarity · ${mentionCount} tool-mentions`;

const svg = d3.select('svg');
const g = svg.append('g');
const linkLayer = g.append('g');
const nodeLayer = g.append('g');
const labelLayer = g.append('g');

const zoom = d3.zoom().scaleExtent([0.1, 6]).on('zoom', (ev) => g.attr('transform', ev.transform));
svg.call(zoom);

const nodeById = new Map(DATA.nodes.map(n => [n.id, n]));
let simulation;
let currentNodes = [], currentLinks = [];

function edgeColor(e) {
  if (e.ty === 'mentions') return getComputedStyle(document.documentElement).getPropertyValue('--mention');
  if (e.ty === 'links_to') return getComputedStyle(document.documentElement).getPropertyValue('--link');
  if (e.tier === 'near_duplicate') return getComputedStyle(document.documentElement).getPropertyValue('--dup');
  if (e.tier === 'heavy_overlap') return getComputedStyle(document.documentElement).getPropertyValue('--overlap');
  return getComputedStyle(document.documentElement).getPropertyValue('--related');
}

function nodeColor(n) {
  if (n.node_type === 'tool') return getComputedStyle(document.documentElement).getPropertyValue('--tool');
  return domainColor(n.domain);
}

function computeGraph() {
  const minSim = parseFloat(document.getElementById('simSlider').value);
  const showLinks = document.getElementById('toggleLinks').checked;
  const showMentions = document.getElementById('toggleMentions').checked;
  const hideIsolated = document.getElementById('toggleIsolated').checked;
  const domainF = domainFilterEl.value;
  const toolCatF = toolCatFilterEl.value;

  let edges = DATA.edges.filter(e => {
    if (e.ty === 'similar_to' && e.w < minSim) return false;
    if (e.ty === 'links_to' && !showLinks) return false;
    if (e.ty === 'mentions' && !showMentions) return false;
    return true;
  });

  const connected = new Set();
  edges.forEach(e => { connected.add(e.s); connected.add(e.t); });

  let nodes = DATA.nodes.filter(n => {
    if (hideIsolated && !connected.has(n.id)) return false;
    if (domainF && n.domain !== domainF) return false;
    if (toolCatF && n.node_type === 'tool' && n.category !== toolCatF) return false;
    return true;
  });
  const nodeIds = new Set(nodes.map(n => n.id));
  edges = edges.filter(e => nodeIds.has(e.s) && nodeIds.has(e.t));

  document.getElementById('statNodes').innerHTML = `<b>${nodes.length}</b> nodes shown`;
  document.getElementById('statEdges').innerHTML = `<b>${edges.length}</b> edges shown`;

  return { nodes, edges };
}

function render() {
  const { nodes, edges } = computeGraph();
  currentNodes = nodes.map(n => Object.assign({}, nodeById.get(n.id) || n));
  const nodeMap = new Map(currentNodes.map(n => [n.id, n]));
  currentLinks = edges.map(e => ({ source: nodeMap.get(e.s), target: nodeMap.get(e.t), ty: e.ty, w: e.w || 0, tier: e.tier }));

  if (simulation) simulation.stop();

  const link = linkLayer.selectAll('line').data(currentLinks, (d,i) => i);
  link.exit().remove();
  const linkEnter = link.enter().append('line')
    .attr('stroke-width', d => {
      if (d.ty === 'mentions') return 1;
      if (d.ty === 'links_to') return 1;
      return 1 + d.w * 3;
    })
    .attr('stroke', d => edgeColor(d))
    .attr('stroke-opacity', d => {
      if (d.ty === 'mentions') return 0.35;
      if (d.ty === 'links_to') return 0.25;
      return 0.55;
    })
    .attr('stroke-dasharray', d => d.ty === 'mentions' ? '3,3' : null);
  const linkMerged = linkEnter.merge(link);

  // Tool nodes rendered as diamonds (rotated squares), page nodes as circles
  const toolNodes = currentNodes.filter(n => n.node_type === 'tool');
  const pageNodes = currentNodes.filter(n => n.node_type !== 'tool');

  // Page nodes (circles)
  const node = nodeLayer.selectAll('circle.page-node').data(pageNodes, d => d.id);
  node.exit().remove();
  const radius = d => Math.max(4, Math.min(16, 3 + Math.sqrt(d.wc || 100) / 12));
  const nodeEnter = node.enter().append('circle')
    .attr('class', 'page-node')
    .attr('r', radius)
    .attr('fill', d => nodeColor(d))
    .attr('stroke', '#0c0e12').attr('stroke-width', 1)
    .call(d3.drag()
      .on('start', (ev, d) => { if (!ev.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => { if (!ev.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('mouseenter', showTooltip)
    .on('mousemove', moveTooltip)
    .on('mouseleave', hideTooltip)
    .on('click', (ev, d) => focusNode(d));
  const nodeMerged = nodeEnter.merge(node);

  // Tool nodes (diamonds)
  const toolSize = 7;
  const tnode = nodeLayer.selectAll('rect.tool-node').data(toolNodes, d => d.id);
  tnode.exit().remove();
  const tnodeEnter = tnode.enter().append('rect')
    .attr('class', 'tool-node')
    .attr('width', toolSize * 2).attr('height', toolSize * 2)
    .attr('transform', d => `rotate(45,${d.x||0},${d.y||0})`)
    .attr('fill', 'var(--tool)')
    .attr('stroke', '#0c0e12').attr('stroke-width', 1)
    .call(d3.drag()
      .on('start', (ev, d) => { if (!ev.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => { if (!ev.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('mouseenter', showTooltip)
    .on('mousemove', moveTooltip)
    .on('mouseleave', hideTooltip)
    .on('click', (ev, d) => focusNode(d));
  const tnodeMerged = tnodeEnter.merge(tnode);

  // Labels for large pages
  const label = labelLayer.selectAll('text').data(currentNodes.filter(n => (n.wc||0) > 6000 || n.node_type === 'tool'), d => d.id);
  label.exit().remove();
  const labelEnter = label.enter().append('text')
    .attr('font-size', d => d.node_type === 'tool' ? 8 : 9)
    .attr('fill', d => d.node_type === 'tool' ? '#fcd34d' : '#c7cbd6')
    .attr('pointer-events', 'none')
    .attr('dx', 8).attr('dy', 3)
    .text(d => d.node_type === 'tool' ? d.title : d.title.slice(0, 28));
  const labelMerged = labelEnter.merge(label);

  simulation = d3.forceSimulation(currentNodes)
    .force('link', d3.forceLink(currentLinks).id(d => d.id)
      .distance(d => {
        if (d.ty === 'mentions') return 60;
        if (d.ty === 'part_of') return 50;
        return 40 + (1 - (d.w||0)) * 80;
      })
      .strength(d => d.ty === 'mentions' ? 0.1 : d.ty === 'part_of' ? 0.08 : 0.25))
    .force('charge', d3.forceManyBody().strength(d => d.node_type === 'tool' ? -200 : -90))
    .force('center', d3.forceCenter(0, 0))
    .force('collide', d3.forceCollide().radius(d => d.node_type === 'tool' ? 14 : radius(d) + 3))
    .on('tick', () => {
      linkMerged.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
                .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
      nodeMerged.attr('cx', d=>d.x).attr('cy', d=>d.y);
      tnodeMerged.attr('x', d => (d.x||0) - toolSize).attr('y', d => (d.y||0) - toolSize)
                 .attr('transform', d => `rotate(45,${d.x||0},${d.y||0})`);
      labelMerged.attr('x', d=>d.x).attr('y', d=>d.y);
    });
}

function showTooltip(ev, d) {
  const tt = document.getElementById('tooltip');
  tt.style.display = 'block';
  if (d.node_type === 'tool') {
    tt.innerHTML = `<div class="tt-title">🔧 ${d.title}</div>
      <div class="tt-meta">category: ${d.category}<br>${d.description || ''}</div>`;
  } else {
    tt.innerHTML = `<div class="tt-title">${d.title}</div>
      <div class="tt-meta">${d.id}<br>domain: ${d.domain} · type: ${d.doc_type} · ${d.wc} words${d.status ? ' · ' + d.status : ''}<br>
      tags: ${(d.tags||[]).join(', ') || '–'}${d.cat ? '<br>nav: '+d.cat : ''}</div>`;
  }
  moveTooltip(ev);
}
function moveTooltip(ev) {
  const tt = document.getElementById('tooltip');
  tt.style.left = (ev.clientX + 16) + 'px';
  tt.style.top = (ev.clientY + 12) + 'px';
}
function hideTooltip() { document.getElementById('tooltip').style.display = 'none'; }

function focusNode(d) {
  document.getElementById('search').value = d.title;
  runSearch(d.title, d.id);
}

function runSearch(query, exactId) {
  const results = document.getElementById('results');
  results.innerHTML = '';
  if (!query) return;
  const q = query.toLowerCase();
  const matches = DATA.nodes.filter(n =>
    n.id === exactId ||
    n.title.toLowerCase().includes(q) ||
    (n.tags||[]).some(t => t.toLowerCase().includes(q)) ||
    (n.aliases||[]).some(a => a.toLowerCase().includes(q))
  ).slice(0, 30);
  matches.forEach(m => {
    const div = document.createElement('div');
    div.className = 'result-item';
    const prefix = m.node_type === 'tool' ? '🔧 ' : '';
    div.innerHTML = `${prefix}${m.title}<div class="rt">${m.id} · ${m.node_type === 'tool' ? m.category : m.domain}</div>`;
    div.onclick = () => {
      domainFilterEl.value = '';
      document.getElementById('toggleIsolated').checked = false;
      render();
      setTimeout(() => {
        const el = currentNodes.find(n => n.id === m.id);
        if (el) {
          const svgNode = svg.node();
          const t = d3.zoomIdentity.translate(svgNode.clientWidth/2 - el.x, svgNode.clientHeight/2 - el.y).scale(1.4);
          svg.transition().duration(500).call(zoom.transform, t);
        }
      }, 300);
    };
    results.appendChild(div);
  });
  if (!matches.length) results.innerHTML = '<div class="result-item">No matches.</div>';
}

document.getElementById('search').addEventListener('input', (e) => runSearch(e.target.value));
document.getElementById('simSlider').addEventListener('input', (e) => {
  document.getElementById('simVal').textContent = e.target.value;
  render();
});
document.getElementById('toggleLinks').addEventListener('change', render);
document.getElementById('toggleMentions').addEventListener('change', render);
document.getElementById('toggleIsolated').addEventListener('change', render);
domainFilterEl.addEventListener('change', render);
toolCatFilterEl.addEventListener('change', render);
document.getElementById('reset').addEventListener('click', () => {
  document.getElementById('search').value = '';
  document.getElementById('simSlider').value = 0.6;
  document.getElementById('simVal').textContent = '0.6';
  document.getElementById('toggleLinks').checked = false;
  document.getElementById('toggleMentions').checked = true;
  document.getElementById('toggleIsolated').checked = true;
  domainFilterEl.value = '';
  toolCatFilterEl.value = '';
  document.getElementById('results').innerHTML = '';
  svg.transition().duration(400).call(zoom.transform, d3.zoomIdentity);
  render();
});

function resize() {
  const rect = document.getElementById('main').getBoundingClientRect();
  svg.attr('viewBox', [-rect.width/2, -rect.height/2, rect.width, rect.height]);
}
window.addEventListener('resize', resize);
resize();
render();
</script>
</body>
</html>
"""


def build_data(graph):
    """Build a compact DATA object for the explorer from graph.json.

    graph.json node fields:
      page: id, type='page', title, domain, doc_type, tags, word_count, category_path, tools_mentioned
      tool: id='tool:xxx', type='tool', name, category, description, aliases(optional)
    Edge types: similar_to (+ tier), links_to, mentions (page→tool), tagged (page→concept:tag)
    """
    nodes = []
    for n in graph["nodes"]:
        if n.get("type") == "tool":
            nodes.append({
                "id": n["id"],
                "title": n.get("name", n["id"]),
                "node_type": "tool",
                "category": n.get("category", ""),
                "description": n.get("description", ""),
                "aliases": n.get("aliases", []),
                "domain": "tool",
            })
        else:
            nodes.append({
                "id": n["id"],
                "title": n.get("title", n["id"]),
                "domain": n.get("domain", ""),
                "doc_type": n.get("doc_type", ""),
                "tags": n.get("tags", []),
                "wc": n.get("word_count", n.get("wc", 0)),
                "cat": n.get("category_path", n.get("cat", "")),
                "node_type": n.get("type", "page"),
                "tools": n.get("tools_mentioned", []),
                "status": n.get("status", ""),
            })

    edges = []
    for e in graph["edges"]:
        # Include all useful edge types; skip 'tagged' (concept nodes add noise)
        if e["type"] in ("similar_to", "links_to", "mentions"):
            entry = {"s": e["source"], "t": e["target"], "ty": e["type"]}
            if "weight" in e:
                entry["w"] = round(e["weight"], 3)
            if "tier" in e:
                entry["tier"] = e["tier"]
            edges.append(entry)

    return {"nodes": nodes, "edges": edges}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="_meta/graph.json")
    ap.add_argument("--out", default="_meta/knowledge-graph-explorer.html")
    args = ap.parse_args()

    if not os.path.exists(args.graph):
        print(f"ERROR: {args.graph} not found — run build_graph.py first.", file=sys.stderr)
        return 1

    with open(args.graph, encoding="utf-8") as f:
        graph = json.load(f)

    data = build_data(graph)
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    page_count = sum(1 for n in data["nodes"] if n.get("node_type") != "tool")
    tool_count = sum(1 for n in data["nodes"] if n.get("node_type") == "tool")
    edge_counts = {}
    for e in data["edges"]:
        edge_counts[e["ty"]] = edge_counts.get(e["ty"], 0) + 1

    html = (
        TEMPLATE_BEFORE_DATA
        + f"const DATA = {data_json};\n"
        + TEMPLATE_AFTER_DATA
    )

    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print(f"Written: {args.out}")
    print(f"  Nodes: {page_count} pages + {tool_count} tools")
    print(f"  Edges: " + ", ".join(f"{v} {k}" for k, v in sorted(edge_counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
