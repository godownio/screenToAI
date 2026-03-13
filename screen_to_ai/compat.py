from __future__ import annotations

import sys


def fix_six_metapath_importer() -> None:
    try:
        import six
    except Exception:
        return

    for o in sys.meta_path:
        if o.__class__.__name__ == "_SixMetaPathImporter" and not hasattr(o, "_path"):
            try:
                o._path = []
            except Exception:
                pass
