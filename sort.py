import csv
import re

FILE_PATH = "CSVData (1).csv"

mapping = {
    "fuel": [
        "BP",
        "AMPOL",
        "EG GROUP",
        "Reddy Express",
        "7-ELEVEN",
        "PETRO NATIONAL",
        "UNITED",
        "COLES EXPRESS",
    ],
    "shopping": ["WOOLWORTHS", "COLES", "CRAIG COOKS PRIME QUALITY"],
}


def write_list_to_csv(filepath, data, headers=None):
    """
    Writes a list of lists (or tuples) to a CSV file.

    Args:
        filepath (str): The path where the CSV file will be saved.
        data (list of lists/tuples): The data to write. Each inner list/tuple is a row.
        headers (list, optional): A list of strings for the header row.
                                  If None, no header row is written.
    """
    print(data)
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if headers:
                writer.writerow(headers)  # Write the header row first
            for r in data:
                print(r)
                writer.writerow(r)
            # writer.writerows(data)  # Write all data rows

        print(f"Data successfully written to '{filepath}'")
    except IOError as e:
        print(f"Error writing to file '{filepath}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def extract_date_from_string(text):
    """
    Extracts a date in DD/MM/YYYY format from a given string.

    Args:
        text (str): The input string to search for the date.

    Returns:
        str or None: The extracted date string if found, otherwise None.
    """
    # Regular expression to find DD/MM/YYYY pattern
    # \d{2} matches exactly two digits
    # \/ matches the literal forward slash
    # The parentheses create a capturing group for the entire date
    date_pattern = r"\b(\d{2}\/\d{2}\/\d{4})\b"

    match = re.search(date_pattern, text)

    if match:
        return match.group(
            1
        )  # group(1) returns the content of the first capturing group
    else:
        return None


def create_description(text):
    is_fuel = False
    fuel = ""
    for fuel_type in mapping["fuel"]:
        if fuel_type in text:
            is_fuel = True
            fuel = fuel_type.lower().capitalize()
    if is_fuel:
        return fuel, "fuel"

    is_shopping = False
    shopping = ""

    for shopping_type in mapping["shopping"]:
        if shopping_type in text:
            is_shopping = True
            shopping = shopping_type.lower().capitalize()
    if is_shopping:
        return shopping, "groceries"

    return "", ""


def sort_type(row):

    new_dict = {
        "date": row["Date"],
        "amount": float(row["Amount"].replace("-", "")),
        "description": row["Description"],
        "type": "",
    }
    value_date = extract_date_from_string(row["Description"])
    if value_date is not None:
        new_dict["date"] = value_date

    if "Transfer" in row["Description"]:
        return None
    if "+" in row["Amount"]:
        return None

    sorted_description = create_description(row["Description"])

    new_dict["description"] = sorted_description[0]
    new_dict["type"] = sorted_description[1]

    return new_dict


def csv_to_list_of_dicts(filepath):
    """
    Imports a CSV file and converts its rows into a list of dictionaries.
    Each dictionary represents a row, with column headers as keys.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary corresponds to a row
              in the CSV file. Returns an empty list if the file is not found
              or an error occurs during reading.
    """
    data = []
    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as file:
            # csv.DictReader automatically uses the first row as fieldnames (keys)
            reader = csv.DictReader(file)
            for row in reader:
                new_dict = sort_type(row)
                if new_dict is not None:
                    data.append(new_dict)
    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
    return data


data_list = csv_to_list_of_dicts(FILE_PATH)

# 3. Print the result to see the list of dictionaries
if data_list:
    print("CSV data as a list of dictionaries:")
    for row_dict in data_list:
        print(row_dict)


fuel_list = [r.values() for r in data_list if r["type"] == "fuel"]
shopping_list = [r.values() for r in data_list if r["type"] == "groceries"]
headers = ["date", "cost", "description", "type"]
write_list_to_csv("fuel_list.csv", fuel_list, headers)
write_list_to_csv("shopping_list.csv", shopping_list, headers)
