#!/usr/bin/env bash

# Ask user to keep/remove old files
read -p "Delete old build? [y/N]: " -n 1 -r
echo  # Move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    rm -r dist retadys.pyz
fi

# Install project and its dependencies
pip install ./ --target dist/

# Extra files to be included
cp -r -t dist config.py retadys_logo.xcf

# Build a compressed executable file with Shiv
shiv --site-packages dist --compressed -p '/usr/bin/env python3' \
-o retadys.pyz -e retadys.main