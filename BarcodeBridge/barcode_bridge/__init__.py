"""BarcodeBridge — intercetta barcode HID e rimuove il prefisso fino a '-'."""

from .paths import APP_DIR, VERSION
from .strip import strip_prefix

__all__ = ["strip_prefix", "APP_DIR", "VERSION"]
__version__ = VERSION


def __getattr__(name: str):
    if name == "BarcodeBridge":
        from .core import BarcodeBridge

        return BarcodeBridge
    raise AttributeError(name)
