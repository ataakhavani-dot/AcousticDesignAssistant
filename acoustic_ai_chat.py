"""Streamlit presentation for the public Acoustic Atlas chat."""

from __future__ import annotations

import streamlit as st

from acoustic_ai import (
    DEFAULT_SUGGESTED_QUESTIONS,
    MAXIMUM_CHARACTERS,
    AcousticAIError,
    ask_acoustic_ai,
    build_conversation,
    validate_question,
)


MESSAGES_KEY = "acoustic_atlas_messages"
SUGGESTIONS_KEY = "acoustic_atlas_suggestions"
ERROR_KEY = "acoustic_atlas_error"


def render_acoustic_ai_chat() -> None:
    """Render the API-backed Acoustic Atlas conversation."""
    _initialize_state()
    _inject_styles()

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

    with st.container(border=True):
        if st.session_state[MESSAGES_KEY]:
            _render_messages()
        else:
            _render_empty_state()

    _render_composer()


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
            div[data-testid="stChatInput"] {
                background: #111827;
                border: 1px solid #475569;
                border-radius: 8px;
            }
            div[data-testid="stChatInput"] textarea {
                color: #f8fafc;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_empty_state() -> None:
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
                    _submit_question(suggestion)
                    st.rerun()


def _render_messages() -> None:
    for message in st.session_state[MESSAGES_KEY]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _render_composer() -> None:
    error_message = st.session_state[ERROR_KEY]
    if error_message:
        st.error(error_message)
    else:
        st.caption("Use at least four words. Questions are checked before they are sent.")

    question = st.chat_input(
        "Ask Acoustic Atlas about sound in your space",
        key="acoustic_atlas_input",
        max_chars=MAXIMUM_CHARACTERS,
    )
    if question:
        _submit_question(question)
        st.rerun()


def _submit_question(question: str) -> None:
    validation_error = validate_question(question)
    if validation_error:
        st.session_state[ERROR_KEY] = validation_error
        return

    st.session_state[ERROR_KEY] = None
    messages = st.session_state[MESSAGES_KEY]
    conversation = build_conversation(messages, question)

    try:
        with st.spinner("Acoustic Atlas is thinking..."):
            response = ask_acoustic_ai(conversation)
    except AcousticAIError as error:
        st.session_state[ERROR_KEY] = str(error)
        return

    messages.extend(
        [
            {"role": "user", "content": question.strip()},
            {"role": "assistant", "content": response.reply},
        ]
    )
    st.session_state[SUGGESTIONS_KEY] = list(response.suggested_questions)


def _reset_conversation() -> None:
    st.session_state[MESSAGES_KEY] = []
    st.session_state[SUGGESTIONS_KEY] = list(DEFAULT_SUGGESTED_QUESTIONS)
    st.session_state[ERROR_KEY] = None