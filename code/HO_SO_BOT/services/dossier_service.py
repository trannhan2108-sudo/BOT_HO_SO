import uuid, json
from typing import Dict, Any
from core.config import LOG_DIR
from core.render_engine import render_bundle, RenderError

def save_log(payload: Dict[str,Any]) -> str:
    doc_id = payload.get('doc_id') or uuid.uuid4().hex[:8]
    p = LOG_DIR / f"{doc_id}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return doc_id

def build_draft(payload: Dict[str,Any]) -> Dict[str,Any]:
    try:
        out_root, written = render_bundle(
            payload.get('header',{}),
            payload.get('services',[]),
            payload.get('materials',[]),
            mode='draft'
        )
        doc_id = save_log(payload)
        return {'ok': True, 'doc_id': doc_id, 'folder': str(out_root), 'written': written}
    except RenderError as e:
        return {'ok': False, 'error': str(e)}
    except Exception as e:
        return {'ok': False, 'error': f'Lỗi không mong đợi: {e.__class__.__name__}: {e}'}
