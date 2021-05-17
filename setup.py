"""Handle module packaging."""

import subprocess
import textwrap

from setuptools import setup


def _get_release_version() -> None:
    """Get git release tag version."""
    version = (
        subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .strip()
    )
    print("VERSION: ", version)
    # assert re.match(r"\d\.\d.\d{1,2}", version)
    return version


def _write_version(version: str) -> None:
    """Write version to version.py."""
    with open("src/voiceassistant/version.py", "w") as file:
        file.write(
            textwrap.dedent(
                f'''
                """Host package version, generated on build."""
                __version__ = "{version}"
                '''
            ).lstrip()
        )


version = _get_release_version()

_write_version(version)
setup(version=version)
