from database import get_daily_financial_report_data
from service import format_daily_financial_report


report_data = get_daily_financial_report_data(
    "2026-07-28"
)

message = format_daily_financial_report(report_data)

print(message)