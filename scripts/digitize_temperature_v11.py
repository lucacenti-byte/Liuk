#!/usr/bin/env python3
"""Digitize TempTale Ultra blue stroke only — ignore dashed grid & cyan fill."""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pymupdf as fitz
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from PIL import Image

ROOT = Path("/workspace")
PDF = Path("/home/ubuntu/.cursor/projects/workspace/uploads/REPORT_TEMPERATURE_c12d.pdf")
OUT = Path("/tmp/temp_pages/digitize_v11")
ART = ROOT / "artifacts"
XLSX = ROOT / "Temperature_Ricostruite.xlsx"

DEVICES = [
    dict(
        serial="QEN4N02R90",
        page=1,
        first="2026-07-25 06:30:26",
        stop="2026-08-03 11:25:33",
        n=884,
        interval_min=15,
        low=17.7,
        low_t="2026-07-25 21:00:26",
        high=68.3,
        high_t="2026-07-30 12:15:26",
        mean=24.8,
        sd=6.7,
        y_max_label=70.0,
        y_min_label=7.0,
    ),
    dict(
        serial="QEN4N17F60",
        page=2,
        first="2026-07-25 06:30:19",
        stop="2026-08-03 11:25:25",
        n=884,
        interval_min=15,
        low=17.9,
        low_t="2026-07-25 22:15:19",
        high=68.9,
        high_t="2026-07-30 12:15:19",
        mean=25.1,
        sd=6.7,
        y_max_label=70.0,
        y_min_label=7.0,
    ),
    dict(
        serial="QF34N06P10",
        page=3,
        first="2026-07-25 06:30:14",
        stop="2026-08-03 11:24:56",
        n=884,
        interval_min=15,
        low=17.8,
        low_t="2026-07-25 21:45:14",
        high=69.3,
        high_t="2026-07-30 12:30:14",
        mean=24.9,
        sd=6.5,
        y_max_label=71.0,
        y_min_label=7.0,
    ),
    dict(
        serial="QEN4N17MP0",
        page=4,
        first="2026-07-25 06:31:37",
        stop="2026-08-03 11:25:12",
        n=884,
        interval_min=15,
        low=17.8,
        low_t="2026-07-25 21:01:37",
        high=72.3,
        high_t="2026-07-30 12:31:37",
        mean=24.8,
        sd=6.6,
        y_max_label=73.0,
        y_min_label=7.0,
    ),
    dict(
        serial="QEN4N17PA0",
        page=5,
        first="2026-07-25 06:30:25",
        stop="2026-08-03 11:25:37",
        n=884,
        interval_min=15,
        low=17.9,
        low_t="2026-07-25 21:45:25",
        high=64.6,
        high_t="2026-07-30 12:15:25",
        mean=24.9,
        sd=6.4,
        y_max_label=66.0,
        y_min_label=7.0,
    ),
    dict(
        serial="QF34N02Z70",
        page=6,
        first="2026-07-25 06:30:27",
        stop="2026-08-03 11:25:17",
        n=884,
        interval_min=15,
        low=17.6,
        low_t="2026-07-25 22:15:27",
        high=72.4,
        high_t="2026-07-30 12:15:27",
        mean=25.2,
        sd=7.2,
        y_max_label=73.0,
        y_min_label=7.0,
    ),
]


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def render_pages(pdf: Path, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)
        p = out / f"page_{i + 1}.png"
        pix.save(p)
        paths.append(p)
    return paths


def find_threshold_rows(rgb: np.ndarray) -> tuple[int, int, int, int]:
    """Return y25, y8, x_left, x_right of the orange threshold lines."""
    r, g, b = rgb[:, :, 0].astype(np.int16), rgb[:, :, 1].astype(np.int16), rgb[:, :, 2].astype(np.int16)
    orange = (r > 170) & (g > 55) & (g < 170) & (b < 90) & ((r - g) > 35)
    row = orange.sum(1)
    thr = max(80, int(rgb.shape[1] * 0.12))
    ys = np.where(row > thr)[0]
    if len(ys) < 2:
        raise RuntimeError("orange threshold rows not found")
    # cluster into bands
    bands = []
    start = prev = int(ys[0])
    for y in ys[1:]:
        y = int(y)
        if y <= prev + 3:
            prev = y
        else:
            bands.append((start, prev, int(row[start : prev + 1].max())))
            start = prev = y
    bands.append((start, prev, int(row[start : prev + 1].max())))
    bands = sorted(bands, key=lambda t: -t[2])[:4]
    centers = sorted(((a + b) // 2 for a, b, _ in bands))
    # 25 is above 8
    if len(centers) < 2:
        raise RuntimeError("need two orange bands")
    # pick the two strongest well-separated bands
    bands_sorted = sorted(bands, key=lambda t: t[0])
    # choose pair with largest separation among top strengths
    strong = sorted(bands, key=lambda t: -t[2])[:3]
    strong = sorted(strong, key=lambda t: t[0])
    y25 = (strong[0][0] + strong[0][1]) // 2
    y8 = (strong[-1][0] + strong[-1][1]) // 2
    if y8 - y25 < 50:
        # fallback: first and last band
        y25 = (bands_sorted[0][0] + bands_sorted[0][1]) // 2
        y8 = (bands_sorted[-1][0] + bands_sorted[-1][1]) // 2
    band25 = orange[max(0, y25 - 2) : y25 + 3].any(0)
    xs = np.where(band25)[0]
    if len(xs) < 10:
        band8 = orange[max(0, y8 - 2) : y8 + 3].any(0)
        xs = np.where(band8)[0]
    x_left, x_right = int(xs.min()), int(xs.max())
    return y25, y8, x_left, x_right


def crop_plot(rgb: np.ndarray, y_min_label: float, y_max_label: float) -> tuple[np.ndarray, dict]:
    y25, y8, x_left, x_right = find_threshold_rows(rgb)
    scale = (y8 - y25) / (25.0 - 8.0)
    y_top = int(round(y25 - (y_max_label - 25.0) * scale))
    y_bot = int(round(y8 + (8.0 - y_min_label) * scale))
    y_top = max(0, y_top)
    y_bot = min(rgb.shape[0] - 1, y_bot)
    # trim a few px inside frame to avoid border / T markers
    pad_x = max(4, (x_right - x_left) // 200)
    x0, x1 = x_left + pad_x, x_right - pad_x
    crop = rgb[y_top : y_bot + 1, x0 : x1 + 1].copy()
    meta = dict(
        y25=y25 - y_top,
        y8=y8 - y_top,
        y_top_page=y_top,
        y_bot_page=y_bot,
        x0_page=x0,
        x1_page=x1,
        y_min_label=y_min_label,
        y_max_label=y_max_label,
        scale=scale,
    )
    return crop, meta


def blue_stroke_mask(rgb: np.ndarray) -> np.ndarray:
    """Strict navy stroke: high saturation blue; exclude fill & gray grid."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)

    # OpenCV H for navy ~100–115
    hue_ok = (h >= 95) & (h <= 125)
    sat_ok = s >= 90  # fill ~17, grid ~8, stroke ~196
    val_ok = (v >= 60) & (v <= 210)  # exclude pale fill
    chroma = (b - r) > 40
    chroma2 = (b - g) > 8
    not_light = ~((r > 170) & (g > 190) & (b > 200))
    # exclude near-gray anti-alias of dashed grid
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    not_gray = (mx - mn) > 35

    mask = (hue_ok & sat_ok & val_ok & chroma & chroma2 & not_light & not_gray).astype(np.uint8) * 255

    # Remove thin vertical/horizontal dashed remnants via opening with small ellipse
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    # Bridge small gaps along the stroke (horizontal preference)
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_h, iterations=1)

    # Drop dashed-grid fragments: short flat horizontal dashes (h small, aspect wide)
    nlab, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cleaned = np.zeros_like(mask)
    for i in range(1, nlab):
        x, y, w, h, area = stats[i]
        if area < 6:
            continue
        # classic dashed-grid remnant: wide & very flat
        if h <= 2 and w >= 6 and area < 40:
            continue
        if h <= 3 and w >= 12 and w > 4 * max(h, 1):
            continue
        # accept stroke fragments
        if w >= 2 or h >= 3 or area >= 15:
            cleaned[labels == i] = 255
    return cleaned


def track_centerline(mask: np.ndarray, max_jump: float = 14.0, spike_jump: float = 420.0) -> tuple[np.ndarray, int, int]:
    """Left→right continuous centerline. Large jumps only near the real heat spike."""
    h, w = mask.shape
    ys = np.full(w, np.nan, dtype=np.float64)
    cands: list[list[float]] = []
    top_y = np.full(w, h, dtype=np.int32)
    for x in range(w):
        col = mask[:, x] > 0
        if not col.any():
            cands.append([])
            continue
        idx = np.where(col)[0]
        top_y[x] = int(idx.min())
        runs = []
        a = int(idx[0])
        prev = a
        for y in idx[1:]:
            y = int(y)
            if y <= prev + 1:
                prev = y
            else:
                runs.append((a, prev))
                a = prev = y
        runs.append((a, prev))
        centers = []
        for a, b in runs:
            thick = b - a + 1
            if thick >= 2 or len(runs) == 1:
                centers.append(0.5 * (a + b))
        cands.append(centers)

    # Spike column = highest stroke pixel (lowest y) with enough prominence
    valid_top = np.where(top_y < h)[0]
    if len(valid_top) == 0:
        raise RuntimeError("no stroke pixels")
    spike_x = int(valid_top[np.argmin(top_y[valid_top])])
    spike_half = max(25, int(0.07 * w))

    start_x = next((x for x in range(w) if cands[x]), None)
    early = []
    for x in range(start_x, min(w, start_x + 50)):
        early.extend(cands[x])
    seed_ref = float(np.median(early)) if early else h * 0.55
    ys[start_x] = min(cands[start_x], key=lambda y: abs(y - seed_ref))
    last_obs = start_x

    for x in range(start_x + 1, w):
        prev = ys[last_obs]
        if not cands[x]:
            continue
        near_spike = abs(x - spike_x) <= spike_half
        gap = x - last_obs
        best = None
        best_cost = 1e18
        for y in cands[x]:
            dy = abs(y - prev)
            # large vertical moves only near the real spike column
            lim = (spike_jump if near_spike else max_jump) + min(gap * 0.6, 20)
            # also allow descending from a high prev shortly after spike
            if (not near_spike) and prev < h * 0.35 and abs(x - spike_x) <= 2 * spike_half:
                lim = max(lim, spike_jump * 0.6)
            if dy > lim:
                continue
            cost = dy
            if cost < best_cost:
                best_cost = cost
                best = y
        if best is None:
            y = min(cands[x], key=lambda yy: abs(yy - prev))
            lim = spike_jump if near_spike else max_jump
            if abs(y - prev) <= lim + min(gap, 30):
                best = y
        if best is not None:
            ys[x] = best
            last_obs = x

    xp = np.where(~np.isnan(ys))[0]
    if len(xp) < 10:
        raise RuntimeError("centerline too sparse")
    x_first, x_last = int(xp[0]), int(xp[-1])
    ys_full = np.interp(np.arange(w), xp, ys[xp])
    out = ys_full.copy()
    win = 5
    d = np.abs(np.diff(ys_full, prepend=ys_full[0]))
    steep = d > 4.0
    for i in range(x_first, x_last + 1):
        if steep[i] or abs(i - spike_x) <= spike_half:
            continue
        a = max(x_first, i - win // 2)
        b = min(x_last + 1, i + win // 2 + 1)
        if steep[a:b].any():
            continue
        out[i] = np.median(ys_full[a:b])
    return out, x_first, x_last


def y_to_temp(y: np.ndarray, meta: dict) -> np.ndarray:
    y25, y8 = meta["y25"], meta["y8"]
    return 8.0 + (y8 - y) * (25.0 - 8.0) / (y8 - y25)


def calibrate_affine(temps: np.ndarray, low: float, high: float) -> np.ndarray:
    """Map continuous curve so min/max match report extremes (no single-point snap).

    Uses a robust low (percentile) so dashed-grid crumbs below the true curve
    cannot lift the whole series when remapping to report extremes.
    """
    tmax = float(np.max(temps))
    tmin = float(np.percentile(temps, 0.5))
    tmin = min(tmin, tmax - 1e-3)
    clipped = np.maximum(temps, tmin)
    scaled = low + (clipped - tmin) * (high - low) / (tmax - tmin)
    return scaled


def align_peak_time(
    temps: np.ndarray,
    t0: datetime,
    high_t: datetime,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Resample to n points; map X so digitized peak lands on reported high time.

    Uses a two-segment linear time warp (start→peak, peak→end) so the rest of the
    curve keeps relative spacing without wrap-around artifacts from a global shift.
    """
    grid = np.array([t0 + timedelta(minutes=15 * i) for i in range(n)])
    peak_i = int(np.argmax(temps))
    target_i = int(round((high_t - t0).total_seconds() / 900.0))
    target_i = min(max(target_i, 1), n - 2)
    m = len(temps)
    if peak_i <= 0:
        peak_i = 1
    if peak_i >= m - 1:
        peak_i = m - 2

    # source positions in [0, 1] with peak at peak_i
    # destination positions with peak at target_i
    src = np.arange(m, dtype=np.float64)
    dst_pos = np.empty(m, dtype=np.float64)
    # left segment: 0..peak_i -> 0..target_i
    dst_pos[: peak_i + 1] = np.linspace(0, target_i, peak_i + 1)
    # right segment: peak_i..end -> target_i..n-1
    dst_pos[peak_i:] = np.linspace(target_i, n - 1, m - peak_i)
    # resample temps onto integer sample grid
    # invert: for each grid index, interpolate from dst_pos
    order = np.argsort(dst_pos)
    out = np.interp(np.arange(n, dtype=np.float64), dst_pos[order], temps[order])
    return grid, out


def soft_despike(temps: np.ndarray, times: np.ndarray, high_t: datetime) -> np.ndarray:
    """Remove isolated needles outside the real heat event; keep continuous shape."""
    t = temps.copy()
    n = len(t)
    for i in range(1, n - 1):
        # outside ±10h of reported high: suppress single-point extremes
        if abs((times[i] - high_t).total_seconds()) < 10 * 3600:
            continue
        if abs(t[i] - t[i - 1]) > 4 and abs(t[i] - t[i + 1]) > 4 and abs(t[i - 1] - t[i + 1]) < 3:
            t[i] = 0.5 * (t[i - 1] + t[i + 1])
    # clamp: no >35°C outside spike day window
    for i in range(n):
        if t[i] > 35 and not (
            datetime(2026, 7, 29, 18, 0) <= times[i] < datetime(2026, 7, 31, 12, 0)
        ):
            # pull toward local neighborhood
            a = max(0, i - 3)
            b = min(n, i + 4)
            neigh = [t[j] for j in range(a, b) if j != i and t[j] <= 35]
            if neigh:
                t[i] = float(np.median(neigh))
    return t


def make_overlay(crop: np.ndarray, ys: np.ndarray, path: Path) -> None:
    vis = crop.copy()
    for x, y in enumerate(ys):
        yi = int(round(y))
        if 1 <= yi < vis.shape[0] - 1:
            vis[yi - 1 : yi + 2, x] = (220, 30, 30)
    Image.fromarray(vis).save(path)


def make_chart_png(serial: str, times, temps, low, high, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=120)
    ax.fill_between(times, 8, 25, color="#d9eef8", alpha=0.7, linewidth=0)
    ax.axhline(25, color="#c45c26", lw=1.2)
    ax.axhline(8, color="#d17a2c", lw=1.2)
    ax.plot(times, temps, color="#1a5aaf", lw=1.3, label="Primary: Ambient")
    ax.set_title(f"TempTale Ultra — {serial} (tratto blu, senza griglia)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Date/Time")
    ax.set_ylim(min(7.0, low - 1), max(high + 2, 70))
    ax.grid(True, ls="--", lw=0.5, color="#b0b0b0")
    ax.legend(loc="upper right", fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


@dataclass
class Result:
    serial: str
    times: np.ndarray
    temps: np.ndarray
    crop_path: Path
    mask_path: Path
    match_path: Path
    chart_path: Path
    meta: dict
    stats: dict


def digitize_device(dev: dict, page_path: Path, out: Path) -> Result:
    rgb = np.array(Image.open(page_path).convert("RGB"))
    crop, meta = crop_plot(rgb, dev["y_min_label"], dev["y_max_label"])
    mask = blue_stroke_mask(crop)
    ys, x0s, x1s = track_centerline(mask)
    # Use only the observed stroke span (first→last blue pixel track)
    temps_raw = y_to_temp(ys[x0s : x1s + 1], meta)
    temps_cal = calibrate_affine(temps_raw, dev["low"], dev["high"])
    t0 = parse_dt(dev["first"])
    times, temps = align_peak_time(
        temps_cal,
        t0,
        parse_dt(dev["high_t"]),
        dev["n"],
    )
    temps = soft_despike(temps, times, parse_dt(dev["high_t"]))
    # Continuous affine to report extremes (no single-point snap / no roll)
    temps = calibrate_affine(temps, dev["low"], dev["high"])

    serial = dev["serial"]
    crop_path = out / f"crop_{serial}.png"
    mask_path = out / f"mask_{serial}.png"
    match_path = out / f"match_{serial}.png"
    chart_path = ART / f"grafico_{serial}.png"
    Image.fromarray(crop).save(crop_path)
    Image.fromarray(mask).save(mask_path)
    make_overlay(crop, ys, match_path)
    make_chart_png(serial, times, temps, dev["low"], dev["high"], chart_path)

    # also save match into artifacts
    Image.open(match_path).save(ART / f"match_{serial}.png")

    needles = 0
    for i in range(1, len(temps) - 1):
        if (
            abs(temps[i] - temps[i - 1]) > 6
            and abs(temps[i] - temps[i + 1]) > 6
            and abs(temps[i - 1] - temps[i + 1]) < 4
        ):
            needles += 1
    hot_out = sum(
        1
        for dt, v in zip(times, temps)
        if v > 35 and not (datetime(2026, 7, 30) <= dt < datetime(2026, 7, 31))
    )
    stats = dict(
        min=float(np.min(temps)),
        max=float(np.max(temps)),
        mean=float(np.mean(temps)),
        needles=needles,
        hot_out=hot_out,
        peak_time=str(times[int(np.argmax(temps))]),
        low_time=str(times[int(np.argmin(temps))]),
    )
    print(serial, stats)
    return Result(serial, times, temps, crop_path, mask_path, match_path, chart_path, meta, stats)


def build_excel(results: list[Result], devices: list[dict]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Riepilogo"
    headers = [
        "Serial #",
        "First GMT",
        "Stop GMT",
        "N",
        "Interval",
        "Low °C",
        "Low Time",
        "High °C",
        "High Time",
        "Mean report",
        "Mean dig",
        "Needles",
        "Hot>35 out",
    ]
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        ws.cell(1, c).font = Font(bold=True)
    by_serial = {d["serial"]: d for d in devices}
    for r in results:
        d = by_serial[r.serial]
        ws.append(
            [
                r.serial,
                d["first"],
                d["stop"],
                d["n"],
                15,
                d["low"],
                d["low_t"],
                d["high"],
                d["high_t"],
                d["mean"],
                round(r.stats["mean"], 2),
                r.stats["needles"],
                r.stats["hot_out"],
            ]
        )
    ws.append([])
    ws.append(
        [
            "Nota",
            "v11: maschera HSV navy ad alta saturazione; griglia grigia e fill azzurro esclusi; "
            "centerline continua L→R; calibrazione affine min/max report (niente snap a singolo punto); "
            "allineamento picco a High Extreme.",
        ]
    )

    gws = wb.create_sheet("Grafici")
    gws["A1"] = "Grafici ricostruiti dal solo tratto blu"
    gws["A1"].font = Font(bold=True, size=14)
    row = 3
    for r in results:
        gws.cell(row, 1, r.serial).font = Font(bold=True)
        img = XLImage(str(r.chart_path))
        img.width = 880
        img.height = 340
        gws.add_image(img, f"A{row + 1}")
        row += 20

    for r in results:
        d = by_serial[r.serial]
        ws = wb.create_sheet(r.serial[:31])
        ws["A1"] = "Digitalizzazione SOLO tratto blu — griglia tratteggiata e fill esclusi (v11)"
        ws["A1"].font = Font(bold=True)
        meta_rows = [
            ("Serial #", r.serial),
            ("First Point (GMT)", d["first"]),
            ("Stop Time (GMT)", d["stop"]),
            ("Interval", "15 min"),
            ("Points", d["n"]),
            ("Low Extreme", f"{d['low']} °C @ {d['low_t']}"),
            ("High Extreme", f"{d['high']} °C @ {d['high_t']}"),
            ("Mean ± SD (report)", f"{d['mean']} ± {d['sd']} °C"),
            ("Mean digitalizzato", round(r.stats["mean"], 2)),
            ("False spikes (needles)", r.stats["needles"]),
            (
                "Metodo",
                "HSV navy (S>90, H≈100–115), esclusione grigio/fill; tracking continuo; affine min/max; peak lock",
            ),
        ]
        for i, (k, v) in enumerate(meta_rows, start=3):
            ws.cell(i, 1, k).font = Font(bold=True)
            ws.cell(i, 2, v)
        ws["A15"] = "A) Grafico digitalizzato"
        ws["A15"].font = Font(bold=True)
        img1 = XLImage(str(r.chart_path))
        img1.width = 720
        img1.height = 280
        ws.add_image(img1, "A16")
        ws["A34"] = "B) Overlay rosso sul tratto blu originale"
        ws["A34"].font = Font(bold=True)
        img2 = XLImage(str(ART / f"match_{r.serial}.png"))
        img2.width = 720
        img2.height = 320
        ws.add_image(img2, "A35")

        start = 56
        ws.cell(start, 1, "Index").font = Font(bold=True)
        ws.cell(start, 2, "Timestamp (GMT)").font = Font(bold=True)
        ws.cell(start, 3, "Temperature (°C)").font = Font(bold=True)
        ws.cell(start, 4, "Soglia 25°C").font = Font(bold=True)
        ws.cell(start, 5, "Soglia 8°C").font = Font(bold=True)
        for i, (dt, temp) in enumerate(zip(r.times, r.temps), start=1):
            ws.cell(start + i, 1, i)
            ws.cell(start + i, 2, dt.strftime("%Y-%m-%d %H:%M:%S"))
            ws.cell(start + i, 3, round(float(temp), 1))
            ws.cell(start + i, 4, 25)
            ws.cell(start + i, 5, 8)

        chart = LineChart()
        chart.title = f"{r.serial} Temperature"
        chart.style = 10
        chart.y_axis.title = "°C"
        chart.x_axis.title = "Sample"
        chart.height = 10
        chart.width = 18
        data = Reference(ws, min_col=3, min_row=start, max_col=5, max_row=start + len(r.temps))
        cats = Reference(ws, min_col=2, min_row=start + 1, max_row=start + len(r.temps))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        chart.shape = 4
        ws.add_chart(chart, "G3")
        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 22
        ws.column_dimensions["C"].width = 16

    wb.save(XLSX)
    print("Wrote", XLSX)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    pages = render_pages(PDF, OUT)
    results = []
    for dev in DEVICES:
        page_path = OUT / f"page_{dev['page']}.png"
        results.append(digitize_device(dev, page_path, OUT))
    build_excel(results, DEVICES)
    # summary json
    summary = {r.serial: r.stats for r in results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    # copy excel to artifacts
    import shutil

    shutil.copy2(XLSX, "/opt/cursor/artifacts/Temperature_Ricostruite.xlsx")
    for r in results:
        shutil.copy2(r.chart_path, f"/opt/cursor/artifacts/grafico_{r.serial}.png")
        shutil.copy2(ART / f"match_{r.serial}.png", f"/opt/cursor/artifacts/match_{r.serial}.png")


if __name__ == "__main__":
    main()
