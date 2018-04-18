# DjangoFileStorageHandler
You can handle your storage files to MINIO, S3 or Local through Settings

About
-----
This project is useful if you want to store and serve your file to different types of servers. You need to change a switch in settings.py and storage server will change their server in one go.

Installation
------------
To install DjangoFileStoragesHandler, simply use pip:
.. code-block:: bash

    $ pip install DjangoFileStoragesHandler

Documentation
-------------
You need to add few variables in your settings.py .

FILE_STORAGE_TO: This can be s3, local or Minio as per your need.
.. code-block:: python

     FILE_STORAGE_TO = 's3' / 'local' / 'minio'
 
BUCKET_NAME: Enter the bucket name
.. code-block:: python

     BUCKET_NAME = '*******' 
     
SUPPORTED_FORMAT_LIST

.. code-block:: python

     SUPPORTED_FORMAT_LIST = ['.pdf', '.png', '.bmp', '.jpeg', '.jpg', '.doc', '.txt', '.docx', '.PDF', '.PNG', '.BMP',
                            '.JPEG', '.JPG', '.DOC', '.TXT', '.DOCX']
     
In case of AWS S3 you need to add below keys:
AWS_ACCESS_KEY: Access key of AWS
.. code-block:: python

     AWS_ACCESS_KEY = '************' 
     
AWS_SECRET_KEY: SECRET Access key of AWS
.. code-block:: python

     AWS_SECRET_KEY = '************' 
     
AWS_REGION_NAME: Region name AWS
.. code-block:: python

     AWS_REGION_NAME = '*******' 
     
In case of Minio:
MINIO_ACCESS_KEY: Add Minio Access key.
.. code-block:: python

     MINIO_ACCESS_KEY = '*******' 
     
MINIO_SECURE: Add MINIO SECURE key
.. code-block:: python

     MINIO_SECURE = '*******' 

Example
--------

    >>>sh = storage_handler(path='/docs/', filename='uploadfilename',file_data=open('example.pdf','r')
    >>>sh.upload_file()  # upload file to Server.
    {'success': 1, 'message': 'successful'}
    >>>sh.get_file_byte()  # gives file in byte format
    {'success': 1, 'file':b'****************************....'}
    >>>sh.get_file_base64() # gives file in base64 format
    {'success': 1, 'message': 'successful', 'file': base64****************, 'file_extension':'***'}
    >>>sh.download_file()  # Gives file in HTTPResponse.
    >>>sh.delete()  #will delete you file
    {'success': 1, 'message': 'successful'}
    
Found a Bug? Something Unsupported?
---------------

Please write me shuklashashank@outlook.com.

    
    
