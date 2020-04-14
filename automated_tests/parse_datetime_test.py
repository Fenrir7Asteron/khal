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


# ====== WHITE BOX TESTS ======

class TestWeekdaypstr:
    def test_valid_weekdays_wb(self):
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for num, day in enumerate(weekdays):
            assert weekdaypstr(day) == num

    def test_invalid_weekdays_wb(self):
        with pytest.raises(ValueError):
            weekdaypstr("other_day")


@freeze_time('2020-02-29')
class TestConstructDaynames:
    def test_today_wb(self):
        assert construct_daynames(datetime.date(2020, 2, 29)).lower() == 'today'

    def test_tomorrow_wb(self):
        assert construct_daynames(datetime.date(2020, 3, 1)).lower() == 'tomorrow'

    def test_yesterday_wb(self):
        assert construct_daynames(datetime.date(2020, 2, 28)).lower() == 'friday'

    def test_weekdays_bb(self):
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for num, day in enumerate(weekdays):
            assert construct_daynames(datetime.date(2000, 4, 3 + num)).lower() == day


@freeze_time('2020-02-29')
class TestDatetimefstr:
    def test_no_default_day_wb(self):
        assert datetimefstr(['28.02'], '%d.%m', default_day=None,
                            infer_year=True, in_future=True).timestamp() == datetime.datetime(2021, 2, 28).timestamp()

    def test_default_day_wb(self):
        assert datetimefstr(['28.02'], '%d.%m', default_day=datetime.date(2020, 4, 10),
                            infer_year=True, in_future=False).timestamp() == datetime.datetime(2021, 2, 28).timestamp()

    def test_no_infer_year_wb(self):
        assert datetimefstr(['2022.28.02'], '%Y.%d.%m', default_day=datetime.date(2020, 4, 10),
                            infer_year=False, in_future=False).timestamp() == datetime.datetime(2022, 2, 28).timestamp()

    def test_non_leap_29_february_wb(self):
        with pytest.raises(ValueError):
            datetimefstr(['2021.29.02'], '%Y.%d.%m', default_day=datetime.date(2021, 2, 28),
                         infer_year=True, in_future=False)

    def test_leap_29_february_bb(self):
        assert datetimefstr(['2024.29.02'], '%Y.%d.%m', infer_year=False).timestamp() == \
               datetime.datetime(2024, 2, 29).timestamp()

    def test_forward_bb(self):
        assert datetimefstr(['05.03'], '%d.%m', infer_year=True, in_future=False).timestamp() == \
               datetime.datetime(2020, 3, 5).timestamp()

    def test_backward_bb(self):
        assert datetimefstr(['16.02'], '%d.%m', infer_year=True, in_future=False).timestamp() == \
               datetime.datetime(2021, 2, 16).timestamp()

    def test_infer_year_fail_bb(self):
        with pytest.raises(ValueError):
            datetimefstr(['05.03'], '%d.%m', infer_year=False, in_future=False).timestamp()

    def test_wrong_year_bb(self):
        with pytest.raises(ValueError):
            datetimefstr(['05.03.1900'], '%d.%m%Y', infer_year=False, in_future=False).timestamp()

    def test_wrong_month_bb(self):
        with pytest.raises(ValueError):
            datetimefstr(['05.13'], '%d.%m', infer_year=True, in_future=False).timestamp()

    def test_wrong_day_bb(self):
        with pytest.raises(ValueError):
            datetimefstr(['32.12'], '%d.%m', infer_year=True, in_future=False).timestamp()

    def test_format_mismatch_bb(self):
        with pytest.raises(ValueError):
            datetimefstr(['30.12'], '%d-%m', infer_year=True, in_future=False).timestamp()

    def test_wrong_format_bb(self):
        with pytest.raises(ValueError):
            datetimefstr(['30-12-2000'], '%d-%m-%E', infer_year=True, in_future=False).timestamp()


@freeze_time('2020-02-29')
class TestCalcDay:
    def test_today_wb(self):
        assert calc_day("today") == datetime.datetime.now()

    def test_tomorrow_wb(self):
        assert calc_day("tomorrow") == datetime.datetime.now() + datetime.timedelta(days=1)

    def test_yesterday_wb(self):
        assert calc_day("yesterday") == datetime.datetime.now() - datetime.timedelta(days=1)

    def test_sunday_wb(self):
        assert calc_day("sunday") == datetime.datetime(2020, 3, 1)


@freeze_time('2020-02-29')
class TestDatefstrWeekday:
    def test_empty_wb(self):
        with pytest.raises(ValueError):
            datefstr_weekday([], None)

    def test_monday_wb(self):
        assert datefstr_weekday(['monday'], None) == datetime.datetime(2020, 3, 2)


@freeze_time('2020-02-29')
class TestDatetimefstrWeekday:
    def test_empty_wb(self):
        with pytest.raises(ValueError):
            datetimefstr_weekday([], None)

    def test_monday_wb(self):
        assert datetimefstr_weekday(['monday', '10:30'], '%H:%M') == datetime.datetime(2020, 3, 2, 10, 30)


@freeze_time('2020-02-29')
class TestGuessdatetimefstr:
    def test_monday_date_wb(self):
        assert guessdatetimefstr(['monday', '10:30'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 3, 2, 10, 30), False)

    def test_time_wb(self):
        assert guessdatetimefstr(['10:30'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 2, 29, 10, 30), False)

    def test_end_of_day_wb(self):
        assert guessdatetimefstr(['24:00'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 2, 29, 0, 0), False)

    def test_now_wb(self):
        assert guessdatetimefstr(['now'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 2, 29, 0, 0), False)

    def test_today_wb(self):
        assert guessdatetimefstr(['today'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 2, 29, 0, 0), True)

    def test_monday_datetime_wb(self):
        assert guessdatetimefstr(['monday'], LOCALE_NEW_YORK, in_future=True) == \
               (datetime.datetime(2020, 3, 2), True)

    def test_date_wb(self):
        assert guessdatetimefstr(['2020/03/02'], LOCALE_NEW_YORK, default_day=datetime.datetime.now(), in_future=True) \
               == (datetime.datetime(2020, 3, 2), True)

    def test_invalid_wb(self):
        with pytest.raises(DateTimeParseError):
            guessdatetimefstr(['not now'], LOCALE_NEW_YORK, in_future=True)


class TestTimedelta2str:
    def test_negative_wb(self):
        assert timedelta2str(-datetime.timedelta(days=2, hours=3, minutes=10, seconds=24)) == '-2d -3h -10m -24s'

    def test_seconds_wb(self):
        assert timedelta2str(datetime.timedelta(seconds=24)) == '24s'

    def test_minutes_wb(self):
        assert timedelta2str(datetime.timedelta(minutes=5)) == '5m'


@freeze_time('2020-02-29')
class TestRrulefstr:
    def test_every_monday_wb(self):
        assert rrulefstr('daily', 'monday', LOCALE_NEW_YORK) == \
               {'freq': 'daily', 'until': datetime.datetime(2020, 3, 2)}

    def test_daily_wb(self):
        assert rrulefstr('daily', None, LOCALE_NEW_YORK) == {'freq': 'daily'}

    def test_invalid_wb(self):
        with pytest.raises(FatalError):
            rrulefstr('every morning', None, LOCALE_NEW_YORK)


@freeze_time('2020-02-29')
class TestGuesstimedeltafstr:
    def test_usual_wb(self):
        assert guesstimedeltafstr('1d 1h 15m 30s') == datetime.timedelta(days=1, hours=1, minutes=15, seconds=30)

    def test_invalid_wb(self):
        with pytest.raises(ValueError):
            guesstimedeltafstr('--1d 1h 15m 30s')

    def test_invalid_unit_wb(self):
        with pytest.raises(ValueError):
            guesstimedeltafstr('1d 1h 15m 30k')


@freeze_time('2020-02-27')
class TestGuessrangefstr:
    def test_datetime_plus_timedelta_wb(self):
        assert guessrangefstr(
            ['2020/03/10-10:30', '1 day 10 minute'],
            LOCALE_NEW_YORK,
            adjust_reasonably=True
        ) == \
               (datetime.datetime(2020, 3, 10, 10, 30), datetime.datetime(2020, 3, 11, 10, 40), False)

    def test_date_wb(self):
        assert guessrangefstr(
            '2020/03/10', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 3, 10), datetime.datetime(2020, 3, 11), True)

    def test_datetime_wb(self):
        assert guessrangefstr(
            '2020/03/10-10:31', LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(minutes=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 3, 10, 10, 31), datetime.datetime(2020, 3, 10, 10, 32), False)

    def test_datetime_plus_end_of_day_wb(self):
        assert guessrangefstr(
            ['2020/03/10-02:04', 'eod'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1)
        ) == (datetime.datetime(2020, 3, 10, 2, 4),
              datetime.datetime.combine(datetime.datetime(2020, 3, 10), datetime.time.max), False)

    def test_datetime_to_datetime_wb(self):
        assert guessrangefstr(
            ['2020/03/10-10:00', '2020/03/10-12:00'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1)
        ) == (datetime.datetime(2020, 3, 10, 10), datetime.datetime(2020, 3, 10, 12), False)

    def test_date_to_date_wb(self):
        assert guessrangefstr(
            ['2019/03/10', '2020/03/12'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2019, 3, 10), datetime.datetime(2019, 3, 13), True)

    def test_date_to_datetime_wb(self):
        # TODO: bug that when START is allday and END is not it adds additional day to end, but it should not
        assert guessrangefstr(
            ['2019/03/10', '2020/03/12-10:30'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2019, 3, 10), datetime.datetime(2019, 3, 12, 10, 30), True)

    def test_date_to_the_past_wb(self):
        assert guessrangefstr(
            ['2020/03/13', '2020/03/10'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 3, 13), datetime.datetime(2021, 3, 11), True)

    def test_datetime_to_the_past_wb(self):
        assert guessrangefstr(
            ['2020/03/13-10:30', '2020/03/12-9:30'], LOCALE_NEW_YORK,
            default_timedelta_date=datetime.timedelta(days=1),
            default_timedelta_datetime=datetime.timedelta(hours=1),
            adjust_reasonably=True
        ) == (datetime.datetime(2020, 3, 13, 10, 30), datetime.datetime(2020, 3, 14, 9, 30), False)

    def test_wrong_order_wb(self):
        with pytest.raises(DateTimeParseError):
            guessrangefstr(
                ['10.03.2020 09:30', '10:30 13.03.2020'], LOCALE_BERLIN,
                default_timedelta_date=datetime.timedelta(days=1),
                default_timedelta_datetime=datetime.timedelta(hours=1)
            )

    def test_no_year_wb(self):
        with pytest.raises(DateTimeParseError):
            guessrangefstr(
                ['03/10-10:30'], LOCALE_NEW_YORK,
                default_timedelta_date=datetime.timedelta(days=1),
                default_timedelta_datetime=datetime.timedelta(hours=1)
            )

    def test_empty_wb(self):
        with pytest.raises(DateTimeParseError):
            guessrangefstr([], LOCALE_NEW_YORK)

    def test_date_plus_timedelta_wb(self):
        with pytest.raises(FatalError):
            guessrangefstr(
                ['2020/03/10', '10 minute'], LOCALE_NEW_YORK,
                default_timedelta_date=datetime.timedelta(days=1),
                default_timedelta_datetime=datetime.timedelta(hours=1)
            )

    def test_plus_zero_wb(self):
        with pytest.raises(FatalError):
            guessrangefstr(
                ['2020/03/10-10:00', '0 second'], LOCALE_NEW_YORK,
                default_timedelta_date=datetime.timedelta(days=1),
                default_timedelta_datetime=datetime.timedelta(hours=1)
            )

    def test_week_wb(self):
        # TODO: Check why there are 8 days in a week. May be a bug, may be some strange logic.
        assert guessrangefstr('week', LOCALE_NEW_YORK) == \
               (datetime.datetime(2020, 3, 1), datetime.datetime(2020, 3, 8), True)

        assert guessrangefstr(['2020/03/02', 'week'], LOCALE_NEW_YORK) == \
               (datetime.datetime(2020, 3, 8), datetime.datetime(2020, 3, 15), True)


@freeze_time('2020-02-29')
class TestEventinfofstr:
    def test_description_wb(self):
        assert eventinfofstr(
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

    def test_allday_wb(self):
        # TODO: Check that resetting timezone to None if allday is a bug.
        assert eventinfofstr(
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

    def test_invalid_wb(self):
        with pytest.raises(DateTimeParseError):
            eventinfofstr(
                '2020/03//10-10:31 America/New_York Summary',
                LOCALE_NEW_YORK,
                adjust_reasonably=True
            )
