import json
import csv


def extract_between_substrings(file_path, start_substring, end_substring):
    result = []
    within_range = False

    with open(file_path, "r") as file:
        for line in file:
            if start_substring in line:
                within_range = True
                continue
            elif end_substring in line:
                break
            if within_range:
                result.append(line.strip())

    return result


def log_to_csv(log_path: str, csv_file_path: str):
    data = extract_between_substrings(log_path, "Activities log:", "Trade History:")
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for line in data:
            writer.writerow(line.split(";"))



