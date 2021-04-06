from hstest.stage_test import *
from hstest.test_case import TestCase
from os import path
import shutil
import re
import sqlite3
import os

class EasyRiderStage1(StageTest):
    files_to_delete = []
    files_to_check = ["data_one_xlsx.xlsx", "data_big_xlsx.xlsx", "data_one_csv.csv", "data_big_csv.csv",
                      "data_one_chk[CHECKED].csv", "data_big_chk[CHECKED].csv"]

    @staticmethod
    def remove_s3db_files(files):
        for name in [names.split(".")[0].strip("[CHECKED]") + ".s3db" for names in files]:
            name_del = os.path.join("test", name)
            if path.exists(name_del):
                os.remove(name_del)

    def generate(self) -> List[TestCase]:
#        self.checking_files()
        self.remove_s3db_files(self.files_to_check)
        return [
                TestCase(stdin=[self.prepare_file], attach=("data_one_xlsx.xlsx", 1, "line", 4, "cell", 488, "record")),
                TestCase(stdin=[self.prepare_file], attach=("data_big_xlsx.xlsx", 10, "line", 12, "cell", 5961, "record")),
                TestCase(stdin=[self.prepare_file], attach=("data_one_csv.csv", 1, None, 4, "cell", 488, "record")),
                TestCase(stdin=[self.prepare_file], attach=("data_big_csv.csv", 10, None, 12, "cell", 5961, "record")),
                TestCase(stdin=[self.prepare_file], attach=("data_one_chk[CHECKED].csv", 1, None, 4, "cell", 488, "record")),
                TestCase(stdin=[self.prepare_file], attach=("data_big_chk[CHECKED].csv", 10, None, 12, "cell", 5961, "record")),
        ]

#    def checking_files(self):
#        for file in self.files_to_check:
#            file = os.path.join("test", file)
#            if all([not file.endswith(".s3db"), not path.exists(file)]):
#                raise WrongAnswer(f"There is no {file} file in test repository. Please restore the file or restart the lesson.")

    def after_all_tests(self):
        for file in set(self.files_to_delete):
            try:
                os.remove(file)
            except PermissionError:
                raise WrongAnswer(f"Can't delete the database file: {file}. Looks like database connection wasn't closed.")

    def prepare_file(self, output):
        file_name = self.files_to_check.pop(0)
        shutil.copy(os.path.join("test", file_name), os.path.join("."))
        self.files_to_delete.append(file_name)
        return file_name

    def file_exist(self, file_name):
        if not path.exists(file_name):
            return f"The file '{file_name}' does not exist or is outside of the script directory."
        self.files_to_delete.append(file_name)
        return False

    @staticmethod
    def wrong_number_of_lines_csv(file_name, nr):
        with open(file_name, 'r', encoding='utf-8') as file_csv:
            csv_len = len([x for x in file_csv]) - 1
            if csv_len != nr:
                return f"Wrong number of lines in file {file_name}. Expected {nr}, found {csv_len}\n" + \
                       "check if you have imported headers and all data is present;\ncheck if you have imported the appropriate sheet.)"
        return False

    @staticmethod
    def check_output(quantity, nr, text, file_name):
        prefix = f"{quantity} {nr}{' was' if quantity == 1 else 's were'}"
        if not text.startswith(prefix):
            return f"Output don't starts with sentence '{prefix}'"
        if file_name not in text:
            return f"There is no {file_name} name in output '{text}'."
        return False

    @staticmethod
    def quality_of_data_csv(file_name, number):
        count = 0
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                if not line.startswith("vehicle_id"):
                    for item in line.split(","):
                        if not re.match(r"^[\d]+$", item):
                            return f"In line '{line.strip()}': '{item}' is not a number. Check {file_name}"
                        count += int(item)
        if count != number:
            return f"Check data in {file_name}. Sum of integer should be {number}, found {count}"
        return False

    @staticmethod
    def checking_database(file_name, nr_lines, number):
        conn = sqlite3.connect(file_name)
        convoy = conn.cursor()

        #  checking if table exists
        try:
            lines = convoy.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='convoy';").fetchall()
        except sqlite3.DatabaseError as er:
            return f"Attempting to read from the {file_name} database generates the error: {er}."
        if lines[0][0] == 0:
            return f"There is no table named 'convoy' in database {file_name}"

        #  counting number of the records
        lines = convoy.execute("SELECT COUNT(*) FROM convoy").fetchone()[0]
        if lines != nr_lines:
            return f"Wrong number of records in database {file_name}. Expected {nr_lines}, found {lines}"

        #  checking column names
        lines = convoy.execute('select * from convoy').description
        if sorted([x[0] for x in lines]) != sorted(['vehicle_id', 'engine_capacity', 'fuel_consumption', 'maximum_load']):
            return f"There is something wrong in {file_name}. Found column names: {[x[0] for x in lines]}. " + \
                   "Expected four columns names: 'vehicle_id', 'engine_capacity', 'fuel_consumption', 'maximum_load'"

        #  checking sum of cells
        all_lines = convoy.execute("SELECT * FROM convoy")
        try:
            count = sum(sum(x) for x in all_lines.fetchall())
        except TypeError:
            return f"There is a value other than INTEGER in the table."
        if count != number:
            return f"Check data. Sum of integer in '.s3db' should be {number}, found {count}."

        #  checking if PRIMARY KEY exists
        all_lines = convoy.execute("SELECT * FROM convoy")
        p_key = all_lines.fetchall()[0][0]
        try:
            convoy.execute(f"INSERT INTO convoy(vehicle_id,engine_capacity,fuel_consumption,maximum_load) VALUES({p_key},0,0,0)")
        except sqlite3.IntegrityError:
            pass
        else:
            return f"There is no PRIMARY KEY parameter on column 'vehicle_id' in {file_name}."

        #  checking if columns have an attribute NOT NULL
        not_null = (('1000', 'Null', 'Null', 'Null'), ('1001', 'Null', 'Null', 'Null'), ('1002', 'Null', 'Null', 'Null'))
        for values in not_null:
            try:
                convoy.execute(f"INSERT INTO convoy(vehicle_id,engine_capacity,fuel_consumption,maximum_load) "
                               f"VALUES({values[0]},{values[1]},{values[2]},{values[3]})")
            except sqlite3.IntegrityError:
                pass
            else:
                return f"At least one of the columns has no 'NOT NULL' parameter in {file_name}."

        conn.close()
        return False

    def check(self, reply: str, result) -> CheckResult:
        if "input" not in reply.lower():
            return CheckResult.wrong(f"The first line of the output should be 'Input file name'")
        reply = reply.splitlines()
        reply.pop(0)
        if len(reply) == 0:
            return CheckResult.wrong(f"There is not enough lines in the output")
        file_name = result[0].split(".")

        #  => xlsx
        if file_name[1] == "xlsx":

            test = self.file_exist(f'{file_name[0]}.csv')
            if test:
                return CheckResult.wrong(test)

            test = self.wrong_number_of_lines_csv(f'{file_name[0]}.csv', result[1])
            if test:
                return CheckResult.wrong(test)

            test = self.check_output(result[1], result[2], reply[0], f'{file_name[0]}.csv')
            if test:
                return CheckResult.wrong(test)

            reply.pop(0)
            if len(reply) == 0:
                return CheckResult.wrong(f"There is not enough lines in the output")

        #  => csv
        if any([file_name[1] == "xlsx", all([file_name[1] == "csv", not ".".join(file_name).endswith("[CHECKED].csv")])]):

            test = self.file_exist(f'{file_name[0]}[CHECKED].csv')
            if test:
                return CheckResult.wrong(test)

            test = self.quality_of_data_csv(f'{file_name[0]}[CHECKED].csv', result[5])
            if test:
                return CheckResult.wrong(test)

            test = self.check_output(result[3], result[4], reply[0], f'{file_name[0]}[CHECKED].csv')
            if test:
                return CheckResult.wrong(test)

            reply.pop(0)
            if len(reply) == 0:
                return CheckResult.wrong(f"There is not enough lines in the output")

        #  => [CHECKED]csv
        if any([file_name[1] == "xlsx", file_name[1] == "csv", ".".join(file_name).endswith("[CHECKED].csv")]):

            test = self.file_exist(f'{file_name[0].strip("[CHECKED]")}.s3db')
            if test:
                return CheckResult.wrong(test)

            test = self.checking_database(f'{file_name[0].strip("[CHECKED]")}.s3db', result[1], result[5])
            if test:
                return CheckResult.wrong(test)

            test = self.check_output(result[1], result[6], reply[0], f'{file_name[0].strip("[CHECKED]")}.s3db')
            if test:
                return CheckResult.wrong(test)

            reply.pop(0)

        return CheckResult.correct()


if __name__ == '__main__':
    EasyRiderStage1('convoy.convoy').run_tests()
