import pandas as pd


def xlsx_to_csv(name):
    read_file = pd.read_excel(f'{name}.xlsx', sheet_name="Vehicles")
    read_file.to_csv(f'{name}.csv', index=None, header=True)
    with open(f'{name}.csv', 'r', encoding='utf-8') as file:
        line = file.readlines()
    return f"{len(line) - 1} {'line was' if len(line) - 1 == 1 else 'lines were'} added to {name}.csv"


print("Input file name")
f_name = input().split(".")
print(xlsx_to_csv(f_name[0]))
