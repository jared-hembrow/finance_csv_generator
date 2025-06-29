from datetime import date, timedelta
import csv

template = [
    "=DATE(2025,4,28)",
    "=DATE(2025,5,4)",
    '=SUMIFS(Expanses!C:C, Expanses!A:A, ">="&DATE(2025,4,28), Expanses!A:A, "<="&DATE(2025,5,4), Expanses!C:C, ">0")',
    '=SUMIFS(Expanses!C:C, Expanses!A:A, ">="&DATE(2025,4,28), Expanses!A:A, "<="&DATE(2025,5,4), Expanses!C:C, "<0")',
    '=SUMIFS(Budget!C:C, Budget!A:A, ">="&DATE(2025,4,28), Budget!A:A, "<="&DATE(2025,5,4))',
    "=C18+D18",
]


def create_date_cell(ss):

    split_date = ss.strftime("%Y-%m-%d").split("-")
    return f"=DATE({split_date[0]}, {split_date[1]}, {split_date[2]})"


def get_monday_sunday_weeks(start_month, start_year, end_month, end_year):
    """
    Generates a list of [Monday_date, Sunday_date] pairs for each week
    within the specified date range.

    Args:
        start_month (int): The starting month (1-12).
        start_year (int): The starting year.
        end_month (int): The ending month (1-12).
        end_year (int): The ending year.

    Returns:
        list: A list of lists, where each inner list contains two datetime.date objects.
    """
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

    # Find the first Monday on or after the start_period_date
    current_monday = start_period_date
    while current_monday.weekday() != 0:  # 0 represents Monday
        current_monday += timedelta(days=1)

    # Iterate week by week
    while (
        current_monday <= end_period_date
        or current_monday <= end_period_date + timedelta(days=6)
    ):
        # Calculate the Sunday of the current week
        current_sunday = current_monday + timedelta(days=6)

        # Only add the week if its Monday is within or before the end of the period
        # and if the Monday itself isn't too far past the end date
        if (
            current_monday <= end_period_date
            or current_monday <= end_period_date + timedelta(days=6)
        ):
            week_ranges.append([current_monday, current_sunday])

        # Move to the next Monday
        current_monday += timedelta(weeks=1)

    return week_ranges


# Define your desired date range
start_m = 6
start_y = 2024
end_m = 7
end_y = 2025

# Get the list of weeks
monday_sunday_weeks = get_monday_sunday_weeks(start_m, start_y, end_m, end_y)

# convert to csv format
sorted_data = []
print(f"Weeks from {start_m}/{start_y} to {end_m}/{end_y}:")
for i, week in enumerate(monday_sunday_weeks):
    start = create_date_cell(week[0])
    end = create_date_cell(week[1])
    cell_3 = f'=SUMIFS(Expanses!C:C, Expanses!A:A, ">="&{start[1:]}, Expanses!A:A, "<="&{end[1:]}, Expanses!C:C, ">0")'
    cell_4 = f'=SUMIFS(Expanses!C:C, Expanses!A:A, ">="&{start[1:]}, Expanses!A:A, "<="&{end[1:]}, Expanses!C:C, "<0")'
    cell_5 = (
        f'=SUMIFS(Budget!C:C, Budget!A:A, ">="&{start[1:]}, Budget!A:A, "<="&{end[1:]})'
    )
    cell_6 = f"=C{i+2}+D{i+2}"
    sorted_data.append([start, end, cell_3, cell_4, cell_5, cell_6])
    # print(
    #     f"Week {i+1}: Monday {week[0].strftime('%Y-%m-%d')} - Sunday {week[1].strftime('%Y-%m-%d')}"
    # )

# print(f"\nTotal weeks found: {sorted_data}")
for i, week in enumerate(sorted_data[:5]):
    for r in week:
        print(r)
# Example of accessing a specific week:
# print("\nExample: First week entry:", monday_sunday_weeks[0])
# print("Example: Last week entry:", monday_sunday_weeks[-1])

file_path = "dash.csv"
sorted_data.reverse()
try:
    # Open the file in write mode ('w')
    # newline='' is crucial to prevent extra blank rows
    # encoding='utf-8' is recommended for broad character support
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write all rows at once
        csv_writer.writerows(sorted_data)

    print(f"Data successfully written to '{file_path}' (list of lists).")

except Exception as e:
    print(f"An error occurred: {e}")
