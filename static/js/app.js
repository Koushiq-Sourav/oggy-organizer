// My Oggy Organizer: library shows only your files (live backend docs).
(function () {
  "use strict";
  // No auto sample papers — library starts empty, fills from /api/docs only.
  const KIND_TAG = { papers: ["Research paper", "var(--bg-tint-violet)", "var(--text-tint-violet)", "M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"], slides: ["Slides", "var(--bg-tint-orange)", "var(--text-tint-orange)", "M3 4h18v12H3z"], notes: ["Notes", "var(--bg-tint-yellow)", "var(--text-tint-yellow)", "M6 3h9l4 4v14H6z"], data: ["Sheet", "var(--bg-tint-green)", "var(--text-tint-green)", "M3 4h18v16H3z"], report: ["Report", "var(--bg-tint-blue)", "var(--text-tint-blue)", "M6 3h12v18H6z"] };
  const STATUS_TAG = { Analyzed: ["var(--bg-success)", "var(--text-success)", "M5 13l4 4L19 7"], Analyzing: ["var(--bg-progress)", "var(--text-progress)", "M12 6v6l4 2"], "Needs review": ["var(--bg-warning)", "var(--text-warning)", "M12 8v5M12 16.5v.5"], Failed: ["var(--bg-danger)", "var(--text-danger)", "M6 6l12 12M18 6L6 18"], Queued: ["var(--bg-queued)", "var(--text-queued)", "M12 6v6l4 2"] };
  function icon(path) { return "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' aria-hidden='true'><path d='" + path + "'/></svg>"; }

  const list = document.getElementById("lib-list");
  if (!list) {
    // Upload page wiring (kept).
    wireUploadPage();
    wireTheme();
    return;
  }
  const emptyBox = document.getElementById("lib-empty");
  const summary = document.getElementById("lib-summary");
  const tags = document.getElementById("lib-tags");
  const counts = document.getElementById("lib-counts");
  const links = document.getElementById("lib-links");
  const search = document.getElementById("lib-search");
  const answerWrap = document.getElementById("lib-answer-wrap");
  const answer = document.getElementById("lib-answer");
  const filePick = document.getElementById("lib-file");
  const addBtn = document.getElementById("lib-add");
  const drop = document.getElementById("lib-drop");
  const uploads = document.getElementById("lib-uploads");
  const pane = document.getElementById("analysis-pane");
  const backdrop = document.getElementById("sheet-backdrop");
  let docs = [], shelf = "all", query = "", selected = null, focusIdx = -1;

  wireTheme();
  document.querySelectorAll("[data-shelf]").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll("[data-shelf]").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll('[data-shelf="' + b.dataset.shelf + '"]').forEach((x) => x.classList.add("active"));
    shelf = b.dataset.shelf;
    render();
  }));
  if (search) {
    search.addEventListener("change", ask);
    search.addEventListener("keydown", (e) => { if (e.key === "Enter") ask(); });
    const params = new URLSearchParams(location.search);
    if (params.get("q")) { search.value = params.get("q"); ask(); }
  }
  const searchForm = document.getElementById("lib-search-form");
  if (searchForm) searchForm.addEventListener("submit", (e) => {
    if (document.getElementById("lib-list")) { e.preventDefault(); ask(); }
  });
  if (addBtn && filePick) addBtn.onclick = () => filePick.click();
  if (filePick) filePick.addEventListener("change", () => { if (filePick.files.length) uploadFiles(filePick.files); filePick.value = ""; });
  if (drop) {
    drop.addEventListener("click", () => filePick.click());
    drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); filePick.click(); } });
    ["dragover", "dragenter"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
    ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
    drop.addEventListener("drop", (e) => { if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files); });
  }
  list.addEventListener("keydown", (e) => {
    const items = filtered();
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      focusIdx = e.key === "ArrowDown" ? Math.min(items.length - 1, focusIdx + 1) : Math.max(0, focusIdx - 1);
      const el = list.children[focusIdx];
      const btn = el ? el.querySelector(".doc-main") : null;
      if (btn) btn.focus();
    } else if (e.key === "Enter" && focusIdx >= 0 && items[focusIdx]) {
      select(items[focusIdx].id);
    }
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeSheet(); });
  if (backdrop) backdrop.addEventListener("click", closeSheet);
  const rb = document.getElementById("lib-reading");
  if (rb) rb.onclick = () => { if (selected && selected.report) location.href = "/report/" + selected.report; else if (answer) showAnswer(!docs.length ? "No files in Library." : "Select a file first to find gaps.", []); };

  refresh();
  async function refresh() {
    try {
      const [d, h] = await Promise.all([(await fetch("/api/docs")).json(), (await fetch("/api/history")).json()]);
      const live = (d.docs || []).map((x) => ({ id: x.id, name: x.name, kind: x.kind, detail: x.detail || x.kind, status: x.status, summary: "Analyzed by Oggy Q1 engine. Open the full report for the fix list.", topics: [], counts: x.kind, links: [], gaps: x.major || 0, report: x.report }));
      docs = live;
    } catch (_) { docs = []; }
    render();
    if (!selected && docs.length) select(firstVisible() || docs[0].id, false);
  }
  function firstVisible() { const f = filtered(); return f.length ? f[0].id : null; }
  function filtered() {
    return docs.filter((d) => {
      if (shelf === "review") { if ((d.gaps || 0) <= 0 && d.status !== "Needs review") return false; }
      else if (shelf === "related") { if (selected && d.kind !== selected.kind && d.id !== selected.id) return false; }
      else if (shelf !== "all" && d.kind !== shelf && !(shelf === "papers" && d.kind === "report")) return false;
      if (query && !(d.name || "").toLowerCase().includes(query)) return false;
      return true;
    });
  }
  function render() {
    const items = filtered();
    document.querySelectorAll("[data-count]").forEach((el) => {
      const k = el.dataset.count;
      el.textContent = k === "all" ? docs.length : k === "review" ? docs.filter((d) => (d.gaps || 0) > 0 || d.status === "Needs review").length : docs.filter((d) => d.kind === k).length;
    });
    if (emptyBox) emptyBox.style.display = docs.length ? "none" : "block";
    list.innerHTML = "";
    focusIdx = -1;
    items.forEach((d) => {
      const k = KIND_TAG[d.kind] || KIND_TAG.papers;
      const flag = (d.gaps > 0) ? (d.gaps + " gaps found") : d.status;
      const s = STATUS_TAG[d.status] || STATUS_TAG.Queued;
      const el = document.createElement("div");
      el.setAttribute("role", "option");
      el.setAttribute("aria-selected", selected && selected.id === d.id ? "true" : "false");
      el.className = "doc-row" + (selected && selected.id === d.id ? " selected" : "");
      el.dataset.id = d.id;
      const main = document.createElement("button");
      main.type = "button";
      main.className = "doc-main";
      main.innerHTML = "<span style='display:flex;justify-content:space-between;gap:8px;align-items:center'><span style='font-weight:500'>" + esc(d.name) + "</span><span class='badge' style='background:" + s[0] + ";color:" + s[1] + "'>" + icon(s[2]) + esc(flag) + "</span></span>" +
        "<span class='meta' style='display:block;margin-top:4px'><span class='tag' style='background:" + k[1] + ";color:" + k[2] + "'>" + icon(k[3]) + k[0] + "</span> " + esc(d.detail || "") + "</span>";
      main.onclick = () => select(d.id);
      const del = document.createElement("button");
      del.type = "button";
      del.className = "doc-del";
      del.title = "Remove from library (deletes from database)";
      del.setAttribute("aria-label", "Remove " + d.name + " from library");
      del.innerHTML = "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' aria-hidden='true'><path d='M6 6l12 12M18 6L6 18'/></svg>";
      del.onclick = (e) => { e.stopPropagation(); removeDoc(d.id, el); };
      el.appendChild(main);
      el.appendChild(del);
      list.appendChild(el);
    });
  }
  async function removeDoc(id, rowEl) {
    if (rowEl) rowEl.classList.add("removing");
    const done = () => {
      docs = docs.filter((x) => x.id !== id);
      if (selected && selected.id === id) {
        selected = null;
        const f = filtered();
        if (f.length) select(f[0].id, false);
        else { summary.textContent = "Select a document to see Oggy analysis."; tags.innerHTML = ""; counts.textContent = ""; links.textContent = "—"; }
      }
      render();
    };
    // Sample docs live only in memory — no backend delete needed.
    // Local-only failed uploads (up-) have no backend entry.
    if (String(id).indexOf("up-") === 0) {
      setTimeout(done, 180);
      return;
    }
    try {
      const r = await fetch("/api/docs/" + encodeURIComponent(id), { method: "DELETE" });
      if (!r.ok) throw new Error("delete failed");
    } catch (_) {
      if (rowEl) rowEl.classList.remove("removing");
      return;
    }
    setTimeout(done, 180);
  }
  function select(id, open) {
    selected = docs.find((d) => d.id === id) || null;
    render();
    if (!selected) return;
    summary.textContent = selected.summary || "No summary yet.";
    tags.innerHTML = (selected.topics || []).map((t) => "<span class='tag' style='background:" + t[1] + ";color:" + t[2] + "'>" + esc(t[0]) + "</span>").join("");
    counts.textContent = selected.counts || "";
    links.innerHTML = "";
    (selected.links || []).forEach((l, i) => {
      if (i > 0) links.appendChild(document.createTextNode(", "));
      const a = document.createElement("a");
      a.href = "#";
      a.textContent = l.t;
      a.style.textDecoration = "underline";
      a.onclick = (e) => { e.preventDefault(); select(l.id); };
      links.appendChild(a);
    });
    if (!(selected.links || []).length) links.textContent = "—";
    const box = document.getElementById("lib-analysis");
    if (box) { box.classList.remove("fade-in"); void box.offsetWidth; box.classList.add("fade-in"); }
    if (open !== false) openSheet();
  }
  function ask() {
    const q = (search.value || "").trim();
    if (!q) { answerWrap.hidden = true; query = ""; render(); return; }
    const m = q.match(/slide\s*(\d+)/i);
    let hits = [];
    if (m) {
      hits = docs.filter((d) => d.kind === "papers");
      showAnswer("Slide " + m[1] + " is supported by " + hits.length + " paper(s) in your library:", hits);
    } else {
      const words = q.toLowerCase().split(/\s+/).filter((w) => w.length > 3);
      hits = docs.filter((d) => words.some((w) => (d.name + " " + (d.summary || "")).toLowerCase().includes(w)));
      showAnswer(hits.length ? "Found " + hits.length + " document(s) matching your question:" : "No direct match. Try keywords from the paper or slide title.", hits);
    }
    query = "";
  }
  function showAnswer(text, hits) {
    answerWrap.hidden = false;
    answer.innerHTML = "";
    answer.appendChild(document.createTextNode(text + " "));
    hits.forEach((h, i) => {
      if (i > 0) answer.appendChild(document.createTextNode(", "));
      const a = document.createElement("a");
      a.href = "#";
      a.textContent = h.name;
      a.style.textDecoration = "underline";
      a.onclick = (e) => { e.preventDefault(); select(h.id); };
      answer.appendChild(a);
    });
  }
  async function uploadFiles(files) {
    for (const f of files) {
      const box = document.createElement("div");
      box.className = "per-file";
      box.innerHTML = "<span>" + esc(f.name) + "</span><div class='progress-track'><div class='progress-fill'></div></div>";
      uploads.prepend(box);
      const fill = box.querySelector(".progress-fill");
      fill.style.width = "20%";
      const fd = new FormData();
      if (/\.pptx$/i.test(f.name)) fd.append("deck", f);
      else fd.append("thesis", f);
      fill.style.width = "60%";
      try {
        const r = await fetch("/api/analyze", { method: "POST", body: fd });
        const j = await r.json();
        fill.style.width = "100%";
        docs.unshift({ id: j.doc || ("up-" + Date.now()), name: f.name, kind: kindOf(f.name), detail: f.name, status: j.verdict === "Pass" ? "Analyzed" : "Needs review", summary: (j.fix_list || [])[0] || "Analyzed.", topics: [], counts: "", links: [], gaps: j.major || 0, report: j.id });
        setTimeout(() => box.remove(), 1200);
      } catch (_) {
        docs.unshift({ id: "up-" + Date.now(), name: f.name, kind: kindOf(f.name), detail: f.name, status: "Failed", summary: "Upload failed. Try again.", topics: [], counts: "", links: [], gaps: 0 });
        box.remove();
      }
      render();
    }
  }
  function kindOf(n) { if (/\.pptx$/i.test(n)) return "slides"; if (/\.md$|\.txt$/i.test(n)) return "notes"; if (/\.csv$|\.xlsx?$/i.test(n)) return "data"; return "papers"; }
  function esc(s) { return (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
  function openSheet() {
    if (window.innerWidth > 900 || !pane) return;
    pane.classList.add("sheet");
    if (backdrop) backdrop.hidden = false;
  }
  function closeSheet() {
    if (!pane) return;
    pane.classList.remove("sheet");
    if (backdrop) backdrop.hidden = true;
  }
  function wireTheme() {
    const t = document.getElementById("theme-toggle");
    if (t) t.onclick = () => {
      const h = document.documentElement;
      h.dataset.theme = h.dataset.theme === "dark" ? "light" : "dark";
    };
  }
  function wireUploadPage() {
    const addBtn = document.getElementById("lib-add");
    if (addBtn) addBtn.onclick = () => { location.href = "/"; };
    const params = new URLSearchParams(location.search);
    if (params.get("paper")) {
      const ctx = document.createElement("p");
      ctx.className = "meta";
      ctx.textContent = "Checking against: " + params.get("paper");
      const h = document.querySelector(".page-lib h1");
      if (h) h.after(ctx);
    }
    const MAX = 50 * 1024 * 1024;
    function wireFile(inputId, chipId, nameId, clearId, pickId, dropId, errId, okExts) {
      const input = document.getElementById(inputId);
      const chip = document.getElementById(chipId);
      if (!input || !chip) return;
      const name = document.getElementById(nameId);
      const clear = document.getElementById(clearId);
      const pick = pickId ? document.getElementById(pickId) : null;
      const drop = dropId ? document.getElementById(dropId) : null;
      const err = errId ? document.getElementById(errId) : null;
      function valid(f) {
        const ok = okExts.some((e) => f.name.toLowerCase().endsWith(e));
        if (!ok && err) err.textContent = "Type not accepted. Use " + okExts.join(", ");
        else if (f.size > MAX && err) err.textContent = "File over 50 MB. Split it first.";
        else if (err) err.textContent = "";
        return ok && f.size <= MAX;
      }
      function setFile(f) {
        if (!valid(f)) { input.value = ""; return; }
        const dt = new DataTransfer();
        dt.items.add(f);
        input.files = dt.files;
        name.textContent = f.name;
        chip.hidden = false;
        if (pick) pick.textContent = f.name;
      }
      input.addEventListener("change", () => {
        if (input.files && input.files.length > 0) {
          if (!valid(input.files[0])) { input.value = ""; return; }
          name.textContent = input.files[0].name; chip.hidden = false;
          if (pick) pick.textContent = input.files[0].name;
        } else { chip.hidden = true; if (pick) pick.textContent = "No file chosen"; }
      });
      clear.addEventListener("click", () => { input.value = ""; chip.hidden = true; name.textContent = ""; if (pick) pick.textContent = "No file chosen"; if (err) err.textContent = ""; });
      if (drop) {
        ["dragover", "dragenter"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
        ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
        drop.addEventListener("drop", (e) => { if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]); });
        drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
      }
    }
    wireFile("thesis-input", "thesis-chip", "thesis-name", "thesis-clear", "thesis-pick-name", "thesis-drop", "thesis-err", [".pdf", ".html", ".htm", ".docx"]);
    wireFile("deck-input", "deck-chip", "deck-name", "deck-clear", "deck-pick-name", "deck-drop", "deck-err", [".pptx"]);
    const form = document.getElementById("oggy-form");
    if (form) form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const prog = document.getElementById("oggy-progress");
      const bar = document.getElementById("oggy-bar");
      const fill = document.getElementById("oggy-fill");
      if (prog) prog.hidden = false;
      if (bar) bar.textContent = "30%";
      if (fill) fill.style.width = "30%";
      const fd = new FormData(form);
      const r = await fetch("/api/analyze", { method: "POST", body: fd });
      const j = await r.json();
      if (bar) bar.textContent = "100%";
      if (fill) fill.style.width = "100%";
      document.getElementById("oggy-result").innerHTML = "Overall " + j.overall + " (" + j.verdict + ") — <a class='underline' href='/report/" + j.id + "'>open report</a> · <a class='underline' href='/'>view in library</a>";
      loadUploadHistory();
    });
    loadUploadHistory();
    async function loadUploadHistory() {
      const box = document.getElementById("upload-history");
      if (!box) return;
      try {
        const h = await (await fetch("/api/history")).json();
        const reps = (h.reports || []).slice(0, 5);
        if (!reps.length) { box.textContent = "No reviews yet."; return; }
        box.innerHTML = "";
        reps.forEach((r) => {
          const a = document.createElement("a");
          a.href = "/report/" + r.id;
          a.style.textDecoration = "underline";
          a.style.display = "block";
          a.textContent = r.id + " — " + r.overall + " (" + r.verdict + ")";
          box.appendChild(a);
        });
      } catch (_) { box.textContent = "History unavailable."; }
    }
  }
})();
