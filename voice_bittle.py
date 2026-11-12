"""Entrada desde el checkout: python voice_bittle.py --demo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from app.consola import main

if __name__ == "__main__":
    raise SystemExit(main())
