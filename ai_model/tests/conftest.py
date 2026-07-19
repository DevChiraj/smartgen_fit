import sys
from pathlib import Path

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
for subdir in ("preprocessing", "training", "inference"):
    path = str(AI_MODEL_DIR / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)
