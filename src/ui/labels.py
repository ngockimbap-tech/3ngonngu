"""Nhãn chữ có thể đổi giữa bản wireframe và bản chạy thật.

WIREFRAME_MODE = True: dùng đúng các dòng chữ trong ảnh thiết kế (kể cả dòng
"dữ liệu minh họa"). Mặc định False vì giao diện đang hiển thị kết quả mô phỏng
thật, nên không nên ghi là minh họa.
"""
WIREFRAME_MODE = False

_WIREFRAME = {
    "header_sub": "Task 5 · Wireframe desktop · Chưa phải giao diện đã triển khai",
    "badge": "THIẾT KẾ / DỮ LIỆU MINH HỌA",
    "validation_title": "Vị trí lỗi validation · trạng thái minh họa",
    "counters_title": "Counters lũy kế phiên · dữ liệu minh họa",
    "chart_caption": "DỮ LIỆU MINH HỌA · KHÔNG PHẢI KẾT QUẢ THỰC",
    "status_suffix": " (mẫu)",
    "confirm_idle": "Khung minh họa bước xác nhận, chưa thực hiện xóa.",
}
_LIVE = {
    "header_sub": "Task 5 · Giao diện Streamlit · Mô phỏng đèn giao thông thông minh",
    "badge": "TRANG WEB MÔ PHỎNG",
    "validation_title": "Vị trí lỗi validation",
    "counters_title": "Counters lũy kế phiên",
    "chart_caption": "DỮ LIỆU TỪ PHIÊN MÔ PHỎNG HIỆN TẠI",
    "status_suffix": "",
    "confirm_idle": "Chưa có thao tác nào đang chờ xác nhận.",
}
T = _WIREFRAME if WIREFRAME_MODE else _LIVE


def edit_mode_text(config_id: str) -> str:
    """Wireframe ghi 'chỉnh sửa bản mẫu' cho JCT-001."""
    return "chỉnh sửa bản mẫu" if WIREFRAME_MODE and config_id == "JCT-001" else "chỉnh sửa"
