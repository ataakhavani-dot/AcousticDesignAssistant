"""Interactive historical acoustics experiment records for ADA's Digital Lab."""

from __future__ import annotations

import json

import streamlit.components.v1 as components


DIGITAL_LAB_EXPERIMENTS = (
    {
        "id": "helmholtz",
        "initials": "HH",
        "name": "Hermann von Helmholtz",
        "era": "Mid-19th century",
        "field": "Resonance",
        "accent": "#fbbf24",
        "setup": (
            "Helmholtz compared metal spheres with different cavity volumes and necks. "
            "By aiming each opening toward a sound and listening at the neck, he could "
            "isolate the energy around its resonant frequency."
        ),
        "outcome": (
            "The work established the cavity-and-neck resonator model: air in the cavity "
            "acts like a spring while air in the neck acts like a moving mass. It remains "
            "the foundation for narrow-band low-frequency absorbers."
        ),
        "principle": "Resonant frequency is set by cavity volume, neck area, and neck length.",
        "diagram": "helmholtz",
    },
    {
        "id": "sabine",
        "initials": "WS",
        "name": "Wallace C. Sabine",
        "era": "1890s",
        "field": "Reverberation",
        "accent": "#a3e635",
        "setup": (
            "Sabine used a controlled sound source, organ pipes, a stopwatch, and careful "
            "listening in two lecture halls. He changed the amount of absorptive seating "
            "material and measured how long sound took to become inaudible."
        ),
        "outcome": (
            "He demonstrated the connection between room volume, surface absorption, and "
            "decay time. The resulting Sabine relation gave architects a practical way to "
            "estimate reverberation before a room was built."
        ),
        "principle": "More equivalent absorption shortens the room's reverberation time.",
        "diagram": "sabine",
    },
    {
        "id": "pohl",
        "initials": "RP",
        "name": "R. W. Pohl",
        "era": "Early 20th century",
        "field": "Diffraction",
        "accent": "#fb7185",
        "setup": (
            "Pohl sent a high-frequency test sound through a narrow slit and mapped level "
            "against angle using a detector at a distance. The slit width was varied against "
            "the sound wavelength."
        ),
        "outcome": (
            "The measured beam widened beyond simple geometric rays, demonstrating acoustic "
            "diffraction. The comparison made clear that a narrower aperture produces more "
            "spreading for a given wavelength."
        ),
        "principle": "Diffraction increases as aperture width becomes small relative to wavelength.",
        "diagram": "pohl",
    },
    {
        "id": "fletcher",
        "initials": "HF",
        "name": "Harvey Fletcher",
        "era": "1933",
        "field": "Psychoacoustics",
        "accent": "#c084fc",
        "setup": (
            "Fletcher compared two tones at 168 Hz and 318 Hz while changing level. Listeners "
            "reported how the interval and consonance changed as the playback level rose."
        ),
        "outcome": (
            "The study illustrated that perceived pitch and musical relation can shift with "
            "level even when physical frequencies do not. It helped separate measurable "
            "frequency from the listener's subjective pitch experience."
        ),
        "principle": "Perceived pitch is level-dependent; frequency is a fixed physical quantity.",
        "diagram": "fletcher",
    },
    {
        "id": "haas",
        "initials": "HH",
        "name": "Helmut Haas",
        "era": "1951",
        "field": "Localization",
        "accent": "#60a5fa",
        "setup": (
            "Listeners heard identical speech from two loudspeakers under near-anechoic "
            "conditions. One signal was delayed while source angle and level were held under "
            "control."
        ),
        "outcome": (
            "For short delays, listeners fused the signals and located the event at the "
            "undelayed source. This precedence effect is central to sound reinforcement, "
            "stereo imaging, and early-reflection design."
        ),
        "principle": "The first arriving wavefront strongly controls perceived source direction.",
        "diagram": "haas",
    },
    {
        "id": "franssen",
        "initials": "NF",
        "name": "Nico Franssen",
        "era": "Mid-20th century",
        "field": "Auditory memory",
        "accent": "#34d399",
        "setup": (
            "A tone began at one loudspeaker, then crossfaded to another at equal overall "
            "level. Listeners were asked where the sound appeared to remain while the first "
            "source faded away."
        ),
        "outcome": (
            "Many listeners continued to hear the signal at the original source even when "
            "the second loudspeaker carried the sound. The Franssen effect highlights how "
            "onset cues and auditory memory dominate localization."
        ),
        "principle": "A stable onset cue can outweigh later level changes in perceived location.",
        "diagram": "franssen",
    },
    {
        "id": "schroeder",
        "initials": "MS",
        "name": "Manfred R. Schroeder",
        "era": "1970s",
        "field": "Diffusion",
        "accent": "#f97316",
        "setup": (
            "Schroeder tested surfaces whose well depths followed number sequences and were "
            "scaled to wavelength. The reflected pattern was compared with a simple flat, "
            "specular surface."
        ),
        "outcome": (
            "The sequence distributed reflected energy across a broad angle instead of a "
            "single mirror-like direction. This work led directly to practical QRD and MLS "
            "diffusers used in studios and halls."
        ),
        "principle": "Sequence-controlled well depths spread reflected energy over angle and time.",
        "diagram": "schroeder",
    },
)


def render_digital_lab() -> None:
    """Render the ADA-styled, selectable historical-experiments lab."""
    components.html(_build_digital_lab_html(), height=860, scrolling=False)


def _build_digital_lab_html() -> str:
    experiments_json = json.dumps(DIGITAL_LAB_EXPERIMENTS)
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {{
                color-scheme: dark;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                background: transparent;
                color: #e2e8f0;
                margin: 0;
                overflow: hidden;
            }}
            button {{ font: inherit; }}
            .digital-lab {{
                background: #111827;
                border: 1px solid #334155;
                border-radius: 8px;
                height: 858px;
                overflow-y: auto;
                padding: 20px;
                scrollbar-color: #475569 #111827;
            }}
            .lab-heading {{
                align-items: end;
                border-bottom: 1px solid #334155;
                display: flex;
                justify-content: space-between;
                gap: 20px;
                margin-bottom: 18px;
                padding-bottom: 16px;
            }}
            .eyebrow {{
                color: #60a5fa;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.11em;
                margin: 0 0 5px;
            }}
            h1 {{
                color: #f8fafc;
                font-size: 24px;
                line-height: 1.15;
                margin: 0;
            }}
            .heading-copy {{
                color: #94a3b8;
                font-size: 13px;
                line-height: 1.45;
                margin: 7px 0 0;
                max-width: 620px;
            }}
            .record-count {{
                background: #172033;
                border: 1px solid #475569;
                border-radius: 999px;
                color: #cbd5e1;
                font-size: 11px;
                font-weight: 700;
                padding: 7px 10px;
                white-space: nowrap;
            }}
            .lab-layout {{
                display: grid;
                gap: 16px;
                grid-template-columns: minmax(190px, 0.7fr) minmax(0, 2.3fr);
            }}
            .experiment-index {{
                background: #172033;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px;
            }}
            .index-title {{
                color: #94a3b8;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.08em;
                margin: 7px 8px 8px;
            }}
            .experiment-selector {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                color: #cbd5e1;
                cursor: pointer;
                display: grid;
                gap: 9px;
                grid-template-columns: 25px minmax(0, 1fr);
                padding: 10px 8px;
                text-align: left;
                width: 100%;
            }}
            .experiment-selector:hover {{ background: #1e293b; }}
            .experiment-selector.is-selected {{
                background: #0f2744;
                border-color: #2563eb;
            }}
            .selector-number {{
                color: var(--accent);
                font-size: 11px;
                font-weight: 800;
                padding-top: 1px;
            }}
            .selector-name {{
                color: #f8fafc;
                display: block;
                font-size: 12px;
                font-weight: 700;
                line-height: 1.2;
            }}
            .selector-field {{
                color: #94a3b8;
                display: block;
                font-size: 10px;
                margin-top: 3px;
            }}
            .experiment-record {{
                background: #172033;
                border: 1px solid #334155;
                border-radius: 8px;
                min-width: 0;
                overflow: hidden;
            }}
            .record-header {{
                align-items: center;
                background: #0f172a;
                border-bottom: 1px solid #334155;
                display: flex;
                gap: 13px;
                padding: 16px;
            }}
            .researcher-mark {{
                align-items: center;
                background: var(--accent);
                border: 3px solid #f8fafc;
                border-radius: 50%;
                color: #0f172a;
                display: flex;
                flex: 0 0 auto;
                font-size: 13px;
                font-weight: 900;
                height: 54px;
                justify-content: center;
                letter-spacing: 0.04em;
                width: 54px;
            }}
            .record-title {{
                color: #f8fafc;
                font-size: 20px;
                line-height: 1.15;
                margin: 0;
            }}
            .record-era {{
                color: #94a3b8;
                font-size: 12px;
                margin: 4px 0 0;
            }}
            .field-tag {{
                border: 1px solid var(--accent);
                border-radius: 999px;
                color: var(--accent);
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.05em;
                margin-left: auto;
                padding: 6px 9px;
                text-transform: uppercase;
                white-space: nowrap;
            }}
            .record-body {{
                display: grid;
                gap: 16px;
                grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
                padding: 16px;
            }}
            .record-copy {{ display: grid; gap: 14px; }}
            .copy-label {{
                color: #60a5fa;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.09em;
                margin: 0 0 5px;
            }}
            .copy-text {{
                color: #cbd5e1;
                font-size: 13px;
                line-height: 1.55;
                margin: 0;
            }}
            .principle {{
                background: #0f2744;
                border-left: 3px solid var(--accent);
                color: #dbeafe;
                font-size: 12px;
                line-height: 1.45;
                padding: 10px 12px;
            }}
            .principle strong {{ color: #f8fafc; }}
            .schematic-card {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 7px;
                min-height: 282px;
                overflow: hidden;
                padding: 13px;
            }}
            .schematic-title {{
                color: #94a3b8;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.08em;
                margin: 0 0 8px;
            }}
            .schematic {{ height: 225px; width: 100%; }}
            .lab-footer {{
                align-items: center;
                border-top: 1px solid #334155;
                display: flex;
                justify-content: space-between;
                gap: 12px;
                padding: 12px 16px;
            }}
            .lab-note {{
                color: #64748b;
                font-size: 11px;
                line-height: 1.4;
                margin: 0;
            }}
            .record-controls {{ display: flex; gap: 7px; }}
            .record-control {{
                background: #1e293b;
                border: 1px solid #475569;
                border-radius: 6px;
                color: #cbd5e1;
                cursor: pointer;
                font-size: 11px;
                font-weight: 700;
                padding: 7px 10px;
            }}
            .record-control:hover {{ border-color: #60a5fa; color: #f8fafc; }}
            svg text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
            @media (max-width: 760px) {{
                .digital-lab {{ height: 858px; min-height: 0; padding: 14px; }}
                .lab-heading {{ align-items: start; flex-direction: column; }}
                .lab-layout {{ grid-template-columns: 1fr; }}
                .experiment-index {{
                    display: flex;
                    gap: 6px;
                    overflow-x: auto;
                    padding: 7px;
                }}
                #experiment-list {{
                    display: flex;
                    gap: 6px;
                }}
                .index-title {{ display: none; }}
                .experiment-selector {{
                    flex: 0 0 160px;
                    grid-template-columns: 22px minmax(0, 1fr);
                }}
                .record-body {{ grid-template-columns: 1fr; }}
                .field-tag {{ margin-left: 0; }}
                .record-header {{ align-items: start; flex-wrap: wrap; }}
                .schematic {{ height: 210px; }}
            }}
        </style>
    </head>
    <body>
        <main class="digital-lab">
            <header class="lab-heading">
                <div>
                    <p class="eyebrow">DIGITAL LAB</p>
                    <h1>Historical acoustics experiments</h1>
                    <p class="heading-copy">Explore the physical demonstrations that shaped modern resonance, reverberation, localization, and diffusion practice.</p>
                </div>
                <span class="record-count" id="record-count"></span>
            </header>
            <div class="lab-layout">
                <nav class="experiment-index" aria-label="Historical experiment records">
                    <p class="index-title">EXPERIMENT RECORDS</p>
                    <div id="experiment-list"></div>
                </nav>
                <section class="experiment-record" id="experiment-record" aria-live="polite"></section>
            </div>
        </main>
        <script>
            const experiments = {experiments_json};
            const experimentList = document.getElementById("experiment-list");
            const experimentRecord = document.getElementById("experiment-record");
            let selectedIndex = 0;

            document.getElementById("record-count").textContent = `${{experiments.length}} historical records`;

            const schematic = (kind, accent) => {{
                const base = `viewBox="0 0 520 250" role="img" aria-label="Conceptual experiment schematic"`;
                const label = (x, y, text, color = "#94a3b8", size = 11) =>
                    `<text x="${{x}}" y="${{y}}" fill="${{color}}" font-size="${{size}}" text-anchor="middle">${{text}}</text>`;
                const wave = (x, y, width, color = "#60a5fa") =>
                    `<path d="M ${{x}} ${{y}} q 14 -14 28 0 t 28 0 t 28 0 t 28 0" fill="none" stroke="${{color}}" stroke-width="2.5"/>`;

                if (kind === "helmholtz") return `
                    <svg class="schematic" ${{base}}>
                        ${{wave(24, 76)}}${{wave(24, 102)}}${{wave(24, 128)}}
                        ${{label(88, 165, "incident sound")}}
                        <path d="M250 35 a75 75 0 1 1 0 150 a75 75 0 1 1 0 -150" fill="#172033" stroke="#94a3b8" stroke-width="5"/>
                        <path d="M145 93 h58 M145 127 h58" stroke="#94a3b8" stroke-width="5"/>
                        <circle cx="278" cy="110" r="38" fill="${{accent}}" opacity="0.18"/>
                        <circle cx="278" cy="110" r="24" fill="${{accent}}" opacity="0.35"/>
                        ${{label(278, 114, "resonance", accent, 13)}}
                        <path d="M416 84 q22 -24 33 1 q10 30 -15 43" fill="none" stroke="#fbbf24" stroke-width="4"/>
                        ${{label(431, 165, "listener")}}
                    </svg>`;
                if (kind === "sabine") return `
                    <svg class="schematic" ${{base}}>
                        <rect x="20" y="22" width="480" height="188" rx="7" fill="#172033" stroke="#475569" stroke-dasharray="7 6" stroke-width="2"/>
                        <path d="M65 151 v-70 h30 v70 M65 81 l15 -25 l15 25" fill="#60a5fa" stroke="#60a5fa" stroke-width="2"/>
                        ${{wave(112, 102)}}${{wave(112, 132)}}
                        <rect x="227" y="160" width="58" height="25" rx="5" fill="#34d399"/>
                        <rect x="300" y="160" width="58" height="25" rx="5" fill="#34d399"/>
                        <circle cx="425" cy="105" r="21" fill="#fbbf24"/>
                        <circle cx="394" cy="145" r="14" fill="#fb7185"/>
                        <path d="M394 145 v-9" stroke="#f8fafc" stroke-width="2"/>
                        ${{label(80, 198, "sound source")}}${{label(293, 204, "absorption samples")}}${{label(418, 198, "listener + timer")}}
                    </svg>`;
                if (kind === "pohl") return `
                    <svg class="schematic" ${{base}}>
                        <circle cx="52" cy="124" r="15" fill="#60a5fa"/>
                        <path d="M79 124 h88" stroke="#94a3b8" stroke-dasharray="6 5" stroke-width="3"/>
                        <path d="M185 30 v75 M185 145 v75" stroke="#94a3b8" stroke-width="12"/>
                        <path d="M198 122 q95 -78 202 -72 M198 124 h220 M198 126 q95 78 202 72" fill="none" stroke="${{accent}}" stroke-width="3"/>
                        <path d="M198 89 h205 M198 159 h205" stroke="#475569" stroke-dasharray="6 5" stroke-width="2"/>
                        <path d="M444 50 q39 73 0 146" fill="none" stroke="#34d399" stroke-width="4"/>
                        ${{label(52, 165, "source")}}${{label(185, 236, "slit")}}${{label(327, 28, "diffracted field", accent)}}${{label(452, 225, "detector")}}
                    </svg>`;
                if (kind === "fletcher") return `
                    <svg class="schematic" ${{base}}>
                        <rect x="24" y="36" width="190" height="155" rx="7" fill="#172033" stroke="#475569"/>
                        <rect x="306" y="36" width="190" height="155" rx="7" fill="#172033" stroke="#475569"/>
                        ${{label(119, 61, "low level", "#cbd5e1", 13)}}${{label(401, 61, "high level", "#cbd5e1", 13)}}
                        <path d="M40 120 q10 -17 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="#60a5fa" stroke-width="2"/>
                        <path d="M322 120 q10 -52 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="#60a5fa" stroke-width="4"/>
                        <path d="M234 113 h48" stroke="#94a3b8" stroke-width="3"/><path d="M274 105 l12 8 l-12 8" fill="#94a3b8"/>
                        ${{label(119, 168, "reported: discordant", "#fb7185")}}${{label(401, 168, "reported: more consonant", "#34d399")}}
                    </svg>`;
                if (kind === "haas") return `
                    <svg class="schematic" ${{base}}>
                        <rect x="70" y="38" width="42" height="58" rx="4" fill="#60a5fa"/>
                        <rect x="408" y="38" width="42" height="58" rx="4" fill="#fb7185"/>
                        <circle cx="260" cy="185" r="22" fill="#fbbf24"/>
                        <path d="M112 96 L238 168" stroke="#60a5fa" stroke-dasharray="7 5" stroke-width="4"/>
                        <path d="M408 96 L282 168" stroke="#fb7185" stroke-dasharray="3 7" stroke-width="4"/>
                        ${{label(92, 27, "direct")}}${{label(430, 27, "delayed")}}${{label(260, 229, "listener")}}
                        ${{label(168, 137, "first arrival", "#60a5fa")}}${{label(352, 137, "later arrival", "#fb7185")}}
                    </svg>`;
                if (kind === "franssen") return `
                    <svg class="schematic" ${{base}}>
                        <rect x="70" y="38" width="42" height="58" rx="4" fill="#64748b"/>
                        <rect x="408" y="38" width="42" height="58" rx="4" fill="#34d399"/>
                        <circle cx="260" cy="185" r="22" fill="#fbbf24"/>
                        <path d="M112 96 L238 168" stroke="#60a5fa" stroke-width="5"/>
                        <path d="M408 96 L282 168" stroke="#34d399" stroke-dasharray="4 5" stroke-width="3"/>
                        <path d="M150 124 q40 -45 77 -2" fill="none" stroke="#60a5fa" stroke-width="2"/>
                        ${{label(92, 27, "faded out")}}${{label(430, 27, "faded in", "#34d399")}}${{label(260, 229, "listener")}}
                        ${{label(165, 151, "remembered location", "#60a5fa")}}
                    </svg>`;
                return `
                    <svg class="schematic" ${{base}}>
                        <path d="M55 205 h35 v-55 h32 v55 h34 v-92 h32 v92 h34 v-35 h32 v35 h34 v-75 h32 v75 h34 v-48 h32 v48" fill="none" stroke="#94a3b8" stroke-width="7"/>
                        <path d="M260 28 v88" stroke="#60a5fa" stroke-width="4"/><path d="M252 105 l8 14 l8 -14" fill="#60a5fa"/>
                        <path d="M260 140 L103 52 M260 140 L182 30 M260 140 L340 30 M260 140 L440 62" stroke="${{accent}}" stroke-width="3"/>
                        ${{label(286, 35, "incident energy", "#60a5fa")}}${{label(260, 232, "sequence-controlled wells")}}${{label(406, 49, "diffused reflections", accent)}}
                    </svg>`;
            }};

            const renderIndex = () => {{
                experimentList.innerHTML = "";
                experiments.forEach((experiment, index) => {{
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = `experiment-selector${{index === selectedIndex ? " is-selected" : ""}}`;
                    button.style.setProperty("--accent", experiment.accent);
                    button.setAttribute("aria-current", index === selectedIndex ? "true" : "false");
                    button.innerHTML = `
                        <span class="selector-number">${{String(index + 1).padStart(2, "0")}}</span>
                        <span><span class="selector-name">${{experiment.name}}</span><span class="selector-field">${{experiment.field}}</span></span>
                    `;
                    button.addEventListener("click", () => {{ selectedIndex = index; render(); }});
                    experimentList.appendChild(button);
                }});
            }};

            const renderRecord = () => {{
                const experiment = experiments[selectedIndex];
                experimentRecord.style.setProperty("--accent", experiment.accent);
                experimentRecord.innerHTML = `
                    <header class="record-header">
                        <div class="researcher-mark">${{experiment.initials}}</div>
                        <div>
                            <h2 class="record-title">${{experiment.name}}</h2>
                            <p class="record-era">${{experiment.era}}</p>
                        </div>
                        <span class="field-tag">${{experiment.field}}</span>
                    </header>
                    <div class="record-body">
                        <div class="record-copy">
                            <section>
                                <p class="copy-label">EXPERIMENTAL SETUP</p>
                                <p class="copy-text">${{experiment.setup}}</p>
                            </section>
                            <section>
                                <p class="copy-label">WHAT IT ESTABLISHED</p>
                                <p class="copy-text">${{experiment.outcome}}</p>
                            </section>
                            <aside class="principle"><strong>Working principle:</strong> ${{experiment.principle}}</aside>
                        </div>
                        <section class="schematic-card">
                            <p class="schematic-title">CONCEPTUAL SCHEMATIC</p>
                            ${{schematic(experiment.diagram, experiment.accent)}}
                        </section>
                    </div>
                    <footer class="lab-footer">
                        <p class="lab-note">Historical summary for learning. Diagrams are conceptual reconstructions, not to scale.</p>
                        <div class="record-controls">
                            <button class="record-control" type="button" id="previous-record">Previous</button>
                            <button class="record-control" type="button" id="next-record">Next</button>
                        </div>
                    </footer>
                `;
                document.getElementById("previous-record").addEventListener("click", () => {{
                    selectedIndex = (selectedIndex - 1 + experiments.length) % experiments.length;
                    render();
                }});
                document.getElementById("next-record").addEventListener("click", () => {{
                    selectedIndex = (selectedIndex + 1) % experiments.length;
                    render();
                }});
            }};

            const render = () => {{
                renderIndex();
                renderRecord();
            }};
            render();
        </script>
    </body>
    </html>
    """