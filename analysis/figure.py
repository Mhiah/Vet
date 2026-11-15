"""Figure 1: the confidence label each method gave, for every question."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for f in fm.findSystemFonts():
    if "Inter" in os.path.basename(f):
        fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Inter"
S = json.load(open(os.path.join(HERE, "summary.json")))
SHORT = {"W1": "15-minute grocery delivery (US)", "W2": "Mobile before desktop (Nigeria)", "W3": "Buy now, pay later at checkout (US)",
         "C1": "Four-day work week", "C2": "Seat pricing to usage pricing", "C3": "European fintech into Nigeria",
         "T1": "Cultivated-meat pet food (Kenya)", "T2": "AI bookkeeping, traders (Sierra Leone)", "T3": "Esports smart water bottle (SE Asia)"}
GROUPS = [("Well-evidenced", ["W1", "W2", "W3"]), ("Contested", ["C1", "C2", "C3"]), ("Thin evidence", ["T1", "T2", "T3"])]
COLS = [("plain", "Plain\nchatbot"), ("one_shot", "One-shot\nwith evidence"), ("first_answer", "Stress-tested:\nfirst answer"), ("crux", "Stress-tested:\nfinal answer")]
FILL = {"medium": "#86b6ef", "high": "#1c5cab", "low": "#e9e8e4"}
INK = {"medium": "#0b0b0b", "high": "#ffffff", "low": "#0b0b0b"}
rows = {r["id"]: r for r in S["confidence"]}

fig, ax = plt.subplots(figsize=(7.6, 4.9), dpi=200)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
x0, cw, ch, gap = 3.55, 1.5, 0.52, 0.34
y = 0.0
for gname, ids in GROUPS:
    ax.text(0, y - 0.02, gname.upper(), fontsize=7.5, color="#52514e", va="center", fontweight="bold")
    y += 0.44
    for i in ids:
        ax.text(0, y, SHORT[i], fontsize=9, color="#0b0b0b", va="center")
        for k, (col, _) in enumerate(COLS):
            v = rows[i][col]
            ax.add_patch(FancyBboxPatch((x0 + k * cw + 0.03, y - ch / 2 + 0.03), cw - 0.06, ch - 0.06,
                                        boxstyle="round,pad=0,rounding_size=0.06", fc=FILL[v], ec="none"))
            ax.text(x0 + k * cw + cw / 2, y, v.capitalize(), ha="center", va="center", fontsize=9, color=INK[v],
                    fontweight="bold" if v == "high" else "normal")
        y += ch
    y += gap
for k, (_, label) in enumerate(COLS):
    ax.text(x0 + k * cw + cw / 2, -0.62, label, ha="center", va="center", fontsize=8.5, color="#0b0b0b", linespacing=1.25)
ax.plot([x0 + 3 * cw - 0.02] * 2, [-0.25, y - gap + 0.05], color="#c3c2b7", lw=0.8, ls=(0, (2, 2)))
ax.text(0, y + 0.02, "Each cell is the confidence label the method gave. “Low” was available to every method and was never used (0 of 36).",
        fontsize=7.8, color="#52514e", va="center")
ax.set_xlim(-0.05, x0 + 4 * cw + 0.05); ax.set_ylim(y + 0.3, -1.0); ax.axis("off")
fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
fig.savefig(os.path.join(ROOT, "report", "figure1.png"), facecolor=fig.get_facecolor())
fig.savefig(os.path.join(ROOT, "report", "figure1.pdf"), facecolor=fig.get_facecolor())
print("ok")
