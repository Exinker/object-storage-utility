import asyncio

from faker import Faker

from utility.config import S3_CONFIG
from utility.managers import ObjectStorageManager


fake = Faker()

bucket_name = 'test'
object_key = fake.file_path(
    depth=1,
    category='home',
    extension='dat',
)
object_data = fake.binary(
    length=4*1024*1024,
)


async def main():

    manager = ObjectStorageManager(
        access_key=S3_CONFIG.access_key,
        secret_key=S3_CONFIG.secret_key,
        region_name=S3_CONFIG.region_name,
        endpoint_url=S3_CONFIG.endpoint_url,
        certificate_verify=S3_CONFIG.certificate_verify,
    )
    # await manager.create_bucket(
    #     bucket_name=bucket_name,
    # )
    await manager.upload_object(
        bucket_name=bucket_name,
        object_key=object_key,
        object_data=object_data,
    )
    # await manager.download_object(
    #     bucket_name=bucket_name,
    #     object_key=object_key,
    # )
    await manager.remove_object(
        bucket_name=bucket_name,
        object_key=object_key,
    )
    # await manager.remove_bucket(
    #     bucket_name=bucket_name,
    # )


if __name__ == '__main__':
    asyncio.run(main())
