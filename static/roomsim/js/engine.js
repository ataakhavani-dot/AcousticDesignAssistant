/*
 * Room-acoustics engine — pure functions, no DOM.
 *
 * PROVENANCE: every coefficient and formula in this file is ported from ADA's
 * Python physics engine (web_application.py, "SECTION 7: PHYSICS ENGINE
 * FUNCTIONS", plus the RT60 loop in the RT60 Calculator tab). The numbers this
 * file produces are meant to agree with ADA's own tabs to the digit — if you
 * change a formula in web_application.py, change it here too.
 *
 * Ported from ADA:
 *   MATERIALS      ← MATERIALS                 (web_application.py)
 *   C              ← SPEED_OF_SOUND
 *   rt60()         ← the sabine_rt / eyring_rt loop in the RT60 tab
 *   modes()        ← calculate_modes()
 *   roomRatios()   ← get_room_ratios()
 *   boltArea()     ← check_bolt_area()
 *   targetRT60()   ← the target_rt line in the RT60 tab
 *   sbirCurve()    ← calculate_sbir_curve()
 *
 * NOT in ADA — kept from the original simulator because ADA models no sound
 * field at all, and the 2-D/3-D room view is built around one. These consume
 * ADA-derived absorption, so they stay consistent with the ported formulas:
 *   roomConstant(), splAt(), heatmap(), schroeder(), criticalDistance()
 *
 * The room is a vertical prism: a polygon floor plan (metres, x east / y
 * north, counter-clockwise) extruded to height H. Statistical results work for
 * any simple polygon; mode analysis additionally requires a rectangular plan.
 * All band arrays run over the octave bands 125 Hz … 4 kHz.
 */
(function(global) {
    'use strict';

    // ADA: SPEED_OF_SOUND = 343.0 m/s at 20 °C
    var C = 343.0;
    var BANDS = [125, 250, 500, 1000, 2000, 4000];
    var BAND_LABELS = ['125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz'];

    // ADA: OCTAVE_BANDS
    var BAND_SHORT = ['125', '250', '500', '1k', '2k', '4k'];

    // ADA's MATERIALS dictionary. Keys are slugs so they survive URL / storage
    // round-trips; `label` matches the Streamlit RT60 calculator.
    var MATERIALS = {
        concrete_or_tile: { label: 'Concrete or tile', alpha: [0.01, 0.01, 0.015, 0.02, 0.02, 0.02] },
        linoleum_vinyl_tile_on_concrete: { label: 'Linoleum/vinyl tile on concrete', alpha: [0.02, 0.03, 0.03, 0.03, 0.03, 0.02] },
        wood_on_joists: { label: 'Wood on joists', alpha: [0.15, 0.11, 0.10, 0.07, 0.06, 0.07] },
        parquet_on_concrete: { label: 'Parquet on concrete', alpha: [0.04, 0.04, 0.07, 0.06, 0.06, 0.07] },
        carpet_on_concrete: { label: 'Carpet on concrete', alpha: [0.02, 0.06, 0.14, 0.37, 0.60, 0.65] },
        carpet_on_foam: { label: 'Carpet on foam', alpha: [0.08, 0.24, 0.57, 0.69, 0.71, 0.73] },

        seating_fully_occupied_fabric_upholstered: { label: 'Fully occupied fabric upholstered seating', alpha: [0.60, 0.74, 0.88, 0.96, 0.93, 0.85] },
        seating_occupied_wooden_pews: { label: 'Occupied wooden pews', alpha: [0.57, 0.61, 0.75, 0.86, 0.91, 0.86] },
        seating_empty_fabric_upholstered: { label: 'Empty fabric upholstered seating', alpha: [0.49, 0.66, 0.80, 0.88, 0.82, 0.70] },
        seating_empty_metal_wood: { label: 'Empty metal/wood seats', alpha: [0.15, 0.19, 0.22, 0.39, 0.38, 0.30] },

        brick_unglazed: { label: 'Brick: unglazed', alpha: [0.03, 0.03, 0.03, 0.04, 0.05, 0.07] },
        brick_unglazed_painted: { label: 'Brick: unglazed and painted', alpha: [0.01, 0.01, 0.02, 0.02, 0.02, 0.03] },
        concrete_block_coarse: { label: 'Concrete block: coarse', alpha: [0.36, 0.44, 0.31, 0.29, 0.39, 0.25] },
        concrete_block_painted: { label: 'Concrete block: painted', alpha: [0.10, 0.05, 0.06, 0.07, 0.09, 0.08] },
        curtain_molleton_10oz: { label: 'Curtain: 10 oz/sq yd fabric molleton', alpha: [0.03, 0.04, 0.11, 0.17, 0.24, 0.35] },
        curtain_molleton_14oz: { label: 'Curtain: 14 oz/sq yd fabric molleton', alpha: [0.07, 0.31, 0.49, 0.75, 0.70, 0.60] },
        curtain_molleton_18oz: { label: 'Curtain: 18 oz/sq yd fabric molleton', alpha: [0.14, 0.35, 0.55, 0.72, 0.70, 0.65] },
        fiberglass_2in_703_no_airspace: { label: 'Fiberglass: 2 in. 703, no airspace', alpha: [0.22, 0.82, 0.99, 0.99, 0.99, 0.99] },
        fiberglass_spray_5in: { label: 'Fiberglass: spray, 5 in.', alpha: [0.05, 0.15, 0.45, 0.70, 0.80, 0.80] },
        fiberglass_spray_1in: { label: 'Fiberglass: spray, 1 in.', alpha: [0.16, 0.45, 0.70, 0.90, 0.90, 0.85] },
        fiberglass_2in_rolls: { label: 'Fiberglass: 2 in. rolls', alpha: [0.17, 0.55, 0.80, 0.90, 0.85, 0.80] },
        foam_sonex_2in: { label: 'Foam: Sonex, 2 in.', alpha: [0.06, 0.25, 0.56, 0.81, 0.90, 0.91] },
        foam_sdg_3in: { label: 'Foam: SDG, 3 in.', alpha: [0.24, 0.58, 0.67, 0.91, 0.96, 0.99] },
        foam_sdg_4in: { label: 'Foam: SDG, 4 in.', alpha: [0.33, 0.90, 0.84, 0.99, 0.98, 0.99] },
        foam_polyurethane_1in: { label: 'Foam: polyurethane, 1 in.', alpha: [0.13, 0.22, 0.68, 1.00, 0.92, 0.97] },
        foam_polyurethane_half_in: { label: 'Foam: polyurethane, 1/2 in.', alpha: [0.09, 0.11, 0.22, 0.60, 0.88, 0.94] },
        glass_plate_quarter_in: { label: 'Glass: 1/4 in. plate, large', alpha: [0.18, 0.06, 0.04, 0.03, 0.02, 0.02] },
        glass_window: { label: 'Glass: window', alpha: [0.35, 0.25, 0.18, 0.12, 0.07, 0.04] },
        plaster_smooth_tile_brick: { label: 'Plaster: smooth on tile/brick', alpha: [0.013, 0.015, 0.02, 0.03, 0.04, 0.05] },
        plaster_rough_lath: { label: 'Plaster: rough on lath', alpha: [0.02, 0.03, 0.04, 0.05, 0.04, 0.03] },
        marble_tile: { label: 'Marble/tile', alpha: [0.01, 0.01, 0.01, 0.01, 0.02, 0.02] },
        sheetrock_half_in_16in_oc: { label: 'Sheetrock: 1/2 in., 16 in. on center', alpha: [0.29, 0.10, 0.05, 0.04, 0.07, 0.09] },
        wood_plywood_three_eighth_in: { label: 'Wood: 3/8 in. plywood panel', alpha: [0.28, 0.22, 0.17, 0.09, 0.10, 0.11] },
        acoustic_tiles: { label: 'Acoustic tiles', alpha: [0.05, 0.22, 0.52, 0.56, 0.45, 0.32] },
        acoustic_ceiling_tiles: { label: 'Acoustic ceiling tiles', alpha: [0.70, 0.66, 0.72, 0.92, 0.88, 0.75] },
        wood: { label: 'Wood', alpha: [0.15, 0.11, 0.10, 0.07, 0.06, 0.07] },

        water_or_ice_surface: { label: 'Water or ice surface', alpha: [0.008, 0.008, 0.013, 0.015, 0.020, 0.025] },
        people_adults: { label: 'People (adults)', alpha: [0.25, 0.35, 0.42, 0.46, 0.50, 0.50] }
    };

    // ADA's Modal Analysis tab colours one series per room axis.
    var AXIS_COLORS = { Length: '#ef4444', Width: '#22c55e', Height: '#3b82f6' };

    // ---- polygon geometry -----------------------------------------------------
    function signedArea(pts) {
        var s = 0;
        for (var i = 0; i < pts.length; i++) {
            var a = pts[i],
                b = pts[(i + 1) % pts.length];
            s += a.x * b.y - b.x * a.y;
        }
        return s / 2;
    }

    function area(pts) { return Math.abs(signedArea(pts)); }

    // Edge list with lengths, midpoints, and outward normals (assumes CCW).
    function edges(pts) {
        return pts.map(function(a, i) {
            var b = pts[(i + 1) % pts.length];
            var dx = b.x - a.x,
                dy = b.y - a.y;
            var len = Math.hypot(dx, dy) || 1e-9;
            return {
                a: a,
                b: b,
                len: len,
                mid: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 },
                nx: dy / len,
                ny: -dx / len
            };
        });
    }

    function perimeter(pts) {
        return edges(pts).reduce(function(s, e) { return s + e.len; }, 0);
    }

    function bbox(pts) {
        var minX = Infinity,
            minY = Infinity,
            maxX = -Infinity,
            maxY = -Infinity;
        pts.forEach(function(p) {
            if (p.x < minX) minX = p.x;
            if (p.y < minY) minY = p.y;
            if (p.x > maxX) maxX = p.x;
            if (p.y > maxY) maxY = p.y;
        });
        return { minX: minX, minY: minY, maxX: maxX, maxY: maxY, w: maxX - minX, h: maxY - minY };
    }

    function centroid(pts) {
        var sx = 0,
            sy = 0,
            a2 = 0;
        for (var i = 0; i < pts.length; i++) {
            var a = pts[i],
                b = pts[(i + 1) % pts.length];
            var cr = a.x * b.y - b.x * a.y;
            a2 += cr;
            sx += (a.x + b.x) * cr;
            sy += (a.y + b.y) * cr;
        }
        if (Math.abs(a2) < 1e-9) {
            var bb = bbox(pts);
            return { x: (bb.minX + bb.maxX) / 2, y: (bb.minY + bb.maxY) / 2 };
        }
        return { x: sx / (3 * a2), y: sy / (3 * a2) };
    }

    function pointIn(pts, x, y) {
        var inside = false;
        for (var i = 0, j = pts.length - 1; i < pts.length; j = i++) {
            var pi = pts[i],
                pj = pts[j];
            if ((pi.y > y) !== (pj.y > y) &&
                x < (pj.x - pi.x) * (y - pi.y) / (pj.y - pi.y) + pi.x) inside = !inside;
        }
        return inside;
    }

    function ccw(a, b, c) { return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x); }
    // Proper crossing of segments ab and cd (shared endpoints don't count).
    function segsCross(a, b, c, d) {
        var d1 = ccw(a, b, c),
            d2 = ccw(a, b, d),
            d3 = ccw(c, d, a),
            d4 = ccw(c, d, b);
        return ((d1 > 0) !== (d2 > 0)) && ((d3 > 0) !== (d4 > 0));
    }

    function selfIntersects(pts) {
        var n = pts.length;
        for (var i = 0; i < n; i++) {
            for (var j = i + 1; j < n; j++) {
                if (j === i + 1 || (i === 0 && j === n - 1)) continue; // adjacent edges share a vertex
                if (segsCross(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n])) return true;
            }
        }
        return false;
    }
    // {L, W} if the plan is a rectangle (any orientation, ~1° tolerance), else null.
    function isRectangle(pts) {
        if (pts.length !== 4) return null;
        for (var i = 0; i < 4; i++) {
            var p0 = pts[i],
                p1 = pts[(i + 1) % 4],
                p2 = pts[(i + 2) % 4];
            var ux = p1.x - p0.x,
                uy = p1.y - p0.y;
            var vx = p2.x - p1.x,
                vy = p2.y - p1.y;
            var dot = ux * vx + uy * vy;
            var mag = Math.hypot(ux, uy) * Math.hypot(vx, vy);
            if (mag < 1e-9 || Math.abs(dot) / mag > 0.02) return null;
        }
        return {
            L: Math.hypot(pts[1].x - pts[0].x, pts[1].y - pts[0].y),
            W: Math.hypot(pts[2].x - pts[1].x, pts[2].y - pts[1].y)
        };
    }

    function ensureCCW(pts) {
        return signedArea(pts) < 0 ? pts.slice().reverse() : pts.slice();
    }

    var geom = {
        signedArea: signedArea,
        area: area,
        edges: edges,
        perimeter: perimeter,
        bbox: bbox,
        centroid: centroid,
        pointIn: pointIn,
        segsCross: segsCross,
        selfIntersects: selfIntersects,
        isRectangle: isRectangle,
        ensureCCW: ensureCCW
    };

    // ---- surfaces & absorption ------------------------------------------------
    function surfaceAreas(room) {
        var floorA = area(room.points);
        return {
            floor: floorA,
            ceiling: floorA,
            walls: edges(room.points).map(function(e) { return e.len * room.H; })
        };
    }

    function alphaOf(key, b) {
        var mat = MATERIALS[key];
        return mat ? mat.alpha[b] : 0.02;
    }

    // Per-band absorption. ADA computes A = Σ(α_i · S_i) over walls, floor and
    // ceiling and takes ᾱ = A / S_total — no air-absorption term, so there is
    // deliberately no 4mV here (the original simulator had one; ADA does not).
    function absorption(room, surfaces) {
        var areas = surfaceAreas(room);
        var V = areas.floor * room.H;
        var S = areas.floor + areas.ceiling +
            areas.walls.reduce(function(s, a) { return s + a; }, 0);

        var A = BANDS.map(function(_, b) {
            var sum = areas.floor * alphaOf(surfaces.floor, b) +
                areas.ceiling * alphaOf(surfaces.ceiling, b);
            areas.walls.forEach(function(wa, i) {
                sum += wa * alphaOf(surfaces.walls[i], b);
            });
            return sum;
        });
        // ADA: alpha_avg = abs_total / surface_area
        var meanAlpha = A.map(function(a) { return a / S; });

        return { areas: areas, S: S, V: V, A: A, meanAlpha: meanAlpha };
    }

    // RT60 per band, exactly as ADA's RT60 Calculator tab computes it:
    //   Sabine: RT60 = 0.161·V / A
    //   Eyring: RT60 = 0.161·V / (−S·ln(1 − ᾱ)), and 0 when ᾱ ≥ 0.99
    // Note ADA's Eyring returns 0 (not Infinity) in the saturated case.
    function rt60(abs) {
        var sabine = abs.A.map(function(A) {
            return A > 0 ? 0.161 * abs.V / A : Infinity;
        });
        var eyring = abs.meanAlpha.map(function(a) {
            return a < 0.99 ? (0.161 * abs.V) / (-abs.S * Math.log(1 - a)) : 0;
        });
        return { sabine: sabine, eyring: eyring };
    }

    // ADA: target_rt = 0.25 · (V/100)^(1/3)
    function targetRT60(V) {
        return 0.25 * Math.pow(V / 100, 1 / 3);
    }

    // ADA: get_room_ratios() — sort dims descending, return
    // (middle/smallest, largest/smallest).
    function roomRatios(L, W, H) {
        var d = [L, W, H].sort(function(a, b) { return b - a; });
        return { x: d[1] / d[2], y: d[0] / d[2] };
    }

    // ADA: check_bolt_area() — the stable-ratio rectangle.
    function boltArea(x, y) {
        return (x > 1.14 && x < 1.6 && y > 1.12 && y < 1.54) ?
            { status: 'Stable Zone', stable: true } :
            { status: 'Unstable', stable: false };
    }

    // NOT FROM ADA — ADA models no sound field, but the room view needs one.
    // Room constant R = A / (1 − ᾱ) per band, fed by ADA's absorption above.
    function roomConstant(abs) {
        return abs.A.map(function(A, b) {
            return A / Math.max(1 - abs.meanAlpha[b], 0.01);
        });
    }

    // ADA: calculate_modes() — axial modes only, f = (c/2)·(n/dimension), for
    // n = 1…4 along each of Length, Width and Height independently, keeping
    // everything at or below maxFreq (ADA's default is 300 Hz). ADA does not
    // model tangential or oblique modes, so neither do we.
    function modes(dims, maxFreq) {
        var fMax = maxFreq || 300;
        var out = [];
        var axes = [
            { axis: 'Length', dim: dims.L, n: function(n) { return { nx: n, ny: 0, nz: 0 }; } },
            { axis: 'Width', dim: dims.W, n: function(n) { return { nx: 0, ny: n, nz: 0 }; } },
            { axis: 'Height', dim: dims.H, n: function(n) { return { nx: 0, ny: 0, nz: n }; } }
        ];
        for (var n = 1; n < 5; n++) {
            axes.forEach(function(a) {
                var f = (C / 2) * (n / a.dim);
                if (f > fMax) return;
                var order = a.n(n);
                out.push({
                    f: f,
                    n: n,
                    axis: a.axis,
                    color: AXIS_COLORS[a.axis],
                    type: 'axial',
                    nx: order.nx,
                    ny: order.ny,
                    nz: order.nz
                });
            });
        }
        out.sort(function(a, b) { return a.f - b.f; });
        return out;
    }

    // ADA: calculate_sbir_curve() — quarter-wavelength cancellation at
    // f = c/(4d) for each boundary distance, applied as a triangular notch
    // 10 dB deep spanning ±30 % of f_cancel, summed, then floored at −20 dB.
    function sbirCurve(distances) {
        var freqs = [40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800];
        var resp = freqs.map(function() { return 0; });
        distances.forEach(function(d) {
            if (!(d > 0)) return;
            var fCancel = C / (4 * d);
            var span = fCancel * 0.3;
            freqs.forEach(function(f, i) {
                var diff = Math.abs(f - fCancel);
                if (diff < span) resp[i] -= 10 * (1 - diff / span);
            });
        });
        return { freqs: freqs, response: resp.map(function(v) { return Math.max(v, -20); }) };
    }

    // Steady-state SPL at a point for one band:
    // Lp = Lw + 10·log10( Q/(4πr²) + 4/R ), energy-summed over sources.
    // Returns null when there are no sources.
    function splAt(x, y, z, sources, R) {
        if (!sources.length) return null;
        var sum = 0;
        for (var i = 0; i < sources.length; i++) {
            var s = sources[i];
            var r = Math.sqrt(
                Math.pow(x - s.x, 2) + Math.pow(y - s.y, 2) + Math.pow(z - s.z, 2));
            r = Math.max(r, 0.25); // near-field clamp
            var lp = s.Lw + 10 * Math.log10(s.Q / (4 * Math.PI * r * r) + 4 / R);
            sum += Math.pow(10, lp / 10);
        }
        return 10 * Math.log10(sum);
    }

    // SPL sampled on a horizontal grid at height z over the plan's bounding box;
    // cells outside the polygon are NaN.
    function heatmap(room, sources, R, z, targetCells) {
        var bb = bbox(room.points);
        var res = Math.max(bb.w, bb.h) / (targetCells || 48);
        var nx = Math.max(8, Math.min(72, Math.round(bb.w / res)));
        var ny = Math.max(8, Math.min(72, Math.round(bb.h / res)));
        var values = new Float64Array(nx * ny);
        var min = Infinity,
            max = -Infinity;
        for (var j = 0; j < ny; j++) {
            for (var i = 0; i < nx; i++) {
                var cx = bb.minX + (i + 0.5) * bb.w / nx;
                var cy = bb.minY + (j + 0.5) * bb.h / ny;
                var v = pointIn(room.points, cx, cy) ? splAt(cx, cy, z, sources, R) : null;
                values[j * nx + i] = v === null ? NaN : v;
                if (v !== null) { if (v < min) min = v; if (v > max) max = v; }
            }
        }
        return { nx: nx, ny: ny, bb: bb, values: values, min: min, max: max };
    }

    // Everything the UI needs, from one state object.
    function computeAll(state) {
        var abs = absorption(state.room, state.surfaces);
        var rt = rt60(abs);
        var R = roomConstant(abs);

        var tMid = (rt.sabine[2] + rt.sabine[3]) / 2; // 500 Hz / 1 kHz average
        var schroeder = 2000 * Math.sqrt(tMid / abs.V); // not from ADA
        var target = targetRT60(abs.V);

        var rect = isRectangle(state.room.points);
        // ADA caps modal analysis at 300 Hz regardless of room size.
        var modeFMax = 300;
        var dims = rect ? { L: rect.L, W: rect.W, H: state.room.H } : null;
        var modeList = dims ? modes(dims, modeFMax) : [];
        var ratios = dims ? roomRatios(dims.L, dims.W, dims.H) : null;
        var bolt = ratios ? boltArea(ratios.x, ratios.y) : null;

        var L = state.listener;
        var splListener = BANDS.map(function(_, b) {
            return splAt(L.x, L.y, L.z, state.sources, R[b]);
        });
        var splOverall = null;
        if (state.sources.length) {
            var e = 0;
            splListener.forEach(function(lp) { e += Math.pow(10, lp / 10); });
            splOverall = 10 * Math.log10(e);
        }

        // Critical distance per source at 1 kHz: Dc = 0.141·√(Q·R) — not from ADA.
        var critical = state.sources.map(function(s) {
            return 0.141 * Math.sqrt(s.Q * R[3]);
        });

        return {
            abs: abs,
            rt: rt,
            R: R,
            tMid: tMid,
            schroeder: schroeder,
            target: target,
            rect: rect,
            modes: modeList,
            modeFMax: modeFMax,
            ratios: ratios,
            bolt: bolt,
            splListener: splListener,
            splOverall: splOverall,
            critical: critical
        };
    }

    global.Acoustics = {
        C: C,
        BANDS: BANDS,
        BAND_LABELS: BAND_LABELS,
        BAND_SHORT: BAND_SHORT,
        MATERIALS: MATERIALS,
        AXIS_COLORS: AXIS_COLORS,
        geom: geom,
        surfaceAreas: surfaceAreas,
        absorption: absorption,
        rt60: rt60,
        targetRT60: targetRT60,
        roomRatios: roomRatios,
        boltArea: boltArea,
        roomConstant: roomConstant,
        modes: modes,
        sbirCurve: sbirCurve,
        splAt: splAt,
        heatmap: heatmap,
        computeAll: computeAll
    };
    if (typeof module !== 'undefined' && module.exports) module.exports = global.Acoustics;
})(typeof window !== 'undefined' ? window : globalThis);