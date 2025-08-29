from getpass import getuser
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent
ROOT_DIR = Path(f'.mosaic.{getuser()}')
TEMP_DIR = ROOT_DIR / '.temp'
