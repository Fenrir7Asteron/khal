import khal.parse_datetime as parse_datetime
import pytest
import datetime
from freezegun import freeze_time

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
