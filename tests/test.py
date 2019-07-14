import pybotlib
import pybotlib.utils as pu
import pybotlib.exceptions as pe
from minio import Minio
from minio.error import ResponseError
import pandas

import subprocess

import uuid
import os
import datetime
import glob

MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]

# global vars

def test_minio_create_bucket():
    minioClient = Minio('minio.crossentropy.solutions',
                  access_key=MINIO_ACCESS_KEY,
                  secret_key=MINIO_SECRET_KEY,
                  secure=False)

    bucket_name = "test-pybotlib-"+str(uuid.uuid4())
    pu.create_minio_bucket(
        host_uri="minio.crossentropy.solutions",
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        bucket_name=bucket_name)


    bucket_exists = minioClient.bucket_exists(bucket_name)

    #clean up
    minioClient.remove_bucket(bucket_name)
    assert bucket_exists == True

def test_dt_parse():
    dt_string = "Mon, 20 Nov 1995 19:12:08 -0500"
    dt = pu.dt_parse(dt_string)
    assert type(dt) == datetime.datetime

def test_get_geckodriver():
    pu.get_geckodriver()
    assert "geckodriver" in glob.glob('*')
    os.remove("geckodriver")

def test_pandas_read_google_sheets():
    sheet_id = "1pBecz5Db9eK0QDR_oePmamdaFtEiCaO69RaE-Ozduk"
    df = pu.pandas_read_google_sheets(sheet_id)
    assert type(df) == pandas.DataFrame

def test_write_file_to_minio_bucket():
    minioClient = Minio('minio.crossentropy.solutions',
                  access_key=MINIO_ACCESS_KEY,
                  secret_key=MINIO_SECRET_KEY,
                  secure=False)

    bucket_name = "test-pybotlib-"+str(uuid.uuid4())
    pu.create_minio_bucket(
        host_uri="minio.crossentropy.solutions",
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        bucket_name=bucket_name)

    with open("./testfile.txt", 'w') as f:
        f.write("hello world!")

    pu.write_file_to_minio_bucket(
        host_uri="minio.crossentropy.solutions",
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        bucket_name=bucket_name,
        filename='testfile.txt'
        )


    minioClient.remove_object(bucket_name, 'testfile.txt')
    os.remove('./testfile.txt')
    minioClient.remove_bucket(bucket_name)
