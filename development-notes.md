# Development Notes

## (In progress) build binary for Linux using PyInstaller

- for building install pyinstaller

    pip install pyinstaller
    pyinstaller -w -F -n ConText --collect-all scipy --collect-all faicons  --copy-metadata great_tables --collect-all great_tables --add-data "templates:templates" --add-data "static:static" --exclude-module jupyterlab --hidden-import en_core_web_sm --collect-all en_core_web_sm context.py

- Note: this requires Chromium

## Packages for development

- pyinstaller
- twine
