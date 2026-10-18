"""Điểm vào Streamlit: chỉ ghép hai tab, không chứa thuật toán hay xử lý nghiệp vụ.

Chạy từ thư mục gốc dự án:  uv run streamlit run src/app.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:   # để import được "src.*" khi Streamlit chạy file này
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="Smart Traffic Light Simulator", layout="wide")

from src.ui.config_tab import render_config_tab  # noqa: E402
from src.ui.labels import T  # noqa: E402
from src.ui.simulation_tab import render_simulation_tab  # noqa: E402
from src.ui.state import init_session  # noqa: E402
from src.ui.theme import inject_css  # noqa: E402

inject_css()
init_session()

HEADER_HTML = f"""
<div class="header-container">
    <div>
        <div class="app-title">Smart Traffic Light Simulator</div>
        <div class="app-sub">{T["header_sub"]}</div>
    </div>
    <div>
        <span class="badge">{T["badge"]}</span>
    </div>
</div>
"""
st.markdown(HEADER_HTML, unsafe_allow_html=True)

configuration_tab, simulation_tab = st.tabs(["Quản lý cấu hình", "Mô phỏng và phân tích"])
with configuration_tab:
    render_config_tab()
with simulation_tab:
    render_simulation_tab()

st.html('<svg width="100" height="40"><rect width="100" height="40" fill="red"/></svg>')
