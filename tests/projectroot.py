import sys
import os
from pathlib import Path

def add_project_root(marker_file: str = ".env"):
    """
    Walk up the directory tree until a folder containing `marker_file` is found.
    Then add that folder to sys.path.
    """
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / marker_file).exists():
            root_path = str(parent.resolve())
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
                print(f"Added to sys.path: {root_path}")
            return
    print(f"Project root with {marker_file} not found.")

    return current

# add_project_root()