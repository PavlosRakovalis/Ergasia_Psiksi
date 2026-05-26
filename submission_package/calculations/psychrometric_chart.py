#!/usr/bin/env python3
"""
=================================================================
Ερώτημα γ — Ψυχρομετρικός Χάρτης Διεργασιών
=================================================================
Δημιουργεί ψυχρομετρικά διαγράμματα για τις Περιπτώσεις (i) και (ii):

  O  →  Εξωτερικός αέρας
  R  →  Χώρος (Return air)
  M  →  Μίγμα (Mixing point)  =  R + O ως προς μάζα
  S  →  Προσαγωγή (Supply air)
  ADP → Apparatus Dew Point (σημείο στην καμπύλη κορεσμού)
=================================================================
"""
import psychrolib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

psychrolib.SetUnitSystem(psychrolib.SI)
P_ATM = 101325  # Pa
PACKAGE_DIR = Path(__file__).resolve().parent.parent

CASES = {
    'i': {
        'title': 'Ψυχρομετρικός Χάρτης — Περίπτωση (i): Χαμηλή παροχή νωπού (λόγος 1:15)',
        'O':   {'T': 35.7, 'W': 0.0145},
        'R':   {'T': 26.0, 'W': 0.0105},
        'M':   {'T': 26.61, 'W': 0.01075},
        'S':   {'T': 17.01, 'W': 0.01020},
        'ADP': {'T': 14.10, 'W': 0.01003},
        'Q_coil_total': 6.54,
        'Q_coil_sens': 5.62,
        'Q_coil_lat': 0.80,
        'BF': 0.232,
        'm_total': 0.582,
        'V_fresh': 108.75,
    },
    'ii': {
        'title': 'Ψυχρομετρικός Χάρτης — Περίπτωση (ii): Υψηλή παροχή νωπού 6× (λόγος 1:2)',
        'O':   {'T': 35.7, 'W': 0.0145},
        'R':   {'T': 26.0, 'W': 0.0105},
        'M':   {'T': 29.23, 'W': 0.01183},
        'S':   {'T': 18.00, 'W': 0.01023},
        'ADP': {'T': 13.39, 'W': 0.00958},
        'Q_coil_total': 10.21,
        'Q_coil_sens': 7.40,
        'Q_coil_lat': 2.62,
        'BF': 0.291,
        'm_total': 0.655,
        'V_fresh': 652.50,
    },
}


def humratio_g_kg(T):
    return psychrolib.GetSatHumRatio(float(T), P_ATM) * 1000


def curve_angle(ax, x_data, y_data, idx):
    i0 = max(0, idx - 2)
    i1 = min(len(x_data) - 1, idx + 2)
    p0 = ax.transData.transform((x_data[i0], y_data[i0]))
    p1 = ax.transData.transform((x_data[i1], y_data[i1]))
    return np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0]))


def label_curve(ax, x_data, y_data, text, frac=0.75, color="#555", fontsize=9):
    if len(x_data) < 5:
        return
    idx = int(np.clip(frac, 0.05, 0.95) * (len(x_data) - 1))
    angle = curve_angle(ax, x_data, y_data, idx)
    ax.text(
        x_data[idx], y_data[idx], text,
        color=color, fontsize=fontsize, rotation=angle,
        rotation_mode="anchor", ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.70),
        zorder=12,
    )


def plot_psychrometric_grid(ax, x_min, x_max, y_max, full_range):
    temps = np.linspace(x_min, x_max, 900)
    w_sat = np.array([humratio_g_kg(t) for t in temps])

    # Βασικό ορθογώνιο πλέγμα: Tdb και W.
    for w in np.arange(0, y_max + 0.1, 2):
        if w == 0:
            continue
        if w <= w_sat[0]:
            x0 = x_min
        elif w <= w_sat.max():
            x0 = np.interp(w, w_sat, temps)
        else:
            continue
        ax.hlines(w, x0, x_max, color="#d2d2d2", linewidth=0.55, zorder=0)

    for t in np.arange(np.ceil(x_min / 5) * 5, x_max + 0.1, 5):
        ax.vlines(
            t, 0, min(humratio_g_kg(t), y_max),
            color="#d2d2d2", linewidth=0.55, zorder=0,
        )

    # Καμπύλες σχετικής υγρασίας.
    for rh in range(10, 100, 10):
        w = np.array([
            psychrolib.GetHumRatioFromRelHum(float(t), rh / 100, P_ATM) * 1000
            for t in temps
        ])
        mask = (w >= 0) & (w <= y_max) & (w <= w_sat)
        ax.plot(temps[mask], w[mask], color="#8bbcff", linewidth=0.75,
                linestyle=":", zorder=1)
        if rh in ([20, 40, 60, 80] if not full_range else [10, 20, 30, 40, 50, 60, 70, 80, 90]):
            label_curve(ax, temps[mask], w[mask], f"RH {rh}%",
                        frac=0.76, color="#6f98d8", fontsize=8)

    # Καμπύλη κορεσμού.
    mask_sat = w_sat <= y_max
    ax.plot(temps[mask_sat], w_sat[mask_sat], color="#001f8f",
            linewidth=2.4, zorder=4, label="Καμπύλη κορεσμού 100% RH")

    # Γραμμές σταθερής ενθαλπίας h [kJ/kg_da].
    h_values = range(10, 125, 10) if full_range else range(30, 90, 10)
    for h in h_values:
        w = 1000 * (h - 1.006 * temps) / (2501 + 1.86 * temps)
        mask = (w >= 0) & (w <= y_max) & (w <= w_sat)
        ax.plot(temps[mask], w[mask], color="#777777", linewidth=0.7,
                linestyle="-", alpha=0.65, zorder=2)
        if full_range and h % 20 == 0:
            label_curve(ax, temps[mask], w[mask], f"{h} kJ/kg_da",
                        frac=0.90, color="#777777", fontsize=8)

    if full_range:
        # Γραμμές σταθερής θερμοκρασίας υγρού βολβού.
        for twb in range(0, 35, 5):
            t_line = np.linspace(max(twb, x_min), x_max, 500)
            w_line = []
            for t in t_line:
                try:
                    w_line.append(psychrolib.GetHumRatioFromTWetBulb(float(t), twb, P_ATM) * 1000)
                except ValueError:
                    w_line.append(np.nan)
            w_line = np.array(w_line)
            w_sat_line = np.array([humratio_g_kg(t) for t in t_line])
            mask = np.isfinite(w_line) & (w_line >= 0) & (w_line <= y_max) & (w_line <= w_sat_line)
            ax.plot(t_line[mask], w_line[mask], color="#1f1f1f",
                    linewidth=0.8, alpha=0.62, zorder=3)
            label_curve(ax, t_line[mask], w_line[mask], f"{twb} °C",
                        frac=0.16, color="#555555", fontsize=8)

        # Γραμμές σταθερού ειδικού όγκου v [m3/kg_da].
        r_da = 287.042
        for v in np.arange(0.78, 0.95, 0.02):
            w = 1000 * ((v * P_ATM / (r_da * (temps + 273.15))) - 1) / 1.607858
            mask = (w >= 0) & (w <= y_max) & (w <= w_sat)
            ax.plot(temps[mask], w[mask], color="#666666", linewidth=0.65,
                    linestyle="--", alpha=0.55, zorder=2)
            label_curve(ax, temps[mask], w[mask], f"{v:.2f} m³/kg_da",
                        frac=0.14, color="#777777", fontsize=8)


def plot_process(ax, case, full_range):
    pts = {k: (case[k]["T"], case[k]["W"] * 1000) for k in ("O", "R", "M", "S", "ADP")}

    colors = {
        "O": "#d62728",
        "R": "#2ca02c",
        "M": "#9467bd",
        "S": "#1f77b4",
        "ADP": "#17becf",
    }
    markers = {"O": "o", "R": "s", "M": "D", "S": "^", "ADP": "X"}

    ax.plot([pts["R"][0], pts["O"][0]], [pts["R"][1], pts["O"][1]],
            color="#ff7f0e", linewidth=2.2, linestyle="--", zorder=20,
            label="Γραμμή ανάμιξης R — O")
    ax.plot([pts["M"][0], pts["S"][0], pts["ADP"][0]],
            [pts["M"][1], pts["S"][1], pts["ADP"][1]],
            color="#1f77b4", linewidth=2.7, zorder=21,
            label="Ψυκτικό στοιχείο M → S → ADP")
    ax.plot([pts["S"][0], pts["R"][0]], [pts["S"][1], pts["R"][1]],
            color="#2ca02c", linewidth=2.7, zorder=22,
            label="Διεργασία χώρου S → R")

    label_offsets = {
        "O": (10, 8),
        "R": (10, 10),
        "M": (-22, 12),
        "S": (-30, -3),
        "ADP": (-15, -18),
    }
    for name, (t, w) in pts.items():
        ax.scatter(t, w, s=160 if name == "ADP" else 130,
                   marker=markers[name], color=colors[name],
                   edgecolor="black", linewidth=1.3, zorder=30,
                   label=f"{name} ({t:.1f} °C, {w:.1f} g/kg)")
        dx, dy = label_offsets[name]
        ax.annotate(
            name, xy=(t, w), xytext=(dx, dy), textcoords="offset points",
            fontsize=14, fontweight="bold", color=colors[name], zorder=31,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                      edgecolor=colors[name], linewidth=1.1, alpha=0.94),
        )


def add_info_box(ax, case, full_range):
    info_text = (
        f"ΠΑΡΑΜΕΤΡΟΙ ΣΥΣΤΗΜΑΤΟΣ\n"
        f"────────────────────\n"
        f"V_νωπού      = {case['V_fresh']:.1f} m³/h\n"
        f"ṁ_total       = {case['m_total']:.3f} kg/s\n"
        f"BF              = {case['BF']:.3f}\n"
        f"────────────────────\n"
        f"Q_coil,αισθ  = {case['Q_coil_sens']:.2f} kW\n"
        f"Q_coil,λανθ  = {case['Q_coil_lat']:.2f} kW\n"
        f"Q_coil,total = {case['Q_coil_total']:.2f} kW"
    )
    x, y = (0.02, 0.56) if full_range else (0.985, 0.98)
    ha = "left" if full_range else "right"
    ax.text(
        x, y, info_text, transform=ax.transAxes,
        fontsize=10 if full_range else 10.5,
        verticalalignment="top", horizontalalignment=ha,
        family="DejaVu Sans Mono",
        bbox=dict(boxstyle="round,pad=0.65", facecolor="#fff8e1",
                  edgecolor="#888888", linewidth=1.1, alpha=0.96),
        zorder=40,
    )


def make_chart(case_key, output_path, full_range=False):
    case = CASES[case_key]
    x_min, x_max = (0, 55) if full_range else (5, 40)
    y_max = 30 if full_range else 22
    fig_size = (16.5, 10.5) if full_range else (14, 9)

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
        "axes.labelweight": "bold",
    })

    fig, ax = plt.subplots(figsize=fig_size, dpi=180)
    fig.subplots_adjust(left=0.07, right=0.90, top=0.91, bottom=0.13)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("Θερμοκρασία ξηρού βολβού, Tdb  [°C]", fontsize=15, labelpad=14)
    ax.set_ylabel("Λόγος υγρασίας, W  [g / kg ξηρού αέρα]", fontsize=15, labelpad=18)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.tick_params(axis="both", which="major", labelsize=11, width=1.1, length=5)
    ax.set_xticks(np.arange(x_min, x_max + 0.1, 5))
    ax.set_yticks(np.arange(0, y_max + 0.1, 2))
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_linewidth(1.6)
        spine.set_color("#222222")

    title_prefix = "Ψυχρομετρικός Χάρτης (πλήρης) — " if full_range else ""
    ax.set_title(title_prefix + case["title"].replace("Ψυχρομετρικός Χάρτης — ", ""),
                 fontsize=18, pad=14)

    plot_psychrometric_grid(ax, x_min, x_max, y_max, full_range)
    plot_process(ax, case, full_range)
    add_info_box(ax, case, full_range)

    legend = ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.02, 0.99),
        fontsize=9.5 if full_range else 10.5,
        frameon=True, facecolor="white", edgecolor="#888888",
        framealpha=0.92, labelspacing=0.45, borderpad=0.7,
    )
    legend.set_zorder(50)

    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.35)
    plt.close(fig)
    print(f"  ✓ Αποθηκεύτηκε: {output_path}")


if __name__ == "__main__":
    print("Δημιουργία ψυχρομετρικών χαρτών για το Ερώτημα γ...")

    # Εστιασμένοι χάρτες (όπως πριν)
    make_chart('i',  PACKAGE_DIR / 'psychrometric_case_i.png',
               full_range=False)
    make_chart('ii', PACKAGE_DIR / 'psychrometric_case_ii.png',
               full_range=False)

    # Χάρτες πλήρους εμβέλειας (0–55°C, 0–30 g/kg)
    make_chart('i',  PACKAGE_DIR / 'psychrometric_case_i_full.png',
               full_range=True)
    make_chart('ii', PACKAGE_DIR / 'psychrometric_case_ii_full.png',
               full_range=True)

    print("Ολοκληρώθηκε.")
