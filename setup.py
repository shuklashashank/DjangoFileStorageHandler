from distutils.core import setup

setup(name='DjangoFileStorageHandler',
      version='1.0',
      description=('You can handle your storage files to MINIO, S3 or Local through Settings'),
      author='Shashank Shukla',
      author_email='shuklashashank@outlook.com',
      url='',
      install_requires =['minio>=3.0.4', 'requests>=2.18.2', 'boto3>=1.5.19', 'Django>=1.11'],
     )