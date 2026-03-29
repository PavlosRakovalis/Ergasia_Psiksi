"""
ΚΤΙΡΙΟ Γ1 - ΚΑΤΟΨΗ ΙΣΟΓΕΙΟΥ
Professional architectural floor plan — Python + Matplotlib
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# =========================================================================
#  COLOUR PALETTE & STYLE CONSTANTS
# =========================================================================
BG_COLOR      = "#FFFFFF"
FLOOR_COLOR   = "#F7F5F0"      # ελαφρύ μπεζ δάπεδο
WALL_COLOR    = "#1A1A1A"       # σχεδόν μαύρο
HATCH_FILL    = "#D6D2CA"       # γεμισμα hatching
HATCH_LINE    = "#4A4A4A"       # γραμμές hatching
WINDOW_COLOR  = "#2B7ABA"       # μπλε παράθυρα
DOOR_COLOR    = "#2D8E57"       # πράσινο πόρτες
FURN_FILL     = "#EAE7E0"       # γέμισμα επίπλων
FURN_EDGE     = "#666666"       # περίγραμμα επίπλων
TEXT_COLOR     = "#1A1A1A"
DIM_COLOR      = "#888888"
GRID_COLOR     = "#E8E8E8"
EXTERIOR_HATCH = "#E0DDD5"
TITLE_COLOR    = "#2C2C2C"

EXT_LW   = 3.5     # εξωτερικός τοίχος
INT_LW   = 2.2     # εσωτερικός τοίχος
WIN_LW   = 1.8     # παράθυρα
DOOR_LW  = 1.0     # πόρτες
FURN_LW  = 0.7     # έπιπλα
DASH_LW  = 0.6     # dashed


def draw_floor_plan():
    fig, ax = plt.subplots(figsize=(13, 17))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # =====================================================================
    #  ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ
    # =====================================================================
    def draw_wall_thick(x1, y1, x2, y2, thickness, lw=EXT_LW):
        """Τοίχος ως γεμάτο ορθογώνιο με hatching."""
        dx, dy = x2 - x1, y2 - y1
        L = np.hypot(dx, dy)
        if L < 1e-6:
            return
        nx, ny = -dy / L * thickness / 2, dx / L * thickness / 2
        corners_x = [x1 + nx, x2 + nx, x2 - nx, x1 - nx, x1 + nx]
        corners_y = [y1 + ny, y2 + ny, y2 - ny, y1 - ny, y1 + ny]
        ax.fill(corners_x, corners_y, color=HATCH_FILL, zorder=2)
        # Διαγώνιες γραμμές hatching
        n_lines = max(int(L / 0.25), 3)
        for i in range(n_lines + 1):
            t = i / n_lines
            px, py = x1 + t * dx, y1 + t * dy
            ax.plot([px + nx, px - nx], [py + ny, py - ny],
                    color=HATCH_LINE, linewidth=0.35, zorder=3)
        # Περίγραμμα
        ax.plot(corners_x, corners_y, color=WALL_COLOR, linewidth=lw,
                solid_capstyle='projecting', zorder=4)

    def draw_wall_rect(x, y, w, h, lw=EXT_LW):
        """Τοίχος ως ορθογώνιο (για κάθετες/οριζόντιες τοποθετήσεις)."""
        ax.add_patch(patches.Rectangle(
            (x, y), w, h, facecolor=HATCH_FILL,
            edgecolor=WALL_COLOR, linewidth=lw, zorder=2))
        # Hatching γραμμές (45°)
        if w > h:  # οριζόντιος
            step = 0.22
            cx = x
            while cx <= x + w:
                y0c = max(y, y)
                y1c = min(y + h, y + h)
                ax.plot([cx, cx + h], [y0c, y1c],
                        color=HATCH_LINE, linewidth=0.35, zorder=3,
                        clip_on=True)
                cx += step
        else:  # κάθετος
            step = 0.22
            cy = y
            while cy <= y + h:
                ax.plot([x, x + w], [cy, cy + w],
                        color=HATCH_LINE, linewidth=0.35, zorder=3,
                        clip_on=True)
                cy += step

    def window(x1, y1, x2, y2, wall_t=0.30):
        """Αρχιτεκτονικό σύμβολο παραθύρου: κενό στον τοίχο + διπλή γραμμή γυαλιού."""
        dx, dy = x2 - x1, y2 - y1
        L = np.hypot(dx, dy)
        if L < 1e-6:
            return
        nx, ny = -dy / L, dx / L
        off = wall_t / 2
        # Λευκό γέμισμα (σβήνει τον τοίχο)
        cx = [x1 + nx * off, x2 + nx * off, x2 - nx * off, x1 - nx * off]
        cy = [y1 + ny * off, y2 + ny * off, y2 - ny * off, y1 - ny * off]
        ax.fill(cx, cy, color=BG_COLOR, zorder=5)
        # Δύο παράλληλες γραμμές γυαλιού
        g = wall_t * 0.15
        for sign in [1, -1]:
            gx, gy = nx * g * sign, ny * g * sign
            ax.plot([x1 + gx, x2 + gx], [y1 + gy, y2 + gy],
                    color=WINDOW_COLOR, linewidth=WIN_LW, zorder=6,
                    solid_capstyle='round')
        # Ακραίες γραμμές τοίχου
        for sign in [1, -1]:
            ox, oy = nx * off * sign, ny * off * sign
            ax.plot([x1 + ox, x1 + ox * 0.0], [y1 + oy, y1 + oy * 0.0],
                    color=WALL_COLOR, linewidth=1.0, zorder=6)
            ax.plot([x2 + ox, x2 + ox * 0.0], [y2 + oy, y2 + oy * 0.0],
                    color=WALL_COLOR, linewidth=1.0, zorder=6)

    def door(cx, cy, radius, start_deg, end_deg):
        """Πόρτα: λεπτή γραμμή φύλλου + τόξο ανοίγματος."""
        theta = np.linspace(np.radians(start_deg), np.radians(end_deg), 80)
        xs = cx + radius * np.cos(theta)
        ys = cy + radius * np.sin(theta)
        # Τόξο (dashed, λεπτό)
        ax.plot(xs, ys, color=DOOR_COLOR, linewidth=DOOR_LW,
                linestyle=(0, (4, 3)), zorder=7)
        # Φύλλο πόρτας
        ax.plot([cx, xs[-1]], [cy, ys[-1]], color=DOOR_COLOR,
                linewidth=DOOR_LW * 1.8, solid_capstyle='round', zorder=7)

    def swing_thetas(angle_from, angle_to, steps=60):
        a0 = np.radians(angle_from)
        delta = (np.radians(angle_to - angle_from) + np.pi) % (2 * np.pi) - np.pi
        return np.linspace(a0, a0 + delta, steps)

    def draw_swing_arc(cx, cy, radius, angle_from, angle_to,
                       color=DOOR_COLOR, lw=DOOR_LW):
        theta = swing_thetas(angle_from, angle_to)
        ax.plot(cx + radius * np.cos(theta), cy + radius * np.sin(theta),
                color=color, linewidth=lw, linestyle=(0, (4, 3)), zorder=7)

    def balcony_door(x1, y1, x2, y2, wall_t=0.30, swing_dir=1):
        dx, dy = x2 - x1, y2 - y1
        L = np.hypot(dx, dy)
        if L < 1e-6:
            return

        nx, ny = -dy / L, dx / L
        off = wall_t / 2

        cx = [x1 + nx * off, x2 + nx * off, x2 - nx * off, x1 - nx * off]
        cy = [y1 + ny * off, y2 + ny * off, y2 - ny * off, y1 - ny * off]
        ax.fill(cx, cy, color=BG_COLOR, zorder=5)

        g = wall_t * 0.18
        for sign in [1, -1]:
            gx, gy = nx * g * sign, ny * g * sign
            ax.plot([x1 + gx, x2 + gx], [y1 + gy, y2 + gy],
                    color=WINDOW_COLOR, linewidth=WIN_LW, zorder=6,
                    solid_capstyle='round')

        for px, py in [(x1, y1), (x2, y2)]:
            ax.plot([px + nx * off, px - nx * off], [py + ny * off, py - ny * off],
                    color=WALL_COLOR, linewidth=1.0, zorder=6)

        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([mx + nx * off * 0.9, mx - nx * off * 0.9],
                [my + ny * off * 0.9, my - ny * off * 0.9],
                color=WINDOW_COLOR, linewidth=1.0, zorder=6)

        panel_r = L / 2
        inward_x, inward_y = nx * swing_dir * panel_r, ny * swing_dir * panel_r
        leaf_ends = [
            (x1 + inward_x, y1 + inward_y),
            (x2 + inward_x, y2 + inward_y),
        ]

        for (px, py), (lx, ly) in zip([(x1, y1), (x2, y2)], leaf_ends):
            ax.plot([px, lx], [py, ly], color=DOOR_COLOR,
                    linewidth=DOOR_LW * 1.8, solid_capstyle='round', zorder=7)

        first_closed = np.degrees(np.arctan2(my - y1, mx - x1))
        second_closed = np.degrees(np.arctan2(my - y2, mx - x2))
        open_angle = np.degrees(np.arctan2(inward_y, inward_x))

        draw_swing_arc(x1, y1, panel_r, first_closed, open_angle)
        draw_swing_arc(x2, y2, panel_r, second_closed, open_angle)

    def door(cx, cy, radius, open_deg, closed_deg, wall_t=0.20):
        closed_rad = np.radians(closed_deg)
        open_rad = np.radians(open_deg)

        closed_x = cx + radius * np.cos(closed_rad)
        closed_y = cy + radius * np.sin(closed_rad)
        open_x = cx + radius * np.cos(open_rad)
        open_y = cy + radius * np.sin(open_rad)

        seg_dx, seg_dy = closed_x - cx, closed_y - cy
        seg_len = np.hypot(seg_dx, seg_dy)
        if seg_len < 1e-6:
            return

        nx, ny = -seg_dy / seg_len, seg_dx / seg_len
        clear = wall_t / 2 + 0.03
        ax.fill(
            [cx + nx * clear, closed_x + nx * clear, closed_x - nx * clear, cx - nx * clear],
            [cy + ny * clear, closed_y + ny * clear, closed_y - ny * clear, cy - ny * clear],
            color=BG_COLOR, zorder=6
        )

        ax.plot([cx + nx * clear, cx - nx * clear], [cy + ny * clear, cy - ny * clear],
                color=WALL_COLOR, linewidth=1.0, zorder=6.5)
        ax.plot([closed_x + nx * clear, closed_x - nx * clear],
                [closed_y + ny * clear, closed_y - ny * clear],
                color=WALL_COLOR, linewidth=1.0, zorder=6.5)

        theta = swing_thetas(closed_deg, open_deg)
        ax.fill(
            np.concatenate(([cx], cx + (radius + 0.04) * np.cos(theta), [cx])),
            np.concatenate(([cy], cy + (radius + 0.04) * np.sin(theta), [cy])),
            color=BG_COLOR, zorder=6.7
        )
        draw_swing_arc(cx, cy, radius, closed_deg, open_deg)
        ax.plot([cx, open_x], [cy, open_y], color=DOOR_COLOR,
                linewidth=DOOR_LW * 2.2, solid_capstyle='round', zorder=8)
        ax.add_patch(patches.Circle((cx, cy), 0.035, facecolor=DOOR_COLOR,
                     edgecolor='none', zorder=8))

    def furniture_rect(x, y, w, h, rounded=False, fill=FURN_FILL):
        """Έπιπλο ορθογώνιο."""
        if rounded:
            ax.add_patch(FancyBboxPatch(
                (x, y), w, h, boxstyle='round,pad=0.04',
                facecolor=fill, edgecolor=FURN_EDGE,
                linewidth=FURN_LW, zorder=6))
        else:
            ax.add_patch(patches.Rectangle(
                (x, y), w, h, facecolor=fill, edgecolor=FURN_EDGE,
                linewidth=FURN_LW, zorder=6))

    def label(x, y, text, fs=12, bold=True):
        ax.text(x, y, text, fontsize=fs, ha='center', va='center',
                fontweight='bold' if bold else 'normal', color=TEXT_COLOR,
                fontfamily='sans-serif', zorder=10)

    def dim_label(x, y, text, fs=7):
        ax.text(x, y, text, fontsize=fs, ha='center', va='center',
                color=DIM_COLOR, fontfamily='sans-serif',
                fontstyle='italic', zorder=10)

    def win_label(x, y, text, fs=8):
        ax.text(x, y, text, fontsize=fs, ha='center', va='center',
                color=WINDOW_COLOR, fontfamily='sans-serif',
                fontweight='bold', zorder=10)

    def format_dim(value):
        return f"{value:.2f} m"

    def draw_dimension(x1, y1, x2, y2, offset=0.0, text=None, color=DIM_COLOR,
                       fs=7, text_offset=0.12, lw=0.85, arrow_scale=10):
        """Draw a simple architectural dimension line parallel to the segment."""
        dx, dy = x2 - x1, y2 - y1
        length = np.hypot(dx, dy)
        if length < 1e-6:
            return

        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux

        px1, py1 = x1 + nx * offset, y1 + ny * offset
        px2, py2 = x2 + nx * offset, y2 + ny * offset

        ax.plot([x1, px1], [y1, py1], color=color, linewidth=lw,
                zorder=8, clip_on=False)
        ax.plot([x2, px2], [y2, py2], color=color, linewidth=lw,
                zorder=8, clip_on=False)
        ax.annotate(
            '', xy=(px2, py2), xytext=(px1, py1),
            arrowprops=dict(
                arrowstyle='<->', color=color, lw=lw,
                shrinkA=0, shrinkB=0, mutation_scale=arrow_scale
            ),
            zorder=8
        )

        if text is None:
            text = format_dim(length)

        rotation = np.degrees(np.arctan2(dy, dx))
        if rotation > 90:
            rotation -= 180
        if rotation < -90:
            rotation += 180

        ax.text(
            (px1 + px2) / 2 + nx * text_offset,
            (py1 + py2) / 2 + ny * text_offset,
            text,
            fontsize=fs, ha='center', va='center',
            rotation=rotation, rotation_mode='anchor',
            color=color, fontfamily='sans-serif',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=BG_COLOR,
                      edgecolor='none', alpha=0.95),
            zorder=11, clip_on=False
        )

    # =====================================================================
    #  ΔΑΠΕΔΟ
    # =====================================================================
    ax.add_patch(patches.Rectangle(
        (0, 0), 10, 14.5, facecolor=FLOOR_COLOR, edgecolor='none', zorder=1))

    # =====================================================================
    #  ΕΞΩΤΕΡΙΚΟΙ ΤΟΙΧΟΙ  (πάχος 0.30 m)
    # =====================================================================
    wt = 0.30  # πάχος εξωτερικού τοίχου

    # Κάτω τοίχος
    draw_wall_rect(0, -wt / 2, 10, wt, lw=EXT_LW)
    # Πάνω τοίχος
    draw_wall_rect(0, 14.5 - wt / 2, 10, wt, lw=EXT_LW)
    # Αριστερός τοίχος
    draw_wall_rect(-wt / 2, 0, wt, 14.5, lw=EXT_LW)
    # Δεξιός τοίχος
    draw_wall_rect(10 - wt / 2, 0, wt, 14.5, lw=EXT_LW)

    # =====================================================================
    #  ΕΣΩΤΕΡΙΚΟΙ ΤΟΙΧΟΙ  (πάχος 0.20 m)
    # =====================================================================
    iwt = 0.20

    # Οριζόντιος: ΚΑΘΙΣΤΙΚΟ / κάτω χώροι  y = 8.5
    draw_wall_rect(0, 8.5 - iwt / 2, 10, iwt, lw=INT_LW)

    # Κάθετος: ΤΡΑΠΕΖΑΡΙΑ-ΚΟΥΖΙΝΑ / δεξιοί χώροι  x = 5.5
    draw_wall_rect(5.5 - iwt / 2, 0, iwt, 8.5, lw=INT_LW)

    # Οριζόντιος: ΤΡΑΠΕΖΑΡΙΑ / ΚΟΥΖΙΝΑ  y = 4.2
    draw_wall_rect(0, 4.2 - iwt / 2, 5.5, iwt, lw=INT_LW)

    # Τοίχοι WC
    draw_wall_rect(7.2 - iwt / 2, 0, iwt, 3.8, lw=INT_LW)
    draw_wall_rect(7.2, 3.8 - iwt / 2, 2.8, iwt, lw=INT_LW)

    # =====================================================================
    #  ΠΑΡΑΘΥΡΑ
    # =====================================================================
    # Πάνω τοίχος — ΚΑΘΙΣΤΙΚΟ
    top_windows = [
        (1.5, 14.5, 4.0, 14.5),
        (5.5, 14.5, 8.5, 14.5),
    ]
    for x1, y1, x2, y2 in top_windows:
        window(x1, y1, x2, y2, wall_t=wt)

    kitchen_windows = [
        (1.8, 0, 3.6, 0),
    ]
    for x1, y1, x2, y2 in kitchen_windows:
        window(x1, y1, x2, y2, wall_t=wt)

    living_balcony_doors = [
        (10, 12.35, 10, 9.20, -1),
    ]
    for x1, y1, x2, y2, swing_dir in living_balcony_doors:
        balcony_door(x1, y1, x2, y2, wall_t=wt, swing_dir=swing_dir)

    dining_balcony_doors = [
        (0, 7.10, 0, 5.35, 1),
    ]
    for x1, y1, x2, y2, swing_dir in dining_balcony_doors:
        balcony_door(x1, y1, x2, y2, wall_t=wt, swing_dir=swing_dir)

    # =====================================================================
    #  ΠΟΡΤΕΣ
    # =====================================================================
    door(7.5, 8.5, 1.0, 270, 180, wall_t=iwt)   # ΚΑΘΙΣΤΙΚΟ → ΧΩΛ
    door(3.9, 8.5, 0.95, 90, 0, wall_t=iwt)     # ΤΡΑΠΕΖΑΡΙΑ → ΚΑΘΙΣΤΙΚΟ
    door(5.5, 6.0, 0.9, 0, 90, wall_t=iwt)      # ΤΡΑΠΕΖΑΡΙΑ → ΧΩΛ
    door(1.5, 4.2, 0.85, 270, 0, wall_t=iwt)    # ΤΡΑΠΕΖΑΡΙΑ → ΚΟΥΖΙΝΑ
    door(8.85, 3.8, 0.75, 90, 180, wall_t=iwt)  # ΧΩΛ → WC
    door(5.95, 0, 0.95, 90, 0, wall_t=wt)       # Εξώπορτα ΧΩΛ

    # =====================================================================
    #  ΕΞΟΠΛΙΣΜΟΣ / ΕΠΙΠΛΑ
    # =====================================================================
    # --- ΚΟΥΖΙΝΑ ---
    # Πάγκος κουζίνας (L-shape)
    furniture_rect(0.35, 0.35, 4.5, 0.75)
    furniture_rect(0.35, 0.35, 0.75, 2.8)
    # Νεροχύτης
    furniture_rect(2.2, 0.45, 1.0, 0.55, rounded=True, fill='#D4E9F7')
    # Εστίες (4 κύκλοι)
    for dx, dy in [(3.6, 0.55), (4.1, 0.55), (3.6, 0.9), (4.1, 0.9)]:
        ax.add_patch(patches.Circle((dx, dy), 0.12,
                     facecolor='#E8E0D8', edgecolor=FURN_EDGE,
                     linewidth=0.5, zorder=6))

    # --- ΤΡΑΠΕΖΑΡΙΑ ---
    # Τραπέζι
    furniture_rect(1.5, 5.5, 2.5, 1.5, rounded=True)
    # Καρέκλες (6)
    chair_positions = [
        (1.8, 5.2), (2.5, 5.2), (3.2, 5.2),   # κάτω
        (1.8, 7.15), (2.5, 7.15), (3.2, 7.15), # πάνω
    ]
    for cx, cy in chair_positions:
        ax.add_patch(patches.FancyBboxPatch(
            (cx - 0.15, cy - 0.10), 0.30, 0.20,
            boxstyle='round,pad=0.03', facecolor='#E0DCD4',
            edgecolor=FURN_EDGE, linewidth=0.4, zorder=6))

    # --- ΚΑΘΙΣΤΙΚΟ ---
    # Καναπές (L-shape)
    furniture_rect(1.0, 9.5, 3.5, 1.0, rounded=True)
    furniture_rect(1.0, 10.5, 1.0, 1.8, rounded=True)
    # Τραπεζάκι σαλονιού
    furniture_rect(2.8, 10.0, 1.5, 0.8, rounded=True, fill='#DDD8CE')

    # --- WC ---
    # Λεκάνη
    furniture_rect(8.6, 0.5, 0.55, 0.75)
    ax.add_patch(patches.Ellipse(
        (8.875, 0.7), 0.40, 0.30,
        facecolor='#D4E9F7', edgecolor=FURN_EDGE,
        linewidth=0.5, zorder=7))
    # Καζανάκι
    furniture_rect(8.65, 1.25, 0.45, 0.20, fill='#DDD')
    # Νιπτήρας
    furniture_rect(8.3, 2.4, 0.65, 0.50, rounded=True, fill='#D4E9F7')
    # Μπανιέρα / ντουζιέρα
    furniture_rect(7.5, 0.4, 0.85, 1.5, rounded=True, fill='#DFE8ED')

    # =====================================================================
    #  ΕΞΩΤΕΡΙΚΟΙ ΧΩΡΟΙ (στικτό pattern)
    # =====================================================================
    for ext_x, ext_w in [(-2.5, 2.2), (10.3, 2.2)]:
        ax.add_patch(patches.Rectangle(
            (ext_x, -0.5), ext_w, 15.5,
            facecolor=EXTERIOR_HATCH, edgecolor='none', zorder=0))
        # Στικτό pattern
        ny, nx_p = 40, 6
        for iy in range(ny):
            for ix in range(nx_p):
                px = ext_x + 0.35 + ix * (ext_w / nx_p)
                py = -0.3 + iy * (15.5 / ny)
                ax.plot(px, py, '.', color='#C0BDB5', markersize=1.2, zorder=0)

    # =====================================================================
    #  DASHED ΓΡΑΜΜΕΣ (προεξοχές κτηρίου)
    # =====================================================================
    dash_style = dict(color='#999999', linewidth=DASH_LW,
                      linestyle=(0, (6, 4)), zorder=1)
    ax.plot([0, -2.0], [8.5, 8.5], **dash_style)
    ax.plot([10, 12.0], [8.5, 8.5], **dash_style)
    ax.plot([0, -2.0], [4.2, 4.2], **{**dash_style, 'linestyle': 'dashdot'})
    ax.plot([10, 12.0], [3.8, 3.8], **{**dash_style, 'linestyle': 'dashdot'})
    ax.plot([-0.4, -0.4], [-0.5, 15.0], **dash_style)
    ax.plot([10.4, 10.4], [-0.5, 15.0], **dash_style)

    # =====================================================================
    #  ΔΙΑΣΤΑΣΕΙΣ ΤΟΙΧΩΝ / ΠΑΡΑΘΥΡΩΝ
    # =====================================================================
    # Συνολικές εξωτερικές διαστάσεις
    draw_dimension(0, 14.5, 10, 14.5, offset=1.10, text=format_dim(10.0), fs=8)
    draw_dimension(0, 0, 0, 14.5, offset=1.15, text=format_dim(14.5), fs=8)

    # Βασικές εσωτερικές διαστάσεις τοίχων
    draw_dimension(5.5, 0, 5.5, 8.5, offset=-0.65, text=format_dim(8.5), fs=7)
    draw_dimension(0, 4.2, 5.5, 4.2, offset=0.55, text=format_dim(5.5), fs=7)
    draw_dimension(7.2, 0, 7.2, 3.8, offset=-0.40, text=format_dim(3.8), fs=6.8)
    draw_dimension(7.2, 3.8, 10, 3.8, offset=-0.45, text=format_dim(2.8), fs=6.8)

    # Διαστάσεις ανοιγμάτων παραθύρων
    for x1, y1, x2, y2 in top_windows:
        draw_dimension(x1, y1, x2, y2, offset=0.55, color=WINDOW_COLOR,
                       fs=6.5, text_offset=0.10, arrow_scale=9)

    for x1, y1, x2, y2 in kitchen_windows:
        draw_dimension(x1, y1, x2, y2, offset=-0.65, color=WINDOW_COLOR,
                       fs=6.0, text_offset=0.10, arrow_scale=8)

    for x1, y1, x2, y2, _ in living_balcony_doors:
        draw_dimension(x1, y1, x2, y2, offset=-0.72, color=DOOR_COLOR,
                       fs=6.0, text_offset=0.10, arrow_scale=8)

    for x1, y1, x2, y2, _ in dining_balcony_doors:
        draw_dimension(x1, y1, x2, y2, offset=0.72, color=DOOR_COLOR,
                       fs=6.0, text_offset=0.10, arrow_scale=8)

    # =====================================================================
    #  ΟΝΟΜΑΣΙΕΣ ΧΩΡΩΝ
    # =====================================================================
    label(4.5, 12.8, 'ΚΑΘΙΣΤΙΚΟ', fs=14)
    dim_label(4.5, 12.0, '10λΣ χώρου < Σ.ανοιγ. = 2.90m² < 8.16m²', fs=7)

    label(2.8, 6.8, 'ΤΡΑΠΕΖΑΡΙΑ', fs=13)
    dim_label(2.8, 6.1, '10λΣ χώρου < Σ.ανοιγ. = 3.10m² < 3.84m²', fs=7)

    label(3.0, 2.5, 'ΚΟΥΖΙΝΑ', fs=13)

    label(8.5, 3.0, 'WC', fs=13)

    # Ονομασία δεξιού χώρου (πρώην σκάλες, τώρα ανοιχτός χώρος)
    label(7.7, 6.5, 'ΧΩΛ', fs=11, bold=False)

    # =====================================================================
    #  ΤΙΤΛΟΣ (κάτω, επαγγελματικό πλαίσιο)
    # =====================================================================
    # Γραμμή πλαισίου
    ax.plot([-2, 12], [-2.0, -2.0], color=TITLE_COLOR, linewidth=1.5, zorder=10)
    ax.plot([-2, 12], [-3.5, -3.5], color=TITLE_COLOR, linewidth=1.5, zorder=10)
    ax.plot([-2, -2], [-2.0, -3.5], color=TITLE_COLOR, linewidth=1.5, zorder=10)
    ax.plot([12, 12], [-2.0, -3.5], color=TITLE_COLOR, linewidth=1.5, zorder=10)
    ax.add_patch(patches.Rectangle(
        (-2, -3.5), 14, 1.5, facecolor='#FAFAF8', edgecolor=TITLE_COLOR,
        linewidth=1.5, zorder=9))

    ax.text(5, -2.5, 'ΚΤΙΡΙΟ Γ1 — ΚΑΤΟΨΗ ΙΣΟΓΕΙΟΥ',
            fontsize=16, ha='center', va='center', fontweight='bold',
            color=TITLE_COLOR, fontfamily='sans-serif', zorder=10)
    ax.text(5, -3.1, 'Κλίμακα: 1:100  |  Διαστάσεις σε μέτρα',
            fontsize=8, ha='center', va='center',
            color=DIM_COLOR, fontfamily='sans-serif', zorder=10)

    # =====================================================================
    #  ΒΟΡΡΑΣ (σύμβολο)
    # =====================================================================
    nx0, ny0 = 11.2, 13.5
    ax.annotate('', xy=(nx0, ny0 + 1.0), xytext=(nx0, ny0),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=TEXT_COLOR),
                zorder=10)
    ax.text(nx0, ny0 + 1.2, 'Β', fontsize=10, ha='center', va='bottom',
            fontweight='bold', color=TEXT_COLOR, zorder=10)

    # =====================================================================
    #  ΡΥΘΜΙΣΕΙΣ ΑΞΟΝΩΝ
    # =====================================================================
    ax.set_xlim(-3, 13)
    ax.set_ylim(-4, 16.8)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout(pad=0.5)
    plt.savefig('floor_plan_G1.png', dpi=250, bbox_inches='tight', facecolor=BG_COLOR)
    plt.savefig('floor_plan_G1.svg', bbox_inches='tight', facecolor=BG_COLOR)
    print("Saved: floor_plan_G1.png & floor_plan_G1.svg")


if __name__ == '__main__':
    draw_floor_plan()
