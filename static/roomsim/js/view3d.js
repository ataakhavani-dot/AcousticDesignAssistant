/*
 * 3-D room view: the floor plan extruded to height H, drawn in perspective on
 * a plain canvas (no libraries). Walls whose outside faces the camera are
 * hidden so you can see into the room; the SPL heat map is drawn as a
 * translucent sheet at listener height. Drag empty space to orbit, scroll or
 * pinch to zoom, double-click to reset the view. Drag a source or the
 * listener to move it; hold Shift while dragging to set its height. Click a
 * wall (or, for hidden walls, its floor edge) to jump to its material row.
 * Pure view + pointer handling — all numbers come from the app via render().
 */
(function (global) {
  'use strict';

  var canvas, wrap, tipEl, ctx;
  var cbs = {};    // onChange, onWallClick(i), samplePoint(x,y)
  var view = null; // last render payload from the app

  var HOME = { yaw: -0.55, pitch: 0.60, zoom: 1 };
  var cam = { yaw: HOME.yaw, pitch: HOME.pitch, zoom: HOME.zoom };

  var drag = null;    // {kind:'orbit',x,y,moved,wall} | {kind:'source'|'listener',index,vertical}
  var hoverWall = null;
  var pointers = {};  // active pointerId → {x,y}, for pinch zoom
  var pinch = null;   // {dist, zoom}

  function G() { return global.Acoustics.geom; }
  function pts() { return view.state.room.points; }
  function roomH() { return view.state.room.H; }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function snap(v) { return Math.round(v * 20) / 20; }

  // ---- small vector + color helpers ----------------------------------------
  function norm(v) {
    var l = Math.hypot(v.x, v.y, v.z) || 1e-9;
    return { x: v.x / l, y: v.y / l, z: v.z / l };
  }
  function cross(a, b) {
    return { x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x };
  }
  function hex(c) {
    if (c.length === 4) c = '#' + c[1] + c[1] + c[2] + c[2] + c[3] + c[3];
    return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
  }
  function mix(a, b, t) {
    var A = hex(a), B = hex(b);
    if (A.some(isNaN) || B.some(isNaN)) return a;
    return 'rgb(' + Math.round(A[0] + (B[0] - A[0]) * t) + ',' +
      Math.round(A[1] + (B[1] - A[1]) * t) + ',' +
      Math.round(A[2] + (B[2] - A[2]) * t) + ')';
  }

  // ---- camera ---------------------------------------------------------------
  // Orbit camera around the room centre. Returns projection helpers; the
  // focal length is chosen so the room's bounding sphere fits the canvas.
  function makeCamera() {
    var w = canvas.clientWidth, h = canvas.clientHeight;
    var c = G().centroid(pts());
    var bb = G().bbox(pts());
    var Hh = roomH();
    var target = { x: c.x, y: c.y, z: Hh / 2 };
    var radius = Math.hypot(Math.hypot(bb.w, bb.h) / 2, Hh / 2) + 0.6;
    var dist = radius * 2.9;
    var cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
    var eye = {
      x: target.x + dist * cp * Math.sin(cam.yaw),
      y: target.y - dist * cp * Math.cos(cam.yaw),
      z: target.z + dist * sp
    };
    var fwd = norm({ x: target.x - eye.x, y: target.y - eye.y, z: target.z - eye.z });
    var right = norm(cross(fwd, { x: 0, y: 0, z: 1 }));
    var up = cross(right, fwd);
    var f = 0.44 * Math.min(w, h) * (dist / radius) * cam.zoom;

    function project(p) {
      var dx = p.x - eye.x, dy = p.y - eye.y, dz = p.z - eye.z;
      var z = dx * fwd.x + dy * fwd.y + dz * fwd.z;
      return {
        x: w / 2 + f * (dx * right.x + dy * right.y + dz * right.z) / z,
        y: h / 2 - f * (dx * up.x + dy * up.y + dz * up.z) / z,
        z: z
      };
    }
    // world-space ray direction through a canvas point
    function ray(sx, sy) {
      var kx = (sx - w / 2) / f, ky = (h / 2 - sy) / f;
      return norm({
        x: fwd.x + right.x * kx + up.x * ky,
        y: fwd.y + right.y * kx + up.y * ky,
        z: fwd.z + right.z * kx + up.z * ky
      });
    }
    // ray ∩ horizontal plane z = zp (null if behind the camera)
    function onPlane(sx, sy, zp) {
      var d = ray(sx, sy);
      if (Math.abs(d.z) < 1e-9) return null;
      var t = (zp - eye.z) / d.z;
      if (t <= 0) return null;
      return { x: eye.x + d.x * t, y: eye.y + d.y * t, z: zp };
    }
    return { w: w, h: h, f: f, eye: eye, project: project, ray: ray, onPlane: onPlane };
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
      ch = Math.max(320, Math.min(480, Math.round(cw * 0.68)));
      canvas.style.height = ch + 'px';
    }
    if (canvas.width !== Math.round(cw * dpr) || canvas.height !== Math.round(ch * dpr)) {
      canvas.width = Math.round(cw * dpr);
      canvas.height = Math.round(ch * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function trace(scr) {
    ctx.beginPath();
    scr.forEach(function (p, i) {
      if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
  }

  function label(text, x, y, color, font, align) {
    ctx.fillStyle = color;
    ctx.font = font || '11px system-ui, sans-serif';
    ctx.textAlign = align || 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
    ctx.textBaseline = 'alphabetic';
  }

  // Horizontal circle at height zc, drawn only where it lies inside the room.
  function strokeWorldCircle(C, cx, cy, zc, rr) {
    var N = 48;
    ctx.beginPath();
    var pen = false;
    for (var i = 0; i <= N; i++) {
      var ang = (i / N) * Math.PI * 2;
      var wx = cx + rr * Math.cos(ang), wy = cy + rr * Math.sin(ang);
      if (G().pointIn(pts(), wx, wy)) {
        var s = C.project({ x: wx, y: wy, z: zc });
        if (pen) ctx.lineTo(s.x, s.y); else { ctx.moveTo(s.x, s.y); pen = true; }
      } else {
        pen = false;
      }
    }
    ctx.stroke();
  }

  // Wall quads with projected corners; `front` walls (outside toward the
  // camera) are culled to keep the interior visible.
  function wallData(C) {
    var Hh = roomH();
    return G().edges(pts()).map(function (e, i) {
      var quad = [
        { x: e.a.x, y: e.a.y, z: 0 }, { x: e.b.x, y: e.b.y, z: 0 },
        { x: e.b.x, y: e.b.y, z: Hh }, { x: e.a.x, y: e.a.y, z: Hh }
      ];
      return {
        i: i, e: e,
        scr: quad.map(C.project),
        depth: C.project({ x: e.mid.x, y: e.mid.y, z: Hh / 2 }).z,
        front: (C.eye.x - e.mid.x) * e.nx + (C.eye.y - e.mid.y) * e.ny > 0
      };
    });
  }

  function render(v) {
    if (v) view = v;
    if (!view) return;
    sizeCanvas();
    if (canvas.clientWidth < 20) return;
    var C = makeCamera();
    drawScene(Charts.theme(), C, wallData(C));
  }

  function drawScene(th, C, walls) {
    var Hh = roomH(), poly = pts(), st = view.state;
    // sizeCanvas() only resets the backing store when the size changes, so an
    // orbit at a stable size never clears — wipe explicitly before repainting,
    // otherwise a non-opaque --page-plane leaves every previous frame behind.
    ctx.clearRect(0, 0, C.w, C.h);
    ctx.fillStyle = Charts.cssVar('--page-plane');
    ctx.fillRect(0, 0, C.w, C.h);

    // floor: surface fill, 1-m grid, outline
    var floorScr = poly.map(function (p) { return C.project({ x: p.x, y: p.y, z: 0 }); });
    trace(floorScr);
    ctx.fillStyle = th.surface;
    ctx.fill();
    var bb = G().bbox(poly);
    ctx.save();
    trace(floorScr);
    ctx.clip();
    ctx.strokeStyle = th.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (var gx = Math.ceil(bb.minX); gx <= Math.floor(bb.maxX); gx++) {
      var ga = C.project({ x: gx, y: bb.minY, z: 0 }), gb = C.project({ x: gx, y: bb.maxY, z: 0 });
      ctx.moveTo(ga.x, ga.y); ctx.lineTo(gb.x, gb.y);
    }
    for (var gy = Math.ceil(bb.minY); gy <= Math.floor(bb.maxY); gy++) {
      var gc = C.project({ x: bb.minX, y: gy, z: 0 }), gd = C.project({ x: bb.maxX, y: gy, z: 0 });
      ctx.moveTo(gc.x, gc.y); ctx.lineTo(gd.x, gd.y);
    }
    ctx.stroke();
    ctx.restore();
    trace(floorScr);
    ctx.strokeStyle = th.axis;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // rear walls, far to near, with fixed-direction shading so orientation reads
    var light = { x: -0.5, y: 0.86 };
    walls.filter(function (wd) { return !wd.front; })
      .sort(function (a, b) { return b.depth - a.depth; })
      .forEach(function (wd) {
        var shade = Math.max(0, wd.e.nx * light.x + wd.e.ny * light.y);
        var active = hoverWall === wd.i || view.selectedWall === wd.i;
        var fill = mix(th.surface, th.ink, 0.05 + 0.09 * (1 - shade));
        trace(wd.scr);
        ctx.fillStyle = active ? mix(fill, th.s1, 0.2) : fill;
        ctx.fill();
        ctx.strokeStyle = active ? th.s1 : th.axis;
        ctx.lineWidth = active ? 2.5 : 1.25;
        ctx.stroke();
      });
    walls.forEach(function (wd) { // numbers match the Surfaces panel
      if (wd.front) return;
      var p = C.project({
        x: wd.e.mid.x - wd.e.nx * 0.3, y: wd.e.mid.y - wd.e.ny * 0.3, z: Hh * 0.85
      });
      label(String(wd.i + 1), p.x, p.y, th.muted, '10px system-ui, sans-serif');
    });

    // SPL heat map — a translucent sheet at listener height
    var heat = view.heat && view.heat.grid && isFinite(view.heat.grid.min) ? view.heat : null;
    if (heat) {
      var g = heat.grid, hb = g.bb, Lz = st.listener.z;
      var cw = hb.w / g.nx, chh = hb.h / g.ny;
      var corners = [];
      for (var j = 0; j <= g.ny; j++) {
        var row = [];
        for (var i = 0; i <= g.nx; i++) {
          row.push(C.project({ x: hb.minX + i * cw, y: hb.minY + j * chh, z: Lz }));
        }
        corners.push(row);
      }
      ctx.save();
      ctx.globalAlpha = 0.72;
      for (var jj = 0; jj < g.ny; jj++) {
        for (var ii = 0; ii < g.nx; ii++) {
          var val = g.values[jj * g.nx + ii];
          if (isNaN(val)) continue;
          var t = g.max > g.min ? (val - g.min) / (g.max - g.min) : 0.5;
          trace([corners[jj][ii], corners[jj][ii + 1], corners[jj + 1][ii + 1], corners[jj + 1][ii]]);
          ctx.fillStyle = heat.ramp(t);
          ctx.fill();
          ctx.strokeStyle = ctx.fillStyle; // hide seams between cells
          ctx.lineWidth = 0.75;
          ctx.stroke();
        }
      }
      ctx.restore();
      trace(poly.map(function (p) { return C.project({ x: p.x, y: p.y, z: Lz }); }));
      ctx.strokeStyle = th.axis;
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // spherical wave fronts from each source: the equator plus two latitude
    // cross-sections per front, clipped at walls / floor / ceiling
    if (view.waves && view.waves.rings.length) {
      var latOffsets = [0, 0.6, -0.6];
      ctx.save();
      ctx.strokeStyle = th.s3;
      view.waves.rings.forEach(function (ring, ri) {
        ctx.globalAlpha = ring.a * 0.9;
        ctx.lineWidth = ri === view.waves.rings.length - 1 ? 1.8 : 1.1;
        st.sources.forEach(function (src) {
          latOffsets.forEach(function (off) {
            var zc = src.z + off * ring.r;
            if (zc < 0.03 || zc > Hh - 0.03) return;
            strokeWorldCircle(C, src.x, src.y, zc, ring.r * Math.sqrt(1 - off * off));
          });
          var lx = src.x + ring.r * 0.7071, ly = src.y + ring.r * 0.7071;
          if (G().pointIn(poly, lx, ly)) {
            var lp = C.project({ x: lx, y: ly, z: src.z });
            ctx.globalAlpha = 1;
            label(ring.r.toFixed(1) + ' m', lp.x, lp.y - 8, th.ink2, '10px system-ui, sans-serif');
            ctx.globalAlpha = ring.a * 0.9;
          }
        });
      });
      ctx.restore();
      label('sound slowed ×' + view.waves.slow, C.w - 12, C.h - 12, th.muted,
        '10px system-ui, sans-serif', 'right');
    }

    // sources and listener, far to near, each with a floor shadow and a
    // dashed stem showing its height
    var markers = st.sources.map(function (s, i) {
      return { kind: 'source', index: i, p: s };
    }).concat([{ kind: 'listener', index: 0, p: st.listener }]);
    markers.forEach(function (mk) {
      mk.scr = C.project(mk.p);
      mk.foot = C.project({ x: mk.p.x, y: mk.p.y, z: 0 });
    });
    markers.sort(function (a, b) { return b.scr.z - a.scr.z; });
    markers.forEach(function (mk) {
      var r = clamp(C.f * 0.16 / mk.scr.z, 6, 13);
      ctx.save();
      ctx.globalAlpha = 0.18;
      ctx.beginPath();
      ctx.ellipse(mk.foot.x, mk.foot.y, r * 0.7, r * 0.28, 0, 0, Math.PI * 2);
      ctx.fillStyle = th.ink;
      ctx.fill();
      ctx.restore();
      ctx.beginPath();
      ctx.moveTo(mk.foot.x, mk.foot.y);
      ctx.lineTo(mk.scr.x, mk.scr.y);
      ctx.strokeStyle = th.muted;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.stroke();
      ctx.setLineDash([]);
      if (mk.kind === 'source') {
        ctx.beginPath();
        ctx.arc(mk.scr.x, mk.scr.y, r, 0, Math.PI * 2);
        ctx.fillStyle = th.s2;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = th.surface;
        ctx.stroke();
        label(String(mk.index + 1), mk.scr.x, mk.scr.y + 0.5, '#ffffff', 'bold 10px system-ui, sans-serif');
      } else {
        ctx.beginPath();
        ctx.arc(mk.scr.x, mk.scr.y, r * 0.85, 0, Math.PI * 2);
        ctx.fillStyle = th.surface;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = th.ink;
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(mk.scr.x, mk.scr.y, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = th.ink;
        ctx.fill();
        label('L', mk.scr.x, mk.scr.y - r - 7, th.ink2, 'bold 10px system-ui, sans-serif');
      }
      if (drag && drag.kind === mk.kind && drag.index === mk.index && drag.vertical) {
        label('z ' + mk.p.z.toFixed(2) + ' m', mk.scr.x + r + 6, mk.scr.y, th.ink2,
          'bold 11px system-ui, sans-serif', 'left');
      }
    });

    // ceiling outline + vertical edges, light so they don't fight the content
    ctx.save();
    ctx.globalAlpha = 0.6;
    ctx.strokeStyle = th.axis;
    ctx.lineWidth = 1;
    trace(poly.map(function (p) { return C.project({ x: p.x, y: p.y, z: Hh }); }));
    ctx.stroke();
    ctx.beginPath();
    poly.forEach(function (p) {
      var a = C.project({ x: p.x, y: p.y, z: 0 });
      var b = C.project({ x: p.x, y: p.y, z: Hh });
      ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
    });
    ctx.stroke();
    ctx.restore();

    // hovered/selected wall that is culled: show it as a ghost so clicks on
    // the Surfaces panel and floor-edge hovers still have a visual anchor
    walls.forEach(function (wd) {
      if (!wd.front || (hoverWall !== wd.i && view.selectedWall !== wd.i)) return;
      trace(wd.scr);
      ctx.save();
      ctx.globalAlpha = 0.14;
      ctx.fillStyle = th.s1;
      ctx.fill();
      ctx.restore();
      ctx.strokeStyle = th.s1;
      ctx.lineWidth = 2;
      ctx.stroke();
      var p = C.project({ x: wd.e.mid.x, y: wd.e.mid.y, z: Hh * 0.85 });
      label(String(wd.i + 1), p.x, p.y, th.s1, 'bold 10px system-ui, sans-serif');
    });

    // compass (projected north) + room dimensions
    var cc = G().centroid(poly);
    var p0 = C.project({ x: cc.x, y: cc.y, z: 0 });
    var p1 = C.project({ x: cc.x, y: cc.y + 1, z: 0 });
    var ndx = p1.x - p0.x, ndy = p1.y - p0.y;
    var nl = Math.hypot(ndx, ndy);
    if (nl > 1e-6) {
      var ux = ndx / nl, uy = ndy / nl;
      var ax = C.w - 30, ay = 26, len = 11;
      ctx.strokeStyle = th.muted;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(ax - ux * len, ay - uy * len);
      ctx.lineTo(ax + ux * len, ay + uy * len);
      ctx.moveTo(ax + ux * len, ay + uy * len);
      ctx.lineTo(ax + ux * len - ux * 5 + uy * 3, ay + uy * len - uy * 5 - ux * 3);
      ctx.moveTo(ax + ux * len, ay + uy * len);
      ctx.lineTo(ax + ux * len - ux * 5 - uy * 3, ay + uy * len - uy * 5 + ux * 3);
      ctx.stroke();
      label('N', ax + ux * (len + 10), ay + uy * (len + 10), th.muted);
    }
    label(bb.w.toFixed(1) + ' × ' + bb.h.toFixed(1) + ' × ' + Hh.toFixed(2) + ' m',
      12, C.h - 12, th.muted, '11px system-ui, sans-serif', 'left');
  }

  // ---- hit testing ----------------------------------------------------------
  function localPoint(ev) {
    var r = canvas.getBoundingClientRect();
    return { x: ev.clientX - r.left, y: ev.clientY - r.top };
  }
  function distToSeg(p, a, b) {
    var dx = b.x - a.x, dy = b.y - a.y;
    var t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1e-9);
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p.x - (a.x + t * dx), p.y - (a.y + t * dy));
  }

  function hitMarker(p, C) {
    var best = null, bestZ = Infinity;
    function check(mk) {
      var s = C.project(mk.p);
      var r = clamp(C.f * 0.16 / s.z, 6, 13);
      if (Math.hypot(p.x - s.x, p.y - s.y) <= r + 5 && s.z < bestZ) {
        best = mk; bestZ = s.z;
      }
    }
    view.state.sources.forEach(function (s, i) {
      check({ kind: 'source', index: i, p: s });
    });
    check({ kind: 'listener', index: 0, p: view.state.listener });
    return best;
  }

  function hitWall(p, walls) {
    var back = walls.filter(function (w) { return !w.front; })
      .sort(function (a, b) { return a.depth - b.depth; });
    for (var i = 0; i < back.length; i++) {
      if (G().pointIn(back[i].scr, p.x, p.y)) return back[i].i;
    }
    for (var j = 0; j < walls.length; j++) { // culled walls: their floor edge
      if (walls[j].front && distToSeg(p, walls[j].scr[0], walls[j].scr[1]) <= 7) return walls[j].i;
    }
    return null;
  }

  // Tooltip lines for hovering the heat sheet (SPL at that spot), or null.
  function samplePlane(p, C) {
    if (!cbs.samplePoint || !view.heat) return null;
    var pt = C.onPlane(p.x, p.y, view.state.listener.z);
    if (!pt || !G().pointIn(pts(), pt.x, pt.y)) return null;
    return cbs.samplePoint(pt.x, pt.y);
  }

  function wallTipLines(i) {
    var e = G().edges(pts())[i];
    var compass = Math.abs(e.nx) > Math.abs(e.ny)
      ? (e.nx > 0 ? 'E' : 'W') : (e.ny > 0 ? 'N' : 'S');
    var mat = global.Acoustics.MATERIALS[view.state.surfaces.walls[i]];
    return [
      'Wall ' + (i + 1) + ' · ' + compass + (mat ? ' — ' + mat.label : ''),
      e.len.toFixed(2) + ' m × ' + roomH().toFixed(2) + ' m · click to edit material'
    ];
  }

  // ---- pointer handling -----------------------------------------------------
  function pointerDist() {
    var ids = Object.keys(pointers);
    var a = pointers[ids[0]], b = pointers[ids[1]];
    return Math.hypot(a.x - b.x, a.y - b.y) || 1;
  }

  function onPointerDown(ev) {
    if (!view) return;
    var p = localPoint(ev);
    pointers[ev.pointerId] = p;
    if (Object.keys(pointers).length === 2) { // second finger: pinch zoom
      drag = null;
      pinch = { dist: pointerDist(), zoom: cam.zoom };
      canvas.setPointerCapture(ev.pointerId);
      return;
    }
    var C = makeCamera();
    var mk = hitMarker(p, C);
    if (mk) {
      drag = { kind: mk.kind, index: mk.index, vertical: ev.shiftKey };
    } else {
      // orbit; remember a wall under the cursor so a movement-free click
      // still jumps to its material (the heat sheet takes priority)
      var wall = samplePlane(p, C) ? null : hitWall(p, wallData(C));
      drag = { kind: 'orbit', x: p.x, y: p.y, moved: 0, wall: wall };
    }
    canvas.setPointerCapture(ev.pointerId);
    canvas.style.cursor = 'grabbing';
  }

  function onPointerMove(ev) {
    if (!view) return;
    var p = localPoint(ev);
    if (pointers[ev.pointerId]) pointers[ev.pointerId] = p;
    if (pinch) {
      if (Object.keys(pointers).length >= 2) {
        cam.zoom = clamp(pinch.zoom * pointerDist() / pinch.dist, 0.45, 3.5);
        render();
      }
      return;
    }

    if (drag && drag.kind === 'orbit') {
      var dx = p.x - drag.x, dy = p.y - drag.y;
      drag.moved += Math.abs(dx) + Math.abs(dy);
      drag.x = p.x; drag.y = p.y;
      cam.yaw -= dx * 0.008;
      cam.pitch = clamp(cam.pitch + dy * 0.008, 0.12, 1.45);
      hideTip();
      render();
      return;
    }

    if (drag) { // source / listener drag
      var C = makeCamera();
      drag.vertical = ev.shiftKey;
      var target = drag.kind === 'source' ? view.state.sources[drag.index] : view.state.listener;
      if (!target) { drag = null; return; }
      if (drag.vertical) {
        // slide along the marker's vertical line: intersect the pointer ray
        // with the camera-facing vertical plane through that line
        var n = norm({ x: C.eye.x - target.x, y: C.eye.y - target.y, z: 0 });
        var d = C.ray(p.x, p.y);
        var denom = n.x * d.x + n.y * d.y;
        if (Math.abs(denom) > 1e-6) {
          var t = ((target.x - C.eye.x) * n.x + (target.y - C.eye.y) * n.y) / denom;
          if (t > 0) target.z = snap(clamp(C.eye.z + d.z * t, 0.1, roomH() - 0.1));
        }
      } else {
        var pt = C.onPlane(p.x, p.y, target.z);
        if (pt) {
          var x = snap(pt.x), y = snap(pt.y);
          if (G().pointIn(pts(), x, y)) { target.x = x; target.y = y; }
        }
      }
      hideTip();
      if (cbs.onChange) cbs.onChange();
      return;
    }

    // hover: marker > heat sheet > wall
    var C2 = makeCamera();
    var mk = hitMarker(p, C2);
    var lines = mk ? null : samplePlane(p, C2);
    var wall = (mk || lines) ? null : hitWall(p, wallData(C2));
    if (wall !== hoverWall) { hoverWall = wall; render(); }
    canvas.style.cursor = mk ? 'move' : wall !== null ? 'pointer' : 'grab';
    if (mk) {
      showTip(p, [
        mk.kind === 'source' ? 'Source ' + (mk.index + 1) : 'Listener',
        'z ' + mk.p.z.toFixed(2) + ' m · drag moves · ⇧ drag sets height'
      ]);
    } else if (lines) {
      showTip(p, lines);
    } else if (wall !== null) {
      showTip(p, wallTipLines(wall));
    } else {
      hideTip();
    }
  }

  function onPointerUp(ev) {
    delete pointers[ev.pointerId];
    if (pinch && Object.keys(pointers).length < 2) pinch = null;
    if (!drag) return;
    if (drag.kind === 'orbit' && drag.moved < 4 && drag.wall !== null && cbs.onWallClick) {
      cbs.onWallClick(drag.wall);
    }
    var wasMarker = drag.kind !== 'orbit';
    drag = null;
    try { canvas.releasePointerCapture(ev.pointerId); } catch (e) { /* already released */ }
    canvas.style.cursor = 'grab';
    if (wasMarker) render(); // drop the z read-out
  }

  function onPointerLeave() {
    if (hoverWall !== null) { hoverWall = null; render(); }
    hideTip();
  }

  function onWheel(ev) {
    if (!view) return;
    ev.preventDefault();
    cam.zoom = clamp(cam.zoom * Math.exp(-ev.deltaY * 0.0015), 0.45, 3.5);
    hideTip();
    render();
  }

  function onDblClick() {
    cam.yaw = HOME.yaw; cam.pitch = HOME.pitch; cam.zoom = HOME.zoom;
    hideTip();
    render();
  }

  function showTip(p, lines) {
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
  function hideTip() { tipEl.hidden = true; }

  function init(canvasEl, wrapEl, tipElement, callbacks) {
    canvas = canvasEl; wrap = wrapEl; tipEl = tipElement; cbs = callbacks;
    ctx = canvas.getContext('2d');
    canvas.style.cursor = 'grab';
    canvas.addEventListener('pointerdown', onPointerDown);
    canvas.addEventListener('pointermove', onPointerMove);
    canvas.addEventListener('pointerup', onPointerUp);
    canvas.addEventListener('pointercancel', onPointerUp);
    canvas.addEventListener('pointerleave', onPointerLeave);
    canvas.addEventListener('dblclick', onDblClick);
    canvas.addEventListener('wheel', onWheel, { passive: false });
    new ResizeObserver(function () { render(); }).observe(wrap);
  }

  global.View3D = { init: init, render: render };
})(window);
