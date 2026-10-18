"""Tab 1 · Quản lý cấu hình.

UI chỉ giữ bản nháp trong session_state và gọi ConfigManager; validation do
Config.from_dict (qua ConfigManager.validate) quyết định, UI không ghi file.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from src.models.config import Config
from src.ui import form, state
from src.ui.form import DIRS, key
from src.ui.labels import T, edit_mode_text

S = st.session_state
RUN_LOCKED_STATES = ("RUNNING", "PAUSED")
SAMPLE = {
    "name": "Giao lộ mẫu - lệch hướng Đông Tây",
    "rates_per_min": {"N": 12, "S": 9, "E": 18, "W": 7},
    "initial_queue": {"N": 7, "S": 4, "E": 16, "W": 5},
    "seed": 2026,
}


# ----------------------------------------------------------------------
# Callbacks (chạy trước khi script rerun, được phép sửa session_state)
# ----------------------------------------------------------------------
def _select(config_id: str | None) -> None:
    S.selected_config_id = S.sel_box = config_id
    S.editor_mode, S.pending_action = "EDIT", None
    cfg = state.get_config(config_id)
    form.load_form(cfg if cfg else form.default_payload(""))


def on_select() -> None:
    S.notice = None
    _select(S.sel_box)


def on_new() -> None:
    S.editor_mode, S.pending_action, S.notice = "NEW", None, None
    form.load_form(form.default_payload(state.next_id()))


def on_save() -> None:
    payload = form.payload_from_form()
    payload["id"] = state.next_id()
    ok, message = S.manager.create(payload)
    S.notice = ("ok" if ok else "error", message)
    if ok:
        _select(payload["id"])


def on_update() -> None:
    payload = form.payload_from_form()
    ok, message = S.manager.update(S.selected_config_id, payload)
    S.notice = ("ok" if ok else "error", message)
    if ok:
        form.load_form(state.get_config(S.selected_config_id))


def on_use() -> None:
    S.use_config_id = S.selected_config_id
    S.notice = ("ok", f"Đã chọn '{S.use_config_id}' cho lần Start tiếp theo.")


def on_delete_ask() -> None:
    S.pending_action = "delete"


def on_cancel() -> None:
    S.pending_action = None


def on_delete_confirm() -> None:
    config_id = S.selected_config_id
    ok, message = S.manager.delete(config_id)
    S.notice, S.pending_action = ("ok" if ok else "error", message), None
    if ok:
        if S.use_config_id == config_id:
            S.use_config_id = None
        S.selected_config_id = S.sel_box = None   # không tự chọn âm thầm bản khác
        S.editor_mode = "EDIT"
        form.load_form(form.default_payload(""))


def _restore_form() -> None:
    if S.editor_mode == "NEW":
        on_new()
    else:
        cfg = state.get_config(S.selected_config_id)
        if cfg:
            form.load_form(cfg)


def on_reset() -> None:
    S.pending_action = "reset" if S.get("_dirty") else None
    if S.pending_action is None:
        _restore_form()


def on_reset_confirm() -> None:
    S.pending_action = None
    _restore_form()


def on_seed_sample() -> None:
    payload = form.default_payload(state.next_id())
    payload.update({k: v for k, v in SAMPLE.items()})
    payload["motion_2d"]["clearance_limit_s"] = 30.0
    ok, message = S.manager.create(payload)
    S.notice = ("ok" if ok else "error", message)
    if ok:
        _select(payload["id"])


def on_reload() -> None:
    S.notice = None
    state.reload_data()


# ----------------------------------------------------------------------
# Helpers hiển thị
# ----------------------------------------------------------------------
def _card(title: str):
    container = st.container(border=True)
    container.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
    return container


def _hint(text: str) -> None:
    st.markdown(f'<div class="hint">{text}</div>', unsafe_allow_html=True)


def _field_error(flat: str, err_key: str | None, err_text: str) -> None:
    if err_key == flat and err_text:
        st.markdown(f'<div class="field-err">{escape(err_text)}</div>', unsafe_allow_html=True)


def _validate(payload: dict) -> tuple[bool, str]:
    if S.manager is not None:
        is_update = S.editor_mode == "EDIT"
        return S.manager.validate(payload, is_update=is_update,
                                  config_id=S[key("id")] if is_update else None)
    try:
        Config.from_dict(payload)
        return True, ""
    except (ValueError, TypeError) as error:
        return False, str(error)


def _status(config_id: str) -> str:
    chosen, used = config_id == S.selected_config_id, config_id == S.use_config_id
    return "Đang chọn · đang dùng" if chosen and used else "Đang chọn" if chosen else "Đang dùng" if used else "—"


def _table(configs: list[dict]) -> str:
    head = (
        "<tr><th>Configuration ID</th><th>Tên cấu hình</th>"
        + "".join(f"<th>Lưu lượng {d}<small>xe/phút</small></th>" for d in DIRS)
        + "<th>Ngân sách xanh</th><th>Số chu kỳ</th><th>Trạng thái lựa chọn</th></tr>"
    )
    widths = [10.5, 25, 7.8, 7.8, 7.8, 7.8, 10.5, 7.2, 15.5]
    cols = "".join(f'<col style="width:{w}%">' for w in widths)
    if not configs:
        rows = '<tr><td colspan="9" class="empty-row">Chưa có cấu hình nào trong data/junctions.json.</td></tr>'
    else:
        rows = ""
        for cfg in configs:
            cls = ' class="sel"' if cfg["id"] == S.selected_config_id else ""
            rates = cfg["rates_per_min"]
            rows += (
                f"<tr{cls}><td>{escape(cfg['id'])}</td><td>{escape(cfg['name'])}</td>"
                + "".join(f"<td>{rates[d]:g}</td>" for d in DIRS)
                + f"<td>{cfg['green_budget_s']} giây</td><td>{cfg['cycles_to_run']}</td>"
                f"<td>{_status(cfg['id'])}</td></tr>"
            )
    return f'<table class="cfg-table"><colgroup>{cols}</colgroup>{head}{rows}</table>'


# ----------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------
def render_config_tab() -> None:
    configs = state.configs()
    ids = [c["id"] for c in configs]
    manager_ok = S.manager is not None
    is_new = S.editor_mode == "NEW"
    selected = S.selected_config_id
    no_selection = (not is_new) and selected is None
    locked = no_selection or not manager_ok and not is_new

    payload = form.payload_from_form()
    if no_selection:
        valid, message = False, ""
    else:
        valid, message = _validate(payload)
    err_key, err_text = form.explain_error(message) if (not valid and message) else (None, "")
    if no_selection:
        dirty = False
    elif is_new:
        dirty = payload != form.default_payload(S[key("id")])
    else:
        saved = state.get_config(selected)
        dirty = saved is None or payload != saved
    S["_dirty"] = dirty

    engine = S.get("engine")
    run_locked = bool(engine is not None and engine.state in RUN_LOCKED_STATES
                      and S.run_config_snapshot and S.run_config_snapshot.get("id") == selected)

    # ---- Danh sách cấu hình ----
    with _card("Danh sách cấu hình · Xem, chọn và quản lý các giao lộ"):
        st.markdown(_table(configs), unsafe_allow_html=True)
        col_sel, col_note, col_seed = st.columns([1.3, 4, 1.7])
        with col_sel:
            st.selectbox("Chọn theo ID", ids, key="sel_box", index=None,
                         placeholder="Chọn cấu hình", on_change=on_select, disabled=not ids)
        with col_note:
            _hint("st.selectbox + bảng chỉ đọc · ID không sửa trực tiếp trong bảng")
        if manager_ok and not ids:
            with col_seed:
                st.button("Tạo cấu hình mẫu", key="btn_seed", on_click=on_seed_sample)

    # ---- Banner trạng thái ----
    with st.container(border=True):
        if is_new:
            banner = f"Đang tạo: {escape(S[key('id')])} | Cấu hình mới | Chế độ: tạo mới"
        elif selected:
            cfg_now = state.get_config(selected) or {"name": ""}
            banner = (f"Đang chọn: {escape(selected)} | {escape(cfg_now['name'])} | "
                      f"Chế độ: {edit_mode_text(selected)}")
        else:
            banner = "Chưa chọn cấu hình · chọn theo ID hoặc bấm Tạo mới"
        st.markdown(f'<p class="banner">{banner}</p>', unsafe_allow_html=True)
        problems = []
        if S.load_error:
            problems.append(S.load_error)
        if err_text:
            problems.append(err_text)
        if run_locked:
            problems.append("Cấu hình đang chạy trong phiên mô phỏng; Stop hoặc Reset trước khi xóa.")
        if problems:
            st.markdown('<ul class="err-list">' + "".join(f"<li>{escape(p)}</li>" for p in problems) + "</ul>",
                        unsafe_allow_html=True)
        if S.notice:
            kind, text = S.notice
            st.markdown(f'<div class="{"field-err" if kind == "error" else "ok-line"}">{escape(text)}</div>',
                        unsafe_allow_html=True)
        if S.load_error:
            st.button("Tải lại dữ liệu", key="btn_reload", on_click=on_reload)

    # ---- Lưới 3 cột ----
    left, mid, right = st.columns([26, 31.5, 32.5], gap="small")

    def num(flat: str, label: str, **kw) -> None:
        st.number_input(label, key=key(flat), disabled=locked, **kw)
        _field_error(flat, err_key, err_text)

    with left:
        with _card("Thông tin chung"):
            st.text_input("Tên cấu hình", key=key("name"), disabled=locked)
            _field_error("name", err_key, err_text)
            st.text_input("Configuration ID · hệ thống quản lý / chỉ đọc", key=key("id"), disabled=True)
        with _card("Lưu lượng bốn hướng"):
            for col, d in zip(st.columns(4), DIRS):
                with col:
                    num(f"rate_{d}", f"{d} · xe/phút", step=1.0, format="%g")
        with _card("Hàng chờ ban đầu · Initial Queue"):
            for col, d in zip(st.columns(4), DIRS):
                with col:
                    num(f"queue_{d}", f"Initial {d} · xe", step=1)
        _hint("N/S/E/W bắt buộc · ID giữ nguyên khi cập nhật")

    with mid:
        with _card("Thông số tín hiệu"):
            for pair in (("green_budget_s", "Green Budget · giây", "min_green_s", "Min Green · giây"),
                         ("yellow_s", "Yellow · giây", "all_red_s", "All Red · giây"),
                         ("startup_delay_s", "Startup Delay · giây", "headway_s", "Headway · giây")):
                a, b = st.columns(2)
                with a:
                    num(pair[0], pair[1], step=1)
                with b:
                    num(pair[2], pair[3], step=1)
            _hint("Ràng buộc: Green Budget ≥ 2 × Min Green")
        with _card("Thông số mô phỏng"):
            a, b = st.columns(2)
            with a:
                num("cycles_to_run", "Số chu kỳ · 1–100", step=1)
            with b:
                num("seed", "Random seed · số nguyên", step=1)
        with _card(T["validation_title"]):
            if problems or err_text:
                st.markdown('<ul class="err-list">' + "".join(f"<li>{escape(p)}</li>" for p in problems) + "</ul>",
                            unsafe_allow_html=True)
            else:
                _hint("Thiếu tên / ID trùng · Sai lưu lượng / thiếu hướng · Sai xanh / motion")

    with right:
        with _card("Thông số chuyển động 2D"):
            st.toggle("Bật motion 2D · enabled = true", key=key("m_enabled"), disabled=locked)
            _field_error("m_enabled", err_key, err_text)
            rows = (
                (("m_dt_s", "dt · giây / substep", "%g"), ("m_vehicle_length_m", "Vehicle Length · mét", "%.1f")),
                (("m_min_gap_m", "Min Gap · mét", "%.1f"), ("m_max_speed_mps", "Max Speed · m/s", "%.1f")),
                (("m_accel_mps2", "Acceleration · m/s²", "%.1f"), ("m_approach_visible_m", "Approach Visible · mét", "%.1f")),
                (("m_intersection_width_m", "Intersection Width · mét", "%.1f"), ("m_stop_margin_m", "Stop Margin · mét", "%.1f")),
            )
            for left_f, right_f in rows:
                a, b = st.columns(2)
                with a:
                    num(left_f[0], left_f[1], step=0.1, format=left_f[2])
                with b:
                    num(right_f[0], right_f[1], step=0.1, format=right_f[2])
            a, b = st.columns(2)
            with a:
                num("m_clearance_limit_s", "Clearance Limit · giây", step=1.0, format="%g")
            with b:
                dt = S[key("m_dt_s")]
                steps = f"{round(1 / dt)}" if isinstance(dt, (int, float)) and dt > 0 else "—"
                _hint(f"dt = {dt:g} → {steps} substep/tick<br>Thông số mô phỏng học thuật"
                      if isinstance(dt, (int, float)) and dt > 0 else "dt chưa hợp lệ")

    # ---- Thanh nút hành động ----
    can_edit = manager_ok and not no_selection
    bar = st.columns([145, 185, 157, 226, 238, 229, 575], gap="small")
    bar[0].button("Tạo mới", key="btn_new", on_click=on_new, disabled=is_new)
    bar[1].button("Lưu cấu hình", key="btn_save", on_click=on_save,
                  disabled=not (manager_ok and is_new and valid))
    bar[2].button("Cập nhật", key="btn_update", on_click=on_update,
                  disabled=not (can_edit and not is_new and valid and dirty))
    bar[3].button("Xóa · cần xác nhận", key="btn_delete", on_click=on_delete_ask,
                  disabled=not (can_edit and not is_new) or run_locked)
    bar[4].button("Dùng cấu hình này", key="btn_use", on_click=on_use,
                  disabled=not (can_edit and not is_new) or dirty)
    bar[5].button("Làm mới biểu mẫu", key="btn_reset", on_click=on_reset, disabled=no_selection)
    with bar[6]:
        with st.container(border=True):
            action = S.pending_action
            if action == "delete" and selected:
                st.markdown(f'<p class="banner" style="font-size:16px">Xác nhận xóa {escape(selected)}? '
                            "[Hủy] [Xác nhận xóa]</p>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.button("Hủy", key="btn_cancel", on_click=on_cancel)
                c2.button("Xác nhận xóa", key="btn_confirm", on_click=on_delete_confirm)
            elif action == "reset":
                st.markdown('<p class="banner" style="font-size:16px">Bỏ thay đổi chưa lưu? '
                            "[Hủy] [Bỏ thay đổi]</p>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.button("Hủy", key="btn_cancel", on_click=on_cancel)
                c2.button("Bỏ thay đổi", key="btn_confirm", on_click=on_reset_confirm)
            else:
                label = f"Xác nhận xóa {escape(selected)}? [Hủy] [Xác nhận xóa]" if selected else "Xác nhận xóa? [Hủy] [Xác nhận xóa]"
                st.markdown(f'<p class="banner" style="font-size:16px">{label}</p>', unsafe_allow_html=True)
                _hint(T["confirm_idle"])

    st.markdown(
        '<p class="foot">Enabled: thao tác hợp lệ · Disabled: sai chế độ / dữ liệu lỗi · '
        "Lỗi hiển thị dưới trường và trong banner</p>"
        '<p class="foot">Nguồn mẫu: docs/examples/junctions_v2.example.json · '
        "ID do ConfigManager cấp · UI không ghi file trực tiếp</p>",
        unsafe_allow_html=True,
    )
