import os
import json
import csv


def load_all_budget_json_from_folder(folder_path):
    """
    Loads the content of all JSON files found in the specified folder.

    Args:
        folder_path (str): The path to the folder containing JSON files.

    Returns:
        list: A list of Python objects (dictionaries or lists) parsed from the JSON files.
              Returns an empty list if the folder does not exist or contains no JSON files.
              Prints error messages for files that could not be read or parsed.
    """
    json_contents = []

    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'")
        return []

    print(f"Searching for JSON files in: '{folder_path}'")

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            print(f"  Found JSON file: '{filename}'")
            json_contents.append(load_json(file_path))
    return json_contents


def load_json(file_path):
    print("Load JSON:", file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"    Successfully loaded '{file_path}'")
            return data
    except json.JSONDecodeError as e:
        print(f"    Error: Could not decode JSON from '{file_path}': {e}")
    except FileNotFoundError:
        print(
            f"    Error: File not found (should not happen for listed files): '{file_path}'"
        )
    except Exception as e:
        print(f"    An unexpected error occurred while reading '{file_path}': {e}")
        # else:
        #     print(f"  Skipping non-JSON file: '{filename}'") # Uncomment to see skipped files


def write_csv(fp, data):
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
