# Expense tracker CLI

A lightweight CLI application for tracking and managing personal expenses, working with __CSV__ and __JSON__ data. 
The command-line interface is implemented using the standard Python library __argparse__.

## Installation

1. Clone repository
```bash
git clone https://github.com/andrii758/expense-tracker..git
cd expense_tracker
```

2. Creating and activating a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate # linux/macos
# .venv\Scripts\activate # windows
```

3. Installing requirements
```bash
pip install -r requirements.txt
```

4. Launching the application(* *from the project root folder* *)
```bash
python3 -m src.main -h
```

## Usage 

```python
main.py [-h] {add,update,list,summary,delete,set-limit} ...

positional arguments:
    add                 Add an expense
    update              Update an existing expense
    list                List all expenses
    summary             Summary expenses
    delete              Delete an expense
    set-limit           Set a budget for a certain month

options:
  -h, --help            show this help message and exit

-------- QUICK START EXAMPLES --------

1. Adding a new expense:
   $ python3 -m src.main add --amount 500 --category Food --description Coffee break

2. Setting a monthly budget limit:
   $ python3 -m src.main set-limit --month 11 --amount 30000

3. Viewing the overall summary for the current month:
   $ python3 -m src.main summary --month 10

4. Updating an existing expense (assuming expense ID is 5):
   $ python3 -m src.main update --id 5 --amount 550

---
For detailed information on the arguments for a specific command, use:
$ python3 -m src.main <command> -h
(Example: python3 -m src.main list -h)
```


andrii.p

https://roadmap.sh/projects/expense-tracker
