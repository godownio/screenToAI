from .compat import fix_six_metapath_importer

fix_six_metapath_importer()

from .app import run

if __name__ == "__main__":
    run()
