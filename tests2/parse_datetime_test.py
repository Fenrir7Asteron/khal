import khal.parse_datetime as parse_datetime
import pytest
import datetime
import pytz
from freezegun import freeze_time

from khal.exceptions import DateTimeParseError, FatalError

BERLIN = pytz.timezone('Europe/Berlin')
NEW_YORK = pytz.timezone('America/New_York')

LOCALE_BERLIN = {
    'default_timezone': BERLIN,
    'local_timezone': BERLIN,
    'dateformat': '%d.%m.',
    'longdateformat': '%d.%m.%Y',
    'timeformat': '%H:%M',
    'datetimeformat': '%d.%m. %H:%M',
    'longdatetimeformat': '%d.%m.%Y %H:%M',
    'unicode_symbols': True,
    'firstweekday': 0,
    'weeknumbers': False,
}

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


@freeze_time('2020-02-29')
def test_guesstimedeltafstr():
    assert parse_datetime.guesstimedeltafstr('1d 1h 15m 30s') == datetime.timedelta(days=1, hours=1, minutes=15, seconds=30)
    with pytest.raises(ValueError):
        parse_datetime.guesstimedeltafstr('--1d 1h 15m 30s')
    with pytest.raises(ValueError):
        parse_datetime.guesstimedeltafstr('1d 1h 15m 30k')


@freeze_time('2020-02-27')
def test_guessrangefstr():
    assert parse_datetime.guessrangefstr(
        ['2020/03/10-10:30', '1 day 10 minute'],
        LOCALE_NEW_YORK,
        adjust_reasonably=True
    ) == \
           (datetime.datetime(2020, 3, 10, 10, 30), datetime.datetime(2020, 3, 11, 10, 40), False)
    assert parse_datetime.guessrangefstr(
        '2020/03/10', LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1),
        adjust_reasonably=True
    ) == (datetime.datetime(2020, 3, 10), datetime.datetime(2020, 3, 11), True)
    assert parse_datetime.guessrangefstr(
        '2020/03/10-10:31', LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(minutes=1),
        adjust_reasonably=True
    ) == (datetime.datetime(2020, 3, 10, 10, 31), datetime.datetime(2020, 3, 10, 10, 32), False)
    assert parse_datetime.guessrangefstr(
        ['2020/03/10-02:04', 'eod'], LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1)
    ) == (datetime.datetime(2020, 3, 10, 2, 4), datetime.datetime.combine(datetime.datetime(2020, 3, 10), datetime.time.max), False)
    assert parse_datetime.guessrangefstr(
        ['2020/03/10-10:00', '2020/03/10-12:00'], LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1)
    ) == (datetime.datetime(2020, 3, 10, 10), datetime.datetime(2020, 3, 10, 12), False)
    assert parse_datetime.guessrangefstr(
        ['2019/03/10', '2020/03/12'], LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1),
        adjust_reasonably=True
    ) == (datetime.datetime(2019, 3, 10), datetime.datetime(2019, 3, 13), True)
    # TODO: bug that when START is allday and END is not it adds additional day to end, but it should not
    assert parse_datetime.guessrangefstr(
        ['2019/03/10', '2020/03/12-10:30'], LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1),
        adjust_reasonably=True
    ) == (datetime.datetime(2019, 3, 10), datetime.datetime(2019, 3, 12, 10, 30), True)
    assert parse_datetime.guessrangefstr(
        ['2020/03/13', '2020/03/10'], LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1),
        adjust_reasonably=True
    ) == (datetime.datetime(2020, 3, 13), datetime.datetime(2021, 3, 11), True)
    assert parse_datetime.guessrangefstr(
        ['2020/03/13-10:30', '2020/03/12-9:30'], LOCALE_NEW_YORK,
        default_timedelta_date=datetime.timedelta(days=1),
        default_timedelta_datetime=datetime.timedelta(hours=1),
        adjust_reasonably=True
    ) == (datetime.datetime(2020, 3, 13, 10, 30), datetime.datetime(2020, 3, 14, 9, 30), False)

    with pytest.raises(DateTimeParseError):
        parse_datetime.guessrangefstr(
            ['10.03.2020 09:30', '10:30 13.03.2020'], LOCALE_BERLIN,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1)
        )

    with pytest.raises(DateTimeParseError):
        parse_datetime.guessrangefstr(
            ['03/10-10:30'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1)
        )

    with pytest.raises(DateTimeParseError):
        parse_datetime.guessrangefstr([], LOCALE_NEW_YORK)

    with pytest.raises(FatalError):
        parse_datetime.guessrangefstr(
            ['2020/03/10', '10 minute'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1)
        )
    with pytest.raises(FatalError):
        parse_datetime.guessrangefstr(
            ['2020/03/10-10:00', '0 second'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1)
        )

    # TODO: Check why there are 8 days in a week. May be a bug, may be some strange logic.
    assert parse_datetime.guessrangefstr('week', LOCALE_NEW_YORK) == \
       (datetime.datetime(2020, 3, 1), datetime.datetime(2020, 3, 8), True)

    assert parse_datetime.guessrangefstr(['2020/03/02', 'week'], LOCALE_NEW_YORK) == \
           (datetime.datetime(2020, 3, 8), datetime.datetime(2020, 3, 15), True)


@freeze_time('2020-02-29')
def test_eventinfofstr():
    assert parse_datetime.eventinfofstr(
        '2020/03/10-10:31 2020/03/10-10:36 :: Some description',
        LOCALE_NEW_YORK,
        adjust_reasonably=True
    ) == {
        'dtstart': datetime.datetime(2020, 3, 10, 10, 31),
        'dtend': datetime.datetime(2020, 3, 10, 10, 36),
        'summary': None,
        'description': 'Some description',
        'timezone': NEW_YORK,
        'allday': False
    }

    # TODO: Check that resetting timezone to None if allday is a bug.
    assert parse_datetime.eventinfofstr(
        '2020/03/10 America/New_York Summary',
        LOCALE_NEW_YORK,
        adjust_reasonably=True
    ) == {
               'dtstart': datetime.date(2020, 3, 10),
               'dtend': datetime.date(2020, 3, 11),
               'summary': 'Summary',
               'description': None,
               'timezone': NEW_YORK,
               'allday': True
           }

    with pytest.raises(DateTimeParseError):
        parse_datetime.eventinfofstr(
            '2020/03//10-10:31 America/New_York Summary',
            LOCALE_NEW_YORK,
            adjust_reasonably=True
        )