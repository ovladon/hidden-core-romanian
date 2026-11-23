#!/usr/bin/env python3
"""Prezentarea ConsILR 2026 (pptx), din results/results.json si din celelalte fisiere de rezultate.
15 slide-uri principale (circa 15 minute) si slide-uri de rezerva pentru intrebari. Note de vorbitor in romana.

  cd slides && python3 make_slides.py && soffice --headless --convert-to pdf HiddenCore_ConsILR2026.pptx
"""
import json, statistics
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

R = json.load(open("../results/results.json", encoding="utf8"))
N = R["data"]["headwords"]; ai = R["regimes"]["ai"]
LB = ai.get("minset_lb_ilp", ai["minset_lb"]); UB = ai["minset_ub"]
_rg = list(R["regimes"].values())
import sys as _s; _s.path.insert(0, "..")
from calib import calib, EN, RO
CB = calib(R)
G, S, E, L, V = R["graur"], R["swadesh"], R["etymology"], R["layers"], R["validation"]
D9 = json.load(open("../results/dex98_only.json", encoding="utf8"))
XS = json.load(open("../crossling/summary.json", encoding="utf8"))
XO = [r for r in XS if r["language"] != "Romanian"]; XD = next(r for r in XS if r["code"] == "dex")
WN = next(r for r in XS if r["code"] == "wordnet")
WD = json.load(open("html_data.json", encoding="utf8"))["words"]
LOGO = "../../../ConsILR2025/logo_consilr.png"
FIG = "../figures/"

INK, INK2, MUTED = RGBColor(0x0b, 0x0b, 0x0b), RGBColor(0x52, 0x51, 0x4e), RGBColor(0x8a, 0x89, 0x84)
BLUE, ORANGE, AQUA = RGBColor(0x2a, 0x78, 0xd6), RGBColor(0xeb, 0x68, 0x34), RGBColor(0x1b, 0xaf, 0x7a)
SURF, LINE, PALE, GREY = RGBColor(0xfc, 0xfc, 0xfb), RGBColor(0xe6, 0xe5, 0xe1), RGBColor(0xe8, 0xf1, 0xfb), RGBColor(0xf0, 0xef, 0xec)
FONT = "Calibri"


def kr(r, g):
    d = r.get(g, r["freq"]); return 100 * (d["minset_lb_n"] + d["minset_ub_n"]) / 2 / d["kernel_n"]


XR = [kr(r, g) for r in XO for g in ("freq", "all")]
MIDS = [(kr(r, "freq") + kr(r, "all")) / 2 for r in XO]
DEX_RATIO = (kr(XD, "freq") + kr(XD, "all")) / 2
DEX_Z = (DEX_RATIO - statistics.mean(MIDS)) / statistics.stdev(MIDS)
ROM = [kr(r, g) for r in XO if r["language"] in ("Italian", "Spanish", "Portuguese", "French") for g in ("freq", "all")]
PP = [r["reciprocal_pairs_per_1000"] for r in XO]
NL = len({r["language"] for r in XO})
NUMW = {11: "eleven", 13: "thirteen"}
pct = lambda x, d=0: f"{100 * x:.{d}f}%"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W, H = prs.slide_width, prs.slide_height
COUNT = {"n": 1, "b": 0}


def text(slide, x, y, w, h, runs, size=22, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, gap=0.45):
    tb = slide.shapes.add_textbox(x, y, w, h); tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = align
        segs = para if isinstance(para, tuple) else (para,)
        for seg in segs:
            r = par.add_run()
            if isinstance(seg, dict):
                r.text = seg["t"]; f = r.font
                f.size = Pt(seg.get("size", size)); f.bold = seg.get("bold", bold); f.italic = seg.get("italic", False)
                f.color.rgb = seg.get("color", color); f.name = FONT
            else:
                r.text = seg; f = r.font; f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = FONT
        par.space_after = Pt(size * gap)
    return tb


def base(title, kicker, backup=False):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill; bg.solid(); bg.fore_color.rgb = SURF
    s.shapes.add_picture(LOGO, W - Inches(1.75), Inches(0.28), height=Inches(0.55))
    text(s, Inches(0.7), Inches(0.35), Inches(10), Inches(0.4), kicker.upper(), size=13,
         color=ORANGE if backup else BLUE, bold=True)
    text(s, Inches(0.7), Inches(0.68), Inches(11.3), Inches(0.8), title, size=28, bold=True)
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.7), H - Inches(0.45), W - Inches(0.7), H - Inches(0.45))
    ln.line.color.rgb = LINE; ln.line.width = Pt(0.75)
    COUNT["b" if backup else "n"] += 1
    text(s, Inches(0.7), H - Inches(0.42), Inches(9), Inches(0.35),
         "Belciug & Pelican · The Hidden Core of Romanian · ConsILR 2026", size=11, color=MUTED)
    text(s, W - Inches(1.7), H - Inches(0.42), Inches(1.0), Inches(0.35),
         f"B{COUNT['b']}" if backup else str(COUNT["n"]), size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


def notes(s, t):
    s.notes_slide.notes_text_frame.text = t


def box(s, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, label=None, size=20, color=INK,
        bold=False, italic=False):
    b = s.shapes.add_shape(shape, x, y, w, h)
    b.fill.solid(); b.fill.fore_color.rgb = fill
    if line: b.line.color.rgb = line; b.line.width = Pt(1.25)
    else: b.line.fill.background()
    b.shadow.inherit = False
    if label is not None:
        tf = b.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        lines = label if isinstance(label, list) else [label]
        for i, l in enumerate(lines):
            par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            par.alignment = PP_ALIGN.CENTER
            r = par.add_run(); r.text = l
            r.font.size = Pt(size if i == 0 else size * 0.7); r.font.bold = bold and i == 0
            r.font.italic = italic and i == 0; r.font.color.rgb = color; r.font.name = FONT
    return b


def arrow(s, x1, y1, x2, y2, color=ORANGE, width=2.5):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    c.line.color.rgb = color; c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd", {"type": "triangle"}))
    return c


def stat(s, x, y, big, small, color=BLUE, w=Inches(3.6), size=50):
    text(s, x, y, w, Inches(1.0), big, size=size, bold=True, color=color)
    text(s, x, y + Inches(0.95), w, Inches(1.2), small, size=16, color=INK2)


def bullets(s, x, y, w, h, items, size=19):
    """Lista cu bara colorata in stanga fiecarui element: [(titlu, text), ...]."""
    step = h / len(items)
    for i, (head, body) in enumerate(items):
        yy = y + int(step * i)
        box(s, x, yy + Inches(0.05), Inches(0.12), int(step) - Inches(0.25), BLUE)
        text(s, x + Inches(0.3), yy, w - Inches(0.3), int(step), [({"t": head, "bold": True, "size": size + 2},), body],
             size=size, gap=0.25)


# ── 1 titlu
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = SURF
s.shapes.add_picture(LOGO, Inches(0.7), Inches(0.6), height=Inches(0.9))
text(s, Inches(0.7), Inches(2.0), Inches(11.5), Inches(1.4), "The Hidden Core of Romanian", size=54, bold=True)
text(s, Inches(0.7), Inches(3.1), Inches(11.5), Inches(1.0), "A graph-theoretic analysis of dictionary definitions",
     size=28, color=INK2)
text(s, Inches(0.7), Inches(4.6), Inches(11.5), Inches(1.4),
     [({"t": "Vlad Belciug, Elena Pelican", "bold": True, "size": 22},),
      "“Ovidius” University of Constanța · Faculty of Mathematics and Informatics",
      "ConsILR 2026 · Galați · 9–11 December 2026"], size=18, color=INK2)
notes(s, "(0:20) Bună ziua. Vă propun o întrebare simplă despre dicționar și răspunsul ei, măsurat pe tot DEX-ul și comparat cu alte unsprezece limbi.")

# ── 2 cercul
s = base("A dictionary explains words with other words", "The question")
box(s, Inches(1.2), Inches(2.1), Inches(3.4), Inches(1.25), PALE, BLUE, label="copac", size=34, italic=True)
box(s, Inches(8.0), Inches(2.1), Inches(3.4), Inches(1.25), PALE, BLUE, label="arbore", size=34, italic=True)
arrow(s, Inches(8.0), Inches(2.45), Inches(4.6), Inches(2.45))
arrow(s, Inches(4.6), Inches(3.0), Inches(8.0), Inches(3.0))
text(s, Inches(4.7), Inches(1.75), Inches(3.2), Inches(0.5), "used in the definition of", size=15, color=INK2, align=PP_ALIGN.CENTER)
text(s, Inches(4.7), Inches(3.1), Inches(3.2), Inches(0.5), "used in the definition of", size=15, color=INK2, align=PP_ALIGN.CENTER)
text(s, Inches(1.2), Inches(3.7), Inches(11.0), Inches(0.9),
     [({"t": "copac", "italic": True}, " ‘tree’: “Plantă cu trunchiul lemnos și înalt … ; ", {"t": "arbore", "bold": True}, ", pom.”   ",
       {"t": "arbore", "italic": True}, ": “… plantă cu trunchi înalt … ; ", {"t": "copac", "bold": True}, "; pom.”")],
     size=16, color=INK2)
text(s, Inches(1.2), Inches(4.7), Inches(11.2), Inches(1.8),
     [({"t": "How many words must a reader already know ", "bold": True},
       {"t": "before the dictionary can explain all the others?", "bold": True, "color": BLUE}),
      "Somewhere the circle has to be broken by words learned from experience: the symbol grounding problem (Harnad 1990)."],
     size=24)
notes(s, "(1:00) Căutați copac în DEX: definiția se termină cu arbore. Căutați arbore: apare copac. Dacă nu știți niciunul, rămâneți în cerc. "
         "Întrebarea noastră: câte cuvinte, și care, trebuie știute dinainte, din experiență, pentru ca tot restul dicționarului să poată fi înțeles numai din definiții?")

# ── 3 structura latenta
s = base("Definitions reveal layers that the alphabet hides", "What we mean by the latent (hidden) structure")
cx, cy = Inches(3.1), Inches(4.35)
for rad, col in ((2.45, GREY), (1.8, RGBColor(0xcd, 0xe2, 0xfb)), (1.2, RGBColor(0x86, 0xb6, 0xef)), (0.62, BLUE)):
    box(s, cx - Inches(rad), cy - Inches(rad), Inches(2 * rad), Inches(2 * rad), col, None, MSO_SHAPE.OVAL)
for lab, yy, col in (("Rest", 2.1, INK2), ("Kernel", 2.75, INK2), ("Core", 3.4, INK), ("MinSet", 4.15, SURF)):
    text(s, cx - Inches(1.0), Inches(yy), Inches(2.0), Inches(0.4), lab, size=16, bold=True, color=col, align=PP_ALIGN.CENTER)
EXA = lambda ws: ", ".join(ws)
text(s, Inches(6.1), Inches(1.75), Inches(6.6), Inches(5.0),
     [({"t": "Graph: ", "bold": True}, "an arrow from each word to every headword in whose definition it occurs."),
      ({"t": "Rest: ", "bold": True}, "words that define no other word; they can always be learned last. ",
       {"t": EXA(["arici", "mânz", "topor"]), "italic": True, "color": INK2}),
      ({"t": "Kernel: ", "bold": True}, "what remains after removing them again and again; all other words are defined from it."),
      ({"t": "Core: ", "bold": True}, "its largest part in which every word leads to every other through definitions. ",
       {"t": EXA(["pom", "câine", "noapte"]), "italic": True, "color": INK2}),
      ({"t": "MinSet: ", "bold": True}, "a smallest set of words that, known in advance, makes the whole dictionary learnable. ",
       {"t": EXA(["apă", "om", "a fi", "a face"]), "italic": True, "color": INK2}),
      ({"t": "Hidden: ", "bold": True, "color": BLUE},
       {"t": "no single entry shows it; it appears only when all definitions are read together.", "color": BLUE})],
     size=17, gap=0.35)
notes(s, "(1:15) Ce înseamnă structura latentă. Facem un graf: o săgeată de la fiecare cuvânt la cuvintele în a căror definiție apare. "
         "Scoatem repetat cuvintele care nu definesc nimic, cum ar fi arici sau topor: rămâne nucleul. În nucleu, partea cea mai legată e Core. "
         "Iar MinSet e cel mai mic set de cuvinte din care, dacă le știi, poți învăța tot dicționarul: apă, om, a fi, a face. "
         "E „ascunsă” pentru că nu o vezi citind intrările una câte una, în ordine alfabetică; apare doar când citești toate definițiile împreună. De aici titlul.")

# ── 4 intrebari si contributii
s = base("Three questions, and what is new", "Research questions")
text(s, Inches(0.7), Inches(1.8), Inches(6.2), Inches(4.8),
     [({"t": "Q1 ", "bold": True, "color": BLUE}, "How large are the Kernel and the MinSet of a Romanian dictionary, compared with other languages?"),
      ({"t": "Q2 ", "bold": True, "color": BLUE}, "Which properties of the definitions determine their size?"),
      ({"t": "Q3 ", "bold": True, "color": BLUE}, "Does the Kernel contain the basic vocabulary identified by independent lists: the Swadesh list (about 200 basic meanings used in comparative linguistics; Swadesh 1955) and Graur’s fundamental lexical stock (1954)?")],
     size=20, gap=0.6)
box(s, Inches(7.4), Inches(1.85), Inches(5.3), Inches(4.7), GREY)
text(s, Inches(7.65), Inches(2.0), Inches(4.9), Inches(4.5),
     [({"t": "New in this study", "bold": True, "size": 20},),
      "The first measurement of the latent structure of a Romanian dictionary, over all its headwords.",
      f"The same procedure applied to {NUMW.get(NL, str(NL))} other languages, so that the comparison is fair.",
      "A test against two lists of basic vocabulary compiled without the dictionary.",
      "Graph, layers, mutually defined pairs and code released."], size=17, gap=0.5)
notes(s, "(0:45) Trei întrebări. Cât de mari sunt nucleul și setul minim în DEX și cum se compară cu alte limbi? Ce le determină mărimea? "
         "Și conține nucleul vocabularul de bază: lista Swadesh, adică vreo două sute de sensuri de bază folosite în lingvistica comparată, și lista lui Graur din 1954? "
         "Noutatea: prima măsurătoare pentru română, comparație corectă cu aceeași procedură în alte limbi, verificare pe liste independente și date publice.")

# ── 5 datele
s = base("The data: the whole DEX, second edition", "Data")
stat(s, Inches(0.7), Inches(1.8), f"{R['data']['definitions']:,}", "definitions (first sense of each entry)")
stat(s, Inches(4.7), Inches(1.8), f"{N:,}", "headwords")
stat(s, Inches(8.7), Inches(1.8), pct(R["data"]["from_dex96"] / R["data"]["definitions"], 1),
     "taken from the 1996 printing (G, H, part of I are missing from DEX ’98 in the dump)", color=ORANGE, w=Inches(4.0))
text(s, Inches(0.7), Inches(4.15), Inches(12.0), Inches(2.6),
     [({"t": "Why the second edition? ", "bold": True},
       "It is the only DEX whose full text dexonline distributes under an open licence (GNU GPL). The later revised editions (2009, 2012, 2016) may not be redistributed: the public dump has only the first 23 characters of each of their definitions."),
      ({"t": "Does the 1996 supplement matter? ", "bold": True},
       f"No. DEX ’98 alone gives a Kernel of {pct(D9['dex98_only']['kernel'], 1)} (complete graph: {pct(D9['dex98_dex96']['kernel'], 1)}) and the same MinSet range."),
      ({"t": "First senses only, ", "bold": True}, "as in the earlier studies of English dictionaries, so that the figures can be compared.")],
     size=18, gap=0.45)
notes(s, "(1:00) Datele: DEX-ul ediția a doua, întreg, așa cum îl distribuie dexonline. De ce a doua ediție și nu cele din 2009 sau 2016? Pentru că e singura distribuită integral sub licență liberă; "
         "edițiile ulterioare apar în export doar cu primele 23 de caractere ale fiecărei definiții. În export, DEX ’98 nu are literele G, H și o parte din I, așa că le luăm din tirajul din 1996: 7% din definiții. "
         "Am verificat: numai cu DEX ’98, rezultatele sunt aceleași. Folosim primul sens, ca studiile anterioare, ca să putem compara.")

# ── 6 metoda
s = base("From definitions to a graph, with every step checked", "Method")
steps = [("1  Arcs", "Each word of a definition is linked to its headword through the dexonline inflection tables (2.27 million forms)."),
         ("2  Ambiguity", f"{pct(ai['ambig_rate'])} of the forms are ambiguous: sare is ‘salt’ or ‘jumps’; fire is ‘threads’, ‘temper’ or ‘to be’."),
         ("3  Language model", f"Claude Haiku 4.5 chooses the lemma in context. A stronger model agrees on {pct(V['opus_random_content'])} of content-word choices; every result is also computed without any model."),
         ("4  MinSet bounds", f"Integer programming proves a lower and an upper bound: {LB:,}–{UB:,} words.")]
for i, (h, b) in enumerate(steps):
    x = Inches(0.7 + i * 3.1)
    box(s, x, Inches(1.95), Inches(2.85), Inches(0.75), BLUE, label=h, size=19, color=SURF, bold=True)
    text(s, x, Inches(2.85), Inches(2.85), Inches(3.0), b, size=16)
    if i < 3: arrow(s, x + Inches(2.85), Inches(2.32), x + Inches(3.1), Inches(2.32), color=INK2, width=1.5)
text(s, Inches(0.7), Inches(5.8), Inches(12.0), Inches(0.8),
     f"The language model does one narrow, checkable task; the full run cost about {V['cost_usd']:.0f} USD, so the procedure can be repeated for other dictionaries.",
     size=16, color=INK2)
notes(s, "(1:15) Metoda în patru pași. Legăm fiecare cuvânt din definiție de cuvântul-titlu, prin tabelele de flexiune dexonline. "
         "Un sfert din forme sunt ambigue: sare poate fi substantiv sau verb. Un model de limbaj alege lema în context; îl verificăm cu un model mai puternic, 87% acord, și refacem totul fără model. "
         "Mărimea setului minim e o problemă NP-dificilă, așa că demonstrăm o limită inferioară și una superioară, prin programare în numere întregi. Totul a costat cam 23 de dolari, deci se poate repeta.")

# ── 7 rezultat: marime
s = base("A third of the DEX is Kernel; a tenth is MinSet", "Result 1 · Q1")
s.shapes.add_picture(FIG + "fig1_size.png", Inches(0.6), Inches(1.8), width=Inches(7.2))
stat(s, Inches(8.4), Inches(1.9), pct(L["Kernel"]["share"]), f"of the headwords are in the Kernel ({L['Kernel']['size']:,} words)")
stat(s, Inches(8.4), Inches(4.0), f"{100*LB/N:.1f}–{100*UB/N:.1f}%", f"MinSet: {LB:,}–{UB:,} words (proven bounds)",
     color=ORANGE, w=Inches(4.5))
text(s, Inches(8.4), Inches(5.95), Inches(4.5), Inches(0.6), "English dictionaries: Kernel 7–12%, MinSet about 1%.",
     size=15, color=INK2)
notes(s, f"(0:45) Primul rezultat. Nucleul DEX are o treime din cuvinte. Setul minim are între {LB:,} și {UB:,} de cuvinte, aproape zece la sută. "
         f"În dicționarele englezești studiate înainte, nucleul are 7–12% și setul minim în jur de 1%. Dar acolo procedura era alta; de aceea slide-ul următor compară corect.")

# ── 8 comparatia
s = base(f"The DEX stands apart from {NUMW.get(NL, str(NL))} other languages", "Result 2 · Q1, same procedure for all")
s.shapes.add_picture(FIG + "fig5_crossling.png", Inches(0.45), Inches(1.6), height=Inches(5.2))
text(s, Inches(8.85), Inches(1.75), Inches(4.2), Inches(5.0),
     [({"t": "Measure: ", "bold": True}, "the share of the Kernel taken by the MinSet, which does not depend on dictionary size."),
      ({"t": f"{min(XR):.0f}–{max(XR):.0f}%", "bold": True, "color": INK2, "size": 26}, " in all other dictionaries"),
      ({"t": f"{min(kr(XD, 'freq'), kr(XD, 'all')):.0f}–{max(kr(XD, 'freq'), kr(XD, 'all')):.0f}%", "bold": True, "color": BLUE, "size": 26},
       f" in the DEX: {DEX_Z:.1f} standard deviations above their mean"),
      ({"t": "Not a Romance effect: ", "bold": True}, f"Italian, Spanish, Portuguese and French have {min(ROM):.0f}–{max(ROM):.0f}%."),
      ({"t": "Different dictionary types: ", "bold": True},
       f"the others are Wiktionaries (collaborative) and WordNet (a lexical database, {kr(WN, 'freq'):.0f}%). The DEX run through the Wiktionary procedure keeps its value.")],
     size=15, gap=0.4)
notes(s, f"(1:30) Am aplicat exact aceeași procedură pe Wiktionary-urile a {NL} limbi și pe WordNet. Măsura comparabilă e cât din nucleu ocupă setul minim, pentru că nu depinde de mărimea dicționarului. "
         f"Peste tot: {min(XR):.0f}–{max(XR):.0f}%. În DEX: {DEX_RATIO:.0f}%, adică {DEX_Z:.1f} abateri standard peste medie. "
         f"Nu e un efect al limbilor romanice: italiana, spaniola, portugheza și franceza au {min(ROM):.0f}–{max(ROM):.0f}%. "
         "Tipul de dicționar contează, de aceea avem două controale: WordNet, care nu e Wiktionary, stă în același interval; iar DEX-ul trecut prin procedura Wiktionary își păstrează valoarea. "
         "Wiktionary-ul românesc seamănă cu DEX-ul, dar 70% din definițiile lui sunt copiate din DEX, deci nu e o dovadă independentă.")

# ── 9 de ce
s = base("Why: words defined by each other, mostly synonyms", "Result 3 · Q2")
for i, (a, b) in enumerate(R["pairs"]["examples"][:6]):
    x = Inches(0.7 + (i % 3) * 4.1); y = Inches(1.85 + (i // 3) * 1.2)
    box(s, x, y, Inches(3.8), Inches(0.95), PALE, label=f"{a}  ⇄  {b}", size=23, italic=True)
text(s, Inches(0.7), Inches(4.45), Inches(12.0), Inches(2.3),
     [({"t": f"{R['pairs']['n']:,} pairs of headwords occur in each other’s definitions", "bold": True, "color": BLUE},
       f": about {round(1000 * R['pairs']['n'] / N)} per 1,000 headwords, "
       f"{max(5, round(XD['reciprocal_pairs_per_1000'] / max(PP) / 5) * 5)} to {round(XD['reciprocal_pairs_per_1000'] / min(PP) / 5) * 5} times more often than in the other dictionaries."),
      f"Each pair is a cycle of length two: one of its words must be in every MinSet. Such pairs make up {pct(R.get('two_cycle_share', 0.98))} of the disjoint cycles behind the lower bound.",
      f"About {pct(R['pairs']['derivational'])} of the pairs share a stem (masticare–masticație); most of the others are synonyms. Learner’s dictionaries of English avoid this with a controlled defining vocabulary."],
     size=18, gap=0.45)
notes(s, "(1:15) De ce? Aproape nouă mii de perechi de cuvinte se definesc unul prin altul: arbore și copac, amabil și binevoitor, primejdie și risc. "
         "Fiecare pereche e un cerc de lungime doi, deci un cuvânt din ea trebuie să fie în orice set minim. Asta explică aproape tot. "
         "Nu sunt greșeli: definirea prin sinonim e o tehnică legitimă. Dicționarele englezești pentru cursanți o evită folosind un vocabular de definire controlat, de circa două mii de cuvinte.")

# ── 10 robustete
s = base("The result holds without the model and without DEX ’96", "Robustness")
s.shapes.add_picture(FIG + "fig3_robustness.png", Inches(0.6), Inches(1.8), width=Inches(7.2))
RNG_K = f"{min(100 * r['kernel'] / N for r in _rg):.0f}–{max(100 * r['kernel'] / N for r in _rg):.0f}%"
RNG_M = f"{min(100 * r.get('minset_lb_ilp', r['minset_lb']) / N for r in _rg):.1f}–{max(100 * r['minset_ub'] / N for r in _rg):.1f}%"
text(s, Inches(8.3), Inches(1.9), Inches(4.6), Inches(4.8),
     [({"t": "Three ways of resolving ambiguous forms", "bold": True},),
      "the language model · the most frequent lemma · all candidate lemmas",
      ({"t": "Same picture each time: ", "bold": True}, f"Kernel {RNG_K}, MinSet {RNG_M}."),
      ({"t": "DEX ’98 alone, ", "bold": True},
       f"without the 1996 supplement: Kernel {pct(D9['dex98_only']['kernel'], 1)}, MinSet {100*D9['dex98_only']['minset_lb']:.1f}–{100*D9['dex98_only']['minset_ub']:.1f}% (complete graph: {100*D9['dex98_dex96']['minset_lb']:.1f}–{100*D9['dex98_dex96']['minset_ub']:.1f}%).")],
     size=17, gap=0.45)
notes(s, f"(0:45) Rezultatul nu depinde de model: refacem totul cu regula celei mai frecvente leme și cu toate lemele posibile. Nucleul rămâne {RNG_K}, setul minim {RNG_M}. "
         "Și nu depinde de completarea din tirajul 1996: numai cu DEX ’98, cifrele sunt practic aceleași.")

# ── 11 vocabular de baza
s = base("The Kernel contains the basic vocabulary", "Result 4 · Q3, no list given to the method")
s.shapes.add_picture(FIG + "fig2_enrichment.png", Inches(0.55), Inches(1.8), width=Inches(8.1))
text(s, Inches(8.95), Inches(1.85), Inches(4.0), Inches(4.9),
     [({"t": pct(S["layers"]["Kernel"]["rate"]), "bold": True, "color": BLUE, "size": 30}, " of the Swadesh list in the Kernel"),
      ({"t": pct(G["all"]["Kernel"]["rate"], 1), "bold": True, "color": BLUE, "size": 30}, " of Graur’s 1,419 words in the Kernel"),
      ({"t": f"by chance: {pct(L['Kernel']['share'])}", "color": INK2}, ""),
      f"Graur’s most certain words are the most central: {pct(G['core']['MinSet']['rate'])} in the MinSet, against {pct(G['middle']['MinSet']['rate'])} and {pct(G['maximal']['MinSet']['rate'])} for his wider groups.",
      ({"t": "The graph is computed from definitions alone, so the overlap is evidence that it isolates a real lexical core.", "color": INK2},)],
     size=16, gap=0.4)
notes(s, f"(1:00) Este acest nucleu real lingvistic? Calculul nu știe nimic despre vocabularul de bază, folosește doar definițiile. "
         f"Și totuși nucleul conține {pct(S['layers']['Kernel']['rate'])} din lista Swadesh și {pct(G['all']['Kernel']['rate'], 1)} din lista lui Graur, față de o treime cât ar fi la întâmplare. "
         "Mai mult, cuvintele pe care Graur le considera cele mai sigure sunt cele mai centrale: aproape jumătate sunt în setul minim.")

# ── 12 doua nuclee
s = base("Two cores: inherited words and defining words", "Result 5")
s.shapes.add_picture(FIG + "fig4_etymology.png", Inches(0.55), Inches(1.8), width=Inches(8.0))
outk = [w for w in ["arici", "mânz", "țap", "țarc", "teasc", "topor", "prag", "ginere", "socru", "vișin"] if w in G["outside_kernel"]]
text(s, Inches(8.85), Inches(1.85), Inches(4.1), Inches(4.9),
     [({"t": "Graur’s core: ", "bold": True}, "old, stable, mostly Latin and Slavic."),
      ({"t": "The defining core: ", "bold": True}, "the 1,419 words used most in definitions are mostly learned French loanwords: ",
       {"t": "acțiune, rezultat, persoană", "italic": True}, "."),
      f"Only {E['graur_in_top1419']} words belong to both.",
      ({"t": "arbore", "italic": True, "bold": True},
       f": excluded by Graur, yet used in {WD['arbore']['o']} DEX definitions (copac: {WD['copac']['o']})."),
      ({"t": "Outside the Kernel: ", "bold": True}, {"t": ", ".join(outk[:6]), "italic": True}, ": defined, but defining nothing.")],
     size=16, gap=0.4)
notes(s, "(1:00) Dar nucleul are două fețe. Cuvintele lui Graur sunt vechi, latinești și slave. Cuvintele cu care DEX-ul își scrie definițiile sunt mai ales împrumuturi savante franceze: acțiune, rezultat, persoană. "
         "Graur a exclus arbore din fondul principal, din cauza concurenței cu copac; DEX-ul folosește arbore aproape de două ori mai des. "
         "Preferințele dicționarului și uzul descris de Graur sunt lucruri diferite, și graful le separă.")

# ── 13 utilitate
s = base("What the results are good for", "Uses")
bullets(s, Inches(0.7), Inches(1.85), Inches(12.0), Inches(4.8),
        [("Revising definitions", f"the list of {R['pairs']['n']:,} mutually defined pairs shows where the DEX explains a word only by a synonym."),
         ("A Romanian defining vocabulary", "the Kernel and the MinSet, with frequency, are a starting point for learner’s dictionaries and for teaching Romanian as a foreign language."),
         ("Language technology", "the graph and its layers are a resource for work on definitions, e.g. checking definitions generated by language models."),
         ("History of linguistics", "Graur’s 1954 list tested with data that were not available to him.")], size=18)
notes(s, "(0:45) La ce folosesc rezultatele. Lexicografilor: lista perechilor care se definesc reciproc arată unde un cuvânt e explicat doar printr-un sinonim. "
         "Didacticii: nucleul și setul minim sunt un punct de plecare pentru un vocabular de definire al limbii române. Tehnologiei limbajului: o resursă publică. Și istoriei lingvisticii: lista lui Graur testată cu date noi.")

# ── 14 cat de siguri
s = base("How strong is the evidence", "Strengths and limits")
rows = [("Strong", f"The DEX is far more circular than dictionaries of {NL} other languages processed the same way; reciprocal definitions explain it.", BLUE),
        ("Strong", "Swadesh and Graur words are concentrated in the Kernel (p < 10⁻²⁰⁰); results unchanged without the language model.", BLUE),
        ("Good", f"MinSet: proven bounds {LB:,}–{UB:,} (gap {100*(UB-LB)/UB:.1f}%), not an exact value.", AQUA),
        ("Open", "Whether the large core is specific to the DEX or common to Romanian lexicography: older dictionaries are needed.", ORANGE),
        ("Scope", "One edition, first senses only; the other dictionaries are of a different type (controlled as shown).", MUTED)]
for i, (tag, t, col) in enumerate(rows):
    y = Inches(1.9 + i * 0.92)
    box(s, Inches(0.7), y, Inches(1.8), Inches(0.66), col, label=tag, size=16, color=SURF, bold=True)
    text(s, Inches(2.75), y + Inches(0.06), Inches(10.2), Inches(0.8), t, size=18)
notes(s, "(0:45) Cât de solide sunt concluziile. Foarte solide: circularitatea mai mare a DEX-ului și cauza ei, plus concentrarea vocabularului de bază în nucleu. "
         "Bine: mărimea setului minim, cu limite demonstrate. Deschis: dacă e o trăsătură a DEX-ului sau a lexicografiei românești; pentru asta trebuie dicționare mai vechi, independente de DEX, și lucrăm la asta.")

# ── 15 concluzie
s = base("Take-home", "Conclusion")
text(s, Inches(0.7), Inches(1.85), Inches(12.0), Inches(4.0),
     [("A third of the DEX forms a Kernel; about one word in ten must be known in advance to read the whole dictionary."),
      (f"Relative to its Kernel, the DEX needs about twice as large a MinSet as dictionaries of {NL} other languages, because it often defines words by synonyms."),
      ("Computed from definitions alone, the Kernel contains almost all the basic vocabulary of Romanian."),
      ({"t": "Graph, layers, mutual pairs and code: github.com/ovladon/hidden-core-romanian", "bold": True, "color": BLUE},)],
     size=22, gap=0.6)
text(s, Inches(0.7), Inches(6.15), Inches(12), Inches(0.5),
     "vlad.belciug@365.univ-ovidius.ro · epelican@univ-ovidius.ro · Thanks to the dexonline volunteers.", size=15, color=INK2)
notes(s, "(0:30) Pe scurt: o treime din DEX e nucleu; un cuvânt din zece trebuie știut dinainte. Raportat la nucleu, DEX-ul are nevoie de un set minim de circa două ori mai mare decât dicționarele altor limbi, pentru că definește des prin sinonime. "
         "Și nucleul, calculat doar din definiții, conține aproape tot vocabularul de bază. Datele și codul sunt publice. Vă mulțumesc!")

# ── Rezerva (pentru intrebari)
s = base("Which DEX, and why", "Backup · data", backup=True)
eds = [("1975", "first edition", "not distributable; present in dexonline only as fragments"),
       ("1996 / 1998", "second edition", "full text under GNU GPL: used here (1998 printing, completed from 1996 for G–I)"),
       ("2009, 2012, 2016", "revised editions", "listed by dexonline, not redistributable; dump keeps the first 23 characters of each definition")]
tshape = s.shapes.add_table(len(eds) + 1, 3, Inches(0.7), Inches(1.8), Inches(11.9), Inches(2.4)); tbl = tshape.table
for j, wd in enumerate((2.2, 2.4, 7.3)): tbl.columns[j].width = Inches(wd)
for j, h_ in enumerate(["year", "edition", "availability for research"]):
    tbl.cell(0, j).text = h_
for i, row in enumerate(eds, 1):
    for j, v in enumerate(row): tbl.cell(i, j).text = v
for i in range(len(eds) + 1):
    for j in range(3):
        c = tbl.cell(i, j)
        for r in c.text_frame.paragraphs[0].runs:
            r.font.size = Pt(17); r.font.name = FONT; r.font.bold = (i == 0); r.font.color.rgb = SURF if i == 0 else INK
        c.fill.solid(); c.fill.fore_color.rgb = BLUE if i == 0 else (SURF if i % 2 else GREY)
text(s, Inches(0.7), Inches(5.0), Inches(12), Inches(1.6),
     [f"Definitions used: {R['data']['from_dex98']:,} from DEX ’98 and {R['data']['from_dex96']:,} from DEX ’96 ({pct(R['data']['from_dex96'] / R['data']['definitions'], 1)}).",
      f"DEX ’98 alone ({D9['dex98_only']['headwords']:,} headwords): Kernel {pct(D9['dex98_only']['kernel'], 1)}, MinSet {100*D9['dex98_only']['minset_lb']:.1f}–{100*D9['dex98_only']['minset_ub']:.1f}%, reciprocal pairs {D9['dex98_only']['pairs_per_1000']:.0f} per 1,000 headwords (complete graph: {pct(D9['dex98_dex96']['kernel'], 1)}, {100*D9['dex98_dex96']['minset_lb']:.1f}–{100*D9['dex98_dex96']['minset_ub']:.1f}%, {D9['dex98_dex96']['pairs_per_1000']:.0f})."],
     size=17)
notes(s, "Rezervă, dacă întreabă de ediții: doar ediția a doua e distribuită integral sub GPL. Edițiile 2009–2016 sunt în dexonline, dar nu pot fi redistribuite; în export apar trunchiate la 23 de caractere. "
         "Completarea din 1996 reprezintă 7% din definiții și nu schimbă rezultatele.")

s = base("Is the comparison fair across dictionary types?", "Backup · comparison", backup=True)
text(s, Inches(0.7), Inches(1.85), Inches(12.0), Inches(4.8),
     [({"t": "Same rules for every dictionary: ", "bold": True},
       "single-word lemmas with a noun, verb, adjective, adverb or numeral entry; first sense of each entry; function words ignored; forms mapped with each dictionary’s own inflection data."),
      ({"t": "Size-independent measure: ", "bold": True},
       "the Kernel’s share of the headwords falls as dictionaries grow, the MinSet’s share of the Kernel does not."),
      ({"t": "Control 1: ", "bold": True}, f"WordNet, a lexical database and not a Wiktionary, has {kr(WN, 'freq'):.0f}%, inside the range of the Wiktionaries ({min(XR):.0f}–{max(XR):.0f}%)."),
      ({"t": "Control 2: ", "bold": True}, f"the DEX converted to the Wiktionary format and processed by the same program: {min(kr(XD, 'freq'), kr(XD, 'all')):.0f}–{max(kr(XD, 'freq'), kr(XD, 'all')):.0f}%."),
      ({"t": "Romanian Wiktionary: ", "bold": True}, "close to the DEX, but 70% of its first definitions are near-copies of the DEX, so it is not independent evidence.")],
     size=18, gap=0.5)
notes(s, "Rezervă, dacă întreabă de comparabilitate: aceleași reguli pentru toate dicționarele, o măsură care nu depinde de mărime și două controale pentru tipul de dicționar.")

s = base("The language model: a narrow task, checked three ways", "Backup · method", backup=True)
text(s, Inches(0.7), Inches(1.85), Inches(12.0), Inches(4.8),
     [({"t": "Input: ", "bold": True}, "a definition, its ambiguous words and, for each, the numbered candidate lemmas with their parts of speech; 15 definitions per request."),
      ({"t": "Output: ", "bold": True}, "the number of the chosen lemma (or none, e.g. for the infinitive marker a)."),
      ({"t": "Check 1: ", "bold": True}, f"a stronger model on {V['opus_random_n_defs']} random definitions agrees on {pct(V['opus_random_content'])} of content-word choices; most disagreements are defensible (declarat as adjective or verb)."),
      ({"t": "Check 2: ", "bold": True}, "every result is recomputed with two model-free rules; the conclusions do not change."),
      ({"t": "Cost: ", "bold": True}, f"about {V['cost_usd']:.0f} USD for the whole dictionary ({V['ai_choices']:,} choices).")],
     size=18, gap=0.5)
notes(s, "Rezervă despre model: sarcina e îngustă și verificabilă; acordul cu un model mai puternic e 87%, iar concluziile rămân aceleași fără model.")

s = base("How the MinSet is bounded", "Backup · optimisation", backup=True)
text(s, Inches(0.7), Inches(1.85), Inches(12.0), Inches(4.8),
     [({"t": "The problem: ", "bold": True}, "a minimum feedback vertex set, NP-hard (Karp 1972); a dictionary has many MinSets of the same size."),
      ({"t": "Upper bound: ", "bold": True}, "any concrete grounding set; we check that removing it leaves no cycle."),
      ({"t": "Lower bound: ", "bold": True}, "an integer program chooses the fewest words such that every known cycle contains one of them; cycles are added round by round, and each optimum is a valid lower bound."),
      ({"t": "Result: ", "bold": True}, f"{LB:,} ≤ MinSet ≤ {UB:,} words, a gap of {100*(UB-LB)/UB:.1f}%.")],
     size=18, gap=0.5)
notes(s, "Rezervă despre optimizare: problema e NP-dificilă; limita superioară e o mulțime concretă verificată, limita inferioară vine din programul în numere întregi.")

s = base("Graur’s own examples, seen through the graph", "Backup · case studies", backup=True)
CATN = {"C": "most certain", "M": "middle group", "X": "widest group", "": "not in the list"}
LAYN = {"minset": "MinSet", "core": "Core", "satellite": "Satellite", "rest": "outside Kernel"}
ex = [w for w in ["arbore", "copac", "pom", "femeie", "nevastă", "muiere", "cioban", "păcurar", "doagă", "săgeată", "concert", "axiomă"] if w in WD]
tbl = s.shapes.add_table(len(ex) + 1, 4, Inches(0.7), Inches(1.8), Inches(9.0), Inches(0.36 * (len(ex) + 1))).table
for j, h_ in enumerate(["word", "Graur 1954", "graph layer", "used in definitions of"]):
    tbl.cell(0, j).text = h_
for i, w in enumerate(ex, 1):
    d = WD[w]
    for j, v in enumerate([w, CATN[d.get("g", "")], LAYN[d["l"]], f"{d['o']:,} headwords"]):
        tbl.cell(i, j).text = v
for i in range(len(ex) + 1):
    for j in range(4):
        c = tbl.cell(i, j)
        for r in c.text_frame.paragraphs[0].runs:
            r.font.size = Pt(15); r.font.name = FONT; r.font.bold = (i == 0); r.font.italic = (j == 0 and i > 0)
            r.font.color.rgb = SURF if i == 0 else INK
        c.fill.solid(); c.fill.fore_color.rgb = BLUE if i == 0 else (SURF if i % 2 else GREY)
notes(s, "Rezervă: exemplele discutate de Graur și poziția lor în graf.")

s = base("Graur’s list: how it was transcribed and checked", "Backup · data", backup=True)
text(s, Inches(0.7), Inches(1.85), Inches(12.0), Inches(4.8),
     [f"Transcribed from pp. 48–55 of the 1954 book: {G['entries']:,} entries, Slavic share 21.49%, both exactly as published.",
      "Certainty groups: 966 / 216 / 237 against Graur’s 964 / 217 / 238, so two marks out of 1,419 remain uncertain.",
      "Orthography modernised to the 1993 norm; inflected forms mapped to lemmas (eram, ești → fi).",
      f"{G['linked']:,} entries linked to DEX headwords. The transcription is not distributed, for copyright reasons."],
     size=19, gap=0.6)
notes(s, "Rezervă: cum am transcris lista lui Graur și cum am verificat-o față de totalurile publicate.")

prs.save("HiddenCore_ConsILR2026.pptx")
print("scris HiddenCore_ConsILR2026.pptx,", len(prs.slides), "slide-uri")
