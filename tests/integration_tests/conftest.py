from typing import Coroutine, Generator

import pytest
from pydantic import SecretStr
from testcontainers.minio import MinioContainer

from utility.config import S3_CONFIG
from utility.managers import ObjectStorageManager


@pytest.fixture(scope='session', autouse=True)
def minio_container() -> Generator[MinioContainer, None, None]:

    container = MinioContainer(
        image='minio/minio',
    )
    container.start()

    yield container

    container.stop()


@pytest.fixture
def manager(
    minio_container: MinioContainer,
    monkeypatch: pytest.MonkeyPatch,
) -> ObjectStorageManager:

    monkeypatch.setattr(S3_CONFIG, 'access_key', minio_container.access_key)
    monkeypatch.setattr(S3_CONFIG, 'secret_key', SecretStr(minio_container.secret_key))
    monkeypatch.setattr(S3_CONFIG, 'endpoint_url', 'http://{host}:{port}'.format(
        host=minio_container.get_container_host_ip(),
        port=minio_container.get_exposed_port(9000),
    ))
    monkeypatch.setattr(S3_CONFIG, 'certificate_verify', False)

    client = ObjectStorageManager(
        access_key=S3_CONFIG.access_key,
        secret_key=S3_CONFIG.secret_key,
        region_name=S3_CONFIG.region_name,
        endpoint_url=S3_CONFIG.endpoint_url,
        certificate_verify=S3_CONFIG.certificate_verify,
    )
    return client


@pytest.fixture
def check_bucket_exists(
    bucket_name: str,
    manager: ObjectStorageManager,
) -> Coroutine[bool, None, None]:

    async def inner(
        __status: bool,
    ) -> bool:

        async with manager.get_client() as client:

            response = await client.list_buckets()
            is_exists = bucket_name in (
                bucket['Name']
                for bucket in response['Buckets']
            )

            return is_exists == __status

    return inner
