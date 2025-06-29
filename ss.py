import re
import csv


def create_date_cell(ss):
    split_date = ss.split("/")
    return f"=DATE({split_date[2]}, {split_date[1]}, {split_date[0]})"


def get_date(row):

    # date_string_full = "Value Date: 17/06/2025"
    date_string = row[2]
    string_list = date_string.split("Value Date: ")
    print(string_list)
    print(f"Has Date: {len(string_list) > 1}")
    result = {"Date": create_date_cell(row[0]), "WD/Date": create_date_cell(row[0])}
    if len(string_list) > 1:
        result["Date"] = create_date_cell(string_list[1])
    return result
    # Pattern to find DD/MM/YYYY
    # \d{2} matches exactly two digits (for day, month)
    # \d{4} matches exactly four digits (for year)
    # \/ matches the literal forward slash
    # pattern = r"\b(\d{2}/\d{2}/\d{4})\b"  # \b are word boundaries for more precise matching

    # match = re.search(pattern, date_string_full)

    # if match:
    #     date_part = match.group(
    #         1
    #     )  # group(1) refers to the content inside the first parenthesis
    #     print(date_part)
    #     # Output: 17/06/2025
    # else:
    #     print("No date found in the expected format.")


file_path = "june-july.csv"  # Replace with the actual path to your CSV file

data = []
sorted_data = []
try:
    with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    print("CSV loaded successfully (as list of lists):")
    sorted_list = []
    for i, row in enumerate(data):  # Print first 5 rows
        dates = get_date(row)

        # new_row = {
        #     "T Value": row[1],
        #     "Description": row[2],
        #     "Acc Update": row[3],
        #     **dates,
        # }
        sorted_data.append([dates["Date"], dates["WD/Date"], row[1], row[2], row[3]])
        # print(new_row)

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

for i, row in enumerate(sorted_data[:10]):  # Print first 5 rows
    print(f"Row {i+1}: {row}")


try:
    # Open the file in write mode ('w')
    # newline='' is crucial to prevent extra blank rows
    # encoding='utf-8' is recommended for broad character support
    with open("sorted_d.csv", "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write all rows at once
        csv_writer.writerows(sorted_data)

    print(f"Data successfully written to '{file_path}' (list of lists).")

except Exception as e:
    print(f"An error occurred: {e}")
# Accessing data:
# print(data[0])    # Header row
# print(data[1][0]) # First cell of the first data row
