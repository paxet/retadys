import datetime
import businesstimedelta
import holidays as pyholidays

businesshrs = None


def workday(hours=8, minutes=0):
    global businesshrs
    # Definimos la jornada laboral. De lunes a viernes y segun las horas de trabajo
    if hours <= 12:
        start = 8
    elif hours == 24:
        start = 0
        hours = 23
        minutes = 59
    else:
        start = 0
    workd = businesstimedelta.WorkDayRule(
        start_time=datetime.time(start),
        end_time=datetime.time(hour=(start + hours), minute=minutes),
        working_days=[0, 1, 2, 3, 4])
    cva_holidays = pyholidays.ES(prov='CVA')
    holidays = businesstimedelta.HolidayRule(cva_holidays)
    businesshrs = businesstimedelta.Rules([workd, holidays])


def workhours_until_date(tarjetdate, workday_hours):
    if workday_hours:
        workday(workday_hours)
    now = datetime.datetime.now()
    if now < tarjetdate:
        diff = businesshrs.difference(now, tarjetdate).hours
    else:
        diff = 0
    return diff


def finish_datetime(hours, workday_hours):
    if workday_hours:
        workday(workday_hours)
    now = datetime.datetime.now()
    return now + businesstimedelta.BusinessTimeDelta(businesshrs, hours)
