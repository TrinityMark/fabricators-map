ACTOR_MAPS = 'nwua9Gu5YrADL7ZDj'

# (label, google_maps_search_query, unique_match_keyword)
# search_query  → sent to Google Maps as the search string
# match_keyword → unique substring used to tag which category a result came from
TRADES = [
    ('Air Conditioning',  'air conditioning',    'air conditioning'),
    ('Auto Electricians', 'auto electrical',     'auto electr'),
    ('Builders',          'builder',             'builder'),
    ('Cabinet Makers',    'cabinet maker',       'cabinet maker'),
    ('Car Mechanics',     'car mechanic',        'car mechanic'),
    ('Carpenters',        'carpenter',           'carpenter'),
    ('Concreters',        'concreter',           'concret'),
    ('Diesel Mechanics',  'diesel mechanic',     'diesel'),
    ('Earthmoving',       'earthmoving',         'earthmov'),
    ('Electricians',      'electrician',         'electrician'),
    ('Fabricators',       'fabricator',          'fabricat'),
    ('Fencing',           'fencing',             'fencing'),
    ('Flooring',          'flooring',            'flooring'),
    ('Glaziers',          'glazier',             'glazier'),
    ('Landscapers',       'landscaper',          'landscap'),
    ('Locksmiths',        'locksmith',           'locksmith'),
    ('Painters',          'painter',             'painter'),
    ('Panel Beaters',     'panel beater',        'panel beat'),
    ('Pest Control',      'pest control',        'pest control'),
    ('Plasterers',        'plasterer',           'plaster'),
    ('Plumbers',          'plumber',             'plumber'),
    ('Roofers',           'roofer',              'roofer'),
    ('Solar',             'solar installer',     'solar'),
    ('Tilers',            'tiler',               'tiler'),
]

# One visually distinct colour per category (same order as TRADES)
COLOURS = [
    '#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6',
    '#1abc9c','#e67e22','#34495e','#e91e63','#00bcd4',
    '#8bc34a','#ff5722','#795548','#ff9800','#673ab7',
    '#607d8b','#009688','#c0392b','#2980b9','#27ae60',
    '#d35400','#16a085','#8e44ad','#2c3e50',
]

import json
TRADES = sorted(TRADES, key=lambda t: t[0])
trades_json  = json.dumps([[t[0], t[1], t[2]] for t in TRADES])
colours_json = json.dumps(COLOURS)

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trades Overview Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display: flex; flex-direction: column; height: 100vh; }

    header {
      background: #1a1a2e; color: #fff;
      padding: 10px 16px;
      display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
      box-shadow: 0 2px 8px rgba(0,0,0,.5); z-index: 1000; flex-shrink: 0;
    }
    header h1 { font-size: 1rem; font-weight: 600; white-space: nowrap; }
    .badge { background: #e94560; color: #fff; border-radius: 12px; padding: 2px 10px; font-size: 0.78rem; font-weight: 700; white-space: nowrap; }
    .controls { margin-left: auto; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .controls label { font-size: 0.75rem; color: #aaa; margin-right: 2px; }
    .ctrl-input { padding: 6px 10px; border: 1px solid #444; border-radius: 6px; background: #2a2a3e; color: #fff; font-size: 0.85rem; width: 180px; }
    .ctrl-input::placeholder { color: #888; }
    .btn { padding: 6px 16px; border: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
    .btn:hover { opacity: 0.85; }
    .btn:disabled { opacity: 0.4; cursor: not-allowed; }
    .btn-go  { background: #e94560; color: #fff; }
    .btn-csv { background: #2ecc71; color: #fff; }
    .btn-key { background: #444; color: #ccc; font-size: 0.75rem; }
    .btn-other { background: #2a2a3e; color: #aaa; font-size: 0.75rem; border: 1px solid #444; }

    /* Category picker */
    .picker-wrap { position: relative; }
    .picker-toggle {
      padding: 6px 10px; border: 1px solid #444; border-radius: 6px;
      background: #2a2a3e; color: #fff; font-size: 0.82rem; cursor: pointer;
      white-space: nowrap; min-width: 160px; text-align: left;
      display: flex; align-items: center; justify-content: space-between; gap: 6px;
    }
    .picker-toggle:hover { border-color: #888; }
    .picker-arrow { font-size: 0.65rem; opacity: 0.7; }
    .picker-dropdown {
      display: none; position: absolute; top: calc(100% + 4px); left: 0;
      background: #fff; border: 1px solid #ddd; border-radius: 8px;
      box-shadow: 0 6px 24px rgba(0,0,0,.2); z-index: 2000;
      width: 220px; max-height: 360px; overflow: hidden;
      flex-direction: column;
    }
    .picker-dropdown.open { display: flex; }
    .picker-top {
      display: flex; gap: 6px; padding: 8px 10px;
      border-bottom: 1px solid #eee; flex-shrink: 0;
    }
    .picker-top button {
      flex: 1; padding: 3px 0; border: 1px solid #ddd; border-radius: 4px;
      background: #f5f5f5; font-size: 0.75rem; cursor: pointer; color: #444;
    }
    .picker-top button:hover { background: #eee; }
    .picker-items { overflow-y: auto; padding: 4px 0; }
    .picker-item {
      display: flex; align-items: center; gap: 8px;
      padding: 6px 12px; cursor: pointer; font-size: 0.82rem; color: #333;
    }
    .picker-item:hover { background: #f5f5f5; }
    .picker-item input[type="checkbox"] { accent-color: #e94560; width: 14px; height: 14px; cursor: pointer; }
    .picker-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

    .main { display: flex; flex: 1; overflow: hidden; }

    /* Sidebar */
    #sidebar {
      width: 260px; flex-shrink: 0;
      display: flex; flex-direction: column;
      background: #fff; border-right: 1px solid #ddd; overflow: hidden;
    }
    #sidebar-header {
      padding: 10px 14px; background: #f0f0f0;
      border-bottom: 1px solid #ddd; flex-shrink: 0;
    }
    #sidebar-title { font-size: 0.82rem; font-weight: 600; color: #333; margin-bottom: 8px; }
    .toggle-row { display: flex; gap: 6px; }
    .toggle-btn {
      flex: 1; padding: 4px 0; border: 1px solid #ccc; border-radius: 4px;
      background: #fff; font-size: 0.75rem; cursor: pointer; color: #555;
    }
    .toggle-btn:hover { background: #f5f5f5; }

    #cat-list { flex: 1; overflow-y: auto; padding: 6px 0; }
    .cat-row {
      display: flex; align-items: center; gap: 8px;
      padding: 7px 14px; cursor: pointer; transition: background 0.1s;
      border-bottom: 1px solid #f5f5f5;
    }
    .cat-row:hover { background: #f8f8f8; }
    .cat-row.muted { opacity: 0.4; }
    .cat-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
    .cat-name { font-size: 0.82rem; color: #333; flex: 1; }
    .cat-count {
      background: #eee; color: #555;
      border-radius: 10px; padding: 1px 7px;
      font-size: 0.72rem; font-weight: 600; white-space: nowrap;
    }
    .cat-count.has-results { background: #e8f0fe; color: #1a73e8; }

    #map { flex: 1; }

    /* Overlay */
    #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 9999; flex-direction: column; align-items: center; justify-content: center; gap: 16px; }
    #overlay.active { display: flex; }
    .spinner { width: 48px; height: 48px; border: 5px solid rgba(255,255,255,0.3); border-top-color: #e94560; border-radius: 50%; animation: spin 0.9s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    #status-msg { color: #fff; font-size: 1rem; font-weight: 500; background: rgba(0,0,0,0.5); padding: 8px 24px; border-radius: 8px; max-width: 380px; text-align: center; }

    /* Key modal */
    #key-modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 10000; align-items: center; justify-content: center; }
    #key-modal.active { display: flex; }
    .key-box { background: #fff; border-radius: 10px; padding: 28px 32px; width: 420px; max-width: 90vw; box-shadow: 0 8px 32px rgba(0,0,0,.4); }
    .key-box h2 { font-size: 1rem; margin-bottom: 8px; color: #1a1a2e; }
    .key-box p  { font-size: 0.82rem; color: #555; margin-bottom: 14px; line-height: 1.5; }
    .key-box input { width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.88rem; margin-bottom: 14px; font-family: monospace; }
    .key-box .row { display: flex; gap: 8px; justify-content: flex-end; }

    /* Popup */
    .popup-name { font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; color: #1a1a2e; }
    .popup-tag { display: inline-flex; align-items: center; gap: 5px; border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; margin-bottom: 6px; color: #fff; }
    .popup-row { font-size: 0.8rem; margin: 3px 0; color: #333; }
    .popup-row a { color: #1a73e8; text-decoration: none; }
    .popup-row a:hover { text-decoration: underline; }
    .popup-rating { display: inline-block; background: #f5a623; color: #fff; border-radius: 4px; padding: 1px 6px; font-size: 0.75rem; font-weight: 700; margin-left: 6px; }
  </style>
</head>
<body>

<div id="key-modal">
  <div class="key-box">
    <h2>Apify API Key</h2>
    <p>Enter your Apify API key. Saved in your browser — only sent to Apify when you run a search.</p>
    <input type="password" id="key-input" placeholder="apify_api_..." />
    <div class="row">
      <button class="btn" style="background:#ddd;color:#333;" onclick="closeKeyModal()">Cancel</button>
      <button class="btn btn-go" onclick="saveKey()">Save</button>
    </div>
  </div>
</div>

<div id="overlay">
  <div class="spinner"></div>
  <div id="status-msg">Starting&hellip;</div>
</div>

<header>
  <h1>Trades Overview Map</h1>
  <a href="index.html" style="color:#aaa;font-size:0.75rem;text-decoration:none;border:1px solid #444;border-radius:6px;padding:4px 10px;white-space:nowrap;">&#8592; Leads Search Map</a>
  <span class="badge" id="count-badge">0 businesses</span>
  <div class="controls">
    <div><label>Suburb</label><input class="ctrl-input" type="text" id="inp-suburb" placeholder="e.g. Brendale" oninput="onStreetOrSuburbChange()" /></div>
    <div><label>Street <span style="color:#888;font-size:0.7rem">(optional)</span></label><input class="ctrl-input" type="text" id="inp-street" placeholder="e.g. Terrence Rd" oninput="onStreetOrSuburbChange()" /></div>
    <div class="picker-wrap" id="picker-wrap">
      <button class="picker-toggle" id="picker-toggle" onclick="togglePicker(event)">
        <span id="picker-label">All categories</span>
        <span class="picker-arrow">&#9660;</span>
      </button>
      <div class="picker-dropdown" id="picker-dropdown">
        <div class="picker-top">
          <button onclick="pickerSelectAll()">Select all</button>
          <button onclick="pickerClearAll()">Clear all</button>
        </div>
        <div class="picker-items" id="picker-items"></div>
      </div>
    </div>
    <button class="btn btn-go" id="btn-go" onclick="runSearch()">Go</button>
<button class="btn btn-csv" id="btn-csv" onclick="saveCSV()" disabled>&#11123; Save CSV</button>
    <button class="btn btn-key" onclick="promptApiKey()">&#9881; API Key</button>
  </div>
</header>

<div class="main">
  <div id="sidebar">
    <div id="sidebar-header">
      <div id="sidebar-title">Trade Categories</div>
      <div class="toggle-row">
        <button class="toggle-btn" onclick="toggleAll(true)">Show All</button>
        <button class="toggle-btn" onclick="toggleAll(false)">Hide All</button>
      </div>
    </div>
    <div id="cat-list"></div>
  </div>
  <div id="map"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const ACTOR_MAPS = '##ACTOR_MAPS##';

const TRADES = ##TRADES_JSON##;
const COLOURS = ##COLOURS_JSON##;

// Map category label → colour
const CAT_COLOUR = {};
TRADES.forEach(([label], i) => { CAT_COLOUR[label] = COLOURS[i % COLOURS.length]; });

// ── Category picker ────────────────────────────────────────
const pickerState = {};  // label → checked bool
TRADES.forEach(([label]) => { pickerState[label] = true; });

function buildPicker() {
  const container = document.getElementById('picker-items');
  TRADES.forEach(([label], i) => {
    const colour = COLOURS[i % COLOURS.length];
    const row = document.createElement('label');
    row.className = 'picker-item';
    row.innerHTML = `
      <input type="checkbox" checked data-cat="${label}" onchange="onPickerChange()" />
      <span class="picker-dot" style="background:${colour}"></span>
      ${label}`;
    container.appendChild(row);
  });
}

function togglePicker(e) {
  e.stopPropagation();
  document.getElementById('picker-dropdown').classList.toggle('open');
}

function closePicker() { document.getElementById('picker-dropdown').classList.remove('open'); }

document.addEventListener('click', e => {
  if (!document.getElementById('picker-wrap').contains(e.target)) closePicker();
});

function onPickerChange() {
  document.querySelectorAll('#picker-items input[type="checkbox"]').forEach(cb => {
    pickerState[cb.dataset.cat] = cb.checked;
  });
  updatePickerLabel();
}

function updatePickerLabel() {
  const total    = TRADES.length;
  const selected = Object.values(pickerState).filter(Boolean).length;
  document.getElementById('picker-label').textContent =
    selected === total ? 'All categories' :
    selected === 0     ? 'None selected' :
    `${selected} of ${total} selected`;
}

function pickerSelectAll() {
  document.querySelectorAll('#picker-items input[type="checkbox"]').forEach(cb => { cb.checked = true; pickerState[cb.dataset.cat] = true; });
  updatePickerLabel();
}

function pickerClearAll() {
  document.querySelectorAll('#picker-items input[type="checkbox"]').forEach(cb => { cb.checked = false; pickerState[cb.dataset.cat] = false; });
  updatePickerLabel();
}

function getSelectedTrades() {
  return TRADES.filter(([label]) => pickerState[label]);
}

function getToken() { return localStorage.getItem('apify_token') || ''; }
function setToken(t) { localStorage.setItem('apify_token', t); }

// ── Map ────────────────────────────────────────────────────
const map = L.map('map').setView([-27.33, 152.99], 12);
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  subdomains: 'abcd', maxZoom: 19,
}).addTo(map);

function makeIcon(color) {
  return L.divIcon({
    className: '',
    html: `<svg width="22" height="30" viewBox="0 0 28 36" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 0C6.268 0 0 6.268 0 14c0 9.333 14 22 14 22S28 23.333 28 14C28 6.268 21.732 0 14 0z"
            fill="${color}" stroke="rgba(0,0,0,0.25)" stroke-width="1.5"/>
      <circle cx="14" cy="14" r="5" fill="rgba(255,255,255,0.85)"/></svg>`,
    iconSize: [22, 30], iconAnchor: [11, 30], popupAnchor: [0, -30],
  });
}

// Precompute icons per category
const ICONS = {};
TRADES.forEach(([label], i) => { ICONS[label] = makeIcon(COLOURS[i % COLOURS.length]); });
const ICON_ACTIVE = makeIcon('#ffffff');

let allPlaces = [];
let markersByCategory = {};   // label → Leaflet marker[]
let categoryVisible = {};     // label → bool
let activeMarker = null;

// ── Utilities ──────────────────────────────────────────────
const sleep = ms => new Promise(r => setTimeout(r, ms));
function showOverlay(msg) { document.getElementById('overlay').classList.add('active'); document.getElementById('status-msg').textContent = msg; }
function setStatus(msg)   { document.getElementById('status-msg').textContent = msg; }
function hideOverlay()    { document.getElementById('overlay').classList.remove('active'); }

async function geocode(suburb) {
  const r = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(suburb + ', Australia')}&format=json&limit=1`, { headers: { 'Accept-Language': 'en' } });
  const d = await r.json();
  if (!d.length) throw new Error('Could not locate: ' + suburb);
  return { lat: parseFloat(d[0].lat), lng: parseFloat(d[0].lon) };
}

// ── Apify helpers ──────────────────────────────────────────
async function apifyRun(input, token) {
  const r = await fetch(`https://api.apify.com/v2/acts/${ACTOR_MAPS}/runs?token=${token}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input),
  });
  if (!r.ok) throw new Error(`Apify start failed (${r.status}): ` + (await r.text()).slice(0,200));
  return (await r.json()).data.id;
}

async function apifyWait(runId, token) {
  while (true) {
    await sleep(6000);
    const d = (await (await fetch(`https://api.apify.com/v2/actor-runs/${runId}?token=${token}`)).json()).data;
    const secs = d.stats?.durationMillis ? Math.round(d.stats.durationMillis / 1000) : '…';
    setStatus(`Searching Google Maps… (${secs}s)`);
    if (d.status === 'SUCCEEDED') return d.defaultDatasetId;
    if (['FAILED','ABORTED','TIMED-OUT'].includes(d.status)) throw new Error('Run ended: ' + d.status);
  }
}

async function apifyDataset(datasetId, token) {
  const r = await fetch(`https://api.apify.com/v2/datasets/${datasetId}/items?token=${token}&format=json&clean=true&limit=1000`);
  if (!r.ok) throw new Error('Dataset fetch failed: ' + r.status);
  return r.json();
}

// ── Main search ────────────────────────────────────────────
async function runSearch() {
  const suburb = document.getElementById('inp-suburb').value.trim();
  const street = document.getElementById('inp-street').value.trim();
  if (!suburb) { alert('Please enter a suburb.'); return; }
  const token  = getToken();
  if (!token) { promptApiKey(); return; }

  document.getElementById('btn-go').disabled = true;

  try {
    const locationLabel = street ? `${street}, ${suburb}` : suburb;
    showOverlay('Locating ' + suburb + '…');
    // Always geocode the suburb — Nominatim can't reliably locate individual streets
    const center = await geocode(suburb);
    map.setView([center.lat, center.lng], street ? 15 : 13);

    let queries, perQuery, places;

    if (street) {
      // ── Street mode: all trades, street included in each query ─
      // Searching "electrician Terrence Road Brendale Australia" finds
      // businesses of that type on/near the street. Run all 24 trades
      // with a small per-trade limit (street is short).
      perQuery = 10;
      queries  = TRADES.map(([, searchQuery]) => `${searchQuery} ${street} ${suburb} Australia`);
      setStatus(`Searching all trades on ${street}…`);
    } else {
      // ── Suburb mode: one query per selected trade ──────────
      const selected = getSelectedTrades();
      if (!selected.length) { alert('Please select at least one trade category.'); hideOverlay(); document.getElementById('btn-go').disabled = false; return; }
      perQuery = Math.min(100, Math.max(20, Math.round(400 / selected.length)));
      queries  = selected.map(([, searchQuery]) => `${searchQuery} ${suburb} Australia`);
      setStatus(`Searching ${selected.length} trade categor${selected.length === 1 ? 'y' : 'ies'} in ${suburb}…`);
    }

    const runId     = await apifyRun({ searchStringsArray: queries, maxCrawledPlacesPerSearch: perQuery, language: 'en', maxImages: 0, scrapeReviews: false }, token);
    const datasetId = await apifyWait(runId, token);

    setStatus('Loading results…');
    const raw   = await apifyDataset(datasetId, token);
    const seen  = new Set();
    places = [];

    for (const p of raw) {
      const name = (p.title || '').trim();
      if (!name || seen.has(name.toLowerCase())) continue;
      seen.add(name.toLowerCase());
      const loc = p.location || {};
      if (!loc.lat || !loc.lng) continue;

      // Match back to our trade label via the search query keyword (both modes)
      const search = (p.searchString || '').toLowerCase();
      let category = 'Other';
      for (const [label, , matchKey] of TRADES) {
        if (search.includes(matchKey.toLowerCase())) { category = label; break; }
      }

      // ownerName is set when the Google Maps listing owner has a profile
      const ownerRaw = p.ownerName || (typeof p.owner === 'object' ? p.owner?.name : p.owner) || '';
      places.push({
        name,
        street:   p.street     || '',
        suburb:   p.city       || '',
        phone:    p.phone      || '',
        website:  p.website    || '',
        rating:   p.totalScore || '',
        owner:    ownerRaw,
        category,
        lat: loc.lat,
        lng: loc.lng,
      });
    }

    // isStreetMode controls sidebar title only; both modes now use TRADES categorisation
    if (street) {
      // Keep only businesses whose street address actually contains the searched street.
      // Strip common road-type suffixes so "Terrence Road" matches "Terrence Rd" etc.
      const streetKey = street.toLowerCase()
        .replace(/\\b(road|rd|street|st|avenue|ave|drive|dr|court|ct|place|pl|lane|ln|way|close|cl|crescent|cres|boulevard|blvd|highway|hwy|parade|pde)\\b/g, '')
        .replace(/\\s+/g, ' ').trim();
      // First meaningful word e.g. "terrence" from "terrence road"
      const keyword = streetKey.split(' ')[0];
      if (keyword) {
        const unfiltered = places;
        places = unfiltered.filter(p => (p.street || '').toLowerCase().includes(keyword));
        if (places.length === 0 && unfiltered.length > 0) {
          alert(`No results had "${street}" in their address.\\nShowing all ${unfiltered.length} nearby results instead.`);
          places = unfiltered;
        }
      }
    }

    renderResults(places, locationLabel, !!street);
    document.getElementById('btn-csv').disabled = places.length === 0;
  } catch (err) {
    alert('Error: ' + err.message);
    console.error(err);
  } finally {
    hideOverlay();
    document.getElementById('btn-go').disabled = false;
  }
}

// Assign a stable colour to any category string (known or freeform)
const _dynamicColours = {};
const _extraPalette = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e','#e91e63','#00bcd4','#8bc34a','#ff5722','#795548','#ff9800','#673ab7','#607d8b','#009688'];
let _colourIdx = 0;
function colourFor(cat) {
  if (CAT_COLOUR[cat]) return CAT_COLOUR[cat];
  if (!_dynamicColours[cat]) _dynamicColours[cat] = _extraPalette[_colourIdx++ % _extraPalette.length];
  return _dynamicColours[cat];
}

// ── Render ─────────────────────────────────────────────────
function renderResults(places, locationLabel, isStreetMode) {
  Object.values(markersByCategory).flat().forEach(m => map.removeLayer(m));
  markersByCategory = {};
  categoryVisible   = {};
  allPlaces         = places;
  activeMarker      = null;

  document.getElementById('count-badge').textContent = places.length + ' businesses';

  // Group by category
  const groups = {};
  places.forEach(p => {
    if (!groups[p.category]) groups[p.category] = [];
    groups[p.category].push(p);
  });

  // Add markers
  places.forEach(p => {
    const colour = colourFor(p.category);
    const icon   = ICONS[p.category] || makeIcon(colour);
    const m = L.marker([p.lat, p.lng], { icon })
      .addTo(map)
      .bindPopup(popupHtml(p), { maxWidth: 280 });
    m.on('click', () => {
      if (activeMarker) {
        const prevCat = activeMarker._tradeCategory;
        activeMarker.setIcon(ICONS[prevCat] || makeIcon(colourFor(prevCat)));
      }
      m.setIcon(makeIcon('#222'));
      activeMarker = m;
      activeMarker._tradeCategory = p.category;
      highlightCatRow(p.category);
    });
    m._tradeCategory = p.category;
    if (!markersByCategory[p.category]) markersByCategory[p.category] = [];
    markersByCategory[p.category].push(m);
    categoryVisible[p.category] = true;
  });

  buildSidebar(groups, locationLabel, isStreetMode);
}

function popupHtml(p) {
  const addr   = [p.street, p.suburb].filter(Boolean).join(', ');
  const colour = colourFor(p.category);
  const rating = p.rating ? `<span class="popup-rating">&#9733; ${p.rating}</span>` : '';
  const phone  = p.phone   ? `<div class="popup-row">&#128222; <a href="tel:${p.phone}">${p.phone}</a></div>` : '';
  const site   = p.website ? `<div class="popup-row">&#127760; <a href="${p.website}" target="_blank" rel="noopener">Visit website</a></div>` : '';
  const owner  = p.owner   ? `<div class="popup-row">&#128100; ${p.owner}</div>` : '';
  return `<div class="popup-name">${p.name} ${rating}</div>
    <div><span class="popup-tag" style="background:${colour}">${p.category}</span></div>
    ${addr ? `<div class="popup-row">&#128205; ${addr}</div>` : ''}
    ${phone}${owner}${site}`;
}

// ── Sidebar ────────────────────────────────────────────────
function buildSidebar(groups, locationLabel, isStreetMode) {
  document.getElementById('sidebar-title').textContent =
    isStreetMode ? `Businesses on ${locationLabel}` : `Trades in ${locationLabel}`;
  const listEl = document.getElementById('cat-list');
  listEl.innerHTML = '';

  // Both modes: show all TRADES categories sorted by count desc (0-count ones at bottom).
  // Street mode shows only businesses whose trade queries matched the street.
  const sorted = TRADES.map(([label]) => ({ label, count: (groups[label] || []).length }))
                       .sort((a, b) => b.count - a.count);

  sorted.forEach(({ label, count }) => {
    const colour = colourFor(label);
    const row    = document.createElement('div');
    row.className = 'cat-row';
    row.dataset.cat = label;
    row.innerHTML = `
      <div class="cat-dot" style="background:${colour}"></div>
      <span class="cat-name">${label}</span>
      <span class="cat-count ${count > 0 ? 'has-results' : ''}">${count}</span>`;
    row.addEventListener('click', () => toggleCategory(label, row));
    listEl.appendChild(row);
  });
}

function toggleCategory(label, row) {
  const isVisible = categoryVisible[label] !== false;
  const nowVisible = !isVisible;
  categoryVisible[label] = nowVisible;
  (markersByCategory[label] || []).forEach(m => {
    if (nowVisible) map.addLayer(m); else map.removeLayer(m);
  });
  row.classList.toggle('muted', !nowVisible);
}

function toggleAll(show) {
  // Work from whatever categories are currently on the map (handles both modes)
  Object.keys(markersByCategory).forEach(label => {
    categoryVisible[label] = show;
    (markersByCategory[label] || []).forEach(m => {
      if (show) map.addLayer(m); else map.removeLayer(m);
    });
  });
  document.querySelectorAll('.cat-row').forEach(r => r.classList.toggle('muted', !show));
}

function highlightCatRow(label) {
  document.querySelectorAll('.cat-row').forEach(r => r.classList.remove('active'));
  const row = document.querySelector(`.cat-row[data-cat="${label}"]`);
  if (row) { row.classList.add('active'); row.scrollIntoView({ block: 'nearest' }); }
}

// ── Save CSV ───────────────────────────────────────────────
// Default values used when a field is missing — keeps CRM bulk-upload happy
const CSV_DEFAULTS = {
  suburb:  'Unknown',
  phone:   '+61 7 0000 0000',
  website: 'https://unknown.com.au',
  rating:  '0',
};

function saveCSV() {
  if (!allPlaces.length) return;
  const cols = ['Business Name','Street Address','Suburb','Phone','Website','Google Rating','Owner / Contact','Trade Category'];
  const rows = [cols.join(',')];
  allPlaces.forEach(p => rows.push([
    csv(p.name),
    csv(p.street),
    csv(p.suburb   || CSV_DEFAULTS.suburb),
    csv(p.phone    || CSV_DEFAULTS.phone),
    csv(p.website  || CSV_DEFAULTS.website),
    p.rating       || CSV_DEFAULTS.rating,
    csv(p.owner    || ''),
    csv(p.category),
  ].join(',')));
  const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob) });
  const suburb = document.getElementById('inp-suburb').value.trim().replace(/\\s+/g, '-').toLowerCase();
  const street = document.getElementById('inp-street').value.trim().replace(/\\s+/g, '-').toLowerCase();
  a.download = street ? `trades-${street}-${suburb}.csv` : `trades-${suburb}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function csv(v) {
  if (!v) return '';
  const s = String(v);
  return (s.includes(',') || s.includes('"') || s.includes('\n')) ? `"${s.replace(/"/g, '""')}"` : s;
}

// ── Street / suburb toggle ─────────────────────────────────
function onStreetOrSuburbChange() {
  const hasStreet = document.getElementById('inp-street').value.trim().length > 0;
  // Hide the trade-category picker when a street is entered (all types returned)
  document.getElementById('picker-wrap').style.display = hasStreet ? 'none' : '';
}

// ── Key modal ──────────────────────────────────────────────
function promptApiKey() {
  document.getElementById('key-input').value = getToken();
  document.getElementById('key-modal').classList.add('active');
  setTimeout(() => document.getElementById('key-input').focus(), 50);
}
function closeKeyModal() { document.getElementById('key-modal').classList.remove('active'); }
function saveKey() {
  const v = document.getElementById('key-input').value.trim();
  if (!v) { alert('Please enter your API key.'); return; }
  setToken(v); closeKeyModal();
}
document.getElementById('key-modal').addEventListener('click', e => { if (e.target === document.getElementById('key-modal')) closeKeyModal(); });
window.addEventListener('load', () => { buildPicker(); if (!getToken()) promptApiKey(); });
</script>
</body>
</html>"""

html = (html
    .replace('##ACTOR_MAPS##',    ACTOR_MAPS)
    .replace('##TRADES_JSON##',   trades_json)
    .replace('##COLOURS_JSON##',  colours_json))

with open('trades-map.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Written trades-map.html ({len(html):,} bytes)')
