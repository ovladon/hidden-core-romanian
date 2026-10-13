#!/usr/bin/env bash
# Regenereaza toate livrabilele din rezultatele existente (fara apeluri API):
# results.json -> figuri -> lucrare (Word oficial ConsILR + varianta LaTeX) -> abstract -> prezentare (pptx/pdf/html)
set -e
cd "$(dirname "$0")"
python3 collect_results.py > /dev/null
python3 make_figures.py 2>/dev/null
python3 slides/export_html_data.py
(cd paper && python3 build_paper.py && python3 build_docx.py)
(cd abstract && python3 build_abstract.py)
(cd slides && python3 make_slides.py && soffice --headless --convert-to pdf HiddenCore_ConsILR2026.pptx > /dev/null 2>&1 && python3 build_html.py)
python3 release_data.py
mkdir -p LIVRABILE
cp paper/HiddenCore_ConsILR2026.docx "LIVRABILE/PAPER - The Hidden Core of Romanian.docx"
cp paper/HiddenCore_ConsILR2026.pdf "LIVRABILE/PAPER - The Hidden Core of Romanian.pdf"
cp "abstract/ABSTRACT - The Hidden Core of Romanian.docx" "abstract/ABSTRACT - The Hidden Core of Romanian.pdf" \
   abstract/ABSTRACT_easychair.txt LIVRABILE/
cp slides/HiddenCore_ConsILR2026.pptx slides/HiddenCore_ConsILR2026.pdf slides/HiddenCore_ConsILR2026.html LIVRABILE/
echo "gata: LIVRABILE/ (lucrare .docx/.pdf, abstract, prezentare .pptx/.pdf/.html)"
