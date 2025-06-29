from datetime import date, timedelta


class Weeks:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.weeks = self.generate_weeks()

    def __repr__(self):
        return f"Week: ({self.start_date} - {self.end_date} - {len(self.weeks)})"

    def index_weeks_list(self):
        index_list = {}
        start_date = date()
        end_date = date()

        for index, week in enumerate(self.weeks):
            if week.start_date < start_date:
                start_date = week.start_date
            if week.end_date < end_date:
                end_date = week.end_date
            for day in week.days:
                year = day.date.year
                month = day.date.year
                day = day.date.day
                if year not in index_list:
                    index_list[year] = {}
                if month not in index_list:
                    index_list[year][month] = {}
                index_list[year][month][day] = index

    def add_week(self, week):
        if type(week) is not Week:
            print("add_week Error: week type is invalid")
            return
        self.weeks.append(week)

    def generate_weeks(self, start_day=0):
        weeks = []

        # Define the first day of the start month and the last day of the end month
        start_period_date = date(self.start_date.year, self.start_date.month, 1)

        # Calculate the last day of the end_month
        # Handle December-January transition
        if self.end_date.month == 12:
            end_period_date = date(self.end_date.year, self.end_date.month, 31)
        else:
            # Get the first day of the next month, then subtract one day
            end_period_date = date(
                self.end_date.year, self.end_date.month + 1, 1
            ) - timedelta(days=1)
        # Find the first Monday on or before the start_period_date
        current_day = start_period_date
        while current_day.weekday() != start_day:  # 0 represents start_day
            current_day -= timedelta(days=1)
        # Iterate week by week
        while (
            current_day <= end_period_date
            or current_day <= end_period_date + timedelta(days=6)
        ):
            # Calculate the Sunday of the current week
            current_end_day = current_day + timedelta(days=6)
            # Only add the week if its Monday is within or before the end of the period
            # and if the Monday itself isn't too far past the end date
            if (
                current_day <= end_period_date
                or current_day <= end_period_date + timedelta(days=6)
            ):
                weeks.append(
                    Week(
                        current_day,
                        current_end_day,
                    )
                )

            # Move to the next Monday
            current_day += timedelta(weeks=1)
        return weeks


class Week:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.days = self.generate_days()

    def generate_days(self):
        days = []
        current_date = self.start_date
        while current_date <= self.end_date:
            days.append(Day(current_date))
            current_date += timedelta(days=1)
        return days

    def __repr__(self):
        return f"Week: ({self.start_date} - {self.end_date} - {len(self.days)})"


class Day:
    def __init__(self, date):
        self.date = date
        self.day = date.day
        self.month = date.month
        self.year = date.year
        self.weekday = date.weekday()
        self.items = []

    def __repr__(self):
        return f"Week: ({self.date} - {self.weekday} - items: {len(self.items)})"


class DateMap:
    years = {}

    def __init__(self, start_date, end_date):
        print("INIT DateMap")
        if not type(start_date) == date or not type(end_date) == date:
            print(
                f"Invalid date limit inputs \n\t Start Date: {type(start_date)} - End Date: {type(end_date)}",
            )
            return
        self.start_date = start_date
        self.end_date = end_date
        self.weeks = Weeks(self.start_date, self.end_date)
        self.years = self.generate_map()

    def create_dict_item(self, data_dict, key):
        if key not in data_dict:
            data_dict[key] = {}

    def generate_map(self):
        years = {}
        current_date = self.start_date
        while current_date <= self.end_date:
            year = current_date.year
            self.create_dict_item(years, year)
            month = current_date.month
            self.create_dict_item(years[year], month)
            day = current_date.day
            self.create_dict_item(years[year][month], day)

            years[year][month][day] = {
                "date": current_date,
                "year": current_date.year,
                "month": current_date.month,
                "day": current_date.day,
                "weekday": current_date.weekday(),
                "items": [],
            }
            current_date += timedelta(days=1)
        return years
