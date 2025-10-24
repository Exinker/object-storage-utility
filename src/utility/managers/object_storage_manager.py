import asyncio
import io
import json
import logging
import time
from enum import Enum
from typing import Generator

import aiobotocore.session
import botocore
from aiobotocore.client import AioBaseClient
from pydantic import SecretStr

from utility.managers.exceptions import (
    BucketNameInvalidError,
    CreateBucketError,
    RemoveBucketError,
)


LOGGER = logging.getLogger('app')


class Policy(Enum):

    public = 'PUBLIC'
    private = 'PRIVATE'


def read_file(
    stream: io.BytesIO,
    chunk_size: int,
) -> Generator[bytes, None, None]:

    while True:

        data = stream.read(chunk_size)
        if not data:
            break

        yield data


class ObjectStorageManager:

    def __init__(
        self,
        access_key: str,
        secret_key: SecretStr,
        region_name: str,
        endpoint_url: str,
        certificate_verify: str,
        chunk_size: int = 8*1024*1024,
        max_workers: int = 10,
    ) -> None:

        self._access_key = access_key
        self._secret_key = secret_key
        self._region_name = region_name
        self._endpoint_url = endpoint_url
        self._certificate_verify = certificate_verify

        self._session = aiobotocore.session.get_session()

        self._chunk_size = chunk_size
        self._semaphore = asyncio.Semaphore(max_workers)

    async def create_bucket(
        self,
        bucket_name: str,
    ) -> None:

        async with self.get_client() as client:

            try:
                await client.create_bucket(
                    Bucket=bucket_name,
                )
            except (
                client.exceptions.BucketAlreadyExists,
                client.exceptions.BucketAlreadyOwnedByYou,
            ) as error:
                LOGGER.error(
                    'Creating a bucket is failed. Bucket already exists',
                    extra=dict(
                        bucket_name=bucket_name,
                        error=str(error),
                    ),
                )
                raise CreateBucketError from error
            except (
                botocore.exceptions.ClientError,
                botocore.exceptions.ParamValidationError,
            ) as error:
                LOGGER.error(
                    'Creating a bucket is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        error=str(error),
                    ),
                )
                raise BucketNameInvalidError from error
            except Exception as error:
                LOGGER.error(
                    'Creating a bucket is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        error=str(error),
                    ),
                )
            else:
                LOGGER.info(
                    'Bucket is created successfully',
                    extra=dict(
                        bucket_name=bucket_name,
                    ),
                )

    async def remove_bucket(
        self,
        bucket_name: str,
        force: bool = False,  # FIXME: add removing not empty bucket
    ) -> None:

        async with self.get_client() as client:

            try:
                await client.delete_bucket(
                    Bucket=bucket_name,
                )
            except client.exceptions.NoSuchBucket as error:
                LOGGER.error(
                    'Removing a bucket is failed. Bucket is not exists',
                    extra=dict(
                        bucket_name=bucket_name,
                        error=str(error),
                    ),
                )
                raise RemoveBucketError from error
            except Exception as error:
                LOGGER.error(
                    'Removing a bucket is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        error=str(error),
                    ),
                )
            else:
                LOGGER.info(
                    'Bucket removed successfully',
                    extra=dict(
                        bucket_name=bucket_name,
                    ),
                )

    async def set_bucket_policy(
        self,
        bucket_name: str,
        policy: Policy = Policy.public,
    ) -> None:

        match policy:

            case Policy.public:
                config = {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Principal': '*',
                            'Action': 's3:GetObject',
                            'Resource': [
                                f'arn:aws:s3:::{bucket_name}',
                                f'arn:aws:s3:::{bucket_name}/*'
                            ],
                        },
                    ],
                }
            case Policy.private:
                config = {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Deny',
                            'Principal': '*',
                            'Action': 's3:*',
                            'Resource': [
                                f'arn:aws:s3:::{bucket_name}',
                                f'arn:aws:s3:::{bucket_name}/*'
                            ],
                            'Condition': {
                                'Bool': {'aws:SecureTransport': 'false'}
                            },
                        },
                    ],
                }

        async with self.get_client() as client:

            try:
                await client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(config)
                )
            except Exception as error:
                LOGGER.error(
                    'Setting policy for a bucket is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        policy=policy.value,
                        error=str(error),
                    ),
                )

    async def upload_object(
        self,
        bucket_name: str,
        object_key: str,
        object_data: bytes,
    ) -> None:

        if len(object_data) >= 100*1024*1024:
            await self._upload_multipart_object(
                bucket_name=bucket_name,
                object_key=object_key,
                object_data=object_data,
            )
        else:
            await self._upload_object(
                bucket_name=bucket_name,
                object_key=object_key,
                object_data=object_data,
            )

    async def download_object(
        self,
        bucket_name: str,
        object_key: str,
    ) -> None:
        raise NotImplementedError

    async def remove_object(
        self,
        bucket_name: str,
        object_key: str,
    ) -> None:
        started_at = time.perf_counter()

        async with self.get_client() as client:

            try:
                await client.delete_object(
                    Bucket=bucket_name,
                    Key=object_key,
                )
            except Exception as error:
                LOGGER.error(
                    'Deleting an object is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        error=str(error),
                    ),
                )
                raise Exception from error
            else:
                LOGGER.info(
                    'Object is deleted successfully',
                    extra=dict(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        elapsed_time=time.perf_counter() - started_at,
                    ),
                )

    async def _upload_object(
        self,
        bucket_name: str,
        object_key: str,
        object_data: bytes,
    ) -> None:
        started_at = time.perf_counter()

        async with self.get_client() as client:

            try:
                await client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=object_data,
                )
            except Exception as error:
                LOGGER.error(
                    'Uploading an object is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        error=str(error),
                    ),
                )
                raise Exception from error
            else:
                LOGGER.info(
                    'Object is uploaded successfully',
                    extra=dict(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        elapsed_time=time.perf_counter() - started_at,
                    ),
                )

    async def _upload_multipart_object(
        self,
        bucket_name: str,
        object_key: str,
        object_data: bytes,
    ) -> None:
        started_at = time.perf_counter()

        async with self.get_client() as client:

            response = await client.create_multipart_upload(
                Bucket=bucket_name,
                Key=object_key,
            )
            upload_id = response['UploadId']

            try:
                parts = []
                part_number = 1
 
                for chunk in read_file(
                    stream=io.BytesIO(object_data),
                    chunk_size=self._chunk_size,
                ):

                    response = await self._upload_chunk(
                        client=client,
                        bucket_name=bucket_name,
                        object_key=object_key,
                        part_number=part_number,
                        upload_id=upload_id,
                        chunk=chunk,
                    )

                    parts.append({
                        'ETag': response['ETag'],
                        'PartNumber': part_number,
                    })
                    part_number += 1

                await client.complete_multipart_upload(
                    Bucket=bucket_name,
                    Key=object_key,
                    UploadId=upload_id,
                    MultipartUpload={'Parts': parts}
                )
            except Exception as error:
                LOGGER.info(
                    'Uploading a object is failed',
                    extra=dict(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        error=str(error),
                    ),
                )
                await client.abort_multipart_upload(
                    Bucket=bucket_name,
                    Key=object_key,
                    UploadId=upload_id
                )
                raise error
            else:
                LOGGER.info(
                    'Object is uploaded successfully',
                    extra=dict(
                        bucket_name=bucket_name,
                        object_key=object_key,
                        elapsed_time=time.perf_counter() - started_at,
                    ),
                )

    async def _upload_chunk(
        self,
        client: AioBaseClient,
        bucket_name: str,
        object_key: str,
        part_number: int,
        upload_id: int,
        chunk: bytes,
    ) -> None:

        async with self._semaphore:
            response = await client.upload_part(
                Bucket=bucket_name,
                Key=object_key,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=chunk,
            )
            LOGGER.debug(
                'Object part is uploaded successfully',
                extra=dict(
                    bucket_name=bucket_name,
                    object_key=object_key,
                    part_number=part_number,
                ),
            )
        return response

    def get_client(self) -> AioBaseClient:

        return self._session.create_client(
            service_name='s3',
            region_name=self._region_name,
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key.get_secret_value(),
            verify=self._certificate_verify,
        )
