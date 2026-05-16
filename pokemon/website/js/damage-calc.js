// ── Constants ─────────────────────────────────────────────────────────────────
const NATURES={
  none:{a:1,d:1,sa:1,sd:1,sp:1},
  hardy:{a:1,d:1,sa:1,sd:1,sp:1},lonely:{a:1.1,d:.9,sa:1,sd:1,sp:1},
  brave:{a:1.1,d:1,sa:1,sd:1,sp:.9},adamant:{a:1.1,d:1,sa:.9,sd:1,sp:1},
  naughty:{a:1.1,d:1,sa:1,sd:.9,sp:1},bold:{a:.9,d:1.1,sa:1,sd:1,sp:1},
  docile:{a:1,d:1,sa:1,sd:1,sp:1},relaxed:{a:1,d:1.1,sa:1,sd:1,sp:.9},
  impish:{a:1,d:1.1,sa:.9,sd:1,sp:1},lax:{a:1,d:1.1,sa:1,sd:.9,sp:1},
  timid:{a:.9,d:1,sa:1,sd:1,sp:1.1},hasty:{a:1,d:.9,sa:1,sd:1,sp:1.1},
  serious:{a:1,d:1,sa:1,sd:1,sp:1},jolly:{a:1,d:1,sa:.9,sd:1,sp:1.1},
  naive:{a:1,d:1,sa:1,sd:.9,sp:1.1},modest:{a:.9,d:1,sa:1.1,sd:1,sp:1},
  mild:{a:1,d:.9,sa:1.1,sd:1,sp:1},quiet:{a:1,d:1,sa:1.1,sd:1,sp:.9},
  rash:{a:1,d:1,sa:1.1,sd:.9,sp:1},bashful:{a:1,d:1,sa:1,sd:1,sp:1},
  calm:{a:.9,d:1,sa:1,sd:1.1,sp:1},gentle:{a:1,d:.9,sa:1,sd:1.1,sp:1},
  sassy:{a:1,d:1,sa:1,sd:1.1,sp:.9},careful:{a:1,d:1,sa:.9,sd:1.1,sp:1},
  quirky:{a:1,d:1,sa:1,sd:1,sp:1}
};
const NAT_LABEL={a:'Atk',d:'Def',sa:'SpA',sd:'SpD',sp:'Spe'};

const TYPE_EFF={
  normal:{rock:.5,ghost:0,steel:.5},
  fire:{fire:.5,water:.5,grass:2,ice:2,bug:2,rock:.5,dragon:.5,steel:2},
  water:{fire:2,water:.5,grass:.5,ground:2,rock:2,dragon:.5},
  electric:{water:2,electric:.5,grass:.5,ground:0,flying:2,dragon:.5},
  grass:{fire:.5,water:2,grass:.5,poison:.5,ground:2,flying:.5,bug:.5,rock:2,dragon:.5,steel:.5},
  ice:{fire:.5,water:.5,grass:2,ice:.5,ground:2,flying:2,dragon:2,steel:.5},
  fighting:{normal:2,ice:2,poison:.5,flying:.5,psychic:.5,bug:.5,rock:2,ghost:0,dark:2,steel:2,fairy:.5},
  poison:{grass:2,poison:.5,ground:.5,rock:.5,ghost:.5,steel:0,fairy:2},
  ground:{fire:2,electric:2,grass:.5,poison:2,flying:0,bug:.5,rock:2,steel:2},
  flying:{electric:.5,grass:2,fighting:2,bug:2,rock:.5,steel:.5},
  psychic:{fighting:2,poison:2,psychic:.5,dark:0,steel:.5},
  bug:{fire:.5,grass:2,fighting:.5,poison:.5,flying:.5,psychic:2,ghost:.5,dark:2,steel:.5,fairy:.5},
  rock:{fire:2,ice:2,fighting:.5,ground:.5,flying:2,bug:2,steel:.5},
  ghost:{normal:0,psychic:2,ghost:2,dark:.5},
  dragon:{dragon:2,steel:.5,fairy:0},
  dark:{fighting:.5,psychic:2,ghost:2,dark:.5,fairy:.5},
  steel:{fire:.5,water:.5,electric:.5,ice:2,rock:2,steel:.5,fairy:2},
  fairy:{fire:.5,fighting:2,poison:.5,dragon:2,dark:2,steel:.5}
};

const STAT_KEYS=['hp','atk','def','spa','spd','spe'];
const STAT_LABEL={hp:'HP',atk:'Atk',def:'Def',spa:'SpA',spd:'SpD',spe:'Spe'};
const API_STAT={hp:'hp',attack:'atk',defense:'def','special-attack':'spa','special-defense':'spd',speed:'spe'};

const ITEMS=[
  {slug:'choice-band',name:'Choice Band'},{slug:'choice-specs',name:'Choice Specs'},{slug:'choice-scarf',name:'Choice Scarf'},
  {slug:'life-orb',name:'Life Orb'},{slug:'expert-belt',name:'Expert Belt'},
  {slug:'muscle-band',name:'Muscle Band'},{slug:'wise-glasses',name:'Wise Glasses'},
  {slug:'punching-glove',name:'Punching Glove'},{slug:'throat-spray',name:'Throat Spray'},{slug:'loaded-dice',name:'Loaded Dice'},
  {slug:'assault-vest',name:'Assault Vest'},{slug:'eviolite',name:'Eviolite'},
  {slug:'rocky-helmet',name:'Rocky Helmet'},{slug:'air-balloon',name:'Air Balloon'},
  {slug:'leftovers',name:'Leftovers'},{slug:'black-sludge',name:'Black Sludge'},{slug:'shell-bell',name:'Shell Bell'},
  {slug:'focus-sash',name:'Focus Sash'},{slug:'heavy-duty-boots',name:'Heavy-Duty Boots'},
  {slug:'clear-amulet',name:'Clear Amulet'},{slug:'covert-cloak',name:'Covert Cloak'},
  {slug:'safety-goggles',name:'Safety Goggles'},{slug:'shed-shell',name:'Shed Shell'},
  {slug:'weakness-policy',name:'Weakness Policy'},{slug:'white-herb',name:'White Herb'},
  {slug:'power-herb',name:'Power Herb'},{slug:'mental-herb',name:'Mental Herb'},
  {slug:'red-card',name:'Red Card'},{slug:'eject-button',name:'Eject Button'},{slug:'eject-pack',name:'Eject Pack'},
  {slug:'scope-lens',name:'Scope Lens'},{slug:'razor-claw',name:'Razor Claw'},
  {slug:'wide-lens',name:'Wide Lens'},{slug:'zoom-lens',name:'Zoom Lens'},
  {slug:'kings-rock',name:"King's Rock"},{slug:'razor-fang',name:'Razor Fang'},
  {slug:'lum-berry',name:'Lum Berry'},{slug:'sitrus-berry',name:'Sitrus Berry'},
  {slug:'charcoal',name:'Charcoal'},{slug:'mystic-water',name:'Mystic Water'},
  {slug:'miracle-seed',name:'Miracle Seed'},{slug:'magnet',name:'Magnet'},
  {slug:'never-melt-ice',name:'Never-Melt Ice'},{slug:'black-belt',name:'Black Belt'},
  {slug:'poison-barb',name:'Poison Barb'},{slug:'soft-sand',name:'Soft Sand'},
  {slug:'sharp-beak',name:'Sharp Beak'},{slug:'twisted-spoon',name:'Twisted Spoon'},
  {slug:'silver-powder',name:'Silver Powder'},{slug:'hard-stone',name:'Hard Stone'},
  {slug:'spell-tag',name:'Spell Tag'},{slug:'dragon-fang',name:'Dragon Fang'},
  {slug:'black-glasses',name:'Black Glasses'},{slug:'metal-coat',name:'Metal Coat'},
  {slug:'silk-scarf',name:'Silk Scarf'},{slug:'fairy-feather',name:'Fairy Feather'},
  {slug:'flame-plate',name:'Flame Plate'},{slug:'splash-plate',name:'Splash Plate'},
  {slug:'meadow-plate',name:'Meadow Plate'},{slug:'zap-plate',name:'Zap Plate'},
  {slug:'icicle-plate',name:'Icicle Plate'},{slug:'fist-plate',name:'Fist Plate'},
  {slug:'toxic-plate',name:'Toxic Plate'},{slug:'earth-plate',name:'Earth Plate'},
  {slug:'sky-plate',name:'Sky Plate'},{slug:'mind-plate',name:'Mind Plate'},
  {slug:'insect-plate',name:'Insect Plate'},{slug:'stone-plate',name:'Stone Plate'},
  {slug:'spooky-plate',name:'Spooky Plate'},{slug:'draco-plate',name:'Draco Plate'},
  {slug:'dread-plate',name:'Dread Plate'},{slug:'iron-plate',name:'Iron Plate'},{slug:'pixie-plate',name:'Pixie Plate'},
  {slug:'occa-berry',name:'Occa Berry'},{slug:'passho-berry',name:'Passho Berry'},
  {slug:'wacan-berry',name:'Wacan Berry'},{slug:'rindo-berry',name:'Rindo Berry'},
  {slug:'yache-berry',name:'Yache Berry'},{slug:'chople-berry',name:'Chople Berry'},
  {slug:'kebia-berry',name:'Kebia Berry'},{slug:'shuca-berry',name:'Shuca Berry'},
  {slug:'coba-berry',name:'Coba Berry'},{slug:'payapa-berry',name:'Payapa Berry'},
  {slug:'tanga-berry',name:'Tanga Berry'},{slug:'charti-berry',name:'Charti Berry'},
  {slug:'kasib-berry',name:'Kasib Berry'},{slug:'haban-berry',name:'Haban Berry'},
  {slug:'colbur-berry',name:'Colbur Berry'},{slug:'babiri-berry',name:'Babiri Berry'},
  {slug:'roseli-berry',name:'Roseli Berry'},{slug:'chilan-berry',name:'Chilan Berry'},
];

// ── State ──────────────────────────────────────────────────────────────────────
const S={
  my: Array.from({length:6},()=>mkP('my')),
  en: Array.from({length:6},()=>mkP('en')),
  allPoke:null, moveCache:{}, pokeCache:{},
  weather:'none', terrain:'none',
  screens:{reflect:false,lightscreen:false,auroraveil:false},
  crit:false
};

function mkP(side){
  return{slug:'',name:'',types:[],base:{hp:0,atk:0,def:0,spa:0,spd:0,spe:0},
    nature:'none',ability:'',item:'',abilities:[],
    ivs:{hp:31,atk:31,def:31,spa:31,spd:31,spe:31},
    evs:{hp:0,atk:0,def:0,spa:0,spd:0,spe:0},
    moves:['','','',''],mdata:[null,null,null,null],
    stages:{atk:0,def:0,spa:0,spd:0},
    open:false,sprite:null,fullHP:true};
}

// ── API ───────────────────────────────────────────────────────────────────────
async function loadAllPoke(){
  if(S.allPoke) return;
  const r=await fetch('https://pokeapi.co/api/v2/pokemon?limit=2000');
  const d=await r.json();
  S.allPoke=d.results.map(p=>({slug:p.name,name:fmt(p.name)}));
}

async function loadPoke(slug){
  if(S.pokeCache[slug]) return S.pokeCache[slug];
  let r=await fetch(`https://pokeapi.co/api/v2/pokemon/${slug}`);
  if(!r.ok){
    const sr=await fetch(`https://pokeapi.co/api/v2/pokemon-species/${slug}`);
    if(!sr.ok) return null;
    const sd=await sr.json();
    const def=sd.varieties?.find(v=>v.is_default);
    if(!def) return null;
    r=await fetch(def.pokemon.url);
    if(!r.ok) return null;
  }
  const d=await r.json();
  const res={
    slug:d.name,name:fmt(d.name),
    types:d.types.map(t=>t.type.name),
    base:Object.fromEntries(d.stats.map(s=>[API_STAT[s.stat.name],s.base_stat])),
    sprite:d.sprites.front_default,
    learnset:d.moves.map(m=>m.move.name),
    abilities:d.abilities.map(a=>a.ability.name)
  };
  S.pokeCache[slug]=res; return res;
}

async function loadMove(slug){
  if(S.moveCache[slug]) return S.moveCache[slug];
  const r=await fetch(`https://pokeapi.co/api/v2/move/${slug}`);
  if(!r.ok) return null;
  const d=await r.json();
  const meta=d.meta||{};
  const res={slug:d.name,name:fmt(d.name),type:d.type.name,
    dc:d.damage_class?.name,power:d.power,acc:d.accuracy,pp:d.pp,pri:d.priority,
    flags:(d.flags||[]).map(f=>f.name),
    recoil:(meta.drain||0)<0,
    secondary:(meta.ailment_chance||0)>0||(meta.stat_chance||0)>0||(meta.flinch_chance||0)>0};
  S.moveCache[slug]=res; return res;
}

function fmt(s){return s.split('-').map(w=>w[0].toUpperCase()+w.slice(1)).join(' ')}
function norm(s){return(s||'').toLowerCase().trim().replace(/[\s_]+/g,'-')}

// ── Damage Engine ──────────────────────────────────────────────────────────────
function calcHP(base,iv,ev){
  if(base===1) return 1;
  return Math.floor((2*base+iv)*50/100)+60+ev;
}
function calcStat(base,iv,ev,nm){
  return Math.floor((Math.floor((2*base+iv)*50/100)+5)*nm)+ev;
}

function typeEff(mt,dts){
  let m=1; const row=TYPE_EFF[mt.toLowerCase()]||{};
  for(const dt of dts) m*=(row[dt.toLowerCase()]??1);
  return m;
}

function stab(mt,atypes,ability){
  if(!atypes.some(t=>t.toLowerCase()===mt.toLowerCase())) return 1;
  return norm(ability)==='adaptability'?2:1.5;
}

function atkItemMult(item,mv,eff){
  const i=norm(item); const t=mv.type.toLowerCase(); const dc=mv.dc;
  const flags=mv.flags||[];
  if(i==='choice-band'&&dc==='physical') return 1.5;
  if(i==='choice-specs'&&dc==='special') return 1.5;
  if(i==='life-orb') return 1.3;
  if(i==='expert-belt'&&eff>1) return 1.2;
  if(i==='muscle-band'&&dc==='physical') return 1.1;
  if(i==='wise-glasses'&&dc==='special') return 1.1;
  if(i==='punching-glove'&&flags.includes('punch')) return 1.1;
  const TI={charcoal:'fire','mystic-water':'water','miracle-seed':'grass',magnet:'electric',
    'never-melt-ice':'ice','black-belt':'fighting','poison-barb':'poison','soft-sand':'ground',
    'sharp-beak':'flying','twisted-spoon':'psychic','silver-powder':'bug','hard-stone':'rock',
    'spell-tag':'ghost','dragon-fang':'dragon','black-glasses':'dark','metal-coat':'steel',
    'silk-scarf':'normal','fairy-feather':'fairy','flame-plate':'fire','splash-plate':'water',
    'meadow-plate':'grass','zap-plate':'electric','icicle-plate':'ice','fist-plate':'fighting',
    'toxic-plate':'poison','earth-plate':'ground','sky-plate':'flying','mind-plate':'psychic',
    'insect-plate':'bug','stone-plate':'rock','spooky-plate':'ghost','draco-plate':'dragon',
    'dread-plate':'dark','iron-plate':'steel','pixie-plate':'fairy'};
  if(TI[i]===t) return 1.2;
  return 1;
}

function defItemMult(item,sk){
  const i=norm(item);
  if(i==='assault-vest'&&sk==='spd') return 1.5;
  if(i==='eviolite'&&(sk==='def'||sk==='spd')) return 1.5;
  return 1;
}

function defBerryMult(item,mt,eff){
  const i=norm(item); const t=mt.toLowerCase();
  const BERRIES={
    'occa-berry':'fire','passho-berry':'water','wacan-berry':'electric',
    'rindo-berry':'grass','yache-berry':'ice','chople-berry':'fighting',
    'kebia-berry':'poison','shuca-berry':'ground','coba-berry':'flying',
    'payapa-berry':'psychic','tanga-berry':'bug','charti-berry':'rock',
    'kasib-berry':'ghost','haban-berry':'dragon','colbur-berry':'dark',
    'babiri-berry':'steel','roseli-berry':'fairy'
  };
  if(BERRIES[i]===t&&eff>1) return 0.5;
  if(i==='chilan-berry'&&t==='normal') return 0.5;
  return 1;
}

function atkAbiStatMult(ability){
  const a=norm(ability);
  if(a==='huge-power'||a==='pure-power') return 2;
  if(a==='hustle'||a==='gorilla-tactics') return 1.5;
  return 1;
}

function atkAbiMult(ability,mv,eff){
  const a=norm(ability); const t=mv.type.toLowerCase();
  const flags=mv.flags||[];
  if(a==='transistor'&&t==='electric') return 1.5;
  if(a==='dragons-maw'&&t==='dragon') return 1.5;
  if((a==='steelworker'||a==='steely-spirit')&&t==='steel') return 1.5;
  if(a==='water-bubble'&&t==='water') return 2;
  if((a==='aerilate'||a==='pixilate'||a==='refrigerate'||a==='galvanize')&&t==='normal') return 1.2;
  if(a==='technician'&&mv.power&&mv.power<=60) return 1.5;
  if(a==='tinted-lens'&&eff>0&&eff<1) return 2;
  if(a==='neuroforce'&&eff>1) return 1.25;
  if(a==='tough-claws'&&flags.includes('contact')) return 1.3;
  if(a==='strong-jaw'&&flags.includes('bite')) return 1.5;
  if(a==='iron-fist'&&flags.includes('punch')) return 1.2;
  if(a==='mega-launcher'&&flags.includes('pulse')) return 1.5;
  if(a==='punk-rock'&&flags.includes('sound')) return 1.3;
  if(a==='reckless'&&mv.recoil) return 1.2;
  if(a==='sheer-force'&&mv.secondary) return 1.3;
  return 1;
}

function defAbiMult(ability,mv,eff,fullHP){
  const a=norm(ability); const t=mv.type.toLowerCase();
  const dc=mv.dc; const flags=mv.flags||[];
  const immune={
    'flash-fire':'fire','water-absorb':'water','dry-skin':'water',
    'volt-absorb':'electric','storm-drain':'water','sap-sipper':'grass',
    'levitate':'ground','earth-eater':'ground','wind-rider':'flying',
    'lightning-rod':'electric','motor-drive':'electric'
  };
  if(immune[a]===t) return 0;
  if(a==='soundproof'&&flags.includes('sound')) return 0;
  if(a==='bulletproof'&&flags.includes('bullet')) return 0;
  if(a==='wonder-guard') return 1;
  let m=1;
  if(a==='thick-fat'&&(t==='fire'||t==='ice')) m*=0.5;
  if(a==='heatproof'&&t==='fire') m*=0.5;
  if(a==='water-bubble'&&t==='fire') m*=0.5;
  if(a==='fur-coat'&&dc==='physical') m*=0.5;
  if(a==='fluffy'){
    if(flags.includes('contact')) m*=0.5;
    if(t==='fire') m*=2;
  }
  if((a==='filter'||a==='solid-rock'||a==='prism-armor')&&eff>1) m*=0.75;
  if(a==='ice-scales'&&dc==='special') m*=0.5;
  if(a==='punk-rock'&&flags.includes('sound')) m*=0.5;
  if(a==='dry-skin'&&t==='fire') m*=1.25;
  if(a==='purifying-salt'&&t==='ghost') m*=0.5;
  if((a==='multiscale'||a==='shadow-shield')&&fullHP) m*=0.5;
  return m;
}

function rolls16(atk,def,pow){
  const base=Math.floor(Math.floor(22*pow*atk/def)/50)+2;
  return Array.from({length:16},(_,i)=>Math.floor(base*(85+i)/100));
}

function stageMult(n){return n>=0?(2+n)/2:2/(2-n)}

function weatherMult(mt){
  const t=mt.toLowerCase();
  if(S.weather==='sun'&&t==='fire') return 1.5;
  if(S.weather==='sun'&&t==='water') return 0.5;
  if(S.weather==='rain'&&t==='water') return 1.5;
  if(S.weather==='rain'&&t==='fire') return 0.5;
  return 1;
}

function terrainMult(mt){
  const t=mt.toLowerCase();
  if(S.terrain==='electric'&&t==='electric') return 1.3;
  if(S.terrain==='grassy'&&t==='grass') return 1.3;
  if(S.terrain==='grassy'&&t==='ground') return 0.5;
  if(S.terrain==='psychic'&&t==='psychic') return 1.3;
  if(S.terrain==='misty'&&t==='dragon') return 0.5;
  return 1;
}

function screenMult(dc,isCrit){
  if(isCrit) return 1;
  if(S.screens.auroraveil) return 0.5;
  if(dc==='physical'&&S.screens.reflect) return 0.5;
  if(dc==='special'&&S.screens.lightscreen) return 0.5;
  return 1;
}

function getWorstCaseItem(mv,eff){
  const t=mv.type.toLowerCase();
  if(t==='normal') return 'chilan-berry';
  if(eff>1){
    const B={fire:'occa-berry',water:'passho-berry',electric:'wacan-berry',
      grass:'rindo-berry',ice:'yache-berry',fighting:'chople-berry',
      poison:'kebia-berry',ground:'shuca-berry',flying:'coba-berry',
      psychic:'payapa-berry',bug:'tanga-berry',rock:'charti-berry',
      ghost:'kasib-berry',dragon:'haban-berry',dark:'colbur-berry',
      steel:'babiri-berry',fairy:'roseli-berry'};
    return B[t]||null;
  }
  if(mv.dc==='special') return 'assault-vest';
  return null;
}

function calc(atker,mvSlug,defer,evOver=null,isCrit=false){
  const mv=atker.mdata.find(m=>m?.slug===mvSlug);
  if(!mv) return null;
  if(!mv.power) return{status:true,move:mv};

  const nat=NATURES[atker.nature]||NATURES.none;
  const dnat=NATURES[defer.nature]||NATURES.none;
  const devs=evOver??defer.evs;

  const phys=mv.dc==='physical';
  const ask=phys?'atk':'spa', dsk=phys?'def':'spd';

  let aStat=calcStat(atker.base[ask]||0,atker.ivs[ask],atker.evs[ask]||0,nat[phys?'a':'sa']);
  aStat=Math.floor(aStat*atkAbiStatMult(atker.ability));
  const atkStage=atker.stages?.[ask]||0;
  aStat=Math.floor(aStat*stageMult(isCrit&&atkStage<0?0:atkStage));

  let dStat=calcStat(defer.base[dsk]||0,defer.ivs[dsk],devs[dsk]??0,dnat[phys?'d':'sd']);
  dStat=Math.floor(dStat*defItemMult(defer.item,dsk));
  const defStage=defer.stages?.[dsk]||0;
  dStat=Math.floor(dStat*stageMult(isCrit&&defStage>0?0:defStage));
  if(S.weather==='sand'&&!phys&&defer.types.includes('rock')) dStat=Math.floor(dStat*1.5);
  if(S.weather==='snow'&&phys&&defer.types.includes('ice')) dStat=Math.floor(dStat*1.5);

  const dHP=calcHP(defer.base.hp||0,defer.ivs.hp,devs.hp??0);

  if(!aStat||!dStat||!dHP) return null;

  const eff=typeEff(mv.type,defer.types);
  if(eff===0) return{immune:true,move:mv};

  if(norm(defer.ability)==='wonder-guard'&&eff<=1) return{immune:true,move:mv,wg:true};

  if(norm(defer.item)==='air-balloon'&&mv.type==='ground') return{immune:true,move:mv,byItem:true};

  const st=stab(mv.type,atker.types,atker.ability);
  const aim=atkItemMult(atker.item,mv,eff);
  const aam=atkAbiMult(atker.ability,mv,eff);
  const dam=defAbiMult(defer.ability,mv,eff,defer.fullHP);
  if(dam===0) return{immune:true,move:mv,byAbility:true};

  const dbm=defBerryMult(defer.item,mv.type,eff);
  const wm=weatherMult(mv.type);
  const tm=terrainMult(mv.type);
  const sm=screenMult(mv.dc,isCrit);
  const cm=isCrit?1.5:1;

  const rs=rolls16(aStat,dStat,mv.power).map(r=>{
    let d=r;
    d=Math.floor(d*st);
    d=Math.floor(d*eff);
    d=Math.floor(d*aim);
    d=Math.floor(d*aam);
    d=Math.floor(d*dam);
    d=Math.floor(d*dbm);
    d=Math.floor(d*wm);
    d=Math.floor(d*tm);
    d=Math.floor(d*sm);
    d=Math.floor(d*cm);
    return d;
  });

  const dMin=rs[0], dMax=rs[15];
  const ohko=rs.filter(d=>d>=dHP).length;

  return{dMin,dMax,dHP,aStat,dStat,
    pMin:(dMin/dHP*100).toFixed(1),pMax:(dMax/dHP*100).toFixed(1),
    ohko,eff,st,move:mv,dbm,defItem:defer.item,wm,tm,sm,cm,atkStage,defStage};
}

// ── Type badge ─────────────────────────────────────────────────────────────────
function tb(type){
  const t=type.toLowerCase();
  return`<span class="tb t-${t}">${type}</span>`;
}

// ── Render Team ────────────────────────────────────────────────────────────────
function renderTeams(){
  ['my','en'].forEach(side=>{
    const el=document.getElementById(side==='my'?'my-slots':'enemy-slots');
    el.innerHTML=S[side].map((p,i)=>cardHTML(p,side,i)).join('');
  });
  refreshSelectors();
}

function cardHTML(p,side,idx){
  const spr=p.sprite?`<img class="sprite" src="${p.sprite}" alt="">`:`<div class="no-sprite">?</div>`;
  const types=(p.types||[]).map(tb).join(' ');
  const natOpts=Object.keys(NATURES).map(n=>`<option value="${n}"${n===p.nature?' selected':''}>${n[0].toUpperCase()+n.slice(1)}</option>`).join('');

  return`<div class="poke-card${p.open?' open':''}${p.slug?' active':''}" id="card-${side}-${idx}">
  <div class="card-head" onclick="toggleCard('${side}',${idx})">
    ${spr}<span class="pname">${p.name||`Slot ${idx+1}`}</span><span>${types}</span>
  </div>
  <div class="card-body">
    <div class="ac-wrap" style="margin-bottom:6px">
      <input type="text" placeholder="Search Pokemon…" value="${p.name||''}"
        class="pi" data-side="${side}" data-idx="${idx}" autocomplete="off"
        onfocus="loadAllPoke()">
      <div class="ac-drop"></div>
    </div>
    <div class="row3">
      <div><label>Nature</label><select onchange="setF('${side}',${idx},'nature',this.value)">${natOpts}</select></div>
      <div><label>Ability</label><div class="ac-wrap">
        <input type="text" value="${p.ability||''}" placeholder="Ability"
          class="abi" data-side="${side}" data-idx="${idx}" autocomplete="off">
        <div class="ac-drop"></div>
      </div></div>
      <div><label>Item</label><div class="ac-wrap">
        <input type="text" value="${p.item||''}" placeholder="Item"
          class="ii" data-side="${side}" data-idx="${idx}" autocomplete="off">
        <div class="ac-drop"></div>
      </div></div>
    </div>
    <div class="fullhp-row">
      <label class="fullhp-label"><input type="checkbox" ${p.fullHP?'checked':''} onchange="setF('${side}',${idx},'fullHP',this.checked)"> Full HP</label>
    </div>
    ${statsRow(p,side,idx)}
    <div style="font-size:10px;color:var(--sub);text-transform:uppercase;letter-spacing:.5px;margin:5px 0 3px">Stages</div>
    <div class="stages-grid">
      ${['atk','def','spa','spd'].map(k=>`<div class="stage-ctrl">
        <span class="stage-lbl">${STAT_LABEL[k]}</span>
        <button class="stage-btn" data-side="${side}" data-idx="${idx}" data-stat="${k}" data-dir="-1">−</button>
        <span class="stage-val${(p.stages[k]||0)>0?' pos':(p.stages[k]||0)<0?' neg':''}" id="stage-${side}-${idx}-${k}">${(p.stages[k]||0)>0?'+':''}${p.stages[k]||0}</span>
        <button class="stage-btn" data-side="${side}" data-idx="${idx}" data-stat="${k}" data-dir="1">+</button>
      </div>`).join('')}
    </div>
    <div style="font-size:10px;color:var(--sub);text-transform:uppercase;letter-spacing:.5px;margin:5px 0 3px">Stat Points <span class="ev-total" id="ev-total-${side}-${idx}">${Object.values(p.evs).reduce((a,b)=>a+b,0)}/66</span></div>
    ${evGrid(p.evs,side,idx,'evs')}
    <div style="font-size:10px;color:var(--sub);text-transform:uppercase;letter-spacing:.5px;margin:5px 0 3px">Moves</div>
    <div class="moves-grid">
      ${[0,1,2,3].map(mi=>`<div class="ac-wrap">
        <input type="text" placeholder="Move ${mi+1}" value="${p.moves[mi]?fmt(p.moves[mi]):''}"
          class="mi" data-side="${side}" data-idx="${idx}" data-mi="${mi}" autocomplete="off">
        <div class="ac-drop"></div>
      </div>`).join('')}
    </div>
  </div>
</div>`;
}

function evGrid(vals,side,idx,field){
  return`<div class="stat-grid">${STAT_KEYS.map(k=>`<div>
    <label>${STAT_LABEL[k]}</label>
    <input type="number" min="0" max="31" value="${vals[k]}"
      data-ev-key="${field==='evs'?k:''}"
      onchange="setStat('${side}',${idx},'${field}','${k}',this.value)">
  </div>`).join('')}</div>`;
}

function liveStatsHTML(p){
  const nat=NATURES[p.nature]||NATURES.none;
  const nm={hp:1,atk:nat.a,def:nat.d,spa:nat.sa,spd:nat.sd,spe:nat.sp};
  const STAGE_KEYS={atk:true,def:true,spa:true,spd:true};
  const cells=STAT_KEYS.map(k=>{
    const ev=p.evs?.[k]||0;
    let stat=k==='hp'
      ?calcHP(p.base[k]||0,p.ivs[k],ev)
      :calcStat(p.base[k]||0,p.ivs[k],ev,nm[k]);
    const stage=STAGE_KEYS[k]?(p.stages?.[k]||0):0;
    if(stage) stat=Math.floor(stat*stageMult(stage));
    const cls=nm[k]>1?'nat-boost':nm[k]<1?'nat-nerf':'';
    const stageLabel=stage?(stage>0?` <span style="color:#81c784;font-size:10px">+${stage}</span>`:`<span style="color:#ef9a9a;font-size:10px">${stage}</span>`):'';
    return`<div><label class="${cls}">${STAT_LABEL[k]}${stageLabel}</label><span>${stat}</span></div>`;
  }).join('');
  return`<div class="stat-subhdr">Stats</div><div class="stat-grid stat-ro">${cells}</div>`;
}

function updateLiveStats(side,idx){
  const p=S[side][idx];
  const el=document.getElementById(`live-stats-${side}-${idx}`);
  if(el&&p.slug) el.innerHTML=liveStatsHTML(p);
}

function statsRow(p,side,idx){
  if(!p.slug) return '';
  return`<div id="live-stats-${side}-${idx}">${liveStatsHTML(p)}</div>`;
}

// ── Field / Stage controls ─────────────────────────────────────────────────────
function setWeather(w){
  S.weather=w;
  document.querySelectorAll('.weather-btn').forEach(b=>b.classList.toggle('active',b.dataset.w===w));
}
function setTerrain(t){
  S.terrain=t;
  document.querySelectorAll('.terrain-btn').forEach(b=>b.classList.toggle('active',b.dataset.t===t));
}
function adjStage(side,idx,stat,dir){
  const p=S[side][idx];
  p.stages[stat]=Math.min(6,Math.max(-6,(p.stages[stat]||0)+dir));
  const v=p.stages[stat];
  const el=document.getElementById(`stage-${side}-${idx}-${stat}`);
  if(el){el.textContent=(v>0?'+':'')+v; el.className='stage-val'+(v>0?' pos':v<0?' neg':'');}
  updateLiveStats(side,idx);
}

// ── Card events ────────────────────────────────────────────────────────────────
function toggleCard(side,idx){
  S[side][idx].open=!S[side][idx].open;
  document.getElementById(`card-${side}-${idx}`).classList.toggle('open',S[side][idx].open);
}
function setF(side,idx,field,val){
  S[side][idx][field]=val;
  if(field==='nature') updateLiveStats(side,idx);
}
function setStat(side,idx,field,key,val){
  const p=S[side][idx];
  let v=Math.min(31,Math.max(0,+val||0));
  if(field==='evs'){
    const used=STAT_KEYS.reduce((s,k)=>s+(k===key?0:p.evs[k]),0);
    v=Math.min(v,66-used);
    const inp=document.querySelector(`#card-${side}-${idx} [data-ev-key="${key}"]`);
    if(inp&&+inp.value!==v) inp.value=v;
  }
  p[field][key]=v;
  updateLiveStats(side,idx);
  if(field==='evs'){
    const tot=document.getElementById(`ev-total-${side}-${idx}`);
    if(tot) tot.textContent=`${STAT_KEYS.reduce((s,k)=>s+p.evs[k],0)}/66`;
  }
}

function reCard(side,idx){
  const p=S[side][idx];
  const el=document.getElementById(`card-${side}-${idx}`);
  const wasOpen=el.classList.contains('open');
  p.open=wasOpen;
  el.outerHTML=cardHTML(p,side,idx);
}

// ── Autocomplete (event delegation) ───────────────────────────────────────────
document.addEventListener('input',async e=>{
  const t=e.target;
  if(t.classList.contains('pi')) await onPokeInput(t);
  if(t.classList.contains('mi')) await onMoveInput(t);
  if(t.classList.contains('abi')) onAbilityInput(t);
  if(t.classList.contains('ii')) onItemInput(t);
});

document.addEventListener('focusin',e=>{
  if(e.target.classList.contains('abi')) onAbilityInput(e.target);
});

let _suppressMoveChange=false;

document.addEventListener('mousedown',e=>{
  if(e.target.classList.contains('ac-item')){
    const wrap=e.target.closest('.ac-wrap');
    if(wrap?.querySelector('input.mi')) _suppressMoveChange=true;
  }
});

document.addEventListener('click',e=>{
  if(e.target.classList.contains('stage-btn')){
    const {side,idx,stat,dir}=e.target.dataset;
    adjStage(side,+idx,stat,+dir);
    return;
  }
  if(!e.target.closest('.ac-wrap')){
    document.querySelectorAll('.ac-drop').forEach(d=>d.style.display='none');
    return;
  }
  if(e.target.classList.contains('ac-item')){
    const wrap=e.target.closest('.ac-wrap');
    const inp=wrap.querySelector('input');
    const slug=e.target.dataset.slug;
    const name=e.target.textContent;
    if(inp.classList.contains('pi')) pickPoke(inp,slug,name);
    if(inp.classList.contains('mi')) pickMove(inp,slug,name);
    if(inp.classList.contains('abi')) pickAbility(inp,slug,name);
    if(inp.classList.contains('ii')) pickItem(inp,slug,name);
  }
});

async function onPokeInput(inp){
  const q=inp.value.toLowerCase().trim();
  const drop=inp.nextElementSibling;
  if(!q||!S.allPoke){drop.style.display='none';return}
  const hits=S.allPoke.filter(p=>p.slug.includes(q)||p.name.toLowerCase().includes(q)).slice(0,12);
  if(!hits.length){drop.style.display='none';return}
  drop.style.display='block';
  drop.innerHTML=hits.map(p=>`<div class="ac-item" data-slug="${p.slug}">${p.name}</div>`).join('');
}

async function onMoveInput(inp){
  const q=inp.value.toLowerCase().trim();
  const drop=inp.nextElementSibling;
  if(!q||q.length<2){drop.style.display='none';return}
  const side=inp.dataset.side; const idx=+inp.dataset.idx;
  const p=S[side][idx];
  const pool=p.slug&&S.pokeCache[p.slug]?.learnset||Object.keys(S.moveCache);
  const hits=pool.filter(s=>s.includes(q)||fmt(s).toLowerCase().includes(q)).slice(0,10);
  if(!hits.length){drop.style.display='none';return}
  drop.style.display='block';
  drop.innerHTML=hits.map(s=>`<div class="ac-item" data-slug="${s}">${fmt(s)}</div>`).join('');
}

async function pickPoke(inp,slug,name){
  inp.nextElementSibling.style.display='none';
  inp.value=name;
  const side=inp.dataset.side; const idx=+inp.dataset.idx;
  const p=S[side][idx];
  p.slug=slug; p.name=name;
  const d=await loadPoke(slug);
  if(d){p.types=d.types;p.base=d.base;p.sprite=d.sprite;p.abilities=d.abilities||[]}
  p.open=true;
  reCard(side,idx);
  refreshSelectors();
}

async function pickMove(inp,slug,name){
  inp.nextElementSibling.style.display='none';
  inp.value=name;
  const side=inp.dataset.side; const idx=+inp.dataset.idx; const mi=+inp.dataset.mi;
  const p=S[side][idx];
  p.moves[mi]=slug;
  p.mdata[mi]=await loadMove(slug);
  refreshSelectors();
}

function onAbilityInput(inp){
  const q=inp.value.toLowerCase().trim();
  const drop=inp.nextElementSibling;
  const p=S[inp.dataset.side][+inp.dataset.idx];
  if(!p.abilities.length){drop.style.display='none';return}
  const hits=q
    ?p.abilities.filter(s=>s.includes(q)||fmt(s).toLowerCase().includes(q))
    :p.abilities;
  drop.style.display='block';
  drop.innerHTML=hits.map(s=>`<div class="ac-item" data-slug="${s}">${fmt(s)}</div>`).join('');
}

function onItemInput(inp){
  const q=inp.value.toLowerCase().trim();
  const drop=inp.nextElementSibling;
  if(!q){drop.style.display='none';return}
  const hits=ITEMS.filter(i=>i.slug.includes(q)||i.name.toLowerCase().includes(q)).slice(0,14);
  if(!hits.length){drop.style.display='none';return}
  drop.style.display='block';
  drop.innerHTML=hits.map(i=>`<div class="ac-item" data-slug="${i.slug}">${i.name}</div>`).join('');
}

function pickAbility(inp,slug,name){
  inp.nextElementSibling.style.display='none';
  inp.value=name;
  setF(inp.dataset.side,+inp.dataset.idx,'ability',name);
}

function pickItem(inp,slug,name){
  inp.nextElementSibling.style.display='none';
  inp.value=name;
  setF(inp.dataset.side,+inp.dataset.idx,'item',name);
}

document.addEventListener('change',async e=>{
  const t=e.target;
  if(t.classList.contains('mi')){
    if(_suppressMoveChange){_suppressMoveChange=false;return}
    const slug=norm(t.value); if(!slug) return;
    const p=S[t.dataset.side][+t.dataset.idx];
    p.moves[+t.dataset.mi]=slug;
    p.mdata[+t.dataset.mi]=await loadMove(slug);
    refreshSelectors();
  }
  if(t.classList.contains('abi')) setF(t.dataset.side,+t.dataset.idx,'ability',t.value);
  if(t.classList.contains('ii')) setF(t.dataset.side,+t.dataset.idx,'item',t.value);
});

// ── Selectors ──────────────────────────────────────────────────────────────────
function refreshSelectors(resetMove=false){
  const aSel=document.getElementById('sel-atk');
  const mSel=document.getElementById('sel-move');
  const dSel=document.getElementById('sel-def');
  const prevA=aSel.value, prevM=mSel.value, prevD=dSel.value;

  aSel.innerHTML='<option value="">— attacker —</option>'+
    S.my.map((p,i)=>p.slug?`<option value="${i}">${p.name}</option>`:'').join('');
  if(prevA) aSel.value=prevA;

  const ai=parseInt(aSel.value);
  if(!isNaN(ai)){
    const pAtk=S.my[ai];
    const moveOpts=pAtk.moves.map((slug,mi)=>{
      if(!slug) return null;
      const m=pAtk.mdata[mi];
      return{slug:m?.slug||slug,label:m?`${m.name}${m.power?` [${m.type}/${m.dc}] ${m.power}BP`:' [status]'}`:fmt(slug)};
    }).filter(Boolean);
    if(moveOpts.length){
      mSel.innerHTML='<option value="">— move —</option>'+
        moveOpts.map(o=>`<option value="${o.slug}">${o.label}</option>`).join('');
      if(!resetMove&&prevM) mSel.value=prevM;
    } else {
      mSel.innerHTML='<option value="">— no moves loaded —</option>';
    }
  } else {
    mSel.innerHTML='<option value="">— pick attacker first —</option>';
  }

  dSel.innerHTML='<option value="">— defender —</option>'+
    S.en.map((p,i)=>p.slug?`<option value="${i}">${p.name}</option>`:'').join('');
  if(prevD) dSel.value=prevD;
}

function onAtkChange(){refreshSelectors(true)}

// ── Calculate ──────────────────────────────────────────────────────────────────
function calculate(){
  const ai=parseInt(document.getElementById('sel-atk').value);
  const mvSlug=document.getElementById('sel-move').value;
  const di=parseInt(document.getElementById('sel-def').value);
  const el=document.getElementById('result');

  if(isNaN(ai)||!mvSlug||isNaN(di)){
    el.innerHTML='<div class="empty">Select attacker, move, and defender</div>';return;
  }
  const atk=S.my[ai], def=S.en[di];
  const mv=atk.mdata.find(m=>m?.slug===mvSlug);
  if(!mv){el.innerHTML='<div class="empty">Move data not loaded yet — try again</div>';return}

  if(!mv.power){
    el.innerHTML=`<div class="result-box"><div class="result-title">
      ${atk.types.map(tb).join(' ')} <strong>${atk.name}</strong> uses ${tb(mv.type)} <strong>${mv.name}</strong><br>
      <span style="color:var(--sub)">Status move — no damage</span></div></div>`;
    return;
  }

  const phys=mv.dc==='physical';
  const rActual=calc(atk,mvSlug,def,null,false);
  const worstItem=rActual&&!rActual.immune?getWorstCaseItem(mv,rActual.eff):null;
  const worstDef=worstItem?{...def,item:worstItem}:def;
  const rWorst=calc(atk,mvSlug,worstDef,{hp:31,atk:0,def:phys?31:0,spa:0,spd:phys?0:31,spe:0},false);
  const rCrit=calc(atk,mvSlug,def,null,true);
  el.innerHTML=buildResult(atk,def,mv,rActual,rWorst,rCrit,worstItem);
}

function buildResult(atk,def,mv,rActual,rWorst,rCrit,worstItem){
  const atkTypes=atk.types.map(tb).join(' ');
  const defTypes=def.types.map(tb).join(' ');

  if(rActual?.immune){
    let reason='NO EFFECT';
    if(rActual.wg) reason='NO EFFECT (Wonder Guard)';
    else if(rActual.byAbility) reason=`NO EFFECT (${fmt(def.ability)})`;
    else if(rActual.byItem) reason=`NO EFFECT (${fmt(norm(def.item))})`;
    return`<div class="result-box"><div class="result-title">
      ${atkTypes} <strong>${atk.name}</strong> uses ${tb(mv.type)} <strong>${mv.name}</strong>
      vs ${defTypes} <strong>${def.name}</strong></div>
      <div class="empty">${tb(mv.type)} ${reason}</div>
    </div>`;
  }
  if(!rActual) return`<div class="result-box"><div class="empty">Cannot calculate — missing stats or move data</div></div>`;

  const effStr=rActual.eff>1?`<span style="color:#81c784">SE ${rActual.eff}×</span>`:rActual.eff<1?`<span style="color:#ef9a9a">NVE ${rActual.eff}×</span>`:`<span style="color:var(--sub)">Neutral</span>`;
  const stabStr=rActual.st>1?` · <span style="color:#90caf9">STAB${rActual.st===2?' (Adaptability)':''}</span>`:'';
  const berryStr=rActual.dbm<1?` · <span style="color:#ffcc80">${fmt(norm(rActual.defItem))} (0.5×)</span>`:'';

  const da=norm(def.ability);
  const defMods=[];
  if((da==='multiscale'||da==='shadow-shield')&&def.fullHP) defMods.push(`${fmt(def.ability)} (0.5×)`);
  if((da==='filter'||da==='solid-rock'||da==='prism-armor')&&rActual.eff>1) defMods.push(`${fmt(def.ability)} (0.75× SE)`);
  if(da==='ice-scales'&&mv.dc==='special') defMods.push(`Ice Scales (0.5×)`);
  if(da==='fluffy'&&(mv.flags||[]).includes('contact')) defMods.push(`Fluffy (0.5×)`);
  if(da==='fluffy'&&mv.type==='fire') defMods.push(`Fluffy (2× fire)`);
  const defModStr=defMods.length?` · <span style="color:#ce93d8">${defMods.join(', ')}</span>`:'';

  const phys=mv.dc==='physical';
  const fieldMods=[];
  if(rActual.wm!==1) fieldMods.push(`${S.weather[0].toUpperCase()+S.weather.slice(1)} (${rActual.wm}×)`);
  if(rActual.tm!==1) fieldMods.push(`${S.terrain[0].toUpperCase()+S.terrain.slice(1)} terrain (${rActual.tm}×)`);
  if(rActual.sm<1) fieldMods.push(S.screens.auroraveil?'Aurora Veil (0.5×)':phys?'Reflect (0.5×)':'Light Screen (0.5×)');
  const atkStg=atk.stages?.[phys?'atk':'spa']||0;
  const defStg=def.stages?.[phys?'def':'spd']||0;
  if(atkStg!==0) fieldMods.push(`${phys?'Atk':'SpA'} ${atkStg>0?'+':''}${atkStg}`);
  if(defStg!==0) fieldMods.push(`${phys?'Def':'SpD'} ${defStg>0?'+':''}${defStg}`);
  const fieldStr=fieldMods.length?`<br><span style="color:#ffb74d;font-size:11px">${fieldMods.join(' · ')}</span>`:'';

  const worstLabel=worstItem?`Defensive max — 31 SP + ${fmt(worstItem)}`:'Defensive max — 31 SP';

  return`<div class="result-box">
  <div class="result-title">
    ${atkTypes} <strong>${atk.name}</strong><br>
    uses ${tb(mv.type)} <strong>${mv.name}</strong> (${mv.dc}, ${mv.power}BP)<br>
    vs ${defTypes} <strong>${def.name}</strong>
  </div>
  <div class="result-meta">
    ${effStr}${stabStr}${berryStr}${defModStr}${fieldStr}<br>
    Atk: <span class="val">${rActual.aStat}</span> &nbsp; Def (actual SP): <span class="val">${rActual.dStat}</span> &nbsp; HP: <span class="val">${rActual.dHP}</span>
  </div>
  ${dmgSection('Current',rActual)}
  <hr class="divider">
  ${dmgSection(worstLabel,rWorst)}
  <hr class="divider">
  ${dmgSection('Critical hit',rCrit)}
  </div>`;
}

function dmgSection(label,r){
  if(!r||r.immune) return'';
  const minP=+r.pMin, maxP=+r.pMax;
  const barColor=maxP>=100?'#f44336':maxP>=75?'#ff6d00':maxP>=50?'#ffb300':'#7c83fd';

  let badge;
  if(r.ohko===16)       badge=`<span class="badge kill">OHKO — Guaranteed (16/16)</span>`;
  else if(r.ohko>0)     badge=`<span class="badge warn">OHKO — ${r.ohko}/16 rolls (${(r.ohko/16*100).toFixed(0)}%)</span>`;
  else if(r.dMin*2>=r.dHP) badge=`<span class="badge ok">2HKO — Guaranteed</span>`;
  else if(r.dMax*2>=r.dHP) badge=`<span class="badge warn">2HKO — Possible</span>`;
  else                  badge=`<span class="badge great">No OHKO / No 2HKO</span>`;

  return`<div>
  <div class="section-label">${label}</div>
  <div class="dmg-bar-bg">
    <div class="dmg-bar-fill low" style="width:${Math.min(100,minP)}%;background:${barColor}"></div>
    <div class="dmg-bar-fill" style="width:${Math.min(100,maxP)}%;background:${barColor}"></div>
  </div>
  <div class="dmg-nums"><strong>${r.dMin}–${r.dMax}</strong> / ${r.dHP} HP &nbsp; (<strong>${r.pMin}%–${r.pMax}%</strong>)</div>
  ${badge}
  </div>`;
}

// ── Init ──────────────────────────────────────────────────────────────────────
renderTeams();
