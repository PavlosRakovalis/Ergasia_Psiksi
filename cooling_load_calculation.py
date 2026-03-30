#!/usr/bin/env python3
"""
=================================================================
Ερώτημα β: Υπολογισμός Ψυκτικών Φορτίων — Μέθοδος CLTD/CLF
=================================================================
Κτίριο Γ1 — Ισόγειο ως μία ζώνη
Θεσσαλονίκη (40°N), 21 Ιουλίου
Ώρες: 08:00, 12:00, 16:00, 20:00, 24:00 (ηλιακή ώρα)

Μέθοδος: ASHRAE Handbook of Fundamentals 1989 (CLTD/CLF)
Τυπολόγιο: Μάθημα «Κλιματισμός», ΑΠΘ
=================================================================
"""
import csv

# =============================================================
# 1. ΔΕΔΟΜΕΝΑ ΣΧΕΔΙΑΣΜΟΥ
# =============================================================

# --- Κλιματικά δεδομένα Θεσσαλονίκης (Ιούλιος) ---
Ti = 26.0          # Εσωτερική θερμοκρασία σχεδιασμού [°C]
To_max = 36.0      # Μέγιστη εξωτερική θερμοκρασία [°C]
DR = 11.0          # Ημερήσια θερμοκρασιακή διακύμανση [°C]
To_mean = To_max - DR / 2  # = 30.5 °C
LAT = 40           # Γεωγραφικό πλάτος [°]

# Υγρασία (για λανθάνοντα φορτία αερισμού)
Wi = 0.0105    # kg_w/kg_da — εσωτερικός (26°C, 50% RH)
Wo = 0.0145    # kg_w/kg_da — εξωτερικός (Θεσ/νίκη Ιούλιος μέσος)

# --- Γεωμετρία κτιρίου ---
A_floor = 145.0    # Εμβαδόν δαπέδου/οροφής [m²]
H_floor = 3.0      # Ύψος ορόφου [m]
V_building = A_floor * H_floor  # = 435 m³

# Εξωτερικοί τοίχοι — καθαρά εμβαδά (ακαθάριστο − ανοίγματα)
wall_A = {'N': 22.30, 'S': 27.48, 'E': 35.94, 'W': 39.30}
U_wall = 0.40  # W/(m²·K) — ΚΕΝΑΚ Ζώνη Γ'

# Οροφή
A_roof = 145.0
U_roof = 0.35  # W/(m²·K) — ΚΕΝΑΚ Ζώνη Γ'

# Παράθυρα / Μπαλκονόπορτες
win_A = {'N': 7.70, 'S': 2.52, 'E': 7.56, 'W': 4.20}
U_glass = 2.40    # W/(m²·K) — ΚΕΝΑΚ Ζώνη Γ'
SC = 0.69          # Shading Coefficient — διπλός υαλοπίνακας, αλουμίνιο

# --- Συντελεστές διόρθωσης CLTD ---
K_wall = 0.65  # Ανοιχτόχρωμοι τοίχοι (μπεζ/κρεμ — τυπικό ελληνικό κτίριο)
K_roof = 1.0   # Σκουρόχρωμη/μέση οροφή
f_roof = 1.0   # Χωρίς ροή αέρα στην ψευδοροφή
# LM ≈ 0 για 40°N, Ιούλιο (Table 9: May/Jul row → ~0.0 παντού)
LM_wall = {'N': 0.0, 'S': 0.0, 'E': 0.0, 'W': 0.0}
LM_roof = 0.5  # HOR στίγμα 40°N May/Jul = 0.5 (Table 9)

# =============================================================
# 2. ΠΙΝΑΚΕΣ ASHRAE (CLTD / SHGF / CLF)
# =============================================================

# ---------------------------------------------------------------
# Table 7 — CLTD Τοίχων, Group D [°C]
# (ASHRAE 1989, 40°N, 21 Ιουλίου)
# Ομάδα D: μεσαίου βάρους τοίχος (τσιμεντόλιθος + μόνωση)
# Τιμές σε °C (= °F ÷ 1.8) — H01 έως H24
# ---------------------------------------------------------------
CLTD_wall = {
    'N':  [4.4, 3.9, 3.3, 2.8, 2.2, 2.2, 2.2, 2.8, 3.3, 3.9, 4.4, 5.0,
           5.6, 5.6, 5.6, 5.6, 5.6, 5.6, 5.6, 5.6, 5.6, 5.0, 5.0, 4.4],
    'E':  [5.6, 4.4, 3.9, 3.3, 2.8, 4.4, 8.9, 12.8, 14.4, 14.4, 13.3, 11.7,
           10.6, 9.4, 8.3, 7.8, 7.2, 6.7, 6.7, 6.1, 6.1, 6.1, 5.6, 5.6],
    'S':  [4.4, 3.9, 3.3, 2.8, 2.2, 2.2, 2.8, 3.3, 4.4, 6.1, 7.8, 9.4,
           10.0, 10.0, 9.4, 8.3, 7.8, 7.2, 6.7, 6.1, 5.6, 5.6, 5.0, 5.0],
    'W':  [9.4, 8.9, 7.2, 6.1, 5.0, 3.9, 3.3, 3.3, 3.3, 3.3, 3.3, 3.3,
           3.9, 5.6, 8.3, 12.2, 15.0, 16.1, 15.0, 13.3, 12.2, 11.1, 10.6, 10.0],
}

# ---------------------------------------------------------------
# Table 5 — CLTD Οροφής, Τύπος 9 χωρίς ψευδοροφή [°C]
# 101.6mm h.w. concrete + 25.4mm insulation (Μάζα=254 kg/m²)
# Αντιπροσωπευτικός για ελληνική πλακοσκεπή (οπλισμένο σκυρόδεμα + μόνωση)
# ---------------------------------------------------------------
CLTD_roof = [7.8, 6.7, 5.6, 4.4, 3.9, 2.8, 2.2, 2.2, 3.3, 4.4,
             6.1, 8.3, 10.0, 12.2, 13.9, 15.6, 16.1, 16.7, 16.1, 15.0,
             13.3, 11.7, 10.6, 8.9]

# ---------------------------------------------------------------
# Table 10 — CLTD Υαλοπινάκων (αγωγιμότητα μόνο) [°C]
# Δεν παίρνει διόρθωση LM
# ---------------------------------------------------------------
CLTD_glass = [1, 0, -1, -1, -1, -1, -1, 0, 1, 2, 4, 5,
              7, 7, 8, 8, 7, 7, 6, 4, 3, 2, 2, 1]

# ---------------------------------------------------------------
# Table 11 — SHGF_max [W/m²] — 40°N, Ιούλιος
# (Maximum Solar Heat Gain Factor — μονός υαλοπίνακας αναφοράς 3mm)
# ---------------------------------------------------------------
SHGF_max = {'N': 131, 'E': 527, 'S': 190, 'W': 527}

# ---------------------------------------------------------------
# Table 14 — CLF Ηλιακών Κερδών Παραθύρων (εσωτερική σκίαση)
# H01 έως H24
# ---------------------------------------------------------------
CLF_solar = {
    'N': [0.08,0.07,0.06,0.06,0.07,0.73,0.66,0.65,0.73,0.80,0.86,0.89,
          0.89,0.86,0.82,0.75,0.78,0.91,0.24,0.18,0.15,0.13,0.11,0.10],
    'E': [0.03,0.02,0.02,0.02,0.02,0.47,0.72,0.80,0.76,0.62,0.41,0.27,
          0.24,0.22,0.20,0.17,0.14,0.11,0.06,0.05,0.05,0.04,0.03,0.03],
    'S': [0.04,0.04,0.03,0.03,0.03,0.09,0.16,0.23,0.38,0.58,0.75,0.83,
          0.80,0.68,0.50,0.35,0.27,0.19,0.11,0.09,0.08,0.07,0.06,0.05],
    'W': [0.05,0.05,0.04,0.04,0.03,0.06,0.09,0.11,0.13,0.15,0.16,0.17,
          0.31,0.53,0.72,0.82,0.81,0.61,0.16,0.12,0.10,0.08,0.07,0.06],
}

# ---------------------------------------------------------------
# Ωριαίο προφίλ εξωτερικής θερμοκρασίας (ASHRAE)
# Ποσοστό % της ημερήσιας διακύμανσης κάτω από To_max
# ---------------------------------------------------------------
TEMP_PROFILE_PCT = {
    1: 87, 2: 92, 3: 96, 4: 99, 5: 100,
    6: 98, 7: 93, 8: 84, 9: 71, 10: 56,
    11: 39, 12: 23, 13: 11, 14: 3, 15: 0,
    16: 3, 17: 10, 18: 21, 19: 34, 20: 47,
    21: 58, 22: 68, 23: 76, 24: 82,
}


def To_hourly(h):
    """Εξωτερική θερμοκρασία την ώρα h (ηλιακή ώρα)."""
    return To_max - DR * TEMP_PROFILE_PCT[h] / 100.0


# =============================================================
# 3. ΕΣΩΤΕΡΙΚΑ ΦΟΡΤΙΑ — ΠΑΡΑΔΟΧΕΣ
# =============================================================

# Άνθρωποι (κατοικία — ελαφριά δραστηριότητα, καθιστοί)
N_people = 4
HG_sens_person = 73   # W/άτομο (Table 18)
HG_lat_person = 59     # W/άτομο (Table 18)
CLF_people = 1.0       # Κατοικία: σύστημα λειτουργεί μόνο κατά τη χρήση → CLF=1

# Φωτισμός
P_lights_installed = 10 * A_floor  # 10 W/m² × 145 m² = 1450 W
fu_lights = 0.30     # 30% σε λειτουργία (κατοικία — μέρα χαμηλό, βράδυ υψηλό)
fs_lights = 1.0      # LED / πυρακτώσεως
CLF_lights = 1.0     # Σύστημα λειτουργεί μόνο κατά τη χρήση → CLF=1.0
# HG_lights = P × fu × fs = 1450 × 0.30 × 1.0 = 435 W

# Εξοπλισμός (ψυγείο, TV, ηλεκτρονικά, μαγείρεμα)
HG_equip_sens = 400   # W αισθητό
HG_equip_lat = 200     # W λανθάνον (μαγείρεμα, μπάνιο)
CLF_equip = 1.0

# Αερισμός / Διείσδυση
ACH = 0.5  # Εναλλαγές αέρα ανά ώρα (φυσικός αερισμός + διείσδυση)
V_dot_m3s = V_building * ACH / 3600  # 435×0.5/3600 = 0.0604 m³/s
rho_air = 1.204  # kg/m³
m_dot_air = rho_air * V_dot_m3s  # 0.0728 kg/s

# Ιδιότητες υγρού αέρα (κατά τυπολόγιο)
def Cp_moist(Wi_val, Wo_val):
    """Cp υγρού αέρα [J/(kg·°C)]."""
    W_avg = (Wi_val + Wo_val) / 2
    return 1005 + W_avg * 1852

def hg_vapor(Ti_val, To_val):
    """Ενθαλπία αναφοράς υδρατμών [J/kg_w]."""
    T_avg = (Ti_val + To_val) / 2
    return (1.852 * T_avg + 2501.6) * 1000  # kJ→J


# =============================================================
# 4. ΥΠΟΛΟΓΙΣΜΟΙ ΑΝΑ ΩΡΑ
# =============================================================

target_hours = [8, 12, 16, 20, 24]

print("=" * 90)
print("ΥΠΟΛΟΓΙΣΜΟΣ ΨΥΚΤΙΚΩΝ ΦΟΡΤΙΩΝ — ΜΕΘΟΔΟΣ CLTD/CLF (ASHRAE 1989)")
print("Κτίριο Γ1, Θεσσαλονίκη (40°N), 21 Ιουλίου")
print("=" * 90)

print(f"\n{'ΔΕΔΟΜΕΝΑ ΣΧΕΔΙΑΣΜΟΥ':^90}")
print(f"  Ti = {Ti}°C | To_max = {To_max}°C | DR = {DR}°C | To_mean = {To_mean}°C")
print(f"  K_τοίχ = {K_wall} | K_οροφ = {K_roof} | f = {f_roof} | SC = {SC}")
print(f"  Wi = {Wi} kg/kg | Wo = {Wo} kg/kg | ACH = {ACH}")
print(f"  Τοίχοι Group D | Οροφή Type 9 | CLF_internal = 1.0")

# Temperature correction (common to all hours)
temp_corr = (25.5 - Ti) + (To_mean - 29.4)
print(f"\n  Διόρθωση θερμοκρασίας: (25.5−{Ti}) + ({To_mean}−29.4) = {temp_corr:+.1f} °C")

# Storage for summary table
summary = []

for h in target_hours:
    idx = h - 1  # 0-based index (H01→0, H08→7, etc.)
    To_h = To_hourly(h)

    print(f"\n{'─' * 90}")
    print(f"  ΩΡΑ {h:02d}:00   |   To = {To_h:.1f}°C   |   ΔΤ(To−Ti) = {To_h - Ti:.1f}°C")
    print(f"{'─' * 90}")

    # ─── A. ΤΟΙΧΟΙ ──────────────────────────────────────────
    print(f"\n  A. ΕΞΩΤΕΡΙΚΟΙ ΤΟΙΧΟΙ  (q = U × A × CLTD_corr)")
    print(f"  {'Προσ.':>5s} {'A(m²)':>7s} {'U':>5s} {'CLTD':>6s} {'LM':>5s} "
          f"{'CLTD×K':>7s} {'CLTD_c':>7s} {'q(W)':>8s}")

    q_walls_total = 0
    wall_details = {}
    for orient in ['N', 'S', 'E', 'W']:
        A = wall_A[orient]
        cltd_raw = CLTD_wall[orient][idx]
        lm = LM_wall[orient]
        cltd_k = (cltd_raw + lm) * K_wall
        cltd_corr = cltd_k + temp_corr
        q = U_wall * A * cltd_corr
        wall_details[orient] = {'cltd_raw': cltd_raw, 'cltd_corr': cltd_corr, 'q': q}
        q_walls_total += q
        print(f"  {orient:>5s} {A:>7.2f} {U_wall:>5.2f} {cltd_raw:>6.1f} {lm:>5.1f} "
              f"{cltd_k:>7.2f} {cltd_corr:>7.2f} {q:>8.1f}")
    print(f"  {'Σύνολο τοίχων:':>50s} {q_walls_total:>8.1f} W")

    # ─── B. ΟΡΟΦΗ ────────────────────────────────────────────
    cltd_roof_raw = CLTD_roof[idx]
    cltd_roof_k = (cltd_roof_raw + LM_roof) * K_roof
    cltd_roof_corr = cltd_roof_k + temp_corr
    q_roof = U_roof * A_roof * cltd_roof_corr * f_roof

    print(f"\n  B. ΟΡΟΦΗ  (q = U × A × CLTD_corr × f)")
    print(f"     CLTD_table = {cltd_roof_raw:.1f}°C | LM = {LM_roof} | "
          f"K = {K_roof} | f = {f_roof}")
    print(f"     CLTD_corr = ({cltd_roof_raw}+{LM_roof})×{K_roof} + {temp_corr:+.1f} "
          f"= {cltd_roof_corr:.2f}°C")
    print(f"     q = {U_roof} × {A_roof} × {cltd_roof_corr:.2f} × {f_roof} = {q_roof:.1f} W")

    # ─── C. ΠΑΡΑΘΥΡΑ — ΑΓΩΓΙΜΟΤΗΤΑ ──────────────────────────
    cltd_gl_raw = CLTD_glass[idx]
    cltd_gl_corr = cltd_gl_raw + temp_corr  # Χωρίς K, χωρίς LM

    print(f"\n  C. ΠΑΡΑΘΥΡΑ — ΑΓΩΓΙΜΟΤΗΤΑ  (q = U × A × CLTD_corr)")
    print(f"     CLTD_table = {cltd_gl_raw}°C | CLTD_corr = {cltd_gl_raw} + {temp_corr:+.1f}"
          f" = {cltd_gl_corr:.1f}°C")

    q_glass_cond_total = 0
    for orient in ['N', 'S', 'E', 'W']:
        A = win_A[orient]
        q = U_glass * A * cltd_gl_corr
        q_glass_cond_total += q
        print(f"     {orient}: {U_glass}×{A:.2f}×{cltd_gl_corr:.1f} = {q:.1f} W")
    print(f"  {'Σύνολο αγωγιμότητας υαλοπινάκων:':>50s} {q_glass_cond_total:>8.1f} W")

    # ─── D. ΠΑΡΑΘΥΡΑ — ΗΛΙΑΚΑ ΚΕΡΔΗ ─────────────────────────
    print(f"\n  D. ΠΑΡΑΘΥΡΑ — ΗΛΙΑΚΑ  (q = A × SC × SHGF_max × CLF)")
    print(f"  {'Προσ.':>5s} {'A(m²)':>7s} {'SC':>5s} {'SHGF':>6s} {'CLF':>6s} {'q(W)':>8s}")

    q_glass_solar_total = 0
    for orient in ['N', 'S', 'E', 'W']:
        A = win_A[orient]
        shgf = SHGF_max[orient]
        clf = CLF_solar[orient][idx]
        q = A * SC * shgf * clf
        q_glass_solar_total += q
        print(f"  {orient:>5s} {A:>7.2f} {SC:>5.2f} {shgf:>6d} {clf:>6.2f} {q:>8.1f}")
    print(f"  {'Σύνολο ηλιακών κερδών:':>50s} {q_glass_solar_total:>8.1f} W")

    # ─── E. ΕΣΩΤΕΡΙΚΑ ΦΟΡΤΙΑ ─────────────────────────────────
    q_people_sens = N_people * HG_sens_person * CLF_people
    q_people_lat = N_people * HG_lat_person

    q_lights = P_lights_installed * fu_lights * fs_lights * CLF_lights

    q_equip_sens = HG_equip_sens * CLF_equip
    q_equip_lat = HG_equip_lat

    print(f"\n  E. ΕΣΩΤΕΡΙΚΑ ΦΟΡΤΙΑ")
    print(f"     Άνθρωποι ({N_people} άτομα): αισθ. = {q_people_sens:.0f} W, "
          f"λανθ. = {q_people_lat:.0f} W")
    print(f"     Φωτισμός: {q_lights:.0f} W (αισθητό)")
    print(f"     Εξοπλισμός: αισθ. = {q_equip_sens:.0f} W, λανθ. = {q_equip_lat:.0f} W")

    q_internal_sens = q_people_sens + q_lights + q_equip_sens
    q_internal_lat = q_people_lat + q_equip_lat
    print(f"     Σύνολο εσωτερικών: αισθ. = {q_internal_sens:.0f} W, "
          f"λανθ. = {q_internal_lat:.0f} W")

    # ─── F. ΑΕΡΙΣΜΟΣ / ΔΙΕΙΣΔΥΣΗ ─────────────────────────────
    dT = To_h - Ti
    Cp = Cp_moist(Wi, Wo)
    q_vent_sens = m_dot_air * Cp * max(dT, 0)

    dW = Wo - Wi
    hg = hg_vapor(Ti, To_h)
    q_vent_lat = m_dot_air * dW * hg if dW > 0 else 0

    print(f"\n  F. ΑΕΡΙΣΜΟΣ ({ACH} ACH = {V_dot_m3s*1000:.1f} L/s, "
          f"ṁ = {m_dot_air:.4f} kg/s)")
    print(f"     ΔΤ = {dT:.1f}°C → q_αισθ = {q_vent_sens:.1f} W")
    print(f"     ΔW = {dW:.4f} kg/kg → q_λανθ = {q_vent_lat:.1f} W")

    # ─── ΣΥΝΟΛΑ ──────────────────────────────────────────────
    Q_sens = (q_walls_total + q_roof + q_glass_cond_total +
              q_glass_solar_total + q_internal_sens + q_vent_sens)
    Q_lat = q_internal_lat + q_vent_lat
    Q_total = Q_sens + Q_lat

    print(f"\n  {'═' * 50}")
    print(f"  ΣΥΝΟΛΙΚΟ ΑΙΣΘΗΤΟ ΦΟΡΤΙΟ:    {Q_sens:>10.1f} W  ({Q_sens/1000:.2f} kW)")
    print(f"  ΣΥΝΟΛΙΚΟ ΛΑΝΘΑΝΟΝ ΦΟΡΤΙΟ:   {Q_lat:>10.1f} W  ({Q_lat/1000:.2f} kW)")
    print(f"  ΣΥΝΟΛΙΚΟ ΨΥΚΤΙΚΟ ΦΟΡΤΙΟ:    {Q_total:>10.1f} W  ({Q_total/1000:.2f} kW)")
    print(f"  {'═' * 50}")

    summary.append({
        'hour': h,
        'To': To_h,
        'walls': q_walls_total,
        'roof': q_roof,
        'glass_cond': q_glass_cond_total,
        'glass_solar': q_glass_solar_total,
        'internal_sens': q_internal_sens,
        'vent_sens': q_vent_sens,
        'Q_sens': Q_sens,
        'internal_lat': q_internal_lat,
        'vent_lat': q_vent_lat,
        'Q_lat': Q_lat,
        'Q_total': Q_total,
    })


# =============================================================
# 5. ΣΥΝΟΠΤΙΚΟΣ ΠΙΝΑΚΑΣ
# =============================================================

print(f"\n\n{'=' * 90}")
print(f"{'ΣΥΝΟΠΤΙΚΟΣ ΠΙΝΑΚΑΣ ΑΠΟΤΕΛΕΣΜΑΤΩΝ (W)':^90}")
print(f"{'=' * 90}")

header = (f"{'Ώρα':>5s} {'To°C':>5s} │{'Τοίχοι':>8s} {'Οροφή':>8s} "
          f"{'Υαλ.αγ':>8s} {'Ηλιακά':>8s} {'Εσωτ.':>8s} {'Αερ.αισ':>8s} "
          f"│{'Q_αισθ':>9s} {'Q_λανθ':>8s} │{'Q_total':>9s}")
print(header)
print("─" * 90)

for r in summary:
    line = (f"{r['hour']:>5d} {r['To']:>5.1f} │"
            f"{r['walls']:>8.0f} {r['roof']:>8.0f} "
            f"{r['glass_cond']:>8.0f} {r['glass_solar']:>8.0f} "
            f"{r['internal_sens']:>8.0f} {r['vent_sens']:>8.0f} "
            f"│{r['Q_sens']:>9.0f} {r['Q_lat']:>8.0f} │{r['Q_total']:>9.0f}")
    print(line)

print("─" * 90)

# Μέγιστο φορτίο
max_entry = max(summary, key=lambda x: x['Q_total'])
print(f"\n  ► ΜΕΓΙΣΤΟ ΨΥΚΤΙΚΟ ΦΟΡΤΙΟ: {max_entry['Q_total']:.0f} W "
      f"({max_entry['Q_total']/1000:.2f} kW) στις {max_entry['hour']:02d}:00")
print(f"    (Αισθητό: {max_entry['Q_sens']:.0f} W + Λανθάνον: {max_entry['Q_lat']:.0f} W)")


# =============================================================
# 6. ΣΧΟΛΙΑΣΜΟΣ & ΒΕΛΤΙΩΣΕΙΣ
# =============================================================

print(f"\n\n{'=' * 90}")
print(f"{'ΣΧΟΛΙΑΣΜΟΣ ΕΠΙΔΡΑΣΗΣ ΠΑΡΑΓΟΝΤΩΝ & ΠΡΟΤΑΣΕΙΣ ΒΕΛΤΙΩΣΗΣ':^90}")
print(f"{'=' * 90}")

comments = """
1. ΗΛΙΑΚΑ ΚΕΡΔΗ ΠΑΡΑΘΥΡΩΝ (μεγαλύτερη συνεισφορά)
   - Κυρίαρχος παράγοντας, ιδιαίτερα στις ώρες αιχμής.
   - Ανατολικά & δυτικά παράθυρα: μέγιστα κέρδη πρωί/απόγευμα αντίστοιχα.
   - Η μεγάλη μπαλκονόπορτα Ανατολής (7.56 m²) δίνει πολύ υψηλό φορτίο.
   ► Βελτίωση: Εξωτερική σκίαση (τέντες, brise-soleil), ειδικά σε Α/Δ.
     Χρήση low-e υαλοπινάκων (SC→0.35) μειώνει τα ηλιακά κατά ~50%.

2. ΟΡΟΦΗ (δεύτερη μεγαλύτερη συνεισφορά)
   - Μεγάλη επιφάνεια (145 m²) εκτεθειμένη στον ήλιο.
   - Μέγιστο CLTD απόγευμα (16-18h) λόγω θερμικής αδράνειας σκυροδέματος.
   ► Βελτίωση: Αύξηση μόνωσης (U: 0.35→0.20), ανοιχτόχρωμη μεμβράνη
     (K: 1.0→0.5), cool roof (ψυχρή οροφή).

3. ΤΟΙΧΟΙ
   - Μέτρια συνεισφορά χάρη στο χαμηλό U=0.40.
   - Ο δυτικός τοίχος (39.30 m²) δίνει τη μεγαλύτερη αιχμή (απόγευμα).
   ► Βελτίωση: Μείωση U σε 0.30 ή εξωτερική μόνωση ETICS παχύτερη.

4. ΑΓΩΓΙΜΟΤΗΤΑ ΥΑΛΟΠΙΝΑΚΩΝ
   - Σημαντική λόγω υψηλού U=2.40 (4-6× χειρότερο από τοίχους).
   ► Βελτίωση: Τριπλός υαλοπίνακας (U→1.20) ή low-e (U→1.60).

5. ΕΣΩΤΕΡΙΚΑ ΦΟΡΤΙΑ
   - Σταθερά σε όλες τις ώρες (CLF=1.0 για κατοικία).
   - Λανθάνοντα: κυρίως από ανθρώπους + μαγείρεμα.
   ► Βελτίωση: LED φωτισμός, ενεργειακές συσκευές (A+++).

6. ΑΕΡΙΣΜΟΣ / ΔΙΕΙΣΔΥΣΗ
   - Αισθητό φορτίο ακολουθεί την εξωτερική θερμοκρασία.
   - Λανθάνον σταθερό (εξαρτάται από ΔW).
   ► Βελτίωση: Αεροστεγανότητα κτιρίου, ανάκτηση θερμότητας (HRV).

7. ΧΡΟΝΙΚΗ ΚΑΤΑΝΟΜΗ
   - Αιχμή στις 16:00: συνδυασμός ηλιακών Δύσης + μέγιστης To + οροφής.
   - Στις 24:00: ελάχιστο φορτίο (μόνο θερμική αδράνεια + εσωτερικά).
   - Ο σχεδιασμός του συστήματος κλιματισμού βασίζεται στο μέγιστο.
"""
print(comments)

# =============================================================
# 7. ΕΞΑΓΩΓΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ΣΕ CSV
# =============================================================

csv_path = "/workspaces/Ergasia_Psiksi/Αποτελεσματα_CLTD_Ερωτημα_β.csv"
with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Ώρα', 'To(°C)', 'Τοίχοι(W)', 'Οροφή(W)',
                     'Υαλ.Αγωγ.(W)', 'Ηλιακά(W)', 'Εσωτ.Αισθ.(W)',
                     'Αερ.Αισθ.(W)', 'Q_αισθητό(W)',
                     'Εσωτ.Λανθ.(W)', 'Αερ.Λανθ.(W)', 'Q_λανθάνον(W)',
                     'Q_συνολικό(W)', 'Q_συνολικό(kW)'])
    for r in summary:
        writer.writerow([
            f"{r['hour']:02d}:00", f"{r['To']:.1f}",
            f"{r['walls']:.1f}", f"{r['roof']:.1f}",
            f"{r['glass_cond']:.1f}", f"{r['glass_solar']:.1f}",
            f"{r['internal_sens']:.0f}", f"{r['vent_sens']:.1f}",
            f"{r['Q_sens']:.1f}",
            f"{r['internal_lat']:.0f}", f"{r['vent_lat']:.1f}",
            f"{r['Q_lat']:.1f}",
            f"{r['Q_total']:.1f}", f"{r['Q_total']/1000:.2f}",
        ])

print(f"  Αποτελέσματα αποθηκεύτηκαν: {csv_path}")

# =============================================================
# 8. ΕΞΑΓΩΓΗ ΦΥΛΛΟΥ ΕΡΓΑΣΙΑΣ
# =============================================================

ws_path = "/workspaces/Ergasia_Psiksi/Φυλλο_εργασιας_CLTD (1)(Table 1) (1).csv"

# Precompute all values per hour into a structured dict
ws_data = {}
for h in target_hours:
    idx = h - 1
    To_h = To_hourly(h)
    d = {}

    # Walls
    d['wall'] = {}
    d['wall_total'] = 0
    for orient in ['N', 'S', 'E', 'W']:
        cltd_raw = CLTD_wall[orient][idx]
        cltd_corr = (cltd_raw + LM_wall[orient]) * K_wall + temp_corr
        q = U_wall * wall_A[orient] * cltd_corr
        d['wall'][orient] = {'cltd': cltd_raw, 'cltd_c': cltd_corr, 'q': q}
        d['wall_total'] += q

    # Roof
    cltd_raw = CLTD_roof[idx]
    cltd_corr = (cltd_raw + LM_roof) * K_roof + temp_corr
    d['roof_cltd'] = cltd_raw
    d['roof_cltd_c'] = cltd_corr
    d['roof_q'] = U_roof * A_roof * cltd_corr * f_roof

    # Glass conduction
    cltd_raw = CLTD_glass[idx]
    cltd_corr = cltd_raw + temp_corr
    d['gl_cltd'] = cltd_raw
    d['gl_cltd_c'] = cltd_corr
    d['gl_cond'] = {}
    d['gl_cond_total'] = 0
    for orient in ['N', 'S', 'E', 'W']:
        q = U_glass * win_A[orient] * cltd_corr
        d['gl_cond'][orient] = q
        d['gl_cond_total'] += q

    # Glass solar
    d['gl_solar'] = {}
    d['gl_solar_total'] = 0
    for orient in ['N', 'S', 'E', 'W']:
        clf = CLF_solar[orient][idx]
        q = win_A[orient] * SC * SHGF_max[orient] * clf
        d['gl_solar'][orient] = {'clf': clf, 'q': q}
        d['gl_solar_total'] += q

    # Ventilation
    dT = To_h - Ti
    Cp = Cp_moist(Wi, Wo)
    d['vent_sens'] = m_dot_air * Cp * max(dT, 0)
    dW = Wo - Wi
    hg = hg_vapor(Ti, To_h)
    d['vent_lat'] = m_dot_air * dW * hg if dW > 0 else 0
    d['To'] = To_h
    d['dT'] = dT

    # Internal
    d['int_sens'] = N_people * HG_sens_person * CLF_people + \
                    P_lights_installed * fu_lights * fs_lights * CLF_lights + \
                    HG_equip_sens * CLF_equip
    d['int_lat'] = N_people * HG_lat_person + HG_equip_lat

    # Totals
    d['Q_sens'] = (d['wall_total'] + d['roof_q'] + d['gl_cond_total'] +
                   d['gl_solar_total'] + d['int_sens'] + d['vent_sens'])
    d['Q_lat'] = d['int_lat'] + d['vent_lat']
    d['Q_total'] = d['Q_sens'] + d['Q_lat']

    ws_data[h] = d

hours = target_hours
H = ws_data  # shorthand

def hr_vals(fn):
    """Return 15 cells: for each of 5 hours → CLTDt_or_CLF, (empty), qt."""
    cells = []
    for h in hours:
        v = fn(h)
        cells.extend(v)
    return cells

def fmt(x, decimals=1):
    return f"{x:.{decimals}f}"

rows = []

# Header block
rows.append(['Δεδομένα Εργασίας','','Ημερομηνία:','21 Ιουλίου','','','','','','Μηχανικός:','','','','','','','','','','','','','','',''])
rows.append(['Τοποθεσία','','Θεσσαλονίκη','Γ.Πλάτος:','40°N','','','','','Γ.Μήκος:','22.9°E','','','','','','','','','','','','','',''])
rows.append(['Συνθήκες Σχεδιασμού','','Εσ. Θερμοκρασία:','26.0 °C','','Εσ. Σχ. Υγρασία:','50%','','','Εξ. Θερμοκρασία:','36.0 °C (max) / 30.5 °C (μέση)','','Εξ. Σχ. Υγρασία:','~45%','','DR=11.0°C','','','','','','','','',''])
rows.append(['Χώρος','','ΚΤΙΡΙΟ Γ1 - ΚΑΤΟΨΗ ΙΣΟΓΕΙΟΥ (ΜΙΑ ΖΩΝΗ)','','','','','','','10.00 × 14.50 m = 145.00 m²','','','','','','','','','','','','','','',''])
rows.append(['Παραδοχές','','Τοίχοι: Ομάδα D / K=0.65 / LM≈0','','Οροφή: Τύπος 9 / K=1.0 / f=1.0 / LM_HOR=0.5','','','Παράθυρα: SC=0.69','','Διόρθωση: (25.5−26)+(30.5−29.4) = +0.6°C','','','','','','','','','','','','','','',''])
rows.append(['']*25)

# Hour headers
hour_header = ['ΑΙΣΘΗΤΑ ΦΟΡΤΙΑ','','','','','','','','','']
for h in hours:
    hour_header.extend([f'{h:02d}:00','',''])
rows.append(hour_header)

sub_header = ['','','','','','','','','','']
for h in hours:
    sub_header.extend(['CLTDt/CLF','','qt (W)'])
rows.append(sub_header)

col_header = ['Στοιχείο — Προσ/μός','Τύπος κατασκευής','','','','','U [W/m²K]','','A [m²]','']
for h in hours:
    col_header.extend(['°C','','W'])
rows.append(col_header)

rows.append(['']*25)

# --- WALLS ---
rows.append(['ΤΟΙΧΟΙ (q = U × A × CLTDcorr)','CLTDcorr = (CLTD+LM)×K + 0.6'] + ['']*23)

wall_names = {'N': 'Τοίχος Βορράς (Β)', 'S': 'Τοίχος Νότος (Ν)',
              'E': 'Τοίχος Ανατολή (Α)', 'W': 'Τοίχος Δύση (Δ)'}
for orient in ['N', 'S', 'E', 'W']:
    row = [wall_names[orient], 'Ομάδα D / K=0.65', '', '', '', '',
           fmt(U_wall, 2), '', fmt(wall_A[orient], 2), '']
    for h in hours:
        d = H[h]['wall'][orient]
        row.extend([fmt(d['cltd']), '', fmt(d['q'])])
    rows.append(row)

# Wall totals
row = ['Σύνολο τοίχων', ''] + ['']*8
for h in hours:
    row.extend(['', '', fmt(H[h]['wall_total'])])
rows.append(row)
rows.append(['']*25)

# --- ROOF ---
rows.append(['ΟΡΟΦΗ (q = U × A × CLTDcorr × f)','CLTDcorr = (CLTD+0.5)×1.0 + 0.6'] + ['']*23)
row = ['Οροφή (Τύπος 9)', 'Τύπος 9 / K=1.0 / f=1.0', '', '', '', '',
       fmt(U_roof, 2), '', fmt(A_roof, 2), '']
for h in hours:
    row.extend([fmt(H[h]['roof_cltd']), '', fmt(H[h]['roof_q'])])
rows.append(row)
rows.append(['']*25)

# --- GLASS CONDUCTION ---
rows.append(['ΠΑΡΑΘΥΡΑ — ΑΓΩΓΙΜΟΤΗΤΑ (q = U × A × CLTDcorr)','CLTDcorr = CLTD + 0.6 (χωρίς K/LM)'] + ['']*23)

gl_names = {'N': 'Π1+Π2 Βορράς', 'S': 'Π3 Νότος',
            'E': 'Μπαλκ. Ανατολή', 'W': 'Μπαλκ. Δύση'}
for orient in ['N', 'S', 'E', 'W']:
    row = [gl_names[orient], 'Διπλός υαλοπίνακας', '', '', '', '',
           fmt(U_glass, 2), '', fmt(win_A[orient], 2), '']
    for h in hours:
        row.extend([str(H[h]['gl_cltd']), '', fmt(H[h]['gl_cond'][orient])])
    rows.append(row)

# Glass cond totals
row = ['Σύνολο αγωγιμ. υαλοπ.', ''] + ['']*8
for h in hours:
    row.extend(['', '', fmt(H[h]['gl_cond_total'])])
rows.append(row)
rows.append(['']*25)

# --- GLASS SOLAR ---
rows.append(['ΠΑΡΑΘΥΡΑ — ΗΛΙΑΚΑ (q = A × SC × SHGFmax × CLF)',''] + ['']*23)
# Sub-header for solar
sol_sub = ['Στοιχείο — Προσ/μός','','','','A [m²]','','SC','','SHGFmax','']
for h in hours:
    sol_sub.extend(['CLF','','q (W)'])
rows.append(sol_sub)

gl_orient_names = {'N': 'Π1+Π2 Βορράς (Β)', 'S': 'Π3 Νότος (Ν)',
                   'E': 'Μπαλκ. Ανατολή (Α)', 'W': 'Μπαλκ. Δύση (Δ)'}
for orient in ['N', 'S', 'E', 'W']:
    row = [gl_orient_names[orient], '', '', '', fmt(win_A[orient], 2), '',
           fmt(SC, 2), '', str(SHGF_max[orient]), '']
    for h in hours:
        d = H[h]['gl_solar'][orient]
        row.extend([fmt(d['clf'], 2), '', fmt(d['q'])])
    rows.append(row)

# Solar totals
row = ['Σύνολο ηλιακών κερδών', ''] + ['']*8
for h in hours:
    row.extend(['', '', fmt(H[h]['gl_solar_total'])])
rows.append(row)
rows.append(['']*25)

# --- VENTILATION (sensible) ---
rows.append(['ΕΝΑΛΛΑΓΕΣ ΑΕΡΑ (q_αισθ = ṁ × Cp × ΔΤ)', f'ACH={ACH}  ṁ={m_dot_air:.4f} kg/s  V={V_dot_m3s*1000:.1f} L/s'] + ['']*23)
row = ['', '', '', '', '', '', '', '', '', '']
for h in hours:
    row.extend([f"To={H[h]['To']:.1f}  ΔΤ={H[h]['dT']:.1f}", '', fmt(H[h]['vent_sens'])])
rows.append(row)
rows.append(['']*25)

# --- INTERNAL PARTITIONS ---
rows.append(['ΕΣΩΤΕΡΙΚΑ ΧΩΡΙΣΜΑΤΑ (q = U × A × ΔΤ)',''] + ['']*23)
row = ['Δεν υπολογίζονται — ενιαία ζώνη (ΔΤ=0)', ''] + ['']*8
for h in hours:
    row.extend(['', '', '0.0'])
rows.append(row)
rows.append(['']*25)

# --- INTERNAL LOADS (sensible) ---
rows.append(['ΕΣΩΤΕΡΙΚΑ ΦΟΡΤΙΑ (αισθητά)','','','','Αριθμός/Ισχύς','','HG/μονάδα','','CLF',''] + ['']*15)
# People
row = ['Άνθρωποι','','','',f'{N_people} άτομα','',f'{HG_sens_person} W/άτ.','','1.0','']
for h in hours:
    row.extend(['','',fmt(N_people * HG_sens_person * CLF_people, 0)])
rows.append(row)
# Lights
row = ['Φωτισμός','','','',f'{P_lights_installed:.0f} W (εγκατ.)','','fu=0.30 / fs=1.0','','1.0','']
for h in hours:
    row.extend(['','',fmt(P_lights_installed * fu_lights * fs_lights * CLF_lights, 0)])
rows.append(row)
# Equipment
row = ['Εξοπλισμός (αισθητό)','','','','—','',f'{HG_equip_sens} W','','1.0','']
for h in hours:
    row.extend(['','',fmt(HG_equip_sens * CLF_equip, 0)])
rows.append(row)
# Internal total
row = ['Σύνολο εσωτ. αισθητών',''] + ['']*8
for h in hours:
    row.extend(['','',fmt(H[h]['int_sens'], 0)])
rows.append(row)
rows.append(['']*25)

# --- TOTAL SENSIBLE ---
row = ['ΣΥΝΟΛΙΚΟ ΑΙΣΘΗΤΟ ΦΟΡΤΙΟ',''] + ['']*8
for h in hours:
    row.extend(['','',fmt(H[h]['Q_sens'])])
rows.append(row)
rows.append(['']*25)
rows.append(['']*25)

# === LATENT LOADS ===
lat_header = ['ΛΑΝΘΑΝΟΝΤΑ ΦΟΡΤΙΑ','','','','','','','','','']
for h in hours:
    lat_header.extend([f'{h:02d}:00','',''])
rows.append(lat_header)
rows.append(['']*25)

# Ventilation latent
rows.append(['Εναλλαγές αέρα (q_λανθ = ṁ × ΔW × hg)',''] + ['']*23)
row = ['', f'ṁ={m_dot_air:.4f} kg/s', '', '', f'Wo={Wo}', '', f'Wi={Wi}', '',
       f'ΔW={Wo-Wi:.4f}', '']
for h in hours:
    row.extend(['', '', fmt(H[h]['vent_lat'])])
rows.append(row)
rows.append(['']*25)

# People latent
row = ['Άνθρωποι (λανθάνον)', '', '', '', f'{N_people} άτομα', '',
       f'{HG_lat_person} W/άτ.', '', '', '']
for h in hours:
    row.extend(['', '', fmt(N_people * HG_lat_person, 0)])
rows.append(row)

# Equipment latent
row = ['Εξοπλισμός (λανθάνον)', '', '', '', '—', '',
       f'{HG_equip_lat} W', '', '', '']
for h in hours:
    row.extend(['', '', fmt(HG_equip_lat, 0)])
rows.append(row)
rows.append(['']*25)

# --- TOTAL LATENT ---
row = ['ΣΥΝΟΛΙΚΑ ΛΑΝΘΑΝΟΝΤΑ ΦΟΡΤΙΑ',''] + ['']*8
for h in hours:
    row.extend(['','',fmt(H[h]['Q_lat'])])
rows.append(row)
rows.append(['']*25)
rows.append(['']*25)

# --- GRAND TOTAL ---
row = ['ΣΥΝΟΛΙΚΟ ΨΥΚΤΙΚΟ ΦΟΡΤΙΟ (Αισθ. + Λανθ.)',''] + ['']*8
for h in hours:
    row.extend(['','',fmt(H[h]['Q_total'])])
rows.append(row)

row = ['',''] + ['']*8
for h in hours:
    row.extend(['','kW',fmt(H[h]['Q_total']/1000, 2)])
rows.append(row)

# Write worksheet
with open(ws_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"  Φύλλο εργασίας αποθηκεύτηκε: {ws_path}")
print(f"\n{'=' * 90}")
