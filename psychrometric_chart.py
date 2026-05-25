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
from psychrochart import PsychroChart

psychrolib.SetUnitSystem(psychrolib.SI)
P_ATM = 101325  # Pa

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


def humratio_to_rh_pct(T, W):
    return psychrolib.GetRelHumFromHumRatio(T, W, P_ATM) * 100


def make_chart(case_key, output_path, full_range=False):
    case = CASES[case_key]

    if full_range:
        title_prefix = "Ψυχρομετρικός Χάρτης (πλήρης) — "
        # Πλήρης εμβέλεια ψυχρομετρικού χάρτη
        temp_range = [-5, 55]
        humid_range = [0, 35]
        temp_step = 2.0
        humid_step = 2
        rh_labels = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    else:
        title_prefix = ""
        # Εστιασμένη εμβέλεια στην περιοχή της διεργασίας
        temp_range = [5, 40]
        humid_range = [0, 22]
        temp_step = 1.0
        humid_step = 2
        rh_labels = [20, 40, 50, 60, 80]

    fig_size = [16, 10] if full_range else [14, 9]
    chart_style = {
        "figure": {
            "figsize": fig_size,
            "base_fontsize": 13,
            "title": title_prefix + case['title'].replace("Ψυχρομετρικός Χάρτης — ", ""),
            "x_label": "Θερμοκρασία ξηρού βολβού  T  [°C]",
            "y_label": "Λόγος υγρασίας  W  [g / kg ξηρού αέρα]",
            "partial_axis": False,
            "x_axis_labels": {"color": [0.0, 0.0, 0.0], "fontsize": 12},
            "y_axis_labels": {"color": [0.0, 0.0, 0.0], "fontsize": 12},
        },
        "limits": {
            "range_temp_c": temp_range,
            "range_humidity_g_kg": humid_range,
            "altitude_m": 0,
            "step_temp": temp_step,
        },
        "saturation": {"color": [0.0, 0.0, 0.55], "linewidth": 2.5},
        "constant_rh": {"color": [0.3, 0.5, 0.85, 0.6],
                        "linewidth": 0.8, "linestyle": ":"},
        "constant_dry_temp": {"color": [0.6, 0.6, 0.6, 0.4],
                              "linewidth": 0.5, "linestyle": "-"},
        "constant_humidity": {"color": [0.6, 0.6, 0.6, 0.4],
                              "linewidth": 0.5, "linestyle": "-"},
        "constant_h": {"color": [0.85, 0.55, 0.10, 0.55],
                       "linewidth": 0.6, "linestyle": "-."},
        "chart_params": {
            "with_constant_rh": True,
            "constant_rh_curves": [10, 20, 30, 40, 50, 60, 70, 80, 90],
            "constant_rh_labels": rh_labels,
            "constant_rh_labels_loc": 0.85,
            "with_constant_v": False,
            "with_constant_h": True,
            "constant_h_step": 5,
            "constant_h_labels_values":
                [20, 30, 40, 50, 60, 70, 80, 90, 100] if full_range
                else [30, 40, 50, 60, 70, 80],
            "with_constant_wet_temp": False,
            "with_zones": False,
            "with_constant_dry_temp": True,
            "constant_temp_step": 5,
            "with_constant_humidity": True,
            "constant_humid_step": humid_step,
        },
    }

    chart = PsychroChart.create(chart_style)

    pts = {k: case[k] for k in ('O', 'R', 'M', 'S', 'ADP')}

    colors = {
        'O':   '#d62728',   # red
        'R':   '#2ca02c',   # green
        'M':   '#9467bd',   # purple
        'S':   '#1f77b4',   # blue
        'ADP': '#17becf',   # cyan
    }
    markers = {'O': 'o', 'R': 's', 'M': 'D', 'S': '^', 'ADP': 'X'}
    labels = {
        'O':   'O — Εξωτερικός αέρας (35.7°C, 14.5 g/kg)',
        'R':   'R — Χώρος (26°C, 10.5 g/kg, 50% RH)',
        'M':   f"M — Σημείο ανάμιξης ({case['M']['T']:.1f}°C)",
        'S':   f"S — Αέρας προσαγωγής ({case['S']['T']:.1f}°C)",
        'ADP': f"ADP — Apparatus Dew Point ({case['ADP']['T']:.1f}°C)",
    }

    chart_points = {}
    for name, p in pts.items():
        chart_points[name] = {
            'label': labels[name],
            'style': {
                'color': colors[name],
                'marker': markers[name],
                'markersize': 16 if name == 'ADP' else 14,
                'markeredgecolor': 'black',
                'markeredgewidth': 1.5,
            },
            'xy': (p['T'], humratio_to_rh_pct(p['T'], p['W'])),
        }

    connectors = [
        {
            'start': 'R', 'end': 'O',
            'label': 'Γραμμή ανάμιξης R — O',
            'style': {'color': '#ff7f0e', 'linewidth': 2.4, 'linestyle': '--'},
        },
        {
            'start': 'M', 'end': 'ADP',
            'label': 'Διεργασία ψυκτικού στοιχείου  M → S → ADP',
            'style': {'color': '#1f77b4', 'linewidth': 2.8},
        },
        {
            'start': 'S', 'end': 'R',
            'label': 'Διεργασία χώρου  S → R  (SHR = 0.924)',
            'style': {'color': '#2ca02c', 'linewidth': 2.8},
        },
    ]

    chart.plot_points_dbt_rh(chart_points, connectors=connectors)

    ax = chart.axes
    fig = ax.figure

    if full_range:
        # ---- Στους πλήρεις χάρτες: υπόμνημα + κουτί ΕΞΩ από τον χάρτη ----
        # Συμπιέζουμε λίγο τον χάρτη δεξιά για να χωρέσουν υπόμνημα + κουτί
        fig.subplots_adjust(left=0.06, right=0.74, top=0.93, bottom=0.08)

        legend = ax.legend(loc='upper left',
                           bbox_to_anchor=(1.02, 1.00),
                           fontsize=11, frameon=True,
                           labelspacing=0.7, borderpad=0.8,
                           edgecolor='gray', fancybox=True)

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
        # Τοποθέτηση κουτιού κάτω από το υπόμνημα
        ax.text(1.02, 0.40, info_text,
                transform=ax.transAxes,
                fontsize=11, verticalalignment='top', horizontalalignment='left',
                family='monospace',
                bbox=dict(boxstyle='round,pad=0.7', facecolor='#FFF9E6',
                          edgecolor='#888', linewidth=1.2, alpha=0.95))
    else:
        # ---- Στους εστιασμένους χάρτες: όπως πριν (μέσα στον χάρτη) ----
        chart.plot_legend(loc='upper left', fontsize=11, frameon=True,
                          labelspacing=0.6)
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
        ax.text(0.99, 0.98, info_text,
                transform=ax.transAxes,
                fontsize=11, verticalalignment='top', horizontalalignment='right',
                family='monospace',
                bbox=dict(boxstyle='round,pad=0.7', facecolor='#FFF9E6',
                          edgecolor='#888', linewidth=1.2, alpha=0.95))

    # ---- Ετικέτες δίπλα στα σημεία ----
    label_offsets = {
        'O':   (10, 8),
        'R':   (10, 10),
        'M':   (-22, 12),
        'S':   (-30, -3),
        'ADP': (-15, -18),
    }
    for name, p in pts.items():
        rh = humratio_to_rh_pct(p['T'], p['W'])
        dx, dy = label_offsets[name]
        ax.annotate(name,
                    xy=(p['T'], rh),
                    xytext=(dx, dy), textcoords='offset points',
                    fontsize=16, fontweight='bold',
                    color=colors[name], zorder=25,
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                              edgecolor=colors[name], linewidth=1.3,
                              alpha=0.93))

    chart.save(output_path)
    chart.close_fig()
    print(f"  ✓ Αποθηκεύτηκε: {output_path}")


if __name__ == "__main__":
    print("Δημιουργία ψυχρομετρικών χαρτών για το Ερώτημα γ...")

    # Εστιασμένοι χάρτες (όπως πριν)
    make_chart('i',  '/workspaces/Ergasia_Psiksi/psychrometric_case_i.png',
               full_range=False)
    make_chart('ii', '/workspaces/Ergasia_Psiksi/psychrometric_case_ii.png',
               full_range=False)

    # Χάρτες πλήρους εμβέλειας (0–50°C, 0–30 g/kg)
    make_chart('i',  '/workspaces/Ergasia_Psiksi/psychrometric_case_i_full.png',
               full_range=True)
    make_chart('ii', '/workspaces/Ergasia_Psiksi/psychrometric_case_ii_full.png',
               full_range=True)

    print("Ολοκληρώθηκε.")
