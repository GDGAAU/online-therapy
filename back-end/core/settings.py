"""
Settings package shim.

This module keeps Django's settings discovery working while the actual
configuration lives in core/settings/*.py (base, development, production).
"""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent / "settings")]
