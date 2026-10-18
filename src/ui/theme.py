"""Nạp CSS wireframe cho Streamlit."""
from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).with_name("styles.css")


def inject_css() -> None:
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
