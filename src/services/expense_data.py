import os
import sys
import csv
from datetime import datetime

from ..constants import FIELDS


def load_data(filename: str):
    data = []
    if os.path.exists(filename) and os.path.getsize(filename) != 0:
        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                data.append(row)
    else:
        with open(filename, "w", encoding="utf-8") as file:
            pass
        data = [FIELDS]

    return data


def write_data(filename: str, data: list):
    with open(filename, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)
    print("File is rewritten.")


def get_id(data):
    # if data is empty. first row are fields.
    if len(data) == 1:
        return 1

    used_id = []
    for expense in data[1:]:
        if expense[0].isdigit():
            used_id.append(int(expense[0]))
        else:
            print("Found non digit ID. Please check it out!")

    used_id.sort()

    if used_id[0] == 2:
        return 1

    for i in range(len(used_id)):
        try:
            if used_id[i] + 1 != used_id[i + 1]:
                result = used_id[i] + 1
                break
        except IndexError:
            result = used_id[i] + 1

    return result


# checks if id exists for delete argument
def id_exists(data, id_to_delete):
    target = str(id_to_delete).strip()
    for row in data[1:]:
        if row and str(row[0]).strip() == target:
            return True
    return False


def get_summary(data, month=None):
    summary = 0
    if month:
        for expense in data[1:]:
            datetime_obj = datetime.strptime(expense[1], "%Y-%m-%d")
            if datetime_obj.month == month:
                summary += float(expense[3])
    else:
        for expense in data[1:]:
            summary += float(expense[3])
    return summary
