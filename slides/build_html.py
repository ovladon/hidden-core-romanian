#!/usr/bin/env python3
"""Prezentarea HTML intr-un singur fisier (fara dependente externe): sabloane + results.json + date + sigla."""
import base64, json

R = json.load(open("../results/results.json", encoding="utf8"))
WD = open("html_data.json", encoding="utf8").read()
logo = base64.b64encode(open("../../../ConsILR2025/logo_consilr.png", "rb").read()).decode()
N = R["data"]["headwords"]; ai = R["regimes"]["ai"]
lb = ai.get("minset_lb_ilp", ai["minset_lb"]); ub = ai["minset_ub"]
G, S = R["graur"], R["swadesh"]
f0 = lambda x: f"{100 * x:.0f}%"
V = {"__LOGO__": "data:image/png;base64," + logo,
     "__RESULTS__": json.dumps(R, ensure_ascii=False).replace("</", "<\\/"),
     "__WDATA__": WD.replace("</", "<\\/"),
     "__DEFS__": str(R["data"]["definitions"]), "__HW__": str(N), "__AMB__": f0(ai["ambig_rate"]),
     "__AGREE__": f0(R["validation"]["opus_random_content"]), "__COST__": f"{R['validation']['cost_usd']:.0f}",
     "__KPCT__": f"{100 * ai['kernel'] / N:.0f}%", "__K__": f"{ai['kernel']:,}",
     "__MPCT__": f"≈{100 * ub / N:.0f}%", "__MLB__": f"{lb:,}", "__MUB__": f"{ub:,}",
     "__PAIRS__": f"{ai['mutual_pairs']:,}",
     "__SWK__": f0(S["layers"]["Kernel"]["rate"]), "__GK__": f0(G["all"]["Kernel"]["rate"]),
     "__GCM__": f0(G["core"]["MinSet"]["rate"]), "__GMM__": f0(G["middle"]["MinSet"]["rate"]),
     "__GXM__": f0(G["maximal"]["MinSet"]["rate"])}
import sys as _s; _s.path.insert(0, "..")
from calib import calib, EN, RO
CB = calib(R); V.update({"__RMEN__": EN[CB["rm"]], "__RMRO__": RO[CB["rm"]]})
XS = json.load(open("../crossling/summary.json", encoding="utf8"))
XO = [r for r in XS if r["language"] != "Romanian"]; XD = next(r for r in XS if r["code"] == "dex")
kr = lambda r, g: 100 * (r.get(g, r["freq"])["minset_lb_n"] + r.get(g, r["freq"])["minset_ub_n"]) / 2 / r.get(g, r["freq"])["kernel_n"]
xr = [kr(r, g) for r in XO for g in ("freq", "all")]
V.update({"__XNL__": str(len({r["language"] for r in XO})), "__XDR__": f"{min(kr(XD, 'freq'), kr(XD, 'all')):.0f}%",
          "__XOR__": f"{min(xr):.0f}–{max(xr):.0f}%",
          "__XFIG__": "data:image/png;base64," + base64.b64encode(open("../figures/fig5_crossling.png", "rb").read()).decode()})
t = open("template.html", encoding="utf8").read()
for k, v in V.items():
    t = t.replace(k, v)
left = [k for k in V if k in t]
open("HiddenCore_ConsILR2026.html", "w", encoding="utf8").write(t)
print(f"scris HiddenCore_ConsILR2026.html ({len(t)/1e6:.2f} MB); substituite ramase: {left}")
