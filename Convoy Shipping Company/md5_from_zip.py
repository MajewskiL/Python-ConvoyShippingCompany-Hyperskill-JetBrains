import hashlib
import zipfile
import requests


def get_md5_from_zip(file_name):
    r = requests.get(file_name, allow_redirects=True)
    open("tmp_test.zip", 'wb').write(r.content)
    file_name = "tmp_test.zip"
    md5_json = {}
    with zipfile.ZipFile(file_name, 'r') as zip_object:
        list_of_files = zip_object.namelist()
        for file in list_of_files:
            if len(file.split("/")) > 1:
                archive = zipfile.ZipFile(file_name, 'r')
                zipped_file = archive.open(file)
                content = zipped_file.read()
                md5_hash = hashlib.md5()
                md5_hash.update(content)
                digest = md5_hash.hexdigest()
                md5_json[file.split("/")[1]] = digest
    md5_json.pop("")
    print(md5_json)


get_md5_from_zip("https://stepik.org/media/attachments/lesson/461165/stage1_files.zip")
get_md5_from_zip("https://stepik.org/media/attachments/lesson/461165/stage2_files.zip")
get_md5_from_zip("https://stepik.org/media/attachments/lesson/461165/stage3_files.zip")
get_md5_from_zip("https://stepik.org/media/attachments/lesson/461165/stage4_files.zip")
get_md5_from_zip("https://stepik.org/media/attachments/lesson/461165/stage5_files.zip")
get_md5_from_zip("https://stepik.org/media/attachments/lesson/461165/stage6_files.zip")


'''
{'data.xlsx': '409e3a6a74137dd72d268fbd100c0b20', 'data_big.xlsx': '12ad1512574f861725dbc82286237697', 'data_one.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}
{'data_big_csv.csv': 'ce035f34f6591e089c3bfc4d0cddab03', 'data_big_xlsx.xlsx': '12ad1512574f861725dbc82286237697', 'data_one_csv.csv': '8e3828c13e2c3dd380d6fa2eb22337a1', 'data_one_xlsx.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}
{'data_big_chk[CHECKED].csv': '5f87334c2c4f22e5bfb8a6641fea4f1d', 'data_big_csv.csv': 'ce035f34f6591e089c3bfc4d0cddab03', 'data_big_xlsx.xlsx': '12ad1512574f861725dbc82286237697', 'data_one_chk[CHECKED].csv': 'cdf1d3fae0ccd85fbfac9aa041c0d455', 'data_one_csv.csv': '8e3828c13e2c3dd380d6fa2eb22337a1', 'data_one_xlsx.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}
{'data_big_chk[CHECKED].csv': '5f87334c2c4f22e5bfb8a6641fea4f1d', 'data_big_csv.csv': 'ce035f34f6591e089c3bfc4d0cddab03', 'data_big_xlsx.xlsx': '12ad1512574f861725dbc82286237697', 'data_one_chk[CHECKED].csv': 'cdf1d3fae0ccd85fbfac9aa041c0d455', 'data_one_csv.csv': '8e3828c13e2c3dd380d6fa2eb22337a1', 'data_one_xlsx.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}
{'data_big_chk[CHECKED].csv': '5f87334c2c4f22e5bfb8a6641fea4f1d', 'data_big_csv.csv': 'ce035f34f6591e089c3bfc4d0cddab03', 'data_big_xlsx.xlsx': '12ad1512574f861725dbc82286237697', 'data_one_chk[CHECKED].csv': 'cdf1d3fae0ccd85fbfac9aa041c0d455', 'data_one_csv.csv': '8e3828c13e2c3dd380d6fa2eb22337a1', 'data_one_xlsx.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}
{'data_big_chk[CHECKED].csv': '5f87334c2c4f22e5bfb8a6641fea4f1d', 'data_big_csv.csv': 'ce035f34f6591e089c3bfc4d0cddab03', 'data_big_xlsx.xlsx': '12ad1512574f861725dbc82286237697', 'data_final_xlsx.xlsx': '7166ec4884dc5758067e6da1f4ef884a', 'data_one_chk[CHECKED].csv': 'cdf1d3fae0ccd85fbfac9aa041c0d455', 'data_one_csv.csv': '8e3828c13e2c3dd380d6fa2eb22337a1', 'data_one_xlsx.xlsx': '6b8c741538067a24e7c6bfa39c8b3d94'}
'''
