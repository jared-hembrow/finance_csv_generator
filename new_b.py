from datetime import date, timedelta
import csv
import uuid
import json


class Year:
    def __init__(self, year):
        self.year = year


class Months:
    pass


class Days:
    items = []

    def __init__(self, the_date):
        self.date = the_date


class TimePeriods:
    def create_dict_item(self, data_dict, key):
        if key not in data_dict:
            data_dict[key] = {}

    def create_year_to_day(self, start_date, end_date):
        years = {}
        current_date = start_date
        print(current_date)
        while current_date <= end_date:
            year = current_date.year
            self.create_dict_item(years, year)
            month = current_date.month
            self.create_dict_item(years[f"{year}"], month)
            day = current_date.day
            self.create_dict_item(years[f"{year}"][f"{month}"], day)
            years[f"{year}"][f"{month}"][f"{day}"] = {
                "date": current_date,
                "weekday": current_date.weekday(),
            }

            current_date += timedelta(days=1)
        return years

    def get_days_time_period(self, start_date, end_date):
        days = []

        current_date = start_date
        while current_date <= end_date:
            days.append(
                {"date": current_date, "weekday": current_date.weekday(), "items": []}
            )
            current_date += timedelta(days=1)
        return days

    def get_weeks(self, start_month, start_year, end_month, end_year, start_day=0):
        week_ranges = []

        # Define the first day of the start month and the last day of the end month
        start_period_date = date(start_year, start_month, 1)

        # Calculate the last day of the end_month
        # Handle December-January transition
        if end_month == 12:
            end_period_date = date(end_year, end_month, 31)
        else:
            # Get the first day of the next month, then subtract one day
            end_period_date = date(end_year, end_month + 1, 1) - timedelta(days=1)

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
                week_dict = {
                    "start_date": current_day,
                    "end_date": current_end_day,
                    "days": self.get_days_time_period(current_day, current_end_day),
                }
                week_ranges.append(week_dict)

            # Move to the next Monday
            current_day += timedelta(weeks=1)

        return week_ranges


class Budget:
    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    years = {}
    weeks = None

    def __init__(self, file_path_list, config_file_path, out_path="budget.csv"):
        config = self.handle_json(config_file_path)
        self.config = config
        self.out_path = out_path
        self.time_periods = TimePeriods

        # CONFIG
        self.start_month = config["start_month"]
        self.start_year = config["start_year"]
        self.end_month = config["end_month"]
        self.end_year = config["end_year"]

        # Get budgets
        self.budget_list = []
        for path in file_path_list:
            self.budget_list.append(self.handle_json(path))

    def handle_json(self, fp, data={}, mode="r"):
        if mode is "w":
            with open(fp, "w") as f:
                json.dump(data, f, indent=4)  # json.dump writes directly to a file
            return "Completed"
        if mode is "r":
            print(f"\n--- Reading from {fp} ---")
            try:
                with open(fp, "r") as f:
                    loaded_data = json.load(f)  # json.load reads directly from a file
                print("Loaded data:")
                print(loaded_data)
                return loaded_data
            except FileNotFoundError:
                print(f"Error: {fp} not found.")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {fp}.")

    def create_date_cell(self, ss):
        split_date = ss.strftime("%Y-%m-%d").split("-")
        return f"=DATE({split_date[0]}, {split_date[1]}, {split_date[2]})"

    def sort_budget_lists(self):
        pass

    def create_main_header(self):
        return ["Date", "Item", "Total", "Paid", "W/Total", "W/Paid"]

    def create_week_header_row(self, row_num, sub_row_count, week):
        start_date = week[0]
        end_date = week[1]
        new_header_row = [
            f'=TEXT(DATE({start_date.year}, {start_date.month}, {start_date.day}), "DD/MM/YYYY") & " - " & TEXT(DATE({end_date.year}, {end_date.month}, {end_date.day}), "DD/MM/YYYY")',
            "",
            "",
            "",
            f"=SUM(C{row_num + 1}:C{row_num + sub_row_count})",
            f"=SUMIF(D{row_num + 1}:D{row_num + sub_row_count}, TRUE, C{row_num + 1}:C{row_num + sub_row_count})",
        ]
        return new_header_row

    def create_child_store(self, data_store, data_key, data_type="dict"):
        key = f"{data_key}"
        if key not in data_store:
            if data_type is "dict":
                data_store[key] = {}
            if data_type is "list":
                data_store[key] = []

    def create_row(self, item_dict, item_date):
        new_row = [
            self.create_date_cell(item_date),
            item_dict["name"],
            item_dict["amount"],
            "",
        ]
        if item_dict["amount"] == "average":
            new_row[2] = f"={item_dict['cell']}"
        return new_row

    def build(self):
        print("Start Build")
        date_tools = TimePeriods()
        self.years = date_tools.create_year_to_day(
            date(self.start_year, self.start_month, 1),
            date(self.end_year, self.end_month, 1),
        )
        self.weeks = date_tools.get_weeks(
            self.start_month, self.start_year, self.end_month, self.end_year
        )
        self.sort_budget_items()
        self.create_csv()
        self.write_csv("test_budget.csv", self.csv_rows)

    def sort_weekly_interval(self, item):
        for week in self.weeks:
            the_weekday = self.days[item["withdrawn"]] - 1
            the_date = week["start_date"] + timedelta(days=the_weekday)
            the_day = the_date.day
            the_month = the_date.month
            the_year = the_date.year
            if the_year >= self.end_year and the_month > self.end_month:
                continue
            self.years[f"{the_year}"][f"{the_month}"][f"{the_day}"]["items"].append(
                item
            )

    def sort_monthly_interval(self, item):
        if isinstance(item["withdrawn"], int):
            the_day = item["withdrawn"]
            for year in self.years:
                for month in self.years[year]:
                    self.years[year][month][f"{the_day}"]["items"].append(item)

        elif "last" in item["withdrawn"]:
            the_weekday = self.days[item["withdrawn"].split("last ")[1]]
            for year in self.years:
                for month in self.years[year]:
                    the_last_weekday = 0
                    # Find the last weekday of that month
                    for day in self.years[year][month]:
                        if self.years[year][month][day]["weekday"] == the_weekday:
                            the_last_weekday = self.years[year][month][day]["date"].day
                    if the_last_weekday > 0:
                        self.years[year][month][the_last_weekday].items.append(item)

    def sort_quarterly_interval(self, item):
        the_day = item["withdrawn"]
        for quart in range(0, 4):
            the_month = quart + 3
            for year in self.years:
                self.years[year][f"{the_month}"][f"{the_day}"]["items"].append(item)

    def sort_yearly_interval(self, item):
        the_month = item["month"]
        the_day = item["withdrawn"]
        for year in self.years:
            self.years[year][f"{the_month}"][f"{the_day}"]["items"].append(item)

    def sort_intervals(self, budget_item):
        interval_type = budget_item["interval"]
        if interval_type == "weekly":
            self.sort_weekly_interval(budget_item)
        elif interval_type == "monthly":
            self.sort_monthly_interval(budget_item)
        elif interval_type == "quarterly":
            self.sort_quarterly_interval(budget_item)
        elif interval_type == "yearly":
            self.sort_yearly_interval(budget_item)

    def sort_budget_items(self):
        for budget in self.budget_list:
            for item in budget["items"]:
                self.sort_intervals(item)

    def create_csv(self):
        rows = [self.create_main_header()]
        row_count = 1

        for week in self.weeks:
            data_rows_for_week = []
            start_date = week["start_date"]
            end_date = week["end_week"]
            current_date = start_date

            while current_date != end_date + timedelta(days=1):
                the_year = current_date.year
                the_month = current_date.month
                the_day = current_date.day

                the_day_data = self.years[f"{the_year}"][f"{the_month}"][f"{the_day}"]
                if len(the_day_data["items"]) > 0:
                    data_rows_for_week += [
                        self.create_row(i, current_date) for i in the_day_data["items"]
                    ]

                current_date += timedelta(days=1)

            row_count += 1
            sub_row_count = len(data_rows_for_week)
            rows.append(self.create_week_header_row(row_count, sub_row_count, week))
            rows += data_rows_for_week
            row_count += sub_row_count
        self.csv_rows = rows

    def write_csv(self, fp, data):
        try:
            # Open the file in write mode ('w')
            # newline='' is crucial to prevent extra blank rows
            # encoding='utf-8' is recommended for broad character support
            with open(fp, "w", newline="", encoding="utf-8") as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write all rows at once
                csv_writer.writerows(data)
            print(f"Data successfully written to '{fp}' (list of lists).")

        except Exception as e:
            print(f"An error occurred: {e}")


new_budget = Budget(
    ["budget_1.json", "budget_2.json", "budget_2.json"], "budget_config.json"
)
new_budget.build()
