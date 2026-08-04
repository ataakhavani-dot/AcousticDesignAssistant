"""Streamlit presentation for the public Acoustic Atlas chat."""

from __future__ import annotations

from queue import Empty, Queue
from threading import Thread
from time import monotonic
from typing import Iterable

import streamlit as st

from acoustic_ai import (
    DEFAULT_SUGGESTED_QUESTIONS,
    MAXIMUM_CHARACTERS,
    AcousticAIError,
    build_conversation,
    build_system_prompt,
    stream_acoustic_ai,
    validate_question,
)


MESSAGES_KEY = "acoustic_atlas_messages"
SUGGESTIONS_KEY = "acoustic_atlas_suggestions"
ERROR_KEY = "acoustic_atlas_error"
THINKING_DELAY_SECONDS = 0.5
RENDER_INTERVAL_SECONDS = 0.08
POLL_INTERVAL_SECONDS = 0.03
STREAM_CHARACTERS_PER_SECOND = 420
MINIMUM_RENDER_CHARACTERS = 18
MAXIMUM_RENDER_CHARACTERS = 64


def render_acoustic_ai_chat(room_context: str | None = None) -> None:
    """Render the API-backed Acoustic Atlas conversation."""
    _initialize_state()
    _inject_styles()
    system_prompt = build_system_prompt(room_context)

    title_column, clear_column = st.columns([8, 1])
    with title_column:
        st.markdown(
            """
            <div class="acoustic-atlas-heading">
                <p class="acoustic-atlas-kicker">ACOUSTIC ATLAS</p>
                <h3>Acoustics AI</h3>
                <p>Technical room-acoustics guidance, grounded in your question.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with clear_column:
        if st.session_state[MESSAGES_KEY]:
            if st.button("Clear chat", key="acoustic_atlas_clear"):
                _reset_conversation()
                st.rerun()

    chat_container = st.container(border=True)
    conversation_slot = chat_container.empty()
    _render_conversation(conversation_slot, system_prompt)

    _render_composer(conversation_slot, system_prompt)


def _initialize_state() -> None:
    if MESSAGES_KEY not in st.session_state:
        st.session_state[MESSAGES_KEY] = []
    if SUGGESTIONS_KEY not in st.session_state:
        st.session_state[SUGGESTIONS_KEY] = list(DEFAULT_SUGGESTED_QUESTIONS)
    if ERROR_KEY not in st.session_state:
        st.session_state[ERROR_KEY] = None


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
            .acoustic-atlas-heading {
                padding: 0.25rem 0 1rem;
                border-bottom: 1px solid rgba(96, 165, 250, 0.18);
                margin-bottom: 1rem;
            }
            .acoustic-atlas-kicker {
                color: #60a5fa;
                font-size: 0.78rem;
                font-weight: 700;
                margin: 0 0 0.2rem;
            }
            .acoustic-atlas-heading h3 {
                color: #f8fafc;
                font-size: 1.45rem;
                margin: 0;
            }
            .acoustic-atlas-heading p:last-child {
                color: #94a3b8;
                font-size: 0.9rem;
                margin: 0.35rem 0 0;
            }
            .acoustic-atlas-welcome {
                padding: 2.5rem 1rem 1rem;
                text-align: center;
            }
            .acoustic-atlas-welcome h4 {
                color: #f8fafc;
                font-size: 1.25rem;
                margin: 0 0 0.45rem;
            }
            .acoustic-atlas-welcome p {
                color: #94a3b8;
                font-size: 0.95rem;
                margin: 0;
            }
            .acoustic-atlas-suggestions-label {
                color: #cbd5e1;
                font-size: 0.9rem;
                font-weight: 600;
                margin: 1.5rem 0 0.7rem;
                text-align: center;
            }
            div[data-testid="stChatMessage"] {
                background: rgba(17, 24, 39, 0.72);
                border: 1px solid #334155;
                border-radius: 8px;
                margin-bottom: 0.8rem;
                padding: 0.25rem 0.75rem;
            }
            .acoustic-atlas-thinking {
                display: inline-flex;
                align-items: center;
                gap: 0.55rem;
                min-height: 2.2rem;
                color: #cbd5e1;
                font-size: 0.88rem;
            }
            .acoustic-atlas-thinking-dots {
                display: inline-flex;
                align-items: center;
                gap: 0.22rem;
            }
            .acoustic-atlas-thinking-dots span {
                width: 0.36rem;
                height: 0.36rem;
                border-radius: 50%;
                background: #7dd3fc;
                animation: acoustic-atlas-pulse 1.05s ease-in-out infinite;
            }
            .acoustic-atlas-thinking-dots span:nth-child(2) { animation-delay: 140ms; }
            .acoustic-atlas-thinking-dots span:nth-child(3) { animation-delay: 280ms; }
            @keyframes acoustic-atlas-pulse {
                0%, 70%, 100% { opacity: 0.32; transform: translateY(0); }
                35% { opacity: 1; transform: translateY(-0.16rem); }
            }
            form[data-testid="stForm"] {
                background: #111827;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 0.75rem;
            }
            form[data-testid="stForm"] textarea {
                color: #f8fafc;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_conversation(conversation_slot, system_prompt: str) -> None:
    with conversation_slot.container():
        if st.session_state[MESSAGES_KEY]:
            _render_messages()
        else:
            _render_empty_state(conversation_slot, system_prompt)


def _render_empty_state(conversation_slot, system_prompt: str) -> None:
    st.markdown(
        """
        <div class="acoustic-atlas-welcome">
            <h4>What would you like to explore?</h4>
            <p>Ask about a room, treatment plan, measurement, or system design.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    outer_left, suggestion_area, outer_right = st.columns([1, 5, 1])
    with suggestion_area:
        st.markdown('<p class="acoustic-atlas-suggestions-label">Suggested questions</p>', unsafe_allow_html=True)
        suggestion_columns = st.columns(2)
        for index, suggestion in enumerate(st.session_state[SUGGESTIONS_KEY]):
            with suggestion_columns[index % 2]:
                if st.button(
                    suggestion,
                    key=f"acoustic_atlas_suggestion_{index}",
                    use_container_width=True,
                ):
                    _submit_question(suggestion, conversation_slot, system_prompt)
                    st.rerun()


def _render_messages() -> None:
    for message in st.session_state[MESSAGES_KEY]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _render_composer(conversation_slot, system_prompt: str) -> None:
    error_message = st.session_state[ERROR_KEY]
    if error_message:
        st.error(error_message)
    else:
        st.caption("Live answers stream as they are generated. Use at least four words before sending.")

    with st.form("acoustic_atlas_composer", clear_on_submit=True, border=False):
        question = st.text_area(
            "Ask Acoustic Atlas about sound in your space",
            placeholder="Ask Acoustic Atlas about sound in your space",
            key="acoustic_atlas_input",
            max_chars=MAXIMUM_CHARACTERS - len(system_prompt),
            height=96,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send", type="primary")

    if submitted and question:
        _submit_question(question, conversation_slot, system_prompt)
        st.rerun()


def _submit_question(question: str, conversation_slot, system_prompt: str) -> None:
    validation_error = validate_question(question, system_prompt=system_prompt)
    if validation_error:
        st.session_state[ERROR_KEY] = validation_error
        return

    st.session_state[ERROR_KEY] = None
    messages = st.session_state[MESSAGES_KEY]
    conversation = build_conversation(messages, question, system_prompt=system_prompt)

    try:
        with conversation_slot.container():
            _render_messages()
            with st.chat_message("user"):
                st.markdown(question.strip())
            with st.chat_message("assistant"):
                reply = _render_streamed_reply(stream_acoustic_ai(conversation))
    except AcousticAIError as error:
        st.session_state[ERROR_KEY] = str(error)
        return

    if not isinstance(reply, str) or not reply.strip():
        st.session_state[ERROR_KEY] = "Acoustic Atlas returned an incomplete response. Please try again."
        return

    messages.extend(
        [
            {"role": "user", "content": question.strip()},
            {"role": "assistant", "content": reply.strip()},
        ]
    )


def _render_streamed_reply(chunks: Iterable[str]) -> str:
    """Buffer network chunks and reveal them at a steady, readable cadence."""
    stream_events: Queue[tuple[str, object]] = Queue()
    started_at = monotonic()

    def read_stream() -> None:
        try:
            for chunk in chunks:
                stream_events.put(("chunk", chunk))
        except Exception as error:
            stream_events.put(("error", error))
        finally:
            stream_events.put(("done", None))

    Thread(target=read_stream, daemon=True).start()

    response_placeholder = st.empty()
    thinking_placeholder = st.empty()
    response_text = ""
    pending_text = ""
    last_rendered_at = started_at
    first_content_revealed = False
    stream_finished = False
    thinking_visible = False

    while not (stream_finished and not pending_text):
        try:
            event_kind, payload = stream_events.get(timeout=POLL_INTERVAL_SECONDS)
        except Empty:
            pending_events = []
        else:
            pending_events = [(event_kind, payload)]
            while True:
                try:
                    pending_events.append(stream_events.get_nowait())
                except Empty:
                    break

        for event_kind, payload in pending_events:
            if event_kind == "chunk" and isinstance(payload, str):
                pending_text += payload
            elif event_kind == "error" and isinstance(payload, Exception):
                raise payload
            elif event_kind == "done":
                stream_finished = True

        now = monotonic()
        if (
            not first_content_revealed
            and not thinking_visible
            and now - started_at >= THINKING_DELAY_SECONDS
        ):
            thinking_placeholder.markdown(
                """
                <div class='acoustic-atlas-thinking' role='status' aria-live='polite'>
                    <span>Thinking</span>
                    <span class='acoustic-atlas-thinking-dots' aria-hidden='true'><span></span><span></span><span></span></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            thinking_visible = True

        if pending_text and (
            stream_finished or now - last_rendered_at >= RENDER_INTERVAL_SECONDS
        ):
            elapsed = now - last_rendered_at
            character_budget = min(
                MAXIMUM_RENDER_CHARACTERS,
                max(MINIMUM_RENDER_CHARACTERS, int(elapsed * STREAM_CHARACTERS_PER_SECOND)),
            )
            text_to_reveal, pending_text = _take_stream_segment(pending_text, character_budget)
            response_text += text_to_reveal
            response_placeholder.markdown(f"{response_text}▍")
            thinking_placeholder.empty()
            first_content_revealed = True
            last_rendered_at = now

    if not response_text:
        thinking_placeholder.empty()
        return ""

    response_placeholder.markdown(response_text)
    thinking_placeholder.empty()
    return response_text


def _take_stream_segment(buffer: str, character_budget: int) -> tuple[str, str]:
    if len(buffer) <= character_budget:
        return buffer, ""

    search_limit = min(len(buffer), character_budget + 12)
    break_index = max(
        buffer.rfind(separator, 0, search_limit)
        for separator in (" ", "\n", ".", ",", ";", ":")
    )
    if break_index >= max(1, character_budget // 2):
        return buffer[:break_index + 1], buffer[break_index + 1:]

    return buffer[:character_budget], buffer[character_budget:]


def _reset_conversation() -> None:
    st.session_state[MESSAGES_KEY] = []
    st.session_state[SUGGESTIONS_KEY] = list(DEFAULT_SUGGESTED_QUESTIONS)
    st.session_state[ERROR_KEY] = None