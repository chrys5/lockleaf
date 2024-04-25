# lockleaf

A simple and secure journaling program with terminal GUI to give an intimate, lowkey feel.

<div align="center">
    <img src="screenshots/home page.png" height="240" title="Main Menu">
    <img src="screenshots/write entry page.png" height="240" title="Write Entry">
    <img src="screenshots/archives page.png" height="240" title="Archives">
</div>

## Setup:

1. Clone repo
2. Run `python setup.py` to set up config file and build executable. It will ask you to input a root directory for all your journal entries
3. Find and run executable in dist folder, or run `python src/lockleaf.py`

After the initial setup, running `./scripts/compile.sh/` will also generate a new executable.

## Features:

- Simple installation
- Support for AES encryption
- Keyboard shortcuts to aid minimal mouse use
- Organization into folders
- Timestamped entries

## How to use:

<ul>
    <li> Use Write Entry screen to write entry with a title, folder, and text body. Save with or without password protection.
    <li> Use Archives screen to access past entries with a built-in file browser with easy naming
        <ul>
            <li> Encrypt or decrypt entire folders
            <li> Delete entries or folders
        </ul>
    <li> Use Settings screen to change root directory, change theme, or learn the keyboard shortcuts.
</ul>

## TODO:
- Attach media/files/links
- Export entries
- More customization