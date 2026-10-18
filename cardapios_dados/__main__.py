import sys

from .cli import main
from .publish import RegressionError

try:
    sys.exit(main())
except RegressionError as error:
    sys.exit(error.code)
