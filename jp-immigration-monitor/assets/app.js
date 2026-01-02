function setActiveNav(){
  const path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a").forEach(a=>{
    if(a.getAttribute("href") === path) a.classList.add("active");
  });
}

function formatDateTime(iso){
  try { return new Date(iso).toLocaleString(); }
  catch { return iso; }
}

async function loadSampleData(){
  const res = await fetch("./assets/sample-data.json", {cache:"no-store"});
  return await res.json();
}

function renderTable(rows){
  const tbody = document.querySelector("#dataBody");
  if(!tbody) return;
  tbody.innerHTML = rows.map(r=>`
    <tr>
      <td>${r.category}</td>
      <td>${r.title}</td>
      <td>${r.source}</td>
      <td>${formatDateTime(r.published_at)}</td>
      <td>${r.confidence}%</td>
    </tr>
  `).join("");
}

function applyFilters(allRows){
  const q = (document.querySelector("#q")?.value || "").trim().toLowerCase();
  const cat = document.querySelector("#cat")?.value || "ALL";
  const minc = Number(document.querySelector("#minc")?.value || 0);

  return allRows.filter(r=>{
    const okQ = !q || (r.title.toLowerCase().includes(q) || r.source.toLowerCase().includes(q));
    const okC = cat === "ALL" || r.category === cat;
    const okMin = r.confidence >= minc;
    return okQ && okC && okMin;
  });
}

async function initDashboard(){
  const status = document.querySelector("#status");
  let all = await loadSampleData();

  const update = ()=>{
    const filtered = applyFilters(all);
    renderTable(filtered);
    if(status) status.textContent = `Showing ${filtered.length} of ${all.length} items (sample data)`;
  };

  ["#q","#cat","#minc"].forEach(sel=>{
    const el = document.querySelector(sel);
    if(!el) return;
    el.addEventListener("input", update);
    el.addEventListener("change", update);
  });

  const btn = document.querySelector("#refresh");
  if(btn){
    btn.addEventListener("click", async ()=>{
      btn.disabled = true;
      if(status) status.textContent = "Refreshing (demo)…";
      await new Promise(r=>setTimeout(r, 600));
      all = await loadSampleData();
      update();
      btn.disabled = false;
    });
  }

  update();
}

document.addEventListener("DOMContentLoaded", ()=>{
  setActiveNav();
  initDashboard();
});
