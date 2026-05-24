"""Knowledge status checks for location-based recommendations."""
from datetime import datetime, timedelta

from app.models import TravelKnowledge


STALE_AFTER = timedelta(days=180)


def resolve_kb_status(kn: TravelKnowledge | None, now: datetime | None = None) -> str:
    if not kn or kn.review_status != "approved":
        return "miss"

    has_reason = bool((kn.recommend_reason or "").strip())
    has_tags = bool(kn.scene_tags)
    if not has_reason or not has_tags:
        return "partial"

    checked_at = kn.updated_at
    if checked_at and (now or datetime.utcnow()) - checked_at > STALE_AFTER:
        return "stale"

    return "hit"
