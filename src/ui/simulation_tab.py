"""Tab 2 · Mô phỏng và phân tích.

UI chỉ gọi lệnh công khai của SimulationEngine (start/pause/resume/stop/reset/
run_ticks/run_until_cycle_end) và đọc snapshot()/dashboard_data(). Không tự sinh
xe, không tính Adaptive, không sửa Queue hoặc CSV.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from src.core.history_storage import HistoryStorage, summary_csv_text
from src.core.simulation import SimulationEngine
from src.models.config import Config
from src.models.snapshot import SimulationSnapshot
from src.ui import charts, state
from src.ui.labels import T
from src.ui.renderer_2d import VEHICLE_STYLE, build_map_figure

S = st.session_state
FINISHED = ("STOPPED", "COMPLETED", "ERROR")
AUTORUN = hasattr(st, "fragment")   # tự chạy 1 tick/giây cần Streamlit >= 1.37


# ----------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------
def _run(action, *args) -> None:
    try:
        action(*args)
        S.sim_notice = None
    except Exception as error:  # noqa: BLE001 - hiển thị lý do cho người dùng
        S.sim_notice = str(error)


def on_start() -> None:
    def go() -> None:
        data = state.get_config(S.use_config_id or S.selected_config_id)
        if data is None:
            raise RuntimeError("Chưa có cấu hình hợp lệ để chạy; chọn hoặc tạo ở Tab 1.")
        engine = SimulationEngine(Config.from_dict(data))
        engine.start()
        S.engine, S.run_config_snapshot = engine, data   # bản chốt, không đổi khi sửa Tab 1
        S.summary_saved, S.pending_sim_reset = False, False
    _run(go)


def on_pause() -> None:
    _run(S.engine.pause)


def on_resume() -> None:
    _run(S.engine.resume)


def on_stop() -> None:
    _run(S.engine.stop)


def on_step() -> None:
    _run(S.engine.run_ticks, 1)


def on_cycle() -> None:
    _run(S.engine.run_until_cycle_end)


def on_reset_ask() -> None:
    S.pending_sim_reset = True


def on_reset_cancel() -> None:
    S.pending_sim_reset = False


def on_reset_confirm() -> None:
    _run(S.engine.reset)
    S.pending_sim_reset, S.summary_saved = False, False


def _persist_history() -> None:
    """Ghi sim_history.csv đúng một lần khi phiên có Summary."""
    engine = S.engine
    if engine is None or S.summary_saved:
        return
    summary = engine.summary()
    if summary is None:
        return
    S.summary_saved = True
    try:
        HistoryStorage.append_run(summary, list(engine.cycle_metrics()))
    except Exception as error:  # noqa: BLE001
        S.sim_notice = f"Chưa ghi được lịch sử CSV: {error}"


# ----------------------------------------------------------------------
# Helpers hiển thị
# ----------------------------------------------------------------------
def _card(title: str):
    container = st.container(border=True)
    container.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
    return container


def _metric(label: str, value: str, sub: str = "", big: bool = False) -> str:
    sub_html = f'<div class="m-sub">{sub}</div>' if sub else ""
    cls = "m-value lg" if big else "m-value"
    return f'<div><div class="m-label">{label}</div><div class="{cls}">{value}</div>{sub_html}</div>'


def _grid(*cells: str) -> str:
    return '<div class="m-grid">' + "".join(cells) + "</div>"


def _legend(snapshot: SimulationSnapshot | None, motion_on: bool) -> str:
    rows = "".join(
        f'<div class="lg-row"><span class="sw" style="background:{fill};border-color:{line}"></span>{name}</div>'
        for name, (fill, line) in VEHICLE_STYLE.items())
    colors = snapshot.signals.signal_colors if snapshot else None
    ns, ew = (colors["N"], colors["E"]) if colors else ("—", "—")
    note = "" if motion_on else '<div class="lg-note">Motion 2D đang tắt: không vẽ xe.</div>'
    return (f'<div class="legend"><div class="lg-title">Chú giải</div>{rows}'
            f'<div class="lg-phase">N/S: {ns}<br>E/W: {ew}</div>'
            '<div class="lg-note">Ô nét đứt: vùng xung đột<br>Điểm trên xe: tọa độ đầu xe</div>'
            '<div class="lg-note">Zoom ngã tư / một phần xe<br>Xe ngoài hình vẫn thuộc Core</div>'
            f'{note}</div>')


def _plot(fig) -> None:
    config = {"staticPlot": True, "displayModeBar": False}
    try:
        st.plotly_chart(fig, width="content", config=config, theme=None)
    except TypeError:   # Streamlit cũ chưa có tham số width
        st.plotly_chart(fig, use_container_width=False, config=config, theme=None)


def _dash(value) -> str:
    return "—" if value is None else str(value)


# ----------------------------------------------------------------------
# Phần dashboard (tự làm mới mỗi giây khi RUNNING)
# ----------------------------------------------------------------------
def _dashboard() -> None:
    engine = S.engine
    if engine is not None and engine.state == "RUNNING" and AUTORUN:
        try:
            engine.run_ticks(1)
        except Exception as error:  # noqa: BLE001
            S.sim_notice = str(error)
        if engine.state != "RUNNING":
            st.rerun()   # đổi trạng thái: làm mới cả nút điều khiển

    dd = engine.dashboard_data() if engine is not None else None
    snap = dd.snapshot if dd else None
    run_cfg = S.run_config_snapshot if engine is not None else None
    motion_on = bool(run_cfg["motion_2d"]["enabled"]) if run_cfg else True
    preview = run_cfg or state.get_config(S.use_config_id or S.selected_config_id)
    min_gap = f'{preview["motion_2d"]["min_gap_m"]:.1f}' if preview else "—"

    col_l, col_r = st.columns([1000, 816], gap="small")

    with col_l:
        with _card("Bản đồ 2D · x dương Đông, y dương Nam · đơn vị mét"):
            map_col, legend_col = st.columns([660, 304], gap="small")
            with map_col:
                _plot(build_map_figure(snap, show_vehicles=motion_on))
            with legend_col:
                st.markdown(_legend(snap, motion_on), unsafe_allow_html=True)
        with st.container(border=True):
            if dd:
                hold = snap.metrics.clearance_hold_s
                gap = f"{dd.observed_min_gap_m:.2f}m" if dd.observed_min_gap_m is not None else "—"
                main = (f"Trong vùng: {dd.conflict_occupancy_count} xe · Min Gap cấu hình: "
                        f"{dd.min_gap_config_m:.1f}m · Clearance Hold: {hold:g}s")
                err = engine.error_message
                sub = (f"Gap thực đo nhỏ nhất: {gap} · " +
                       (f"ERROR: {escape(err)}" if err else "Không có ERROR; ERROR sẽ giữ bốn đèn đỏ."))
            else:
                main = f"Trong vùng: — · Min Gap cấu hình: {min_gap}m · Clearance Hold: —"
                sub = "Chưa có phiên mô phỏng · bấm Start để bắt đầu"
            st.markdown(f'<div class="zone-main">{main}</div><div class="zone-sub">{sub}</div>',
                        unsafe_allow_html=True)

    with col_r:
        cycles_total = run_cfg["cycles_to_run"] if run_cfg else (preview["cycles_to_run"] if preview else None)
        with _card("Tín hiệu và thời gian"):
            if snap:
                cells = (_metric("Pha hiện tại", snap.signals.current_segment),
                         _metric("Còn lại", f"{snap.signals.remaining_s} giây"),
                         _metric("Chu kỳ", f"{snap.cycle_index} / {cycles_total}"),
                         _metric("Thời gian", f"{snap.sim_time} giây"))
            else:
                cells = (_metric("Pha hiện tại", "—"), _metric("Còn lại", "—"),
                         _metric("Chu kỳ", f"— / {_dash(cycles_total)}"), _metric("Thời gian", "—"))
            st.markdown(_grid(*cells), unsafe_allow_html=True)

        with _card("Queue hiện tại · xe chưa vượt vạch"):
            q = snap.metrics.queue_lengths if snap else None
            sub = f"NS {q['N'] + q['S']} xe / EW {q['E'] + q['W']} xe" if q else ""
            st.markdown(_grid(*[
                _metric(f"Queue {d}", f"{q[d]} xe" if q else "—", sub if d == "E" else "", big=True)
                for d in "NSEW"]), unsafe_allow_html=True)

        with _card(T["counters_title"]):
            if snap:
                m = snap.metrics
                queue_total = sum(m.queue_lengths.values())
                cells = (f'<div class="ctr-cell">Xe mới đến: {m.total_arrivals}</div>',
                         f'<div class="ctr-cell">Vượt vạch: {m.crossed_stop_total}</div>',
                         f'<div class="ctr-cell">Ra khỏi khung: {m.exited_world_total}</div>',
                         f'<div class="ctr-cell">Còn chờ: {queue_total}</div>')
                note = (f"Initial {m.initial_total} + Arrivals {m.total_arrivals} = Queue {queue_total} + "
                        f"Crossed {m.crossed_stop_total} · Crossed {m.crossed_stop_total} = "
                        f"Active {m.active_crossing_count} + Exited {m.exited_world_total}")
            else:
                cells = tuple('<div class="ctr-cell">—</div>' for _ in range(4))
                note = "Chưa có dữ liệu"
            st.markdown(_grid(*cells) + f'<div class="ctr-note">{note}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            if dd:
                ns, ew = dd.current_green
                prev = f"{dd.previous_green[0]}s / {dd.previous_green[1]}s" if dd.previous_green else "— / —"
                title = f"Xanh đã chốt: NS {ns}s / EW {ew}s · Chu kỳ trước: {prev}"
            else:
                title = "Xanh đã chốt: — · Chu kỳ trước: — / —"
            st.markdown(f'<div class="lock-title">{title}</div>'
                        '<div class="lock-sub">Chỉ tính lại ở đầu chu kỳ; không thay đổi tùy tiện trong từng giây.</div>',
                        unsafe_allow_html=True)

        with st.container(border=True):
            summary = dd.summary if dd else None
            s1, s2 = st.columns([5, 1.3])
            with s1:
                if summary:
                    wait = f"{summary.avg_wait_departed_s:.1f}s" if summary.avg_wait_departed_s is not None else "—"
                    sub = (f"{summary.status} · {summary.departed_vehicles} xe đã qua vạch · còn chờ "
                           f"{summary.remaining_vehicles} · chờ TB {wait}")
                else:
                    sub = "Mở khi STOPPED/COMPLETED · không đồng nghĩa hết xe chờ"
                st.markdown(f'<div class="sum-title">Summary cuối phiên: {"có" if summary else "chưa có"}</div>'
                            f'<div class="sum-sub">{sub}</div>', unsafe_allow_html=True)
            with s2:
                data = summary_csv_text(summary, list(dd.cycle_metrics)) if summary else ""
                st.download_button("Xuất CSV", data, file_name=f"{summary.run_id}.csv" if summary else "summary.csv",
                                   mime="text/csv", key="btn_csv", disabled=summary is None)

    # ---- Ba biểu đồ ----
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        with _card("Queue Length theo thời gian"):
            charts.render(charts.queue_chart(dd.queue_series) if dd else charts.empty_chart())
    with c2:
        with _card("Green NS/EW theo chu kỳ"):
            charts.render(charts.green_chart(dd.cycle_metrics) if dd else charts.empty_chart())
    with c3:
        with _card("Arrivals / Departures theo chu kỳ"):
            charts.render(charts.flow_chart(dd.cycle_metrics) if dd else charts.empty_chart())


# ----------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------
def render_simulation_tab() -> None:
    _persist_history()
    engine = S.engine
    name = engine.state if engine is not None else "IDLE"
    ready = S.manager is not None and state.get_config(S.use_config_id or S.selected_config_id) is not None

    # ---- Cấu hình đã chốt ----
    cfg = S.run_config_snapshot if engine is not None else state.get_config(S.use_config_id or S.selected_config_id)
    with st.container(border=True):
        if cfg:
            r, q = cfg["rates_per_min"], cfg
            tail = "bản cấu hình đã chốt khi Start" if engine is not None else "bản cấu hình sẽ chốt khi Start"
            st.markdown(
                f'<div class="run-title">{escape(cfg["id"])} · {escape(cfg["name"])} · {tail}</div>'
                f'<div class="run-sub">N {r["N"]:g} / S {r["S"]:g} / E {r["E"]:g} / W {r["W"]:g} xe/phút | '
                f'Tổng xanh {q["green_budget_s"]} giây | {q["cycles_to_run"]} chu kỳ | Seed {q["seed"]}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="run-title">Chưa có cấu hình để chạy</div>'
                        '<div class="run-sub">Tạo hoặc chọn một cấu hình ở tab Quản lý cấu hình.</div>',
                        unsafe_allow_html=True)

    # ---- Thanh điều khiển ----
    ctl = st.columns([113, 113, 129, 111, 113, 149, 213, 244, 590], gap="small")
    ctl[0].button("Start", key="sim_start", on_click=on_start,
                  disabled=not (ready and (engine is None or name in FINISHED)))
    ctl[1].button("Pause", key="sim_pause", on_click=on_pause, disabled=name != "RUNNING")
    ctl[2].button("Resume", key="sim_resume", on_click=on_resume, disabled=name != "PAUSED")
    ctl[3].button("Stop", key="sim_stop", on_click=on_stop, disabled=name not in ("RUNNING", "PAUSED"))
    ctl[4].button("Reset", key="sim_reset", on_click=on_reset_ask,
                  disabled=engine is None or name == "RUNNING")
    ctl[5].button("Step +1s", key="sim_step", on_click=on_step, disabled=name != "PAUSED")
    ctl[6].button("Chạy hết chu kỳ", key="sim_cycle", on_click=on_cycle, disabled=name != "PAUSED")
    ctl[8].markdown(
        f'<div class="status-box">{name}{T["status_suffix"]} · Step / Chạy chu kỳ chỉ bật khi PAUSED</div>',
        unsafe_allow_html=True)

    if S.pending_sim_reset:
        with st.container(border=True):
            st.markdown('<p class="banner" style="font-size:16px">Bỏ tiến độ hiện tại và chạy lại từ đầu '
                        "(cùng bản chốt, cùng seed)?</p>", unsafe_allow_html=True)
            a, b, _ = st.columns([1, 1.4, 6])
            a.button("Hủy", key="sim_reset_cancel", on_click=on_reset_cancel)
            b.button("Xác nhận Reset", key="sim_reset_confirm", on_click=on_reset_confirm)
    if S.sim_notice:
        st.markdown(f'<div class="field-err">{escape(S.sim_notice)}</div>', unsafe_allow_html=True)
    if not AUTORUN and name == "RUNNING":
        st.markdown('<div class="hint">Streamlit hiện tại chưa hỗ trợ tự chạy; hãy Pause rồi dùng Step +1s.</div>',
                    unsafe_allow_html=True)

    # ---- Dashboard (fragment tự làm mới khi RUNNING) ----
    if AUTORUN:
        running = engine is not None and name == "RUNNING"
        st.fragment(run_every=1.0 if running else None)(_dashboard)()
    else:
        _dashboard()

    st.markdown('<p class="foot">Core → Snapshot / báo cáo chỉ đọc → Renderer · '
                "UI không tự sinh xe, tính Adaptive, sửa Queue hoặc CSV</p>", unsafe_allow_html=True)
