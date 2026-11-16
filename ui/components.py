"""Reusable interface components."""

import html

import streamlit as st


def render_subheader(title: str, icon: str) -> None:
    """Display a subheader with an SVG icon."""

    safe_title = html.escape(title)

    # Keep the HTML on one line so Markdown does not treat it as code.
    subheader_html = (
        f'<div class="section-heading">'
        f'<div class="section-heading-icon">{icon}</div>'
        f'<h2>{safe_title}</h2>'
        f'</div>'
    )

    st.markdown(
        subheader_html,
        unsafe_allow_html=True,
    )