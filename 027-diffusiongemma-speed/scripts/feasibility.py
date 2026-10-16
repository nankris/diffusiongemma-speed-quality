"""#027 feasibility check (no Colab compute used). Pulls DiffusionGemma checkpoint sizes from the HF API
and compares them with a Colab T4 (15 GB VRAM, ~12.7 GB system RAM on the standard VM)."""
import json, urllib.request
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
api = json.load(urllib.request.urlopen("https://huggingface.co/api/models/google/diffusiongemma-26B-A4B-it?blobs=true"))
bf16_gb = sum(s.get("size", 0) for s in api["siblings"]) / 1e9
params = api["safetensors"]["total"]
# GGUF sizes as listed on https://huggingface.co/unsloth/diffusiongemma-26B-A4B-it-GGUF (file sizes shown by HF, GB)
gguf = {"Q4_K_M": 16.8, "Q5_K_M": 19.1, "Q6_K": 22.7, "Q8_0": 26.9}
rows = {"BF16 (google)": round(bf16_gb, 1), **{f"GGUF {k}": v for k, v in gguf.items()}}
res = {"model": "google/diffusiongemma-26B-A4B-it", "total_params": params, "weights_gb": rows,
       "t4_vram_gb": 15.0, "t4_usable_vram_gb_reported_by_torch": 14.56,
       "verdict": "does not fit on T4; smallest published quant (Q4_K_M, 16.8 GB) exceeds 15 GB VRAM before KV cache/activations"}
json.dump(res, open("results/feasibility.json", "w"), indent=1); print(json.dumps(res, indent=1))
fig, ax = plt.subplots(figsize=(7, 3.6))
names, vals = list(rows), list(rows.values())
ax.barh(names, vals, color=["#888"] + ["#4a7"] * 4)
ax.axvline(15, color="red", ls="--"); ax.text(38, 2.0, "red line = T4 VRAM 15 GB", color="red", fontsize=9)
for i, v in enumerate(vals): ax.text(v + 0.3, i, f"{v:.1f} GB", va="center", fontsize=9)
ax.set_xlabel("weights only (GB)"); ax.set_title("#027 DiffusionGemma 26B-A4B weight size vs Colab T4")
ax.set_xlim(0, 60); ax.set_ylim(-0.6, 4.7); plt.tight_layout(); plt.savefig("chart.png", dpi=130)
