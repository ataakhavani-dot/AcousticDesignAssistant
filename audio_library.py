"""Reusable audio-guide catalog and carousel views for ADA."""

from __future__ import annotations

import json

import streamlit.components.v1 as components


AUDIO_GUIDES = (
    {
        "id": "room-modes",
        "topics": ("modal",),
        "number": "01",
        "duration": "12 min",
        "title": "Room Modes",
        "series": "Acoustic Fundamentals",
        "description": "How standing waves form and why they shape low-frequency response.",
        "cover": "MODES",
        "accent": "#fbbf24",
        "surface": "#7c4a03",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    },
    {
        "id": "bolt-area",
        "topics": ("modal",),
        "number": "02",
        "duration": "16 min",
        "title": "Bolt Area",
        "series": "Room Stability",
        "description": "How room proportions affect modal spacing and acoustic stability.",
        "cover": "BOLT",
        "accent": "#22d3ee",
        "surface": "#155e75",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    },
    {
        "id": "rt60-limits",
        "topics": ("rt60",),
        "number": "03",
        "duration": "15 min",
        "title": "RT60 Limits",
        "series": "Reverberation Basics",
        "description": "How decay time changes clarity, intimacy, and control-room decisions.",
        "cover": "RT60",
        "accent": "#a3e635",
        "surface": "#3f6212",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    },
    {
        "id": "absorption-strategy",
        "topics": ("rt60",),
        "number": "04",
        "duration": "11 min",
        "title": "Absorption Strategy",
        "series": "Treatment Planning",
        "description": "Choosing materials and placement without over-damping a room.",
        "cover": "ABS",
        "accent": "#34d399",
        "surface": "#065f46",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    },
    {
        "id": "sbir-effects",
        "topics": ("sbir",),
        "number": "05",
        "duration": "14 min",
        "title": "SBIR Effects",
        "series": "Speaker Placement",
        "description": "How nearby boundaries create cancellation dips in the low end.",
        "cover": "SBIR",
        "accent": "#60a5fa",
        "surface": "#1d4ed8",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    },
    {
        "id": "monitor-placement",
        "topics": ("sbir",),
        "number": "06",
        "duration": "13 min",
        "title": "Monitor Placement",
        "series": "Critical Listening",
        "description": "A practical starting point for speaker distance, symmetry, and toe-in.",
        "cover": "MON",
        "accent": "#fb7185",
        "surface": "#9f1239",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    },
)


def get_audio_guides(topic: str) -> tuple[dict[str, object], ...]:
    """Return every guide in Gallery or the guides related to one ADA topic."""
    if topic == "gallery":
        return AUDIO_GUIDES

    return tuple(guide for guide in AUDIO_GUIDES if topic in guide["topics"])


def render_audio_carousel_bar(title: str, topic: str) -> None:
    """Render a horizontally scrollable collection of audio guides for one topic."""
    guides = get_audio_guides(topic)
    html_code = _build_carousel_html(title, guides)
    components.html(html_code, height=356 if len(guides) <= 2 else 384)


def _build_carousel_html(title: str, guides: tuple[dict[str, object], ...]) -> str:
    guides_json = json.dumps(guides)
    title_json = json.dumps(title)
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <style>
            :root {{
                color-scheme: dark;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                background: transparent;
                color: #e2e8f0;
            }}
            .audio-carousel {{
                background: #111827;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 14px;
            }}
            .rail-header {{
                align-items: center;
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
            }}
            .rail-eyebrow {{
                color: #60a5fa;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.08em;
                margin: 0 0 3px;
            }}
            h2 {{
                color: #f8fafc;
                font-size: 15px;
                line-height: 1.2;
                margin: 0;
            }}
            .rail-controls {{
                display: flex;
                gap: 6px;
            }}
            .rail-control {{
                align-items: center;
                background: #1e293b;
                border: 1px solid #475569;
                border-radius: 6px;
                color: #cbd5e1;
                cursor: pointer;
                display: flex;
                font-size: 18px;
                height: 30px;
                justify-content: center;
                width: 30px;
            }}
            .rail-control:hover {{
                border-color: #60a5fa;
                color: #f8fafc;
            }}
            .rail-control:disabled {{
                color: #64748b;
                cursor: default;
                opacity: 0.55;
            }}
            .rail-control:disabled:hover {{
                border-color: #475569;
                color: #64748b;
            }}
            .audio-rail {{
                display: flex;
                gap: 12px;
                overflow-x: auto;
                padding: 2px 1px 12px;
                scroll-behavior: smooth;
                scroll-snap-type: x mandatory;
                scrollbar-color: #475569 #111827;
            }}
            .audio-rail::-webkit-scrollbar {{ height: 7px; }}
            .audio-rail::-webkit-scrollbar-thumb {{
                background: #475569;
                border-radius: 6px;
            }}
            .audio-card {{
                align-items: start;
                background: #172033;
                border: 1px solid #334155;
                border-radius: 8px;
                color: inherit;
                cursor: pointer;
                display: grid;
                flex: 0 0 min(340px, calc(100vw - 58px));
                gap: 12px;
                grid-template-columns: 76px minmax(0, 1fr);
                min-height: 126px;
                padding: 12px;
                scroll-snap-align: start;
                text-align: left;
            }}
            .audio-card:hover, .audio-card:focus-visible, .audio-card.is-playing {{
                border-color: var(--accent);
                outline: none;
            }}
            .cover {{
                align-items: center;
                background: var(--surface);
                border: 1px solid var(--accent);
                border-radius: 7px;
                color: #ffffff;
                display: flex;
                font-size: 12px;
                font-weight: 800;
                height: 76px;
                justify-content: center;
                letter-spacing: 0.06em;
                width: 76px;
            }}
            .guide-meta {{
                color: #94a3b8;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.04em;
                margin: 0 0 4px;
            }}
            .guide-title {{
                color: #f8fafc;
                font-size: 15px;
                font-weight: 700;
                line-height: 1.2;
                margin: 0;
            }}
            .guide-series {{
                color: #94a3b8;
                font-size: 11px;
                margin: 3px 0 6px;
            }}
            .guide-description {{
                color: #cbd5e1;
                display: -webkit-box;
                font-size: 11px;
                line-height: 1.35;
                margin: 0;
                overflow: hidden;
                -webkit-box-orient: vertical;
                -webkit-line-clamp: 2;
            }}
            .waveform {{
                align-items: end;
                display: flex;
                gap: 3px;
                grid-column: 1 / -1;
                height: 14px;
                margin-top: -2px;
            }}
            .waveform span {{
                background: var(--accent);
                border-radius: 2px;
                flex: 1;
                opacity: 0.55;
            }}
            .is-playing .waveform span {{
                animation: pulse 0.9s ease-in-out infinite alternate;
                opacity: 1;
            }}
            .is-playing .waveform span:nth-child(2n) {{ animation-delay: 0.18s; }}
            .is-playing .waveform span:nth-child(3n) {{ animation-delay: 0.34s; }}
            @keyframes pulse {{
                from {{ transform: scaleY(0.45); transform-origin: bottom; }}
                to {{ transform: scaleY(1); transform-origin: bottom; }}
            }}
            .player {{
                align-items: center;
                border-top: 1px solid #334155;
                display: grid;
                gap: 10px;
                grid-template-columns: minmax(0, 1fr) minmax(170px, 250px);
                margin-top: 10px;
                padding-top: 10px;
            }}
            .player-label {{
                color: #cbd5e1;
                font-size: 11px;
                font-weight: 600;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            audio {{ height: 30px; width: 100%; }}
            @media (max-width: 520px) {{
                .player {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <section class="audio-carousel" aria-label="Audio guides">
            <header class="rail-header">
                <div>
                    <p class="rail-eyebrow">AUDIO GUIDES</p>
                    <h2 id="rail-title"></h2>
                </div>
                <div class="rail-controls" aria-label="Carousel controls">
                    <button class="rail-control" id="previous" type="button" title="Previous audio guides" aria-label="Previous audio guides">&#8592;</button>
                    <button class="rail-control" id="next" type="button" title="Next audio guides" aria-label="Next audio guides">&#8594;</button>
                </div>
            </header>
            <div class="audio-rail" id="audio-rail" aria-labelledby="rail-title"></div>
            <div class="player">
                <div class="player-label" id="player-label">Audio guide</div>
                <audio id="audio-player" controls preload="none"></audio>
            </div>
        </section>
        <script>
            const guides = {guides_json};
            const title = {title_json};
            const rail = document.getElementById("audio-rail");
            const player = document.getElementById("audio-player");
            const playerLabel = document.getElementById("player-label");
            const previousButton = document.getElementById("previous");
            const nextButton = document.getElementById("next");

            document.getElementById("rail-title").textContent = title;

            const waveform = () => Array.from({{ length: 10 }}, (_, index) =>
                `<span style="height: ${{35 + ((index * 23) % 60)}}%"></span>`
            ).join("");

            const playGuide = (guide, card) => {{
                document.querySelectorAll(".audio-card").forEach((item) => item.classList.remove("is-playing"));
                card.classList.add("is-playing");
                player.src = guide.audio_url;
                playerLabel.textContent = `Now playing: ${{guide.title}}`;
                player.play().catch(() => {{}});
            }};

            guides.forEach((guide) => {{
                const card = document.createElement("button");
                card.type = "button";
                card.className = "audio-card";
                card.style.setProperty("--accent", guide.accent);
                card.style.setProperty("--surface", guide.surface);
                card.setAttribute("aria-label", `Play ${{guide.title}}`);
                card.innerHTML = `
                    <span class="cover">${{guide.cover}}</span>
                    <span>
                        <span class="guide-meta">GUIDE ${{guide.number}} · ${{guide.duration}}</span>
                        <span class="guide-title">${{guide.title}}</span>
                        <span class="guide-series">${{guide.series}}</span>
                        <span class="guide-description">${{guide.description}}</span>
                    </span>
                    <span class="waveform" aria-hidden="true">${{waveform()}}</span>
                `;
                card.addEventListener("click", () => playGuide(guide, card));
                rail.appendChild(card);
            }});

            const updateControls = () => {{
                const hasOverflow = rail.scrollWidth > rail.clientWidth + 1;
                previousButton.disabled = !hasOverflow || rail.scrollLeft <= 1;
                nextButton.disabled = !hasOverflow || rail.scrollLeft >= rail.scrollWidth - rail.clientWidth - 1;
            }};

            const scrollByCard = (direction) => {{
                rail.scrollBy({{ left: direction * Math.max(260, rail.clientWidth * 0.82), behavior: "smooth" }});
                window.setTimeout(updateControls, 350);
            }};
            previousButton.addEventListener("click", () => scrollByCard(-1));
            nextButton.addEventListener("click", () => scrollByCard(1));
            rail.addEventListener("scroll", updateControls);
            window.addEventListener("resize", updateControls);
            updateControls();
        </script>
    </body>
    </html>
    """