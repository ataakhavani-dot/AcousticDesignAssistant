"""Interactive acoustics teaching simulations for ADA's Discovery Lab."""

from __future__ import annotations

import json

import streamlit.components.v1 as components


SIMULATOR_EXPERIMENTS = (
    {
        "id": "helmholtz",
        "name": "Hermann von Helmholtz",
        "topic": "Resonance",
        "description": "Explore how cavity volume and neck area shift a resonator's tuning.",
        "controls": (
            {
                "key": "h_volume",
                "label": "Cavity volume",
                "unit": "L",
                "type": "range",
                "min": 10,
                "max": 100,
                "step": 1,
                "value": 50,
            },
            {
                "key": "h_neck_area",
                "label": "Neck area",
                "unit": "cm2",
                "type": "range",
                "min": 10,
                "max": 100,
                "step": 1,
                "value": 50,
            },
        ),
    },
    {
        "id": "sabine",
        "name": "Wallace C. Sabine",
        "topic": "Reverberation time",
        "description": "Change room volume and equivalent absorption to see an RT60 decay model.",
        "controls": (
            {
                "key": "s_volume",
                "label": "Room volume",
                "unit": "m3",
                "type": "range",
                "min": 500,
                "max": 5000,
                "step": 100,
                "value": 1000,
            },
            {
                "key": "s_absorption",
                "label": "Absorption",
                "unit": "sabins",
                "type": "range",
                "min": 10,
                "max": 1000,
                "step": 10,
                "value": 100,
            },
        ),
    },
    {
        "id": "pohl",
        "name": "R. W. Pohl",
        "topic": "Diffraction",
        "description": "Compare slit width to wavelength and watch the outgoing beam spread.",
        "controls": (
            {
                "key": "p_slit_width",
                "label": "Slit width",
                "unit": "cm",
                "type": "range",
                "min": 5,
                "max": 100,
                "step": 1,
                "value": 20,
            },
            {
                "key": "p_wavelength",
                "label": "Wavelength",
                "unit": "cm",
                "type": "range",
                "min": 5,
                "max": 50,
                "step": 1,
                "value": 15,
            },
        ),
    },
    {
        "id": "fletcher",
        "name": "Harvey Fletcher",
        "topic": "Pitch perception",
        "description": "Raise level to compare a physical tone pair with a perception-oriented model.",
        "controls": (
            {
                "key": "f_level",
                "label": "Sound level",
                "unit": "%",
                "type": "range",
                "min": 0,
                "max": 100,
                "step": 1,
                "value": 35,
            },
        ),
    },
    {
        "id": "haas",
        "name": "Helmut Haas",
        "topic": "Precedence effect",
        "description": "Move the delayed arrival through fusion, localization, and echo regions.",
        "controls": (
            {
                "key": "ha_delay",
                "label": "Delay",
                "unit": "ms",
                "type": "range",
                "min": 0,
                "max": 80,
                "step": 1,
                "value": 10,
            },
        ),
    },
    {
        "id": "franssen",
        "name": "Nico Franssen",
        "topic": "Auditory memory",
        "description": "Run a crossfade while the onset cue preserves the perceived source direction.",
        "controls": (
            {
                "key": "fr_play",
                "label": "Play crossfade",
                "type": "action",
                "action": "playFranssen",
            },
        ),
    },
    {
        "id": "schroeder",
        "name": "Manfred R. Schroeder",
        "topic": "Diffusion",
        "description": "Select a quadratic-residue sequence and inspect the diffuser well pattern.",
        "controls": (
            {
                "key": "sc_prime",
                "label": "Prime sequence",
                "type": "select",
                "options": (7, 11, 13, 17, 19, 23),
                "value": 7,
            },
        ),
    },
    {
        "id": "heaney",
        "name": "K. D. Heaney",
        "topic": "Sound channel",
        "description": "Place a source around a simplified deep-ocean sound channel and trace rays.",
        "controls": (
            {
                "key": "he_depth",
                "label": "Source depth",
                "unit": "fathoms",
                "type": "range",
                "min": 0,
                "max": 2000,
                "step": 10,
                "value": 700,
            },
        ),
    },
    {
        "id": "olive",
        "name": "Olive and Toole",
        "topic": "Lateral reflections",
        "description": "Position a lateral reflection in an educational delay-versus-level perception map.",
        "controls": (
            {
                "key": "ol_delay",
                "label": "Reflection delay",
                "unit": "ms",
                "type": "range",
                "min": 0,
                "max": 80,
                "step": 1,
                "value": 20,
            },
            {
                "key": "ol_level",
                "label": "Reflection level",
                "unit": "dB",
                "type": "range",
                "min": -40,
                "max": 10,
                "step": 1,
                "value": -15,
            },
        ),
    },
    {
        "id": "davis",
        "name": "Don and Chips Davis",
        "topic": "LEDE control room",
        "description": "Toggle a conceptual Live End, Dead End control-room treatment layout.",
        "controls": (
            {
                "key": "d_lede",
                "label": "LEDE treatment",
                "type": "toggle",
                "value": True,
            },
        ),
    },
)


def render_experiment_simulator() -> None:
    """Render an ADA-styled interactive simulator beneath the historical lab records."""
    components.html(_build_experiment_simulator_html(), height=840, scrolling=False)


def _build_experiment_simulator_html() -> str:
    experiments_json = json.dumps(SIMULATOR_EXPERIMENTS)
    markup = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {
                color-scheme: dark;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            * { box-sizing: border-box; }
            body {
                background: transparent;
                color: #e2e8f0;
                margin: 0;
                overflow: hidden;
            }
            button, input, select { font: inherit; }
            .simulator {
                background: #111827;
                border: 1px solid #334155;
                border-radius: 8px;
                height: 838px;
                overflow-y: auto;
                padding: 16px;
                scrollbar-color: #475569 #111827;
            }
            .sim-header {
                align-items: flex-start;
                border-bottom: 1px solid #334155;
                display: flex;
                gap: 18px;
                justify-content: space-between;
                margin-bottom: 14px;
                padding-bottom: 14px;
            }
            .eyebrow {
                color: #60a5fa;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.1em;
                margin: 0 0 4px;
            }
            h1 {
                color: #f8fafc;
                font-size: 21px;
                line-height: 1.2;
                margin: 0;
            }
            .header-copy {
                color: #94a3b8;
                font-size: 12px;
                line-height: 1.45;
                margin: 6px 0 0;
                max-width: 640px;
            }
            .metrics {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: flex-end;
                max-width: 420px;
            }
            .metric {
                background: #172033;
                border: 1px solid #334155;
                border-radius: 6px;
                min-width: 102px;
                padding: 7px 9px;
            }
            .metric-label {
                color: #94a3b8;
                display: block;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            .metric-value {
                color: #f8fafc;
                display: block;
                font-family: "SF Mono", "Roboto Mono", monospace;
                font-size: 12px;
                font-weight: 700;
                margin-top: 2px;
                white-space: nowrap;
            }
            .sim-body {
                display: grid;
                gap: 14px;
                grid-template-columns: minmax(0, 1fr) minmax(260px, 316px);
                min-height: 650px;
            }
            .visual-stage {
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                min-height: 0;
                overflow: hidden;
            }
            .stage-toolbar {
                align-items: center;
                border-bottom: 1px solid #334155;
                display: flex;
                gap: 10px;
                justify-content: space-between;
                padding: 10px 12px;
            }
            .stage-title {
                color: #dbeafe;
                font-size: 12px;
                font-weight: 700;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .reset-button {
                background: #1e293b;
                border: 1px solid #475569;
                border-radius: 6px;
                color: #cbd5e1;
                cursor: pointer;
                flex: 0 0 auto;
                font-size: 11px;
                font-weight: 700;
                padding: 6px 9px;
            }
            .reset-button:hover { border-color: #60a5fa; color: #f8fafc; }
            .canvas-wrap {
                flex: 1;
                min-height: 390px;
                position: relative;
            }
            canvas {
                height: 100%;
                left: 0;
                position: absolute;
                top: 0;
                width: 100%;
            }
            .stage-note {
                border-top: 1px solid #334155;
                color: #94a3b8;
                font-size: 11px;
                line-height: 1.4;
                margin: 0;
                padding: 9px 12px;
            }
            .controls-panel {
                background: #172033;
                border: 1px solid #334155;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                min-height: 0;
                overflow: hidden;
            }
            .panel-heading {
                border-bottom: 1px solid #334155;
                padding: 12px;
            }
            .panel-kicker {
                color: #60a5fa;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.08em;
                margin: 0 0 4px;
            }
            .panel-heading h2 {
                color: #f8fafc;
                font-size: 15px;
                margin: 0;
            }
            .experiment-select-wrap { padding: 12px 12px 0; }
            label {
                color: #cbd5e1;
                display: block;
                font-size: 11px;
                font-weight: 700;
                margin-bottom: 6px;
            }
            select, .number-input {
                background: #0f172a;
                border: 1px solid #475569;
                border-radius: 6px;
                color: #f8fafc;
                height: 36px;
                outline: none;
                padding: 0 9px;
                width: 100%;
            }
            select:focus, .number-input:focus, input[type=range]:focus-visible {
                box-shadow: 0 0 0 2px #0f172a, 0 0 0 3px #60a5fa;
            }
            .control-grid {
                display: grid;
                gap: 12px;
                padding: 14px 12px;
            }
            .control-row { min-width: 0; }
            .control-heading {
                align-items: center;
                display: flex;
                gap: 8px;
                justify-content: space-between;
            }
            .control-heading label { margin: 0; }
            .control-value {
                color: #dbeafe;
                font-family: "SF Mono", "Roboto Mono", monospace;
                font-size: 11px;
                font-weight: 700;
                white-space: nowrap;
            }
            .range-wrap {
                align-items: center;
                display: grid;
                gap: 9px;
                grid-template-columns: minmax(0, 1fr) 74px;
                margin-top: 8px;
            }
            input[type=range] {
                accent-color: #60a5fa;
                cursor: pointer;
                width: 100%;
            }
            .number-input {
                font-family: "SF Mono", "Roboto Mono", monospace;
                font-size: 11px;
            }
            .action-button {
                background: #60a5fa;
                border: 1px solid #93c5fd;
                border-radius: 6px;
                color: #0f172a;
                cursor: pointer;
                font-size: 12px;
                font-weight: 800;
                height: 38px;
                width: 100%;
            }
            .action-button:hover { background: #93c5fd; }
            .toggle-row {
                align-items: center;
                background: #0f172a;
                border: 1px solid #475569;
                border-radius: 6px;
                display: flex;
                justify-content: space-between;
                padding: 8px 9px;
            }
            .toggle-row label { margin: 0; }
            .switch {
                background: #334155;
                border: 1px solid #64748b;
                border-radius: 999px;
                cursor: pointer;
                height: 24px;
                padding: 2px;
                width: 44px;
            }
            .switch-track {
                background: #cbd5e1;
                border-radius: 50%;
                display: block;
                height: 18px;
                transform: translateX(0);
                transition: transform 0.2s ease;
                width: 18px;
            }
            .switch.is-on { background: #60a5fa; border-color: #93c5fd; }
            .switch.is-on .switch-track { background: #0f172a; transform: translateX(18px); }
            .control-note {
                border-top: 1px solid #334155;
                color: #94a3b8;
                font-size: 11px;
                line-height: 1.45;
                margin: auto 0 0;
                padding: 12px;
            }
            .sim-footer {
                border-top: 1px solid #334155;
                color: #64748b;
                font-size: 10px;
                line-height: 1.4;
                margin-top: 14px;
                padding-top: 10px;
            }
            @media (max-width: 760px) {
                .simulator { height: 838px; padding: 14px; }
                .sim-header { flex-direction: column; }
                .metrics { justify-content: flex-start; max-width: none; }
                .sim-body { grid-template-columns: 1fr; min-height: 0; }
                .visual-stage { min-height: 348px; }
                .canvas-wrap { min-height: 265px; }
                .controls-panel { min-height: 390px; }
            }
        </style>
    </head>
    <body>
        <main class="simulator">
            <header class="sim-header">
                <div>
                    <p class="eyebrow">INTERACTIVE SIMULATOR</p>
                    <h1>Acoustics experiments workbench</h1>
                    <p class="header-copy">Adjust one controlled variable at a time and inspect the visual model. This is an educational simulator, not a calibrated prediction tool.</p>
                </div>
                <div class="metrics" id="metrics" aria-live="polite"></div>
            </header>
            <div class="sim-body">
                <section class="visual-stage" aria-label="Interactive experiment visualisation">
                    <div class="stage-toolbar">
                        <span class="stage-title" id="stage-title"></span>
                        <button class="reset-button" id="reset-button" type="button">Reset</button>
                    </div>
                    <div class="canvas-wrap"><canvas id="sim-canvas" aria-label="Experiment visualisation"></canvas></div>
                    <p class="stage-note" id="stage-note"></p>
                </section>
                <aside class="controls-panel" aria-label="Experiment controls">
                    <div class="panel-heading">
                        <p class="panel-kicker">LAB CONTROLS</p>
                        <h2>Change the experiment</h2>
                    </div>
                    <div class="experiment-select-wrap">
                        <label for="experiment-select">Select experiment</label>
                        <select id="experiment-select"></select>
                    </div>
                    <div class="control-grid" id="control-grid"></div>
                    <p class="control-note" id="control-note"></p>
                </aside>
            </div>
            <footer class="sim-footer">Models are conceptual reconstructions of historical demonstrations. Validate design choices with measurements, standards, and qualified engineering review.</footer>
        </main>
        <script>
            const experiments = __EXPERIMENTS__;
            const palette = {
                canvas: "#0f172a", grid: "#172033", text: "#cbd5e1", muted: "#94a3b8",
                outline: "#475569", blue: "#60a5fa", blueSoft: "rgba(96,165,250,0.24)",
                green: "#34d399", amber: "#fbbf24", red: "#fb7185", purple: "#c084fc"
            };
            const state = {};
            const defaults = {};
            const select = document.getElementById("experiment-select");
            const controlGrid = document.getElementById("control-grid");
            const metrics = document.getElementById("metrics");
            const stageTitle = document.getElementById("stage-title");
            const stageNote = document.getElementById("stage-note");
            const controlNote = document.getElementById("control-note");
            const canvas = document.getElementById("sim-canvas");
            const context = canvas.getContext("2d");
            let selectedId = experiments[0].id;
            let canvasWidth = 0;
            let canvasHeight = 0;
            let lastTimestamp = performance.now();
            let lastMetricSignature = "";
            let franssenStartedAt = null;

            experiments.forEach((experiment) => {
                experiment.controls.forEach((control) => {
                    if (control.type !== "action") {
                        state[control.key] = control.value;
                        defaults[control.key] = control.value;
                    }
                });
                const option = document.createElement("option");
                option.value = experiment.id;
                option.textContent = `${experiment.name}: ${experiment.topic}`;
                select.appendChild(option);
            });

            function currentExperiment() {
                return experiments.find((experiment) => experiment.id === selectedId) || experiments[0];
            }

            function clamp(value, min, max) {
                return Math.min(Math.max(value, min), max);
            }

            function resizeCanvas() {
                const rect = canvas.getBoundingClientRect();
                const ratio = Math.min(window.devicePixelRatio || 1, 2);
                canvasWidth = rect.width;
                canvasHeight = rect.height;
                canvas.width = Math.max(1, Math.round(canvasWidth * ratio));
                canvas.height = Math.max(1, Math.round(canvasHeight * ratio));
                context.setTransform(ratio, 0, 0, ratio, 0, 0);
            }

            new ResizeObserver(resizeCanvas).observe(canvas);

            function setMetrics(items) {
                const signature = JSON.stringify(items);
                if (signature === lastMetricSignature) return;
                lastMetricSignature = signature;
                metrics.innerHTML = "";
                items.forEach((item) => {
                    const metric = document.createElement("div");
                    metric.className = "metric";
                    const label = document.createElement("span");
                    label.className = "metric-label";
                    label.textContent = item.label;
                    const value = document.createElement("span");
                    value.className = "metric-value";
                    value.textContent = item.value;
                    if (item.color) value.style.color = item.color;
                    metric.append(label, value);
                    metrics.appendChild(metric);
                });
            }

            function drawGrid(ctx, width, height) {
                ctx.clearRect(0, 0, width, height);
                ctx.fillStyle = palette.canvas;
                ctx.fillRect(0, 0, width, height);
                ctx.strokeStyle = palette.grid;
                ctx.lineWidth = 1;
                for (let x = 24; x < width; x += 32) {
                    ctx.beginPath();
                    ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
                }
                for (let y = 24; y < height; y += 32) {
                    ctx.beginPath();
                    ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
                }
            }

            function text(ctx, value, x, y, color = palette.text, size = 12, align = "center") {
                ctx.fillStyle = color;
                ctx.font = `600 ${size}px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
                ctx.textAlign = align;
                ctx.textBaseline = "middle";
                ctx.fillText(value, x, y);
            }

            function label(ctx, value, x, y, color = palette.blue) {
                ctx.font = '700 10px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
                const width = ctx.measureText(value).width + 16;
                ctx.fillStyle = "rgba(15,23,42,0.9)";
                ctx.strokeStyle = color;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.roundRect(x - width / 2, y - 12, width, 24, 7);
                ctx.fill(); ctx.stroke();
                text(ctx, value, x, y, palette.text, 10);
            }

            function wave(ctx, x, y, length, amplitude, frequency, phase, color) {
                ctx.beginPath();
                for (let offset = 0; offset <= length; offset += 3) {
                    const pointY = y + Math.sin((offset / length) * Math.PI * frequency + phase) * amplitude;
                    if (offset === 0) ctx.moveTo(x + offset, pointY);
                    else ctx.lineTo(x + offset, pointY);
                }
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawHelmholtz(ctx, width, height, time) {
                const volume = Number(state.h_volume);
                const neckArea = Number(state.h_neck_area);
                const volumeM3 = volume / 1000;
                const areaM2 = neckArea / 10000;
                const frequency = (343 / (2 * Math.PI)) * Math.sqrt(areaM2 / (volumeM3 * 0.05));
                setMetrics([
                    { label: "Cavity", value: `${volume} L` },
                    { label: "Neck", value: `${neckArea} cm2` },
                    { label: "Model tune", value: `${frequency.toFixed(0)} Hz`, color: palette.blue },
                ]);
                const cx = width * 0.4;
                const cy = height * 0.57;
                const radius = Math.min(height * 0.24, 38 + volume * 0.25);
                const neckWidth = 15 + neckArea * 0.34;
                const neckHeight = 50;
                for (let index = 0; index < 3; index += 1) wave(ctx, 24, cy - 28 + index * 24, 125, 10, 3.6, time * 5 + index, palette.blue);
                ctx.fillStyle = "#172033";
                ctx.strokeStyle = palette.outline;
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
                ctx.fillStyle = palette.canvas;
                ctx.fillRect(cx - neckWidth / 2, cy - radius - neckHeight - 2, neckWidth, neckHeight + 8);
                ctx.strokeStyle = palette.outline;
                ctx.beginPath();
                ctx.moveTo(cx - neckWidth / 2, cy - radius); ctx.lineTo(cx - neckWidth / 2, cy - radius - neckHeight);
                ctx.moveTo(cx + neckWidth / 2, cy - radius); ctx.lineTo(cx + neckWidth / 2, cy - radius - neckHeight);
                ctx.stroke();
                const displacement = Math.sin(time * frequency * 0.04) * 12;
                ctx.fillStyle = "rgba(96,165,250,0.75)";
                ctx.beginPath(); ctx.arc(cx, cy - radius - neckHeight / 2 + displacement, Math.max(5, neckWidth / 4), 0, Math.PI * 2); ctx.fill();
                label(ctx, "resonator", cx, cy + radius + 28, palette.blue);
                const gx = width * 0.68;
                const gy = height * 0.72;
                const graphWidth = width * 0.25;
                const graphHeight = height * 0.42;
                ctx.strokeStyle = palette.outline;
                ctx.lineWidth = 1;
                ctx.strokeRect(gx, gy - graphHeight, graphWidth, graphHeight);
                ctx.strokeStyle = palette.blue;
                ctx.lineWidth = 2;
                ctx.beginPath();
                for (let index = 0; index <= 80; index += 1) {
                    const hz = 30 + (index / 80) * 350;
                    const gain = Math.exp(-Math.pow((hz - frequency) / 38, 2));
                    const px = gx + (index / 80) * graphWidth;
                    const py = gy - 10 - gain * (graphHeight - 20);
                    if (index === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
                }
                ctx.stroke();
                label(ctx, "relative response", gx + graphWidth / 2, gy + 22, palette.blue);
                stageNote.textContent = "Relative Helmholtz model: f = c / (2π) × sqrt(A / (V × L_eff)); neck length is held at 5 cm.";
            }

            function drawSabine(ctx, width, height) {
                const volume = Number(state.s_volume);
                const absorption = Number(state.s_absorption);
                const rt60 = Math.max(0.05, (0.161 * volume) / absorption);
                setMetrics([
                    { label: "Volume", value: `${volume} m3` },
                    { label: "Absorption", value: `${absorption} sabins` },
                    { label: "RT60", value: `${rt60.toFixed(2)} s`, color: palette.green },
                ]);
                const gx = width * 0.12;
                const gy = height * 0.78;
                const graphWidth = width * 0.76;
                const graphHeight = height * 0.54;
                ctx.strokeStyle = palette.outline;
                ctx.lineWidth = 1;
                ctx.beginPath(); ctx.moveTo(gx, gy - graphHeight); ctx.lineTo(gx, gy); ctx.lineTo(gx + graphWidth, gy); ctx.stroke();
                ctx.strokeStyle = palette.blue;
                ctx.lineWidth = 3;
                ctx.beginPath();
                const timeSpan = Math.max(3, rt60 * 1.25);
                for (let index = 0; index <= 120; index += 1) {
                    const time = (index / 120) * timeSpan;
                    const level = Math.max(0, 60 - (time / rt60) * 60);
                    const px = gx + (index / 120) * graphWidth;
                    const py = gy - (level / 60) * graphHeight;
                    if (index === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
                }
                ctx.stroke();
                ctx.setLineDash([6, 5]);
                ctx.strokeStyle = palette.red;
                ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + graphWidth, gy); ctx.stroke();
                ctx.setLineDash([]);
                text(ctx, "60 dB", gx - 28, gy - graphHeight, palette.muted, 10);
                text(ctx, "0 dB", gx - 24, gy, palette.muted, 10);
                label(ctx, `RT60 = ${rt60.toFixed(2)} s`, gx + (rt60 / timeSpan) * graphWidth, gy - 24, palette.green);
                stageNote.textContent = "Sabine relation: RT60 = 0.161 V / A. This idealised decay model assumes a diffuse field and evenly distributed absorption.";
            }

            function drawPohl(ctx, width, height, time) {
                const slit = Number(state.p_slit_width);
                const wavelength = Number(state.p_wavelength);
                const angle = Math.asin(Math.min(1, wavelength / slit));
                const degrees = angle * 180 / Math.PI;
                setMetrics([
                    { label: "Slit", value: `${slit} cm` },
                    { label: "Wavelength", value: `${wavelength} cm` },
                    { label: "Beam spread", value: `${degrees.toFixed(0)} deg`, color: palette.amber },
                ]);
                const barrierX = width * 0.36;
                const centerY = height * 0.5;
                const opening = Math.max(20, Math.min(height * 0.48, slit * 2.2));
                ctx.fillStyle = palette.outline;
                ctx.fillRect(barrierX - 8, 0, 16, centerY - opening / 2);
                ctx.fillRect(barrierX - 8, centerY + opening / 2, 16, height - centerY - opening / 2);
                ctx.strokeStyle = palette.blueSoft;
                ctx.lineWidth = 2;
                const phase = (time * 45) % Math.max(12, wavelength);
                for (let x = phase; x < barrierX - 10; x += Math.max(12, wavelength)) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
                }
                ctx.strokeStyle = palette.blue;
                for (let radius = phase; radius < width; radius += Math.max(14, wavelength)) {
                    if (radius < 4) continue;
                    ctx.beginPath(); ctx.arc(barrierX + 8, centerY, radius, -angle, angle); ctx.stroke();
                }
                ctx.setLineDash([5, 5]);
                ctx.strokeStyle = palette.outline;
                ctx.beginPath(); ctx.moveTo(barrierX + 8, centerY - opening / 2); ctx.lineTo(width - 30, centerY - opening / 2); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(barrierX + 8, centerY + opening / 2); ctx.lineTo(width - 30, centerY + opening / 2); ctx.stroke();
                ctx.setLineDash([]);
                label(ctx, "slit", barrierX, height - 28, palette.amber);
                label(ctx, "diffracted field", width * 0.73, 36, palette.blue);
                stageNote.textContent = "Educational diffraction approximation: widening occurs as aperture width becomes small relative to wavelength.";
            }

            function drawFletcher(ctx, width, height, time) {
                const level = Number(state.f_level);
                const harmonious = level >= 60;
                setMetrics([
                    { label: "Intensity", value: `${level}%` },
                    { label: "Model response", value: harmonious ? "perceptual shift" : "discordant pair", color: harmonious ? palette.green : palette.red },
                ]);
                const centerY = height * 0.5;
                const amplitude = 8 + level * 0.62;
                ctx.strokeStyle = harmonious ? palette.green : palette.red;
                ctx.lineWidth = 2.5;
                ctx.beginPath();
                for (let x = 0; x < width; x += 2) {
                    const phase = x * 0.045 - time * 5;
                    const y = centerY + Math.sin(phase * 1.68) * amplitude * 0.5 + Math.sin(phase * 3.18) * amplitude * 0.45;
                    if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
                }
                ctx.stroke();
                if (harmonious) {
                    ctx.strokeStyle = "rgba(52,211,153,0.3)";
                    ctx.lineWidth = 8;
                    ctx.beginPath();
                    for (let x = 0; x < width; x += 3) {
                        const y = centerY + Math.sin((x * 0.045 - time * 5) * 1.5) * amplitude * 0.7;
                        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
                    }
                    ctx.stroke();
                }
                label(ctx, harmonious ? "subjective octave relation model" : "fixed physical tone pair", width / 2, 34, harmonious ? palette.green : palette.red);
                stageNote.textContent = "This visualises an historical psychoacoustic observation: perceived pitch relation can change with sound level while the source frequencies remain fixed.";
            }

            function drawHaas(ctx, width, height, time) {
                const delay = Number(state.ha_delay);
                const perception = delay === 0 ? "center image" : delay <= 35 ? "fused at direct source" : "separate echo";
                const color = delay === 0 ? palette.amber : delay <= 35 ? palette.blue : palette.red;
                setMetrics([
                    { label: "Delay", value: `${delay} ms` },
                    { label: "Perception", value: perception, color },
                ]);
                const leftX = width * 0.22;
                const rightX = width * 0.78;
                const speakerY = height * 0.23;
                const listenerX = width * 0.5;
                const listenerY = height * 0.76;
                ctx.fillStyle = palette.blue; ctx.fillRect(leftX - 20, speakerY - 26, 40, 52);
                ctx.fillStyle = palette.red; ctx.fillRect(rightX - 20, speakerY - 26, 40, 52);
                ctx.fillStyle = palette.amber; ctx.beginPath(); ctx.arc(listenerX, listenerY, 18, 0, Math.PI * 2); ctx.fill();
                const pulse = (time * 135) % 230;
                ctx.strokeStyle = "rgba(96,165,250,0.5)"; ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(leftX, speakerY, pulse, 0, Math.PI * 2); ctx.stroke();
                if (delay === 0 || time > delay / 1000) {
                    ctx.strokeStyle = "rgba(251,113,133,0.5)";
                    ctx.beginPath(); ctx.arc(rightX, speakerY, Math.max(0, pulse - delay * 1.6), 0, Math.PI * 2); ctx.stroke();
                }
                ctx.fillStyle = color;
                if (delay === 0) ctx.beginPath(), ctx.arc(listenerX, speakerY + 38, 12, 0, Math.PI * 2), ctx.fill();
                else if (delay <= 35) ctx.beginPath(), ctx.arc(leftX, speakerY + 38, 12, 0, Math.PI * 2), ctx.fill();
                else { ctx.beginPath(); ctx.arc(leftX, speakerY + 38, 8, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.arc(rightX, speakerY + 38, 8, 0, Math.PI * 2); ctx.fill(); }
                label(ctx, "direct", leftX, speakerY - 44, palette.blue);
                label(ctx, "delayed", rightX, speakerY - 44, palette.red);
                label(ctx, "listener", listenerX, listenerY + 34, palette.amber);
                stageNote.textContent = "The precedence region is simplified here: early arrivals can fuse while strongly influencing apparent direction.";
            }

            function drawFranssen(ctx, width, height, now) {
                const elapsed = franssenStartedAt === null ? 0 : Math.min(7, (now - franssenStartedAt) / 1000);
                const leftLevel = elapsed < 2 ? 1 : elapsed < 4 ? 1 - (elapsed - 2) / 2 : 0;
                const rightLevel = elapsed < 2 ? 0 : elapsed < 4 ? (elapsed - 2) / 2 : 1;
                const actual = elapsed === 0 ? "ready" : elapsed < 2 ? "left source" : elapsed < 4 ? "crossfade" : "right source";
                setMetrics([
                    { label: "Actual source", value: actual },
                    { label: "Perceived source", value: "left onset cue", color: palette.amber },
                ]);
                const leftX = width * 0.25;
                const rightX = width * 0.75;
                const speakerY = height * 0.48;
                const listenerY = height * 0.78;
                ctx.fillStyle = palette.blue; ctx.globalAlpha = Math.max(0.18, leftLevel); ctx.fillRect(leftX - 22, speakerY - 28, 44, 56);
                ctx.fillStyle = palette.green; ctx.globalAlpha = Math.max(0.18, rightLevel); ctx.fillRect(rightX - 22, speakerY - 28, 44, 56); ctx.globalAlpha = 1;
                const radius = ((now / 12) % 130) + 10;
                ctx.strokeStyle = `rgba(96,165,250,${leftLevel * 0.65})`; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(leftX, speakerY, radius, 0, Math.PI * 2); ctx.stroke();
                ctx.strokeStyle = `rgba(52,211,153,${rightLevel * 0.65})`; ctx.beginPath(); ctx.arc(rightX, speakerY, radius, 0, Math.PI * 2); ctx.stroke();
                ctx.fillStyle = palette.amber; ctx.beginPath(); ctx.arc(width * 0.5, listenerY, 18, 0, Math.PI * 2); ctx.fill();
                label(ctx, "perceived direction", leftX, speakerY - 52, palette.amber);
                label(ctx, "listener", width * 0.5, listenerY + 34, palette.amber);
                stageNote.textContent = "Press Play crossfade to run a conceptual Franssen-effect sequence. Onset and auditory memory are represented, not reproduced acoustically.";
            }

            function drawSchroeder(ctx, width, height) {
                const prime = Number(state.sc_prime);
                setMetrics([
                    { label: "Prime", value: String(prime) },
                    { label: "Pattern", value: "quadratic residues", color: palette.green },
                ]);
                const startX = width * 0.1;
                const baseline = height * 0.78;
                const availableWidth = width * 0.8;
                const cellWidth = availableWidth / prime;
                const maxDepth = height * 0.42;
                for (let index = 0; index < prime; index += 1) {
                    const residue = (index * index) % prime;
                    const depth = (residue / Math.max(1, prime - 1)) * maxDepth;
                    ctx.fillStyle = "#172033";
                    ctx.strokeStyle = palette.outline;
                    ctx.lineWidth = 1.5;
                    ctx.fillRect(startX + index * cellWidth, baseline - depth, cellWidth, depth);
                    ctx.strokeRect(startX + index * cellWidth, baseline - depth, cellWidth, depth);
                }
                const originX = width * 0.5;
                const originY = baseline - maxDepth - 24;
                ctx.strokeStyle = palette.blue; ctx.lineWidth = 3;
                ctx.beginPath(); ctx.moveTo(originX, 28); ctx.lineTo(originX, originY); ctx.stroke();
                ctx.fillStyle = palette.blue; ctx.beginPath(); ctx.moveTo(originX, originY + 10); ctx.lineTo(originX - 7, originY - 3); ctx.lineTo(originX + 7, originY - 3); ctx.fill();
                ctx.strokeStyle = "rgba(251,113,133,0.72)"; ctx.lineWidth = 2; ctx.setLineDash([5, 5]);
                for (let angle = 25; angle <= 155; angle += 25) {
                    const radians = angle * Math.PI / 180;
                    ctx.beginPath(); ctx.moveTo(originX, originY); ctx.lineTo(originX + Math.cos(radians) * 135, originY - Math.sin(radians) * 135); ctx.stroke();
                }
                ctx.setLineDash([]);
                label(ctx, "incident energy", originX, 20, palette.blue);
                label(ctx, "QRD well profile", width * 0.5, baseline + 28, palette.green);
                stageNote.textContent = "Well depths use n² mod p as a visual sequence. Physical diffuser performance depends on dimensions, bandwidth, and construction.";
            }

            function drawHeaney(ctx, width, height) {
                const sourceDepth = Number(state.he_depth);
                const channelDepth = 700;
                setMetrics([
                    { label: "Source", value: `${sourceDepth} fathoms` },
                    { label: "Channel", value: `${channelDepth} fathoms`, color: palette.blue },
                ]);
                const channelY = (channelDepth / 2000) * height;
                const sourceY = (sourceDepth / 2000) * height;
                const gradient = context.createLinearGradient(0, 0, 0, height);
                gradient.addColorStop(0, "rgba(96,165,250,0.12)");
                gradient.addColorStop(1, "rgba(15,23,42,0)");
                ctx.fillStyle = gradient; ctx.fillRect(0, 0, width, height);
                ctx.strokeStyle = palette.blue; ctx.lineWidth = 2; ctx.setLineDash([6, 5]);
                ctx.beginPath(); ctx.moveTo(0, channelY); ctx.lineTo(width, channelY); ctx.stroke(); ctx.setLineDash([]);
                for (let ray = -4; ray <= 4; ray += 1) {
                    ctx.strokeStyle = "rgba(251,113,133,0.55)";
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    for (let x = 0; x <= width - 46; x += 4) {
                        const envelope = (sourceY - channelY) * Math.cos((x / (width - 46)) * Math.PI * (1.25 + Math.abs(ray) * 0.12));
                        const y = channelY + envelope + ray * 10 * Math.sin((x / width) * Math.PI);
                        if (x === 0) ctx.moveTo(44 + x, y); else ctx.lineTo(44 + x, y);
                    }
                    ctx.stroke();
                }
                ctx.fillStyle = palette.amber; ctx.beginPath(); ctx.arc(40, sourceY, 8, 0, Math.PI * 2); ctx.fill();
                label(ctx, "source", 40, sourceY - 20, palette.amber);
                label(ctx, "minimum-speed channel", width * 0.58, channelY - 16, palette.blue);
                stageNote.textContent = "A conceptual ray picture of deep-ocean refraction around a minimum-sound-speed channel; it is not an ocean propagation solver.";
            }

            function drawOlive(ctx, width, height) {
                const delay = Number(state.ol_delay);
                const level = Number(state.ol_level);
                const spaciousThreshold = -20 - delay * 0.18;
                const broadeningThreshold = -10 - delay * 0.24;
                const echoThreshold = -delay * 0.18;
                let zone = "inaudible";
                let color = palette.muted;
                if (level > echoThreshold) { zone = "discrete echo"; color = palette.red; }
                else if (level > broadeningThreshold) { zone = "image broadening"; color = palette.amber; }
                else if (level > spaciousThreshold) { zone = "spaciousness"; color = palette.green; }
                setMetrics([
                    { label: "Delay", value: `${delay} ms` },
                    { label: "Level", value: `${level} dB` },
                    { label: "Model zone", value: zone, color },
                ]);
                const gx = 58;
                const gy = height - 54;
                const graphWidth = width - 92;
                const graphHeight = height - 112;
                ctx.strokeStyle = palette.outline; ctx.lineWidth = 1;
                ctx.strokeRect(gx, gy - graphHeight, graphWidth, graphHeight);
                const drawBoundary = (fn, lineColor) => {
                    ctx.strokeStyle = lineColor; ctx.lineWidth = 2; ctx.beginPath();
                    for (let d = 0; d <= 80; d += 2) {
                        const x = gx + (d / 80) * graphWidth;
                        const y = gy - ((fn(d) + 40) / 50) * graphHeight;
                        if (d === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
                    }
                    ctx.stroke();
                };
                drawBoundary((d) => -20 - d * 0.18, palette.green);
                drawBoundary((d) => -10 - d * 0.24, palette.amber);
                drawBoundary((d) => -d * 0.18, palette.red);
                const px = gx + (delay / 80) * graphWidth;
                const py = gy - ((level + 40) / 50) * graphHeight;
                ctx.fillStyle = color; ctx.beginPath(); ctx.arc(px, py, 8, 0, Math.PI * 2); ctx.fill();
                label(ctx, zone, px, py - 22, color);
                text(ctx, "delay", gx + graphWidth / 2, gy + 28, palette.muted, 10);
                text(ctx, "level", 24, gy - graphHeight / 2, palette.muted, 10);
                stageNote.textContent = "Educational delay-versus-level map inspired by lateral-reflection research. Audible thresholds vary with programme material, room, and listener.";
            }

            function drawDavis(ctx, width, height) {
                const lede = Boolean(state.d_lede);
                const condition = lede ? "reflection-free front / diffuse rear" : "strong early lateral returns";
                setMetrics([
                    { label: "Room mode", value: lede ? "LEDE" : "untreated" },
                    { label: "Listening condition", value: condition, color: lede ? palette.green : palette.red },
                ]);
                const roomX = width * 0.16;
                const roomY = height * 0.18;
                const roomWidth = width * 0.68;
                const roomHeight = height * 0.58;
                ctx.strokeStyle = palette.outline; ctx.lineWidth = 4; ctx.strokeRect(roomX, roomY, roomWidth, roomHeight);
                if (lede) {
                    ctx.fillStyle = "rgba(96,165,250,0.14)"; ctx.fillRect(roomX, roomY, roomWidth * 0.43, roomHeight);
                    ctx.strokeStyle = palette.amber; ctx.lineWidth = 3;
                    for (let y = roomY + 10; y < roomY + roomHeight - 10; y += 30) {
                        ctx.beginPath(); ctx.moveTo(roomX + roomWidth, y); ctx.lineTo(roomX + roomWidth - 18, y + 13); ctx.lineTo(roomX + roomWidth, y + 26); ctx.stroke();
                    }
                }
                const speakerX = roomX + 38;
                const speakerY1 = roomY + roomHeight * 0.32;
                const speakerY2 = roomY + roomHeight * 0.68;
                const listenerX = roomX + roomWidth * 0.61;
                const listenerY = roomY + roomHeight * 0.5;
                ctx.fillStyle = palette.text; ctx.fillRect(speakerX - 10, speakerY1 - 10, 20, 20); ctx.fillRect(speakerX - 10, speakerY2 - 10, 20, 20);
                ctx.fillStyle = palette.blue; ctx.beginPath(); ctx.arc(listenerX, listenerY, 13, 0, Math.PI * 2); ctx.fill();
                if (!lede) {
                    ctx.strokeStyle = "rgba(251,113,133,0.82)"; ctx.lineWidth = 2.5;
                    ctx.beginPath(); ctx.moveTo(speakerX, speakerY1); ctx.lineTo(roomX + roomWidth * 0.48, roomY); ctx.lineTo(listenerX, listenerY); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(speakerX, speakerY2); ctx.lineTo(roomX + roomWidth * 0.48, roomY + roomHeight); ctx.lineTo(listenerX, listenerY); ctx.stroke();
                    label(ctx, "early lateral reflections", roomX + roomWidth * 0.48, roomY - 22, palette.red);
                } else {
                    ctx.strokeStyle = "rgba(251,191,36,0.45)"; ctx.lineWidth = 2;
                    for (let offset = -2; offset <= 2; offset += 1) {
                        ctx.beginPath(); ctx.moveTo(speakerX, speakerY1); ctx.lineTo(roomX + roomWidth, listenerY + offset * 22); ctx.lineTo(listenerX, listenerY); ctx.stroke();
                    }
                    label(ctx, "absorptive front", roomX + roomWidth * 0.22, roomY - 22, palette.blue);
                    label(ctx, "diffuse rear", roomX + roomWidth * 0.83, roomY - 22, palette.amber);
                }
                label(ctx, "listener", listenerX, listenerY + 30, palette.blue);
                stageNote.textContent = "Conceptual LEDE layout: an absorptive early-reflection zone is paired with later, more diffuse energy at the rear of the room.";
            }

            function drawFrame(timestamp) {
                const delta = Math.min((timestamp - lastTimestamp) / 1000, 0.05);
                lastTimestamp = timestamp;
                if (canvasWidth < 1 || canvasHeight < 1) {
                    window.requestAnimationFrame(drawFrame);
                    return;
                }
                drawGrid(context, canvasWidth, canvasHeight);
                const experiment = currentExperiment();
                if (experiment.id === "helmholtz") drawHelmholtz(context, canvasWidth, canvasHeight, timestamp / 1000);
                else if (experiment.id === "sabine") drawSabine(context, canvasWidth, canvasHeight);
                else if (experiment.id === "pohl") drawPohl(context, canvasWidth, canvasHeight, timestamp / 1000);
                else if (experiment.id === "fletcher") drawFletcher(context, canvasWidth, canvasHeight, timestamp / 1000);
                else if (experiment.id === "haas") drawHaas(context, canvasWidth, canvasHeight, timestamp / 1000);
                else if (experiment.id === "franssen") drawFranssen(context, canvasWidth, canvasHeight, timestamp);
                else if (experiment.id === "schroeder") drawSchroeder(context, canvasWidth, canvasHeight);
                else if (experiment.id === "heaney") drawHeaney(context, canvasWidth, canvasHeight);
                else if (experiment.id === "olive") drawOlive(context, canvasWidth, canvasHeight);
                else if (experiment.id === "davis") drawDavis(context, canvasWidth, canvasHeight);
                void delta;
                window.requestAnimationFrame(drawFrame);
            }

            function renderControls() {
                const experiment = currentExperiment();
                stageTitle.textContent = `${experiment.name} | ${experiment.topic}`;
                controlNote.textContent = experiment.description;
                controlGrid.innerHTML = "";
                experiment.controls.forEach((control) => {
                    const row = document.createElement("div");
                    row.className = "control-row";
                    if (control.type === "range") {
                        const heading = document.createElement("div"); heading.className = "control-heading";
                        const labelElement = document.createElement("label"); labelElement.textContent = control.label;
                        const value = document.createElement("span"); value.className = "control-value";
                        const rangeWrap = document.createElement("div"); rangeWrap.className = "range-wrap";
                        const range = document.createElement("input"); range.type = "range"; range.min = control.min; range.max = control.max; range.step = control.step; range.value = state[control.key];
                        const number = document.createElement("input"); number.className = "number-input"; number.type = "number"; number.min = control.min; number.max = control.max; number.step = control.step; number.value = state[control.key];
                        const renderValue = () => { value.textContent = `${state[control.key]}${control.unit ? ` ${control.unit}` : ""}`; range.value = state[control.key]; number.value = state[control.key]; };
                        const update = (next) => { state[control.key] = clamp(Number(next), control.min, control.max); renderValue(); };
                        range.addEventListener("input", () => update(range.value));
                        number.addEventListener("change", () => update(number.value));
                        renderValue();
                        heading.append(labelElement, value); rangeWrap.append(range, number); row.append(heading, rangeWrap);
                    } else if (control.type === "select") {
                        const labelElement = document.createElement("label"); labelElement.textContent = control.label;
                        const selector = document.createElement("select");
                        control.options.forEach((optionValue) => {
                            const option = document.createElement("option"); option.value = optionValue; option.textContent = optionValue; selector.appendChild(option);
                        });
                        selector.value = state[control.key];
                        selector.addEventListener("change", () => { state[control.key] = Number(selector.value); });
                        row.append(labelElement, selector);
                    } else if (control.type === "toggle") {
                        const toggleRow = document.createElement("div"); toggleRow.className = "toggle-row";
                        const labelElement = document.createElement("label"); labelElement.textContent = control.label;
                        const toggle = document.createElement("button"); toggle.className = "switch"; toggle.type = "button"; toggle.setAttribute("aria-pressed", String(Boolean(state[control.key])));
                        toggle.innerHTML = '<span class="switch-track"></span>';
                        const renderToggle = () => { toggle.classList.toggle("is-on", Boolean(state[control.key])); toggle.setAttribute("aria-pressed", String(Boolean(state[control.key]))); };
                        toggle.addEventListener("click", () => { state[control.key] = !state[control.key]; renderToggle(); });
                        renderToggle(); toggleRow.append(labelElement, toggle); row.append(toggleRow);
                    } else if (control.type === "action") {
                        const button = document.createElement("button"); button.type = "button"; button.className = "action-button"; button.textContent = control.label;
                        button.addEventListener("click", () => { if (control.action === "playFranssen") franssenStartedAt = performance.now(); });
                        row.append(button);
                    }
                    controlGrid.appendChild(row);
                });
            }

            function selectExperiment(nextId) {
                selectedId = nextId;
                franssenStartedAt = null;
                lastMetricSignature = "";
                renderControls();
            }

            select.addEventListener("change", () => selectExperiment(select.value));
            document.getElementById("reset-button").addEventListener("click", () => {
                currentExperiment().controls.forEach((control) => {
                    if (control.type !== "action") state[control.key] = defaults[control.key];
                });
                franssenStartedAt = null;
                lastMetricSignature = "";
                renderControls();
            });

            select.value = selectedId;
            renderControls();
            resizeCanvas();
            window.requestAnimationFrame(drawFrame);
        </script>
    </body>
    </html>
    """
    return markup.replace("__EXPERIMENTS__", experiments_json)