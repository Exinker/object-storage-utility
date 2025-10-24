import pytest

from utility.managers import ObjectStorageManager
from utility.managers.exceptions import (
    RemoveBucketError,
)


@pytest.mark.asyncio
async def test_remove_bucket(
    bucket_name: str,
    manager: ObjectStorageManager,
    check_bucket_exists,
):
    await manager.create_bucket(
        bucket_name=bucket_name,
    )

    await manager.remove_bucket(
        bucket_name=bucket_name,
    )

    assert (await check_bucket_exists(False))


@pytest.mark.asyncio
async def test_remove_bucket_error_when_bucket_not_exists(
    bucket_name: str,
    manager: ObjectStorageManager,
):
    with pytest.raises(RemoveBucketError):
        await manager.remove_bucket(
            bucket_name=bucket_name,
        )
