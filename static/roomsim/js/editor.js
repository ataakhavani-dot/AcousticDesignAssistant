/*
 * Floor-plan editor: draws the polygon room top-down (north up), renders the
 * SPL heat map, and handles two modes:
 *  - normal: drag sources/listener, drag corner handles to reshape, click a
 *    wall to jump to its material row
 *  - draw:   click to place corners (0.05 m grid snap + right-angle snap),
 *    click the first corner / double-click / Enter to close, Backspace to
 *    undo a corner, Esc to cancel
 * Pure view + pointer handling — all numbers come from the app via render().
 */
(function (global) {
  'use strict';

  var canvas, wrap, tipEl, ctx;
  var cbs = {};        // onChange, onWallClick(i), samplePoint(x,y),
                       // onPolygonComplete(pts), onDrawStateChange(bool), onVertexCommit()
  var view = null;     // last render payload from the app
  var drag = null;     // { kind: 'source'|'listener'|'vertex', index }
  var hoverWall = null, hoverVertex = null;

  var mode = 'normal'; // 'normal' | 'draw'
  var draft = [];      // corners placed so far (room metres)
  var cursorPt = null; // snapped cursor position while drawing
  // drawing field bounds in metres; pushing the cursor against an edge grows
  // that edge (throttled), so arbitrarily large rooms can be sketched
  var field = { minX: 0, minY: 0, maxX: 12, maxY: 8 };
  var lastGrow = 0;

  var MARGIN = 36;
  var GRID_SNAP = 0.05, AXIS_SNAP = 0.15, ALIGN_SNAP = 0.08;

  function G() { return global.Acoustics.geom; }
  function pts() { return view.state.room.points; }

  // ---- coordinate mapping ---------------------------------------------------
  function metrics() {
    var bb = mode === 'draw'
      ? { minX: field.minX, minY: field.minY, maxX: field.maxX, maxY: field.maxY,
          w: field.maxX - field.minX, h: field.maxY - field.minY }
      : G().bbox(pts());
    var w = canvas.clientWidth, h = canvas.clientHeight;
    var s = Math.min((w - 2 * MARGIN) / bb.w, (h - 2 * MARGIN) / bb.h);
    return {
      s: s, bb: bb, w: w, h: h,
      ox: (w - bb.w * s) / 2 - bb.minX * s,
      oyTop: (h - bb.h * s) / 2
    };
  }
  function toPx(m, x, y) {
    return { x: m.ox + x * m.s, y: m.oyTop + (m.bb.maxY - y) * m.s };
  }
  function toRoom(m, px, py) {
    return { x: (px - m.ox) / m.s, y: m.bb.maxY - (py - m.oyTop) / m.s };
  }

  // ---- rendering ------------------------------------------------------------
  function isFullscreen() {
    var fe = document.fullscreenElement || document.webkitFullscreenElement;
    return !!(fe && fe.contains(wrap)) || !!(wrap.closest && wrap.closest('.fs-overlay'));
  }

  function sizeCanvas() {
    var dpr = window.devicePixelRatio || 1;
    var cw = wrap.clientWidth, ch;
    if (isFullscreen()) {
      canvas.style.height = '100%';
      ch = wrap.clientHeight;
    } else {
      ch = Math.max(300, Math.min(440, Math.round(cw * 0.62)));
      canvas.style.height = ch + 'px';
    }
    if (canvas.width !== Math.round(cw * dpr) || canvas.height !== Math.round(ch * dpr)) {
      canvas.width = Math.round(cw * dpr);
      canvas.height = Math.round(ch * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function tracePolygon(m, poly) {
    ctx.beginPath();
    poly.forEach(function (p, i) {
      var q = toPx(m, p.x, p.y);
      if (i === 0) ctx.moveTo(q.x, q.y); else ctx.lineTo(q.x, q.y);
    });
    ctx.closePath();
  }

  function drawGrid(m, th, x0, y0, x1, y1) {
    ctx.strokeStyle = th.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (var gx = Math.ceil(x0); gx <= Math.floor(x1); gx++) {
      var a = toPx(m, gx, y0), b = toPx(m, gx, y1);
      ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
    }
    for (var gy = Math.ceil(y0); gy <= Math.floor(y1); gy++) {
      var c = toPx(m, x0, gy), d = toPx(m, x1, gy);
      ctx.moveTo(c.x, c.y); ctx.lineTo(d.x, d.y);
    }
    ctx.stroke();
  }

  function label(text, x, y, color, font, align) {
    ctx.fillStyle = color;
    ctx.font = font || '11px system-ui, sans-serif';
    ctx.textAlign = align || 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
    ctx.textBaseline = 'alphabetic';
  }

  function render(v) {
    if (v) view = v;
    if (!view) return;
    sizeCanvas();
    if (mode === 'draw') renderDraw(); else renderNormal();
  }

  function renderNormal() {
    var th = Charts.theme();
    var m = metrics();
    var poly = pts();
    var v = view;

    // See the note in view3d.js drawScene: the backing store is only reset on
    // resize, so clear explicitly rather than relying on an opaque fill.
    ctx.clearRect(0, 0, m.w, m.h);
    ctx.fillStyle = Charts.cssVar('--page-plane');
    ctx.fillRect(0, 0, m.w, m.h);

    tracePolygon(m, poly);
    ctx.fillStyle = th.surface;
    ctx.fill();

    if (v.heat && v.heat.grid && isFinite(v.heat.grid.min)) {
      var g = v.heat.grid, bb = g.bb;
      ctx.save();
      tracePolygon(m, poly);
      ctx.clip();
      var cw = bb.w / g.nx, ch = bb.h / g.ny;
      for (var j = 0; j < g.ny; j++) {
        for (var i = 0; i < g.nx; i++) {
          var val = g.values[j * g.nx + i];
          if (isNaN(val)) continue;
          var t = g.max > g.min ? (val - g.min) / (g.max - g.min) : 0.5;
          var p = toPx(m, bb.minX + i * cw, bb.minY + (j + 1) * ch);
          ctx.fillStyle = v.heat.ramp(t);
          ctx.fillRect(p.x - 0.5, p.y - 0.5, cw * m.s + 1, ch * m.s + 1);
        }
      }
      ctx.restore();
    } else {
      ctx.save();
      tracePolygon(m, poly);
      ctx.clip();
      drawGrid(m, th, m.bb.minX, m.bb.minY, m.bb.maxX, m.bb.maxY);
      ctx.restore();
    }

    // walls — each a clickable material surface, numbered to match the panel
    var eds = G().edges(poly);
    eds.forEach(function (e, i) {
      var a = toPx(m, e.a.x, e.a.y), b = toPx(m, e.b.x, e.b.y);
      var active = v.selectedWall === i || hoverWall === i;
      ctx.strokeStyle = active ? th.s1 : th.axis;
      ctx.lineWidth = active ? 7 : 5;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    });
    eds.forEach(function (e, i) {
      var mp = toPx(m, e.mid.x, e.mid.y);
      label(String(i + 1), mp.x + e.nx * 14, mp.y - e.ny * 14, th.muted, '10px system-ui, sans-serif');
      var showLen = hoverWall === i || v.selectedWall === i ||
        (drag && drag.kind === 'vertex' &&
          (drag.index === i || (drag.index === (i + 1) % poly.length)));
      if (showLen) {
        label(e.len.toFixed(2) + ' m', mp.x + e.nx * 30, mp.y - e.ny * 30, th.ink2,
          'bold 11px system-ui, sans-serif');
      }
    });

    // corner handles (drag to reshape)
    poly.forEach(function (p, i) {
      var q = toPx(m, p.x, p.y);
      ctx.fillStyle = (hoverVertex === i || (drag && drag.kind === 'vertex' && drag.index === i))
        ? th.s1 : th.surface;
      ctx.strokeStyle = th.ink2;
      ctx.lineWidth = 1.5;
      ctx.fillRect(q.x - 4, q.y - 4, 8, 8);
      ctx.strokeRect(q.x - 4, q.y - 4, 8, 8);
    });

    // compass + bounding dimensions
    label('N ↑', m.w - 24, 16, th.muted);
    label(m.bb.w.toFixed(1) + ' m', m.ox + m.bb.minX * m.s + m.bb.w * m.s / 2,
      m.oyTop + m.bb.h * m.s + 18, th.muted);
    ctx.save();
    ctx.translate(m.ox + m.bb.minX * m.s - 14, m.oyTop + m.bb.h * m.s / 2);
    ctx.rotate(-Math.PI / 2);
    label(m.bb.h.toFixed(1) + ' m', 0, 0, th.muted);
    ctx.restore();

    // expanding wave fronts from each source; radii are real metres
    if (v.waves && v.waves.rings.length) {
      ctx.save();
      tracePolygon(m, poly);
      ctx.clip();
      v.state.sources.forEach(function (src) {
        var c = toPx(m, src.x, src.y);
        v.waves.rings.forEach(function (ring, ri) {
          ctx.beginPath();
          ctx.arc(c.x, c.y, ring.r * m.s, 0, Math.PI * 2);
          ctx.strokeStyle = th.s3;
          ctx.globalAlpha = ring.a;
          ctx.lineWidth = ri === v.waves.rings.length - 1 ? 2 : 1.25; // newest front emphasized
          ctx.stroke();
        });
        ctx.globalAlpha = 1;
        v.waves.rings.forEach(function (ring) {
          if (ring.r * m.s < 26) return;
          var lp = toPx(m, src.x + ring.r * 0.7071, src.y + ring.r * 0.7071);
          label(ring.r.toFixed(1) + ' m', lp.x, lp.y, th.ink2, '10px system-ui, sans-serif');
        });
      });
      ctx.restore();
      label('sound slowed ×' + v.waves.slow, m.w - 12, m.h - 10, th.muted,
        '10px system-ui, sans-serif', 'right');
    }

    // sources: orange dots with a surface ring and index label
    v.state.sources.forEach(function (src, i) {
      var p = toPx(m, src.x, src.y);
      ctx.beginPath();
      ctx.arc(p.x, p.y, 10, 0, Math.PI * 2);
      ctx.fillStyle = th.s2;
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = th.surface;
      ctx.stroke();
      label(String(i + 1), p.x, p.y + 0.5, '#ffffff', 'bold 10px system-ui, sans-serif');
    });

    // listener: ink target with surface ring
    var lp = toPx(m, v.state.listener.x, v.state.listener.y);
    ctx.beginPath();
    ctx.arc(lp.x, lp.y, 9, 0, Math.PI * 2);
    ctx.fillStyle = th.surface;
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = th.ink;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(lp.x, lp.y, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = th.ink;
    ctx.fill();
    label('L', lp.x, lp.y - 15, th.ink2, 'bold 10px system-ui, sans-serif');
  }

  function renderDraw() {
    var th = Charts.theme();
    var m = metrics();

    ctx.clearRect(0, 0, m.w, m.h);
    ctx.fillStyle = Charts.cssVar('--page-plane');
    ctx.fillRect(0, 0, m.w, m.h);
    drawGrid(m, th, field.minX, field.minY, field.maxX, field.maxY);

    label('Click to place corners · push past an edge to grow the field · click the first corner to close · ⌫ undo · Esc cancel',
      12, 14, th.muted, '11px system-ui, sans-serif', 'left');
    label('N ↑', m.w - 24, 16, th.muted);

    if (draft.length) {
      ctx.strokeStyle = th.s1;
      ctx.lineWidth = 2;
      ctx.lineJoin = 'round';
      ctx.beginPath();
      draft.forEach(function (p, i) {
        var q = toPx(m, p.x, p.y);
        if (i === 0) ctx.moveTo(q.x, q.y); else ctx.lineTo(q.x, q.y);
      });
      if (cursorPt) {
        var c = toPx(m, cursorPt.x, cursorPt.y);
        ctx.lineTo(c.x, c.y);
      }
      ctx.stroke();

      draft.forEach(function (p) {
        var q = toPx(m, p.x, p.y);
        ctx.beginPath();
        ctx.arc(q.x, q.y, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = th.s1;
        ctx.fill();
      });

      // close indicator on the first corner
      if (draft.length >= 3 && cursorPt) {
        var f = toPx(m, draft[0].x, draft[0].y);
        var c2 = toPx(m, cursorPt.x, cursorPt.y);
        if (Math.hypot(f.x - c2.x, f.y - c2.y) <= 12) {
          ctx.beginPath();
          ctx.arc(f.x, f.y, 8, 0, Math.PI * 2);
          ctx.strokeStyle = th.s1;
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      }

      // live length of the segment being drawn
      if (cursorPt) {
        var last = draft[draft.length - 1];
        var len = Math.hypot(cursorPt.x - last.x, cursorPt.y - last.y);
        if (len > 0.01) {
          var cp = toPx(m, cursorPt.x, cursorPt.y);
          label(len.toFixed(2) + ' m', cp.x + 18, cp.y - 14, th.ink2, 'bold 11px system-ui, sans-serif', 'left');
        }
      }
    }
  }

  // ---- draw mode ------------------------------------------------------------
  // Cursor near/past a field edge pushes that edge out by 1 m (throttled), so
  // the field is effectively endless. Negative coordinates are fine: the app
  // normalizes the finished polygon back to the origin.
  function growField(p) {
    var now = Date.now();
    if (now - lastGrow < 100) return;
    var grew = false;
    if (p.x > field.maxX - 1) { field.maxX += 1; grew = true; }
    if (p.x < field.minX + 1) { field.minX -= 1; grew = true; }
    if (p.y > field.maxY - 1) { field.maxY += 1; grew = true; }
    if (p.y < field.minY + 1) { field.minY -= 1; grew = true; }
    if (grew) lastGrow = now;
  }
  function snapDraw(p) {
    growField(p);
    var x = Math.round(p.x / GRID_SNAP) * GRID_SNAP;
    var y = Math.round(p.y / GRID_SNAP) * GRID_SNAP;
    if (draft.length) { // right-angle snap relative to the previous corner
      var last = draft[draft.length - 1];
      if (Math.abs(x - last.x) < AXIS_SNAP) x = last.x;
      if (Math.abs(y - last.y) < AXIS_SNAP) y = last.y;
    }
    return {
      x: Math.max(field.minX, Math.min(field.maxX, x)),
      y: Math.max(field.minY, Math.min(field.maxY, y))
    };
  }
  function segmentAllowed(p) {
    if (!draft.length) return true;
    var last = draft[draft.length - 1];
    if (Math.hypot(p.x - last.x, p.y - last.y) < 0.01) return false;
    for (var i = 0; i < draft.length - 2; i++) { // skip the edge sharing `last`
      if (G().segsCross(last, p, draft[i], draft[i + 1])) return false;
    }
    return true;
  }
  function finishDraw() {
    if (draft.length < 3) return;
    var last = draft[draft.length - 1], first = draft[0];
    for (var i = 1; i < draft.length - 2; i++) { // closing edge vs interior edges
      if (G().segsCross(last, first, draft[i], draft[i + 1])) return;
    }
    if (G().area(draft) < 1) return;
    var result = G().ensureCCW(draft);
    draft = [];
    cursorPt = null;
    setMode('normal');
    if (cbs.onPolygonComplete) cbs.onPolygonComplete(result);
  }
  function onKeyDown(ev) {
    if (mode !== 'draw') return;
    if (ev.key === 'Escape') { cancelDraw(); }
    else if (ev.key === 'Backspace') {
      ev.preventDefault();
      draft.pop();
      render();
    } else if (ev.key === 'Enter') { finishDraw(); render(); }
  }
  function setMode(next) {
    if (mode === next) return;
    mode = next;
    if (next === 'draw') window.addEventListener('keydown', onKeyDown);
    else window.removeEventListener('keydown', onKeyDown);
    if (cbs.onDrawStateChange) cbs.onDrawStateChange(next === 'draw');
  }
  function startDraw() {
    var bb = G().bbox(pts());
    field = {
      minX: 0, minY: 0,
      maxX: Math.max(12, Math.ceil(bb.w + 4)),
      maxY: Math.max(8, Math.ceil(bb.h + 4))
    };
    draft = [];
    cursorPt = null;
    hideCanvasTip();
    setMode('draw');
    render();
  }
  function cancelDraw() {
    draft = [];
    cursorPt = null;
    setMode('normal');
    render();
  }
  function isDrawing() { return mode === 'draw'; }

  // ---- hit testing ----------------------------------------------------------
  function hitMarker(p, m) {
    for (var i = view.state.sources.length - 1; i >= 0; i--) {
      var sp = toPx(m, view.state.sources[i].x, view.state.sources[i].y);
      if (Math.hypot(p.x - sp.x, p.y - sp.y) <= 14) return { kind: 'source', index: i };
    }
    var lp = toPx(m, view.state.listener.x, view.state.listener.y);
    if (Math.hypot(p.x - lp.x, p.y - lp.y) <= 14) return { kind: 'listener' };
    return null;
  }
  function hitVertex(p, m) {
    var poly = pts();
    for (var i = 0; i < poly.length; i++) {
      var q = toPx(m, poly[i].x, poly[i].y);
      if (Math.hypot(p.x - q.x, p.y - q.y) <= 9) return i;
    }
    return null;
  }
  function distToSeg(p, a, b) {
    var dx = b.x - a.x, dy = b.y - a.y;
    var t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1e-9);
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p.x - (a.x + t * dx), p.y - (a.y + t * dy));
  }
  function hitWall(p, m) {
    var best = null, bestD = 8;
    G().edges(pts()).forEach(function (e, i) {
      var a = toPx(m, e.a.x, e.a.y), b = toPx(m, e.b.x, e.b.y);
      var d = distToSeg(p, a, b);
      if (d < bestD) { bestD = d; best = i; }
    });
    return best;
  }
  function localPoint(ev) {
    var r = canvas.getBoundingClientRect();
    return { x: ev.clientX - r.left, y: ev.clientY - r.top };
  }

  // ---- pointer handling -----------------------------------------------------
  function onPointerDown(ev) {
    if (!view) return;
    var p = localPoint(ev);
    var m = metrics();

    if (mode === 'draw') {
      var rp = snapDraw(toRoom(m, p.x, p.y));
      if (draft.length >= 3) {
        var f = toPx(m, draft[0].x, draft[0].y);
        if (Math.hypot(f.x - p.x, f.y - p.y) <= 12) { finishDraw(); render(); return; }
      }
      if (segmentAllowed(rp)) draft.push(rp);
      render();
      return;
    }

    var marker = hitMarker(p, m);
    if (marker) {
      drag = marker;
    } else {
      var vi = hitVertex(p, m);
      if (vi !== null) {
        drag = { kind: 'vertex', index: vi };
      } else {
        var wall = hitWall(p, m);
        if (wall !== null && cbs.onWallClick) cbs.onWallClick(wall);
        return;
      }
    }
    canvas.setPointerCapture(ev.pointerId);
    canvas.style.cursor = 'grabbing';
  }

  function onPointerMove(ev) {
    if (!view) return;
    var p = localPoint(ev);
    var m = metrics();

    if (mode === 'draw') {
      cursorPt = snapDraw(toRoom(m, p.x, p.y));
      render();
      return;
    }

    if (drag) {
      var rp = toRoom(m, p.x, p.y);
      if (drag.kind === 'vertex') {
        moveVertex(drag.index, rp);
      } else {
        var x = Math.round(rp.x / GRID_SNAP) * GRID_SNAP;
        var y = Math.round(rp.y / GRID_SNAP) * GRID_SNAP;
        if (G().pointIn(pts(), x, y)) {
          var target = drag.kind === 'source' ? view.state.sources[drag.index] : view.state.listener;
          target.x = x;
          target.y = y;
        }
      }
      hideCanvasTip();
      if (cbs.onChange) cbs.onChange();
      return;
    }

    var marker = hitMarker(p, m);
    var vi = marker ? null : hitVertex(p, m);
    var wall = (marker || vi !== null) ? null : hitWall(p, m);
    if (wall !== hoverWall || vi !== hoverVertex) {
      hoverWall = wall;
      hoverVertex = vi;
      render();
    }
    canvas.style.cursor = marker ? 'grab' : vi !== null ? 'move' : wall !== null ? 'pointer' : 'crosshair';

    var rp2 = toRoom(m, p.x, p.y);
    if (!marker && vi === null && wall === null &&
        G().pointIn(pts(), rp2.x, rp2.y) && cbs.samplePoint) {
      var rows = cbs.samplePoint(rp2.x, rp2.y);
      if (rows) { showCanvasTip(p, rows); return; }
    }
    hideCanvasTip();
  }

  function moveVertex(i, rp) {
    var poly = pts();
    var x = Math.round(rp.x / GRID_SNAP) * GRID_SNAP;
    var y = Math.round(rp.y / GRID_SNAP) * GRID_SNAP;
    var prev = poly[(i - 1 + poly.length) % poly.length];
    var next = poly[(i + 1) % poly.length];
    if (Math.abs(x - prev.x) < ALIGN_SNAP) x = prev.x;
    else if (Math.abs(x - next.x) < ALIGN_SNAP) x = next.x;
    if (Math.abs(y - prev.y) < ALIGN_SNAP) y = prev.y;
    else if (Math.abs(y - next.y) < ALIGN_SNAP) y = next.y;

    var candidate = poly.map(function (p, k) { return k === i ? { x: x, y: y } : p; });
    if (G().selfIntersects(candidate) || G().area(candidate) < 0.5) return;
    poly[i].x = x;
    poly[i].y = y;
  }

  function onPointerUp(ev) {
    if (drag) {
      var wasVertex = drag.kind === 'vertex';
      drag = null;
      canvas.style.cursor = 'crosshair';
      try { canvas.releasePointerCapture(ev.pointerId); } catch (e) { /* already released */ }
      if (wasVertex && cbs.onVertexCommit) cbs.onVertexCommit();
    }
  }
  function onPointerLeave() {
    if (hoverWall !== null || hoverVertex !== null) {
      hoverWall = null;
      hoverVertex = null;
      render();
    }
    hideCanvasTip();
  }
  function onDblClick() {
    if (mode === 'draw') { finishDraw(); render(); }
  }

  function showCanvasTip(p, lines) {
    tipEl.replaceChildren();
    lines.forEach(function (line) {
      var d = document.createElement('div');
      d.textContent = line;
      tipEl.appendChild(d);
    });
    tipEl.hidden = false;
    var x = p.x + 14, y = p.y + 14;
    if (x + tipEl.offsetWidth > wrap.clientWidth - 4) x = p.x - tipEl.offsetWidth - 10;
    if (y + tipEl.offsetHeight > canvas.clientHeight - 4) y = p.y - tipEl.offsetHeight - 10;
    tipEl.style.left = x + 'px';
    tipEl.style.top = y + 'px';
  }
  function hideCanvasTip() { tipEl.hidden = true; }

  function init(canvasEl, wrapEl, tipElement, callbacks) {
    canvas = canvasEl; wrap = wrapEl; tipEl = tipElement; cbs = callbacks;
    ctx = canvas.getContext('2d');
    canvas.addEventListener('pointerdown', onPointerDown);
    canvas.addEventListener('pointermove', onPointerMove);
    canvas.addEventListener('pointerup', onPointerUp);
    canvas.addEventListener('pointercancel', onPointerUp);
    canvas.addEventListener('pointerleave', onPointerLeave);
    canvas.addEventListener('dblclick', onDblClick);
    new ResizeObserver(function () { render(); }).observe(wrap);
  }

  global.Editor = {
    init: init, render: render,
    startDraw: startDraw, cancelDraw: cancelDraw, isDrawing: isDrawing
  };
})(window);
