from app.database.db import SessionDep
from app.database.models import SeenOrder

from sqlalchemy.orm import Session

# =====================================================================================================
# ФИЛЬТРАЦИЯ НОВЫХ ЗАКАЗОВ
# =====================================================================================================

def filter_new(items: list[dict], platform: str, db: Session) :
    """
    Принимает список заказов с бирж, и проверяет - проверяла ли их уже ЛЛМКА,
    если да - скипает, если нет - добавляет в бд и вовращает чистый список который пойдет ЛЛМКЕ
    """
    if not items:
        return []

    incoming_ids = {item["id"] for item in items if item.get("id")}

    existing_ids = {
        row.external_id
        for row in db.query(SeenOrder.external_id)
        .filter(SeenOrder.platform == platform)
        .filter(SeenOrder.external_id.in_(incoming_ids))
        .all()
    }

    new_items = [item for item in items if item.get("id") not in existing_ids]

    for item in new_items:
        db.add(SeenOrder(platform=platform, external_id=item["id"]))

    db.commit()
    return new_items