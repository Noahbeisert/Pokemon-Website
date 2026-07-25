// Run the team-preview analysis from the command line:
//   node js/preview-cli.mjs milotic,raichu,ceruledge,incineroar,sinistcha,floette blastoise,delphox,sneasler,kingambit,sinistcha
import { readFileSync } from 'fs';
import { createRequire } from 'module';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { createPreviewLogic } = require(join(here, 'team-preview-logic.js'));

const load = f => JSON.parse(readFileSync(join(here, '..', 'data', f), 'utf-8'));
const logic = createPreviewLogic({
  profiles: load('TeamProfiles.json'),
  bringRates: load('BringRates.json'),
  archetypes: load('TeamArchetypes.json'),
});

const [myArg, oppArg] = process.argv.slice(2);
const myTeam = myArg.split(',');
const oppTeamIn = oppArg.split(',');

const r = logic.analyze(myTeam, oppTeamIn);
const name = s => r.my.eff[s]?.name || r.opp.eff[s]?.name || s;

function sideReport(label, side, team) {
  const m = side.match;
  console.log(`\n═══ ${label} — matched ${m.teamCount} DB teams` +
    (m.partial ? ' (PARTIAL: closest archetypes only)' : '') + ' ═══');
  team.forEach(slug => {
    const e = side.eff[slug];
    if (!e) { console.log(`  ${slug}: no profile`); return; }
    const mega = e.isMega ? `  [MEGA: ${e.stoneName}, flex=${e.flex.toFixed(2)}]` : '';
    const pred = e.predicted ? `  [PREDICTED 6th: ${e.predicted}%]` : '';
    console.log(`\n  ${e.name} (${e.source}, n=${e.teams})${mega}${pred}`);
    console.log(`    item: ${e.item}${e.itemPct !== null ? ` ${e.itemPct}%` : ''}  ability: ${e.ability}${e.abilityPct !== null ? ` ${e.abilityPct}%` : ''}`);
    e.sets.slice(0, 3).forEach(s =>
      console.log(`    set ${s.pct}%: ${s.moves.join(' / ')}  roles=[${s.roles.join(',')}]`));
    const roles = Object.entries(e.roleProbs).map(([k, v]) => v === null ? k : `${k} ${v}%`).join(', ');
    console.log(`    roles: ${roles}`);
  });
}

sideReport('MY TEAM', r.my, r.myTeam);
sideReport('OPPONENT', r.opp, r.oppTeam);
if (r.predicted) console.log(`\n  → predicted hidden 6th: ${name(r.predicted.slug)} (${r.predicted.pct}%)`);

console.log('\n═══ OPPONENT BRING PREDICTION ═══');
Object.entries(r.oppBring.marginal).sort((a, b) => b[1] - a[1]).forEach(([slug, p]) =>
  console.log(`  ${name(slug).padEnd(14)} ${(p * 100).toFixed(0)}%`));
console.log('  Top scenarios:');
r.oppBring.ranked.slice(0, 3).forEach((sc, i) => {
  const syn = logic.synergyLabel(sc.combo.map(m => m.slug), r.opp.eff);
  console.log(`   #${i + 1} (${sc.total.toFixed(3)}) ${sc.combo.map(m => name(m.slug)).join(' + ')}${syn ? `  [${syn}]` : ''}`);
});

if (r.plan) {
  console.log('\n═══ BATTLE PLAN ═══');
  console.log(`  Recommended bring-4: ${r.plan.myBestBring.map(name).join(' · ')}`);
  console.log(`  Recommended lead: ${name(r.plan.myLead.p1)} + ${name(r.plan.myLead.p2)}  (back: ${r.plan.myLead.back.map(name).join(', ')})`);
  console.log('  Counter-leads:');
  r.plan.counterLeads.forEach(cl =>
    console.log(`   vs ${name(cl.oppP1)}${cl.oppTag1} + ${name(cl.oppP2)}${cl.oppTag2}  →  ${name(cl.myP1)} + ${name(cl.myP2)}`));
  console.log('  My bring-4 options (top 3):');
  r.plan.myScored.slice(0, 3).forEach((s, i) =>
    console.log(`   #${i + 1} (${s.score.toFixed(3)}) ${s.bring.map(name).join(' + ')}`));
}
