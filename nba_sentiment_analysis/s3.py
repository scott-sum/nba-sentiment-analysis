import os
import boto3

BUCKET_NAME = 'nba-sentiment-analysis'

def aws_session(region_name='us-east-2'):
    access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_access_key = os.environ.get('AWS_ACCESS_KEY_SECRET')
    return boto3.session.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name=region_name)

def upload_to_s3(bucket_name, file_path, team):
    session = aws_session()
    s3_resource = session.resource('s3')
    file_dir, file_name = os.path.split(file_path)

    bucket = s3_resource.Bucket(bucket_name)
    bucket.upload_file(
        Filename=file_path, Key=f'{team}/{file_name}'
    )
    print('uploaded')

def download_from_s3(bucket_name, s3_key, dest_path):
    print(s3_key)
    print(dest_path)
    session = aws_session()
    s3_resource = session.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    bucket.download_file(Key=s3_key, Filename=dest_path)
    print('downloaded')
