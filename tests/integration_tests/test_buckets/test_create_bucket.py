import pytest

from utility.managers import ObjectStorageManager
from utility.managers.exceptions import (
    BucketNameInvalidError,
    CreateBucketError,
)


@pytest.mark.asyncio
async def test_create_bucket(
    bucket_name: str,
    manager: ObjectStorageManager,
    check_bucket_exists,
):

    await manager.create_bucket(
        bucket_name=bucket_name,
    )

    assert (await check_bucket_exists(True))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'bucket_name', ['', ], indirect=True,
)
async def test_create_bucket_error_when_bucket_name_invalid(
    bucket_name: str,
    manager: ObjectStorageManager,
):

    with pytest.raises(BucketNameInvalidError):
        await manager.create_bucket(
            bucket_name=bucket_name,
        )


@pytest.mark.asyncio
async def test_create_bucket_error_when_bucket_already_exists(
    bucket_name: str,
    manager: ObjectStorageManager,
):

    await manager.create_bucket(
        bucket_name=bucket_name,
    )

    with pytest.raises(CreateBucketError):
        await manager.create_bucket(
            bucket_name=bucket_name,
        )
