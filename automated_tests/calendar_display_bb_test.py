import pytest
import datetime

from khal.calendar_display import *

class TestGet_weeknumber():
    def test_invalid(self):
        with pytest.raises(ValueError):
            getweeknumber("Wrong_Day")

    def test_int (self):
        with pytest.raises(ValueError):
            getweeknumber(01.10)

    def test_empty(self):
        with pytest.raises(ValueError):
            getweeknumber("")

class TestGet_calendar_color():

    def test_empty(self):
        with pytest.raises(ValueError):
            get_calendar_color("","","")

    def test_non_existing(self):
        with pytest.raises(ValueError):
            get_calendar_color("My_calendar", 34, None)


class TestStr_week():
    first_day = dt.date(2020, 1, 1)
    week = [dt.date(2020, 1, 1),
            dt.date(2020, 1, 2),
            dt.date(2020, 1, 3),
            dt.date(2020, 1, 4),
            dt.date(2020, 1, 5),
            dt.date(2020, 1, 6),
            dt.date(2020, 1, 7)]

    def test_empty_week(self):
        with pytest.raises(ValueError):
            str_week(None, self.first_day)

    def test_empty_day(self):
        with pytest.raises(ValueError):
            str_week(self.week, None)

    def test_not_full_week(self):
        self.week.pop()
        self.week.pop()
        with pytest.raises(EOFError):
            str_week(self.week, self.first_day)