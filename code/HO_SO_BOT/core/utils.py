import datetime as dt, re
from num2words import num2words

def proper_case_vn(text:str) -> str:
    if text is None: return ""
    def fix(w):
        if re.fullmatch(r"[A-ZĐ]{2,}", w): return w
        return w.capitalize()
    parts = re.split(r"(\s+)", (text or "").strip())
    return "".join(fix(w) if i%2==0 else w for i,w in enumerate(parts))

def format_date_vi(d: dt.date) -> str:
    return d.strftime("ngày %d tháng %m năm %Y")

def money_fmt(n: float, sep: str='.') -> str:
    s = f"{int(round(n)):,.0f}".replace(',', '_').replace('.', '_')
    return s.replace('_', sep)

def money_to_words_vi(n: float) -> str:
    return num2words(int(round(n)), lang='vi') + ' đồng'
