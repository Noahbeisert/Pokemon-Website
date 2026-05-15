const TC = {
  Normal:"#A8A878",Fire:"#F08030",Water:"#6890F0",Electric:"#F8D030",
  Grass:"#78C850",Ice:"#98D8D8",Fighting:"#C03028",Poison:"#A040A0",
  Ground:"#E0C068",Flying:"#A890F0",Psychic:"#F85888",Bug:"#A8B820",
  Rock:"#B8A038",Ghost:"#705898",Dragon:"#7038F8",Dark:"#705848",
  Steel:"#B8B8D0",Fairy:"#EE99AC"
};
const TYPES = Object.keys(TC);

const DEF = {
  Normal:   {weak:["Fighting"],immune:["Ghost"],resist:[]},
  Fire:     {weak:["Water","Ground","Rock"],immune:[],resist:["Fire","Grass","Ice","Bug","Steel","Fairy"]},
  Water:    {weak:["Electric","Grass"],immune:[],resist:["Fire","Water","Ice","Steel"]},
  Electric: {weak:["Ground"],immune:[],resist:["Electric","Flying","Steel"]},
  Grass:    {weak:["Fire","Ice","Poison","Flying","Bug"],immune:[],resist:["Water","Electric","Grass","Ground"]},
  Ice:      {weak:["Fire","Fighting","Rock","Steel"],immune:[],resist:["Ice"]},
  Fighting: {weak:["Flying","Psychic","Fairy"],immune:[],resist:["Bug","Rock","Dark"]},
  Poison:   {weak:["Ground","Psychic"],immune:[],resist:["Grass","Fighting","Poison","Bug","Fairy"]},
  Ground:   {weak:["Water","Grass","Ice"],immune:["Electric"],resist:["Poison","Rock"]},
  Flying:   {weak:["Electric","Ice","Rock"],immune:["Ground"],resist:["Grass","Fighting","Bug"]},
  Psychic:  {weak:["Bug","Ghost","Dark"],immune:[],resist:["Fighting","Psychic"]},
  Bug:      {weak:["Fire","Flying","Rock"],immune:[],resist:["Grass","Fighting","Ground"]},
  Rock:     {weak:["Water","Grass","Fighting","Ground","Steel"],immune:[],resist:["Normal","Fire","Poison","Flying"]},
  Ghost:    {weak:["Ghost","Dark"],immune:["Normal","Fighting"],resist:["Poison","Bug"]},
  Dragon:   {weak:["Ice","Dragon","Fairy"],immune:[],resist:["Fire","Water","Electric","Grass"]},
  Dark:     {weak:["Fighting","Bug","Fairy"],immune:["Psychic"],resist:["Ghost","Dark"]},
  Steel:    {weak:["Fire","Fighting","Ground"],immune:["Poison"],resist:["Normal","Grass","Ice","Flying","Psychic","Bug","Rock","Dragon","Steel","Fairy"]},
  Fairy:    {weak:["Poison","Steel"],immune:["Dragon"],resist:["Fighting","Bug","Dark"]},
};

const OFF = {
  Normal:   {strong:[],weak:["Rock","Steel"],noEffect:["Ghost"]},
  Fire:     {strong:["Grass","Ice","Bug","Steel"],weak:["Water","Fire","Rock","Dragon"],noEffect:[]},
  Water:    {strong:["Fire","Ground","Rock"],weak:["Water","Grass","Dragon"],noEffect:[]},
  Electric: {strong:["Water","Flying"],weak:["Electric","Grass","Dragon"],noEffect:["Ground"]},
  Grass:    {strong:["Water","Ground","Rock"],weak:["Fire","Grass","Poison","Flying","Bug","Dragon","Steel"],noEffect:[]},
  Ice:      {strong:["Grass","Ground","Flying","Dragon"],weak:["Water","Ice"],noEffect:[]},
  Fighting: {strong:["Normal","Ice","Rock","Dark","Steel"],weak:["Poison","Bug","Psychic","Flying","Fairy"],noEffect:["Ghost"]},
  Poison:   {strong:["Grass","Fairy"],weak:["Poison","Ground","Rock","Ghost"],noEffect:["Steel"]},
  Ground:   {strong:["Fire","Electric","Poison","Rock","Steel"],weak:["Grass","Bug"],noEffect:["Flying"]},
  Flying:   {strong:["Grass","Fighting","Bug"],weak:["Electric","Rock","Steel"],noEffect:[]},
  Psychic:  {strong:["Fighting","Poison"],weak:["Psychic","Steel"],noEffect:["Dark"]},
  Bug:      {strong:["Grass","Psychic","Dark"],weak:["Fire","Fighting","Poison","Flying","Ghost","Steel","Fairy"],noEffect:[]},
  Rock:     {strong:["Fire","Ice","Flying","Bug"],weak:["Fighting","Ground","Steel"],noEffect:[]},
  Ghost:    {strong:["Ghost","Psychic"],weak:["Dark"],noEffect:["Normal"]},
  Dragon:   {strong:["Dragon"],weak:["Steel"],noEffect:["Fairy"]},
  Dark:     {strong:["Ghost","Psychic"],weak:["Fighting","Dark","Fairy"],noEffect:[]},
  Steel:    {strong:["Ice","Rock","Fairy"],weak:["Fire","Water","Electric","Steel"],noEffect:[]},
  Fairy:    {strong:["Fighting","Dragon","Dark"],weak:["Fire","Poison","Steel"],noEffect:[]},
};

function defMultipliers(selectedTypes) {
  const m = {};
  TYPES.forEach(t => m[t] = 1);
  selectedTypes.forEach(st => {
    DEF[st].weak.forEach(t   => m[t] *= 2);
    DEF[st].resist.forEach(t => m[t] *= 0.5);
    DEF[st].immune.forEach(t => m[t]  = 0);
  });
  return m;
}

function offMultipliers(selectedTypes) {
  const m = {};
  TYPES.forEach(dt => {
    const mults = selectedTypes.map(st => {
      const o = OFF[st];
      if (o.noEffect.includes(dt)) return 0;
      if (o.strong.includes(dt))   return 2;
      if (o.weak.includes(dt))     return 0.5;
      return 1;
    });
    const best = Math.max(...mults);
    const worst = Math.min(...mults);
    if (best === 2)   m[dt] = 2;
    else if (best === 1) m[dt] = 1;
    else if (worst === 0 && best === 0) m[dt] = 0;
    else m[dt] = 0.5;
  });
  return m;
}

function multLabel(v) {
  return v===4?'4×':v===2?'2×':v===0.5?'½×':v===0.25?'¼×':v===0?'0×':'';
}
function pill(type, mult) {
  const badge = (mult !== undefined && mult !== 1)
    ? `<span class="mult-badge">${multLabel(mult)}</span>` : '';
  return `<span class="pill" style="background:${TC[type]}">${type}${badge}</span>`;
}
function renderList(container, items, fallback) {
  container.innerHTML = items.length
    ? items.map(([t, m]) => pill(t, m)).join('')
    : `<span class="empty">${fallback}</span>`;
}

function getMult(moveType, defType) {
  const o = OFF[moveType];
  if (o.noEffect.includes(defType)) return 0;
  if (o.strong.includes(defType))   return 2;
  if (o.weak.includes(defType))     return 0.5;
  return 1;
}

function renderOffCard(containerId, targetMult, fallback) {
  const el = document.getElementById(containerId);
  if (selected.length === 1) {
    const hits = TYPES.filter(t => getMult(selected[0], t) === targetMult);
    el.innerHTML = hits.length
      ? hits.map(t => pill(t)).join('')
      : `<span class="empty">${fallback}</span>`;
    return;
  }
  const cols = selected.map((moveType, i) => {
    const hits = TYPES.filter(t => getMult(moveType, t) === targetMult);
    const accent = i === 0 ? '#f8d030' : '#7ecfff';
    const targets = hits.length
      ? hits.map(t => `<span class="pill" style="background:${TC[t]}">${t}</span>`).join('')
      : `<span class="empty">${fallback}</span>`;
    return `<div style="flex:1;min-width:0;">
      <div style="margin-bottom:8px;">
        <span class="pill" style="background:${TC[moveType]};outline:2px solid ${accent};outline-offset:2px;">${moveType}</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:0;">${targets}</div>
    </div>`;
  });
  el.innerHTML = `<div style="display:flex;gap:16px;align-items:flex-start;">
    ${cols[0]}
    <div style="width:1px;background:rgba(255,255,255,0.07);align-self:stretch;flex-shrink:0;margin-top:2px;"></div>
    ${cols[1]}
  </div>`;
}

function renderSuperEff() {
  const el    = document.getElementById('super-eff');
  const title = document.getElementById('super-eff-title');

  if (currentMoveTypes === null) {
    if (title) title.textContent = 'Super effective vs (2×)';
    renderOffCard('super-eff', 2, 'None at 2×');
    return;
  }

  if (currentMoveTypes === undefined) {
    if (title) title.textContent = 'Super effective vs (2×)';
    renderOffCard('super-eff', 2, 'None at 2×');
    el.innerHTML += `<div class="sub-label" style="margin-top:10px;display:flex;align-items:center;gap:6px">
      <div class="spin-sm" style="width:12px;height:12px;border-width:1.5px;flex-shrink:0"></div>
      Loading full learnset…
    </div>`;
    return;
  }

  if (title) title.textContent = 'Super effective vs — full learnset';

  const stabSet = new Set();
  selected.forEach(st => TYPES.forEach(dt => { if (getMult(st, dt) === 2) stabSet.add(dt); }));

  const covMoveTypes = currentMoveTypes.filter(mt => !selected.includes(mt) && TYPES.includes(mt));

  const covTargetMap = {};
  covMoveTypes.forEach(mt => {
    TYPES.forEach(dt => {
      if (getMult(mt, dt) === 2 && !stabSet.has(dt)) {
        if (!covTargetMap[dt]) covTargetMap[dt] = [];
        covTargetMap[dt].push(mt);
      }
    });
  });

  let html = '';

  if (stabSet.size > 0) {
    if (selected.length === 1) {
      html += `<div class="sub-label">STAB (${selected[0]})</div>`;
      html += [...stabSet].map(t => pill(t)).join('');
    } else {
      const cols = selected.map((moveType, i) => {
        const hits = TYPES.filter(dt => getMult(moveType, dt) === 2);
        const accent = i === 0 ? '#f8d030' : '#7ecfff';
        const targets = hits.length
          ? hits.map(t => `<span class="pill" style="background:${TC[t]}">${t}</span>`).join('')
          : `<span class="empty">None</span>`;
        return `<div style="flex:1;min-width:0;">
          <div style="margin-bottom:8px;"><span class="pill" style="background:${TC[moveType]};outline:2px solid ${accent};outline-offset:2px;">${moveType}</span></div>
          <div style="display:flex;flex-wrap:wrap;gap:0;">${targets}</div>
        </div>`;
      });
      html += `<div class="sub-label">STAB</div>
        <div style="display:flex;gap:16px;align-items:flex-start;">
          ${cols[0]}
          <div style="width:1px;background:rgba(255,255,255,0.07);align-self:stretch;flex-shrink:0;margin-top:2px;"></div>
          ${cols[1]}
        </div>`;
    }
  } else {
    html += `<span class="empty">No STAB coverage</span>`;
  }

  const covEntries = Object.entries(covTargetMap);
  html += `<div class="sub-label" style="margin-top:10px">Coverage moves</div>`;
  if (covEntries.length > 0) {
    html += `<div style="display:flex;flex-wrap:wrap;gap:4px;">`;
    html += covEntries.map(([dt, moveTypes]) => {
      const badges = moveTypes.map(mt =>
        `<span style="font-size:9px;background:${TC[mt]}33;color:${TC[mt]};border:1px solid ${TC[mt]}55;border-radius:3px;padding:1px 4px;line-height:1.4">${mt}</span>`
      ).join('');
      return `<span style="display:inline-flex;align-items:center;gap:3px;margin-bottom:2px;">
        <span class="pill" style="background:${TC[dt]};margin:0">${dt}</span>
        <span style="display:flex;flex-wrap:wrap;gap:2px;">${badges}</span>
      </span>`;
    }).join('');
    html += `</div>`;
  } else {
    html += `<span class="empty">No additional threats beyond STAB</span>`;
  }

  el.innerHTML = html;
}

let selected = [];
let currentMoveTypes = null;

const grid = document.getElementById('type-grid');
const btns = {};
TYPES.forEach(t => {
  const b = document.createElement('button');
  b.className = 'type-btn';
  b.textContent = t;
  b.style.background = TC[t];
  b.onclick = () => toggle(t);
  grid.appendChild(b);
  btns[t] = b;
});

function toggle(t) {
  currentMoveTypes = null;
  const idx = selected.indexOf(t);
  if (idx >= 0) {
    selected.splice(idx, 1);
  } else {
    if (selected.length >= 2) selected.shift();
    selected.push(t);
  }
  render();
}

function render() {
  TYPES.forEach(t => {
    btns[t].classList.remove('selected','sel-1','sel-2');
  });
  selected.forEach((t, i) => {
    btns[t].classList.add('selected', i === 0 ? 'sel-1' : 'sel-2');
  });

  const bar = document.getElementById('sel-display-inner');
  if (!selected.length) {
    bar.innerHTML = `<span class="sel-none">none</span>`;
    document.getElementById('results').classList.remove('visible');
    return;
  }
  bar.innerHTML = selected.map((t, i) => {
    const outline = i === 0 ? '2px solid #f8d030' : '2px solid #7ecfff';
    return `<span class="sel-pill" style="background:${TC[t]};outline:${outline}">
      ${t}
      <span class="remove" onclick="deselect('${t}')">×</span>
    </span>`;
  }).join('');

  const dm = defMultipliers(selected);
  const def4  = TYPES.filter(t => dm[t] === 4).map(t => [t, 4]);
  const def2  = TYPES.filter(t => dm[t] === 2).map(t => [t, 2]);
  const defH  = TYPES.filter(t => dm[t] === 0.5).map(t => [t, 0.5]);
  const defQ  = TYPES.filter(t => dm[t] === 0.25).map(t => [t, 0.25]);
  const def0  = TYPES.filter(t => dm[t] === 0).map(t => [t]);

  const weakEl = document.getElementById('weak-to');
  let weakHtml = '';
  if (def4.length) weakHtml += `<div class="sub-label">4× super effective:</div>${def4.map(([t,m]) => pill(t,m)).join('')}<br>`;
  if (def2.length) weakHtml += `<div class="sub-label"${def4.length?' style="margin-top:8px"':''}>2× super effective:</div>${def2.map(([t,m]) => pill(t,m)).join('')}`;
  weakEl.innerHTML = weakHtml || `<span class="empty">None</span>`;

  const resEl = document.getElementById('resists');
  let resHtml = '';
  if (defH.length) resHtml += `<div class="sub-label">½× not very effective:</div>${defH.map(([t,m]) => pill(t,m)).join('')}<br>`;
  if (defQ.length) resHtml += `<div class="sub-label"${defH.length?' style="margin-top:8px"':''}>¼× barely effective:</div>${defQ.map(([t,m]) => pill(t,m)).join('')}`;
  resEl.innerHTML = resHtml || `<span class="empty">None</span>`;

  renderList(document.getElementById('immune-to'), def0, 'None');

  renderSuperEff();
  renderOffCard('not-eff',   0.5, 'None');
  renderOffCard('no-eff',    0,   'None');

  document.getElementById('results').classList.add('visible');
}

function deselect(t) {
  selected = selected.filter(x => x !== t);
  render();
}

/* ── Pokemon Search ──────────────────────────────────────────── */
let pokeList = null;
let ddFocusIdx = -1;

const pokeInput   = document.getElementById('poke-input');
const pokeClear   = document.getElementById('poke-clear');
const pokeDd      = document.getElementById('poke-dropdown');
const spriteMini  = document.getElementById('sprite-mini');
const searchMeta  = document.getElementById('search-meta');

function fmtName(slug) {
  return slug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

async function loadPokeList() {
  if (pokeList) return pokeList;
  try {
    const r = await fetch('https://pokeapi.co/api/v2/pokemon?limit=2000');
    const d = await r.json();
    pokeList = d.results.map(p => ({ slug: p.name, display: fmtName(p.name) }));
  } catch {
    pokeList = [];
  }
  return pokeList;
}

async function fetchPokeData(slug) {
  let r = await fetch(`https://pokeapi.co/api/v2/pokemon/${slug}`);
  if (!r.ok) {
    const sr = await fetch(`https://pokeapi.co/api/v2/pokemon-species/${slug}`);
    if (!sr.ok) return null;
    const sd = await sr.json();
    const def = sd.varieties?.find(v => v.is_default);
    if (!def) return null;
    r = await fetch(def.pokemon.url);
    if (!r.ok) return null;
  }
  const d = await r.json();
  const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
  return {
    id: d.id,
    slug,
    apiName: d.name,
    sprite: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${d.id}.png`,
    types: d.types.map(t => cap(t.type.name))
  };
}

async function fetchMoveTypes(apiName) {
  try {
    const query = `{
      pokemon_v2_pokemon(where: {name: {_eq: "${apiName}"}}) {
        pokemon_v2_pokemonmoves(where: {version_group_id: {_gte: 20}}) {
          pokemon_v2_move { pokemon_v2_type { name } }
        }
      }
    }`;
    const r = await fetch('https://beta.pokeapi.co/graphql/v1beta', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!r.ok) return null;
    const json = await r.json();
    const poke = json.data?.pokemon_v2_pokemon?.[0];
    if (!poke) return null;
    const types = new Set();
    poke.pokemon_v2_pokemonmoves.forEach(pm => {
      const t = pm.pokemon_v2_move?.pokemon_v2_type?.name;
      if (t) types.add(t.charAt(0).toUpperCase() + t.slice(1));
    });
    return [...types];
  } catch {
    return null;
  }
}

function showDropdown(items, rawQuery) {
  if (!items.length) { pokeDd.classList.add('hidden'); return; }
  const escaped = rawQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`(${escaped})`, 'gi');
  pokeDd.innerHTML = items.slice(0, 8).map((p, i) =>
    `<div class="dd-item" data-slug="${p.slug}" data-idx="${i}">${p.display.replace(re, '<strong>$1</strong>')}</div>`
  ).join('');
  pokeDd.classList.remove('hidden');
  ddFocusIdx = -1;
  pokeDd.querySelectorAll('.dd-item').forEach(item => {
    item.addEventListener('mousedown', e => {
      e.preventDefault();
      selectPoke(item.dataset.slug, item.textContent);
    });
  });
}

function hideDropdown() {
  pokeDd.classList.add('hidden');
  ddFocusIdx = -1;
}

function setSpriteMiniLoading() {
  spriteMini.innerHTML = '<div class="spin-sm"></div>';
}
function setSpriteMiniEmpty() {
  spriteMini.innerHTML = '<span class="sprite-ph">?</span>';
}

async function selectPoke(slug, displayName) {
  pokeInput.value = displayName || fmtName(slug);
  pokeClear.classList.add('visible');
  hideDropdown();
  setSpriteMiniLoading();
  searchMeta.innerHTML = `<span class="search-hint">Loading…</span>`;

  currentMoveTypes = null;
  const data = await fetchPokeData(slug);
  if (data) {
    const img = new Image();
    img.style.cssText = 'width:100%;height:100%;object-fit:contain';
    img.src = data.sprite;
    img.onload = () => { spriteMini.innerHTML = ''; spriteMini.appendChild(img); };
    img.onerror = () => { spriteMini.innerHTML = '<span class="sprite-ph">?</span>'; };

    const typePills = data.types
      .filter(t => TC[t])
      .map(t => `<span class="pill" style="background:${TC[t]};margin:0">${t}</span>`)
      .join('');
    searchMeta.innerHTML = `
      <span class="search-poke-name">${fmtName(data.slug)}</span>
      <span class="search-poke-types">${typePills}</span>
    `;

    selected = data.types.filter(t => TYPES.includes(t)).slice(0, 2);
    currentMoveTypes = undefined;
    render();

    fetchMoveTypes(data.apiName).then(types => {
      currentMoveTypes = types ?? null;
      render();
    });
  } else {
    setSpriteMiniEmpty();
    searchMeta.innerHTML = `<span class="search-hint" style="color:#f85888">Not found — check spelling</span>`;
  }
}

pokeInput.addEventListener('focus', () => loadPokeList());

pokeInput.addEventListener('input', async e => {
  const raw = e.target.value.trim();
  pokeClear.classList.toggle('visible', raw.length > 0);
  if (raw.length < 2) { hideDropdown(); return; }
  const list = await loadPokeList();
  const q = raw.toLowerCase().replace(/\s+/g, '-');
  const qSpace = raw.toLowerCase();
  const starts   = list.filter(p => p.slug.startsWith(q) || p.display.toLowerCase().startsWith(qSpace));
  const contains = list.filter(p => !starts.includes(p) && (p.slug.includes(q) || p.display.toLowerCase().includes(qSpace)));
  showDropdown([...starts, ...contains], raw);
});

pokeInput.addEventListener('keydown', e => {
  const items = pokeDd.querySelectorAll('.dd-item');
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    ddFocusIdx = Math.min(ddFocusIdx + 1, items.length - 1);
    items.forEach((it, i) => it.classList.toggle('focused', i === ddFocusIdx));
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    ddFocusIdx = Math.max(ddFocusIdx - 1, 0);
    items.forEach((it, i) => it.classList.toggle('focused', i === ddFocusIdx));
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (ddFocusIdx >= 0 && items[ddFocusIdx]) {
      const it = items[ddFocusIdx];
      selectPoke(it.dataset.slug, it.textContent);
    } else if (pokeInput.value.trim()) {
      const slug = pokeInput.value.trim().toLowerCase().replace(/\s+/g, '-');
      selectPoke(slug);
    }
  } else if (e.key === 'Escape') {
    hideDropdown();
  }
});

pokeClear.addEventListener('click', () => {
  pokeInput.value = '';
  pokeClear.classList.remove('visible');
  hideDropdown();
  setSpriteMiniEmpty();
  currentMoveTypes = null;
  searchMeta.innerHTML = `<span class="search-hint">Type to search — types auto-fill the chart below</span>`;
});

document.addEventListener('click', e => {
  if (!e.target.closest('#poke-input') && !e.target.closest('#poke-dropdown')) {
    hideDropdown();
  }
});
