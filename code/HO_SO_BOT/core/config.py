from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

# Thư mục chứa 5 file mẫu _READY
TEMPLATES_DIR = BASE / "templates"

# Thư mục đầu ra (tự tạo nếu chưa có)
DRAFT_DIR = BASE / "1_ChoDuyet"
FINAL_DIR = BASE / "2_DaDuyet_ChoKy"

# Logs
LOG_DIR = BASE / "logs"
for d in [TEMPLATES_DIR, DRAFT_DIR, FINAL_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def load_rules():
    return {}
