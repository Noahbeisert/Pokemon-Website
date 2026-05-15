/* ── CONSTANTS ── */
const NATURES = [
  'Hardy','Lonely','Brave','Adamant','Naughty',
  'Bold','Docile','Relaxed','Impish','Lax',
  'Timid','Hasty','Serious','Jolly','Naive',
  'Modest','Mild','Quiet','Bashful','Rash',
  'Calm','Gentle','Sassy','Careful','Quirky'
];

const NAT_FX = {
  Hardy:{u:null,d:null}, Lonely:{u:'atk',d:'def'}, Brave:{u:'atk',d:'spe'},
  Adamant:{u:'atk',d:'spa'}, Naughty:{u:'atk',d:'spd'}, Bold:{u:'def',d:'atk'},
  Docile:{u:null,d:null}, Relaxed:{u:'def',d:'spe'}, Impish:{u:'def',d:'spa'},
  Lax:{u:'def',d:'spd'}, Timid:{u:'spe',d:'atk'}, Hasty:{u:'spe',d:'def'},
  Serious:{u:null,d:null}, Jolly:{u:'spe',d:'spa'}, Naive:{u:'spe',d:'spd'},
  Modest:{u:'spa',d:'atk'}, Mild:{u:'spa',d:'def'}, Quiet:{u:'spa',d:'spe'},
  Bashful:{u:null,d:null}, Rash:{u:'spa',d:'spd'}, Calm:{u:'spd',d:'atk'},
  Gentle:{u:'spd',d:'def'}, Sassy:{u:'spd',d:'spe'}, Careful:{u:'spd',d:'spa'},
  Quirky:{u:null,d:null}
};

const ITEMS = [
  { name: 'Aerodactylite',  desc: 'Mega Stone — Mega Aerodactyl (Rock/Flying, Tough Claws, +10 Spe)' },
  { name: 'Babiri Berry',   desc: 'Halves damage from one super-effective Steel hit' },
  { name: 'Black Belt',     desc: '+20% power to Fighting-type moves' },
  { name: 'Black Glasses',  desc: '+20% power to Dark-type moves' },
  { name: 'Bright Powder',  desc: "Lowers the opponent's accuracy by 10%" },
  { name: 'Charcoal',       desc: '+20% power to Fire-type moves' },
  { name: 'Charizardite X', desc: 'Mega Stone — Mega Charizard X (Fire/Dragon, Tough Claws)' },
  { name: 'Charizardite Y', desc: 'Mega Stone — Mega Charizard Y (Fire/Flying, Drought on entry)' },
  { name: 'Charti Berry',   desc: 'Halves damage from one super-effective Rock hit' },
  { name: 'Choice Scarf',   desc: '+50% Speed; locks you into one move until switch' },
  { name: 'Chople Berry',   desc: 'Halves damage from one super-effective Fighting hit' },
  { name: 'Coba Berry',     desc: 'Halves damage from one super-effective Flying hit' },
  { name: 'Colbur Berry',   desc: 'Halves damage from one super-effective Dark hit' },
  { name: 'Fairy Feather',  desc: '+20% power to Fairy-type moves' },
  { name: 'Focus Sash',     desc: 'Survives any one-hit KO with 1 HP (must start at full HP)' },
  { name: 'Garchompite',    desc: 'Mega Stone — Mega Garchomp (Dragon/Ground, Sand Force)' },
  { name: 'Haban Berry',    desc: 'Halves damage from one super-effective Dragon hit' },
  { name: 'Hard Stone',     desc: '+20% power to Rock-type moves' },
  { name: 'Kasib Berry',    desc: 'Halves damage from one super-effective Ghost hit' },
  { name: 'Kebia Berry',    desc: 'Halves damage from one super-effective Poison hit' },
  { name: "King's Rock",    desc: '10% chance to flinch on any damaging hit' },
  { name: 'Leftovers',      desc: 'Restores 1/16 max HP at end of each turn' },
  { name: 'Lum Berry',      desc: 'Cures any status condition (burn, paralysis, sleep…) once' },
  { name: 'Magnet',         desc: '+20% power to Electric-type moves' },
  { name: 'Mental Herb',    desc: 'Cures Attract, Taunt, Encore, Torment, Disable or Heal Block once' },
  { name: 'Miracle Seed',   desc: '+20% power to Grass-type moves' },
  { name: 'Mystic Water',   desc: '+20% power to Water-type moves' },
  { name: 'Occa Berry',     desc: 'Halves damage from one super-effective Fire hit' },
  { name: 'Passho Berry',   desc: 'Halves damage from one super-effective Water hit' },
  { name: 'Poison Barb',    desc: '+20% power to Poison-type moves' },
  { name: 'Quick Claw',     desc: '20% chance to move first regardless of Speed' },
  { name: 'Rindo Berry',    desc: 'Halves damage from one super-effective Grass hit' },
  { name: 'Sharp Beak',     desc: '+20% power to Flying-type moves' },
  { name: 'Shuca Berry',    desc: 'Halves damage from one super-effective Ground hit' },
  { name: 'Silk Scarf',     desc: '+20% power to Normal-type moves' },
  { name: 'Sitrus Berry',   desc: 'Restores 25% max HP when HP drops below 50%' },
  { name: 'Soft Sand',      desc: '+20% power to Ground-type moves' },
  { name: 'White Herb',     desc: 'Restores all stat drops once, then consumed (pairs with Close Combat / Superpower)' },
  { name: 'Yache Berry',    desc: 'Halves damage from one super-effective Ice hit' },
];

const STATS    = ['hp','atk','def','spa','spd','spe'];
const S_LBEL   = { hp:'HP', atk:'Atk', def:'Def', spa:'SpA', spd:'SpD', spe:'Spe' };
const STAT_MAP = { hp:'hp', attack:'atk', defense:'def', 'special-attack':'spa', 'special-defense':'spd', speed:'spe' };

const TYPES = [
  'Normal','Fire','Water','Electric','Grass','Ice',
  'Fighting','Poison','Ground','Flying','Psychic','Bug',
  'Rock','Ghost','Dragon','Dark','Steel','Fairy'
];

const TC = {
  Normal:'#A8A878',Fire:'#F08030',Water:'#6890F0',Electric:'#F8D030',
  Grass:'#78C850',Ice:'#98D8D8',Fighting:'#C03028',Poison:'#A040A0',
  Ground:'#E0C068',Flying:'#A890F0',Psychic:'#F85888',Bug:'#A8B820',
  Rock:'#B8A038',Ghost:'#705898',Dragon:'#7038F8',Dark:'#806858',
  Steel:'#B8B8D0',Fairy:'#EE99AC'
};

/* ── STATE ── */
const mk = () => ({
  name:'', id:null, sprite:null, gender:'M',
  nature:'Hardy', ability:'', item:'',
  moves:['','','',''],
  learnset:[],
  abilitiesList:[],
  evs:{ hp:0, atk:0, def:0, spa:0, spd:0, spe:0 },
  base:{ hp:0, atk:0, def:0, spa:0, spd:0, spe:0 },
  types:[]
});
const myTeam = Array.from({length:6}, mk);
const enTeam = Array.from({length:6}, () => ({
  name:'', id:null, sprite:null, gender:'M', types:[]
}));

const timers = {};

/* ── TAB SWITCHING ── */
document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    const id = btn.dataset.tab;
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(id === 'preview' ? 'preview-section' : id);
    el.classList.add('active');
    if (id === 'preview') renderPreview();
  });
});

/* ── POKÉAPI ── */
async function fetchPoke(name, cb) {
  if (!name.trim()) return cb(null);
  try {
    const r = await fetch(`https://pokeapi.co/api/v2/pokemon/${name.toLowerCase().trim()}`);
    if (!r.ok) return cb(null);
    const d = await r.json();
    const base = {};
    d.stats.forEach(s => { const k = STAT_MAP[s.stat.name]; if (k) base[k] = s.base_stat; });
    const abilities = d.abilities.map(a => ({ name: a.ability.name, hidden: a.is_hidden }));
    const learnset  = d.moves.map(m => m.move.name).sort();
    let forms = [];
    try {
      const sr = await fetch(d.species.url);
      if (sr.ok) {
        const sd = await sr.json();
        if (sd.varieties.length > 1)
          forms = sd.varieties.map(v => ({ name: v.pokemon.name, isDefault: v.is_default }));
      }
    } catch {}
    cb({
      id: d.id,
      slug: d.name,
      sprite: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${d.id}.png`,
      types: d.types.map(t => cap(t.type.name)),
      base,
      abilities,
      learnset,
      forms
    });
  } catch { cb(null); }
}

const cap = s => s.charAt(0).toUpperCase() + s.slice(1);

/* ── SPRITE BOX ── */
function setSprite(boxId, url, isEnemy = false) {
  const box = document.getElementById(boxId);
  if (!box) return;
  if (!url) { box.innerHTML = '<div class="sprite-ph">?</div>'; return; }
  box.innerHTML = `<div class="${isEnemy ? 'spin e-spin' : 'spin'}"></div>`;
  const img = new Image();
  img.src = url;
  img.onload  = () => { box.innerHTML = ''; box.appendChild(img); };
  img.onerror = () => { box.innerHTML = '<div class="sprite-ph">✗</div>'; };
}

/* ── TYPE BADGES ── */
function renderBadges(containerId, types) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = types.map(t =>
    `<span class="tbadge" style="background:${TC[t]}28;color:${TC[t]};border:1px solid ${TC[t]}44">${t}</span>`
  ).join('');
}

/* ── EV TOTAL ── */
const evTotal = evs => Object.values(evs).reduce((a,b)=>a+b, 0);

/* ── SLIDER FILL ── */
function fillSlider(el, extra, cls) {
  const pct = Math.min(100, (extra / 32) * 100);
  let bright;
  if (cls === 'up-track')        bright = '#ff7070';
  else if (cls === 'down-track') bright = '#6aadff';
  else                           bright = '#4cc9f0';
  const trail = 'rgba(255,255,255,0.07)';
  el.style.background = `linear-gradient(to right,${bright} ${pct}%,${trail} ${pct}%)`;
}

/* ── NATURE COLORS ── */
function applyNatureColors(idx) {
  const fx = NAT_FX[myTeam[idx].nature] || {u:null, d:null};
  STATS.forEach(s => {
    const lbl = document.getElementById(`nl-${idx}-${s}`);
    const sld = document.getElementById(`ev-${idx}-${s}`);
    if (!lbl || !sld) return;
    lbl.className = 'ev-lbl';
    let cls = 'p-track';
    if (s === fx.u) { lbl.classList.add('up');   cls = 'up-track'; }
    if (s === fx.d) { lbl.classList.add('down'); cls = 'down-track'; }
    sld.className = `ev-slider ${cls}`;
    fillSlider(sld, myTeam[idx].evs[s], cls);
  });
  updateStats(idx);
}

/* ── BUILD MY TEAM CARD ── */
function buildMyCard(i) {
  const card = document.createElement('div');
  card.className = 'pcard';
  card.style.animationDelay = `${i * 0.07}s`;
  card.innerHTML = `
    <div class="card-head">
      <div class="sprite-box" id="sb-${i}"><div class="sprite-ph">?</div></div>
      <div class="card-id">
        <div class="name-row">
          <div class="ac-wrap">
            <input class="name-input poke-ac" id="pn-${i}" type="text" placeholder="Pokémon name…" autocomplete="off" data-slot="${i}" data-side="my">
            <div class="ac-drop"></div>
          </div>
          <select class="gender-sel" id="pg-${i}">
            <option value="M">♂</option>
            <option value="F">♀</option>
            <option value="N">⚲</option>
          </select>
        </div>
        <select class="form-sel" id="pf-${i}" style="display:none"></select>
        <div class="type-row" id="pt-${i}"></div>
      </div>
    </div>
    <div class="card-body">
      <div class="form-row">
        <div class="form-field">
          <div class="field-label">Ability</div>
          <select class="field-select" id="ab-${i}">
            <option value="">— pick a Pokémon —</option>
          </select>
        </div>
        <div class="form-field">
          <div class="field-label">Held Item</div>
          <div class="ac-wrap">
            <input class="field-input item-ac" id="it-${i}" type="text" placeholder="Search item…" autocomplete="off" data-slot="${i}">
            <div class="ac-drop"></div>
          </div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-field" style="grid-column:1/-1">
          <div class="field-label">Nature</div>
          <select class="field-select" id="na-${i}">
            ${NATURES.map(n=>`<option>${n}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="moves-block">
        <div class="field-label">Moves</div>
        <div class="move-grid">
          ${[0,1,2,3].map(m=>`
            <div class="ac-wrap">
              <input class="move-inp move-ac" id="mv-${i}-${m}" type="text" placeholder="Move ${m+1}" autocomplete="off" data-slot="${i}" data-mi="${m}">
              <div class="ac-drop"></div>
            </div>`).join('')}
        </div>
      </div>
      <div class="ev-block">
        <div class="ev-head">
          <div class="field-label">EVs</div>
          <div class="ev-total-display">Total <span id="evt-${i}">0</span>/66</div>
        </div>
        ${STATS.map(s=>`
          <div class="ev-row">
            <div class="ev-base" id="eb-${i}-${s}">—</div>
            <div class="ev-lbl" id="nl-${i}-${s}">${S_LBEL[s]}</div>
            <input type="range" class="ev-slider p-track" id="ev-${i}-${s}" min="0" max="32" value="0" step="1">
            <div class="ev-val" id="ev-v-${i}-${s}">0</div>
            <div class="ev-stat" id="es-${i}-${s}">—</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  return card;
}

function wireMyCard(i) {
  document.getElementById(`pg-${i}`).addEventListener('change', e => { myTeam[i].gender = e.target.value; });

  document.getElementById(`pf-${i}`).addEventListener('change', e => {
    document.getElementById(`sb-${i}`).innerHTML = '<div class="spin"></div>';
    fetch(`https://pokeapi.co/api/v2/pokemon/${e.target.value}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (!d) return setSprite(`sb-${i}`, null);
        myTeam[i].id = d.id;
        myTeam[i].sprite = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${d.id}.png`;
        myTeam[i].types = d.types.map(t => cap(t.type.name));
        const base = {};
        d.stats.forEach(s => { const k = STAT_MAP[s.stat.name]; if (k) base[k] = s.base_stat; });
        myTeam[i].base = base;
        const abilities = d.abilities.map(a => ({ name: a.ability.name, hidden: a.is_hidden }));
        myTeam[i].learnset = d.moves.map(m => m.move.name).sort();
        populateAbilities(i, abilities);
        resetEvSliders(i);
        setSprite(`sb-${i}`, myTeam[i].sprite, false);
        renderBadges(`pt-${i}`, myTeam[i].types);
        applyNatureColors(i);
      })
      .catch(() => setSprite(`sb-${i}`, null));
  });

  document.getElementById(`na-${i}`).addEventListener('change', e => {
    myTeam[i].nature = e.target.value;
    applyNatureColors(i);
  });

  document.getElementById(`ab-${i}`).addEventListener('change', e => { myTeam[i].ability = e.target.value; });
  document.getElementById(`it-${i}`).addEventListener('input', e => { myTeam[i].item    = e.target.value; });

  STATS.forEach(s => {
    const sld = document.getElementById(`ev-${i}-${s}`);
    const valEl = document.getElementById(`ev-v-${i}-${s}`);
    fillSlider(sld, 0, 'p-track');
    sld.addEventListener('input', e => {
      const basePos   = parseInt(sld.min);
      const rawExtra  = parseInt(e.target.value) - basePos;
      const otherExtras = STATS.filter(x => x !== s).reduce((a, x) => a + myTeam[i].evs[x], 0);
      const extra = Math.min(rawExtra, 32, Math.max(0, 66 - otherExtras));
      e.target.value = basePos + extra;
      myTeam[i].evs[s] = extra;
      valEl.textContent = extra;
      document.getElementById(`evt-${i}`).textContent = evTotal(myTeam[i].evs);
      const cls = e.target.className.split(' ').find(c => c.endsWith('-track')) || 'p-track';
      fillSlider(sld, extra, cls);
      const statEl = document.getElementById(`es-${i}-${s}`);
      if (statEl) {
        const b = myTeam[i].base[s];
        statEl.textContent = b ? computeStat(s, b, extra, myTeam[i].nature) : '—';
      }
    });
  });

  applyNatureColors(i);
}

/* ── BUILD ENEMY CARD ── */
function buildEnemyCard(i) {
  const card = document.createElement('div');
  card.className = 'ecard';
  card.style.animationDelay = `${i * 0.07}s`;
  card.innerHTML = `
    <div class="card-head">
      <div class="sprite-box" id="esb-${i}"><div class="sprite-ph">?</div></div>
      <div class="card-id">
        <div class="name-row">
          <div class="ac-wrap">
            <input class="name-input poke-ac" id="en-${i}" type="text" placeholder="Pokémon name (opt.)…" autocomplete="off" data-slot="${i}" data-side="en">
            <div class="ac-drop"></div>
          </div>
          <select class="gender-sel" id="eg-${i}">
            <option value="M">♂</option>
            <option value="F">♀</option>
            <option value="N">⚲</option>
          </select>
        </div>
        <select class="form-sel" id="ef-${i}" style="display:none"></select>
        <div class="type-row" id="et-${i}"></div>
      </div>
    </div>
    <div class="type-selector" id="ets-${i}">
      ${TYPES.map(t=>`
        <button class="type-btn" data-type="${t}"
          style="color:${TC[t]};border-color:${TC[t]};"
          onclick="toggleType(${i},'${t}',this)">${t}</button>
      `).join('')}
    </div>
  `;
  return card;
}

function wireEnemyCard(i) {
  document.getElementById(`eg-${i}`).addEventListener('change', e => { enTeam[i].gender = e.target.value; });

  document.getElementById(`ef-${i}`).addEventListener('change', e => {
    document.getElementById(`esb-${i}`).innerHTML = '<div class="spin e-spin"></div>';
    fetch(`https://pokeapi.co/api/v2/pokemon/${e.target.value}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (!d) return setSprite(`esb-${i}`, null, true);
        enTeam[i].id = d.id;
        enTeam[i].sprite = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${d.id}.png`;
        const newTypes = d.types.map(t => cap(t.type.name));
        document.querySelectorAll(`#ets-${i} .type-btn`).forEach(b => b.classList.remove('sel'));
        enTeam[i].types = newTypes;
        newTypes.forEach(t => {
          const btn = document.querySelector(`#ets-${i} [data-type="${t}"]`);
          if (btn) btn.classList.add('sel');
        });
        setSprite(`esb-${i}`, enTeam[i].sprite, true);
        renderBadges(`et-${i}`, newTypes);
      })
      .catch(() => setSprite(`esb-${i}`, null, true));
  });
}

window.toggleType = function(i, type, btn) {
  if (enTeam[i].types.includes(type)) {
    enTeam[i].types = enTeam[i].types.filter(t => t !== type);
    btn.classList.remove('sel');
  } else {
    if (enTeam[i].types.length >= 2) return;
    enTeam[i].types.push(type);
    btn.classList.add('sel');
  }
  renderBadges(`et-${i}`, enTeam[i].types);
};

/* ── PREVIEW ── */
function renderPreview() {
  const sec = document.getElementById('preview-section');

  const myRow = myTeam.map((p, i) => {
    const delay = `animation-delay:${i * 0.08}s`;
    if (p.sprite) return `
      <div class="pv-mon" style="${delay}">
        <img class="pv-img" src="${p.sprite}" alt="${p.name}">
        <div class="pv-name">${p.name || '—'}</div>
        <div class="pv-types">${p.types.map(t=>`<div class="pv-dot" style="background:${TC[t]}" title="${t}"></div>`).join('')}</div>
      </div>`;
    return `<div class="pv-mon" style="${delay}"><div class="pv-empty">?</div><div class="pv-name">—</div></div>`;
  }).join('');

  const enRow = enTeam.map((p, i) => {
    const delay = `animation-delay:${(i + 6) * 0.08}s`;
    if (p.sprite) return `
      <div class="pv-mon" style="${delay}">
        <img class="pv-img" src="${p.sprite}" alt="${p.name || '?'}">
        <div class="pv-name">${p.name || '?'}</div>
        <div class="pv-types">${p.types.map(t=>`<div class="pv-dot" style="background:${TC[t]}" title="${t}"></div>`).join('')}</div>
      </div>`;
    if (p.types.length) {
      const c = TC[p.types[0]];
      return `
        <div class="pv-mon" style="${delay}">
          <div class="pv-type-preview" style="border-color:${c}44">
            ${p.types.map(t=>`<div class="tbadge" style="background:${TC[t]}28;color:${TC[t]};border:1px solid ${TC[t]}55;font-size:9px">${t}</div>`).join('')}
          </div>
          <div class="pv-name">Unknown</div>
          <div class="pv-types">${p.types.map(t=>`<div class="pv-dot" style="background:${TC[t]}"></div>`).join('')}</div>
        </div>`;
    }
    return `<div class="pv-mon" style="${delay}"><div class="pv-empty">?</div><div class="pv-name">—</div></div>`;
  }).join('');

  const notes = buildNotes();

  sec.innerHTML = `
    <div class="preview-arena">
      <div class="p-side">
        <div class="side-label">Your Team</div>
        <div class="poke-row">${myRow}</div>
      </div>
      <div class="vs-col"><div class="vs-text">VS</div></div>
      <div class="e-side">
        <div class="side-label">Opponent</div>
        <div class="poke-row">${enRow}</div>
      </div>
    </div>
    <div class="matchup-box">
      <div class="matchup-title">Scout Notes</div>
      ${notes}
    </div>
  `;
}

function buildNotes() {
  const notes = [];

  const myNames = myTeam.filter(p=>p.name).map(p=>cap(p.name));
  if (myNames.length) notes.push(`Registered: ${myNames.join(', ')}`);

  const hasAttract = myTeam.some(p => p.moves.some(m => m.toLowerCase().includes('attract')));
  if (hasAttract) notes.push('You have <strong>Attract</strong> — track enemy gender. Fails on genderless Pokémon; both same-gender won\'t be affected.');

  const hasRivalry = myTeam.some(p => p.ability.toLowerCase() === 'rivalry');
  if (hasRivalry) notes.push('<strong>Rivalry</strong> detected — +25% dmg vs same gender, −25% vs opposite. Gender scouting is critical.');

  const enAllTypes = [...new Set(enTeam.flatMap(p => p.types))];
  if (enAllTypes.length) notes.push(`Enemy type coverage: <strong>${enAllTypes.join(', ')}</strong>`);

  const myTypes = [...new Set(myTeam.flatMap(p=>p.types))];
  if (myTypes.length && enAllTypes.length) {
    const weak = enAllTypes.filter(t => myTypes.includes(t));
    if (weak.length) notes.push(`Type overlap (both sides have): ${weak.join(', ')} — mirror match-ups possible.`);
  }

  if (!notes.length) notes.push('Add Pokémon to your team and scout enemy types to see analysis here.');
  return notes.map(n=>`<div class="note">${n}</div>`).join('');
}

/* ── STAT CALCULATION ── */
function computeStat(stat, base, ev, nature) {
  const nm = NAT_FX[nature] || { u: null, d: null };
  const inner = Math.floor((2 * base + 31 + Math.floor(ev / 4)) * 50 / 100);
  if (stat === 'hp') return base === 1 ? 1 : inner + 60;
  let val = Math.floor((inner + 5));
  if (nm.u === stat) val = Math.floor(val * 1.1);
  if (nm.d === stat) val = Math.floor(val * 0.9);
  return val;
}

const fmtName = s => s.split('-').map(w => w[0].toUpperCase() + w.slice(1)).join(' ');

function populateAbilities(i, abilities) {
  const sel = document.getElementById(`ab-${i}`);
  if (!sel) return;
  myTeam[i].abilitiesList = abilities;
  sel.innerHTML = abilities.map(a =>
    `<option value="${a.name}">${fmtName(a.name)}${a.hidden ? ' ★' : ''}</option>`
  ).join('');
  myTeam[i].ability = abilities.length ? abilities[0].name : '';
  sel.value = myTeam[i].ability;
}

function resetEvSliders(i) {
  STATS.forEach(s => {
    const basePos = Math.round((myTeam[i].base[s] || 0) / 255 * 252 / 4) * 4;
    myTeam[i].evs[s] = 0;
    const sld   = document.getElementById(`ev-${i}-${s}`);
    const valEl = document.getElementById(`ev-v-${i}-${s}`);
    if (sld) { sld.min = basePos; sld.max = basePos + 32; sld.value = basePos; }
    if (valEl) valEl.textContent = '0';
  });
  const totEl = document.getElementById(`evt-${i}`);
  if (totEl) totEl.textContent = '0';
}

function updateStats(i) {
  STATS.forEach(s => {
    const baseEl = document.getElementById(`eb-${i}-${s}`);
    const statEl = document.getElementById(`es-${i}-${s}`);
    if (!baseEl || !statEl) return;
    const b = myTeam[i].base[s];
    baseEl.textContent = b || '—';
    statEl.textContent = b ? computeStat(s, b, myTeam[i].evs[s], myTeam[i].nature) : '—';
  });
}

/* ── AUTOCOMPLETE ── */
let allPoke = null;

async function loadAllPoke() {
  if (allPoke) return;
  try {
    const r = await fetch('https://pokeapi.co/api/v2/pokemon?limit=2000');
    const d = await r.json();
    allPoke = d.results;
  } catch {}
}

function pickPoke(inp, slug) {
  const side = inp.dataset.side;
  const i = +inp.dataset.slot;
  const isEn = side === 'en';
  const sprId = isEn ? `esb-${i}` : `sb-${i}`;
  const typId = isEn ? `et-${i}` : `pt-${i}`;
  const frmId = isEn ? `ef-${i}` : `pf-${i}`;

  if (isEn) {
    enTeam[i].name = inp.value;
    enTeam[i].types = [];
    document.querySelectorAll(`#ets-${i} .type-btn`).forEach(b => b.classList.remove('sel'));
  } else {
    myTeam[i].name = inp.value;
  }

  document.getElementById(sprId).innerHTML = `<div class="${isEn ? 'spin e-spin' : 'spin'}"></div>`;

  fetchPoke(slug, d => {
    if (!d) { setSprite(sprId, null, isEn); return; }
    if (isEn) {
      enTeam[i].id = d.id; enTeam[i].sprite = d.sprite; enTeam[i].types = d.types;
      setSprite(sprId, d.sprite, true);
      d.types.forEach(t => {
        const btn = document.querySelector(`#ets-${i} [data-type="${t}"]`);
        if (btn) btn.classList.add('sel');
      });
      renderBadges(typId, d.types);
    } else {
      myTeam[i].id = d.id; myTeam[i].sprite = d.sprite; myTeam[i].types = d.types;
      myTeam[i].base = d.base;
      myTeam[i].learnset = d.learnset;
      populateAbilities(i, d.abilities);
      resetEvSliders(i);
      setSprite(sprId, d.sprite, false);
      renderBadges(typId, d.types);
      applyNatureColors(i);
    }
    const frm = document.getElementById(frmId);
    if (d.forms.length > 1) {
      frm.innerHTML = d.forms.map(f =>
        `<option value="${f.name}"${f.name === d.slug ? ' selected' : ''}>${f.name.replace(/-/g, ' ')}</option>`
      ).join('');
      frm.style.display = '';
    } else {
      frm.style.display = 'none'; frm.innerHTML = '';
    }
  });
}

function pickMove(inp, slug) {
  myTeam[+inp.dataset.slot].moves[+inp.dataset.mi] = slug;
}

document.addEventListener('input', e => {
  const inp = e.target;
  const q   = inp.value.trim().toLowerCase();
  const drop = inp.nextElementSibling;

  if (inp.classList.contains('poke-ac')) {
    if (!q) {
      drop.style.display = 'none';
      const side = inp.dataset.side; const i = +inp.dataset.slot;
      if (side === 'my') {
        setSprite(`sb-${i}`, null); renderBadges(`pt-${i}`, []);
        myTeam[i].sprite = null; myTeam[i].types = []; myTeam[i].ability = '';
        myTeam[i].learnset = []; myTeam[i].moves = ['','','',''];
        const pf = document.getElementById(`pf-${i}`);
        pf.style.display = 'none'; pf.innerHTML = '';
        const ab = document.getElementById(`ab-${i}`);
        if (ab) ab.innerHTML = '<option value="">— pick a Pokémon —</option>';
        [0,1,2,3].forEach(m => { const mv = document.getElementById(`mv-${i}-${m}`); if (mv) mv.value = ''; });
      } else {
        setSprite(`esb-${i}`, null, true); enTeam[i].sprite = null;
        const ef = document.getElementById(`ef-${i}`);
        ef.style.display = 'none'; ef.innerHTML = '';
      }
      return;
    }
    if (!allPoke) { drop.style.display = 'none'; return; }
    const hits = allPoke.filter(p => p.name.includes(q)).slice(0, 12);
    drop.style.display = hits.length ? 'block' : 'none';
    drop.innerHTML = hits.map(p =>
      `<div class="ac-item" data-slug="${p.name}">${p.name.replace(/-/g, ' ')}</div>`
    ).join('');
    return;
  }

  if (inp.classList.contains('move-ac')) {
    if (!q) {
      drop.style.display = 'none';
      myTeam[+inp.dataset.slot].moves[+inp.dataset.mi] = '';
      return;
    }
    const pool = myTeam[+inp.dataset.slot].learnset;
    if (!pool.length) { drop.style.display = 'none'; return; }
    const hits = pool.filter(s => s.includes(q) || fmtName(s).toLowerCase().includes(q)).slice(0, 10);
    drop.style.display = hits.length ? 'block' : 'none';
    drop.innerHTML = hits.map(s => `<div class="ac-item" data-slug="${s}">${fmtName(s)}</div>`).join('');
  }

  if (inp.classList.contains('item-ac')) {
    if (!q) { drop.style.display = 'none'; return; }
    const hits = ITEMS.filter(it => it.name.toLowerCase().includes(q)).slice(0, 10);
    drop.style.display = hits.length ? 'block' : 'none';
    drop.innerHTML = hits.map(it =>
      `<div class="ac-item" data-slug="${it.name}">${it.name}</div>`
    ).join('');
  }
});

document.addEventListener('click', e => {
  if (!e.target.closest('.ac-wrap')) {
    document.querySelectorAll('.ac-drop').forEach(d => { d.style.display = 'none'; });
    return;
  }
  if (e.target.classList.contains('ac-item')) {
    const wrap = e.target.closest('.ac-wrap');
    const slug = e.target.dataset.slug;
    wrap.querySelector('.ac-drop').style.display = 'none';
    const pokeInp = wrap.querySelector('.poke-ac');
    const moveInp = wrap.querySelector('.move-ac');
    const itemInp = wrap.querySelector('.item-ac');
    if (pokeInp) {
      pokeInp.value = slug.replace(/-/g, ' ');
      pickPoke(pokeInp, slug);
    } else if (moveInp) {
      moveInp.value = fmtName(slug);
      pickMove(moveInp, slug);
    } else if (itemInp) {
      itemInp.value = slug;
      myTeam[+itemInp.dataset.slot].item = slug;
    }
  }
});

/* ── SAVE / LOAD ── */
function saveTeam() {
  localStorage.setItem('pokeplan_team', JSON.stringify(myTeam));
  const btn = document.getElementById('save-btn');
  if (!btn) return;
  btn.textContent = 'Saved!';
  btn.classList.add('saved');
  setTimeout(() => { btn.textContent = 'Save Team'; btn.classList.remove('saved'); }, 1500);
}

function loadTeam() {
  let saved;
  try { saved = JSON.parse(localStorage.getItem('pokeplan_team')); } catch { return; }
  if (!saved) return;
  saved.forEach((p, i) => {
    if (!p.name) return;
    Object.assign(myTeam[i], p);

    const nameInp = document.getElementById(`pn-${i}`);
    if (nameInp) nameInp.value = p.name;
    document.getElementById(`pg-${i}`).value = p.gender;
    document.getElementById(`na-${i}`).value = p.nature;
    const itemInp = document.getElementById(`it-${i}`);
    if (itemInp) itemInp.value = p.item;
    p.moves.forEach((m, mi) => {
      const mv = document.getElementById(`mv-${i}-${mi}`);
      if (mv) mv.value = m ? fmtName(m) : '';
    });

    if (p.sprite) setSprite(`sb-${i}`, p.sprite, false);
    if (p.types.length) renderBadges(`pt-${i}`, p.types);

    if (p.abilitiesList && p.abilitiesList.length) {
      populateAbilities(i, p.abilitiesList);
      const ab = document.getElementById(`ab-${i}`);
      if (ab) { ab.value = p.ability; myTeam[i].ability = p.ability; }
    }

    STATS.forEach(s => {
      const baseEl = document.getElementById(`eb-${i}-${s}`);
      if (baseEl) baseEl.textContent = p.base[s] || '—';
    });

    if (Object.values(p.base).some(v => v > 0)) {
      resetEvSliders(i);
      STATS.forEach(s => {
        const extra = p.evs[s] || 0;
        myTeam[i].evs[s] = extra;
        const sld = document.getElementById(`ev-${i}-${s}`);
        const valEl = document.getElementById(`ev-v-${i}-${s}`);
        if (sld) sld.value = parseInt(sld.min) + extra;
        if (valEl) valEl.textContent = extra;
      });
      document.getElementById(`evt-${i}`).textContent = evTotal(myTeam[i].evs);
    }

    applyNatureColors(i);
  });
}

/* ── INIT ── */
(function init() {
  const mg = document.getElementById('my-grid');
  const eg = document.getElementById('en-grid');
  for (let i = 0; i < 6; i++) {
    mg.appendChild(buildMyCard(i)); wireMyCard(i);
    eg.appendChild(buildEnemyCard(i)); wireEnemyCard(i);
  }
  loadAllPoke();
  loadTeam();
})();
