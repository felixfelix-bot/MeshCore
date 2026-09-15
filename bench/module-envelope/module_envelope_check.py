#!/usr/bin/env python3
"""Checkable arithmetic for the module rigid envelope (fleet card meshcore:t_69bc5ef5).

stdlib only; prints to stdout only; deterministic (no timestamps, no randomness).
Every input carries a provenance label:

  [DRAWING]     machine-read this session (tesseract OCR) from the vendor
                datasheet V1.3 section 9 mechanical drawing raster; the
                tolerances (+/-0.5, +/-0.1) are printed on the drawing itself.
  [DXF]         computed from the vendor package drawing
                'LoRa2021 V1.2_pads.dxf' (UNITS = Mils per its own companion
                .asc header line 'UNITS 0'); mil->mm factor 0.0254 exact.
  [RECORD]      value already on record in the balloon repo
                (nicerf-lora2021.json / enclosure README / FLIGHT-BOARD-PLAN /
                wiring-dev-board.csv / breadboard-wiring-guide.md).
  [UNVERIFIED]  record value whose as-built realization cannot be confirmed
                from this host (DUT not attached, no calipers, no camera).
"""

MIL_MM = 0.0254  # exact: 1 mil = 0.0254 mm

# --- inputs -------------------------------------------------------------
# [DXF] body outline extreme coordinates, mils (STK/pad insert extents and
# SMOOTH_10 corner arc centers bound the outline):
dxf_x_min_mil, dxf_x_max_mil = -295.5904986877, 294.9606824147
dxf_y_min_mil, dxf_y_max_mil = -388.1251968504, 388.1251968504
# [DXF] pad (STK_TOP_3) center columns and span extremes, mils:
dxf_pad_col_abs_mil = 294.9606824147      # |x| of both pad center columns
dxf_pad_span_abs_mil = 314.9605774278     # |y| of extreme pad centers
dxf_pitch_mil = 78.740183727              # pad center-to-center pitch
dxf_pads_per_side = 9                     # STK_TOP_3 count per long edge

# [DRAWING] section 9 callouts (OCR, this session):
draw_L, draw_L_tol = 19.72, 0.5
draw_W, draw_W_tol = 15.0, 0.5
draw_T, draw_T_tol = 2.2, 0.1
draw_margin, draw_margin_tol = 1.86, 0.1   # edge margin to pad centers

# [RECORD] cross-source values:
json_L, json_W, json_T = 19.81, 14.98, 2.32       # nicerf-lora2021.json
bom_L, bom_W = 19.72, 15.05                        # BOM report 55585471
readme_L, readme_W = 19.72, 15.0                   # enclosure/README.md variant A

# [RECORD] protrusion wires (bendable 30 AWG stiff copper, not rigid):
wire_subghz_total_mm = 164.0   # wiring-dev-board.csv AE1 / FLIGHT-BOARD-PLAN
wire_subghz_leg_mm = 86.0      # breadboard-wiring-guide.md "8.6 cm wire x2"
wire_24ghz_total_mm = 31.0     # wiring-dev-board.csv AE2


def line(c="-"):
    print(c * 72)


print("MODULE RIGID ENVELOPE — CHECKABLE ARITHMETIC (card meshcore:t_69bc5ef5)")
line()

# --- 1. DXF body outline ------------------------------------------------
x_span_mil = dxf_x_max_mil - dxf_x_min_mil
y_span_mil = dxf_y_max_mil - dxf_y_min_mil
x_span_mm = x_span_mil * MIL_MM
y_span_mm = y_span_mil * MIL_MM
half_L_mm = dxf_y_max_mil * MIL_MM   # long axis is y (pads run along y)
half_W_mil = x_span_mil / 2.0
print("1. DXF body outline [DXF]")
print("   sharp-corner rectangle, insert placement points (SMOOTH_10 corners):")
print("   x: %.4f .. %.4f mil -> span %8.4f mil = %8.4f mm (short axis = width)"
      % (dxf_x_min_mil, dxf_x_max_mil, x_span_mil, x_span_mm))
print("   y: %.4f .. %.4f mil -> span %8.4f mil = %8.4f mm (long axis  = length)"
      % (dxf_y_min_mil, dxf_y_max_mil, y_span_mil, y_span_mm))
print("   half-length %8.4f mil = %8.4f mm" % (dxf_y_max_mil, half_L_mm))
half_W_mil = x_span_mil / 2.0
print("   half-width  %8.4f mil = %8.4f mm (rectangle slightly off-center"
      % (half_W_mil, half_W_mil * MIL_MM))
print("   in x: edges at %.4f and %.4f mil, i.e. -%.4f/+%.4f mm)" %
      (dxf_x_min_mil, dxf_x_max_mil, -dxf_x_min_mil * MIL_MM, dxf_x_max_mil * MIL_MM))
print("   corner smoothing radius 2.5 mil = %.4f mm rounds corners INWARD"
      % (2.5 * MIL_MM))
print("   (material outline <= sharp rectangle; projection 0.00 mm outward)")
line()

# --- 2. Pad arithmetic closure ------------------------------------------
pitch_mm = dxf_pitch_mil * MIL_MM
pad_half_span_mm = dxf_pad_span_abs_mil * MIL_MM
pad_margin_mm = half_L_mm - pad_half_span_mm
pad_span_mm = (dxf_pads_per_side - 1) * pitch_mm
closure_L = pad_span_mm + 2 * pad_margin_mm
print("2. Pad arithmetic closure [DXF] vs [DRAWING]")
print("   pitch                %8.4f mil = %8.4f mm (drawing: 2.0+/-0.1)" % (dxf_pitch_mil, pitch_mm))
print("   pad center half-span %8.4f mm" % pad_half_span_mm)
print("   edge margin          %8.4f mm  (drawing callout: %.2f+/-%.2f)" % (pad_margin_mm, draw_margin, draw_margin_tol))
print("   %d pads/side -> %d pitches = %8.4f mm" % (dxf_pads_per_side, dxf_pads_per_side - 1, pad_span_mm))
print("   closure: %8.4f + 2 x %8.4f = %8.4f mm" % (pad_span_mm, pad_margin_mm, closure_L))
print("   drawing length %.2f+/-%.2f -> closure delta %+0.4f mm  -> %s"
      % (draw_L, draw_L_tol, closure_L - draw_L,
         "PASS (well inside tolerance)" if abs(closure_L - draw_L) <= draw_L_tol else "FAIL"))
line()

# --- 3. Cross-source concordance and bounding values ---------------------
print("3. Cross-source concordance (module rigid body, mm)")
print("   source                        length    width    thick")
print("   [DRAWING] ds V1.3 s.9        %8.2f  %8.2f  %8.2f   (tol +/-%.1f, +/-%.1f, +/-%.1f)"
      % (draw_L, draw_W, draw_T, draw_L_tol, draw_W_tol, draw_T_tol))
print("   [DXF] package drawing        %8.4f  %8.4f     n/a" % (y_span_mm, x_span_mm))
print("   [RECORD] footprint json      %8.2f  %8.2f  %8.2f" % (json_L, json_W, json_T))
print("   [RECORD] BOM 55585471        %8.2f  %8.2f     n/a" % (bom_L, bom_W))
print("   [RECORD] enclosure README    %8.2f  %8.2f     n/a" % (readme_L, readme_W))
bound_L = max(draw_L, y_span_mm, json_L, bom_L, readme_L)
bound_W = max(draw_W, x_span_mm, json_W, bom_W, readme_W)
bound_T = max(draw_T, json_T)
print("   BOUNDING (max of record)     %8.2f  %8.2f  %8.2f" % (bound_L, bound_W, bound_T))
tol_L = draw_L + draw_L_tol
tol_W = draw_W + draw_W_tol
tol_T = max(draw_T + draw_T_tol, json_T)
print("   TOLERANCE-INCLUSIVE worst    %8.2f  %8.2f  %8.2f   (drawing upper tol;"
      % (tol_L, tol_W, tol_T))
print("   thickness uses max(2.2+0.1, record 2.32) because record exceeds drawing tol)")
anomaly = json_T - (draw_T + draw_T_tol)
print("   thickness anomaly: record 2.32 exceeds drawing upper tol 2.3 by %+.2f mm"
      % anomaly)
print("   -> bounding thickness 2.32 mm adopted (conservative); interpretation")
print("      (pad/solder bump on the measured unit) UNVERIFIED")
line()

# --- 4. Fit arithmetic ----------------------------------------------------
print("4. Fit arithmetic (all computed from the bounding values above)")
diag_face = (bound_L ** 2 + bound_W ** 2) ** 0.5
diag_face_tol = (tol_L ** 2 + tol_W ** 2) ** 0.5
print("   face diagonal sqrt(%.2f^2 + %.2f^2) = %.2f mm  (bounding)" % (bound_L, bound_W, diag_face))
print("   face diagonal sqrt(%.2f^2 + %.2f^2) = %.2f mm  (tolerance-inclusive)" % (tol_L, tol_W, diag_face_tol))
# minimum round bore for a rectangular box, best orientation (long axis first):
bore_min = (bound_W ** 2 + bound_T ** 2) ** 0.5
bore_min_tol = (tol_W ** 2 + tol_T ** 2) ** 0.5
print("   min round bore, module lengthwise-first (sqrt(W^2+T^2)):")
print("     bounding %.2f mm  /  tolerance-inclusive %.2f mm  (zero clearance)"
      % (bore_min, bore_min_tol))
print("   with 10%% handling clearance: %.2f mm (tolerance-inclusive)"
      % (bore_min_tol * 1.1))
slot_w = tol_L
slot_t = tol_T
print("   min slot, module flat: %.2f x %.2f mm (tolerance-inclusive, zero clearance)"
      % (slot_w, slot_t))
line()

# --- 5. Protrusion deltas -------------------------------------------------
print("5. Protrusion deltas beyond the nominal body")
pad_flush = (dxf_x_max_mil - dxf_pad_col_abs_mil) * MIL_MM
print("   DXF NOTE: this decal is the LAND PATTERN (host-side copper), not")
print("   a module drawing: the STK lands (3.0 x 1.2 mm, +/-59.06 mil spine)")
print("   center on the outline edge and extend 59.06 mil = 1.50 mm OUTBOARD")
print("   of it - that is HOST PCB copper, NOT module material, and adds")
print("   nothing to the MODULE envelope.")
print("   the MODULE's own edge feature is the castellation half-hole")
print("   (DRIL_HOLE dia 39.37 mil = 1.00 mm) centered exactly ON the")
print("   outline edge x = %.4f mil: half-moon plated barrel opening at"
      % dxf_x_max_mil)
print("   the edge; module material extends exactly TO the edge and no")
print("   further -> rigid projection 0.00 mm beyond L x W")
line()
print("   pin-1 marker (PADs decal semicircle, DXF vertices x 329.19-360.81")
print("   mil, y -395 mil) sits OUTSIDE the outline near terminal 1 (ANT")
print("   end) -> NOT material; no envelope effect (decal convention)")
line()
print("5b. Castellation notch geometry (drill holes through the edge)")
print("   DXF DRIL_HOLE_0 is a DIMENSIONLESS decal symbol (zero-size")
print("   polyline; no diameter anywhere in the DXF); the 1.0 mm diameter")
print("   is the DRAWING callout 1.0+/-0.1 [DRAWING].")
print("   -> castellation half-moon notches cut %.2f mm deep INTO the body"
      % 0.5)
print("      (material REMOVED, not added: each notch is a half-circle of")
print("      dia 1.0 mm at the edge; body remains L x W at the pad")
print("      centerlines; depth = radius = 1.0/2 mm)")
line()
print("   antenna wires: bendable 30 AWG stiff copper [RECORD] -> rigid projection")
print("      0.00 mm (bends; does not sweep a rigid envelope)")
print("   [UNVERIFIED] as-built extended tip-to-tip of the sub-GHz dipole:")
print("      reading 1 (one %.0f mm wire bent 180 deg at center): span ~%.0f mm"
      % (wire_subghz_total_mm, wire_subghz_total_mm))
print("      reading 2 (two %.0f mm legs): span ~%.0f mm"
      % (wire_subghz_leg_mm, 2 * wire_subghz_leg_mm))
print("      -> bound 164-172 mm, which reading is as-built UNKNOWN (DUT absent)")
print("   2.4 GHz stub: %.0f mm wire [RECORD], same non-rigid treatment" % wire_24ghz_total_mm)
line()

# --- 6. Headline numbers ---------------------------------------------------
print("6. HEADLINE NUMBERS (card step 4)")
print("   max cross-section (W x H, face-on): %.2f x %.2f mm  (bounding of record)"
      % (bound_L, bound_W))
print("   max cross-section tolerance-inclusive: %.2f x %.2f mm" % (tol_L, tol_W))
print("   max rigid dimension (L, end-to-end incl. mounting hardware):")
print("     %.2f mm  (module body; NO connectors, standoffs, fins, or screws exist"
      % bound_L)
print("      on the module - dut-rf-ports 0b7bfe92: RF exits are soldered wire)")
print("   effective swept cross-section incl. protrusions: UNCHANGED =")
print("     %.2f x %.2f x %.2f mm (every rigid protrusion projects 0.00 mm beyond"
      % (bound_L, bound_W, bound_T))
print("      the outline; only bendable wires extend, up to 164-172 mm non-rigid)")
print("   end-to-end maximum extent with dipole laid collinear (NON-RIGID,")
print("     orientation-dependent): %.2f + 164 = %.2f mm (reading 1 bound)"
      % (bound_L, bound_L + wire_subghz_total_mm))
line()
print("END")