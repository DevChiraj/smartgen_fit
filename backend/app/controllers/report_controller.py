"""Request/response orchestration for the weekly health report endpoint."""

from app.repositories import user_repository
from app.schemas.weekly_report_schema import WeeklyReportSchema
from app.services import weekly_report_service

weekly_report_schema = WeeklyReportSchema()


def handle_get_weekly_report(user_id: str):
    user = user_repository.get_by_id(int(user_id))
    report = weekly_report_service.get_weekly_report(user)
    return {"report": weekly_report_schema.dump(report)}, 200
