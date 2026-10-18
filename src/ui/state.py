"""Khởi tạo st.session_state cho ứng dụng (chỉ chạy một lần mỗi phiên trình duyệt).

Khóa chính theo hợp đồng Task 5: manager, selected_config_id, editor_mode,
pending_action, engine, run_config_snapshot, summary_saved.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from src.core.manager import ConfigManager
from src.ui import form

S = st.session_state


def _load_manager() -> None:
    """Đọc lại dữ liệu cấu hình; lỗi file được giữ lại để UI hiển thị, không crash."""
    S.manager, S.load_error = None, None
    try:
        S.manager = ConfigManager()
    except Exception as error:  # noqa: BLE001 - hiển thị nguyên nhân cho người dùng
        S.load_error = f"Không đọc được dữ liệu cấu hình: {error}"


def configs() -> list[dict[str, Any]]:
    return S.manager.list() if S.manager is not None else []


def get_config(config_id: str | None) -> dict[str, Any] | None:
    if S.manager is None or config_id is None:
        return None
    return S.manager.get(config_id)


def next_id() -> str:
    """ID mới do ConfigManager cấp (dự phòng nếu manager chưa có next_id)."""
    if S.manager is not None and hasattr(S.manager, "next_id"):
        return S.manager.next_id()
    numbers = [int(c["id"][4:]) for c in configs()
               if c["id"].startswith("JCT-") and c["id"][4:].isdigit()]
    return f"JCT-{max(numbers, default=0) + 1:03d}"


def reload_data() -> None:
    """Nạp lại cấu hình từ file và chọn lại một bản hợp lệ."""
    _load_manager()
    ids = [c["id"] for c in configs()]
    if S.selected_config_id not in ids:
        S.selected_config_id = ids[0] if ids else None
    if S.use_config_id not in ids:
        S.use_config_id = None
    S.sel_box = S.selected_config_id
    S.editor_mode, S.pending_action = "EDIT", None
    selected = get_config(S.selected_config_id)
    form.load_form(selected if selected else form.default_payload(""))


def init_session() -> None:
    if "manager" in S:
        return
    S.use_config_id = None
    S.selected_config_id = None
    S.editor_mode = "EDIT"           # "EDIT" | "NEW"
    S.pending_action = None          # None | "delete" | "reset"
    S.notice = None                  # (loại, nội dung) của lần thao tác gần nhất
    S.engine = None
    S.run_config_snapshot = None
    S.summary_saved = False
    S.pending_sim_reset = False
    S.sim_notice = None
    S.sel_box = None
    reload_data()
