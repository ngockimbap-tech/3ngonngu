"""Renderer 2D Plotly: chỉ vẽ SimulationSnapshot, không sửa Queue hoặc Vehicle.

Bố cục lấy từ wireframe (8 px/mét, tâm giao lộ cố định):
- cửa sổ hiển thị ±23,25 m quanh tâm (phần xe ngoài cửa sổ vẫn thuộc Core);
- +x là Đông, +y là Nam (trục y đảo ngược khi vẽ);
- x, y trong snapshot là đầu xe; biểu tượng xe chỉ để minh họa nên bề rộng
  vẽ cố định, không thay cho bề rộng vật lý dùng kiểm tra xung đột.
"""
from __future__ import annotations

import plotly.graph_objects as go

from src.core.geometry import DIRECTION_VECTORS
from src.models.snapshot import SimulationSnapshot

PX_PER_M = 8.0
VIEW_HALF_M = 23.25
FIG_WIDTH_PX, FIG_HEIGHT_PX = 660, 395
X_RANGE = (-51.5, 31.0)      # phần trống bên trái để tâm giao lộ nằm đúng vị trí wireframe
Y_RANGE = (25.25, -24.125)   # đảo ngược: +y hướng Nam (xuống dưới)
VISUAL_VEHICLE_WIDTH_M = 1.625

ROAD, CORE, DASH = "#E1E5E8", "#F6F7F8", "#9DA7AE"
INK = "#263238"
SIGNAL_COLORS = {"GREEN": "#40805B", "RED": "#AA4A4A", "YELLOW": "#C9A23F", "IDLE": "#B5BFC6"}
# (nền, viền) theo trạng thái xe; trùng chú giải.
VEHICLE_STYLE = {
    "APPROACHING": ("#D9E3EB", "#808B92"),
    "STOPPED": ("#6D7982", "#49555D"),
    "CROSSING": ("#91B5AD", "#5B7372"),
}


def _rect(x0: float, y0: float, x1: float, y1: float, fill: str,
          line: str | None = None, dash: bool = False, width: float = 1.3) -> dict:
    return dict(
        type="rect", x0=x0, y0=y0, x1=x1, y1=y1, layer="below",
        fillcolor=fill,
        line=dict(color=line or fill, width=width if line else 0,
                  dash="6px,5px" if dash else "solid"),
    )


def _vehicle_shape(x0: float, y0: float, x1: float, y1: float, clipped: bool,
                   fill: str, stroke: str) -> dict:
    """Hình chữ nhật bo góc; bản bị cắt viền cửa sổ giữ góc vuông."""
    common = dict(fillcolor=fill, line=dict(color=stroke, width=1.3), layer="above")
    if clipped:
        return dict(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, **common)
    r = 0.35
    path = (f"M {x0 + r},{y0} L {x1 - r},{y0} Q {x1},{y0} {x1},{y0 + r} "
            f"L {x1},{y1 - r} Q {x1},{y1} {x1 - r},{y1} L {x0 + r},{y1} "
            f"Q {x0},{y1} {x0},{y1 - r} L {x0},{y0 + r} Q {x0},{y0} {x0 + r},{y0} Z")
    return dict(type="path", path=path, **common)


def build_map_figure(snapshot: SimulationSnapshot | None, show_vehicles: bool = True) -> go.Figure:
    """Dựng figure bản đồ từ snapshot; snapshot None vẽ giao lộ trống (chưa có phiên)."""
    half = snapshot.geometry.intersection_width_m / 2 if snapshot else 8.0
    lane = snapshot.geometry.lane_offset_m if snapshot else 2.0
    view = VIEW_HALF_M
    shapes: list[dict] = [
        # bốn nhánh đường + lõi giao lộ
        _rect(-half, -view, half, -half, ROAD), _rect(-half, half, half, view, ROAD),
        _rect(-view, -half, -half, half, ROAD), _rect(half, -half, view, half, ROAD),
        _rect(-half, -half, half, half, CORE, DASH, dash=True),
    ]
    for x0, y0, x1, y1 in ((0, -view, 0, view), (-view, 0, view, 0)):   # trục giữa
        shapes.append(dict(type="line", x0=x0, y0=y0, x1=x1, y1=y1, layer="below",
                           line=dict(color=DASH, width=1.3, dash="6px,5px")))
    t = 0.25  # nửa bề dày vạch dừng
    for x0, y0, x1, y1 in (
        (-2 * lane, -half - t, 0, -half + t),    # N
        (0, half - t, 2 * lane, half + t),       # S
        (-half - t, 0, -half + t, 2 * lane),     # W
        (half - t, -2 * lane, half + t, 0),      # E
    ):
        shapes.append(_rect(x0, y0, x1, y1, INK))

    dot_x: list[float] = []
    dot_y: list[float] = []
    if show_vehicles and snapshot:
        w = VISUAL_VEHICLE_WIDTH_M / 2
        for v in snapshot.vehicles:
            dx, dy = DIRECTION_VECTORS[v.origin]
            rear_x, rear_y = v.x - v.length_m * dx, v.y - v.length_m * dy
            if v.origin in ("N", "S"):
                x0, x1 = v.x - w, v.x + w
                y0, y1 = min(v.y, rear_y), max(v.y, rear_y)
            else:
                x0, x1 = min(v.x, rear_x), max(v.x, rear_x)
                y0, y1 = v.y - w, v.y + w
            cx0, cx1, cy0, cy1 = max(x0, -view), min(x1, view), max(y0, -view), min(y1, view)
            if cx0 >= cx1 or cy0 >= cy1:
                continue   # nằm ngoài cửa sổ, vẫn thuộc Core
            clipped = (cx0, cx1, cy0, cy1) != (x0, x1, y0, y1)
            fill, stroke = VEHICLE_STYLE[v.motion_state]
            shapes.append(_vehicle_shape(cx0, cy0, cx1, cy1, clipped, fill, stroke))
            px, py = v.x - 0.3 * dx, v.y - 0.3 * dy   # chấm nhỏ đánh dấu đầu xe
            if abs(px) <= view and abs(py) <= view:
                dot_x.append(px)
                dot_y.append(py)

    colors = snapshot.signals.signal_colors if snapshot else dict.fromkeys("NSEW", "IDLE")
    side = lane + 3.25  # đèn lệch tâm đường 5,25 m (chỉ để minh họa)
    lamp_pos = {"N": (-side, -half - lane), "S": (side, half + lane),
                "W": (-half - lane, side), "E": (half + lane, -side)}
    fig = go.Figure()
    if dot_x:
        fig.add_trace(go.Scatter(x=dot_x, y=dot_y, mode="markers", hoverinfo="skip",
                                 marker=dict(size=4, color=INK)))
    fig.add_trace(go.Scatter(
        x=[lamp_pos[d][0] for d in "NSEW"], y=[lamp_pos[d][1] for d in "NSEW"],
        mode="markers", hoverinfo="skip",
        marker=dict(size=12, color=[SIGNAL_COLORS[colors[d]] for d in "NSEW"])))

    label_font = dict(size=17, color=INK, family="Segoe UI, Inter, system-ui, sans-serif")
    fig.update_layout(
        shapes=shapes, showlegend=False,
        width=FIG_WIDTH_PX, height=FIG_HEIGHT_PX, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=list(X_RANGE), visible=False, fixedrange=True,
                   scaleanchor="y", scaleratio=1, constrain="domain"),
        yaxis=dict(range=list(Y_RANGE), visible=False, fixedrange=True, constrain="domain"),
        annotations=[
            dict(x=0, y=-view + 1.0, text="<b>N ↓</b>", showarrow=False, font=label_font),
            dict(x=0, y=view, text="<b>S ↑</b>", showarrow=False, font=label_font),
            dict(x=-28.75, y=0, text="<b>W →</b>", showarrow=False, font=label_font),
            dict(x=28.4, y=0, text="<b>← E</b>", showarrow=False, font=label_font),
        ],
    )
    return fig
