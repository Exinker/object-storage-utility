import pytest

from utility.managers import ObjectStorageManager


@pytest.mark.asyncio
async def test_upload_object(
    bucket_name: str,
    object_key: str,
    object_data: bytes,
    manager: ObjectStorageManager,
):

    await manager.upload_object(
        bucket_name=bucket_name,
        object_key=object_key,
        object_data=object_data,
    )

    assert 
