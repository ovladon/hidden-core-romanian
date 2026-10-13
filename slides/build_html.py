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
t = open("template.html", encoding="utf8").read()
for k, v in V.items():
    t = t.replace(k, v)
left = [k for k in V if k in t]
open("HiddenCore_ConsILR2026.html", "w", encoding="utf8").write(t)
print(f"scris HiddenCore_ConsILR2026.html ({len(t)/1e6:.2f} MB); substituite ramase: {left}")
