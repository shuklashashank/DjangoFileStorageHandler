# coding=utf-8

import base64
import os
from datetime import timedelta

import boto3
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, FileSystemStorage
from django.http import HttpResponse
from minio import Minio

if settings.FILE_STORAGE_TO == 's3':
    s3 = boto3.client(aws_access_key_id=settings.AWS_ACCESS_KEY,
                      aws_secret_access_key=settings.AWS_SECRET_KEY,
                      service_name='s3', region_name=settings.AWS_REGION_NAME)
    bucketname = settings.BUCKET_NAME

if settings.FILE_STORAGE_TO == 'minio':
    minioClient = Minio(settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY,
                        secret_key=settings.MINIO_SECRET_KEY, secure=settings.MINIO_SECURE)  # , httpClient=httpClient)
    bucketname = settings.BUCKET_NAME


def get_content_type(file_extension):
    """
    getting content_type via file_type.
    :param file_extension
    :return: content_type
    """
    file_extension = file_extension.lower()
    if file_extension == 'pdf':
        content_type = 'application/pdf'
    elif file_extension == 'bmp':
        content_type = 'image/bmp'
    elif file_extension == 'png':
        content_type = 'image/png'
    elif file_extension in ['jpeg', 'jpg']:
        content_type = 'image/jpeg'
    elif file_extension == 'doc':
        content_type = 'application/msword'
    elif file_extension == 'docx':
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_extension == 'text':
        content_type = 'text/plain'
    else:
        return 'content_type not found'
    return content_type


class ServerStorage(object):
    """
    Use for Storing the File to local Server.
    """

    def __init__(self, path, filename, file_data=None):
        """
        :param path: upload path
        :param filename: file name
        :param file_data: file data
        """
        self.path = path
        if not self.path.endswith('/'):
            self.path += '/'
        self.filename = filename
        if file_data:
            self.file_data = file_data
            self.fileName, self.file_extension = os.path.splitext(file_data.name)

    def upload_file(self):
        """
        :return: True or False
        """
        if self.file_extension not in settings.SUPPORTED_FORMAT_LIST:
            return {'success': 0, 'message': 'file format not supported.'}
        try:
            try:
                if not os.path.exists(settings.BASE_DIR + self.path):
                    os.makedirs(settings.BASE_DIR + self.path)
            except OSError as e:
                print('DefaultStorage OSError', e)
            default_storage.save(settings.BASE_DIR + self.path + self.filename + self.file_extension,
                                 ContentFile(self.file_data.read()))
            return {'success': 1, 'message': 'successful'}
        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def get_file_byte(self):
        """
        :return: file in bytes
        """
        fs = FileSystemStorage()
        if fs.exists(settings.BASE_DIR + self.path + self.filename):
            return open(settings.BASE_DIR + self.path + self.filename, "rb").read()
        return {'success': 0, 'message': 'File not found'}

    def get_file_base64(self):
        """
        :return: file in base64
        """
        fs = FileSystemStorage()
        if fs.exists(settings.BASE_DIR + self.path + self.filename):
            return {'success': 1, 'message': 'successful',
                    'file': base64.b64encode(open(settings.BASE_DIR + self.path + self.filename, "rb").read()),
                    'file_extension': self.filename.split('.')[-1]}
        return {'success': 0, 'message': 'File not found'}

    def download_file(self):
        """

        :return: file object
        """
        fs = FileSystemStorage()
        if fs.exists(settings.BASE_DIR + self.path + self.filename):
            response = HttpResponse(open(settings.BASE_DIR + self.path + self.filename, "rb"),
                                    content_type=get_content_type(self.filename.split('.')[-1]))
            response['Content-Disposition'] = 'inline; filename=documentfile.%s' % self.filename.split('.')[-1]
            return response
        return {'success': 0, 'message': 'File not found'}

    def delete(self):
        """
        delete file from the server.
        :return: BootUPSettingsHandler response
        """
        fs = FileSystemStorage()
        if fs.exists(settings.BASE_DIR + self.path):
            try:
                fs.delete(settings.BASE_DIR + self.path + self.filename)
                return {'success': 1, 'message': 'successful'}
            except Exception as e:
                print("ServerStorage delete", e)
                return {'success': 0, 'message': str(e)}
        return {'success': 0, 'message': 'File not found'}


class S3Storage(object):
    """
    Use for Storing the File in S3 bucket.
    """

    def __init__(self, path, filename, file_data=None):

        """
        :param path: upload path
        :param filename: file name
        :param file_data: file data
        """
        self.path = path
        if self.path.startswith('/'):
            self.path = self.path[1:]
        if not self.path.endswith('/'):
            self.path += '/'
        self.filename = filename
        if file_data:
            self.file_data = file_data
            self.fileName, self.file_extension = os.path.splitext(file_data.name)

    def upload_file(self):
        """
        :return: True or False
        """

        if self.file_extension not in settings.SUPPORTED_FORMAT_LIST:
            return {'success': 0, 'message': 'file format not supported.'}
        try:
            s3.upload_fileobj(self.file_data, bucketname, str(self.path + self.filename + self.file_extension))
            return {'success': 1, 'message': 'successful'}
        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def get_file_byte(self):
        """
        :return: file in bytes
        """
        try:
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': bucketname,
                                                    'Key': str(self.path + self.filename)},
                                            ExpiresIn=600)
            response = requests.get(url)
            # if response.status_code == 200:
            return response._content
        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def get_file_base64(self):
        """
        :return: file in base64
        """
        try:
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': bucketname,
                                                    'Key': str(self.path + self.filename)},
                                            ExpiresIn=600)
            response = requests.get(url)
            # if response.status_code == 200:
            return {'success': 1, 'message': 'successful',
                    'file': base64.b64encode(response._content),
                    'file_extension': self.filename.split('.')[-1]}
            # return base64.b64encode(response._content)
        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def get_file_url(self):
        """
        :return: file URL
        """
        return s3.generate_presigned_url(ClientMethod='get_object',
                                         Params={'Bucket': bucketname,
                                                 'Key': str(self.path + self.filename)},
                                         ExpiresIn=60)

    def download_file(self):
        """

        :return: file object
        """
        try:
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': bucketname,
                                                    'Key': str(self.path + self.filename)},
                                            ExpiresIn=600)
            response = requests.get(url)
            response = HttpResponse(response._content, content_type=get_content_type(self.filename.split('.')[-1]))
            response['Content-Disposition'] = 'inline; filename=documentfile.%s' % self.filename.split('.')[-1]
            return response

        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def delete(self):
        """
        delete file from the S3 server.
        :return: BootUPSettingsHandler response
        """
        try:
            s3.delete_object(bucketname, str(self.path + self.filename + self.file_extension))
            return {'success': 1, 'message': 'successful'}
        except Exception as e:
            return {'success': 0, 'message': str(e)}


class MinioStorage(object):
    """
    Use for Storing the File in Minio.
    """

    def __init__(self, path, filename, file_data=None):

        """
        :param path: upload path
        :param filename: file name
        :param file_data: file data
        """
        self.path = path
        if self.path.startswith('/'):
            self.path = self.path[1:]
        if not self.path.endswith('/'):
            self.path += '/'
        self.filename = filename
        if file_data:
            self.file_data = file_data
            self.fileName, self.file_extension = os.path.splitext(file_data.name)

    def upload_file(self):
        """
        :return: True or False
        """

        if self.file_extension not in settings.SUPPORTED_FORMAT_LIST:
            return {'success': 0, 'message': 'file format not supported.'}
        try:
            minioClient.put_object(data=self.file_data.file, bucket_name=bucketname, length=self.file_data.size,
                                   object_name=str(self.path + self.filename + self.file_extension))
            return {'success': 1, 'message': 'successful'}
        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def get_file_byte(self):
        """
        :return: file in bytes
        """
        try:
            url = minioClient.presigned_get_object(bucketname, str(self.path + self.filename),
                                                   expires=timedelta(seconds=600))
            response = requests.get(url)
            # if response.status_code == 200:
            return response._content
        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def get_file_base64(self):
        """
        :return: file in base64
        """
        try:
            url = minioClient.presigned_get_object(bucketname, str(self.path + self.filename),
                                                   expires=timedelta(seconds=600))
            response = requests.get(url)
            # if response.status_code == 200:
            return {'success': 1, 'message': 'successful',
                    'file': base64.b64encode(response._content),
                    'file_extension': self.filename.split('.')[-1]}
            # return base64.b64encode(response._content)
        except Exception as e:
            print("MinioStorage get_file_base64 error", e)
            return {'success': 0, 'message': str(e)}

    def get_file_url(self):
        """
        :return: file URL
        """
        return minioClient.presigned_get_object(bucketname, str(self.path + self.filename),
                                                expires=timedelta(seconds=600))

    def download_file(self):
        """

        :return: file object
        """
        try:
            url = minioClient.presigned_get_object(bucketname, str(self.path + self.filename),
                                                   expires=timedelta(seconds=600))
            response = requests.get(url)
            response = HttpResponse(response._content, content_type=get_content_type(self.filename.split('.')[-1]))
            response['Content-Disposition'] = 'inline; filename=documentfile.%s' % self.filename.split('.')[-1]
            return response

        except Exception as e:
            return {'success': 0, 'message': str(e)}

    def delete(self):
        """
        delete file from the S3 server.
        :return: BootUPSettingsHandler response
        """
        try:
            minioClient.remove_object(bucket_name=bucketname,
                                      object_name=str(self.path + self.filename + self.file_extension))
            return {'success': 1, 'message': 'successful'}
        except Exception as e:
            return {'success': 0, 'message': str(e)}


def storage_handler(path, filename, file_data=None):
    """

    :param path:
    :param filename:
    :param file_data:
    :return: Class Object.
    """

    if settings.FILE_STORAGE_TO == 's3':
        return S3Storage(path, filename, file_data)
    elif settings.FILE_STORAGE_TO == 'minio':
        return MinioStorage(path, filename, file_data)
    else:
        return ServerStorage(path, filename, file_data)
