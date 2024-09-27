from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.schemas.metrics import Period


def get_date_range(period: Period) -> (datetime, datetime):
    """
    Returns the start and end dates based on the specified period.
    """
    end_date = datetime.utcnow()

    if period == Period.ALL:
        start_date = datetime.min
    elif period == Period.YEAR_TO_DATE:
        start_date = datetime(year=end_date.year, month=1, day=1)
    elif period == Period.ONE_DAY:
        start_date = end_date - timedelta(days=1)
    elif period == Period.ONE_WEEK:
        start_date = end_date - timedelta(weeks=1)
    elif period == Period.ONE_MONTH:
        start_date = end_date - relativedelta(months=1)
    elif period == Period.THREE_MONTHS:
        start_date = end_date - relativedelta(months=3)
    elif period == Period.SIX_MONTHS:
        start_date = end_date - relativedelta(months=6)
    elif period == Period.ONE_YEAR:
        start_date = end_date - relativedelta(years=1)
    elif period == Period.THREE_YEARS:
        start_date = end_date - relativedelta(years=3)
    elif period == Period.FIVE_YEARS:
        start_date = end_date - relativedelta(years=5)
    elif period == Period.TEN_YEARS:
        start_date = end_date - relativedelta(years=10)
    else:
        raise ValueError("Unsupported period.")

    return start_date, end_date
