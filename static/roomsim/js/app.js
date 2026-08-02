/*
 * App glue: state, control panels, results rendering, theme watching, and
 * session persistence. The engine (js/engine.js) does all the math, using
 * ADA's formulas — see the provenance note at the top of that file.
 *
 * Room state: { H, points: [{x,y}…] } — a CCW polygon floor plan with its
 * bounding box anchored at the origin. surfaces.walls[i] is the material of
 * the wall from points[i] to points[i+1].
 */
(function () {
  'use strict';

  var A = window.Acoustics;
  var SHORT_BANDS = ['125', '250', '500', '1k', '2k', '4k'];
  var DEFAULT_WALL = 'drywall';

  // Sequential blue ramp (light steps 100→700). On a dark surface the ramp is
  // reversed so "quiet" recedes into the surface and "loud" reads bright.
  var RAMP = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7',
              '#3987e5', '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b'];

  function boxPoints(w, d) {
    return [{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: d }, { x: 0, y: d }];
  }

  function defaultState() {
    return {
      room: { H: 2.7, points: boxPoints(6.0, 4.2) },
      surfaces: {
        floor: 'wood_floor', ceiling: 'drywall',
        // wall i runs points[i] → points[i+1]; for a box: S, E, N, W
        walls: [DEFAULT_WALL, 'glass', DEFAULT_WALL, DEFAULT_WALL]
      },
      sources: [{ x: 1.2, y: 2.1, z: 1.4, Lw: 92, Q: 2 }],
      listener: { x: 4.3, y: 2.1, z: 1.2 }
    };
  }

  // Assigned once the persistence helpers below have initialised SEED.
  var state = null;
  var results = null;
  var heatGrid = null;
  var selectedWall = null;  // wall index, or null
  var lastStaticKey = null; // room+surfaces signature: skip static rebuilds on drags
  var els = {};
  var viewMode = 'plan';    // 'plan' | '3d'

  var HINT_PLAN = 'Drag the numbered sources, the listener (L), and the corner ' +
    'handles. Click a wall to jump to its material. Hover anywhere in the room ' +
    'for the level at that spot. Use “Draw room outline” to sketch any shape — ' +
    'push past the field edge while drawing to grow it, and go full screen for ' +
    'big rooms.';
  var HINT_3D = 'Drag empty space to orbit and scroll to zoom; double-click ' +
    'resets the view. Drag a source or the listener to move it — hold Shift ' +
    'while dragging to set its height. The heat map floats at listener height; ' +
    'click a wall for its material.';

  // ---- helpers --------------------------------------------------------------
  function $(id) { return document.getElementById(id); }
  function fmt(n, d) { return isFinite(n) ? n.toFixed(d) : '—'; }
  function isDark() {
    var t = document.documentElement.dataset.theme;
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function ramp(t) {
    var steps = isDark() ? RAMP.slice().reverse() : RAMP;
    t = Math.max(0, Math.min(1, t));
    var pos = t * (steps.length - 1);
    var i = Math.min(steps.length - 2, Math.floor(pos));
    var f = pos - i;
    function hex(c) { return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)]; }
    var a = hex(steps[i]), b = hex(steps[i + 1]);
    return 'rgb(' + Math.round(a[0] + (b[0] - a[0]) * f) + ',' +
      Math.round(a[1] + (b[1] - a[1]) * f) + ',' + Math.round(a[2] + (b[2] - a[2]) * f) + ')';
  }
  function matKey(k) { return A.MATERIALS[k] ? k : DEFAULT_WALL; }
  function compassOf(edge) {
    return Math.abs(edge.nx) > Math.abs(edge.ny)
      ? (edge.nx > 0 ? 'E' : 'W') : (edge.ny > 0 ? 'N' : 'S');
  }

  // ---- state persistence ----------------------------------------------------
  // The standalone simulator kept state in location.hash so a room was
  // shareable by URL. Embedded in Streamlit this document is `about:srcdoc`,
  // so there is no address bar to write to and history.replaceState would edit
  // the *host page's* history entry. We use sessionStorage instead — the
  // component iframe is served with allow-same-origin, so it is available, and
  // state then survives the iframe remount that every Streamlit rerun causes.
  var STORE_KEY = 'ada-roomsim-state';

  // ADA's Room Geometry sliders seed the room. `__ADA_SEED__` is injected by
  // room_simulator.py and carries {L, W, H} plus a signature of those values.
  // If the signature changed since the last save the sliders were moved, so we
  // re-seed from them; otherwise we restore whatever the user drew in here.
  var SEED = window.__ADA_SEED__ || null;

  function validate(s) {
    if (!s || !s.room || !isFinite(s.room.H) || !Array.isArray(s.room.points) ||
        s.room.points.length < 3 ||
        !s.room.points.every(function (p) { return p && isFinite(p.x) && isFinite(p.y); }) ||
        !s.surfaces || !Array.isArray(s.sources) || !s.listener) return null;
    s.surfaces.floor = matKey(s.surfaces.floor);
    s.surfaces.ceiling = matKey(s.surfaces.ceiling);
    var walls = Array.isArray(s.surfaces.walls) ? s.surfaces.walls : [];
    s.surfaces.walls = s.room.points.map(function (_, i) { return matKey(walls[i]); });
    return s;
  }

  function loadSaved() {
    try {
      var raw = sessionStorage.getItem(STORE_KEY);
      if (!raw) return null;
      var saved = JSON.parse(raw);
      // Sliders moved since this was stored → ADA's geometry wins.
      if (SEED && saved.seed !== SEED.sig) return null;
      return validate(saved.state);
    } catch (e) { return null; }
  }

  function seededState() {
    if (!SEED) return null;
    var s = defaultState();
    s.room = { H: SEED.H, points: boxPoints(SEED.L, SEED.W) };
    s.surfaces.walls = [DEFAULT_WALL, DEFAULT_WALL, DEFAULT_WALL, DEFAULT_WALL];
    // Put the source and listener somewhere sensible for the seeded box.
    s.sources = [{ x: SEED.L * 0.25, y: SEED.W * 0.5, z: 1.4, Lw: 92, Q: 2 }];
    s.listener = { x: SEED.L * 0.7, y: SEED.W * 0.5, z: 1.2 };
    return s;
  }

  var saveTimer = null;
  function saveState() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
      try {
        sessionStorage.setItem(STORE_KEY, JSON.stringify({
          seed: SEED ? SEED.sig : null, state: state
        }));
      } catch (e) { /* private mode / storage disabled: skip */ }
    }, 400);
  }

  // Restored edits win only while the sliders haven't moved; then the seed does.
  state = loadSaved() || seededState() || defaultState();

  // ---- room shape operations ------------------------------------------------
  function clampPositions() {
    var c = A.geom.centroid(state.room.points);
    function clampPt(p) {
      if (!A.geom.pointIn(state.room.points, p.x, p.y)) {
        p.x = Math.round(c.x * 20) / 20;
        p.y = Math.round(c.y * 20) / 20;
      }
      p.z = Math.max(0.1, Math.min(state.room.H - 0.1, p.z));
    }
    state.sources.forEach(clampPt);
    clampPt(state.listener);
  }

  // shift the plan so its bounding box sits at the origin, moving markers along
  function normalizeRoom() {
    var bb = A.geom.bbox(state.room.points);
    if (Math.abs(bb.minX) < 1e-9 && Math.abs(bb.minY) < 1e-9) return;
    state.room.points.forEach(function (p) { p.x -= bb.minX; p.y -= bb.minY; });
    state.sources.concat([state.listener]).forEach(function (p) {
      p.x -= bb.minX; p.y -= bb.minY;
    });
  }

  function setBoxRoom(w, d) {
    state.room.points = boxPoints(w, d);
    if (state.surfaces.walls.length !== 4) {
      state.surfaces.walls = [DEFAULT_WALL, DEFAULT_WALL, DEFAULT_WALL, DEFAULT_WALL];
    }
    clampPositions();
    update();
  }

  function applyPolygon(pts) {
    state.room.points = pts.map(function (p) { return { x: p.x, y: p.y }; });
    normalizeRoom();
    var old = state.surfaces.walls;
    state.surfaces.walls = pts.map(function (_, i) {
      return old.length === pts.length ? old[i] : DEFAULT_WALL;
    });
    clampPositions();
    buildSurfacePanel();
    forceUpdate();
  }

  // is the plan an axis-aligned rectangle (so W/D inputs stay live)?
  function axisBox() {
    var rect = A.geom.isRectangle(state.room.points);
    if (!rect) return null;
    var bb = A.geom.bbox(state.room.points);
    if (Math.abs(bb.w * bb.h - A.geom.area(state.room.points)) > 0.01) return null;
    return bb;
  }

  // ---- panels ---------------------------------------------------------------
  function numField(labelText, value, min, max, step, onInput) {
    var wrapEl = document.createElement('label');
    wrapEl.className = 'num-field';
    var span = document.createElement('span');
    span.textContent = labelText;
    var input = document.createElement('input');
    input.type = 'number';
    input.min = min; input.max = max; input.step = step; input.value = value;
    input.addEventListener('input', function () {
      var v = parseFloat(input.value);
      if (isFinite(v)) onInput(Math.max(min, Math.min(max, v)));
    });
    wrapEl.appendChild(span);
    wrapEl.appendChild(input);
    return { el: wrapEl, input: input };
  }

  function buildRoomPanel() {
    var wrapEl = $('roomFields');
    wrapEl.replaceChildren();
    var bb = A.geom.bbox(state.room.points);
    var fw = numField('Width (E–W) m', bb.w.toFixed(2), 1.5, 200, 0.1, function (v) {
      var cur = axisBox();
      if (cur) setBoxRoom(v, cur.h);
    });
    var fd = numField('Depth (N–S) m', bb.h.toFixed(2), 1.5, 200, 0.1, function (v) {
      var cur = axisBox();
      if (cur) setBoxRoom(cur.w, v);
    });
    var fh = numField('Height m', state.room.H, 1.8, 20, 0.05, function (v) {
      state.room.H = v;
      clampPositions();
      update();
    });
    [fw, fd, fh].forEach(function (f) { wrapEl.appendChild(f.el); });
    els.roomW = fw.input;
    els.roomD = fd.input;

    var btnRow = document.createElement('div');
    btnRow.className = 'btn-row';
    var drawBtn = document.createElement('button');
    drawBtn.type = 'button';
    drawBtn.id = 'drawBtn';
    drawBtn.textContent = 'Draw room outline';
    drawBtn.addEventListener('click', function () {
      if (Editor.isDrawing()) { Editor.cancelDraw(); return; }
      setViewMode('plan'); // outline drawing lives in the plan view
      Editor.startDraw();
    });
    btnRow.appendChild(drawBtn);
    wrapEl.appendChild(btnRow);

    var note = document.createElement('p');
    note.className = 'shape-note';
    note.id = 'shapeNote';
    wrapEl.appendChild(note);
    els.drawBtn = drawBtn;
  }

  function renderRoomPanelState() {
    var bb = A.geom.bbox(state.room.points);
    var isBox = !!axisBox();
    function set(input, v) {
      if (document.activeElement !== input) input.value = (+v).toFixed(2);
      input.disabled = !isBox;
    }
    set(els.roomW, bb.w);
    set(els.roomD, bb.h);
    $('shapeNote').textContent = isBox
      ? 'Rectangular plan — edit the sides above, drag corners on the plan, or draw a new outline.'
      : 'Custom plan (' + state.room.points.length + ' corners), floor area ' +
        fmt(A.geom.area(state.room.points), 1) + ' m². Drag corners to adjust, or draw a new outline.';
  }

  function surfaceRow(list, id, labelText, key, getMat, setMat) {
    var row = document.createElement('div');
    row.className = 'field-row';
    var lab = document.createElement('label');
    lab.textContent = labelText;
    lab.setAttribute('for', 'surf-' + id);
    var area = document.createElement('span');
    area.className = 'area-note';
    area.id = 'area-' + id;
    lab.appendChild(area);
    var sel = document.createElement('select');
    sel.id = 'surf-' + id;
    Object.keys(A.MATERIALS).forEach(function (mk) {
      var opt = document.createElement('option');
      opt.value = mk;
      opt.textContent = A.MATERIALS[mk].label;
      sel.appendChild(opt);
    });
    sel.value = getMat();
    sel.addEventListener('change', function () { setMat(sel.value); update(); });
    sel.addEventListener('focus', function () { selectedWall = key; renderCanvas(); });
    sel.addEventListener('blur', function () { selectedWall = null; renderCanvas(); });
    row.appendChild(lab);
    row.appendChild(sel);
    list.appendChild(row);
  }

  function buildSurfacePanel() {
    var list = $('surfaceList');
    list.replaceChildren();
    surfaceRow(list, 'floor', 'Floor', null,
      function () { return state.surfaces.floor; },
      function (v) { state.surfaces.floor = v; });
    surfaceRow(list, 'ceiling', 'Ceiling', null,
      function () { return state.surfaces.ceiling; },
      function (v) { state.surfaces.ceiling = v; });
    var eds = A.geom.edges(state.room.points);
    eds.forEach(function (e, i) {
      surfaceRow(list, 'wall-' + i, 'Wall ' + (i + 1) + ' · ' + compassOf(e), i,
        function () { return state.surfaces.walls[i]; },
        function (v) { state.surfaces.walls[i] = v; });
    });
  }

  function buildSourcePanel() {
    var list = $('sourceList');
    list.replaceChildren();
    els.sourceInputs = [];
    state.sources.forEach(function (src, i) {
      var card = document.createElement('div');
      card.className = 'source-row';
      var head = document.createElement('div');
      head.className = 'source-head';
      var name = document.createElement('strong');
      name.textContent = 'Source ' + (i + 1);
      var del = document.createElement('button');
      del.type = 'button';
      del.className = 'ghost-btn';
      del.textContent = 'Remove';
      del.setAttribute('aria-label', 'Remove source ' + (i + 1));
      del.addEventListener('click', function () {
        state.sources.splice(i, 1);
        buildSourcePanel();
        update();
      });
      head.appendChild(name);
      head.appendChild(del);
      card.appendChild(head);

      var grid = document.createElement('div');
      grid.className = 'field-grid';
      var fx = numField('x m', src.x, 0, 200, 0.1, function (v) { src.x = v; update(); });
      var fy = numField('y m', src.y, 0, 200, 0.1, function (v) { src.y = v; update(); });
      var fz = numField('z m', src.z, 0.1, 20, 0.1, function (v) { src.z = v; update(); });
      var fl = numField('Lw dB', src.Lw, 40, 140, 1, function (v) { src.Lw = v; update(); });
      [fx, fy, fz, fl].forEach(function (f) { grid.appendChild(f.el); });

      var qWrap = document.createElement('label');
      qWrap.className = 'num-field';
      var qs = document.createElement('span');
      qs.textContent = 'Q';
      var qSel = document.createElement('select');
      [[1, '1 · free field'], [2, '2 · near wall'], [4, '4 · wall/floor edge'], [8, '8 · corner']].forEach(function (o) {
        var opt = document.createElement('option');
        opt.value = o[0];
        opt.textContent = o[1];
        qSel.appendChild(opt);
      });
      qSel.value = src.Q;
      qSel.addEventListener('change', function () { src.Q = parseFloat(qSel.value); update(); });
      qWrap.appendChild(qs);
      qWrap.appendChild(qSel);
      grid.appendChild(qWrap);

      card.appendChild(grid);
      list.appendChild(card);
      els.sourceInputs.push({ x: fx.input, y: fy.input, z: fz.input });
    });
  }

  function buildListenerPanel() {
    var wrapEl = $('listenerFields');
    wrapEl.replaceChildren();
    var L = state.listener;
    var fx = numField('x m', L.x, 0, 200, 0.1, function (v) { L.x = v; update(); });
    var fy = numField('y m', L.y, 0, 200, 0.1, function (v) { L.y = v; update(); });
    var fz = numField('z (ear height) m', L.z, 0.1, 20, 0.1, function (v) { L.z = v; update(); });
    [fx, fy, fz].forEach(function (f) { wrapEl.appendChild(f.el); });
    els.listenerInputs = { x: fx.input, y: fy.input, z: fz.input };
  }

  // keep panel inputs in sync after canvas drags (without stealing focus)
  function syncPositionInputs() {
    function set(input, v) {
      if (input && document.activeElement !== input) input.value = v;
    }
    state.sources.forEach(function (src, i) {
      var pair = els.sourceInputs[i];
      if (pair) { set(pair.x, src.x); set(pair.y, src.y); set(pair.z, src.z); }
    });
    set(els.listenerInputs.x, state.listener.x);
    set(els.listenerInputs.y, state.listener.y);
    set(els.listenerInputs.z, state.listener.z);
  }

  // ---- results --------------------------------------------------------------
  function tile(label, value, sub, hero) {
    var t = document.createElement('div');
    t.className = 'tile' + (hero ? ' tile-hero' : '');
    var l = document.createElement('div');
    l.className = 'tile-label';
    l.textContent = label;
    var v = document.createElement('div');
    v.className = 'tile-value';
    v.textContent = value;
    t.appendChild(l);
    t.appendChild(v);
    if (sub) {
      var s = document.createElement('div');
      s.className = 'tile-sub';
      s.textContent = sub;
      t.appendChild(s);
    }
    return t;
  }

  function renderTiles() {
    var box = $('tiles');
    box.replaceChildren();
    var aMid = (results.abs.meanAlpha[2] + results.abs.meanAlpha[3]) / 2;
    box.appendChild(tile('RT60 mid (Sabine, 500 Hz–1 kHz)', fmt(results.tMid, 2) + ' s',
      'target ' + fmt(results.target, 2) + ' s', true));
    box.appendChild(tile('Volume', fmt(results.abs.V, 1) + ' m³', fmt(results.abs.S, 1) + ' m² surface'));
    box.appendChild(results.bolt
      ? tile('Bolt area', results.bolt.status,
          'ratios ' + fmt(results.ratios.x, 2) + ' : ' + fmt(results.ratios.y, 2))
      : tile('Bolt area', '—', 'needs a rectangular plan'));
    box.appendChild(tile('Mean absorption ᾱ (mid)', fmt(aMid, 2),
      'A = ' + fmt((results.abs.A[2] + results.abs.A[3]) / 2, 1) + ' m² Sab'));
  }

  function renderRT() {
    var th = Charts.theme();
    Charts.legend($('rtLegend'), [
      { name: 'Sabine', color: th.s1 }, { name: 'Eyring', color: th.s2 }
    ], 'rect');
    Charts.groupedBars($('rtChart'), {
      labels: SHORT_BANDS,
      unit: 's',
      fmt: function (v) { return (+v).toFixed(2); },
      series: [
        { name: 'Sabine', color: th.s1, values: results.rt.sabine },
        { name: 'Eyring', color: th.s2, values: results.rt.eyring }
      ]
    });
    Charts.fillTable($('rtTable'), ['Band', 'Sabine (s)', 'Eyring (s)'],
      A.BAND_LABELS.map(function (b, i) {
        return [b, fmt(results.rt.sabine[i], 2), fmt(results.rt.eyring[i], 2)];
      }));
  }

  function renderSPL() {
    var th = Charts.theme();
    var sum = $('splSummary');
    if (!state.sources.length) {
      sum.textContent = 'Add a source to compute levels.';
      $('splChart').replaceChildren();
      Charts.fillTable($('splTable'), ['Band', 'SPL (dB)'], []);
      return;
    }
    var crit = state.sources.map(function (s, i) {
      return 'S' + (i + 1) + ' ' + fmt(results.critical[i], 1) + ' m';
    }).join(' · ');
    sum.textContent = 'Overall: ' + fmt(results.splOverall, 1) + ' dB at the listener · Critical distance (1 kHz): ' + crit;

    Charts.bandLine($('splChart'), {
      labels: SHORT_BANDS,
      values: results.splListener,
      color: th.s1,
      seriesName: 'SPL',
      unit: 'dB',
      fmt: function (v) { return (+v).toFixed(1); }
    });
    Charts.fillTable($('splTable'), ['Band', 'SPL (dB)'],
      A.BAND_LABELS.map(function (b, i) {
        return [b, fmt(results.splListener[i], 1)];
      }));
  }

  function renderModes() {
    var th = Charts.theme();
    if (!results.rect) {
      Charts.legend($('modeLegend'), [], 'line');
      $('modeChart').replaceChildren();
      Charts.fillTable($('modeTable'), ['f (Hz)', 'Axis', 'Order n'], []);
      $('modeNote').textContent =
        'Custom (non-rectangular) plan — closed-form mode analysis needs a ' +
        'rectangular room, so no mode list is shown. RT60, SPL and the heat ' +
        'map above remain valid for any shape.';
      return;
    }
    // ADA models axial modes per room axis, one colour each.
    Charts.legend($('modeLegend'), [
      { name: 'Length', color: A.AXIS_COLORS.Length },
      { name: 'Width', color: A.AXIS_COLORS.Width },
      { name: 'Height', color: A.AXIS_COLORS.Height }
    ], 'line');
    Charts.stems($('modeChart'), {
      modes: results.modes,
      fMax: results.modeFMax,
      marker: { f: results.schroeder, label: 'Schroeder ' + fmt(results.schroeder, 0) + ' Hz' }
    });
    $('modeNote').textContent = results.modes.length + ' axial modes below ' +
      fmt(results.modeFMax, 0) + ' Hz (orders 1–4 along each axis, as in the ' +
      'Modal Analysis tab). Taller stems are lower-order and therefore stronger.';
    Charts.fillTable($('modeTable'), ['f (Hz)', 'Axis', 'Order n'],
      results.modes.slice(0, 14).map(function (m) {
        return [fmt(m.f, 1), m.axis, m.n];
      }));
  }

  function renderSurfaceAreas() {
    var areas = results.abs.areas;
    var setNote = function (id, text) {
      var el = $('area-' + id);
      if (el) el.textContent = text;
    };
    setNote('floor', fmt(areas.floor, 1) + ' m²');
    setNote('ceiling', fmt(areas.ceiling, 1) + ' m²');
    A.geom.edges(state.room.points).forEach(function (e, i) {
      setNote('wall-' + i, fmt(e.len, 1) + ' m · ' + fmt(areas.walls[i], 1) + ' m²');
    });
  }

  function renderColorbar() {
    var row = $('colorbarRow');
    var on = $('heatmapOn').checked && heatGrid && isFinite(heatGrid.min);
    row.hidden = !on;
    if (!on) { $('cbBand').textContent = ''; return; }
    var stops = [];
    for (var i = 0; i <= 10; i++) stops.push(ramp(i / 10) + ' ' + i * 10 + '%');
    $('colorbar').style.background = 'linear-gradient(90deg, ' + stops.join(', ') + ')';
    $('cbMin').textContent = fmt(heatGrid.min, 1) + ' dB';
    $('cbMax').textContent = fmt(heatGrid.max, 1) + ' dB';
    $('cbBand').textContent = 'SPL at ' + A.BAND_LABELS[bandIndex()] + ', listener height';
  }

  function bandIndex() { return parseInt($('heatmapBand').value, 10); }

  // ---- wave-front animation --------------------------------------------------
  // Spherical wave fronts expanding from each source at the speed of sound,
  // slowed WAVE_SLOW× so they are visible. Radii are real metres; the emission
  // interval is chosen so about WAVE_COUNT fronts are in flight at once.
  var WAVE_SLOW = 200, WAVE_COUNT = 5;
  var waveStart = null, waveRaf = null;

  function waveRings() {
    var t = (performance.now() - waveStart) / 1000;
    var bb = A.geom.bbox(state.room.points);
    var maxR = Math.hypot(bb.w, bb.h);
    var v = A.C / WAVE_SLOW;
    var interval = maxR / (v * WAVE_COUNT);
    var rings = [];
    var k0 = Math.max(0, Math.ceil((t - maxR / v) / interval));
    for (var k = k0; k < k0 + WAVE_COUNT + 2; k++) {
      var r = (t - k * interval) * v;
      if (r <= 0.02) break;
      if (r < maxR) rings.push({ r: r, a: 0.15 + 0.85 * (1 - r / maxR) });
    }
    return { rings: rings, slow: WAVE_SLOW };
  }

  function waveLoop() {
    if (!$('wavesOn').checked) { waveRaf = null; return; }
    renderCanvas();
    waveRaf = requestAnimationFrame(waveLoop);
  }

  function renderCanvas() {
    var payload = {
      state: state,
      selectedWall: selectedWall,
      heat: ($('heatmapOn').checked && heatGrid) ? { grid: heatGrid, ramp: ramp } : null,
      waves: ($('wavesOn').checked && waveStart !== null && state.sources.length)
        ? waveRings() : null
    };
    if (viewMode === '3d') View3D.render(payload); else Editor.render(payload);
  }

  // ---- plan / 3-D view switching --------------------------------------------
  function setViewMode(m) {
    m = m === '3d' ? '3d' : 'plan';
    if (m === viewMode) return;
    if (m === '3d' && Editor.isDrawing()) Editor.cancelDraw();
    viewMode = m;
    try { localStorage.setItem('ada-roomsim-view', m); } catch (e) { /* private mode */ }
    applyViewMode();
    renderCanvas();
  }
  function applyViewMode() {
    $('canvasWrap').hidden = viewMode === '3d';
    $('canvasWrap3d').hidden = viewMode !== '3d';
    Array.prototype.forEach.call($('viewToggle').querySelectorAll('button'), function (btn) {
      var on = btn.dataset.view === viewMode;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-pressed', String(on));
    });
    $('canvasHint').textContent = viewMode === '3d' ? HINT_3D : HINT_PLAN;
  }

  // ---- full screen -----------------------------------------------------------
  // Native Fullscreen API where allowed; a fixed-position overlay otherwise
  // (e.g. embedded in an iframe without allowfullscreen).
  function fsActive() {
    var card = $('roomCard');
    var fe = document.fullscreenElement || document.webkitFullscreenElement;
    return fe === card || card.classList.contains('fs-overlay');
  }
  function syncFsUI() {
    var on = fsActive();
    var btn = $('fsBtn');
    btn.textContent = on ? '✕ Exit full screen' : '⛶ Full screen';
    btn.setAttribute('aria-pressed', String(on));
    renderCanvas();
  }
  function toggleFullscreen() {
    var card = $('roomCard');
    if (fsActive()) {
      card.classList.remove('fs-overlay');
      var exit = document.exitFullscreen || document.webkitExitFullscreen;
      var fe = document.fullscreenElement || document.webkitFullscreenElement;
      if (fe === card && exit) exit.call(document);
      syncFsUI();
      return;
    }
    var req = card.requestFullscreen || card.webkitRequestFullscreen;
    var usedOverlay = false;
    if (req) {
      try {
        var p = req.call(card);
        if (p && p.catch) {
          p.then(syncFsUI).catch(function () {
            card.classList.add('fs-overlay');
            syncFsUI();
          });
        }
      } catch (e) { usedOverlay = true; }
    } else {
      usedOverlay = true;
    }
    if (usedOverlay) {
      card.classList.add('fs-overlay');
      syncFsUI();
    }
  }

  // ---- main update ----------------------------------------------------------
  function update() {
    results = A.computeAll(state);
    heatGrid = ($('heatmapOn').checked && state.sources.length)
      ? A.heatmap(state.room, state.sources, results.R[bandIndex()], state.listener.z, 48)
      : null;

    var staticKey = JSON.stringify([state.room, state.surfaces]);
    if (staticKey !== lastStaticKey) {
      lastStaticKey = staticKey;
      if ($('surfaceList').querySelectorAll('select').length !== 2 + state.surfaces.walls.length) {
        buildSurfacePanel();
      }
      renderTiles();
      renderRT();
      renderModes();
      renderSurfaceAreas();
      renderRoomPanelState();
    }
    renderSPL();
    renderCanvas();
    renderColorbar();
    syncPositionInputs();
    saveState();
  }
  function forceUpdate() { lastStaticKey = null; update(); }

  var rafPending = false;
  function updateThrottled() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(function () { rafPending = false; update(); });
  }

  // ---- init -----------------------------------------------------------------
  function init() {
    var bandSel = $('heatmapBand');
    A.BAND_LABELS.forEach(function (b, i) {
      var opt = document.createElement('option');
      opt.value = i;
      opt.textContent = b;
      bandSel.appendChild(opt);
    });
    bandSel.value = 3; // 1 kHz
    bandSel.addEventListener('change', update);
    $('heatmapOn').addEventListener('change', update);
    $('wavesOn').addEventListener('change', function () {
      if ($('wavesOn').checked) {
        waveStart = performance.now();
        if (!waveRaf) waveRaf = requestAnimationFrame(waveLoop);
      } else {
        waveStart = null;
        if (waveRaf) { cancelAnimationFrame(waveRaf); waveRaf = null; }
        renderCanvas();
      }
    });
    $('addSource').addEventListener('click', function () {
      var c = A.geom.centroid(state.room.points);
      state.sources.push({
        x: Math.round(c.x * 20) / 20,
        y: Math.round(c.y * 20) / 20,
        z: 1.4, Lw: 90, Q: 2
      });
      buildSourcePanel();
      update();
    });

    function focusWallRow(i) {
      var sel = $('surf-wall-' + i);
      if (!sel) return;
      sel.focus();
      sel.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      var row = sel.parentElement;
      row.classList.remove('flash');
      void row.offsetWidth; // restart the animation
      row.classList.add('flash');
    }
    function samplePoint(x, y) {
      var lines = ['x ' + x.toFixed(2) + ' m · y ' + y.toFixed(2) + ' m'];
      if (state.sources.length && results) {
        var b = bandIndex();
        var lp = A.splAt(x, y, state.listener.z, state.sources, results.R[b]);
        if (lp !== null) lines.push(lp.toFixed(1) + ' dB · ' + A.BAND_LABELS[b]);
      }
      return lines;
    }

    Editor.init($('floorplan'), $('canvasWrap'), $('canvasTip'), {
      onChange: updateThrottled,
      onVertexCommit: function () {
        normalizeRoom();
        clampPositions();
        update();
      },
      onPolygonComplete: applyPolygon,
      onDrawStateChange: function (drawing) {
        els.drawBtn.textContent = drawing ? 'Cancel drawing (Esc)' : 'Draw room outline';
        els.drawBtn.classList.toggle('active-draw', drawing);
      },
      onWallClick: focusWallRow,
      samplePoint: samplePoint
    });

    View3D.init($('room3d'), $('canvasWrap3d'), $('canvasTip3d'), {
      onChange: updateThrottled,
      onWallClick: focusWallRow,
      samplePoint: samplePoint
    });

    Array.prototype.forEach.call($('viewToggle').querySelectorAll('button'), function (btn) {
      btn.addEventListener('click', function () { setViewMode(btn.dataset.view); });
    });
    try {
      if (localStorage.getItem('ada-roomsim-view') === '3d') viewMode = '3d';
    } catch (e) { /* private mode */ }
    applyViewMode();

    $('fsBtn').addEventListener('click', toggleFullscreen);
    document.addEventListener('fullscreenchange', syncFsUI);
    document.addEventListener('webkitfullscreenchange', syncFsUI);
    // Esc leaves the overlay fallback (native fullscreen handles Esc itself);
    // while drawing, Esc cancels the outline first
    window.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && $('roomCard').classList.contains('fs-overlay') &&
          !Editor.isDrawing()) {
        $('roomCard').classList.remove('fs-overlay');
        syncFsUI();
      }
    });

    buildRoomPanel();
    buildSurfacePanel();
    buildSourcePanel();
    buildListenerPanel();

    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', forceUpdate);

    clampPositions();
    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
