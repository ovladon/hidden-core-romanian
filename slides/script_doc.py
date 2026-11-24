#!/usr/bin/env python3
"""Documentul vorbitorului (Word + PDF): ce se spune la fiecare slide al prezentarii scurte, in romana si engleza,
cu timpi, indicatii si raspunsuri la intrebarile probabile. Textul vine din talk_script.py.

  cd slides && python3 script_doc.py <cale_fara_extensie>
"""
import subprocess, sys
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from talk_script import SLIDES, QA

OUT = sys.argv[1]
NAVY, ORANGE, GREY = RGBColor(0x13, 0x23, 0x3f), RGBColor(0xc8, 0x4f, 0x1e), RGBColor(0x55, 0x55, 0x55)
d = docx.Document()
for s in d.sections:
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(1.8)
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(12); st.paragraph_format.space_after = Pt(6)


def para(runs, size=None, align=None, after=None, before=None):
    p = d.add_paragraph()
    for t, opt in runs:
        r = p.add_run(t); r.bold = opt.get("b", False); r.italic = opt.get("i", False)
        if opt.get("c"): r.font.color.rgb = opt["c"]
        if size or opt.get("s"): r.font.size = Pt(opt.get("s", size))
    if align is not None: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if before is not None: p.paragraph_format.space_before = Pt(before)
    return p


def mins(t):
    m, s = t.split(":"); return int(m) * 60 + int(s)


total = sum(mins(t) for _, _, t, *_ in SLIDES)
para([("The Hidden Core of Romanian: textul prezentării", {"b": True, "c": NAVY})], size=18, after=2)
para([(f"ConsILR 2026 · 12 slide-uri · aproximativ {total // 60} minute și {total % 60:02d} de secunde", {"c": GREY})], size=12, after=10)
para([("Cum o folosești", {"b": True, "c": NAVY})], size=13, after=3)
for t in ["Fiecare slide are un singur mesaj; textul de pe ecran e scurt, restul îl spui tu.",
          "Fă o pauză scurtă după fiecare cifră mare (33%, 8.761, 98%): lasă sala să o citească.",
          "Dacă timpul e mai scurt, prescurtează slide-urile 5, 10 și 11; slide-urile 2, 4, 7, 8 și 9 sunt miezul.",
          "Slide-urile de rezervă B1–B4 sunt după „Take-home”; prezentarea detaliată (SLIDES - detailed) e rezerva completă pentru întrebări tehnice.",
          "Textul în română e și în notele vorbitorului din PowerPoint (modul Presenter View)."]:
    p = para([("• " + t, {})], after=2); p.paragraph_format.left_indent = Cm(0.5)

for n, title, t, ro, en, cue in SLIDES:
    para([(f"Slide {n} · {title}", {"b": True, "c": NAVY}), (f"   ({t})", {"c": GREY})], size=14, before=14, after=3)
    para([("RO  ", {"b": True, "c": ORANGE}), (ro, {})], after=4)
    para([("EN  ", {"b": True, "c": ORANGE}), (en, {"i": True, "c": GREY})], after=4)
    para([("Indicație: ", {"b": True}), (cue, {"c": GREY})], size=11, after=6)

para([("Întrebări probabile și răspunsuri scurte", {"b": True, "c": NAVY})], size=16, before=18, after=6)
for q_ro, a_ro, q_en, a_en in QA:
    para([("Î: ", {"b": True, "c": ORANGE}), (q_ro, {"b": True})], before=8, after=2)
    para([("R: ", {"b": True, "c": ORANGE}), (a_ro, {})], after=3)
    para([("Q: ", {"b": True, "c": GREY}), (q_en, {"b": True, "i": True, "c": GREY})], size=11, after=2)
    para([("A: ", {"b": True, "c": GREY}), (a_en, {"i": True, "c": GREY})], size=11, after=6)

d.save(OUT + ".docx")
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT.rsplit("/", 1)[0], OUT + ".docx"],
               capture_output=True)
print("scris", OUT + ".docx/.pdf")
