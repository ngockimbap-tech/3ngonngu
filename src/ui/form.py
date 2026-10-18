"""Ánh xạ giữa ô nhập của Tab 1 và payload JSON V2 của một cấu hình.

Không có luật validation ở đây: Config.from_dict (qua ConfigManager.validate)
là nguồn chuẩn. Module này chỉ gom giá trị form và dịch thông báo lỗi của
Config thành câu hiển thị dưới đúng ô nhập.
"""
from __future__ import annotations

import copy
from typing import Any

import streamlit as st

from src.models.config import Config

DIRS = ("N", "S", "E", "W")
SCALAR_KEYS = ("green_budget_s", "min_green_s", "yellow_s", "all_red_s",
               "startup_delay_s", "headway_s", "cycles_to_run", "seed")
MOTION_KEYS = ("enabled", "dt_s", "vehicle_length_m", "min_gap_m", "max_speed_mps",
               "accel_mps2", "approach_visible_m", "intersection_width_m",
               "stop_margin_m", "clearance_limit_s")
FIELD_LABELS = {
    "green_budget_s": "Green Budget", "min_green_s": "Min Green", "yellow_s": "Yellow",
    "all_red_s": "All Red", "startup_delay_s": "Startup Delay", "headway_s": "Headway",
    "cycles_to_run": "Số chu kỳ", "seed": "Random seed", "dt_s": "dt",
    "vehicle_length_m": "Vehicle Length", "min_gap_m": "Min Gap", "max_speed_mps": "Max Speed",
    "accel_mps2": "Acceleration", "approach_visible_m": "Approach Visible",
    "intersection_width_m": "Intersection Width", "stop_margin_m": "Stop Margin",
    "clearance_limit_s": "Clearance Limit",
}


def key(flat: str) -> str:
    """Khóa session_state của một ô nhập."""
    return f"f_{flat}"


def load_form(cfg: dict[str, Any]) -> None:
    """Nạp một cấu hình (dict JSON V2) vào các ô nhập. Chỉ gọi trong callback."""
    S = st.session_state
    S[key("id")] = cfg["id"]
    S[key("name")] = cfg["name"]
    for d in DIRS:
        S[key(f"rate_{d}")] = float(cfg["rates_per_min"][d])
        S[key(f"queue_{d}")] = int(cfg["initial_queue"][d])
    for name in SCALAR_KEYS:
        S[key(name)] = int(cfg[name])
    motion = cfg["motion_2d"]
    S[key("m_enabled")] = bool(motion["enabled"])
    for name in MOTION_KEYS[1:]:
        S[key(f"m_{name}")] = float(motion[name])


def payload_from_form() -> dict[str, Any]:
    """Gom giá trị ô nhập thành dict đúng schema V2 (không ép kiểu thêm)."""
    S = st.session_state
    payload: dict[str, Any] = {
        "id": S[key("id")],
        "name": S[key("name")],
        "rates_per_min": {d: S[key(f"rate_{d}")] for d in DIRS},
        "initial_queue": {d: S[key(f"queue_{d}")] for d in DIRS},
    }
    for name in SCALAR_KEYS:
        payload[name] = S[key(name)]
    payload["motion_2d"] = {name: S[key(f"m_{name}")] for name in MOTION_KEYS}
    return payload


def default_payload(config_id: str) -> dict[str, Any]:
    """Bản nháp cho cấu hình mới: mặc định của Config, tên để trống cho người dùng nhập."""
    data = copy.deepcopy(Config().to_dict())
    data["id"] = config_id
    data["name"] = ""
    return data


def explain_error(message: str) -> tuple[str | None, str]:
    """Dịch thông báo lỗi của Config thành (khóa ô nhập, câu hiển thị)."""
    text = message.strip()
    if text.startswith("rates_per_min.") and len(text) > 14:
        d = text[14]
        return f"rate_{d}", f"Lưu lượng {d} phải là số hữu hạn từ 0 đến 30 xe/phút."
    if text.startswith("initial_queue.") and len(text) > 14:
        d = text[14]
        return f"queue_{d}", f"Số xe ban đầu hướng {d} phải là số nguyên từ 0 đến 100."
    if text.startswith("name"):
        return "name", "Vui lòng nhập tên cấu hình."
    if text.startswith("green_budget_s"):
        return "green_budget_s", "Green Budget phải là số nguyên và ≥ 2 × Min Green."
    if text.startswith("cycles_to_run"):
        return "cycles_to_run", "Số chu kỳ phải là số nguyên từ 1 đến 100."
    if text.startswith("dt_s") or text.startswith("1 / dt_s"):
        return "m_dt_s", "dt phải ≤ 1 và chia 1 giây thành số bước nguyên (ví dụ 0.2 giây = 5 bước)."
    for name in SCALAR_KEYS:
        if text.startswith(name):
            return name, f"{FIELD_LABELS[name]} phải là số nguyên trong miền hợp lệ."
    for name in MOTION_KEYS[2:]:
        if text.startswith(name):
            kind = "≥ 0" if name in ("min_gap_m", "stop_margin_m") else "> 0"
            return f"m_{name}", f"{FIELD_LABELS[name]} phải là số hữu hạn {kind}."
    if text.startswith("enabled"):
        return "m_enabled", "Bật motion 2D phải là true hoặc false."
    return None, text
