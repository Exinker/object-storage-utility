import pytest
import pytest_asyncio

from utility.managers import ObjectStorageManager


@pytest_asyncio.fixture(scope='function', autouse=True)
async def teardown(
    bucket_name: str,
    manager: ObjectStorageManager,
):

    yield

    async with manager.get_client() as client:

        response = await client.list_buckets()

        if bucket_name in [
            bucket['Name']
            for bucket in response['Buckets']
        ]:
            await client.delete_bucket(
                Bucket=bucket_name,
            )
