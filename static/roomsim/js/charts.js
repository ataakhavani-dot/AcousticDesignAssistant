/*
 * Minimal SVG chart helpers: grouped bars, a band line, and a frequency-stem
 * plot, each with hover/focus tooltips and a shared singleton tooltip element.
 * Colors are read from CSS custom properties at build time, so rebuilding a
 * chart after a theme change restyles it.
 */
(function (global) {
  'use strict';

  var SVGNS = 'http://www.w3.org/2000/svg';

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }
  function theme() {
    return {
      ink: cssVar('--text-primary'), ink2: cssVar('--text-secondary'),
      muted: cssVar('--text-muted'), grid: cssVar('--gridline'),
      axis: cssVar('--axis'), surface: cssVar('--surface-1'),
      s1: cssVar('--series-1'), s2: cssVar('--series-2'), s3: cssVar('--series-3')
    };
  }

  function el(name, attrs, parent) {
    var node = document.createElementNS(SVGNS, name);
    for (var k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function html(tag, cls, parent) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (parent) parent.appendChild(node);
    return node;
  }

  // ---- shared tooltip -------------------------------------------------------
  var tip = null;
  function ensureTip() {
    if (!tip) { tip = html('div', 'viz-tip'); tip.hidden = true; document.body.appendChild(tip); }
    return tip;
  }
  // rows: [{label, value, color?}] — built with textContent only.
  function showTip(clientX, clientY, title, rows) {
    var t = ensureTip();
    t.replaceChildren();
    var h = html('div', 'viz-tip-title', t);
    h.textContent = title;
    rows.forEach(function (r) {
      var row = html('div', 'viz-tip-row', t);
      if (r.color) {
        var key = html('span', 'viz-tip-key', row);
        key.style.background = r.color;
      }
      var val = html('span', 'viz-tip-val', row);
      val.textContent = r.value;
      var lab = html('span', 'viz-tip-label', row);
      lab.textContent = r.label;
    });
    t.hidden = false;
    var pad = 14;
    var w = t.offsetWidth, hgt = t.offsetHeight;
    var x = clientX + pad, y = clientY + pad;
    if (x + w > window.innerWidth - 8) x = clientX - w - pad;
    if (y + hgt > window.innerHeight - 8) y = clientY - hgt - pad;
    t.style.left = x + 'px';
    t.style.top = y + 'px';
  }
  function hideTip() { if (tip) tip.hidden = true; }

  function tipAtRect(node, title, rows) {
    var r = node.getBoundingClientRect();
    showTip(r.left + r.width / 2, r.top, title, rows);
  }

  // ---- scales ---------------------------------------------------------------
  function niceTicks(max, count) {
    var steps = [0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100];
    var raw = max / (count || 4);
    var step = steps[steps.length - 1];
    for (var i = 0; i < steps.length; i++) {
      if (steps[i] >= raw) { step = steps[i]; break; }
    }
    var ticks = [];
    for (var v = 0; v <= max + step * 0.999; v += step) ticks.push(+v.toFixed(4));
    return ticks;
  }

  function legend(container, entries, mark) {
    container.replaceChildren();
    entries.forEach(function (e) {
      var item = html('span', 'legend-item', container);
      var key = html('span', mark === 'line' ? 'legend-line' : 'legend-swatch', item);
      key.style.background = e.color;
      var lab = html('span', 'legend-label', item);
      lab.textContent = e.name;
    });
  }

  // ---- grouped bar chart ----------------------------------------------------
  // cfg: { labels, series: [{name, color, values}], unit, fmt }
  function groupedBars(container, cfg) {
    var th = theme();
    var Wt = 560, Ht = 240, mL = 40, mR = 12, mT = 20, mB = 26;
    var plotW = Wt - mL - mR, plotH = Ht - mT - mB;
    container.replaceChildren();
    var svg = el('svg', { viewBox: '0 0 ' + Wt + ' ' + Ht, role: 'img' }, null);
    svg.classList.add('chart-svg');
    container.appendChild(svg);

    var maxV = 0;
    cfg.series.forEach(function (s) {
      s.values.forEach(function (v) { if (isFinite(v) && v > maxV) maxV = v; });
    });
    if (maxV <= 0) maxV = 1;
    var ticks = niceTicks(maxV * 1.08, 4);
    var yMax = ticks[ticks.length - 1];
    var y = function (v) { return mT + plotH - (v / yMax) * plotH; };

    ticks.forEach(function (tv) {
      el('line', { x1: mL, x2: Wt - mR, y1: y(tv), y2: y(tv), stroke: tv === 0 ? th.axis : th.grid, 'stroke-width': 1 }, svg);
      var t = el('text', { x: mL - 6, y: y(tv) + 3, 'text-anchor': 'end', 'font-size': 10, fill: th.muted }, svg);
      t.textContent = cfg.fmt ? cfg.fmt(tv) : tv;
      t.classList.add('tick-text');
    });
    if (cfg.unit) {
      var u = el('text', { x: mL - 32, y: 11, 'font-size': 10, fill: th.muted }, svg);
      u.textContent = cfg.unit;
    }

    var n = cfg.labels.length, k = cfg.series.length;
    var slot = plotW / n;
    var barW = Math.min(22, (slot * 0.62 - 2 * (k - 1)) / k);
    var groupW = barW * k + 2 * (k - 1);

    cfg.labels.forEach(function (lab, i) {
      var cx = mL + slot * i + slot / 2;
      var lt = el('text', { x: cx, y: Ht - 8, 'text-anchor': 'middle', 'font-size': 10, fill: th.muted }, svg);
      lt.textContent = lab;

      cfg.series.forEach(function (s, j) {
        var v = s.values[i];
        if (!isFinite(v) || v <= 0) return;
        var bx = cx - groupW / 2 + j * (barW + 2);
        var by = y(v), bh = mT + plotH - by;
        var rr = Math.min(4, barW / 2, bh); // rounded data-end, square baseline
        el('path', {
          d: 'M' + bx + ',' + (mT + plotH) + ' V' + (by + rr) +
             ' Q' + bx + ',' + by + ' ' + (bx + rr) + ',' + by +
             ' H' + (bx + barW - rr) +
             ' Q' + (bx + barW) + ',' + by + ' ' + (bx + barW) + ',' + (by + rr) +
             ' V' + (mT + plotH) + ' Z',
          fill: s.color
        }, svg);
      });

      // one hit target per band group; tooltip lists every series
      var hit = el('rect', {
        x: mL + slot * i, y: mT, width: slot, height: plotH,
        fill: 'transparent', tabindex: 0
      }, svg);
      var aria = lab + ': ' + cfg.series.map(function (s) {
        return s.name + ' ' + (cfg.fmt ? cfg.fmt(s.values[i]) : s.values[i]) + (cfg.unit ? ' ' + cfg.unit : '');
      }).join(', ');
      hit.setAttribute('aria-label', aria);
      var rows = function () {
        return cfg.series.map(function (s) {
          return { label: s.name, color: s.color, value: (cfg.fmt ? cfg.fmt(s.values[i]) : s.values[i]) + (cfg.unit ? ' ' + cfg.unit : '') };
        });
      };
      hit.addEventListener('pointermove', function (ev) { showTip(ev.clientX, ev.clientY, lab, rows()); });
      hit.addEventListener('pointerleave', hideTip);
      hit.addEventListener('focus', function () { tipAtRect(hit, lab, rows()); });
      hit.addEventListener('blur', hideTip);
    });
  }

  // ---- single-series line over bands ---------------------------------------
  // cfg: { labels, values, color, unit, fmt }
  function bandLine(container, cfg) {
    var th = theme();
    var Wt = 560, Ht = 220, mL = 42, mR = 16, mT = 18, mB = 26;
    var plotW = Wt - mL - mR, plotH = Ht - mT - mB;
    container.replaceChildren();
    var svg = el('svg', { viewBox: '0 0 ' + Wt + ' ' + Ht, role: 'img' }, null);
    svg.classList.add('chart-svg');
    container.appendChild(svg);

    var vals = cfg.values.filter(function (v) { return isFinite(v); });
    if (!vals.length) return;
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    var pad = Math.max((hi - lo) * 0.25, 2);
    lo = Math.floor((lo - pad) / 5) * 5;
    hi = Math.ceil((hi + pad) / 5) * 5;
    var y = function (v) { return mT + plotH - ((v - lo) / (hi - lo)) * plotH; };
    var x = function (i) { return mL + (plotW / (cfg.labels.length - 1)) * i; };

    for (var tv = lo; tv <= hi; tv += 5) {
      el('line', { x1: mL, x2: Wt - mR, y1: y(tv), y2: y(tv), stroke: th.grid, 'stroke-width': 1 }, svg);
      var t = el('text', { x: mL - 6, y: y(tv) + 3, 'text-anchor': 'end', 'font-size': 10, fill: th.muted }, svg);
      t.textContent = tv;
      t.classList.add('tick-text');
    }
    if (cfg.unit) {
      var u = el('text', { x: mL - 34, y: 11, 'font-size': 10, fill: th.muted }, svg);
      u.textContent = cfg.unit;
    }
    cfg.labels.forEach(function (lab, i) {
      var lt = el('text', { x: x(i), y: Ht - 8, 'text-anchor': 'middle', 'font-size': 10, fill: th.muted }, svg);
      lt.textContent = lab;
    });

    var d = cfg.values.map(function (v, i) { return (i ? 'L' : 'M') + x(i) + ',' + y(v); }).join(' ');
    el('path', { d: d, fill: 'none', stroke: cfg.color, 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, svg);
    cfg.values.forEach(function (v, i) {
      el('circle', { cx: x(i), cy: y(v), r: 4, fill: cfg.color, stroke: th.surface, 'stroke-width': 2 }, svg);
    });

    var cross = el('line', { y1: mT, y2: mT + plotH, stroke: th.axis, 'stroke-width': 1, opacity: 0 }, svg);
    var overlay = el('rect', { x: mL, y: mT, width: plotW, height: plotH, fill: 'transparent', tabindex: 0 }, svg);
    overlay.setAttribute('aria-label', cfg.labels.map(function (lab, i) {
      return lab + ' ' + (cfg.fmt ? cfg.fmt(cfg.values[i]) : cfg.values[i]) + ' ' + cfg.unit;
    }).join(', '));
    function snap(clientX) {
      var rect = svg.getBoundingClientRect();
      var sx = (clientX - rect.left) * (Wt / rect.width);
      var i = Math.round((sx - mL) / (plotW / (cfg.labels.length - 1)));
      return Math.max(0, Math.min(cfg.labels.length - 1, i));
    }
    overlay.addEventListener('pointermove', function (ev) {
      var i = snap(ev.clientX);
      cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i));
      cross.setAttribute('opacity', 1);
      showTip(ev.clientX, ev.clientY, cfg.labels[i],
        [{ label: cfg.seriesName || '', color: cfg.color, value: (cfg.fmt ? cfg.fmt(cfg.values[i]) : cfg.values[i]) + ' ' + cfg.unit }]);
    });
    overlay.addEventListener('pointerleave', function () { cross.setAttribute('opacity', 0); hideTip(); });
    overlay.addEventListener('focus', function () { tipAtRect(overlay, 'SPL per band', [{ label: '', value: 'hover for values', color: cfg.color }]); });
    overlay.addEventListener('blur', hideTip);
  }

  // ---- frequency stems (room modes) ----------------------------------------
  // cfg: { modes: [{f,nx,ny,nz,type}], fMax, colors: {axial,tangential,oblique}, marker: {f,label} }
  function stems(container, cfg) {
    var th = theme();
    var Wt = 560, Ht = 190, mL = 14, mR = 14, mT = 26, mB = 26;
    var plotW = Wt - mL - mR, plotH = Ht - mT - mB;
    container.replaceChildren();
    var svg = el('svg', { viewBox: '0 0 ' + Wt + ' ' + Ht, role: 'img' }, null);
    svg.classList.add('chart-svg');
    container.appendChild(svg);

    var x = function (f) { return mL + (f / cfg.fMax) * plotW; };
    var base = mT + plotH;
    el('line', { x1: mL, x2: Wt - mR, y1: base, y2: base, stroke: th.axis, 'stroke-width': 1 }, svg);
    var tickStep = cfg.fMax > 200 ? 50 : 25;
    for (var f = 0; f <= cfg.fMax; f += tickStep) {
      var t = el('text', { x: x(f), y: Ht - 8, 'text-anchor': 'middle', 'font-size': 10, fill: th.muted }, svg);
      t.textContent = f + (f === 0 ? ' Hz' : '');
      t.classList.add('tick-text');
    }

    // Stem height doubles as a secondary (non-colour) encoding: ADA's modes are
    // all axial, so order n carries the emphasis — n=1 is tallest.
    var hFor = [plotH, plotH * 0.78, plotH * 0.6, plotH * 0.44];
    cfg.modes.forEach(function (m) {
      el('line', {
        x1: x(m.f), x2: x(m.f), y1: base, y2: base - (hFor[m.n - 1] || plotH * 0.44),
        stroke: m.color, 'stroke-width': m.n === 1 ? 2 : 1.5,
        'stroke-linecap': 'round'
      }, svg);
    });

    if (cfg.marker && cfg.marker.f <= cfg.fMax) {
      el('line', { x1: x(cfg.marker.f), x2: x(cfg.marker.f), y1: mT - 12, y2: base, stroke: th.muted, 'stroke-width': 1 }, svg);
      var ml = el('text', { x: Math.min(x(cfg.marker.f) + 4, Wt - 90), y: mT - 4, 'font-size': 10, fill: th.muted }, svg);
      ml.textContent = cfg.marker.label;
    }

    var cross = el('line', { y1: mT, y2: base, stroke: th.axis, 'stroke-width': 1, opacity: 0 }, svg);
    var overlay = el('rect', { x: mL, y: mT - 12, width: plotW, height: plotH + 12, fill: 'transparent', tabindex: 0 }, svg);
    overlay.setAttribute('aria-label', cfg.modes.length + ' modes below ' + Math.round(cfg.fMax) + ' Hz; table below lists the first of them');
    overlay.addEventListener('pointermove', function (ev) {
      if (!cfg.modes.length) return;
      var rect = svg.getBoundingClientRect();
      var fx = ((ev.clientX - rect.left) * (Wt / rect.width) - mL) / plotW * cfg.fMax;
      var nearest = cfg.modes[0];
      cfg.modes.forEach(function (m) { if (Math.abs(m.f - fx) < Math.abs(nearest.f - fx)) nearest = m; });
      var close = cfg.modes.filter(function (m) { return Math.abs(m.f - nearest.f) < 0.75; }).slice(0, 4);
      cross.setAttribute('x1', x(nearest.f)); cross.setAttribute('x2', x(nearest.f));
      cross.setAttribute('opacity', 1);
      showTip(ev.clientX, ev.clientY, nearest.f.toFixed(1) + ' Hz',
        close.map(function (m) {
          return { label: m.axis, color: m.color, value: 'n = ' + m.n };
        }));
    });
    overlay.addEventListener('pointerleave', function () { cross.setAttribute('opacity', 0); hideTip(); });
    overlay.addEventListener('blur', hideTip);
  }

  // ---- table builder --------------------------------------------------------
  function fillTable(tableEl, columns, rows) {
    tableEl.replaceChildren();
    var thead = html('thead', null, tableEl);
    var tr = html('tr', null, thead);
    columns.forEach(function (c) { html('th', null, tr).textContent = c; });
    var tbody = html('tbody', null, tableEl);
    rows.forEach(function (r) {
      var trr = html('tr', null, tbody);
      r.forEach(function (cell) { html('td', null, trr).textContent = cell; });
    });
  }

  global.Charts = {
    theme: theme, cssVar: cssVar, legend: legend,
    groupedBars: groupedBars, bandLine: bandLine, stems: stems,
    fillTable: fillTable, showTip: showTip, hideTip: hideTip
  };
})(window);
