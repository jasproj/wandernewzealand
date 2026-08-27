// s53-wnz-schema-gate: measures the JSON-LD offer-emission population against
// this repo's own app.js, before and after the 3-state unit gate, and derives
// the per-row unit state from this pool's own vocabulary (vocab.json).
// usage: node gate-harness.mjs <before-app.js> <after-app.js> <tours-data.json> <outDir>
import fs from 'fs';
import path from 'path';
import vm from 'vm';

const [, , beforePath, afterPath, dataPath, outDir] = process.argv;
const vocab = JSON.parse(fs.readFileSync(new URL('./vocab.json', import.meta.url), 'utf8'));
const RE = {
  multiCount: new RegExp(vocab.multiCount.source, 'i'),
  group: new RegExp(vocab.group.source, 'i'),
  person: new RegExp(vocab.person.source, 'i'),
  equipment: new RegExp(vocab.equipment.source, 'i'),
};

function classify(label) {
  const l = label || '';
  if (RE.multiCount.test(l)) return 'non-per-person';
  if (RE.group.test(l)) return 'non-per-person';
  if (RE.person.test(l)) return 'per-person';
  if (RE.equipment.test(l)) return 'non-per-person';
  return 'unknown';
}

function loadSchemaFns(appPath) {
  const src = fs.readFileSync(appPath, 'utf8');
  const noop = () => {};
  const el = { addEventListener: noop, querySelector: () => null, querySelectorAll: () => [], classList: { add: noop, remove: noop }, getElementById: () => null, style: {} };
  const ctx = { console: { log: noop, error: noop, warn: noop }, document: { ...el, body: el }, window: { addEventListener: noop, scrollY: 0, gtag: noop }, sessionStorage: { getItem: () => null, setItem: noop }, localStorage: { getItem: () => null, setItem: noop }, fetch: () => new Promise(() => {}), gtag: noop, setTimeout, URL, Number, JSON, Math, String, Array, Object };
  vm.createContext(ctx);
  vm.runInContext(src + '\n;globalThis.__x={createTourCard,generateTourSchema};', ctx);
  return ctx.__x;
}

const d = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const before = loadSchemaFns(beforePath);
const after = loadSchemaFns(afterPath);

// same loader predicate as app.js loadTours()
const loaded = d.tours.filter(t => t.status !== 'inactive' && !t.bookingDead);
const CURRENCY_KNOWN = new Set(['NZD', 'USD']);
const emits = t => Number.isFinite(t.price) && t.priceConfidence !== 'low' && CURRENCY_KNOWN.has(t.currency);

const rows = loaded.filter(emits).map(t => {
  const unitState = classify(t.priceLabel);
  const unitText = (t._unknownFields && typeof t._unknownFields.priceUnit === 'string' && t._unknownFields.priceUnit.trim()) || '';
  const beforeSchema = before.generateTourSchema(t);
  const afterSchema = after.generateTourSchema(t);
  return { id: t.id, pk: t.pk, name: t.name, priceLabel: t.priceLabel, price: t.price, currency: t.currency,
    priceConfidence: t.priceConfidence, unitState, unitText, beforeOffers: beforeSchema.offers ?? null, afterOffers: afterSchema.offers ?? null };
});

fs.mkdirSync(outDir, { recursive: true });

// price-label census: every distinct label in the emitting population, its
// count, dollar face value, and derived state.
const byLabel = new Map();
for (const r of rows) {
  const k = r.priceLabel;
  if (!byLabel.has(k)) byLabel.set(k, { priceLabel: k, unitState: r.unitState, count: 0, dollars: 0 });
  const e = byLabel.get(k);
  e.count += 1;
  e.dollars += r.price;
}
const priceLabelCensus = [...byLabel.values()].sort((a, b) => b.count - a.count);
fs.writeFileSync(path.join(outDir, 'price-labels-census.json'), JSON.stringify(priceLabelCensus, null, 2));

// state census: counts / dollars / how many carry a mirrorable card unit
const byState = new Map();
for (const r of rows) {
  if (!byState.has(r.unitState)) byState.set(r.unitState, { state: r.unitState, count: 0, dollars: 0, withMirrorableUnit: 0 });
  const e = byState.get(r.unitState);
  e.count += 1;
  e.dollars += r.price;
  if (r.unitText) e.withMirrorableUnit += 1;
}
const stateCensus = [...byState.values()].sort((a, b) => b.count - a.count);
const partitionTotal = stateCensus.reduce((s, e) => s + e.count, 0);
fs.writeFileSync(path.join(outDir, 'state-census.json'), JSON.stringify({
  renderEligibleRows: loaded.length,
  emittingPopulation: rows.length,
  partitionTotal,
  partitionExact: partitionTotal === rows.length,
  states: stateCensus,
}, null, 2));

// before/after diff summary
const kindOf = o => !o ? 'none' : (o.priceSpecification ? 'priceSpecification' : 'bareOffer');
const diff = {
  before: { bareOffer: rows.filter(r => kindOf(r.beforeOffers) === 'bareOffer').length, none: rows.filter(r => kindOf(r.beforeOffers) === 'none').length },
  after: {
    bareOffer: rows.filter(r => kindOf(r.afterOffers) === 'bareOffer').length,
    priceSpecification: rows.filter(r => kindOf(r.afterOffers) === 'priceSpecification').length,
    none: rows.filter(r => kindOf(r.afterOffers) === 'none').length,
  },
  perPersonByteIdentical: rows.filter(r => r.unitState === 'per-person')
    .every(r => JSON.stringify(r.beforeOffers) === JSON.stringify(r.afterOffers)),
  nonPerPersonNeverBareAfter: rows.filter(r => r.unitState === 'non-per-person')
    .every(r => kindOf(r.afterOffers) !== 'bareOffer'),
  unknownNeverEmitsAfter: rows.filter(r => r.unitState === 'unknown')
    .every(r => kindOf(r.afterOffers) === 'none'),
};
fs.writeFileSync(path.join(outDir, 'gate-diff.json'), JSON.stringify(diff, null, 2));

// fixtures: one row per state proving the required behavior
const fixturePerPerson = rows.find(r => r.unitState === 'per-person');
const fixtureNonPerPersonMirrored = rows.find(r => r.unitState === 'non-per-person' && r.unitText);
const fixtureNonPerPersonSilent = rows.find(r => r.unitState === 'non-per-person' && !r.unitText);
const fixtureUnknown = rows.find(r => r.unitState === 'unknown');
fs.writeFileSync(path.join(outDir, 'fixtures.json'), JSON.stringify({
  perPersonByteIdentical: fixturePerPerson,
  nonPerPersonMirroredUnit: fixtureNonPerPersonMirrored,
  nonPerPersonSilentNoMirror: fixtureNonPerPersonSilent,
  noEvidenceSilent: fixtureUnknown,
}, null, 2));

console.log(JSON.stringify({ renderEligibleRows: loaded.length, emittingPopulation: rows.length, partitionExact: partitionTotal === rows.length, states: stateCensus, diff }, null, 2));
