class ObjectStorageError(Exception):

    def __init__(self, *args, msg: str = '', **kwargs):
        super().__init__(*args, **kwargs)

        self._msg = msg

    def __str__(self):
        cls = self.__class__
        return f'{cls.__name__}({self._msg})'


class BucketError(ObjectStorageError):
    pass


class CreateBucketError(BucketError):
    pass


class BucketNameInvalidError(CreateBucketError):
    pass


class BucketExistError(CreateBucketError):
    pass


class RemoveBucketError(BucketError):
    pass


class ObjectError(ObjectStorageError):
    pass


class RemoveObjectError(ObjectError):
    pass
