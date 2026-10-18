"""Ghi và xuất CSV thống kê phiên mô phỏng.

Tách khỏi FileStorage (JSON cấu hình) để không đụng file đã ổn định; có thể
gộp vào FileStorage sau. Header cố định theo hợp đồng Task 5, ghi UTF-8, mỗi
run_id chỉ được ghi một lần (idempotent).
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from src.core.statistics import CycleMetric, SimulationSummary

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_PATH = DATA_DIR / "sim_history.csv"
CYCLES_PATH = DATA_DIR / "cycle_metrics.csv"

HISTORY_HEADER = [
    "run_id", "started_at_iso", "config_id", "mode", "seed", "cycles_completed",
    "simulation_seconds", "initial_vehicles", "arrived_vehicles", "departed_vehicles",
    "remaining_vehicles", "exited_vehicles", "avg_wait_departed_s", "avg_stopped_delay_s",
    "max_queue", "avg_queue", "clearance_hold_s", "status",
]
CYCLE_HEADER = [
    "run_id", "cycle_index", "green_ns_s", "green_ew_s", "q_ns_start", "q_ew_start",
    "q_ns_end", "q_ew_end", "arrivals_ns", "arrivals_ew", "departed_ns", "departed_ew",
    "avg_queue", "actual_cycle_s", "clearance_hold_s",
]


def cycle_row(run_id: str, metric: CycleMetric) -> dict[str, object]:
    return {
        "run_id": run_id, "cycle_index": metric.cycle_index,
        "green_ns_s": metric.green_ns_s, "green_ew_s": metric.green_ew_s,
        "q_ns_start": metric.q_ns_start, "q_ew_start": metric.q_ew_start,
        "q_ns_end": metric.q_ns_end, "q_ew_end": metric.q_ew_end,
        "arrivals_ns": metric.arrivals_ns, "arrivals_ew": metric.arrivals_ew,
        "departed_ns": metric.departed_ns, "departed_ew": metric.departed_ew,
        "avg_queue": round(metric.avg_queue, 3), "actual_cycle_s": metric.actual_cycle_s,
        "clearance_hold_s": metric.clearance_hold_s,
    }


def _existing_run_ids(path: Path, header: list[str]) -> set[str]:
    """Đọc run_id đã có; header sai thì dừng, không ghi đè."""
    if not path.exists() or path.stat().st_size == 0:
        return set()
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != header:
            raise ValueError(f"Header CSV '{path.name}' không khớp hợp đồng; cần migration thủ công.")
        return {row["run_id"] for row in reader}


def _append_rows(path: Path, header: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    try:
        with open(path, "a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            if needs_header:
                writer.writeheader()
            writer.writerows(rows)
            handle.flush()
    except OSError as error:
        raise RuntimeError(
            f"Chưa ghi được '{path.name}'; kiểm tra file đang mở hoặc quyền ghi: {error}") from error


class HistoryStorage:
    """Ghi lịch sử phiên; trả False nếu run_id đã tồn tại (không ghi trùng)."""

    @staticmethod
    def append_run(summary: SimulationSummary, cycles: list[CycleMetric],
                   history_path: Path = HISTORY_PATH, cycles_path: Path = CYCLES_PATH) -> bool:
        history_path, cycles_path = Path(history_path), Path(cycles_path)
        if summary.run_id in _existing_run_ids(history_path, HISTORY_HEADER):
            return False
        closed = [cycle_row(summary.run_id, m) for m in cycles if not m.provisional]
        if closed and summary.run_id in _existing_run_ids(cycles_path, CYCLE_HEADER):
            return False
        if closed:
            _append_rows(cycles_path, CYCLE_HEADER, closed)
        _append_rows(history_path, HISTORY_HEADER, [summary.to_row()])
        return True


def summary_csv_text(summary: SimulationSummary, cycles: list[CycleMetric]) -> str:
    """CSV xuất cho người dùng: một dòng Summary, rồi các chu kỳ đã chốt."""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=HISTORY_HEADER, lineterminator="\n")
    writer.writeheader()
    writer.writerow(summary.to_row())
    closed = [cycle_row(summary.run_id, m) for m in cycles if not m.provisional]
    if closed:
        out.write("\n")
        cycle_writer = csv.DictWriter(out, fieldnames=CYCLE_HEADER, lineterminator="\n")
        cycle_writer.writeheader()
        cycle_writer.writerows(closed)
    return out.getvalue()
