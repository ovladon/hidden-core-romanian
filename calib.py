#!/usr/bin/env python3
"""Cifrele de calibrare (DEX fata de WordNet procesat cu aceeasi procedura), comune lucrarii, abstractului si prezentarilor.

Comparatia se face pe regimurile fara model (cel mai frecvent candidat, toti candidatii), singurele aplicabile
ambelor dictionare; raportul MinSet foloseste mijlocul intervalului [limita inferioara, limita superioara].
"""
EN = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
RO = {1: "o dată", 2: "două", 3: "trei", 4: "patru", 5: "cinci", 6: "șase"}


def calib(R):
    N, C, reg = R["data"]["headwords"], R["calibration"], R["regimes"]
    wf, wa = C["wordnet_freq"], C["wordnet_all"]
    p = lambda d, k: 100 * d[k] / d["headwords"]
    lb = lambda r: r.get("minset_lb_ilp", r["minset_lb"])
    mid_dex = lambda r: 100 * (lb(r) + r["minset_ub"]) / 2 / N
    mid_wn = lambda w: (p(w, "minset_lb") + p(w, "minset_ub")) / 2
    rk = [100 * reg["freq"]["kernel"] / N / p(wf, "kernel"), 100 * reg["all"]["kernel"] / N / p(wa, "kernel")]
    rm = [mid_dex(reg["freq"]) / mid_wn(wf), mid_dex(reg["all"]) / mid_wn(wa)]
    VL = C["vincent_lamarre_wordnet"]
    co = C["dex_content_only"]["llm"]
    return {"wn_k": (p(wf, "kernel"), p(wa, "kernel")), "wn_m": (p(wf, "minset_lb"), p(wa, "minset_ub")),
            "wn_headwords": wf["headwords"],
            "rk": round(sum(rk) / 2), "rm": round(sum(rm) / 2), "rk_range": (min(rk), max(rk)), "rm_range": (min(rm), max(rm)),
            "vl_k": 100 * VL["kernel"] / VL["headwords"], "vl_m": 100 * VL["minset"] / VL["headwords"],
            "co_k": 100 * co["kernel"] / co["content_headwords"],
            "co_m": (100 * co["minset_lb"] / co["content_headwords"], 100 * co["minset_ub"] / co["content_headwords"]),
            "fw": C["dex_function_words"]}


def times_en(n):
    return "twice" if n == 2 else f"{EN[n]} times"
