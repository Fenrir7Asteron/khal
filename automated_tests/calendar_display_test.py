import pytest
from khal.calendar_display import *

today = dt.date.today()
yesterday = today - dt.timedelta(days=1)
tomorrow = today + dt.timedelta(days=1)

class collection():         #for testing the calendar collections
    def __init__(self):
        self._calendars = {}

    def addCalendar(self, name, color, priority):
        self._calendars[name] = {'color': color, 'priority': priority}

class get_weeknumberTest:
    def get_year_begin(self):
        assert getweeknumber(dt.date(2020, 1, 1)) == 1
        assert getweeknumber(dt.date(2019, 12, 31)) == 53

    def get_middle(self):
        assert getweeknumber(dt.date(2020, 6, 4)) == 27
        assert getweeknumber(dt.date(2020, 1, 6)) == 2

class get_calendar_colorTest:
    collection = collection()
    collection.addCalendar('first_calendar', 'dark red', 20)
    collection.addCalendar('second_calendar', 'light green', 10)
    collection.addCalendar('third_calendar', '', 10)

    def sligthly_test_color(self):
        assert get_calendar_color('first_calendar', 'light blue', self.collection) == 'dark red'
        assert get_calendar_color('second_calendar', 'light blue', self.collection) == 'light green'

    def check_init_color(self):
        assert get_calendar_color('third_calendar', 'light blue', self.collection) == 'light blue'

    def check_code_color(self):
        self.collection.addCalendar('fourth_calendar', '34', 10)
        assert get_calendar_color('fourth_calendar', '34', 10) == '34'

    def check_format_color(self):
        self.collection.addCalendar('new_calendar', '#334455', 10)
        assert get_calendar_color('new_calendar', '#334455', 10) == '#334455'

class get_color_listTest:
    calendar_list1 = ['first_calendar', 'second_calendar']

    collection1 = collection()
    collection1.addCalendar('first_calendar', 'dark red', 20)
    collection1.addCalendar('second_calendar', 'light green', 10)

    collection2 = collection()
    collection2.addCalendar('first_calendar', 'dark red', 20)
    collection2.addCalendar('second_calendar', 'light green', 20)

    collection3 = collection()
    collection3.addCalendar('first_calendar', 'dark red', 20)
    collection3.addCalendar('second_calendar', 'dark red', 20)


    def priority_test(self):
        test_list = get_color_list(self.calendar_list1, 'light_blue', self.collection1)
        assert 'dark red' in test_list
        assert len(test_list) == 1

    def second_priority_test(self):
        test_list = get_color_list(self.calendar_list1, 'light_blue', self.collection2)
        assert 'dark red' in test_list
        assert 'light green' in test_list
        assert len(test_list) == 2

    def duplicated_colors_test(self):
        test_list = get_color_list(self.calendar_list1, 'light_blue', self.collection3)
        assert len(test_list) == 1

class str_highlight_dayTest:
    pass

class str_weekTest:
    first_day = dt.date(2020, 1, 1)
    week = [dt.date(2020, 1, 1),
            dt.date(2020, 1, 2),
            dt.date(2020, 1, 3),
            dt.date(2020, 1, 4),
            dt.date(2020, 1, 5),
            dt.date(2020, 1, 6),
            dt.date(2020, 1, 7)]

    def just_check(self):
        assert str_week(self.week, self.first_day) == ' 1  2  3  4 5 6 7 '

    def increase_week(self):
        self.week.append(dt.date(2020, 1, 8))
        assert str_week(self.week, self.first_day) == ' 1  2  3  4 5 6 7 '
        self.week.pop(-1)

    def repetition_of_day(self):
        self.week[1] = self.week[0]
        assert str_week(self.week, self.first_day) == ' 1  2  3  4 5 6 7 '
        self.week[1] = dt.date(2020, 1, 2)

    def decrease_week(self):
        self.week.pop(-1)
        assert str_week(self.week, self.first_day) == ' 1  2  3  4 5 6 7 '

class vertical_monthTest:
    pass
