#!/bin/bash
./flatedit
cp README.md Taciturnitas.md
#python -m venv venv
source venv/bin/activate
python update_pdf.py
python changelog.py
bash git.sh
