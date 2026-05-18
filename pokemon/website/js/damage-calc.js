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

// Abilities that need a manual "is it active?" toggle because the trigger
// is mid-battle history the UI cannot derive (item loss, turn counter, etc.)
const MANUAL_ABILITIES={
  'unburden':'Item Lost',
  'slow-start':'Slow Start Active',
  'stakeout':'Vs. Switched-In',
  'disguise':'Disguise Broken',
  'ice-face':'Ice Face Broken'
};

// Protect-type moves: whole-turn protection; any attack targeting the user is blocked
const PROTECT_MOVES=new Set([
  'protect','detect','baneful-bunker','spiky-shield','kings-shield',
  'obstruct','silk-trap','burning-bulwark','wide-guard','quick-guard',
  'mat-block','crafty-shield','max-guard'
]);

// Moves that bypass the target's positive defensive stage boosts
const BYPASS_DEF_BOOST=new Set([
  'sacred-sword','darkest-lariat','chip-away','shadow-chop'
]);

// Moves with 'special' damage class that read the target's physical Defense instead of SpD
const USE_PHYS_DEF=new Set(['psyshock','psystrike','secret-sword']);

const SLICING_MOVES=new Set([
  'cut','razor-wind','slash','fury-cutter','night-slash','x-scissor','leaf-blade',
  'air-cutter','air-slash','sacred-sword','razor-shell','psycho-cut','cross-poison',
  'aerial-ace','smart-strike','ceaseless-edge','kowtow-cleave','bitter-blade',
  'mighty-cleave','tachyon-cutter','stone-axe','false-surrender','aqua-cutter',
  'behemoth-blade','temper-flare'
]);

const SC_LABEL={attack:'Atk',defense:'Def','special-attack':'SpA','special-defense':'SpD',speed:'Spe',accuracy:'Acc',evasion:'Eva'};

// Moves with context-dependent success conditions
const CONDITIONAL_NOTES={
  'sucker-punch':'Fails if target uses a non-damaging move',
  'fake-out':'First turn out only',
  'focus-punch':'Fails if hit before it moves',
  'sleep-talk':'Requires Sleep status',
  'snore':'Requires Sleep status',
  'last-resort':'Fails if other moves still have PP',
  'belch':'Requires having consumed a Berry',
  'solar-beam':'Charges on turn 1 (instant in Sun)',
  'solar-blade':'Charges on turn 1 (instant in Sun)',
  'skull-bash':'Charges on turn 1',
  'sky-attack':'Charges on turn 1',
  'razor-wind':'Charges on turn 1',
  'bounce':'Airborne on turn 1',
  'fly':'Airborne on turn 1',
  'dig':'Underground on turn 1',
  'dive':'Underwater on turn 1',
  'shadow-force':'Vanishes on turn 1 (bypasses Protect)',
  'phantom-force':'Vanishes on turn 1 (bypasses Protect)',
};

// PokeAPI target field is sometimes wrong (especially Gen 9) or reflects singles behavior.
// This map is the authoritative source for VGC doubles targeting.
const SPREAD_OVERRIDES={
  // hits both opponents only (NOT the user's ally)
  'heat-wave':'all-opponents','blizzard':'all-opponents','rock-slide':'all-opponents',
  'muddy-water':'all-opponents','hyper-voice':'all-opponents','dazzling-gleam':'all-opponents',
  'snarl':'all-opponents','icy-wind':'all-opponents','petal-blizzard':'all-opponents',
  'sparkling-aria':'all-opponents','electroweb':'all-opponents',
  'burning-jealousy':'all-opponents','matcha-gotcha':'all-opponents',
  'noble-roar':'all-opponents','parting-shot':'all-opponents',
  'growl':'all-opponents','charm':'all-opponents','tail-whip':'all-opponents',
  'leer':'all-opponents','screech':'all-opponents','scary-face':'all-opponents',
  'featherdance':'all-opponents','baby-doll-eyes':'all-opponents',
  'eerie-impulse':'all-opponents','venom-drench':'all-opponents',
  'tickle':'all-opponents','captivate':'all-opponents',
  // hits both opponents AND the user's ally (spread penalty still applies to all targets)
  'earthquake':'all-other-pokemon','magnitude':'all-other-pokemon',
  'surf':'all-other-pokemon','discharge':'all-other-pokemon',
  'lava-plume':'all-other-pokemon','explosion':'all-other-pokemon',
  'self-destruct':'all-other-pokemon','misty-explosion':'all-other-pokemon',
  'mind-blown':'all-other-pokemon',
};

// Items that actually exist in Pokemon Champions (sourced from pokebase_champions.db)
const ITEMS=[
  // Speed / utility
  {slug:'choice-scarf',name:'Choice Scarf'},
  {slug:'scope-lens',name:'Scope Lens'},{slug:'kings-rock',name:"King's Rock"},
  {slug:'shell-bell',name:'Shell Bell'},{slug:'leftovers',name:'Leftovers'},
  {slug:'focus-sash',name:'Focus Sash'},{slug:'focus-band',name:'Focus Band'},
  {slug:'white-herb',name:'White Herb'},{slug:'mental-herb',name:'Mental Herb'},
  {slug:'bright-powder',name:'Bright Powder'},{slug:'quick-claw',name:'Quick Claw'},
  {slug:'light-ball',name:'Light Ball'},
  // Type-boosting held items (×1.2)
  {slug:'charcoal',name:'Charcoal'},{slug:'mystic-water',name:'Mystic Water'},
  {slug:'miracle-seed',name:'Miracle Seed'},{slug:'magnet',name:'Magnet'},
  {slug:'never-melt-ice',name:'Never-Melt Ice'},{slug:'black-belt',name:'Black Belt'},
  {slug:'poison-barb',name:'Poison Barb'},{slug:'soft-sand',name:'Soft Sand'},
  {slug:'sharp-beak',name:'Sharp Beak'},{slug:'twisted-spoon',name:'Twisted Spoon'},
  {slug:'silver-powder',name:'Silver Powder'},{slug:'hard-stone',name:'Hard Stone'},
  {slug:'spell-tag',name:'Spell Tag'},{slug:'dragon-fang',name:'Dragon Fang'},
  {slug:'black-glasses',name:'Black Glasses'},{slug:'metal-coat',name:'Metal Coat'},
  {slug:'silk-scarf',name:'Silk Scarf'},{slug:'fairy-feather',name:'Fairy Feather'},
  // Utility berries
  {slug:'lum-berry',name:'Lum Berry'},{slug:'sitrus-berry',name:'Sitrus Berry'},
  {slug:'oran-berry',name:'Oran Berry'},
  {slug:'aspear-berry',name:'Aspear Berry'},{slug:'cheri-berry',name:'Cheri Berry'},
  {slug:'chesto-berry',name:'Chesto Berry'},{slug:'pecha-berry',name:'Pecha Berry'},
  {slug:'persim-berry',name:'Persim Berry'},{slug:'rawst-berry',name:'Rawst Berry'},
  {slug:'leppa-berry',name:'Leppa Berry'},
  // Resist berries (×0.5 vs SE moves)
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

// Competitive moves pre-fetched at startup so their learned_by_pokemon data
// is in S.moveCache before the user picks any pokemon.
// These are Gen 9 TMs and VGC staples most likely to have PokeAPI learnset gaps.
const PRELOAD_MOVES=[
  'weather-ball','terrain-pulse','burning-jealousy','matcha-gotcha',
  'expanding-force','rising-voltage',
  'heat-wave','blizzard','muddy-water','petal-blizzard',
  'dazzling-gleam','hyper-voice','snarl','icy-wind',
  'rock-slide','discharge','lava-plume','electroweb',
  'helping-hand','follow-me','rage-powder',
  'fake-out','sucker-punch','extreme-speed',
  'will-o-wisp','thunder-wave',
  'aura-sphere','focus-blast','shadow-ball','energy-ball',
  'flash-cannon','iron-head','close-combat','superpower',
  'flamethrower','thunderbolt','ice-beam','surf',
  'psychic','psyshock','dark-pulse','earth-power',
  'brave-bird','knock-off','power-whip','giga-drain',
];

// ── State ──────────────────────────────────────────────────────────────────────
const S={
  my: Array.from({length:6},()=>mkP('my')),
  en: Array.from({length:6},()=>mkP('en')),
  allPoke:null, moveCache:{}, pokeCache:{},
  weather:'none', terrain:'none',
  screens:{reflect:false,lightscreen:false,auroraveil:false},
  tailwind:{my:false,en:false},trickroom:false,
  ruinAbils:{sword:false,tablets:false,vessel:false,beads:false},
  predictData:{}
};

function mkP(side){
  return{slug:'',name:'',types:[],base:{hp:0,atk:0,def:0,spa:0,spd:0,spe:0},
    nature:'none',ability:'',item:'',abilities:[],
    ivs:{hp:31,atk:31,def:31,spa:31,spd:31,spe:31},
    evs:{hp:0,atk:0,def:0,spa:0,spd:0,spe:0},
    moves:['','','',''],mdata:[null,null,null,null],
    stages:{atk:0,def:0,spa:0,spd:0,spe:0},
    open:false,sprite:null,hpPct:100,status:'',abilityActive:false};
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
    dc:d.damage_class?.name,power:d.power,acc:d.accuracy,pp:d.pp,pri:d.priority,target:d.target?.name,
    flags:(d.flags||[]).map(f=>f.name),
    drain:meta.drain||0,
    recoil:(meta.drain||0)<0,
    secondary:(meta.ailment_chance||0)>0||(meta.stat_chance||0)>0||(meta.flinch_chance||0)>0,
    ailment:meta.ailment?.name&&meta.ailment.name!=='none'?meta.ailment.name:null,
    ailmentChance:meta.ailment_chance||0,
    flinchChance:meta.flinch_chance||0,
    statChanges:(d.stat_changes||[]).map(sc=>({stat:sc.stat.name,change:sc.change})),
    statChance:meta.stat_chance||0,
    minHits:meta.min_hits||null,
    maxHits:meta.max_hits||null,
    learnedBy:(d.learned_by_pokemon||[]).map(p=>p.name),
    usePhysDef:USE_PHYS_DEF.has(d.name),
    protect:PROTECT_MOVES.has(d.name)};
  if(SPREAD_OVERRIDES[d.name]) res.target=SPREAD_OVERRIDES[d.name];
  S.moveCache[slug]=res; return res;
}

async function loadPredictData(){
  if(Object.keys(S.predictData).length) return;
  try{
    const r=await fetch('data/PredictData.json');
    if(r.ok) S.predictData=await r.json();
  }catch(_){}
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
  const a=norm(ability);
  if(a==='protean'||a==='libero') return 1.5;
  if(!atypes.some(t=>t.toLowerCase()===mt.toLowerCase())) return 1;
  return a==='adaptability'?2:1.5;
}

function atkItemMult(item,mv,eff){
  const i=norm(item); const t=mv.type.toLowerCase();
  const TI={charcoal:'fire','mystic-water':'water','miracle-seed':'grass',magnet:'electric',
    'never-melt-ice':'ice','black-belt':'fighting','poison-barb':'poison','soft-sand':'ground',
    'sharp-beak':'flying','twisted-spoon':'psychic','silver-powder':'bug','hard-stone':'rock',
    'spell-tag':'ghost','dragon-fang':'dragon','black-glasses':'dark','metal-coat':'steel',
    'silk-scarf':'normal','fairy-feather':'fairy'};
  if(TI[i]===t) return 1.2;
  return 1;
}

function defItemMult(item,sk){
  return 1; // No AV/Eviolite in Champions
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
  if(a==='rocky-payload'&&t==='rock') return 1.5;
  if(a==='water-bubble'&&t==='water') return 2;
  if((a==='aerilate'||a==='pixilate'||a==='refrigerate'||a==='galvanize')&&t==='normal') return 1.2;
  if(a==='technician'&&mv.power&&mv.power<=60) return 1.5;
  if(a==='sharpness'&&SLICING_MOVES.has(mv.slug)) return 1.5;
  if(a==='sand-force'&&S.weather==='sand'&&(t==='rock'||t==='steel'||t==='ground')) return 1.3;
  if(a==='solar-power'&&S.weather==='sun'&&mv.dc==='special') return 1.5;
  if(a==='flower-gift'&&S.weather==='sun'&&mv.dc==='physical') return 1.5;
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

function defAbiMult(ability,mv,eff,hpPct){
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
  if((a==='multiscale'||a==='shadow-shield')&&hpPct>=100) m*=0.5;
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
  return null; // No Assault Vest in Champions
}

// Resolves moves whose type/power are field-dependent at calc time.
// Returns a shallow copy with overrides — never mutates the cached move object.
function resolveMove(mv){
  if(!mv) return mv;
  if(mv.slug==='weather-ball'&&S.weather!=='none'){
    const WT={sun:'fire',rain:'water',sand:'rock',snow:'ice'};
    return{...mv,type:WT[S.weather],power:100};
  }
  if(mv.slug==='terrain-pulse'&&S.terrain!=='none'){
    const TT={electric:'electric',grassy:'grass',psychic:'psychic',misty:'fairy'};
    return{...mv,type:TT[S.terrain],power:100};
  }
  return mv;
}

function calc(atker,mvSlug,defer,evOver=null,isCrit=false,hh=false,movingLast=false){
  const mv=resolveMove(atker.mdata.find(m=>m?.slug===mvSlug));
  if(!mv) return null;
  if(!mv.power) return{status:true,move:mv};

  const nat=NATURES[atker.nature]||NATURES.none;
  const dnat=NATURES[defer.nature]||NATURES.none;
  const devs=evOver??defer.evs;
  const aa=norm(atker.ability);
  const da=norm(defer.ability);

  const phys=mv.dc==='physical';
  const usePhysDef=mv.usePhysDef||false;
  const ask=phys?'atk':'spa', dsk=(phys||usePhysDef)?'def':'spd';
  const bypassDefBoost=BYPASS_DEF_BOOST.has(mv.slug);
  const ahp=atker.hpPct??100;

  // ── Attacker stat ───────────────────────────────────────────────────────
  let aStat=calcStat(atker.base[ask]||0,atker.ivs[ask],atker.evs[ask]||0,nat[phys?'a':'sa']);
  aStat=Math.floor(aStat*atkAbiStatMult(atker.ability));
  // Light Ball: Pikachu only, doubles both Atk and SpA
  if(norm(atker.item)==='light-ball'&&norm(atker.slug||'').startsWith('pikachu')) aStat=Math.floor(aStat*2);
  const atkStage=atker.stages?.[ask]||0;
  // Unaware (defender) ignores attacker's positive stage boosts
  aStat=Math.floor(aStat*stageMult(isCrit&&atkStage<0?0:(da==='unaware'&&atkStage>0?0:atkStage)));
  // Status-based modifiers
  if(phys&&atker.status==='burn'&&aa!=='guts') aStat=Math.floor(aStat*0.5);
  if(phys&&atker.status&&aa==='guts') aStat=Math.floor(aStat*1.5);
  if(phys&&(atker.status==='poison'||atker.status==='badly')&&aa==='toxic-boost') aStat=Math.floor(aStat*1.5);
  if(!phys&&atker.status==='burn'&&aa==='flare-boost') aStat=Math.floor(aStat*1.5);
  if(phys&&aa==='slow-start'&&atker.abilityActive) aStat=Math.floor(aStat*0.5);
  // HP-threshold abilities
  if(aa==='defeatist'&&ahp<=50) aStat=Math.floor(aStat*0.5);
  // Weather-boosted stat abilities (Orichalcum/Hadron act on the stat, not the roll)
  if(phys&&aa==='orichalcum-pulse'&&S.weather==='sun') aStat=Math.floor(aStat*(4/3));
  if(!phys&&aa==='hadron-engine'&&S.terrain==='electric') aStat=Math.floor(aStat*(4/3));
  // Ruin abilities reduce the attacker's offensive stat
  if(S.ruinAbils.tablets&&phys) aStat=Math.floor(aStat*0.75);
  if(S.ruinAbils.vessel&&!phys) aStat=Math.floor(aStat*0.75);

  // ── Defender stat ───────────────────────────────────────────────────────
  let dStat=calcStat(defer.base[dsk]||0,defer.ivs[dsk],devs[dsk]??0,dnat[(phys||usePhysDef)?'d':'sd']);
  dStat=Math.floor(dStat*defItemMult(defer.item,dsk));
  const defStage=defer.stages?.[dsk]||0;
  // Crits, Unaware, and bypass-boost moves (Sacred Sword, Darkest Lariat) all ignore positive def stages
  dStat=Math.floor(dStat*stageMult(defStage>0&&(isCrit||aa==='unaware'||bypassDefBoost)?0:defStage));
  if(S.weather==='sand'&&!phys&&defer.types.includes('rock')) dStat=Math.floor(dStat*1.5);
  if(S.weather==='snow'&&phys&&defer.types.includes('ice')) dStat=Math.floor(dStat*1.5);
  // Ruin abilities reduce the defender's defensive stat
  if(S.ruinAbils.sword&&phys) dStat=Math.floor(dStat*0.75);
  if(S.ruinAbils.beads&&!phys) dStat=Math.floor(dStat*0.75);

  const dHP=calcHP(defer.base.hp||0,defer.ivs.hp,devs.hp??0);
  if(!aStat||!dStat||!dHP) return null;

  // ── Type effectiveness (Scrappy bypasses Ghost immunity for Normal/Fighting) ──
  let eff=typeEff(mv.type,defer.types);
  if(eff===0&&aa==='scrappy'&&(mv.type==='normal'||mv.type==='fighting')){
    eff=typeEff(mv.type,defer.types.filter(t=>t.toLowerCase()!=='ghost'));
  }
  if(eff===0) return{immune:true,move:mv};
  if(da==='wonder-guard'&&eff<=1) return{immune:true,move:mv,wg:true};
  if(da==='disguise'&&!defer.abilityActive) return{immune:true,move:mv,disguise:true};
  if(da==='ice-face'&&!defer.abilityActive&&phys) return{immune:true,move:mv,iceFace:true};

  const st=stab(mv.type,atker.types,atker.ability);
  const aim=atkItemMult(atker.item,mv,eff);
  const aam=atkAbiMult(atker.ability,mv,eff);
  const dam=defAbiMult(defer.ability,mv,eff,defer.hpPct??100);
  if(dam===0) return{immune:true,move:mv,byAbility:true};

  const dbm=defBerryMult(defer.item,mv.type,eff);
  const wm=weatherMult(mv.type);
  const tm=terrainMult(mv.type);
  const sm=screenMult(mv.dc,isCrit);
  const cm=isCrit?(aa==='sniper'?2.25:1.5):1;

  const hhm=hh?1.5:1;
  const stakeoutM=aa==='stakeout'&&atker.abilityActive?2:1;
  const analyticM=movingLast&&aa==='analytic'?1.3:1;
  const blazeM=(()=>{
    if(ahp>33) return 1;
    const t=mv.type.toLowerCase();
    if(aa==='blaze'&&t==='fire') return 1.5;
    if(aa==='torrent'&&t==='water') return 1.5;
    if(aa==='overgrow'&&t==='grass') return 1.5;
    if(aa==='swarm'&&t==='bug') return 1.5;
    return 1;
  })();
  const spm=(mv.target==='all-opponents'||mv.target==='all-other-pokemon')?0.75:1;

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
    d=Math.floor(d*hhm);
    d=Math.floor(d*stakeoutM);
    d=Math.floor(d*analyticM);
    d=Math.floor(d*blazeM);
    d=Math.floor(d*spm);
    return d;
  });

  const dMin=rs[0], dMax=rs[15];
  const ohko=rs.filter(d=>d>=dHP).length;

  const nHitsMin=mv.minHits||1, nHitsMax=mv.maxHits||1;
  const extra={};
  if(ohko>0&&(defer.hpPct??100)>=100){
    if(da==='sturdy') extra.blocked='sturdy';
    else if(norm(defer.item)==='focus-sash') extra.blocked='sash';
  }
  if(nHitsMax>1){
    extra.nHitsMin=nHitsMin; extra.nHitsMax=nHitsMax;
    extra.dMinPost=dMin; extra.dMaxPost=dMax;
    const damPost=defAbiMult(defer.ability,mv,eff,0);
    if(damPost!==dam){
      const rsPost=rolls16(aStat,dStat,mv.power).map(r=>{
        let d=r;
        d=Math.floor(d*st); d=Math.floor(d*eff); d=Math.floor(d*aim); d=Math.floor(d*aam);
        d=Math.floor(d*damPost); d=Math.floor(d*dbm); d=Math.floor(d*wm); d=Math.floor(d*tm);
        d=Math.floor(d*sm); d=Math.floor(d*cm); d=Math.floor(d*hhm); d=Math.floor(d*stakeoutM);
        d=Math.floor(d*analyticM); d=Math.floor(d*blazeM); d=Math.floor(d*spm);
        return d;
      });
      extra.dMinPost=rsPost[0]; extra.dMaxPost=rsPost[15];
    }
  }

  return{dMin,dMax,dHP,aStat,dStat,hh,spread:spm<1,
    pMin:(dMin/dHP*100).toFixed(1),pMax:(dMax/dHP*100).toFixed(1),
    ohko,eff,st,move:mv,dbm,defItem:defer.item,wm,tm,sm,cm,atkStage,defStage,...extra};
}

// ── Type badge ─────────────────────────────────────────────────────────────────
function tb(type){
  const t=type.toLowerCase();
  return`<span class="tb t-${t}">${type}</span>`;
}

// ── Move secondary-effect tags ─────────────────────────────────────────────────
function moveTags(mv){
  if(!mv) return'';
  const tags=[];
  // Multi-hit
  if(mv.minHits&&mv.maxHits)
    tags.push(`<span class="badge great">${mv.minHits===mv.maxHits?mv.minHits+' hit':mv.minHits+'–'+mv.maxHits+' hits'}</span>`);
  // Status ailment
  if(mv.ailment&&mv.ailmentChance>0)
    tags.push(`<span class="badge warn">${mv.ailmentChance}% ${fmt(mv.ailment)}</span>`);
  else if(mv.ailment&&mv.ailmentChance===0)
    tags.push(`<span class="badge warn">${fmt(mv.ailment)}</span>`);
  // Flinch
  if(mv.flinchChance>0)
    tags.push(`<span class="badge warn">${mv.flinchChance}% Flinch</span>`);
  // Stat changes
  if(mv.statChanges?.length){
    const chanceStr=(mv.statChance>0&&mv.statChance<100)?` ${mv.statChance}%`:'';
    mv.statChanges.forEach(sc=>{
      const lbl=SC_LABEL[sc.stat]||sc.stat;
      tags.push(`<span class="badge ${sc.change>0?'ok':'warn'}">${lbl} ${sc.change>0?'+':''}${sc.change}${chanceStr}</span>`);
    });
  }
  // Conditional notes
  const note=CONDITIONAL_NOTES[mv.slug];
  if(note) tags.push(`<span class="badge warn">⚠ ${note}</span>`);
  return tags.join(' ');
}

// ── Render Team ────────────────────────────────────────────────────────────────
function renderTeams(){
  ['my','en'].forEach(side=>{
    const el=document.getElementById(side==='my'?'my-slots':'enemy-slots');
    el.innerHTML=S[side].map((p,i)=>cardHTML(p,side,i)).join('');
  });
  refreshActivePickers();
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
      </div>
      <label class="abi-act-label" id="abi-act-${side}-${idx}" style="display:${norm(p.ability)in MANUAL_ABILITIES?'flex':'none'}">
        <input type="checkbox" ${p.abilityActive?'checked':''} onchange="setF('${side}',${idx},'abilityActive',this.checked)">
        <span>${MANUAL_ABILITIES[norm(p.ability)]||''}</span>
      </label></div>
      <div><label>Item</label><div class="ac-wrap">
        <input type="text" value="${p.item||''}" placeholder="Item"
          class="ii" data-side="${side}" data-idx="${idx}" autocomplete="off">
        <div class="ac-drop"></div>
      </div></div>
    </div>
    <div class="fullhp-row">
      <label class="fullhp-label">HP <input type="number" class="hppct-inp" min="1" max="100" value="${p.hpPct??100}" onchange="setF('${side}',${idx},'hpPct',Math.min(100,Math.max(1,+this.value||100)))"> %</label>
      <select class="status-sel" onchange="setF('${side}',${idx},'status',this.value)" style="width:auto;font-size:11px;margin-left:8px">
        <option value="">No status</option>
        <option value="burn"${p.status==='burn'?' selected':''}>Burn</option>
        <option value="paralysis"${p.status==='paralysis'?' selected':''}>Paralysis</option>
        <option value="poison"${p.status==='poison'?' selected':''}>Poison</option>
        <option value="badly"${p.status==='badly'?' selected':''}>Badly Poisoned</option>
      </select>
    </div>
    ${statsRow(p,side,idx)}
    <div style="font-size:10px;color:var(--sub);text-transform:uppercase;letter-spacing:.5px;margin:5px 0 3px">Stages</div>
    <div class="stages-grid">
      ${['atk','def','spa','spd','spe'].map(k=>`<div class="stage-ctrl">
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
  const STAGE_KEYS={atk:true,def:true,spa:true,spd:true,spe:true};
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
  const p=S[side][idx];
  p[field]=val;
  if(field==='nature') updateLiveStats(side,idx);
  if(field==='ability'){p.abilityActive=false; updateAbilityToggle(side,idx);}
}

function updateAbilityToggle(side,idx){
  const p=S[side][idx];
  const el=document.getElementById(`abi-act-${side}-${idx}`);
  if(!el) return;
  const a=norm(p.ability);
  const lbl=MANUAL_ABILITIES[a];
  el.style.display=lbl?'flex':'none';
  if(lbl){
    el.querySelector('span').textContent=lbl;
    el.querySelector('input[type=checkbox]').checked=p.abilityActive;
  }
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
  if(t.classList.contains('mi')) onMoveInput(t);
  if(t.classList.contains('abi')) onAbilityInput(t);
  if(t.classList.contains('ii')) onItemInput(t);
});

document.addEventListener('focusin',e=>{
  if(e.target.classList.contains('abi')) onAbilityInput(e.target);
  if(e.target.classList.contains('mi')) onMoveInput(e.target);
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

function onMoveInput(inp){
  const q=inp.value.toLowerCase().trim();
  const drop=inp.nextElementSibling;
  const side=inp.dataset.side; const idx=+inp.dataset.idx;
  const p=S[side][idx];
  const learnset=p.slug&&S.pokeCache[p.slug]?.learnset;
  if(!learnset){drop.style.display='none';return}

  // Augment with any cached moves whose learned_by_pokemon includes this pokemon
  // (covers Gen 9 TM gaps in the PokeAPI pokemon endpoint)
  const learnsetSet=new Set(learnset);
  const cacheBonus=Object.entries(S.moveCache)
    .filter(([slug,mv])=>!learnsetSet.has(slug)&&mv.learnedBy?.includes(p.slug))
    .map(([slug])=>slug);
  const pool=[...learnset,...cacheBonus];

  const hits=q.length<1
    ?pool.slice(0,15)
    :pool.filter(s=>s.includes(q)||fmt(s).toLowerCase().includes(q)).slice(0,15);
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
  refreshActivePickers();
}

async function pickMove(inp,slug,name){
  inp.nextElementSibling.style.display='none';
  inp.value=name;
  const side=inp.dataset.side; const idx=+inp.dataset.idx; const mi=+inp.dataset.mi;
  const p=S[side][idx];
  p.moves[mi]=slug;
  p.mdata[mi]=await loadMove(slug);
  onActiveChange();
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
    const side=t.dataset.side; const idx=+t.dataset.idx; const mi=+t.dataset.mi;
    const p=S[side][idx];
    const mv=await loadMove(slug);
    if(!mv){t.value='';return;}
    if(p.slug){
      const learnset=S.pokeCache[p.slug]?.learnset||[];
      const inLearnset=learnset.includes(slug);
      const inLearnedBy=mv.learnedBy?.includes(p.slug);
      if(!inLearnset&&!inLearnedBy){
        p.moves[mi]=''; p.mdata[mi]=null; t.value='';
        t.style.outline='2px solid #ef9a9a';
        setTimeout(()=>t.style.outline='',1500);
        onActiveChange(); return;
      }
      if(!inLearnset&&inLearnedBy) learnset.push(slug);
    }
    p.moves[mi]=slug;
    p.mdata[mi]=mv;
    onActiveChange();
  }
  if(t.classList.contains('abi')) setF(t.dataset.side,+t.dataset.idx,'ability',t.value);
  if(t.classList.contains('ii')) setF(t.dataset.side,+t.dataset.idx,'item',t.value);
});



function dmgSection(label,r){
  if(!r||r.immune) return'';
  const minP=+r.pMin, maxP=+r.pMax;
  const barColor=maxP>=100?'#f44336':maxP>=75?'#ff6d00':maxP>=50?'#ffb300':'#7c83fd';

  let badge;
  if(r.blocked){
    const who=r.blocked==='sturdy'?'Sturdy':'Focus Sash';
    badge=`<span class="badge ok">${who} — Survives at 1 HP</span>`;
  } else if(r.ohko===16)  badge=`<span class="badge kill">OHKO — Guaranteed (16/16)</span>`;
  else if(r.ohko>0)       badge=`<span class="badge warn">OHKO — ${r.ohko}/16 rolls (${(r.ohko/16*100).toFixed(0)}%)</span>`;
  else if(r.dMin*2>=r.dHP)badge=`<span class="badge ok">2HKO — Guaranteed</span>`;
  else if(r.dMax*2>=r.dHP)badge=`<span class="badge warn">2HKO — Possible</span>`;
  else                    badge=`<span class="badge great">No OHKO / No 2HKO</span>`;

  let drainHTML='';
  if(r.move?.drain){
    const pct=Math.abs(r.move.drain);
    const lo=Math.floor(r.dMin*pct/100), hi=Math.floor(r.dMax*pct/100);
    if(r.move.drain<0)
      drainHTML=`<div style="font-size:11px;color:#ef9a9a;margin-top:3px">Recoil: ${lo}–${hi} HP (${pct}%)</div>`;
    else
      drainHTML=`<div style="font-size:11px;color:#81c784;margin-top:3px">Heals: ${lo}–${hi} HP (${pct}%)</div>`;
  }

  let mhHTML='';
  if(r.nHitsMax>1){
    mhHTML=`<div class="mh-counter"
      data-dmin="${r.dMin}" data-dmax="${r.dMax}"
      data-dminp="${r.dMinPost}" data-dmaxp="${r.dMaxPost}"
      data-dhp="${r.dHP}" data-maxh="${r.nHitsMax}">
      <button class="mh-btn" onclick="mhAdj(this,-1)">−</button>
      <span class="mh-count">1</span>× hit
      <button class="mh-btn" onclick="mhAdj(this,1)">+</button>
    </div>`;
  }

  return`<div class="dmg-section">
  <div class="section-label">${label}</div>
  <div class="dmg-bar-bg">
    <div class="dmg-bar-fill low" style="width:${Math.min(100,minP)}%;background:${barColor}"></div>
    <div class="dmg-bar-fill" style="width:${Math.min(100,maxP)}%;background:${barColor}"></div>
  </div>
  <div class="dmg-nums"><strong>${r.dMin}–${r.dMax}</strong> / ${r.dHP} HP &nbsp; (<strong>${r.pMin}%–${r.pMax}%</strong>)</div>
  <div class="dmg-badge">${badge}</div>${drainHTML}${mhHTML}
  </div>`;
}

function mhAdj(btn,delta){
  const ctr=btn.closest('.mh-counter');
  const dMin=+ctr.dataset.dmin, dMax=+ctr.dataset.dmax;
  const dMinP=+ctr.dataset.dminp, dMaxP=+ctr.dataset.dmaxp;
  const dHP=+ctr.dataset.dhp, maxH=+ctr.dataset.maxh;
  const countEl=ctr.querySelector('.mh-count');
  const count=Math.max(1,Math.min(maxH,+countEl.textContent+delta));
  countEl.textContent=count;

  const totMin=dMin+(count-1)*dMinP;
  const totMax=dMax+(count-1)*dMaxP;
  const minPct=(totMin/dHP*100).toFixed(1);
  const maxPct=(totMax/dHP*100).toFixed(1);
  const barColor=+maxPct>=100?'#f44336':+maxPct>=75?'#ff6d00':+maxPct>=50?'#ffb300':'#7c83fd';

  const sec=ctr.closest('.dmg-section');
  const fills=sec.querySelectorAll('.dmg-bar-fill');
  fills[0].style.width=Math.min(100,+minPct)+'%';
  fills[0].style.background=barColor;
  fills[1].style.width=Math.min(100,+maxPct)+'%';
  fills[1].style.background=barColor;
  sec.querySelector('.dmg-nums').innerHTML=
    `<strong>${totMin}–${totMax}</strong> / ${dHP} HP &nbsp; (<strong>${minPct}%–${maxPct}%</strong>)`;

  let badge;
  if(totMin>=dHP)        badge=`<span class="badge kill">OHKO — Guaranteed</span>`;
  else if(totMax>=dHP)   badge=`<span class="badge warn">OHKO — Possible</span>`;
  else if(totMin*2>=dHP) badge=`<span class="badge ok">2HKO — Guaranteed</span>`;
  else if(totMax*2>=dHP) badge=`<span class="badge warn">2HKO — Possible</span>`;
  else                   badge=`<span class="badge great">No OHKO / No 2HKO</span>`;
  sec.querySelector('.dmg-badge').innerHTML=badge;
}

// ── Speed & Turn Simulator ────────────────────────────────────────────────────
function effectiveSpeed(p,side){
  const nat=NATURES[p.nature]||NATURES.none;
  let spe=calcStat(p.base.spe||0,p.ivs.spe,p.evs.spe||0,nat.sp);
  const stage=p.stages?.spe||0;
  if(stage) spe=Math.floor(spe*stageMult(stage));
  if(norm(p.item)==='choice-scarf') spe=Math.floor(spe*1.5);
  const a=norm(p.ability);
  if(p.status==='paralysis'&&a!=='quick-feet') spe=Math.floor(spe*0.5);
  if((a==='swift-swim'&&S.weather==='rain')||(a==='chlorophyll'&&S.weather==='sun')||
     (a==='sand-rush'&&S.weather==='sand')||(a==='slush-rush'&&S.weather==='snow')||
     (a==='surge-surfer'&&S.terrain==='electric')) spe*=2;
  if(a==='quick-feet'&&p.status) spe=Math.floor(spe*1.5);
  if(a==='unburden'&&p.abilityActive) spe*=2;
  if(a==='slow-start'&&p.abilityActive) spe=Math.floor(spe*0.5);
  if(S.tailwind[side]) spe*=2;
  return Math.floor(spe);
}

function buildSpeInfo(p,side,spe){
  const mods=[];
  const stage=p.stages?.spe||0;
  if(stage) mods.push(`${stage>0?'+':''}${stage}`);
  if(norm(p.item)==='choice-scarf') mods.push('Scarf');
  const a=norm(p.ability);
  const wmap={'swift-swim':'rain','chlorophyll':'sun','sand-rush':'sand','slush-rush':'snow','surge-surfer':'electric'};
  const wkey=wmap[a];
  if(wkey&&(wkey==='electric'?S.terrain===wkey:S.weather===wkey)) mods.push(fmt(p.ability));
  if(a==='quick-feet'&&p.status) mods.push('Quick Feet');
  if(a==='unburden'&&p.abilityActive) mods.push('Unburden');
  if(a==='slow-start'&&p.abilityActive) mods.push('Slow Start ↓');
  if(p.status==='paralysis'&&a!=='quick-feet') mods.push('Paralyzed ×0.5');
  if(S.tailwind[side]) mods.push('Tailwind');
  if(S.trickroom) mods.push('TR');
  return`Spe ${spe}${mods.length?` (${mods.join(', ')})`:''}`;
}

function toggleTailwind(side){
  S.tailwind[side]=!S.tailwind[side];
  document.getElementById(`tw-${side}-btn`).classList.toggle('active',S.tailwind[side]);
}
function toggleTrickRoom(){
  S.trickroom=!S.trickroom;
  document.getElementById('tr-btn').classList.toggle('active',S.trickroom);
}

function refreshActivePickers(){
  ['my','en'].forEach(side=>{
    [0,1].forEach(i=>{
      const sel=document.getElementById(`act-${side}-${i}`);
      if(!sel) return;
      const prev=sel.value;
      sel.innerHTML='<option value="">— pick —</option>'+
        S[side].map((p,j)=>p.slug?`<option value="${j}"${String(j)===prev?' selected':''}>${p.name}</option>`:'').join('');
    });
  });
  onActiveChange();
}

function onActiveChange(){
  ['my','en'].forEach(side=>{
    [0,1].forEach(i=>{
      const monSel=document.getElementById(`act-${side}-${i}`);
      const midx=parseInt(monSel?.value);
      const p=!isNaN(midx)?S[side][midx]:null;

      const lbl=document.getElementById(`trn-${side}-${i}`);
      if(lbl) lbl.textContent=p?.name||`Slot ${i+1}`;

      const mvSel=document.getElementById(`mv-${side}-${i}`);
      if(mvSel){
        const prevMv=mvSel.value;
        mvSel.innerHTML='<option value="">— no move —</option>'+(p?p.moves.map((slug,mi)=>{
          if(!slug) return '';
          const m=p.mdata[mi];
          return`<option value="${mi}"${String(mi)===prevMv?' selected':''}>${m?m.name:fmt(slug)}</option>`;
        }).join(''):'');
      }

      // Re-derive spread state after repopulating
      const moveIdx=parseInt(mvSel?.value);
      const mvData=p?.mdata[moveIdx];
      updateTgtArea(side,i,mvData);
    });
  });

  // Rebuild all target dropdowns (active mons may have changed)
  ['my','en'].forEach(side=>{[0,1].forEach(i=>refreshTargets(side,i));});
}

function buildTargetOpts(attackerSide){
  // Enemy mons are valid targets for my side; my mons for enemy side
  const defSide=attackerSide==='my'?'en':'my';
  const opts=['<option value="">— target —</option>'];
  [0,1].forEach(i=>{
    const midx=parseInt(document.getElementById(`act-${defSide}-${i}`)?.value);
    if(isNaN(midx)) return;
    const p=S[defSide][midx];
    if(!p?.slug) return;
    opts.push(`<option value="${defSide}-${midx}">${defSide==='en'?'Enemy':'My'}: ${p.name}</option>`);
  });
  return opts.join('');
}

function updateTgtArea(side,i,mvData){
  const wrap=document.getElementById(`tgt-wrap-${side}-${i}`);
  if(!wrap) return;
  if(mvData?.protect){
    wrap.innerHTML=`<span class="badge ok">Protects</span>`;
    return;
  }
  const isAOP=mvData?.target==='all-other-pokemon';
  const isSpread=mvData?.target==='all-opponents'||isAOP;
  if(isSpread){
    wrap.innerHTML=`<span class="tr-spread-tag">${isAOP?'→ All':'→ Both'}</span>`;
  } else {
    const prev=wrap.querySelector('select')?.value||'';
    wrap.innerHTML=`<span class="tr-arrow">→</span><select class="tr-target" id="tgt-${side}-${i}">${buildTargetOpts(side)}</select>`;
    const sel=document.getElementById(`tgt-${side}-${i}`);
    if(sel&&prev) sel.value=prev;
  }
}

function refreshTargets(side,i){
  const wrap=document.getElementById(`tgt-wrap-${side}-${i}`);
  if(!wrap||wrap.querySelector('.tr-spread-tag')||wrap.querySelector('.badge.ok')) return; // spread/protect — don't touch
  const prev=wrap.querySelector('select')?.value||'';
  wrap.innerHTML=`<span class="tr-arrow">→</span><select class="tr-target" id="tgt-${side}-${i}">${buildTargetOpts(side)}</select>`;
  const sel=document.getElementById(`tgt-${side}-${i}`);
  if(sel&&prev) sel.value=prev;
}

function onMoveChange(side,i){
  const monSel=document.getElementById(`act-${side}-${i}`);
  const midx=parseInt(monSel?.value);
  const p=!isNaN(midx)?S[side][midx]:null;
  const mvSel=document.getElementById(`mv-${side}-${i}`);
  const moveIdx=parseInt(mvSel?.value);
  const mvData=p?.mdata[moveIdx];
  updateTgtArea(side,i,mvData);
}

// ── Simulate Turn ─────────────────────────────────────────────────────────────
function gatherActions(){
  const actions=[];
  ['my','en'].forEach(side=>{
    [0,1].forEach(i=>{
      const monSel=document.getElementById(`act-${side}-${i}`);
      if(!monSel?.value) return;
      const monIdx=parseInt(monSel.value);
      const mon=S[side][monIdx];
      if(!mon?.slug) return;
      const mvSel=document.getElementById(`mv-${side}-${i}`);
      if(!mvSel?.value) return;
      const moveIdx=parseInt(mvSel.value);
      const mvData=mon.mdata[moveIdx];
      if(!mvData) return;
      const isSpread=mvData.target==='all-opponents'||mvData.target==='all-other-pokemon';
      const hh=document.getElementById(`hh-${side}-${i}`)?.checked||false;
      const spe=effectiveSpeed(mon,side);
      if(isSpread){
        const defSide=side==='my'?'en':'my';
        const targets=[0,1].map(j=>{
          const midx=parseInt(document.getElementById(`act-${defSide}-${j}`)?.value);
          return !isNaN(midx)&&S[defSide][midx]?.slug?{mon:S[defSide][midx],side:defSide,monIdx:midx}:null;
        }).filter(Boolean);
        // all-other-pokemon (e.g. Earthquake, Surf) also hits the user's own ally
        if(mvData.target==='all-other-pokemon'){
          [0,1].forEach(j=>{
            if(j===i) return;
            const aIdx=parseInt(document.getElementById(`act-${side}-${j}`)?.value);
            if(!isNaN(aIdx)&&S[side][aIdx]?.slug)
              targets.push({mon:S[side][aIdx],side,monIdx:aIdx,isAlly:true});
          });
        }
        actions.push({mon,side,monIdx,mvData,targets,spread:true,hh,spe});
      } else {
        const tgtSel=document.getElementById(`tgt-${side}-${i}`);
        const tgtVal=tgtSel?.value||'';
        let target=null,tgtSide=null,tgtMonIdx=null;
        if(tgtVal){const parts=tgtVal.split('-');tgtSide=parts[0];tgtMonIdx=parseInt(parts[1]);target=S[tgtSide][tgtMonIdx];}
        actions.push({mon,side,monIdx,mvData,target,tgtSide,tgtMonIdx,spread:false,hh,spe});
      }
    });
  });
  return actions;
}

function simulateTurn(){
  const el=document.getElementById('turn-result');
  const actions=gatherActions();
  const myMoves=actions.filter(a=>a.side==='my');
  if(myMoves.length<1){
    el.innerHTML='<div class="empty">Assign at least one move from My Team</div>';
    return;
  }
  actions.sort((a,b)=>{
    const pa=a.mvData.pri||0,pb=b.mvData.pri||0;
    if(pa!==pb) return pb-pa;
    if(S.trickroom) return a.spe!==b.spe?a.spe-b.spe:0;
    return b.spe!==a.spe?b.spe-a.spe:0;
  });
  // Show compact speed-order strip
  el.innerHTML=buildTurnResult(actions);
  // Open the full detail modal
  openTurnModal(actions);
}

// Compact strip shown in the panel after Calculate
function buildTurnResult(actions){
  const tied=new Set();
  for(let i=1;i<actions.length;i++){
    const a=actions[i],b=actions[i-1];
    if((a.mvData.pri||0)===(b.mvData.pri||0)&&a.spe===b.spe){tied.add(i-1);tied.add(i);}
  }
  let html='';
  if(tied.size) html+=`<div class="tie-warn">⚡ Speed tie present — order is one possible outcome</div>`;
  html+=`<div class="turn-strip">`;
  actions.forEach((a,ord)=>{
    const ordLabel=tied.has(ord)?'½':`${ord+1}`;
    const mvd=resolveMove(a.mvData);
    const isProtect=a.mvData.protect;
    const tgtLabel=isProtect?'<span class="badge ok">Protects</span>':
      a.spread?(a.mvData.target==='all-other-pokemon'?'→ All':'→ Both'):
      a.target?`→ ${a.target.name}`:'';
    const priLabel=a.mvData.pri&&a.mvData.pri!==0?` <span class="badge ${a.mvData.pri>0?'ok':'warn'}">${a.mvData.pri>0?'+':''}${a.mvData.pri}</span>`:'';
    html+=`<div class="strip-row ${a.side}">
      <span class="strip-ord${tied.has(ord)?' tie':''}">${ordLabel}</span>
      <span class="strip-side">${a.side==='my'?'My':'Enemy'}</span>
      <span class="strip-mon">${a.mon.name}</span>
      <span class="strip-move">${tb(mvd.type)} ${a.mvData.name}${priLabel} ${tgtLabel}</span>
      <span class="strip-spe">${a.spe} Spe</span>
    </div>`;
  });
  html+=`</div><div style="font-size:11px;color:var(--sub);text-align:center;margin-top:6px">Full breakdown in the popup ↑</div>`;
  return html;
}

// ── Modal: full turn breakdown ─────────────────────────────────────────────────
function openTurnModal(actions){
  document.getElementById('modal-content').innerHTML=buildModalTurn(actions);
  document.getElementById('modal-overlay').classList.add('open');
}
function closeModal(){
  document.getElementById('modal-overlay').classList.remove('open');
}

function buildModalTurn(actions){
  const tied=new Set();
  for(let i=1;i<actions.length;i++){
    const a=actions[i],b=actions[i-1];
    if((a.mvData.pri||0)===(b.mvData.pri||0)&&a.spe===b.spe){tied.add(i-1);tied.add(i);}
  }

  let html=`<h3 style="margin-bottom:12px;font-size:1rem">Turn Simulation</h3>`;

  // Speed order summary at top
  html+=`<div class="modal-order-strip">`;
  actions.forEach((a,ord)=>{
    const ordLabel=tied.has(ord)?'½':`${ord+1}`;
    html+=`<div class="modal-order-row">
      <span class="turn-ord${tied.has(ord)?' tie':''} ${a.side}">${ordLabel}</span>
      <span><strong>${a.mon.name}</strong> — ${a.mvData.name}</span>
      <span class="turn-spe">${buildSpeInfo(a.mon,a.side,a.spe)}</span>
    </div>`;
  });
  html+=`</div>`;

  // Collect pokemon that are using a protect-type move this turn
  const protecting=new Set(actions.filter(a=>a.mvData.protect).map(a=>a.mon));

  // Each action detail
  actions.forEach((a,ord)=>{
    const ordLabel=tied.has(ord)?'½':`${ord+1}`;
    const mvd=resolveMove(a.mvData);
    const pri=a.mvData.pri||0;
    const priBadge=pri!==0?`<span class="badge ${pri>0?'ok':'warn'}">${pri>0?'+':''}${pri}</span>`:'';
    const accBadge=a.mvData.acc&&a.mvData.acc<100?`<span class="badge warn">${a.mvData.acc}% acc (${100-a.mvData.acc}% miss)</span>`:'';
    const hhBadge=a.hh?`<span class="badge warn">HH ×1.5</span>`:'';
    const spreadBadge=a.spread?`<span class="badge great">Spread ×0.75</span>`:'';
    const tgtLabel=a.spread?`→ <strong>${a.mvData.target==='all-other-pokemon'?'All (incl. Ally)':'Both'}</strong>`:a.target?`→ ${a.tgtSide==='my'?'My':'Enemy'}: <strong>${a.target.name}</strong>`:'';
    const tags=moveTags(mvd);

    // Sucker Punch fails when the target is using a non-damaging move
    let failHTML='';
    if(a.mvData.slug==='sucker-punch'&&!a.spread&&a.target){
      const tgtAct=actions.find(act=>act.mon===a.target);
      if(tgtAct&&!tgtAct.mvData.power)
        failHTML=`<div style="margin-top:6px"><span class="badge kill">Sucker Punch Fails — ${a.target.name} uses ${tgtAct.mvData.name} (non-damaging)</span></div>`;
    }

    html+=`<div class="modal-action">
      <div class="modal-action-head">
        <span class="turn-ord ${a.side}${tied.has(ord)?' tie':''}">${ordLabel}</span>
        <div>
          <div style="font-size:13px;font-weight:700">${a.side==='my'?'My':'Enemy'}: ${a.mon.name}</div>
          <div style="font-size:12px;color:var(--sub)">
            ${a.mon.types.map(tb).join(' ')} uses ${tb(mvd.type)} <strong>${a.mvData.name}</strong>
            ${mvd.power?`(${mvd.dc}, ${mvd.power}BP)`:''} ${tgtLabel}
            ${priBadge}${accBadge}${hhBadge}${spreadBadge}
          </div>
          ${tags?`<div style="margin-top:4px">${tags}</div>`:''}
        </div>
      </div>
      ${failHTML||buildActionScenarios(a,ord===actions.length-1,protecting)}
    </div>`;
  });

  // End of turn
  html+=buildSpeedMatchups(actions);
  html+=buildCombinedDamage(actions);
  html+=buildEndOfTurn(actions);

  return html;
}

function buildActionScenarios(a,movingLast=false,protecting=new Set()){
  if(a.mvData.protect) return`<div style="margin-top:6px"><span class="badge ok">Protected this turn — all attacks blocked</span></div>`;
  if(a.spread){
    const parts=a.targets.map(tgt=>{
      const allyTag=tgt.isAlly?` <span style="color:#ffcc80;font-size:10px">(Ally — self-hit)</span>`:'';
      const label=`<div class="modal-spread-target"><strong>${tgt.mon.name}</strong>${allyTag}</div>`;
      if(protecting.has(tgt.mon)) return`${label}<div style="margin-top:4px"><span class="badge ok">Protected — blocked</span></div>`;
      return`${label}${buildThreeScenarios(a.mon,a.mvData,tgt.mon,a.hh,movingLast)}`;
    }).join('<hr class="divider">');
    return`<div class="spread-result">${parts}</div>`;
  }
  if(!a.mvData.power) return`<div style="margin-top:6px"><span class="badge ok">Status move — no damage</span></div>`;
  if(!a.target) return`<div style="margin-top:6px;font-size:11px;color:var(--sub)">No target selected</div>`;
  if(a.tgtSide===a.side) return`<div style="margin-top:6px;font-size:11px;color:var(--sub)">Targeting ally — no damage calc</div>`;
  if(protecting.has(a.target)) return`<div style="margin-top:6px"><span class="badge ok">Protected — attack blocked</span></div>`;
  return buildThreeScenarios(a.mon,a.mvData,a.target,a.hh,movingLast);
}

function buildThreeScenarios(atk,mv,defender,hh,movingLast=false){
  const r=calc(atk,mv.slug,defender,null,false,hh,movingLast);
  if(!r) return`<div class="empty" style="padding:8px;font-size:11px">Missing stats — fill in the Pokémon card</div>`;
  if(r.immune){
    if(r.disguise) return`<div style="margin-top:6px"><span class="badge ok">Disguise absorbs hit — 0 damage</span></div>`;
    if(r.iceFace) return`<div style="margin-top:6px"><span class="badge ok">Ice Face absorbs hit — 0 damage</span></div>`;
    return`<div style="margin-top:6px"><span class="badge kill">No Effect</span></div>`;
  }

  const phys=mv.dc==='physical';
  const rCrit=calc(atk,mv.slug,defender,null,true,hh,movingLast);

  // Worst case: max defensive EVs + boosting nature + resist berry; force hpPct=100 so Multiscale is active
  const worstItem=getWorstCaseItem(mv,r.eff);
  const worstDef={...defender,
    nature:phys?'bold':'calm',
    item:worstItem||'',
    hpPct:100,
    evs:{hp:31,atk:0,def:phys?31:0,spa:0,spd:phys?0:31,spe:0}};
  const rWorst=calc(atk,mv.slug,worstDef,null,false,hh,movingLast);
  const worstLabel=`Worst case — ${phys?'Bold':'Calm'} + 31 HP / 31 ${phys?'Def':'SpD'}${worstItem?' + '+fmt(worstItem):''}`;

  const effStr=r.eff>1?`<span style="color:#81c784">SE ${r.eff}×</span>`:
    r.eff<1?`<span style="color:#ef9a9a">NVE ${r.eff}×</span>`:`Neutral`;
  const stabStr=r.st>1?` · <span style="color:#90caf9">STAB</span>`:'';
  const accStr=mv.acc&&mv.acc<100?` · <span style="color:#ffcc80">${mv.acc}% acc (${100-mv.acc}% miss)</span>`:'';
  const psyStr=mv.usePhysDef?` · <span style="color:#ce93d8">reads Def</span>`:'';
  const bypassStr=BYPASS_DEF_BOOST.has(mv.slug)?` · <span style="color:#80cbc4">ignores boosts</span>`:'';

  return`<div class="scenario-meta">${effStr}${stabStr}${accStr}${psyStr}${bypassStr}
    &nbsp;·&nbsp; Atk <strong>${r.aStat}</strong> Def <strong>${r.dStat}</strong> HP <strong>${r.dHP}</strong>
  </div>
  ${dmgSection('As set up',r)}
  <hr class="divider">
  ${dmgSection('Critical hit',rCrit)}
  <hr class="divider">
  ${dmgSection(worstLabel,rWorst)}`;
}

// ── Combined Damage ───────────────────────────────────────────────────────────
function buildCombinedDamage(actions){
  const myAtks=actions.filter(a=>a.side==='my'&&!a.mvData.protect&&a.mvData.power);
  if(myAtks.length<2) return '';

  const hitMap=new Map();
  myAtks.forEach(a=>{
    const targets=a.spread
      ?(a.targets?.filter(t=>!t.isAlly&&t.mon?.slug)||[]).map(t=>t.mon)
      :(a.target&&a.tgtSide==='en'&&a.target.slug?[a.target]:[]);
    targets.forEach(tmon=>{
      if(!hitMap.has(tmon)) hitMap.set(tmon,[]);
      hitMap.get(tmon).push(a);
    });
  });

  const groups=[...hitMap.entries()].filter(([,acts])=>acts.length>=2);
  if(!groups.length) return '';

  let html=`<div class="modal-combined"><div class="modal-section-label">Combined Damage</div>`;
  groups.forEach(([tmon,grpActs])=>{
    const calcs=grpActs.map(a=>{
      const r=calc(a.mon,a.mvData.slug,tmon,null,false,a.hh,false);
      return{r,label:`${a.mon.name}'s ${a.mvData.name}`};
    }).filter(({r})=>r&&!r.immune&&!r.status&&r.dMin!=null);
    if(calcs.length<2) return;

    const dHP=calcs[0].r.dHP;
    const totalMin=calcs.reduce((s,{r})=>s+r.dMin,0);
    const totalMax=calcs.reduce((s,{r})=>s+r.dMax,0);
    const minPct=(totalMin/dHP*100).toFixed(1);
    const maxPct=(totalMax/dHP*100).toFixed(1);
    const barColor=+maxPct>=100?'#f44336':+maxPct>=75?'#ff6d00':+maxPct>=50?'#ffb300':'#7c83fd';

    let badge;
    if(totalMin>=dHP)      badge=`<span class="badge kill">Guaranteed KO</span>`;
    else if(totalMax>=dHP) badge=`<span class="badge warn">Possible KO</span>`;
    else                   badge=`<span class="badge great">Not a KO</span>`;

    html+=`<div class="combined-group">
      <div class="combined-label">${calcs.map(c=>c.label).join(' + ')} → <strong>${tmon.name}</strong></div>
      <div class="dmg-bar-bg">
        <div class="dmg-bar-fill low" style="width:${Math.min(100,+minPct)}%;background:${barColor}"></div>
        <div class="dmg-bar-fill" style="width:${Math.min(100,+maxPct)}%;background:${barColor}"></div>
      </div>
      <div class="dmg-nums"><strong>${totalMin}–${totalMax}</strong> / ${dHP} HP &nbsp; (<strong>${minPct}%–${maxPct}%</strong>)</div>
      ${badge}
    </div>`;
  });
  html+=`</div>`;
  return html;
}

// ── End of turn ────────────────────────────────────────────────────────────────
function endOfTurnDelta(p,side,tookContactHit){
  const hp=calcHP(p.base.hp||0,p.ivs.hp,p.evs.hp||0);
  const it=norm(p.item); const a=norm(p.ability);
  const magicGuard=a==='magic-guard';
  const entries=[];

  // Status
  if(p.status==='burn')  entries.push({d:-Math.floor(hp/16),label:'Burn'});
  if(p.status==='poison') entries.push({d:-Math.floor(hp/8), label:'Poison'});
  if(p.status==='badly') entries.push({d:-Math.floor(hp/16),label:'Bad Poison (1st turn)'});

  if(!magicGuard){
    // Item heal/damage
    if(it==='leftovers') entries.push({d:Math.floor(hp/16),label:'Leftovers'});
    if(it==='shell-bell'&&tookContactHit) entries.push({d:0,label:'Shell Bell (varies)'});

    // Weather
    if(S.weather==='sand'){
      const immuneTypes=['rock','steel','ground'];
      const immuneAbils=['sand-veil','sand-rush','sand-force','sand-spit','overcoat'];
      if(!p.types?.some(t=>immuneTypes.includes(t))&&!immuneAbils.includes(a))
        entries.push({d:-Math.floor(hp/16),label:'Sandstorm'});
    }
  }

  const delta=entries.reduce((s,e)=>s+e.d,0);
  return{hp,delta,entries};
}

function buildEndOfTurn(actions){
  // Collect all unique active mons
  const seen=new Set();
  const mons=[];
  ['my','en'].forEach(side=>{
    [0,1].forEach(i=>{
      const monSel=document.getElementById(`act-${side}-${i}`);
      if(!monSel?.value) return;
      const midx=parseInt(monSel.value);
      const p=S[side][midx];
      if(!p?.slug) return;
      const key=`${side}-${midx}`;
      if(seen.has(key)) return;
      seen.add(key);
      // Check if this mon attacked (for Life Orb)
      const attacked=actions.some(a=>a.mon===p&&a.mvData.power);
      mons.push({p,side,attacked});
    });
  });

  const rows=mons.map(({p,side,attacked})=>{
    const {hp,delta,entries}=endOfTurnDelta(p,side,attacked);
    if(!entries.length) return`<div class="eot-row"><span class="eot-name">${p.name}</span><span style="color:var(--sub);font-size:11px">No end-of-turn effects</span></div>`;
    const parts=entries.map(e=>{
      const col=e.d>0?'#81c784':e.d<0?'#ef9a9a':'var(--sub)';
      return`<span style="color:${col}">${e.label} ${e.d>0?'+':''}${e.d||'?'} HP</span>`;
    }).join(' · ');
    const netCol=delta>0?'#81c784':delta<0?'#ef9a9a':'var(--sub)';
    const net=delta!==0?` <strong style="color:${netCol}">(net ${delta>0?'+':''}${delta} HP)</strong>`:'';
    return`<div class="eot-row"><span class="eot-name">${p.name}</span><span>${parts}${net}</span></div>`;
  }).join('');

  return`<div class="modal-eot">
    <div class="modal-section-label">End of Turn</div>
    ${rows||'<div style="color:var(--sub);font-size:11px">No active Pokémon with end-of-turn effects</div>'}
  </div>`;
}

// ── Speed Matchups ────────────────────────────────────────────────────────────
function calcSpeRaw(p,nature,evSpe,item,ability,tailwind,status,weather,terrain){
  const nat=NATURES[nature]||NATURES.none;
  let s=calcStat(p.base.spe||0,31,evSpe,nat.sp);
  if(norm(item)==='choice-scarf') s=Math.floor(s*1.5);
  const a=norm(ability);
  if(status==='paralysis'&&a!=='quick-feet') s=Math.floor(s*0.5);
  if((a==='swift-swim'&&weather==='rain')||(a==='chlorophyll'&&weather==='sun')||
     (a==='sand-rush'&&weather==='sand')||(a==='slush-rush'&&weather==='snow')||
     (a==='surge-surfer'&&terrain==='electric')) s*=2;
  if(a==='quick-feet'&&status) s=Math.floor(s*1.5);
  if(tailwind) s*=2;
  return Math.floor(s);
}

function speRow(val,label,out,exact,pct,predicted){
  const icon=out==='faster'?'⚠':out==='tied'?'≈':'✓';
  const res=out==='faster'?'Moves before you':out==='tied'?'Speed tie':'You move first';
  const pctTag=pct!=null?`<span class="spe-pct">${pct}%</span>`:'';
  return`<div class="spe-row ${out}${exact?' exact':''}${predicted?' predicted':''}">
    <span class="spe-lbl">${label}${pctTag}</span>
    <span class="spe-val">${val}</span>
    <span class="spe-res">${icon} ${res}</span>
  </div>`;
}

function buildSpeedMatchups(actions){
  const myActs=actions.filter(a=>a.side==='my');
  const enActs=actions.filter(a=>a.side==='en');
  if(!myActs.length||!enActs.length) return'';

  let html=`<div class="modal-speed"><div class="modal-section-label">Speed Matchups</div>`;

  myActs.forEach(myA=>{
    enActs.forEach(enA=>{
      const mySpe=myA.spe;
      const p=enA.mon;
      const tr=S.trickroom;
      const wx=S.weather,te=S.terrain;
      const pAbil=p.ability||'';

      const scenarios=[
        {label:'Neutral, 0 EVs',       spe:calcSpeRaw(p,'none',0,'',pAbil,false,'',wx,te)},
        {label:'Jolly, max EVs',        spe:calcSpeRaw(p,'jolly',31,'',pAbil,false,'',wx,te)},
        {label:'Scarf + Jolly, max EVs',spe:calcSpeRaw(p,'jolly',31,'choice-scarf',pAbil,false,'',wx,te)},
        {label:'Tailwind + Jolly, max EVs',spe:calcSpeRaw(p,'jolly',31,'',pAbil,true,'',wx,te)},
        {label:'Paralyzed + Jolly, max EVs',spe:calcSpeRaw(p,'jolly',31,'',pAbil,false,'paralysis',wx,te)},
      ];

      // weather/terrain speed ability — show scenario if condition isn't currently active
      const WABIL={'swift-swim':['rain',false],'chlorophyll':['sun',false],
        'sand-rush':['sand',false],'slush-rush':['snow',false],'surge-surfer':['electric',true]};
      const abilInfo=WABIL[norm(pAbil)];
      if(abilInfo){
        const[req,isTerrain]=abilInfo;
        const active=isTerrain?te===req:wx===req;
        if(!active){
          const owx=isTerrain?wx:req, ote=isTerrain?req:te;
          scenarios.push({label:`${fmt(pAbil)} active, Jolly, max EVs`,spe:calcSpeRaw(p,'jolly',31,'',pAbil,false,'',owx,ote)});
        }
      }
      if(norm(pAbil)==='quick-feet')
        scenarios.push({label:'Quick Feet active, Jolly, max EVs',spe:calcSpeRaw(p,'jolly',31,'',pAbil,false,'burn',wx,te)});

      // dedup by speed value
      const seen=new Set();
      const unique=scenarios.filter(sc=>{
        if(seen.has(sc.spe)) return false;
        seen.add(sc.spe); return true;
      });
      unique.sort((a,b)=>tr?a.spe-b.spe:b.spe-a.spe);

      function outcome(enSpe){
        const fst=tr?enSpe<mySpe:enSpe>mySpe;
        return fst?'faster':enSpe===mySpe?'tied':'slower';
      }

      const pred=S.predictData[p.slug]||null;

      // Build prediction rows from tournament data
      let predHTML='';
      if(pred?.speeds?.length){
        const sorted=tr?[...pred.speeds].sort((a,b)=>a.spe-b.spe):pred.speeds;
        predHTML=`<div class="spe-group-label">Tournament data</div>`+
          sorted.map(s=>speRow(s.spe,s.label,outcome(s.spe),false,s.pct,true)).join('');
      } else if(pred){
        const itemStr=pred.topItem?fmt(pred.topItem):'?';
        const abilStr=pred.topAbility?fmt(pred.topAbility):'?';
        predHTML=`<div class="spe-info-row">Most common: ${itemStr} · ${abilStr}</div>`;
      }

      const trNote=tr?` <span style="font-size:10px;color:#ffcc80">(TR)</span>`:'';
      html+=`<div class="speed-matchup">
        <div class="spe-my-row">${myA.mon.name} — <strong>${mySpe}</strong>${trNote} <span class="spe-mods">${buildSpeInfo(myA.mon,myA.side,mySpe)}</span></div>
        <div class="spe-vs">vs <strong>${enA.mon.name}</strong> ${p.types.map(tb).join('')}</div>
        <div class="spe-rows">
          ${speRow(enA.spe,'As configured',outcome(enA.spe),true)}
          ${predHTML}
          ${predHTML?'<div class="spe-group-label">Benchmarks</div>':''}
          ${unique.map(sc=>speRow(sc.spe,sc.label,outcome(sc.spe),false)).join('')}
        </div>
      </div>`;
    });
  });

  html+=`</div>`;
  return html;
}

// ── Init ──────────────────────────────────────────────────────────────────────
// Fire-and-forget: loads learned_by_pokemon for competitive moves in the background.
// By the time a user has typed a pokemon name and picked one, these will be ready.
function preloadMoves(){
  PRELOAD_MOVES.forEach(slug=>{if(!S.moveCache[slug]) loadMove(slug);});
}

renderTeams();
preloadMoves();
loadPredictData();
