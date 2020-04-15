import pytest
import datetime
from freezegun import freeze_time
from khal.parse_datetime import *
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


# ====== BLACK BOX TESTS ======

class TestWeekdaypstr:
    def test_empty(self):
        with pytest.raises(ValueError):
            weekdaypstr("")


@freeze_time('2020-02-29')
class TestConstructDaynames:
    def test_weekdays(self):
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for num, day in enumerate(weekdays):
            assert construct_daynames(datetime.date(2000, 4, 3 + num)).lower() == day


@freeze_time('2020-02-29')
class TestDatetimefstr:
    def test_leap_29_february(self):
        assert datetimefstr(['2024.29.02'], '%Y.%d.%m', infer_year=False).timestamp() == \
               datetime.datetime(2024, 2, 29).timestamp()

    def test_forward(self):
        assert datetimefstr(['05.03'], '%d.%m', infer_year=True, in_future=False).timestamp() == \
               datetime.datetime(2020, 3, 5).timestamp()

    def test_backward(self):
        assert datetimefstr(['16.02'], '%d.%m', infer_year=True, in_future=False).timestamp() == \
               datetime.datetime(2021, 2, 16).timestamp()

    def test_infer_year_fail(self):
        with pytest.raises(ValueError):
            datetimefstr(['05.03'], '%d.%m', infer_year=False, in_future=False).timestamp()

    def test_wrong_year(self):
        with pytest.raises(ValueError):
            datetimefstr(['05.03.1900'], '%d.%m%Y', infer_year=False, in_future=False).timestamp()

    def test_wrong_month(self):
        with pytest.raises(ValueError):
            datetimefstr(['05.13'], '%d.%m', infer_year=True, in_future=False).timestamp()

    def test_wrong_day(self):
        with pytest.raises(ValueError):
            datetimefstr(['32.12'], '%d.%m', infer_year=True, in_future=False).timestamp()

    def test_format_mismatch(self):
        with pytest.raises(ValueError):
            datetimefstr(['30.12'], '%d-%m', infer_year=True, in_future=False).timestamp()

    def test_wrong_format(self):
        with pytest.raises(ValueError):
            datetimefstr(['30-12-2000'], '%d-%m-%E', infer_year=True, in_future=False).timestamp()


@freeze_time('2020-02-29')
class TestCalcDay:
    def test_invalid(self):
        with pytest.raises(ValueError):
            calc_day("Wrong_Day")

    def test_empty(self):
        with pytest.raises(ValueError):
            calc_day("")


@freeze_time('2020-02-29')
class TestDatefstrWeekday:
    def test_monday_tuesday(self):
        assert datefstr_weekday(['monday', 'tuesday'], None) == datetime.datetime(2020, 3, 2)

    def test_today(self):
        assert datefstr_weekday(['today', 'tomorrow'], None) == datetime.datetime(2020, 2, 29)

    def test_tomorrow(self):
        assert datefstr_weekday(['tomorrow', 'today'], None) == datetime.datetime(2020, 3, 1)


@freeze_time('2020-02-29')
class TestDatetimefstrWeekday:
    def test_24(self):
        with pytest.raises(ValueError):
            assert datetimefstr_weekday(['monday', '24:00'], '%H:%M')

    def test_date(self):
        with pytest.raises(ValueError):
            datetimefstr_weekday(['wednesday'], "")

    # def test_seconds(self):
    #     assert datetimefstr_weekday(['monday', '10:30:59'], '%H:%M:%S') == datetime.datetime(2020, 3, 2, 10, 30, 59)


@freeze_time('2020-02-29')
class TestGuessdatetimefstr:
    def test_tomorrow(self):
        assert guessdatetimefstr(['tomorrow'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 3, 1, 0, 0), True)

    def test_berlin_locale(self):
        assert guessdatetimefstr(['03.03.', '10:30'], LOCALE_BERLIN, in_future=False) == \
               (datetime.datetime(2020, 3, 3, 10, 30), False)

    def test_empty(self):
        with pytest.raises(ValueError):
            guessdatetimefstr([], LOCALE_BERLIN, in_future=False)


class TestTimedelta2str:
    def test_days_hours(self):
        assert timedelta2str(datetime.timedelta(days=1, hours=10)) == '1d 10h'

    def test_days_minutes(self):
        assert timedelta2str(datetime.timedelta(days=5, minutes=30)) == '5d 30m'

    def test_days_seconds(self):
        assert timedelta2str(datetime.timedelta(days=3, seconds=51)) == '3d 51s'

    def test_hours_minutes(self):
        assert timedelta2str(datetime.timedelta(hours=10, minutes=20)) == '10h 20m'

    def test_hours_seconds(self):
        assert timedelta2str(datetime.timedelta(hours=10, seconds=50)) == '10h 50s'

    def test_minutes_seconds(self):
        assert timedelta2str(datetime.timedelta(minutes=20, seconds=43)) == '20m 43s'

    def test_overseconds(self):
        assert timedelta2str(datetime.timedelta(seconds=93923)) == '1d 2h 5m 23s'

    def test_overminutes(self):
        assert timedelta2str(datetime.timedelta(minutes=5885)) == '4d 2h 5m'

    def test_overhours(self):
        assert timedelta2str(datetime.timedelta(hours=25)) == '1d 1h'

    def test_2years(self):
        assert timedelta2str(datetime.timedelta(days=365*2)) == '730d'


@freeze_time('2020-02-29')
class TestRrulefstr:
    def test_daily_none(self):
        assert rrulefstr('daily', None, LOCALE_NEW_YORK) == \
               {'freq': 'daily'}

    def test_daily_until_friday(self):
        assert rrulefstr('daily', 'friday', LOCALE_NEW_YORK) == \
               {'freq': 'daily', 'until': datetime.datetime(2020, 3, 6)}

    def test_weekly_none(self):
        assert rrulefstr('weekly', None, LOCALE_NEW_YORK) == \
               {'freq': 'weekly'}

    def test_weekly_until_friday(self):
        assert rrulefstr('weekly', 'friday', LOCALE_NEW_YORK) == \
               {'freq': 'weekly', 'until': datetime.datetime(2020, 3, 6)}

    def test_monthly_none(self):
        assert rrulefstr('monthly', None, LOCALE_NEW_YORK) == \
               {'freq': 'monthly'}

    def test_monthly_until_friday(self):
        assert rrulefstr('monthly', 'friday', LOCALE_NEW_YORK) == \
               {'freq': 'monthly', 'until': datetime.datetime(2020, 3, 6)}

    def test_yearly_none(self):
        assert rrulefstr('yearly', None, LOCALE_NEW_YORK) == \
               {'freq': 'yearly'}

    def test_yearly_until_friday(self):
        assert rrulefstr('yearly', 'friday', LOCALE_NEW_YORK) == \
               {'freq': 'yearly', 'until': datetime.datetime(2020, 3, 6)}

    def test_daily_format(self):
        assert rrulefstr('daily', '2020/04/20', LOCALE_NEW_YORK) == \
               {'freq': 'daily', 'until': datetime.datetime(2020, 4, 20)}

    def test_empty_repeat(self):
        with pytest.raises(ValueError):
            rrulefstr('', '2020/04/20', LOCALE_NEW_YORK)

    def test_empty_until(self):
        with pytest.raises(ValueError):
            rrulefstr('monthly', '', LOCALE_NEW_YORK)

    def test_none_format(self):
        with pytest.raises(ValueError):
            rrulefstr('monthly', '2020/04/20', None)

    def test_format_mismatch(self):
        with pytest.raises(DateTimeParseError):
            rrulefstr('monthly', '2020.04.20', LOCALE_NEW_YORK)


@freeze_time('2020-02-29')
class TestGuesstimedeltafstr:
    def test_days_hours(self):
        assert guesstimedeltafstr('5d 13h') == datetime.timedelta(days=5, hours=13)

    def test_days_minutes(self):
        assert guesstimedeltafstr('5d 20m') == datetime.timedelta(days=5, minutes=20)

    def test_days_seconds(self):
        assert guesstimedeltafstr('5d 16s') == datetime.timedelta(days=5, seconds=16)

    def test_hours_minutes(self):
        assert guesstimedeltafstr('10h 14m') == datetime.timedelta(hours=10, minutes=14)

    def test_hours_seconds(self):
        assert guesstimedeltafstr('10h 14s') == datetime.timedelta(hours=10, seconds=14)

    def test_minutes_seconds(self):
        assert guesstimedeltafstr('20m 50s') == datetime.timedelta(minutes=20, seconds=50)

    def test_unordered(self):
        assert guesstimedeltafstr('50s 13d 20m 2h') == datetime.timedelta(days=13, hours=2, minutes=20, seconds=50)

    def test_empty(self):
        assert guesstimedeltafstr('') == datetime.timedelta()

    def test_repeat(self):
        assert guesstimedeltafstr('2d 2d') == datetime.timedelta(days=4)


@freeze_time('2020-02-27')
class TestGuessrangefstr:
    def test_time_reasonable(self):
        assert guessrangefstr(
            '10:30', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=2),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 2, 27, 10, 30), datetime.datetime(2020, 2, 27, 12, 30), False)

    def test_time_unreasonable(self):
        assert guessrangefstr(
            '10:30', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=2),
            adjust_reasonably=False
        ) == (datetime.datetime(2020, 2, 27, 10, 30), datetime.datetime(2020, 2, 27, 12, 30), False)

    # def test_seconds_delta(self):
    #     assert guessrangefstr(
    #         '10:30', LOCALE_NEW_YORK,
    #         default_timedelta_date=datetime.timedelta(days=1),
    #         default_timedelta_datetime=datetime.timedelta(seconds=1),
    #         adjust_reasonably=True
    #     ) == (datetime.datetime(2020, 2, 27, 10, 30), datetime.datetime(2020, 2, 27, 10, 30, 1), False)

    def test_date_reasonable(self):
        assert guessrangefstr(
            '2020/04/10', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=3),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 4, 10), datetime.datetime(2020, 4, 13), True)

    def test_date_reasonable2(self):
        assert guessrangefstr(
            '2020/01/10', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=3),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2021, 1, 10), datetime.datetime(2021, 1, 13), True)

    def test_date_unreasonable(self):
        assert guessrangefstr(
            '2020/04/10', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=3),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=False
        ) == (datetime.datetime(2020, 4, 10), datetime.datetime(2020, 4, 13), True)

    def test_date_unreasonable2(self):
        assert guessrangefstr(
            '2020/01/10', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=3),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=False
        ) == (datetime.datetime(2020, 1, 10), datetime.datetime(2020, 1, 13), True)

    def test_today_reasonable(self):
        assert guessrangefstr(
            'today', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime.today(), datetime.datetime.today() + datetime.timedelta(days=2), True)

    def test_today_unreasonable(self):
        assert guessrangefstr(
            'today', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=False
        ) == (datetime.datetime.today(), datetime.datetime.today() + datetime.timedelta(days=2), True)

    def test_today_reasonable2(self):
        assert guessrangefstr(
            'today 12:00', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=23),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 2, 27, 12), datetime.datetime(2020, 2, 28, 11), False)

    def test_today_unreasonable2(self):
        assert guessrangefstr(
            'today 12:00', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=23),
            adjust_reasonably=False
        ) == (datetime.datetime(2020, 2, 27, 12), datetime.datetime(2020, 2, 28, 11), False)

    def test_tomorrow_reasonable(self):
        assert guessrangefstr(
            'tomorrow', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime.today() + datetime.timedelta(days=1),
              datetime.datetime.today() + datetime.timedelta(days=3), True)

    def test_tomorrow_unreasonable(self):
        assert guessrangefstr(
            'tomorrow', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=False
        ) == (datetime.datetime.today() + datetime.timedelta(days=1),
              datetime.datetime.today() + datetime.timedelta(days=3), True)

    def test_tomorrow_reasonable2(self):
        assert guessrangefstr(
            ['tomorrow 13:30', 'eod'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=2),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 2, 28, 13, 30),
              datetime.datetime.combine(datetime.datetime(2020, 2, 28), datetime.time.max), False)


@freeze_time('2020-02-29')
class TestEventinfofstr:
    def test_full(self):
        assert eventinfofstr(
            '2020/03/10-10:30 2020/03/10-10:36 America/New_York Summary :: Some description',
            LOCALE_NEW_YORK,
            adjust_reasonably=True
        ) == {
                   'dtstart': datetime.datetime(2020, 3, 10, 10, 30),
                   'dtend': datetime.datetime(2020, 3, 10, 10, 36),
                   'summary': 'Summary',
                   'description': 'Some description',
                   'timezone': NEW_YORK,
                   'allday': False
               }

    def test_adjust(self):
        assert eventinfofstr(
            '2020/02/10-10:30 2020/02/10-10:20 Summary',
            LOCALE_NEW_YORK,
            adjust_reasonably=True
        ) == {
                   'dtstart': datetime.datetime(2020, 2, 10, 10, 20),
                   'dtend': datetime.datetime(2020, 2, 10, 10, 30),
                   'summary': 'Summary',
                   'description': 'Some description',
                   'timezone': NEW_YORK,
                   'allday': False
               }

    def test_empty(self):
        with pytest.raises(DateTimeParseError):
            assert eventinfofstr(
                '',
                LOCALE_NEW_YORK,
                adjust_reasonably=True
            )
