"""#027 analysis: speed + quality for DiffusionGemma vs Gemma 4 26B-A4B (both Q4_K_M, L4).
useful tokens = tokens in the model's reply (thought + answer), counted with the Gemma 4 tokenizer;
DiffusionGemma's own 'throughput' counts whole 256-token canvases (incl. padding after the reply ends), so we report both."""
import json, re, os, sys, glob, statistics as st
from tokenizers import Tokenizer
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, "..", "results")
tok = Tokenizer.from_file(f"{R}/tok/tokenizer.json")
def ntok(s): return len(tok.encode(s, add_special_tokens=False).ids)

def reply_dg(txt):
    body = re.split(r"\ntotal time:", txt)[0]
    i = body.find("<|channel>"); return body[i:] if i >= 0 else body
def reply_ar(txt):
    i = txt.find("<|channel>"); body = txt[i:] if i >= 0 else txt.split("\nmodel\n", 1)[-1]
    return body.replace("[end of text]", "").strip()
def answer_part(r):
    return r.split("<channel|>", 1)[1] if "<channel|>" in r else ""

def grade(p, r):
    a = answer_part(r) or r
    if p["kind"] == "gsm8k":
        m = re.findall(r"Answer:\s*\$?\s*([-\d,\.]+)", a)
        if not m: return False, None
        v = m[-1].replace(",", "").rstrip(".")
        try: return abs(float(v) - float(p["gold"])) < 1e-6, v
        except: return False, v
    if p["kind"] == "code":
        m = re.findall(r"```python\n(.*?)```", a, re.S)
        if not m: return False, "no code block in answer"
        ns = {}
        try:
            exec(m[-1], ns); exec(p["test"], ns); return True, "tests pass"
        except Exception as e: return False, f"{type(e).__name__}: {e}"[:80]
    return None, f"{len(a.split())} words"

def run(benchdir, prompts_file, tag, cap):
    P = json.load(open(prompts_file)); rows = []
    for p in P:
        for f in sorted(glob.glob(f"{R}/{benchdir}/dg_{p['id']}_r*.out")):
            rep = f.split("_r")[-1].split(".")[0]
            dg = open(f).read(); ar = open(f.replace("/dg_", "/ar_")).read(); arerr = open(f.replace("/dg_", "/ar_").replace(".out", ".err")).read()
            m = re.search(r"total time: ([\d\.]+)ms, time per step: ([\d\.]+)ms \((\d+) steps over (\d+) blocks", dg)
            th = re.search(r"throughput: ([\d\.]+) tok/s \((\d+) tok", dg)
            e = re.search(r"eval time =\s+([\d\.]+) ms /\s+(\d+) runs", arerr)
            pe = re.search(r"prompt eval time =\s+([\d\.]+) ms", arerr)
            rd, ra = reply_dg(dg), reply_ar(ar)
            gd, gdv = grade(p, rd); ga, gav = grade(p, ra)
            row = {"run": tag, "id": p["id"], "kind": p["kind"], "rep": rep,
                   "dg_total_ms": float(m.group(1)), "dg_steps": int(m.group(3)), "dg_blocks": int(m.group(4)),
                   "dg_reported_tok_s": float(th.group(1)), "dg_canvas_tok": int(th.group(2)),
                   "dg_reply_tok": ntok(rd), "dg_useful_tok_s": ntok(rd) / (float(m.group(1)) / 1000),
                   "dg_tokens_per_step": ntok(rd) / int(m.group(3)),
                   "dg_finished": not (int(th.group(2)) >= cap and ntok(rd) >= 0.95 * cap),
                   "ar_eval_ms": float(e.group(1)), "ar_gen_tok": int(e.group(2)), "ar_prompt_ms": float(pe.group(1)),
                   "ar_tok_s": int(e.group(2)) / (float(e.group(1)) / 1000), "ar_reply_tok": ntok(ra),
                   "ar_finished": "[end of text]" in ar,
                   "dg_correct": gd, "dg_detail": gdv, "ar_correct": ga, "ar_detail": gav}
            rows.append(row)
    return rows

rows = []
if os.path.isdir(f"{R}/bench"): rows += run("bench", f"{H}/prompts.json", "run1_n768", 768)
if os.path.isdir(f"{R}/bench2") and glob.glob(f"{R}/bench2/ar_*.err"): rows += run("bench2", f"{H}/prompts_run2.json", "run2_n2048", 2048)
json.dump(rows, open(f"{R}/per_prompt.json", "w"), indent=1)
import csv
with open(f"{R}/per_prompt.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
summ = {}
for tag in sorted(set(r["run"] for r in rows)):
    rr = [r for r in rows if r["run"] == tag]
    s = {"n": len(rr)}
    for k in ["dg_useful_tok_s", "dg_reported_tok_s", "ar_tok_s", "dg_tokens_per_step", "dg_reply_tok", "ar_reply_tok", "dg_total_ms", "ar_eval_ms"]:
        s[k + "_median"] = round(st.median(r[k] for r in rr), 2); s[k + "_mean"] = round(st.mean(r[k] for r in rr), 2)
    s["dg_total_s_sum"] = round(sum(r["dg_total_ms"] for r in rr) / 1000, 1)
    s["ar_total_s_sum"] = round(sum((r["ar_eval_ms"] + r["ar_prompt_ms"]) for r in rr) / 1000, 1)
    for kind in ["gsm8k", "code"]:
        kk = [r for r in rr if r["kind"] == kind]
        if kk:
            s[f"{kind}_dg_correct"] = f"{sum(bool(r['dg_correct']) for r in kk)}/{len(kk)}"
            s[f"{kind}_ar_correct"] = f"{sum(bool(r['ar_correct']) for r in kk)}/{len(kk)}"
    s["dg_unfinished"] = sum(not r["dg_finished"] for r in rr); s["ar_unfinished"] = sum(not r["ar_finished"] for r in rr)
    summ[tag] = s
json.dump(summ, open(f"{R}/summary.json", "w"), indent=1); print(json.dumps(summ, indent=1))

# chart: main run (run2 if present)
tag = "run2_n2048" if "run2_n2048" in summ else "run1_n768"
rr = [r for r in rows if r["run"] == tag]
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
a.scatter([r["ar_reply_tok"] for r in rr], [r["ar_tok_s"] for r in rr], label="Gemma 4 26B-A4B (autoregressive)", color="#888")
a.scatter([r["dg_reply_tok"] for r in rr], [r["dg_useful_tok_s"] for r in rr], label="DiffusionGemma 26B-A4B (useful tok/s)", color="#2a6")
a.scatter([r["dg_reply_tok"] for r in rr], [r["dg_reported_tok_s"] for r in rr], label="DiffusionGemma, tool-reported (whole canvas)", color="#2a6", marker="x", alpha=.5)
a.set_xlabel("reply length (tokens)"); a.set_ylabel("decode tokens / second"); a.set_title(f"Speed on 1x L4, both Q4_K_M ({tag})" + ("\nDG rerun used --n-cpu-moe 2 (2 layers of experts on CPU)" if tag == "run2_n2048" else ""), fontsize=9); a.legend(fontsize=7)
a.set_ylim(0, max(max(r["dg_reported_tok_s"] for r in rr), max(r["ar_tok_s"] for r in rr)) * 1.25)
cats = []; dv = []; av = []
for kind in ["gsm8k", "code"]:
    kk = [r for r in rr if r["kind"] == kind]
    if kk:
        cats.append(f"{kind} (n={len(kk)})"); dv.append(100 * sum(bool(r["dg_correct"]) for r in kk) / len(kk)); av.append(100 * sum(bool(r["ar_correct"]) for r in kk) / len(kk))
x = range(len(cats)); w = .38
b.bar([i - w/2 for i in x], av, w, color="#888", label="Gemma 4 26B-A4B"); b.bar([i + w/2 for i in x], dv, w, color="#2a6", label="DiffusionGemma")
for i in x: b.text(i - w/2, av[i] + 1.5, f"{av[i]:.0f}%", ha="center", fontsize=8); b.text(i + w/2, dv[i] + 1.5, f"{dv[i]:.0f}%", ha="center", fontsize=8)
b.set_xticks(list(x)); b.set_xticklabels(cats); b.set_ylim(0, 115); b.set_ylabel("% correct"); b.set_title("Quality on the same prompts", fontsize=10); b.legend(fontsize=7, loc="lower right")
plt.tight_layout(); plt.savefig(os.path.join(R, "..", "chart.png"), dpi=130)
