#!/usr/bin/env python3
"""The short conference talk (pptx): one idea per slide, large numbers and real examples; four backup slides.
The detailed deck (make_slides.py) remains the full backup. Figures from talk_figures.py.

  cd slides && python3 talk_figures.py && python3 make_talk.py
"""
import json, statistics
from talk_script import SLIDES as SCRIPT
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

R = json.load(open("../results/results.json", encoding="utf8"))
N = R["data"]["headwords"]; ai = R["regimes"]["ai"]
LB = ai.get("minset_lb_ilp", ai["minset_lb"]); UB = ai["minset_ub"]
G, S, E, L, V = R["graur"], R["swadesh"], R["etymology"], R["layers"], R["validation"]
D9 = json.load(open("../results/dex98_only.json", encoding="utf8"))
XS = json.load(open("../crossling/summary.json", encoding="utf8"))
XO = [r for r in XS if r["language"] != "Romanian"]; XD = next(r for r in XS if r["code"] == "dex")
WN = next(r for r in XS if r["code"] == "wordnet")
WD = json.load(open("html_data.json", encoding="utf8"))["words"]
kr = lambda r, g: 100 * (r[g]["minset_lb_n"] + r[g]["minset_ub_n"]) / 2 / r[g]["kernel_n"]
XR = [kr(r, g) for r in XO for g in ("freq", "all")]
ROM = [kr(r, g) for r in XO if r["language"] in ("Italian", "Spanish", "Portuguese", "French") for g in ("freq", "all")]
MIDS = [(kr(r, "freq") + kr(r, "all")) / 2 for r in XO]
DEXR = (kr(XD, "freq") + kr(XD, "all")) / 2
DEX_Z = (DEXR - statistics.mean(MIDS)) / statistics.stdev(MIDS)
EDGES = 600473
LOGO = "../../../ConsILR2025/logo_consilr.png"

NAVY, NAVY2 = RGBColor(0x13, 0x23, 0x3f), RGBColor(0x24, 0x3a, 0x63)
ORANGE, BLUE, PALE = RGBColor(0xeb, 0x68, 0x34), RGBColor(0x2a, 0x78, 0xd6), RGBColor(0xe8, 0xf1, 0xfb)
INK, INK2, MUTED, WHITE = RGBColor(0x14, 0x14, 0x14), RGBColor(0x4a, 0x49, 0x46), RGBColor(0x8f, 0x8e, 0x89), RGBColor(0xff, 0xff, 0xff)
PAPER, SOFT, GREYC = RGBColor(0xfb, 0xfa, 0xf7), RGBColor(0xc9, 0xd3, 0xe4), RGBColor(0xd9, 0xd7, 0xd1)
FONT, HFONT = "Calibri", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]; W, H = prs.slide_width, prs.slide_height
C = {"n": 0, "b": 0}


def text(s, x, y, w, h, runs, size=24, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, gap=0.3,
         font=FONT):
    tb = s.shapes.add_textbox(x, y, w, h); tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.03)
    for i, para in enumerate(runs if isinstance(runs, list) else [runs]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        for seg in (para if isinstance(para, tuple) else (para,)):
            r = p.add_run(); d = seg if isinstance(seg, dict) else {"t": seg}
            r.text = d["t"]; f = r.font; f.name = d.get("font", font); f.size = Pt(d.get("size", size))
            f.bold = d.get("bold", bold); f.italic = d.get("italic", False); f.color.rgb = d.get("color", color)
        p.space_after = Pt(size * gap)
    return tb


def shape(s, kind, x, y, w, h, fill, line=None):
    b = s.shapes.add_shape(kind, x, y, w, h); b.fill.solid(); b.fill.fore_color.rgb = fill
    if line: b.line.color.rgb = line; b.line.width = Pt(1.5)
    else: b.line.fill.background()
    b.shadow.inherit = False
    return b


def label(b, t, size=22, color=INK, bold=False, italic=False):
    tf = b.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, line in enumerate(t if isinstance(t, list) else [t]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = line; f = r.font; f.name = FONT; f.size = Pt(size if i == 0 else size * 0.62)
        f.bold = bold and i == 0; f.italic = italic and i == 0; f.color.rgb = color


def arrow(s, x1, y1, x2, y2, color=ORANGE, width=3.0):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2); c.line.color.rgb = color; c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd", {"type": "triangle"}))


def slide(dark=False, kicker=None, title=None, backup=False):
    s = prs.slides.add_slide(BLANK); bg = s.background.fill; bg.solid(); bg.fore_color.rgb = NAVY if dark else PAPER
    if backup: C["b"] += 1
    else: C["n"] += 1
    if kicker:
        text(s, Inches(0.75), Inches(0.42), Inches(10), Inches(0.4), kicker.upper(), size=14, bold=True,
             color=(ORANGE if backup else (SOFT if dark else BLUE)))
    if title:
        text(s, Inches(0.75), Inches(0.78), Inches(11.8), Inches(1.0), title, size=36, bold=True,
             color=WHITE if dark else NAVY, font=HFONT)
    if C["n"] > 1 or backup:
        text(s, Inches(0.75), H - Inches(0.5), Inches(8), Inches(0.35), "The Hidden Core of Romanian · ConsILR 2026",
             size=11, color=SOFT if dark else MUTED)
        text(s, W - Inches(1.6), H - Inches(0.5), Inches(0.9), Inches(0.35),
             f"B{C['b']}" if backup else str(C["n"]), size=11, color=SOFT if dark else MUTED, align=PP_ALIGN.RIGHT)
    return s


def notes(s, t):
    s.notes_slide.notes_text_frame.text = t


def NOTE():
    n, title, t, ro, en, cue = SCRIPT[C["n"] - 1]
    return f"({t}) {ro}\n\n[{cue}]"


# ── 1 titlu
s = slide(dark=True)
s.shapes.add_picture("talk_graph_dark.png", Inches(7.45), Inches(0.75), width=Inches(5.55))
s.shapes.add_picture(LOGO, Inches(0.75), Inches(0.6), height=Inches(0.75))
text(s, Inches(0.75), Inches(2.05), Inches(6.5), Inches(2.2), "The Hidden Core of Romanian", size=50, bold=True, color=WHITE)
text(s, Inches(0.75), Inches(3.75), Inches(6.3), Inches(0.9), "A graph-theoretic analysis of dictionary definitions",
     size=22, color=SOFT)
text(s, Inches(0.75), Inches(4.95), Inches(6.4), Inches(1.6),
     [({"t": "Vlad Belciug · Elena Pelican", "bold": True, "size": 20, "color": WHITE},),
      "“Ovidius” University of Constanța, Faculty of Mathematics and Informatics", "ConsILR 2026 · Galați"],
     size=15, color=SOFT, gap=0.25)
text(s, Inches(7.4), Inches(6.85), Inches(5.6), Inches(0.4),
     "A real piece of the DEX: orange = words to know first; white arrows = words defined by each other",
     size=11, color=SOFT, align=PP_ALIGN.RIGHT)
notes(s, NOTE())

# ── 2 cercul
s = slide(kicker="A simple experiment", title="Look up copac. Then look up arbore.")
b1 = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(2.35), Inches(3.6), Inches(1.5), PALE, BLUE)
label(b1, ["copac", "‘tree’"], size=40, italic=True, color=NAVY)
b2 = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.4), Inches(2.35), Inches(3.6), Inches(1.5), PALE, BLUE)
label(b2, ["arbore", "‘tree’"], size=40, italic=True, color=NAVY)
arrow(s, Inches(4.95), Inches(2.75), Inches(8.35), Inches(2.75))
arrow(s, Inches(8.35), Inches(3.45), Inches(4.95), Inches(3.45))
text(s, Inches(5.0), Inches(2.15), Inches(3.3), Inches(0.5), "… ; arbore, pom", size=17, color=INK2, align=PP_ALIGN.CENTER)
text(s, Inches(5.0), Inches(3.55), Inches(3.3), Inches(0.5), "… ; copac; pom", size=17, color=INK2, align=PP_ALIGN.CENTER)
text(s, Inches(1.3), Inches(4.75), Inches(10.8), Inches(1.4),
     [({"t": "Each word sends you to the other.", "color": INK},),
      ({"t": "Somewhere, the circle has to be broken by a word you already know.", "color": ORANGE, "bold": True},)],
     size=30, align=PP_ALIGN.CENTER, gap=0.2)
notes(s, NOTE())

# ── 3 intrebarea
s = slide(dark=True)
text(s, Inches(1.0), Inches(2.0), Inches(11.3), Inches(2.6),
     [({"t": "How many words must you ", "color": WHITE}, {"t": "already know", "color": ORANGE}),
      ({"t": "before a dictionary can teach you all the others?", "color": WHITE},)],
     size=44, bold=True, gap=0.15)
text(s, Inches(1.0), Inches(5.0), Inches(11.3), Inches(1.0),
     "The symbol grounding problem (Harnad 1990) · first measured on English dictionaries (Vincent-Lamarre et al. 2016)",
     size=18, color=SOFT)
notes(s, NOTE())

# ── 4 straturile
s = slide(kicker="The answer has a shape", title="Every dictionary has a hidden core")
cx, cy = Inches(3.55), Inches(4.45)
for rad, col in ((2.55, RGBColor(0xee, 0xec, 0xe7)), (1.85, RGBColor(0xcd, 0xe2, 0xfb)), (1.05, ORANGE)):
    shape(s, MSO_SHAPE.OVAL, cx - Inches(rad), cy - Inches(rad), Inches(2 * rad), Inches(2 * rad), col)
text(s, cx - Inches(1.5), Inches(2.0), Inches(3.0), Inches(0.9), [({"t": "Rest", "bold": True},), ({"t": "arici · topor · fag", "italic": True, "size": 15},)],
     size=18, color=INK2, align=PP_ALIGN.CENTER, gap=0.05)
text(s, cx - Inches(1.5), Inches(2.72), Inches(3.0), Inches(0.9), [({"t": "Kernel", "bold": True},), ({"t": "pom · câine · noapte", "italic": True, "size": 15},)],
     size=18, color=NAVY, align=PP_ALIGN.CENTER, gap=0.05)
text(s, cx - Inches(1.0), Inches(3.95), Inches(2.0), Inches(1.0), [({"t": "MinSet", "bold": True},), ({"t": "apă · om · a fi", "italic": True, "size": 15},)],
     size=18, color=WHITE, align=PP_ALIGN.CENTER, gap=0.05)
rows = [("Rest", "words that define no other word"),
        ("Kernel", "the words from which all the others are defined"),
        ("MinSet", "the smallest set you must know first")]
for i, (h_, b_) in enumerate(rows):
    y = Inches(2.2 + i * 1.12)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(7.0), y + Inches(0.08), Inches(0.12), Inches(0.75), [GREYC, BLUE, ORANGE][i])
    text(s, Inches(7.3), y, Inches(5.4), Inches(1.0), [({"t": h_, "bold": True, "size": 24, "color": NAVY},), b_], size=20, gap=0.05)
text(s, Inches(7.0), Inches(5.65), Inches(5.6), Inches(1.0),
     [({"t": "Hidden: ", "bold": True, "color": ORANGE}, "no single entry shows it; it appears only when all definitions are read together.")],
     size=18, color=INK2)
notes(s, NOTE())

# ── 5 ce am facut
s = slide(kicker="What we did", title="We read the whole DEX as a network")
steps = [(f"{R['data']['definitions']:,}", "definitions of the DEX, 2nd edition", "(the full text dexonline distributes)"),
         (f"{EDGES:,}", "links: word → word it defines", "(ambiguous forms resolved by a language model, checked against rules)"),
         ("11", "other languages, same procedure", "(Wiktionaries and WordNet)")]
for i, (big, mid, small) in enumerate(steps):
    x = Inches(0.75 + i * 4.15)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.2), Inches(3.75), Inches(3.4), WHITE, GREYC)
    text(s, x + Inches(0.2), Inches(2.5), Inches(3.35), Inches(1.1), big, size=48, bold=True,
         color=ORANGE if i == 0 else NAVY, align=PP_ALIGN.CENTER)
    text(s, x + Inches(0.25), Inches(3.65), Inches(3.25), Inches(1.9), [({"t": mid, "bold": True},), ({"t": small, "size": 15, "color": INK2},)],
         size=20, align=PP_ALIGN.CENTER, gap=0.2)
    if i < 2: arrow(s, x + Inches(3.8), Inches(3.9), x + Inches(4.1), Inches(3.9), color=MUTED, width=2)
text(s, Inches(0.75), Inches(5.95), Inches(11.8), Inches(0.6),
     "The size of the MinSet is an NP-hard problem: we prove a lower and an upper bound with integer programming.",
     size=17, color=INK2, align=PP_ALIGN.CENTER)
notes(s, NOTE())

# ── 6 rezultat 1
s = slide(kicker="Result 1", title="A third is Kernel. A tenth must be known first.")
text(s, Inches(0.9), Inches(2.0), Inches(5.6), Inches(1.8), f"{100 * L['Kernel']['share']:.0f}%", size=110, bold=True, color=NAVY)
text(s, Inches(0.9), Inches(3.95), Inches(5.6), Inches(1.0), f"of the DEX is Kernel ({L['Kernel']['size']:,} words)", size=22, color=INK2)
text(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(1.8), f"{100 * LB / N:.1f}–{100 * UB / N:.1f}%", size=96, bold=True, color=ORANGE)
text(s, Inches(6.9), Inches(3.95), Inches(5.8), Inches(1.0), f"is MinSet: {LB:,}–{UB:,} words to know first", size=22, color=INK2)
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(5.2), Inches(11.5), Inches(0.95), WHITE, GREYC)
text(s, Inches(1.1), Inches(5.35), Inches(11.1), Inches(0.7),
     [("English dictionaries (Vincent-Lamarre et al. 2016):  Kernel ", {"t": "7–12%", "bold": True}, "  ·  MinSet ", {"t": "≈1%", "bold": True})],
     size=20, color=INK2, align=PP_ALIGN.CENTER)
notes(s, NOTE())

# ── 7 comparatia
s = slide(kicker="Result 2 · same procedure for every dictionary", title="The DEX is about twice as circular")
s.shapes.add_picture("talk_languages.png", Inches(0.6), Inches(1.95), width=Inches(7.4))
text(s, Inches(8.45), Inches(2.0), Inches(4.3), Inches(4.6),
     [({"t": "Share of the Kernel that must be known first", "bold": True, "color": NAVY},),
      f"DEX {DEXR:.0f}%; other languages {min(XR):.0f}–{max(XR):.0f}%",
      ({"t": "Not a Romance effect: ", "bold": True}, f"Italian, Spanish, Portuguese, French {min(ROM):.0f}–{max(ROM):.0f}%"),
      ({"t": "Not the type of dictionary: ", "bold": True}, f"WordNet {kr(WN, 'freq'):.0f}%; the DEX run through the same program keeps its value")],
     size=19, gap=0.55)
notes(s, NOTE())

# ── 8 de ce
s = slide(kicker="Result 3 · why", title="Words that define each other")
s.shapes.add_picture("talk_graph_light.png", Inches(0.55), Inches(1.65), height=Inches(5.2))
text(s, Inches(7.25), Inches(1.9), Inches(5.6), Inches(1.4), f"{R['pairs']['n']:,}", size=88, bold=True, color=ORANGE)
text(s, Inches(7.25), Inches(3.35), Inches(5.6), Inches(0.9), "pairs of words in the DEX are defined by each other", size=22, color=INK, bold=True)
for i, (a, b) in enumerate([("arbore", "copac"), ("amabil", "binevoitor"), ("primejdie", "risc")]):
    bx = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.25), Inches(4.3 + i * 0.68), Inches(4.4), Inches(0.56), PALE)
    label(bx, f"{a}  ⇄  {b}", size=20, italic=True, color=NAVY)
text(s, Inches(7.25), Inches(6.35), Inches(5.6), Inches(0.6), "mostly synonyms · each pair puts one word in the MinSet",
     size=16, color=INK2)
notes(s, NOTE())

# ── 9 vocabular de baza
s = slide(kicker="Result 4", title="The core is linguistically real")
cards = [(f"{100 * S['layers']['Kernel']['rate']:.0f}%", "of the Swadesh list", "200 basic meanings used in comparative linguistics", ORANGE),
         (f"{100 * G['all']['Kernel']['rate']:.1f}%", "of Graur’s fundamental lexical stock", "1,419 words, 1954", ORANGE),
         (f"{100 * L['Kernel']['share']:.0f}%", "expected by chance", "the Kernel’s share of all words", MUTED)]
for i, (big, mid, small, col) in enumerate(cards):
    x = Inches(0.75 + i * 4.15)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.1), Inches(3.75), Inches(3.3), WHITE, GREYC)
    text(s, x + Inches(0.2), Inches(2.35), Inches(3.35), Inches(1.4), big, size=66, bold=True, color=col, align=PP_ALIGN.CENTER)
    text(s, x + Inches(0.25), Inches(3.8), Inches(3.25), Inches(1.6), [({"t": mid, "bold": True},), ({"t": small, "size": 15, "color": INK2},)],
         size=20, align=PP_ALIGN.CENTER, gap=0.2)
text(s, Inches(0.75), Inches(5.8), Inches(11.8), Inches(0.8),
     [("are in the Kernel. ", {"t": "The method never saw these lists: it used the definitions alone.", "bold": True, "color": NAVY})],
     size=20, color=INK2, align=PP_ALIGN.CENTER)
notes(s, NOTE())

# ── 10 doua nuclee
s = slide(kicker="Result 5", title="Two cores in one dictionary")
for i, (head, words, stat_, col, fill) in enumerate([
        ("The inherited core", "apă · om · casă · mână · foc · pâine", "Graur’s list: 53% Latin, 20% Slavic", NAVY, PALE),
        ("The defining core", "acțiune · rezultat · persoană", "the 1,419 words the DEX defines with most:\n35% French, 30% Latin", ORANGE, RGBColor(0xfd, 0xe9, 0xdf))]):
    x = Inches(0.75 + i * 6.05)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.1), Inches(5.75), Inches(3.4), fill)
    text(s, x + Inches(0.35), Inches(2.3), Inches(5.1), Inches(0.7), head, size=28, bold=True, color=col)
    text(s, x + Inches(0.35), Inches(3.1), Inches(5.1), Inches(1.2), words, size=26, color=INK, bold=False)
    text(s, x + Inches(0.35), Inches(4.3), Inches(5.1), Inches(1.1), stat_, size=18, color=INK2)
text(s, Inches(0.75), Inches(5.85), Inches(11.8), Inches(0.8),
     [({"t": "arbore", "italic": True, "bold": True}, f": left out by Graur in 1954, yet used in {WD['arbore']['o']} DEX definitions (copac: {WD['copac']['o']})")],
     size=20, color=INK2, align=PP_ALIGN.CENTER)
notes(s, NOTE())

# ── 11 utilitate
s = slide(kicker="Why it matters", title="What the results can be used for")
for i, (head, body) in enumerate([("Lexicographers", f"a list of {R['pairs']['n']:,} mutually defined pairs to review"),
                                  ("Teachers", "a core vocabulary for learning Romanian and for learner’s dictionaries"),
                                  ("Language technology", "an open network of Romanian definitions, with code for any dictionary")]):
    x = Inches(0.75 + i * 4.15)
    c = shape(s, MSO_SHAPE.OVAL, x + Inches(1.35), Inches(2.05), Inches(1.05), Inches(1.05), [ORANGE, BLUE, NAVY][i])
    label(c, str(i + 1), size=30, color=WHITE, bold=True)
    text(s, x, Inches(3.3), Inches(3.75), Inches(2.6), [({"t": head, "bold": True, "size": 26, "color": NAVY},), body],
         size=20, align=PP_ALIGN.CENTER, gap=0.3)
notes(s, NOTE())

# ── 12 concluzie
s = slide(dark=True, kicker="Take-home")
for i, (big, t) in enumerate([("⅓", "of the DEX is Kernel; one word in ten must be known first"),
                              ("×2", "as circular as dictionaries of 11 other languages: the DEX often defines by synonyms"),
                              ("98%", "of the Swadesh list sits in the Kernel, found from definitions alone")]):
    y = Inches(1.35 + i * 1.45)
    text(s, Inches(0.9), y, Inches(2.4), Inches(1.3), big, size=60, bold=True, color=ORANGE)
    text(s, Inches(3.2), y + Inches(0.3), Inches(9.4), Inches(1.2), t, size=26, color=WHITE)
text(s, Inches(0.9), Inches(5.85), Inches(11.5), Inches(0.5), "Graph, layers and code: github.com/ovladon/hidden-core-romanian",
     size=20, color=SOFT, bold=True)
text(s, Inches(0.9), Inches(6.35), Inches(11.5), Inches(0.5), "Thank you · and thanks to the dexonline volunteers", size=18, color=SOFT)
notes(s, NOTE())

# ── rezerve
s = slide(kicker="Backup", title="Which DEX, and why", backup=True)
for i, (yr, ed, av, col) in enumerate([("1975", "first edition", "not distributable", MUTED),
                                       ("1996 / 1998", "second edition", "full text under GNU GPL: used here", BLUE),
                                       ("2009 – 2016", "revised editions", "not redistributable; the dump keeps 23 characters per definition", MUTED)]):
    y = Inches(2.0 + i * 1.05)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(0.75), y, Inches(0.12), Inches(0.8), col)
    text(s, Inches(1.05), y, Inches(2.6), Inches(0.9), yr, size=24, bold=True, color=NAVY)
    text(s, Inches(3.7), y, Inches(3.0), Inches(0.9), ed, size=22)
    text(s, Inches(6.6), y, Inches(6.2), Inches(0.9), av, size=20, color=INK2)
text(s, Inches(0.75), Inches(5.35), Inches(11.8), Inches(1.2),
     f"DEX ’98 lacks G, H and part of I in the dump: {100 * R['data']['from_dex96'] / R['data']['definitions']:.1f}% of definitions come from DEX ’96. "
     f"With DEX ’98 alone: Kernel {100 * D9['dex98_only']['kernel']:.1f}% (complete graph {100 * D9['dex98_dex96']['kernel']:.1f}%), same MinSet range.",
     size=18, color=INK2)
notes(s, "Rezervă: edițiile DEX.")

s = slide(kicker="Backup", title="Is the comparison fair?", backup=True)
text(s, Inches(0.75), Inches(1.95), Inches(11.8), Inches(4.8),
     [({"t": "Same rules ", "bold": True, "color": NAVY}, "for every dictionary: single-word lemmas, first sense, function words ignored, each dictionary’s own inflection data."),
      ({"t": "A measure that does not depend on size: ", "bold": True, "color": NAVY}, "the share of the Kernel taken by the MinSet."),
      ({"t": "Dictionary type: ", "bold": True, "color": NAVY}, f"WordNet, which is not a Wiktionary, has {kr(WN, 'freq'):.0f}%; the DEX converted to the Wiktionary format keeps {min(kr(XD, 'freq'), kr(XD, 'all')):.0f}–{max(kr(XD, 'freq'), kr(XD, 'all')):.0f}%."),
      ({"t": "Distance: ", "bold": True, "color": NAVY}, f"the DEX lies {DEX_Z:.1f} standard deviations above the mean of the 13 other dictionaries."),
      ({"t": "Romanian Wiktionary: ", "bold": True, "color": NAVY}, "close to the DEX, but 70% of its definitions are copied from it.")],
     size=21, gap=0.55)
notes(s, "Rezervă: comparabilitatea.")

s = slide(kicker="Backup", title="Can we trust the language model?", backup=True)
text(s, Inches(0.75), Inches(1.95), Inches(11.8), Inches(4.8),
     [({"t": "A narrow task: ", "bold": True, "color": NAVY}, "for each ambiguous form, choose the lemma among numbered candidates."),
      ({"t": "Checked: ", "bold": True, "color": NAVY}, f"a stronger model agrees on {100 * V['opus_random_content']:.0f}% of content-word choices ({V['opus_random_n_defs']} random definitions); most disagreements are defensible."),
      ({"t": "Not needed for the conclusions: ", "bold": True, "color": NAVY}, "two rules without any model give the same picture (Kernel 29–36%, MinSet 7.5–10.9%)."),
      ({"t": "Cost: ", "bold": True, "color": NAVY}, f"about {V['cost_usd']:.0f} USD for the whole dictionary.")],
     size=21, gap=0.55)
notes(s, "Rezervă: modelul de limbaj.")

s = slide(kicker="Backup", title="How sure are we?", backup=True)
for i, (tag, t, col) in enumerate([("Strong", "The DEX is far more circular than 11 other languages; reciprocal definitions explain it.", BLUE),
                                   ("Strong", "Swadesh and Graur words are concentrated in the Kernel (p < 10⁻²⁰⁰).", BLUE),
                                   ("Good", f"MinSet between {LB:,} and {UB:,} words: proven bounds, not an exact value.", RGBColor(0x1b, 0xaf, 0x7a)),
                                   ("Open", "Is it the DEX, or Romanian lexicography? Older dictionaries will tell.", ORANGE)]):
    y = Inches(2.0 + i * 1.1)
    b = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), y, Inches(1.9), Inches(0.75), col); label(b, tag, size=20, color=WHITE, bold=True)
    text(s, Inches(2.95), y + Inches(0.1), Inches(9.8), Inches(0.9), t, size=21)
notes(s, "Rezervă: cât de siguri suntem.")

prs.save("HiddenCore_ConsILR2026_talk.pptx")
print("scris HiddenCore_ConsILR2026_talk.pptx,", len(prs.slides), "slide-uri")
