import logging
import tarfile
from pathlib import Path


LOGGER = logging.getLogger('app')


class CompressionManager:

    def __init__(
        self,
        destination: Path | None = None,
    ) -> None:

        destination = destination or Path.cwd() / '.archives'
        destination.mkdir(parents=True, exist_ok=True)

        self.__destination = destination

    def compress(
        self,
        directory: Path,
    ) -> str:
        filename = '{}.tar.gz'.format(directory.parts[-1])
        filepath = self.__destination / filename

        if not directory.exists():
            LOGGER.error(
                'Compression is failed. Directiry is not exists',
                extra=dict(
                    filename=filename,
                ),
            )
            raise ValueError

        if not directory.is_dir():
            LOGGER.error(
                'Compression is failed. Archivation for directory is supported only',
                extra=dict(
                    filename=filename,
                ),
            )
            raise ValueError

        if Path(filepath).exists():
            LOGGER.debug(
                'Compression is failed. The archive is exists',
                extra=dict(
                    filepath=filepath,
                ),
            )
            return filename

        try:
            with tarfile.open(filepath, "w:gz") as tar:
                for item in directory.rglob('*'):
                    LOGGER.debug(
                        'Adding an item',
                        extra=dict(
                            filepath=filename,
                            item=str(item),
                        ),
                    )
                    tar.add(item, arcname=str(item.relative_to(directory)))
        except Exception as error:
            LOGGER.error(
                'Compression is failed. Unexpected error',
                extra=dict(
                    filename=filename,
                    error=str(error),
                ),
            )
            if filepath.exists():
                filepath.unlink()

        return filename
