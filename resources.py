import boto3
import os.path
from boto3 import client,resource

from botocore.exceptions import ClientError
from config import S3_BUCKET,S3_KEY,S3_SECRET_ACCESS_KEY
from flask import session

def _get_s3_resource():
    if S3_KEY and S3_SECRET_ACCESS_KEY:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY

        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = S3_BUCKET

    return s3_resource.Bucket(bucket)


def get_buckets_list():
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')




def upload_file(file_name,bucket,key, args=None):
    try:
        return client.upload_fileobj(file_name,bucket,key, ExtraArgs=args) 
    except  ClientError as err:
        return err

def delete_file(bucket,key):

    try:
        return client.delete_object(Bucket=bucket, Key=key)
    except  ClientError as err:
        return err

def rename_file(bucket_name,folder_name,new_name,old_name):
    try:
        copy_source = {
            "Bucket": bucket_name,
            "Key" : old_name
        }
        otherkey = new_name
        print(old_name)
        resource.meta.client.copy(copy_source,bucket_name,otherkey)
        response =  delete_file(bucket_name,old_name)
        return  response
    except ClientError as err:
        return err

def copy_to_bucket(source_bucket,source_key,otherbucket,otherkey = None):
    try:
        if otherkey == None:
            otherkey = source_key
            copy_source = {
                "Bucket": source_bucket,
                "Key" : source_key
            }
            response = resource.meta.client.copy(copy_source,otherbucket,otherkey)
        else: 
            copy_source = {
                    "Bucket": source_bucket,
                    "Key" : source_key
                }
            response = resource.meta.client.copy(copy_source,otherbucket,otherkey)
        return response
    except ClientError as err:
        return err


def create_folder(bucket_name,dir_name):
        try:
           return client.put_object(Bucket=bucket_name, Body='', Key=dir_name)
        except ClientError as err:
            return err


def delete_folder(bucket_name, dir_name): 
      try:
          return resource.Bucket(bucket_name).objects.filter(Prefix=dir_name).delete()
      except ClientError as err:
            return err