from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from services.dossier_service import build_draft

app = FastAPI(title="HO_SO_BOT")

# Payload DEMO để bấm chạy là ra file ngay
DEMO_PAYLOAD = {
    "header": {
        "SO_HD_CORE": "25",
        "NGAY_HD": "2025-03-15",
        "KH_TEN": "Công ty TNHH ABC",
        "KH_DIA_CHI": "123 Đường XYZ, Quận 1, TP.HCM",
        "KH_DAI_DIEN": "Nguyễn Văn A",
        "KH_CHUC_VU": "Giám đốc",
        "VAT": 8
    },
    "services": [
        {"TEN_DV": "Cung cấp & lắp đặt máy lạnh", "DVT": "Gói", "SO_LUONG": 1, "DON_GIA": 4567000},
        {"TEN_DV": "Thi công hệ thống điện", "DVT": "Gói", "SO_LUONG": 1, "DON_GIA": 1234000}
    ],
    "materials": [
        {"service_idx": 1, "TEN_VT": "Ống đồng 1HP", "DVT": "Mét", "SO_LUONG": 5},
        {"service_idx": 1, "TEN_VT": "Gas R32", "DVT": "Kg", "SO_LUONG": 2},
        {"service_idx": 2, "TEN_VT": "Cáp điện Cadivi 2.5mm", "DVT": "Mét", "SO_LUONG": 30}
    ]
}

@app.get("/")
def root():
    return {"status": "ok", "message": "HO_SO_BOT is running. Open /docs to test."}

@app.get("/demo")
def demo_payload():
    return DEMO_PAYLOAD

@app.post("/draft")
def draft(payload: dict = Body(...)):
    """Render bộ nháp 5 file theo payload."""
    result = build_draft(payload)
    return JSONResponse(result)

# (tuỳ chọn) Endpoint 1 nút chạy demo, khỏi dán JSON
@app.post("/draft-demo")
def draft_demo():
    return build_draft(DEMO_PAYLOAD)
