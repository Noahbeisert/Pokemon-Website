// Team-preview analysis logic — pure functions, no DOM.
// Used by team-preview.html in the browser and runnable in node for testing:
//   node js/preview-cli.mjs milotic,raichu,... blastoise,delphox,...

const MOVE_TYPES = {
  'dragon-claw':'Dragon','draco-meteor':'Dragon','dragon-pulse':'Dragon','outrage':'Dragon',
  'dragon-rush':'Dragon','breaking-swipe':'Dragon','scale-shot':'Dragon',
  'earthquake':'Ground','earth-power':'Ground','bulldoze':'Ground','high-horsepower':'Ground',
  'stomping-tantrum':'Ground','scorching-sands':'Ground',
  'rock-slide':'Rock','stone-edge':'Rock','rock-tomb':'Rock',
  'iron-head':'Steel','flash-cannon':'Steel','gyro-ball':'Steel','heavy-slam':'Steel','steel-roller':'Steel',
  'close-combat':'Fighting','superpower':'Fighting','focus-blast':'Fighting','drain-punch':'Fighting',
  'mach-punch':'Fighting','body-press':'Fighting','brick-break':'Fighting','cross-chop':'Fighting',
  'aura-sphere':'Fighting','low-kick':'Fighting',
  'flare-blitz':'Fire','fire-blast':'Fire','heat-wave':'Fire','flamethrower':'Fire','sacred-fire':'Fire',
  'overheat':'Fire','fire-fang':'Fire','flame-charge':'Fire','bitter-blade':'Fire',
  'moonblast':'Fairy','dazzling-gleam':'Fairy','play-rough':'Fairy','draining-kiss':'Fairy',
  'light-of-ruin':'Fairy',
  'hyper-voice':'Normal','return':'Normal','double-edge':'Normal','body-slam':'Normal',
  'quick-attack':'Normal','extreme-speed':'Normal','facade':'Normal','boomburst':'Normal',
  'weather-ball':'Normal',
  'brave-bird':'Flying','aerial-ace':'Flying','air-slash':'Flying','hurricane':'Flying','dual-wingbeat':'Flying',
  'sucker-punch':'Dark','kowtow-cleave':'Dark','knock-off':'Dark','crunch':'Dark','night-slash':'Dark',
  'dark-pulse':'Dark','throat-chop':'Dark','foul-play':'Dark',
  'psychic':'Psychic','psyshock':'Psychic','zen-headbutt':'Psychic','expanding-force':'Psychic','psycho-cut':'Psychic',
  'shadow-ball':'Ghost','poltergeist':'Ghost','shadow-sneak':'Ghost','last-respects':'Ghost','hex':'Ghost',
  'phantom-force':'Ghost','spirit-shackle':'Ghost',
  'surf':'Water','hydro-pump':'Water','scald':'Water','aqua-jet':'Water','wave-crash':'Water',
  'liquidation':'Water','flip-turn':'Water','waterfall':'Water','muddy-water':'Water',
  'origin-pulse':'Water','steam-eruption':'Water','water-spout':'Water',
  'thunderbolt':'Electric','thunder':'Electric','wild-charge':'Electric','volt-tackle':'Electric',
  'discharge':'Electric','volt-switch':'Electric','zap-cannon':'Electric',
  'blizzard':'Ice','ice-beam':'Ice','icicle-crash':'Ice','ice-punch':'Ice','icy-wind':'Ice','ice-shard':'Ice',
  'avalanche':'Ice','freeze-dry':'Ice','ice-hammer':'Ice','frost-breath':'Ice',
  'leaf-storm':'Grass','giga-drain':'Grass','solar-beam':'Grass','energy-ball':'Grass','power-whip':'Grass',
  'wood-hammer':'Grass','matcha-gotcha':'Grass','seed-bomb':'Grass','petal-blizzard':'Grass',
  'flower-trick':'Grass','grassy-glide':'Grass',
  'sludge-bomb':'Poison','sludge-wave':'Poison','poison-jab':'Poison','gunk-shot':'Poison','dire-claw':'Poison',
  'bug-buzz':'Bug','x-scissor':'Bug','u-turn':'Bug','lunge':'Bug','fell-stinger':'Bug','pollen-puff':'Bug',
  'iron-tail':'Steel',
};

const ROLE_BRING_SCORE = {
  'fake-out': 0.88, 'tr-setter': 0.80, 'tailwind-setter': 0.80,
  'weather-setter': 0.72, 'redirector': 0.65, 'setup': 0.55,
  'spread-attacker': 0.50, 'screen-setter': 0.50, 'priority': 0.45,
  'pivot': 0.40, 'weather-speed': 0.40, 'support': 0.38,
};

const ROLE_LEAD_SCORE = {
  'fake-out': 0.92, 'tailwind-setter': 0.82, 'tr-setter': 0.78,
  'weather-setter': 0.70, 'redirector': 0.65, 'screen-setter': 0.60,
  'terrain-setter': 0.55, 'speed-drop': 0.50, 'setup': 0.42,
  'weather-speed': 0.38, 'spread-attacker': 0.30, 'pivot': 0.30,
};

const WEATHER_SET = { 'Drizzle':'rain', 'Drought':'sun', 'Sand Stream':'sand', 'Snow Warning':'snow' };
const WEATHER_BEATS = { rain:'sun', sun:'rain', sand:'rain', snow:'sun' };
const WEATHER_MOVE_SLUGS = {
  'rain-dance':'rain', 'sunny-day':'sun', 'sandstorm':'sand', 'hail':'snow',
  'snowscape':'snow', 'chilly-reception':'snow',
};

// Softmax temperature turning combo scores into a bring-4 probability distribution
const COMBO_TEMP = 0.08;

function combinations(arr, k) {
  if (k === 0) return [[]];
  if (arr.length < k) return [];
  const [first, ...rest] = arr;
  return [
    ...combinations(rest, k - 1).map(c => [first, ...c]),
    ...combinations(rest, k),
  ];
}

function slugifyItem(name) {
  return (name || '').toLowerCase().trim().replace(/ /g, '-').replace(/'/g, '');
}

function stripMega(slug) {
  return slug.replace(/-mega(-x|-y)?$/, '');
}

function createPreviewLogic({ profiles, bringRates, archetypes }) {
  const PROFILES = profiles;
  const BRING_RATES = bringRates || {};
  const A = archetypes;
  const monIdOf = new Map(A.mons.map((s, i) => [s, i]));

  // stone item slug -> base pokemon slug (values in file may be mega-form slugs)
  const STONES = {};
  for (const [stone, base] of Object.entries(A.stones)) STONES[stone] = stripMega(base);

  // ── Archetype matching ──────────────────────────────────────────────────────
  // Comps where every entered mon appears. With 6 entered that's an exact match;
  // with 5 it's the "predict the 6th" case. Falls back to (len-1)-overlap when
  // nothing contains the full entry (off-meta team or a reading mistake).
  function matchTeam(enteredSlugs) {
    const ids = enteredSlugs.map(s => monIdOf.get(s)).filter(x => x !== undefined);
    const need = ids.length;
    if (!need) return { matches: [], teamCount: 0, partial: false, predictedSixth: [] };

    const idSet = new Set(ids);
    const overlapOf = comp => comp.m.reduce((n, id) => n + idSet.has(id), 0);

    let matches = A.comps.filter(c => overlapOf(c) === need);
    let partial = false;
    if (!matches.length && need >= 4) {
      matches = A.comps.filter(c => overlapOf(c) === need - 1);
      partial = true;
    }

    const teamCount = matches.reduce((s, c) => s + c.n, 0);

    let predictedSixth = [];
    if (!partial && need < 6 && matches.length) {
      const extra = new Map();
      matches.forEach(c => c.m.forEach(id => {
        if (!idSet.has(id)) extra.set(id, (extra.get(id) || 0) + c.n);
      }));
      predictedSixth = [...extra.entries()]
        .map(([id, n]) => ({ slug: A.mons[id], pct: Math.round(100 * n / teamCount) }))
        .sort((a, b) => b.pct - a.pct)
        .slice(0, 3);
    }
    return { matches, teamCount, partial, predictedSixth };
  }

  // ── Effective per-mon profile: archetype-conditional sets, roles, item ──────
  function effProfileFor(slug, matches) {
    const p = PROFILES[slug];
    const id = String(monIdOf.get(slug));

    let denom = 0;
    const setAgg = new Map();
    matches.forEach(comp => {
      const sets = comp.s && comp.s[id];
      if (!sets) return;
      denom += comp.n;
      sets.forEach(st => {
        const key = st.mv.join(',');
        let agg = setAgg.get(key);
        if (!agg) {
          agg = { mvIds: st.mv, n: 0, items: new Map(), abils: new Map(), roleIds: new Set() };
          setAgg.set(key, agg);
        }
        agg.n += st.n;
        agg.items.set(st.it, (agg.items.get(st.it) || 0) + st.n);
        agg.abils.set(st.ab, (agg.abils.get(st.ab) || 0) + st.n);
        st.r.forEach(r => agg.roleIds.add(r));
      });
    });

    if (!denom) return speciesFallback(slug);

    const top = m => [...m.entries()].sort((a, b) => b[1] - a[1])[0];
    const sets = [...setAgg.values()].sort((a, b) => b.n - a.n).map(agg => ({
      moves:   agg.mvIds.map(i => A.moves[i]),
      item:    A.items[top(agg.items)[0]],
      ability: A.abils[top(agg.abils)[0]],
      roles:   [...agg.roleIds].map(i => A.roles[i]),
      count:   agg.n,
      pct:     Math.round(100 * agg.n / denom),
    })).filter(s => s.pct >= 5);

    const moveProbs = {}, roleProbs = {};
    const itemCount = new Map(), abilCount = new Map();
    sets.forEach(s => {
      s.moves.forEach(mv => { moveProbs[mv] = (moveProbs[mv] || 0) + s.count; });
      s.roles.forEach(r => { roleProbs[r] = (roleProbs[r] || 0) + s.count; });
      itemCount.set(s.item, (itemCount.get(s.item) || 0) + s.count);
      abilCount.set(s.ability, (abilCount.get(s.ability) || 0) + s.count);
    });
    for (const k in moveProbs) moveProbs[k] = Math.round(100 * moveProbs[k] / denom);
    for (const k in roleProbs) roleProbs[k] = Math.round(100 * roleProbs[k] / denom);

    const [item] = top(itemCount), [ability] = top(abilCount);
    return finishEff(slug, p, {
      source: 'archetype', teams: denom, sets, moveProbs, roleProbs,
      item, itemPct: Math.round(100 * itemCount.get(item) / denom),
      ability, abilityPct: Math.round(100 * abilCount.get(ability) / denom),
    });
  }

  function speciesFallback(slug) {
    const p = PROFILES[slug];
    if (!p) return null;
    const sets = (p.sets || []).map(s => ({
      moves: s.moves.map(m => m.slug), item: s.item, ability: s.ability,
      roles: s.roles, count: s.count, pct: s.pct,
    }));
    const moveProbs = {}, roleProbs = {};
    sets.forEach(s => {
      s.moves.forEach(mv => { moveProbs[mv] = Math.max(moveProbs[mv] || 0, s.pct); });
      s.roles.forEach(r => { roleProbs[r] = Math.max(roleProbs[r] || 0, s.pct); });
    });
    p.roles.forEach(r => { if (!(r in roleProbs)) roleProbs[r] = null; });
    return finishEff(slug, p, {
      source: 'species', teams: p.team_count, sets, moveProbs, roleProbs,
      item: p.top_item, itemPct: null, ability: p.top_ability, abilityPct: null,
    });
  }

  function finishEff(slug, p, eff) {
    eff.slug = slug;
    eff.name = p ? p.name : slug;
    const stoneBase = STONES[slugifyItem(eff.item)];
    eff.isMega = stoneBase === stripMega(slug);
    eff.stoneName = eff.isMega ? eff.item : null;
    eff.megaForm = null;
    if (eff.isMega && p && p.mega) {
      const f = p.mega.forms.find(f => slugifyItem(f.stone) === slugifyItem(eff.item));
      eff.megaForm = f || p.mega.forms[0];
    }
    // Flex viability: how playable is the base form without mega-evolving?
    // Data-driven — the species' non-stone usage rate across the whole DB
    // (Venusaur/Aerodactyl ~56% → flexable; Floette/Delphox ~1% → stone-locked).
    eff.flex = p ? Math.min(0.9, Math.max(0.15, 1 - (p.stone_pct || 0) / 100)) : 0.5;
    return eff;
  }

  function analyzeSide(enteredSlugs) {
    const match = matchTeam(enteredSlugs);
    const eff = {};
    enteredSlugs.forEach(slug => {
      const e = effProfileFor(slug, match.partial ? [] : match.matches);
      if (e) eff[slug] = e;
    });
    return { match, eff };
  }

  // ── Type effectiveness ──────────────────────────────────────────────────────
  function maxStabEff(atkProfile, defProfile) {
    const chart = defProfile.defensive.chart || {};
    let max = 0, bestType = '—';
    for (const t of atkProfile.stab_types) {
      const m = chart[t] ?? 1;
      if (m > max) { max = m; bestType = t; }
    }
    if (max === 0) {
      bestType = atkProfile.stab_types.find(t => (chart[t] ?? 1) === 0) || '—';
    }
    return { mult: max, bestType };
  }

  // Coverage including carried moves (from the archetype-matched set when
  // available), not just STAB. `moves` = array of move slugs.
  function bestCoverage(atkSlug, defSlug, moves) {
    const ap = PROFILES[atkSlug], dp = PROFILES[defSlug];
    if (!ap || !dp) return { mult: 1, bestType: '—' };
    let { mult: best, bestType } = maxStabEff(ap, dp);
    const chart = dp.defensive.chart || {};
    (moves || []).forEach(mv => {
      const mtype = MOVE_TYPES[mv];
      if (!mtype || ap.stab_types.includes(mtype)) return;
      const m = chart[mtype] ?? 1;
      if (m > best) { best = m; bestType = mtype; }
    });
    return { mult: best, bestType };
  }

  function effMoves(eff, minPct = 25) {
    if (!eff) return [];
    return Object.entries(eff.moveProbs)
      .filter(([, pct]) => pct === null || pct >= minPct)
      .map(([mv]) => mv);
  }

  function threatToTeam(atkSlug, atkEff, defSlugs, movesOverride) {
    if (!PROFILES[atkSlug] || !defSlugs.length) return 0;
    const moves = movesOverride || effMoves(atkEff);
    const total = defSlugs.reduce((s, d) =>
      s + (PROFILES[d] ? bestCoverage(atkSlug, d, moves).mult : 0), 0);
    return total / defSlugs.length;
  }

  // ── Role helpers over effective profiles ────────────────────────────────────
  // Role prob: null (species-level, unquantified) counts as certain.
  function roleP(eff, role) {
    if (!eff || !(role in eff.roleProbs)) return 0;
    const p = eff.roleProbs[role];
    return p === null ? 1 : p / 100;
  }

  function weightedRoleScore(eff, table, floor) {
    let best = floor;
    for (const role in eff.roleProbs) {
      const s = (table[role] || 0) * roleP(eff, role);
      if (s > best) best = s;
    }
    return Math.min(1, best);
  }

  // ── Bring & lead scoring ────────────────────────────────────────────────────
  function computeBringScore(slug, eff, vsTeamSlugs, vsEff) {
    const rate = BRING_RATES[slug];
    const n = rate ? rate.appearances : 0;
    const confidence = Math.min(1, Math.sqrt(n / 30));
    const historical = rate ? rate.bring_rate * confidence : 0;

    const roleScore = weightedRoleScore(eff, ROLE_BRING_SCORE, 0.28);

    let covScore = 0;
    if (vsTeamSlugs && vsTeamSlugs.length) {
      let maxMult = 0;
      vsTeamSlugs.forEach(d => {
        const { mult } = bestCoverage(slug, d, effMoves(eff));
        if (mult > maxMult) maxMult = mult;
      });
      covScore = maxMult >= 4 ? 1 : maxMult >= 2 ? 0.6 : 0;
    }

    const megaBonus = eff.isMega ? 0.08 : 0;
    return 0.35 * historical + 0.40 * roleScore + 0.25 * covScore + megaBonus;
  }

  function computeLeadScore(slug, eff, rolesOverride) {
    const rate = BRING_RATES[slug];
    const n = rate ? rate.appearances : 0;
    const confidence = Math.min(1, Math.sqrt(n / 30));
    const historical = rate ? rate.lead_rate * confidence : 0;
    let roleScore;
    if (rolesOverride) {
      roleScore = Math.min(1, rolesOverride.reduce((best, r) =>
        Math.max(best, ROLE_LEAD_SCORE[r] || 0), 0.15));
    } else {
      roleScore = weightedRoleScore(eff, ROLE_LEAD_SCORE, 0.15);
    }
    return 0.5 * historical + 0.5 * roleScore;
  }

  function synergyBonus(slugs, effMap) {
    let bonus = 0;
    const effs = slugs.map(s => effMap[s]).filter(Boolean);
    const has = role => effs.some(e => roleP(e, role) >= 0.5);
    const slow = s => PROFILES[s] && PROFILES[s].speed_tier === 'slow';
    const attacker = e => ['spread-attacker'].some(r => roleP(e, r) >= 0.5) ||
      (PROFILES[e.slug] && PROFILES[e.slug].attack_axis);
    if (has('tr-setter') && slugs.some(slow)) bonus += 0.30;
    if (has('weather-setter') && has('weather-speed')) bonus += 0.30;
    if (has('tailwind-setter') && effs.some(attacker)) bonus += 0.20;
    if (has('fake-out') && has('setup')) bonus += 0.20;
    if (has('redirector') && effs.some(attacker)) bonus += 0.15;
    return bonus;
  }

  function synergyLabel(slugs, effMap) {
    const effs = slugs.map(s => effMap[s]).filter(Boolean);
    const has = role => effs.some(e => roleP(e, role) >= 0.5);
    const slow = s => PROFILES[s] && PROFILES[s].speed_tier === 'slow';
    const labels = [];
    if (has('tr-setter') && slugs.some(slow)) labels.push('TR core');
    if (has('weather-setter') && has('weather-speed')) labels.push('Weather core');
    if (has('tailwind-setter')) labels.push('Tailwind core');
    if (has('fake-out') && has('setup')) labels.push('Fake-out + Setup');
    else if (has('redirector') && has('setup')) labels.push('Redirect + Setup');
    return labels.join(' · ');
  }

  // Mega exclusivity: only one mega evolves per battle. The strongest mega user
  // in the combo keeps its full score; every additional stone holder is valued
  // as its base form (score × flex viability).
  function megaAdjustedScores(combo, effMap) {
    const megas = combo.filter(m => effMap[m.slug] && effMap[m.slug].isMega)
      .sort((a, b) => b.score - a.score);
    const devalued = new Map();
    megas.slice(1).forEach(m => devalued.set(m.slug, effMap[m.slug].flex));
    return combo.map(m => ({ ...m, adjScore: m.score * (devalued.get(m.slug) || 1) }));
  }

  function computeBringCombos(teamSlugs, vsTeamSlugs, effMap, vsEffMap) {
    const scored = teamSlugs.map(slug => {
      const eff = effMap[slug];
      if (!eff) return { slug, name: slug, score: 0.5, leadScore: 0.3 };
      return {
        slug, name: eff.name,
        score: computeBringScore(slug, eff, vsTeamSlugs, vsEffMap),
        leadScore: computeLeadScore(slug, eff),
      };
    });

    const combos = combinations(scored, Math.min(4, scored.length));
    const ranked = combos.map(combo => {
      const adjusted = megaAdjustedScores(combo, effMap);
      const base = adjusted.reduce((s, m) => s + m.adjScore, 0) / adjusted.length;
      const syn = synergyBonus(combo.map(m => m.slug), effMap);
      return { combo: adjusted, total: base + syn * 0.3, syn };
    }).sort((a, b) => b.total - a.total);

    // Bring-4 distribution → per-mon marginal probability
    const weights = ranked.map(r => Math.exp(r.total / COMBO_TEMP));
    const wSum = weights.reduce((a, b) => a + b, 0) || 1;
    const marginal = {};
    ranked.forEach((r, i) => r.combo.forEach(m => {
      marginal[m.slug] = (marginal[m.slug] || 0) + weights[i] / wSum;
    }));

    return { ranked, marginal };
  }

  // ── Weather counter-play ────────────────────────────────────────────────────
  function monWeather(slug, eff) {
    const p = PROFILES[slug];
    if (!p) return null;
    if (eff && eff.megaForm && WEATHER_SET[eff.megaForm.ability]) return WEATHER_SET[eff.megaForm.ability];
    if (eff && WEATHER_SET[eff.ability]) return WEATHER_SET[eff.ability];
    if (p.mega) {
      for (const f of p.mega.forms) if (WEATHER_SET[f.ability]) return WEATHER_SET[f.ability];
    }
    return WEATHER_SET[p.top_ability] || null;
  }

  function weatherCounterBonus(slug, eff, vsTeamSlugs, vsEffMap) {
    const myWeather = monWeather(slug, eff);
    if (!myWeather) return 0;
    const vsWeathers = new Set(vsTeamSlugs.map(s => monWeather(s, vsEffMap[s])).filter(Boolean));
    return vsWeathers.has(WEATHER_BEATS[myWeather]) ? 4.0 : 0;
  }

  function weatherBackThreats(myWeatherSlugs, myEffMap, oppFullTeam, oppEffMap, oppPredictedBring) {
    const myWeathers = new Set(myWeatherSlugs.map(s => monWeather(s, myEffMap[s])).filter(Boolean));
    if (!myWeathers.size) return [];
    const inBring = new Set(oppPredictedBring);
    const threats = [];
    oppFullTeam.forEach(slug => {
      const p = PROFILES[slug], eff = oppEffMap[slug];
      if (!p) return;
      const label = inBring.has(slug) ? 'IN bring' : 'possible bring';
      const oppW = monWeather(slug, eff);
      if (oppW && [...myWeathers].some(mw => WEATHER_BEATS[oppW] === mw)) {
        threats.push({ name: p.name, desc: `switch-in ${oppW} (${(eff && eff.ability) || p.top_ability})`, label });
        return;
      }
      for (const mv of effMoves(eff)) {
        const moveWx = WEATHER_MOVE_SLUGS[mv];
        if (moveWx && [...myWeathers].some(mw => WEATHER_BEATS[moveWx] === mw)) {
          const ability = (eff && eff.ability) || p.top_ability;
          const priorityTag = ability === 'Prankster' ? ' [PRIORITY via Prankster]' : '';
          threats.push({ name: p.name, desc: `${mv.replace(/-/g,' ')}${priorityTag}`, label });
          return;
        }
      }
    });
    return threats;
  }

  // ── Lead pair + battle plan solve ───────────────────────────────────────────
  function leadPairScore(slug1, slug2, vsTeamSlugs, effMap, vsEffMap, set1, set2) {
    const e1 = effMap[slug1], e2 = effMap[slug2];
    if (!e1 || !e2) return 0;
    let s = computeLeadScore(slug1, e1, set1 && set1.roles) +
            computeLeadScore(slug2, e2, set2 && set2.roles);
    s += synergyBonus([slug1, slug2], effMap) * 0.2;
    s += threatToTeam(slug1, e1, vsTeamSlugs, set1 && set1.moves);
    s += threatToTeam(slug2, e2, vsTeamSlugs, set2 && set2.moves);
    s += Math.max(weatherCounterBonus(slug1, e1, vsTeamSlugs, vsEffMap),
                  weatherCounterBonus(slug2, e2, vsTeamSlugs, vsEffMap));
    return s;
  }

  function bestLeadFrom(bring4, vsBring4, effMap, vsEffMap) {
    let best = { score: -999, p1: null, p2: null };
    combinations(bring4, 2).forEach(([p1, p2]) => {
      const s = leadPairScore(p1, p2, vsBring4, effMap, vsEffMap);
      if (s > best.score) best = { score: s, p1, p2 };
    });
    best.back = bring4.filter(s => s !== best.p1 && s !== best.p2);
    return best;
  }

  function buildBattlePlan(myTeam, oppTeam, myEff, oppEff) {
    const oppCombos = computeBringCombos(oppTeam, myTeam, oppEff, myEff);
    const myCombos = computeBringCombos(myTeam, oppTeam, myEff, oppEff);
    if (!oppCombos.ranked.length || !myCombos.ranked.length) return null;

    const oppBrings = oppCombos.ranked.map(r => r.combo.map(m => m.slug));
    const totalOppWeight = oppCombos.ranked.reduce((s, r) => s + r.total, 0) || 1;

    const matchupScore = (myBring4, oppBring4) =>
      bestLeadFrom(myBring4, oppBring4, myEff, oppEff).score -
      bestLeadFrom(oppBring4, myBring4, oppEff, myEff).score;

    // Blend lead-matchup expectation with the combo's own bring quality —
    // r.total carries the mega-exclusivity devaluation (a second stone holder
    // is valued as its base form), which the matchup solve alone can't see.
    const myScored = myCombos.ranked.map(r => {
      const myBring = r.combo.map(m => m.slug);
      const expected = oppCombos.ranked.reduce((s, or_, i) =>
        s + (or_.total / totalOppWeight) * matchupScore(myBring, oppBrings[i]), 0);
      const wxBonus = myBring.reduce((s, slug) =>
        s + weatherCounterBonus(slug, myEff[slug], oppTeam, oppEff), 0);
      return { bring: myBring, score: expected + wxBonus + 2.5 * r.total };
    }).sort((a, b) => b.score - a.score);

    const myBestBring = myScored[0].bring;
    const predOppBring = oppBrings[0];
    const myLead = bestLeadFrom(myBestBring, predOppBring, myEff, oppEff);

    const oppLeadPairs = combinations(predOppBring, 2)
      .map(([p1, p2]) => ({ p1, p2, score: leadPairScore(p1, p2, myBestBring, oppEff, myEff) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);

    // My pair's strength minus their pair's threat back at me — a one-sided
    // score can't tell counters apart.
    const counterLeadScore = (m1, m2, oppP1, oppP2, set1, set2) =>
      leadPairScore(m1, m2, [oppP1, oppP2], myEff, oppEff) -
      leadPairScore(oppP1, oppP2, [m1, m2], oppEff, myEff, set1, set2);

    function bestCounterFor(p1, p2, set1, set2) {
      let best = { score: -999, p1: null, p2: null };
      combinations(myBestBring, 2).forEach(([m1, m2]) => {
        const s = counterLeadScore(m1, m2, p1, p2, set1, set2);
        if (s > best.score) best = { score: s, p1: m1, p2: m2 };
      });
      return best;
    }

    // Expand predicted lead pairs by real archetype set variants, surfacing a
    // separate row only when the variant changes my best counter.
    const setVariants = slug => {
      const eff = oppEff[slug];
      return (eff && eff.sets.length) ? eff.sets : [null];
    };
    const counterLeads = oppLeadPairs.flatMap(({ p1, p2 }) => {
      const v1 = setVariants(p1), v2 = setVariants(p2);
      const baseline = bestCounterFor(p1, p2, v1[0], v2[0]);
      const setTag = (set, slug) => (set && setVariants(slug).length > 1)
        ? ` [${set.pct}% set: ${set.moves.map(m => m.replace(/-/g,' ')).join('/')}]`
        : '';
      const rows = [{
        oppP1: p1, oppP2: p2, myP1: baseline.p1, myP2: baseline.p2,
        back: myBestBring.filter(s => s !== baseline.p1 && s !== baseline.p2),
        oppTag1: '', oppTag2: '',
      }];
      [...v1.slice(1).map(v => [v, v2[0]]),
       ...v2.slice(1).map(v => [v1[0], v])].forEach(([s1, s2]) => {
        const alt = bestCounterFor(p1, p2, s1, s2);
        if (alt.p1 === baseline.p1 && alt.p2 === baseline.p2) return;
        rows.push({
          oppP1: p1, oppP2: p2, myP1: alt.p1, myP2: alt.p2,
          back: myBestBring.filter(s => s !== alt.p1 && s !== alt.p2),
          oppTag1: setTag(s1, p1), oppTag2: setTag(s2, p2),
        });
      });
      return rows;
    });

    return { myBestBring, predOppBring, myLead, oppLeadPairs, counterLeads, myScored, oppCombos };
  }

  // ── Full analysis entry point ───────────────────────────────────────────────
  function analyze(myTeamInput, oppTeamInput) {
    const my = analyzeSide(myTeamInput);
    const opp = analyzeSide(oppTeamInput);

    // If the opponent entry is incomplete but the DB knows the archetype,
    // fold the predicted mon into the analysis (marked as predicted).
    let oppTeam = [...oppTeamInput];
    let predicted = null;
    if (oppTeamInput.length < 6 && opp.match.predictedSixth.length) {
      predicted = opp.match.predictedSixth[0];
      if (PROFILES[predicted.slug] && !oppTeam.includes(predicted.slug)) {
        oppTeam = [...oppTeam, predicted.slug];
        const e = effProfileFor(predicted.slug, opp.match.partial ? [] : opp.match.matches);
        if (e) { e.predicted = predicted.pct; opp.eff[predicted.slug] = e; }
      }
    }

    const myTeam = [...myTeamInput];
    const oppBring = computeBringCombos(oppTeam, myTeam, opp.eff, my.eff);
    const plan = (myTeam.length === 6 && oppTeam.length === 6)
      ? buildBattlePlan(myTeam, oppTeam, my.eff, opp.eff)
      : null;

    return { my, opp, myTeam, oppTeam, predicted, oppBring, plan };
  }

  return {
    analyze, analyzeSide, matchTeam, effProfileFor, maxStabEff, bestCoverage,
    effMoves, roleP, computeBringScore, computeLeadScore, computeBringCombos,
    synergyLabel, synergyBonus, weatherCounterBonus, weatherBackThreats,
    bestLeadFrom, buildBattlePlan, combinations, monWeather,
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { createPreviewLogic };
} else {
  window.createPreviewLogic = createPreviewLogic;
}
