from hstest.stage_test import *
from hstest.test_case import TestCase
import re
from os import path
import shutil
import os
import hashlib
import requests
import zipfile


class EasyRiderStage1(StageTest):
    files_to_delete = []
    files_to_check = ["data_one.xlsx", "data.xlsx", "data_big.xlsx"]

    def generate(self) -> List[TestCase]:
        check_test_files("https://stepik.org/media/attachments/lesson/461165/stage1_files.zip")
        return [
                TestCase(stdin=[self.prepare_file], attach=("data_one.xlsx", 1, "line")),
                TestCase(stdin=[self.prepare_file], attach=("data.xlsx", 4, "line")),
                TestCase(stdin=[self.prepare_file], attach=("data_big.xlsx", 10, "line")),
        ]

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
            csv_len = len([x for x in file_csv])
            if csv_len != nr + 1:
                return f"Wrong number of lines in file {file_name}. Expected {nr + 1}, found {csv_len}\ncheck if you have imported headers and all data is present;\ncheck if you have imported the appropriate sheet.)"
        return False

    @staticmethod
    def check_output(quantity, nr, text, file_name):
        prefix = f"{quantity} {nr}{' was' if quantity == 1 else 's were'}"
        if not text.startswith(prefix):
            return f"Output don't starts with sentence '{prefix}'"
        if not re.search(file_name, text):
            return f"There is no {file_name} name in output '{text}'."
        return False

    def check(self, reply: str, result) -> CheckResult:
        if "input" not in reply.lower():
            return CheckResult.wrong(f"The first line of the output should be 'Input file name'")
        reply = reply.splitlines()
        reply.pop(0)
        if len(reply) == 0:
            return CheckResult.wrong(f"There is not enough lines in the output")

        file_name = result[0].split(".")

        test = self.file_exist(f'{file_name[0]}.csv')
        if test:
            return CheckResult.wrong(test)

        test = self.wrong_number_of_lines_csv(f'{file_name[0]}.csv', result[1])
        if test:
            return CheckResult.wrong(test)

        test = self.check_output(result[1], result[2], reply[0], f'{file_name[0]}.csv')
        if test:
            return CheckResult.wrong(test)

        return CheckResult.correct()


def extract_files(file_url):
    r = requests.get(file_url, allow_redirects=True)  # download file to local repository
    with open("tmp_test.zip", 'wb') as tmp_file:
        tmp_file.write(r.content)

    with zipfile.ZipFile("tmp_test.zip", 'r') as zip_object:  # unpack zip
        list_of_files = zip_object.namelist()
        for org_file in list_of_files:
            zip_object.extract(org_file)

    if path.exists("tmp_test.zip"):  # delete local zip file
        os.remove("tmp_test.zip")


def check_test_files(file_url):  # as input http address of the zip file on Stpeik
    direct = "test"
    md5_sum = {'data.xlsx': '409e3a6a74137dd72d268fbd100c0b20',
               'data_big.xlsx': '12ad1512574f861725dbc82286237697',
               'data_one.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}

    for file in md5_sum:
        try:
            with open(os.path.join(direct, file), "rb") as local_file:
                content = local_file.read()  # reed content and calculate hash value
                md5_hash = hashlib.md5()
                md5_hash.update(content)
                digest = md5_hash.hexdigest()

                if md5_sum[file] != digest:  # if wrong hash value restore all files
                    extract_files(file_url)
                    return

        except FileNotFoundError:  # if there is no file restore all files
            extract_files(file_url)
            return


if __name__ == '__main__':
    EasyRiderStage1('convoy.convoy').run_tests()
