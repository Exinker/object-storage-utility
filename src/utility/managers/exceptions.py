
class BucketError(Exception):
    pass


class CreateBucketError(BucketError):
    pass


class BucketNameInvalidError(CreateBucketError):
    pass


class BucketExistError(CreateBucketError):
    pass


class RemoveBucketError(BucketError):
    pass
