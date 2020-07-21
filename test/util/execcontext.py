import os
import subprocess
import sys
import tempfile
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Any

# By default, we run the r2e in the dir above this script, not the
# system-wide installed version, which you probably don't mean to
# test. You can also pass in an alternate location in the R2E_PATH
# environment variable.
r2e_path = os.getenv("R2E_PATH", str(Path(__file__).absolute().parent.parent.parent.joinpath("r2e")))


class ExecContext:
    """Creates temporary config, data file and lets you call r2e with them
    easily. Cleans up temp files afterwards.

    Example:

    with ExecContext(config="[DEFAULT]\nto=me@example.com") as context:
        context.call("run", "--no-send")

    """

    def __init__(self, config: str):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.cfg_path = Path(self._tmpdir.name, "rss2email.cfg")
        self.data_path = Path(self._tmpdir.name, "rss2email.json")
        self.opml_path = Path(self._tmpdir.name, "rss2email.opml")

        self.cfg_path.write_text(config)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tmpdir.cleanup()

    def call(self, *args) -> None:
        subprocess.call([sys.executable, r2e_path, "-c", str(self.cfg_path), "-d", str(self.data_path)] + list(args))

    def change_config(self, params: Dict[str, Any]) -> None:
        config = ConfigParser()
        config.read(str(self.cfg_path))
        for name, value in params.items():
            config['DEFAULT'][name] = str(value)
        with self.cfg_path.open('w') as file:
            config.write(file)
