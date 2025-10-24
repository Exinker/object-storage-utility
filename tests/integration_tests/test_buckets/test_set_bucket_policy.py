import aiohttp
import pytest

from utility.config import S3_CONFIG
from utility.managers import ObjectStorageManager, Policy


@pytest.mark.asyncio
async def test_set_bucket_public(
    bucket_name: str,
    manager: ObjectStorageManager,
):
    await manager.create_bucket(
        bucket_name=bucket_name,
    )

    await manager.set_bucket_policy(
        bucket_name=bucket_name,
        policy=Policy.public,
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(S3_CONFIG.endpoint_url + '/' + bucket_name) as response:
            assert response.status == 200
