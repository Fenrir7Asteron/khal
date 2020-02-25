import khal.parse_datetime as parse_datetime
import pytest
import datetime
import pytz
from freezegun import freeze_time

from khal.exceptions import DateTimeParseError, FatalError

NEW_YORK = pytz.timezone('America/New_York')

LOCALE_NEW_YORK = {
    'default_timezone': NEW_YORK,
    'local_timezone': NEW_YORK,
    'timeformat': '%H:%M',
    'dateformat': '%Y/%m/%d',
    'longdateformat': '%Y/%m/%d',
    'datetimeformat': '%Y/%m/%d-%H:%M',
    'longdatetimeformat': '%Y/%m/%d-%H:%M',
    'firstweekday': 6,
    'unicode_symbols': True,
    'weeknumbers': False,
}


# ====== WHITE BOX TESTS ======


def test_weekdaypstr():
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for num, day in enumerate(weekdays):
        assert parse_datetime.weekdaypstr(day) == num

    with pytest.raises(ValueError):
        parse_datetime.weekdaypstr("other_day")


@freeze_time('2020-02-29')
def test_construct_daynames():
    assert parse_datetime.construct_daynames(datetime.date(2020, 2, 29))
    assert parse_datetime.construct_daynames(datetime.date(2020, 3, 1))
    assert parse_datetime.construct_daynames(datetime.date(2020, 2, 28))


@freeze_time('2020-02-29')
def test_datetimefstr():
    assert parse_datetime.datetimefstr(['28.02'], '%d.%m', default_day=None, infer_year=True, in_future=True).timestamp() == datetime.datetime(2021, 2, 28).timestamp()
    assert parse_datetime.datetimefstr(['28.02'], '%d.%m', default_day=datetime.date(2020, 4, 10), infer_year=True, in_future=False).timestamp() == datetime.datetime(2021, 2, 28).timestamp()
    assert parse_datetime.datetimefstr(['2022.28.02'], '%Y.%d.%m', default_day=datetime.date(2020, 4, 10), infer_year=False, in_future=False).timestamp() == datetime.datetime(2022, 2, 28).timestamp()
    with pytest.raises(ValueError):
        parse_datetime.datetimefstr(['2021.29.02'], '%Y.%d.%m', default_day=datetime.date(2021, 2, 28), infer_year=True, in_future=False)


@freeze_time('2020-02-29')
def test_calc_day():
    assert parse_datetime.calc_day("today") == datetime.datetime.now()
    assert parse_datetime.calc_day("tomorrow") == datetime.datetime.now() + datetime.timedelta(days=1)
    assert parse_datetime.calc_day("yesterday") == datetime.datetime.now() - datetime.timedelta(days=1)
    assert parse_datetime.calc_day("sunday") == datetime.datetime(2020, 3, 1)


@freeze_time('2020-02-29')
def test_datefstr_weekday():
    with pytest.raises(ValueError):
        parse_datetime.datefstr_weekday([], None)
    assert parse_datetime.datefstr_weekday(['monday'], None) == datetime.datetime(2020, 3, 2)


@freeze_time('2020-02-29')
def test_datetimefstr_weekday():
    with pytest.raises(ValueError):
        parse_datetime.datetimefstr_weekday([], None)
    assert parse_datetime.datetimefstr_weekday(['monday', '10:30'], '%H:%M') == datetime.datetime(2020, 3, 2, 10, 30)


@freeze_time('2020-02-29')
def test_guessdatetimefstr():
    assert parse_datetime.guessdatetimefstr(['monday', '10:30'], LOCALE_NEW_YORK, default_day=None, in_future=True) == (datetime.datetime(2020, 3, 2, 10, 30), False)
    assert parse_datetime.guessdatetimefstr(['10:30'], LOCALE_NEW_YORK, default_day=None, in_future=True) == (datetime.datetime(2020, 2, 29, 10, 30), False)
    assert parse_datetime.guessdatetimefstr(['24:00'], LOCALE_NEW_YORK, default_day=None, in_future=True) == (datetime.datetime(2020, 2, 29, 0, 0), False)
    assert parse_datetime.guessdatetimefstr(['now'], LOCALE_NEW_YORK, default_day=None, in_future=True) == (datetime.datetime(2020, 2, 29, 0, 0), False)
    assert parse_datetime.guessdatetimefstr(['today'], LOCALE_NEW_YORK, default_day=None, in_future=True) == (datetime.datetime(2020, 2, 29, 0, 0), True)
    assert parse_datetime.guessdatetimefstr(['monday'], LOCALE_NEW_YORK, default_day=None, in_future=True) == (datetime.datetime(2020, 3, 2), True)
    assert parse_datetime.guessdatetimefstr(['2020/03/02'], LOCALE_NEW_YORK, default_day=datetime.datetime.now(), in_future=True) == (datetime.datetime(2020, 3, 2), True)
    with pytest.raises(DateTimeParseError):
        parse_datetime.guessdatetimefstr(['not now'], LOCALE_NEW_YORK, default_day=None, in_future=True)


def test_timedelta2str():
    assert parse_datetime.timedelta2str(-datetime.timedelta(days=2, hours=3, minutes=10, seconds=24)) == '-2d -3h -10m -24s'
    assert parse_datetime.timedelta2str(datetime.timedelta(seconds=24)) == '24s'
    assert parse_datetime.timedelta2str(datetime.timedelta(minutes=5)) == '5m'


@freeze_time('2020-02-29')
def test_rrulefstr():
    assert parse_datetime.rrulefstr('daily', 'monday', LOCALE_NEW_YORK) == {'freq': 'daily', 'until': datetime.datetime(2020, 3, 2)}
    assert parse_datetime.rrulefstr('daily', None, LOCALE_NEW_YORK) == {'freq': 'daily'}
    with pytest.raises(FatalError):
        parse_datetime.rrulefstr('every morning', None, LOCALE_NEW_YORK)