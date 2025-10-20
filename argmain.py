import argparse
import time
import csv


Filename = "expense.csv"
fields = ["ID", "Datetime", "Description", "Amount"]
parser = argparse.ArgumentParser()
# func allow to write down a desc with multiple values like "buy banana" 
# where "buy" and "banana" will be in a list of arguments.
parser.add_argument("-d", "--description", nargs="+", help="Add a description to your expense")

parser.add_argument("-a", "--amount", help="How much does it cost")

parser.add_argument("add", help="call the func that adds the expense to the file")

args = parser.parse_args()
expense = ['id', time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime()), "".join(args.description), f"${args.amount}"]
print(expense)
rows = []
def load_data(filename: str):
    # добавить проверку на то что файл не пустой и существует вообще.
    # если файл пустой вылетает ошибка StopIteration так как next() нет куда применить
# сделать нужно через os модуль. проверить что он есть fileexists и то что не пустой через его размер(пустой файл ничего не весит в памяти)   
        rows = []
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            rows.append(row)
    
    return fields, rows

def add_data(expense: list):
    x = list(load_data("expense.csv"))
    expense_id = len(x)
    expense[0] = expense_id
    x.append(expense)
    print(x)
    with open("expense.csv", 'a', encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(x)
    print(f"Expense added successfully (ID : {expense_id})")

add_data(expense)
print(load_data(Filename))
