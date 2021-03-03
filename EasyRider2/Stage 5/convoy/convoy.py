import pandas as pd
import re
import sqlite3
import json
#from lxml import etree

def xlsx_to_csv(name):
    read_file = pd.read_excel(f"{name}.xlsx", sheet_name="Vehicles")
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

        convoy.execute(f"CREATE TABLE convoy({db_convoy[0]} INTEGER PRIMARY KEY, {db_convoy[1]} INTEGER NOT NULL, {db_convoy[2]} INTEGER NOT NULL, {db_convoy[3]} INTEGER NOT NULL);")
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


def s3db_to_json(name):
    name = name.strip("[CHECKED]")
    table_name = "convoy"
    columns = ['vehicle_id', 'engine_capacity', 'fuel_consumption', 'maximum_load']
    json_data = {f"{table_name}": []}
    conn = sqlite3.connect(f'{name.strip("[CHECKED]")}.s3db')
    convoy = conn.cursor()
    convoy.execute(f"SELECT * FROM {table_name}")
    convoy = convoy.fetchall()
    conn.close()
    for record in convoy:
        tmp = {}
        for x in range(4):
            tmp[columns[x]] = record[x]
        json_data[table_name].append(tmp)
#    json_data = json.dumps(json_data, indent=4)
#    print(json_data)
    with open(f"{name}.json", "w") as json_f:
        json.dump(json_data, json_f)
    return f"{len(convoy)} {'vehicle was' if len(convoy) == 1 else 'vehicles were'} saved into {name}.json"


def s3db_to_xml(name):
    table_name = "convoy"
    tags = ['vehicle_id', 'engine_capacity', 'fuel_consumption', 'maximum_load']
    xml_data = []
    xml_data.append(f"<{table_name}>\n")
    conn = sqlite3.connect(f'{name.strip("[CHECKED]")}.s3db')
    convoy = conn.cursor()
    convoy.execute(f"SELECT * FROM {table_name}")
    convoy = convoy.fetchall()
    conn.close()
    for record in convoy:
        xml_data.append(f"    <vehicle>\n")
        for x in range(4):
            xml_data.append(f"        <{tags[x]}>{record[x]}</{tags[x]}>\n")
        xml_data.append(f"    </vehicle>\n")
    xml_data.append(f"</{table_name}>\n")
    with open(f"{name}.xml", "w") as file:
        file.writelines(xml_data)
#    root = etree.fromstring("".join(xml_data))
#    etree.dump(root)
    return f"{int(len(xml_data)/6)} {'vehicle was' if int(len(xml_data)/6) == 1 else 'vehicles were'} saved into {name}.xml"


print("Input file name")
f_name = input().split(".")
if f_name[1] in ["xlsx"]:
    print(xlsx_to_csv(f_name[0]))
if f_name[1] in ["csv", "xlsx"] and not ".".join(f_name).endswith("[CHECKED].csv"):
    print(xlsx_to_csv_checked(f_name[0]))
if f_name[1] in ["csv", "xlsx"] or ".".join(f_name).endswith("[CHECKED].csv"):
    print(csv_to_s3db(f_name[0]))
f_name[0] = f_name[0].strip("[CHECKED]")
if f_name[1] in ["csv", "xlsx", "s3db"]:
    print(s3db_to_json(f_name[0]))
    print(s3db_to_xml(f_name[0]))
