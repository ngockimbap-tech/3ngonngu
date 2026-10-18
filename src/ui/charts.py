"""Ba biểu đồ nhỏ của Tab 2 bằng SVG thuần, đúng kích thước wireframe.

Đầu vào là dữ liệu chỉ đọc từ DashboardData; không có dữ liệu thì hiện
"Chưa có dữ liệu" thay vì đường hoặc cột giả.
"""
from __future__ import annotations

from src.core.statistics import CycleMetric
from src.ui.labels import T

import streamlit.components.v1 as components

SVG_OPEN = '<svg width="560" height="104" viewBox="0 0 560 104" xmlns="http://www.w3.org/2000/svg">'
LINE_COLOR = "#738795"
NS_COLOR, EW_COLOR, FLOW_COLOR = "#839EAA", "#B5BFC6", "#9CABB5"
BASE_Y = 74          # đường nền cột
MAX_BAR_PX = 53
MAX_GROUPS = 6


def _caption() -> str:
    return f'<div class="chart-cap">{T["chart_caption"]}</div>'


def empty_chart() -> str:
    return (_caption() + SVG_OPEN
            + '<text class="ct" x="18" y="60">Chưa có dữ liệu</text></svg>')


def queue_chart(series: tuple[tuple[int, int], ...]) -> str:
    """Đường Queue tổng theo thời gian mô phỏng."""
    if len(series) < 2:
        return empty_chart()
    if len(series) > 120:   # giảm điểm vẽ, giữ điểm cuối
        step = len(series) / 120
        series = tuple(series[int(i * step)] for i in range(120)) + (series[-1],)
    t_max = max(series[-1][0], 1)
    values = [q for _, q in series]
    lo, hi = min(values), max(values)
    points = []
    for t, q in series:
        x = 18 + (t / t_max) * 486
        y = 43 if hi == lo else 66 - (q - lo) / (hi - lo) * 46
        points.append(f"{x:.1f},{y:.1f}")
    t_last, q_last = series[-1]
    return (_caption() + SVG_OPEN
            + f'<polyline points="{" ".join(points)}" fill="none" stroke="{LINE_COLOR}" stroke-width="2"/>'
            '<line x1="18" y1="72" x2="530" y2="72" stroke="#E3E7EA" stroke-width="1.5"/>'
            '<text class="ct" x="18" y="97">0s</text>'
            f'<text class="ct" x="530" y="97" text-anchor="end">{t_last}s · Queue cuối: {q_last}</text></svg>')


def _bar(x: float, width: float, value: float, unit: float, color: str, suffix: str = "") -> str:
    height = value * unit
    shown = f"{value:g}{suffix}"
    return (f'<rect x="{x:.1f}" y="{BASE_Y - height:.1f}" width="{width:.1f}" height="{height:.1f}" fill="{color}"/>'
            f'<text class="cv" x="{x + width / 2:.1f}" y="{BASE_Y - height - 5:.1f}" text-anchor="middle">{shown}</text>')


def _tail(cycles: list[CycleMetric]) -> list[CycleMetric]:
    return cycles[-MAX_GROUPS:]


def green_chart(cycles: tuple[CycleMetric, ...]) -> str:
    """Giây xanh NS/EW đã chốt theo chu kỳ."""
    groups = _tail(list(cycles))
    if not groups:
        return empty_chart()
    unit = MAX_BAR_PX / max(max(g.green_ns_s, g.green_ew_s) for g in groups)
    if len(groups) == 1:   # đúng bố cục wireframe cho một chu kỳ
        g = groups[0]
        return (_caption() + SVG_OPEN
                + _bar(120, 78, g.green_ns_s, unit, NS_COLOR, "s") + _bar(268, 78, g.green_ew_s, unit, EW_COLOR, "s")
                + '<text class="ct" x="159" y="97" text-anchor="middle">NS</text>'
                '<text class="ct" x="307" y="97" text-anchor="middle">EW</text>'
                f'<text class="ct" x="474" y="97" text-anchor="middle">C{g.cycle_index}</text></svg>')
    slot = 512 / len(groups)
    bar_w = min(30.0, slot / 2 - 4)
    parts = []
    for i, g in enumerate(groups):
        cx = 18 + slot * (i + 0.5)
        parts.append(_bar(cx - bar_w - 1, bar_w, g.green_ns_s, unit, NS_COLOR))
        parts.append(_bar(cx + 1, bar_w, g.green_ew_s, unit, EW_COLOR))
        parts.append(f'<text class="ct" x="{cx:.1f}" y="97" text-anchor="middle">C{g.cycle_index}</text>')
    legend = ('<rect x="440" y="2" width="10" height="10" fill="#839EAA"/><text class="ct" x="454" y="11">NS</text>'
              '<rect x="486" y="2" width="10" height="10" fill="#B5BFC6"/><text class="ct" x="500" y="11">EW</text>')
    return _caption() + SVG_OPEN + "".join(parts) + legend + "</svg>"


def flow_chart(cycles: tuple[CycleMetric, ...]) -> str:
    """Số xe đến và số xe qua vạch theo chu kỳ (chu kỳ đang chạy là bản tạm)."""
    groups = _tail(list(cycles))
    if not groups:
        return empty_chart()
    unit = min(10.5, MAX_BAR_PX / max(max(g.arrivals, g.departures, 1) for g in groups))
    if len(groups) == 1:
        g = groups[0]
        tag = f"C{g.cycle_index} tạm" if g.provisional else f"C{g.cycle_index}"
        return (_caption() + SVG_OPEN
                + _bar(103, 85, g.arrivals, unit, FLOW_COLOR) + _bar(279, 85, g.departures, unit, FLOW_COLOR)
                + '<text class="ct" x="145" y="97" text-anchor="middle">Arrivals</text>'
                '<text class="ct" x="321" y="97" text-anchor="middle">Departures</text>'
                f'<text class="ct" x="522" y="97" text-anchor="middle">{tag}</text></svg>')
    slot = 512 / len(groups)
    bar_w = min(30.0, slot / 2 - 4)
    parts = []
    for i, g in enumerate(groups):
        cx = 18 + slot * (i + 0.5)
        parts.append(_bar(cx - bar_w - 1, bar_w, g.arrivals, unit, "#839EAA"))
        parts.append(_bar(cx + 1, bar_w, g.departures, unit, "#B5BFC6"))
        label = f"C{g.cycle_index}" + (" tạm" if g.provisional else "")
        parts.append(f'<text class="ct" x="{cx:.1f}" y="97" text-anchor="middle">{label}</text>')
    legend = ('<rect x="400" y="2" width="10" height="10" fill="#839EAA"/><text class="ct" x="414" y="11">Arrivals</text>'
              '<rect x="466" y="2" width="10" height="10" fill="#B5BFC6"/><text class="ct" x="480" y="11">Departures</text>')
    return _caption() + SVG_OPEN + "".join(parts) + legend + "</svg>"

_IFRAME_CSS = (
    "<style>"
    "html,body{margin:0;padding:0;background:transparent;"
    "font-family:'Segoe UI',Inter,system-ui,sans-serif}"
    ".chart-cap{font-size:12.5px;color:#66727B;letter-spacing:.2px;margin-bottom:2px}"
    ".ct{font-size:13px;fill:#66727B}"
    ".cv{font-size:13px;fill:#263238}"
    "svg{display:block;max-width:100%;height:auto}"
    "</style>"
)


def render(html: str) -> None:
    """Vẽ một biểu đồ trong iframe riêng (không bị lọc SVG, tự mang CSS theo)."""
    components.html(_IFRAME_CSS + html, height=132)
