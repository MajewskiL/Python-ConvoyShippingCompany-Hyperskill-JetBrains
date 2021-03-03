import pandas as pd
import re


def xlsx_to_csv(name):
    read_file = pd.read_excel(name+".xlsx", sheet_name="Vehicles")
    read_file.to_csv(f'{name}.csv', index=None, header=True)
    with open(f'{name}.csv', 'r', encoding='utf-8') as file:
        line = file.readlines()
    return f"{len(line) - 1} {'line was' if len(line) - 1 == 1 else 'lines were'} added to {name}.csv"


def xlsx_to_csv_checked(name):
    out, count = [], 0
    with open(f'{name}.csv', 'r', encoding='utf-8') as file:
        out.append(file.readline())
        for line in file:
            tmp_line = [re.search(r'[\d]+', cell)[0] for cell in line.strip().split(",")]
            count += sum(1 if line.strip().split(",")[z] != tmp_line[z] else 0 for z in range(len(tmp_line)))
            out.append(tmp_line)
    with open(f'{name}[CHECKED].csv', 'w', encoding='utf-8') as file:
        file.writelines(out[0])
        for line in out[1:]:
            file.write(",".join(line) + "\n")
    return f"{count} {'cell was' if count == 1 else 'cells were'} corrected in {name}[CHECKED].csv"


print("Input file name")
f_name = input().split(".")
if f_name[1] == "xlsx":
    print(xlsx_to_csv(f_name[0]))
print(xlsx_to_csv_checked(f_name[0]))
