import pandas as pd
import re
import sqlite3


def xlsx_to_csv(name):
    read_file = pd.read_excel(name + ".xlsx", sheet_name="Vehicles")
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


def csv_to_s3db(name):
    name = name.strip("[CHECKED]")
    with open(f'{name.strip()}[CHECKED].csv', 'r', encoding='utf-8') as file:
        db_convoy = file.readline().strip().split(",")
        conn = sqlite3.connect(f'{name}.s3db')
        convoy = conn.cursor()

        lines = convoy.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='convoy';").fetchall()
        if lines[0][0] != 0:
            convoy.execute(f"DROP TABLE convoy;")
            conn.commit()

        convoy.execute(f"CREATE TABLE IF NOT EXISTS convoy({db_convoy[0]} INTEGER PRIMARY KEY, {db_convoy[1]} INTEGER NOT NULL, {db_convoy[2]} INTEGER NOT NULL, {db_convoy[3]} INTEGER NOT NULL);")
        conn.commit()
        for line in file:
            line = line.strip().split(",")
            convoy.execute(f"INSERT INTO convoy({db_convoy[0]},{db_convoy[1]},{db_convoy[2]},{db_convoy[3]}) "
                           f"VALUES({line[0]},{line[1]},{line[2]},{line[3]})")
        conn.commit()

        base = convoy.execute("SELECT COUNT(*) FROM convoy")
        db_len = base.fetchone()[0]
        conn.close()
        return f"{db_len} {'record was' if db_len == 1 else 'records were'} inserted into {name}.s3db"


print("Input file name")
f_name = input().split(".")
if f_name[1] == "xlsx":
    print(xlsx_to_csv(f_name[0]))
if f_name[1] in ["csv", "xlsx"] and not ".".join(f_name).endswith("[CHECKED].csv"):
    print(xlsx_to_csv_checked(f_name[0]))
print(csv_to_s3db(f_name[0]))
