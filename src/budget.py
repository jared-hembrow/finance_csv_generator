from datetime import date, timedelta
from src.date_tools import Weeks, DateMap
from src.os_tools import load_all_budget_json_from_folder, load_json, write_csv


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

    def __init__(
        self,
        folder_path_list="config/budgets",
        config_file_path="config/config.json",
        out_path="budget.csv",
    ):
        config = load_json(config_file_path)
        self.config = config
        self.out_path = out_path

        # CONFIG
        self.start_month = config["start_month"]
        self.start_year = config["start_year"]
        self.end_month = config["end_month"]
        self.end_year = config["end_year"]
        self.weekday_start = config["weekday_start"]

        self.start_date = date(self.start_year, self.start_month, 1)
        self.end_date = date(self.end_year, self.end_month, 30)

        self.weeks = Weeks(self.start_date, self.end_date)
        self.date_map = DateMap(
            self.start_date - timedelta(days=7), self.end_date + timedelta(days=7)
        )

        # Get budgets
        self.budget_list = load_all_budget_json_from_folder(folder_path_list)
        # for path in folder_path_list:
        #     self.budget_list.append(self.handle_json(path))

    def create_date_cell(self, ss):
        split_date = ss.strftime("%Y-%m-%d").split("-")
        return f"=DATE({split_date[0]}, {split_date[1]}, {split_date[2]})"

    def sort_budget_lists(self):
        pass

    def create_main_header(self):
        return ["Date", "Item", "Total", "Paid", "W/Total", "W/Paid"]

    def create_week_header_row(self, row_num, sub_row_count, week):
        start_date = week.start_date
        end_date = week.end_date
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
        # self.date_map.years = date_tools.create_year_to_day(
        #     date(self.start_year, self.start_month, 1),
        #     date(self.end_year, self.end_month, 1),
        # )
        # self.weeks = date_tools.get_weeks(
        #     self.start_month, self.start_year, self.end_month, self.end_year
        # )
        self.sort_budget_items()
        self.create_csv()
        write_csv("test_budget.csv", self.csv_rows)
        print("Build Complete!")

    def check_date_within_range(self, date_item):
        the_month = date_item.month
        the_year = date_item.year
        if (
            the_year == self.end_year
            and the_month > self.end_month
            or the_year == self.start_year
            and the_month < self.start_month
        ):
            return False
        return True

    def sort_weekly_interval(self, item):
        start_date = self.start_date
        end_date = self.end_date
        the_weekday = self.days[item["withdrawn"]] - 1

        current_date = start_date
        while current_date.weekday() != self.weekday_start:  # 0 represents start_day
            current_date -= timedelta(days=1)
        # Iterate week by week
        while current_date <= end_date or current_date <= end_date + timedelta(days=6):
            the_date = current_date + timedelta(days=the_weekday)
            if the_date.day in self.date_map.years[the_date.year][the_date.month]:
                self.date_map.years[the_date.year][the_date.month][the_date.day][
                    "items"
                ].append(item)
            # Move to the next Week
            current_date += timedelta(weeks=1)

    def sort_monthly_interval(self, item):
        if isinstance(item["withdrawn"], int):
            the_day = item["withdrawn"]
            for year in self.date_map.years:
                for month in self.date_map.years[year]:
                    if the_day in self.date_map.years[year][month]:
                        self.date_map.years[year][month][the_day]["items"].append(item)

        elif "last" in item["withdrawn"]:
            the_weekday = self.days[item["withdrawn"].split("last ")[1]]
            for year in self.date_map.years:
                for month in self.date_map.years[year]:
                    the_last_weekday = 0
                    # Find the last weekday of that month
                    for day in self.date_map.years[year][month]:
                        if not self.check_date_within_range(
                            date(int(year), int(month), int(day))
                        ):
                            continue
                        if (
                            self.date_map.years[year][month][day]["weekday"]
                            == the_weekday
                        ):
                            the_last_weekday = self.date_map.years[year][month][day][
                                "date"
                            ].day
                    if the_last_weekday > 0:

                        self.date_map.years[year][month][the_last_weekday][
                            "items"
                        ].append(item)

    def sort_quarterly_interval(self, item):
        the_day = item["withdrawn"]
        for quart in range(0, 4):
            the_month = quart + 3
            for year in self.date_map.years:
                if not self.check_date_within_range(
                    date(int(year), the_month, the_day)
                ):
                    continue
                if f"{the_month}" in self.date_map.years[year]:
                    self.date_map.years[year][f"{the_month}"][f"{the_day}"][
                        "items"
                    ].append(item)

    def sort_yearly_interval(self, item):
        the_month = item["month"]
        the_day = item["withdrawn"]
        for year in self.date_map.years:
            # if not self.check_date_within_range(date(int(year), the_month, the_day)):
            #     continue
            if (
                the_month in self.date_map.years[year]
                and the_day in self.date_map.years[year][the_month]
            ):
                self.date_map.years[year][the_month][the_day]["items"].append(item)

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

    def populate_weeks(self):
        start_date = self.weeks.start_date
        end_date = self.weeks.end_date
        for week in self.weeks.weeks:
            pass

    def create_csv(self):
        print("Creating CSV")
        rows = [self.create_main_header()]
        row_count = 1
        for week in self.date_map.weeks.weeks:
            if week.end_date > self.end_date or week.start_date < self.start_date:
                continue
            data_rows_for_week = []

            for day in week.days:

                if (
                    day.year in self.date_map.years
                    and day.month in self.date_map.years[day.year]
                    and day.day in self.date_map.years[day.year][day.month]
                ):

                    day_data = self.date_map.years[day.year][day.month][day.day]
                    if len(day_data["items"]) < 1:
                        continue
                    data_rows_for_week += [
                        self.create_row(i, day.date) for i in day_data["items"]
                    ]

            row_count += 1
            sub_row_count = len(data_rows_for_week)
            rows.append(self.create_week_header_row(row_count, sub_row_count, week))
            data_rows_for_week.reverse()
            rows += data_rows_for_week
            row_count += sub_row_count
        self.csv_rows = rows


# new_budget = Budget(
#     ["budget_1.json", "budget_2.json", "budget_2.json"], "budget_config.json"
# )
# new_budget.build()
