import pytest_asyncio

from utility.managers import ObjectStorageManager


@pytest_asyncio.fixture(scope='function', autouse=True)
async def setup(
    bucket_name: str,
    manager: ObjectStorageManager,
):

    await manager.create_bucket(
        bucket_name=bucket_name,
    )

    yield


@pytest_asyncio.fixture(scope='function', autouse=True)
async def teardown(
    bucket_name: str,
    object_key: str,
    manager: ObjectStorageManager,
):

    yield

    await manager.remove_object(
        bucket_name=bucket_name,
        object_key=object_key,
    )
    await manager.remove_bucket(
        bucket_name=bucket_name,
    )
