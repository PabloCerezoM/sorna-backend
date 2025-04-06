from pathlib import Path
from typing import Callable

HOME_PATH: Callable[[], Path] = lambda: Path.home()


