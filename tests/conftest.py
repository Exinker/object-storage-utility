import pytest


@pytest.fixture
def bucket_name(faker) -> str:
    length = faker.random_int(min=2+1, max=64-1)

    return faker.password(
        length=length,
        special_chars=False,
        digits=True,
        upper_case=False,
    )


@pytest.fixture
def object_key(faker) -> str:
    depth = faker.random_int(min=0, max=10)

    return faker.file_path(
        depth=depth,
        category='home',
        extension='.txt',
    )


@pytest.fixture
def object_data(faker) -> bytes:
    length = faker.random_int(min=1024, max=1024*1024)

    return faker.binary(
        length=length,
    )
