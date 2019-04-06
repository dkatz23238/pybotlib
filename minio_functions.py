from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
import os

# Convinience function for uploading a folder to Minio

def create_minio_bucket(host_uri, minio_access_key, minio_secret_key, bucket_name):
    ''' Creates a minio bucket to upload files to'''
    minioClient = Minio('%s:9000' % host_uri,
                    access_key= minio_access_key,
                    secret_key= minio_secret_key,
                    secure=False)
    try:
        minioClient.make_bucket(bucket_name)
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise

def write_file_to_minio_bucket(host_uri, minio_access_key, minio_secret_key, bucket_name, filename):
    ''' Convinience function in order to upload a file to a minio bucket. Filename must exist in current working directory'''
    if not os.path.exists("./%s" % filename):
        raise Exception("file must be in current working directory")
    else:
        minioClient = Minio('%s:9000' % host_uri,
                        access_key= minio_access_key,
                        secret_key= minio_secret_key,
                        secure=False)
        try:
            object = minioClient.fput_object(
                bucket_name=bucket_name, object_name=filename, file_path="./%s" % filename
            )
            # print("MINIO FILE WRITE COMPLETE!")
            # print(object)
        except Exception as e:
            raise e
