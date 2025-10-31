import logging
import subprocess
from pathlib import Path


LOGGER = logging.getLogger('app')


class ArchiveManager:

    def __init__(
        self,
        destination: Path | None = None,
    ) -> None:

        destination = destination or Path.cwd() / '.archive'
        destination.mkdir(parents=True, exist_ok=True)

        self._destination = destination

    def archive(
        self,
        source: Path,
    ) -> str:
        filename = '{}.tar'.format(source.parts[-1])
        filepath = self._destination / filename

        if not source.exists():
            LOGGER.error(
                'Archivation failed: directory not exists',
                extra=dict(
                    filename=filename,
                ),
            )
            raise ValueError

        if not source.is_dir():
            LOGGER.error(
                'Archivation failed: archivation for directory is supported only',
                extra=dict(
                    filename=filename,
                ),
            )
            raise ValueError

        if Path(filepath).exists():
            LOGGER.debug(
                'Archivation failed: the archive is exists',
                extra=dict(
                    filepath=filepath,
                ),
            )
            return filename

        command = [
            'tar',
            '-cvf',
            str(filepath),
            '-C',
            str(source),
            '.',
        ]
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            LOGGER.error(
                'Archivation failed: unexpected error',
                extra=dict(
                    destination=str(filepath),
                    stderr=error.stderr.strip(),
                ),
            )
        else:
            LOGGER.info(
                'Archivation finished successfully',
                extra=dict(
                    destination=str(filepath),
                    stdout=result.stdout.strip(),
                ),
            )

        return filename
