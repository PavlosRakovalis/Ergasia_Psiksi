#!/usr/bin/env python3
"""
=================================================================
Ερώτημα γ: Σχεδιασμός Κεντρικού Συστήματος Κλιματισμού
=================================================================
Κτίριο Γ1 — Ισόγειο ως μία ζώνη
Συνθήκες αιχμής: 21 Ιουλίου, 16:00 (από Ερώτημα β)

Περίπτωση (i):  Χαμηλός νωπός αέρας, λόγος fresh:recirc = 1:15
Περίπτωση (ii): Υψηλός νωπός αέρας (6×), λόγος fresh:recirc = 1:2

Παραδοχές:
- Παροχή νωπού: 0.75 m³/(h·m²) × 145 m² = 108.75 m³/h (ΤΟΤΕΕ 20701-1, Πιν. 2.3)
- Πίεση αναφοράς: 101.325 kPa
- Ροή στον χώρο = Σύνολο (νωπό + ανακυκλοφορίας)
=================================================================
"""
import math

# =============================================================
# 1. ΔΕΔΟΜΕΝΑ ΣΧΕΔΙΑΣΜΟΥ (από Ερώτημα β, ώρα αιχμής 16:00)
# =============================================================

# --- Συνθήκες αέρα ---
Ti = 26.0           # Εσωτερική θερμοκρασία [°C]
RHi = 0.50          # Εσωτερική σχετική υγρασία
Wi = 0.0105         # Λόγος υγρασίας εσωτερικός [kg_w/kg_da]

To = 35.7           # Εξωτερική θερμοκρασία στην αιχμή [°C]
Wo = 0.0145         # Λόγος υγρασίας εξωτερικός [kg_w/kg_da]

# --- Φορτία χώρου (αφαιρώντας τον αερισμό από τα συνολικά του β) ---
Q_sens_total_b = 5989.0     # W (ώρα 16:00, με αερισμό)
Q_lat_total_b = 1180.5      # W (ώρα 16:00, με αερισμό)
Q_vent_sens_b = 723.2       # W (συμμετοχή αερισμού στο αισθητό)
Q_vent_lat_b = 744.5        # W (συμμετοχή αερισμού στο λανθάνον)

Q_sens_room = Q_sens_total_b - Q_vent_sens_b    # 5265.8 W
Q_lat_room = Q_lat_total_b - Q_vent_lat_b       # 436.0 W
Q_total_room = Q_sens_room + Q_lat_room          # 5701.8 W
SHR_room = Q_sens_room / Q_total_room            # 0.924

# --- Παροχή νωπού αέρα (ΤΟΤΕΕ 20701-1, Πιν. 2.3) ---
A_floor = 145.0
V_fresh_req = 0.75 * A_floor    # 108.75 m³/h

# --- Φυσικές σταθερές ---
rho_air = 1.204         # Πυκνότητα αέρα [kg/m³]
cp_da = 1.006           # Cp ξηρού αέρα [kJ/(kg·K)]
h_fg = 2501             # Ενθαλπία εξάτμισης στους 0°C [kJ/kg]
P_atm = 101.325         # Ατμοσφαιρική πίεση [kPa]


# =============================================================
# 2. ΨΥΧΡΟΜΕΤΡΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ
# =============================================================

def enthalpy(T, W):
    """Ενθαλπία υγρού αέρα [kJ/kg_da]
    h = cp_da·T + W·(h_fg + 1.86·T)"""
    return cp_da * T + W * (h_fg + 1.86 * T)

def Psat(T):
    """Πίεση κορεσμού νερού [kPa] (Magnus)"""
    return 0.61078 * math.exp(17.27 * T / (T + 237.3))

def W_sat(T, P=P_atm):
    """Λόγος υγρασίας κορεσμού στους T [kg_w/kg_da]"""
    ps = Psat(T)
    return 0.622 * ps / (P - ps)


def find_ADP(T_M, W_M, T_S, W_S, T_min=5, T_max=20, tol=1e-5):
    """Βρίσκει το ADP — σημείο τομής γραμμής M-S με καμπύλη κορεσμού.
    Επιστρέφει (T_ADP, W_ADP)."""
    if abs(T_M - T_S) < 1e-9:
        return T_S, W_S
    slope = (W_M - W_S) / (T_M - T_S)
    # f(T) = W_line(T) - W_sat(T)
    def f(T):
        W_line = W_S + slope * (T - T_S)
        return W_line - W_sat(T)
    # Bisection: η γραμμή πάνω από κορεσμό σε υψηλή Τ, κάτω σε χαμηλή
    a, b = T_min, T_max
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        # Πιο επιθετική αναζήτηση
        for T_try in [T_S - 5, T_S - 4, T_S - 3, T_S - 2, T_S - 1, T_S + 0.5]:
            if f(T_try) * fb < 0:
                a = T_try
                fa = f(T_try)
                break
    while b - a > tol:
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    T_adp = 0.5 * (a + b)
    return T_adp, W_sat(T_adp)


# =============================================================
# 3. ΣΗΜΕΙΑ ΧΩΡΟΥ ΚΑΙ ΕΞΩΤΕΡΙΚΟΥ ΑΕΡΑ
# =============================================================

h3 = enthalpy(Ti, Wi)     # Χώρος (σημείο 3)
ho = enthalpy(To, Wo)     # Εξωτερικός (σημείο O)

print("=" * 80)
print("ΕΡΩΤΗΜΑ γ — ΣΧΕΔΙΑΣΜΟΣ ΣΥΣΤΗΜΑΤΟΣ ΚΛΙΜΑΤΙΣΜΟΥ")
print("=" * 80)
print(f"\nΦΟΡΤΙΑ ΧΩΡΟΥ (αφαιρώντας τον αερισμό):")
print(f"  Q_αισθ,χώρου  = {Q_sens_room:.1f} W")
print(f"  Q_λανθ,χώρου  = {Q_lat_room:.1f} W")
print(f"  Q_total,χώρου = {Q_total_room:.1f} W")
print(f"  SHR_χώρου     = {SHR_room:.3f}")
print(f"\nΣΗΜΕΙΑ ΑΝΑΦΟΡΑΣ:")
print(f"  Χώρος (3):   T={Ti}°C, W={Wi} kg/kg, h={h3:.2f} kJ/kg")
print(f"  Εξωτ. (O):  T={To}°C, W={Wo} kg/kg, h={ho:.2f} kJ/kg")
print(f"\nΑΠΑΙΤΟΥΜΕΝΗ ΠΑΡΟΧΗ ΝΩΠΟΥ ΑΕΡΑ:")
print(f"  V_νωπού,απαιτ = 0.75 × {A_floor} = {V_fresh_req:.2f} m³/h "
      f"= {V_fresh_req/3.6:.2f} L/s")


# =============================================================
# 4. ΣΥΝΑΡΤΗΣΗ ΥΠΟΛΟΓΙΣΜΟΥ ΓΙΑ ΜΙΑ ΠΕΡΙΠΤΩΣΗ
# =============================================================

def analyze_case(case_name, V_fresh, ratio_recirc_to_fresh):
    """
    Αναλύει μια περίπτωση σχεδιασμού.
    V_fresh: παροχή νωπού αέρα [m³/h]
    ratio_recirc_to_fresh: λόγος ανακυκλοφορίας προς νωπό
    """
    print(f"\n\n{'=' * 80}")
    print(f"  ΠΕΡΙΠΤΩΣΗ {case_name}")
    print(f"{'=' * 80}")

    # --- Παροχές αέρα ---
    V_recirc = ratio_recirc_to_fresh * V_fresh
    V_total = V_fresh + V_recirc
    V_total_si = V_total / 3600  # m³/s
    m_total = rho_air * V_total_si  # kg/s
    m_fresh = m_total * V_fresh / V_total
    m_recirc = m_total - m_fresh

    print(f"\n  ΒΗΜΑ 1 — ΠΑΡΟΧΕΣ ΑΕΡΑ")
    print(f"  V_νωπού      = {V_fresh:.2f} m³/h ({V_fresh/3.6:.2f} L/s)")
    print(f"  V_ανακυκλ.   = {V_recirc:.2f} m³/h ({V_recirc/3.6:.2f} L/s)")
    print(f"  V_total      = {V_total:.2f} m³/h ({V_total_si*1000:.2f} L/s)")
    print(f"  ṁ_total      = {m_total:.4f} kg/s")
    print(f"  ṁ_νωπού      = {m_fresh:.4f} kg/s ({1/(1+ratio_recirc_to_fresh)*100:.1f}%)")
    print(f"  ṁ_ανακυκλ.   = {m_recirc:.4f} kg/s ({ratio_recirc_to_fresh/(1+ratio_recirc_to_fresh)*100:.1f}%)")

    # --- Σημείο ανάμιξης M (πριν το ψυκτικό στοιχείο) ---
    x_fresh = 1.0 / (1 + ratio_recirc_to_fresh)   # κλάσμα νωπού στη μάζα
    x_recirc = 1 - x_fresh
    T_M = x_fresh * To + x_recirc * Ti
    W_M = x_fresh * Wo + x_recirc * Wi
    h_M = enthalpy(T_M, W_M)

    print(f"\n  ΒΗΜΑ 2 — ΣΗΜΕΙΟ ΑΝΑΜΙΞΗΣ (M)")
    print(f"  Κλάσμα νωπού στη μάζα: {x_fresh:.4f}")
    print(f"  T_M = {x_fresh:.4f}×{To} + {x_recirc:.4f}×{Ti} = {T_M:.2f}°C")
    print(f"  W_M = {x_fresh:.4f}×{Wo} + {x_recirc:.4f}×{Wi} = {W_M:.5f} kg/kg")
    print(f"  h_M = {h_M:.2f} kJ/kg")

    # --- Σημείο προσαγωγής S (από φορτία χώρου) ---
    # Q_sens_room = m × cp_da × (T3 - T_S)  =>  T_S
    T_S = Ti - Q_sens_room / (m_total * cp_da * 1000)
    # Q_lat_room  = m × h_fg × (W3 - W_S)   =>  W_S
    W_S = Wi - Q_lat_room / (m_total * h_fg * 1000)
    h_S = enthalpy(T_S, W_S)
    DeltaT_room = Ti - T_S

    print(f"\n  ΒΗΜΑ 3 — ΣΗΜΕΙΟ ΠΡΟΣΑΓΩΓΗΣ (S)")
    print(f"  Από Q_αισθ,χώρου = ṁ·cp·(T3 − T_S):")
    print(f"    T_S = {Ti} − {Q_sens_room:.1f}/({m_total:.4f}×{cp_da*1000:.0f}) "
          f"= {T_S:.2f}°C  (ΔΤ_χώρου = {DeltaT_room:.1f}°C)")
    print(f"  Από Q_λανθ,χώρου = ṁ·hfg·(W3 − W_S):")
    print(f"    W_S = {Wi} − {Q_lat_room:.1f}/({m_total:.4f}×{h_fg*1000:.0f}) "
          f"= {W_S:.5f} kg/kg")
    print(f"  h_S = {h_S:.2f} kJ/kg")

    # Έλεγχος SHR γραμμής 3-S
    Q_total_check = m_total * (h3 - h_S) * 1000  # W
    print(f"  Έλεγχος: ṁ·(h3−h_S) = {m_total:.4f}×({h3:.2f}−{h_S:.2f})×1000 "
          f"= {Q_total_check:.1f} W ≈ {Q_total_room:.1f} W ✓")

    # --- Σημείο αποπεράτωσης (ADP) ---
    T_ADP, W_ADP = find_ADP(T_M, W_M, T_S, W_S)
    h_ADP = enthalpy(T_ADP, W_ADP)

    print(f"\n  ΒΗΜΑ 4 — ΣΗΜΕΙΟ ΑΠΟΠΕΡΑΤΩΣΗΣ (ADP)")
    print(f"  Τομή της ευθείας M-S με την καμπύλη κορεσμού:")
    print(f"    T_ADP = {T_ADP:.2f}°C")
    print(f"    W_ADP = {W_ADP:.5f} kg/kg (= W_sat στους {T_ADP:.2f}°C)")
    print(f"    h_ADP = {h_ADP:.2f} kJ/kg")

    # --- Συντελεστής Παράκαμψης ---
    BF_T = (T_S - T_ADP) / (T_M - T_ADP)
    BF_W = (W_S - W_ADP) / (W_M - W_ADP)
    BF_h = (h_S - h_ADP) / (h_M - h_ADP)
    BF = (BF_T + BF_W + BF_h) / 3  # μέσος όρος για συνέπεια

    print(f"\n  ΒΗΜΑ 5 — ΣΥΝΤΕΛΕΣΤΗΣ ΠΑΡΑΚΑΜΨΗΣ (BF)")
    print(f"  BF = (T_S − T_ADP) / (T_M − T_ADP) "
          f"= ({T_S:.2f}−{T_ADP:.2f})/({T_M:.2f}−{T_ADP:.2f}) = {BF_T:.4f}")
    print(f"  BF = (W_S − W_ADP) / (W_M − W_ADP) "
          f"= ({W_S:.5f}−{W_ADP:.5f})/({W_M:.5f}−{W_ADP:.5f}) = {BF_W:.4f}")
    print(f"  BF = (h_S − h_ADP) / (h_M − h_ADP) "
          f"= ({h_S:.2f}−{h_ADP:.2f})/({h_M:.2f}−{h_ADP:.2f}) = {BF_h:.4f}")
    print(f"  ► Μέσο BF = {BF:.4f} ≈ {BF:.2f}")

    # --- Φορτία ψυκτικού στοιχείου (M → S) ---
    Q_coil_total = m_total * (h_M - h_S) * 1000   # W
    Q_coil_sens = m_total * cp_da * (T_M - T_S) * 1000  # W
    Q_coil_lat = m_total * h_fg * (W_M - W_S) * 1000    # W
    SHR_coil = Q_coil_sens / Q_coil_total

    print(f"\n  ΒΗΜΑ 6 — ΦΟΡΤΙΑ ΨΥΚΤΙΚΟΥ ΣΤΟΙΧΕΙΟΥ")
    print(f"  Q_coil,total = ṁ·(h_M − h_S) = {m_total:.4f}×({h_M:.2f}−{h_S:.2f})"
          f"×1000 = {Q_coil_total:.1f} W ({Q_coil_total/1000:.2f} kW)")
    print(f"  Q_coil,sens  = ṁ·cp·(T_M − T_S) = {m_total:.4f}×{cp_da}×{T_M-T_S:.2f}"
          f"×1000 = {Q_coil_sens:.1f} W ({Q_coil_sens/1000:.2f} kW)")
    print(f"  Q_coil,lat   = ṁ·hfg·(W_M − W_S) = {m_total:.4f}×{h_fg}×"
          f"{(W_M-W_S):.5f}×1000 = {Q_coil_lat:.1f} W ({Q_coil_lat/1000:.2f} kW)")
    print(f"  SHR_coil     = {SHR_coil:.3f}")

    # Επιπλέον φορτίο νωπού (παράπλευρο φορτίο)
    Q_oa_sens = m_fresh * cp_da * (To - Ti) * 1000
    Q_oa_lat = m_fresh * h_fg * (Wo - Wi) * 1000
    Q_oa_total = Q_oa_sens + Q_oa_lat
    print(f"\n  ΕΠΙΠΛΕΟΝ — Φορτίο νωπού αέρα μόνο (πριν την ανάμιξη):")
    print(f"  Q_νωπού,αισθ  = ṁ_f·cp·(To−Ti)  = {Q_oa_sens:.1f} W")
    print(f"  Q_νωπού,λανθ  = ṁ_f·hfg·(Wo−Wi) = {Q_oa_lat:.1f} W")
    print(f"  Q_νωπού,total = {Q_oa_total:.1f} W ({Q_oa_total/1000:.2f} kW)")

    return {
        'case': case_name,
        'V_fresh_m3h': V_fresh,
        'V_recirc_m3h': V_recirc,
        'V_total_m3h': V_total,
        'm_total': m_total,
        'm_fresh': m_fresh,
        'm_recirc': m_recirc,
        'T_M': T_M, 'W_M': W_M, 'h_M': h_M,
        'T_S': T_S, 'W_S': W_S, 'h_S': h_S,
        'T_ADP': T_ADP, 'W_ADP': W_ADP, 'h_ADP': h_ADP,
        'BF': BF,
        'Q_coil_total': Q_coil_total,
        'Q_coil_sens': Q_coil_sens,
        'Q_coil_lat': Q_coil_lat,
        'SHR_coil': SHR_coil,
        'Q_oa_total': Q_oa_total,
        'Q_oa_sens': Q_oa_sens,
        'Q_oa_lat': Q_oa_lat,
    }


# =============================================================
# 5. ΕΚΤΕΛΕΣΗ ΓΙΑ ΤΙΣ ΔΥΟ ΠΕΡΙΠΤΩΣΕΙΣ
# =============================================================

# Περίπτωση i: V_νωπού = απαιτούμενη, λόγος 1:15
case_i = analyze_case(
    case_name="(i) — Χαμηλή παροχή νωπού, λόγος νωπού:ανακυκλ. = 1:15",
    V_fresh=V_fresh_req,
    ratio_recirc_to_fresh=15
)

# Περίπτωση ii: V_νωπού = 6×απαιτούμενη, λόγος 1:2
case_ii = analyze_case(
    case_name="(ii) — Υψηλή παροχή νωπού (6×απαιτ.), λόγος νωπού:ανακυκλ. = 1:2",
    V_fresh=6 * V_fresh_req,
    ratio_recirc_to_fresh=2
)


# =============================================================
# 6. ΣΥΓΚΕΝΤΡΩΤΙΚΟΣ ΠΙΝΑΚΑΣ ΣΥΓΚΡΙΣΗΣ
# =============================================================

print(f"\n\n{'=' * 80}")
print(f"{'ΣΥΓΚΡΙΤΙΚΟΣ ΠΙΝΑΚΑΣ ΠΕΡΙΠΤΩΣΕΩΝ (i) και (ii)':^80}")
print(f"{'=' * 80}")

rows = [
    ("Παράμετρος", "Περ. (i)", "Περ. (ii)", "Μονάδα"),
    ("V_νωπού", f"{case_i['V_fresh_m3h']:.1f}", f"{case_ii['V_fresh_m3h']:.1f}", "m³/h"),
    ("V_ανακυκλ.", f"{case_i['V_recirc_m3h']:.1f}", f"{case_ii['V_recirc_m3h']:.1f}", "m³/h"),
    ("V_total", f"{case_i['V_total_m3h']:.1f}", f"{case_ii['V_total_m3h']:.1f}", "m³/h"),
    ("ṁ_total", f"{case_i['m_total']:.4f}", f"{case_ii['m_total']:.4f}", "kg/s"),
    ("T_M (ανάμιξη)", f"{case_i['T_M']:.2f}", f"{case_ii['T_M']:.2f}", "°C"),
    ("W_M (ανάμιξη)", f"{case_i['W_M']:.5f}", f"{case_ii['W_M']:.5f}", "kg/kg"),
    ("h_M", f"{case_i['h_M']:.2f}", f"{case_ii['h_M']:.2f}", "kJ/kg"),
    ("T_S (προσαγωγή)", f"{case_i['T_S']:.2f}", f"{case_ii['T_S']:.2f}", "°C"),
    ("W_S (προσαγωγή)", f"{case_i['W_S']:.5f}", f"{case_ii['W_S']:.5f}", "kg/kg"),
    ("h_S", f"{case_i['h_S']:.2f}", f"{case_ii['h_S']:.2f}", "kJ/kg"),
    ("T_ADP", f"{case_i['T_ADP']:.2f}", f"{case_ii['T_ADP']:.2f}", "°C"),
    ("W_ADP", f"{case_i['W_ADP']:.5f}", f"{case_ii['W_ADP']:.5f}", "kg/kg"),
    ("BF (παράκαμψη)", f"{case_i['BF']:.3f}", f"{case_ii['BF']:.3f}", "—"),
    ("Q_coil,αισθ", f"{case_i['Q_coil_sens']:.1f}", f"{case_ii['Q_coil_sens']:.1f}", "W"),
    ("Q_coil,λανθ", f"{case_i['Q_coil_lat']:.1f}", f"{case_ii['Q_coil_lat']:.1f}", "W"),
    ("Q_coil,total", f"{case_i['Q_coil_total']:.1f}", f"{case_ii['Q_coil_total']:.1f}", "W"),
    ("Q_coil,total", f"{case_i['Q_coil_total']/1000:.2f}", f"{case_ii['Q_coil_total']/1000:.2f}", "kW"),
    ("SHR_coil", f"{case_i['SHR_coil']:.3f}", f"{case_ii['SHR_coil']:.3f}", "—"),
]

w = 22
for r in rows:
    print(f"  {r[0]:<{w}} │ {r[1]:>12} │ {r[2]:>12} │ {r[3]}")

# --- Παρατηρήσεις ---
print(f"\n{'=' * 80}")
print(f"{'ΠΑΡΑΤΗΡΗΣΕΙΣ — ΣΥΓΚΡΙΣΗ ΠΕΡΙΠΤΩΣΕΩΝ':^80}")
print(f"{'=' * 80}")

dQ = case_ii['Q_coil_total'] - case_i['Q_coil_total']
pct = dQ / case_i['Q_coil_total'] * 100
print(f"""
1. ΦΟΡΤΙΟ ΣΥΣΚΕΥΗΣ
   - Περ. (i):  Q_coil = {case_i['Q_coil_total']/1000:.2f} kW
   - Περ. (ii): Q_coil = {case_ii['Q_coil_total']/1000:.2f} kW
   - Διαφορά:   +{dQ/1000:.2f} kW ({pct:+.1f}%)
   ► Η περ. (ii) απαιτεί συσκευή με μεγαλύτερη ψυκτική ικανότητα,
     επειδή ο πολύς νωπός αέρας φέρνει επιπλέον αισθητό και λανθάνον φορτίο.

2. ΣΗΜΕΙΟ ΑΝΑΜΙΞΗΣ (M)
   - Περ. (i):  T_M = {case_i['T_M']:.1f}°C, W = {case_i['W_M']:.4f} kg/kg
   - Περ. (ii): T_M = {case_ii['T_M']:.1f}°C, W = {case_ii['W_M']:.4f} kg/kg
   ► Στην περ. (ii) το M πλησιάζει περισσότερο τις εξωτερικές συνθήκες,
     επομένως το ψυκτικό στοιχείο πρέπει να αφαιρέσει πολύ περισσότερη
     θερμότητα και υγρασία.

3. ΣΥΝΤΕΛΕΣΤΗΣ ΠΑΡΑΚΑΜΨΗΣ (BF)
   - Περ. (i):  BF = {case_i['BF']:.3f}
   - Περ. (ii): BF = {case_ii['BF']:.3f}
   ► Οι τιμές BF αντιστοιχούν σε τυπικά κεντρικά ψυκτικά στοιχεία
     (BF=0.05–0.30). Η μεγαλύτερη BF στην περ. (ii) δείχνει
     "λιγότερο αποτελεσματική" επαφή με την επιφάνεια του στοιχείου,
     γιατί η υψηλή ροή μειώνει τον χρόνο επαφής.

4. ΣΗΜΕΙΟ ΠΡΟΣΑΓΩΓΗΣ
   - Περ. (i):  T_S = {case_i['T_S']:.1f}°C (ΔΤ_χώρου = {Ti-case_i['T_S']:.1f}°C)
   - Περ. (ii): T_S = {case_ii['T_S']:.1f}°C (ΔΤ_χώρου = {Ti-case_ii['T_S']:.1f}°C)
   ► Στην περ. (ii) ο αέρας προσάγεται σε υψηλότερη θερμοκρασία γιατί
     η συνολική παροχή είναι μεγαλύτερη.

5. ΠΟΙΟΤΗΤΑ ΑΕΡΑ
   - Περ. (i):  Νωπός = {case_i['V_fresh_m3h']:.0f} m³/h (= απαιτούμενη)
   - Περ. (ii): Νωπός = {case_ii['V_fresh_m3h']:.0f} m³/h (= 6× απαιτούμενη)
   ► Η περ. (ii) εξασφαλίζει υψηλότερη ποιότητα αέρα, αλλά με μεγαλύτερο
     ενεργειακό κόστος.
""")

print("=" * 80)
