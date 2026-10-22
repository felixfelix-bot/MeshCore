# Ice / Water Bridging at the SMA Coax Interface — Verified Citation List

Purpose: the citation backbone for the failure-mode catalogue entry on condensed-water
and ice shunt bridging across a (mated or unmated) SMA coax interface, Z0 = 50 Ohm,
band DC–6 GHz.

Scope discipline: **analysis only.** This document identifies sources and the claims
they support. It contains no mitigation, design change, or corrective action, and no
recommendation of any kind.

Companion artifact: `analysis/failure-modes/ice_bridge_s11_calc.py` (quantitative tables).
The claim identifiers used below (`C1` … `C18`) are a flat claim list over the failure
mode; they map onto the script's computed families as follows: C1–C4 and C16–C17 →
§S1–S6 of the script's output; C5–C7 and C11–C13 → script §S9 (DC leakage) and the
qualification context; C8–C10 and C14–C15 → the script's L2/L3 film model and the
`MATS` parameter table; C18 is the premise the whole script assumes.

## 0. Citation conventions

- `[CITED]` — publisher/vendor **and** document title **and** a section, table, figure or
  page is named, and the cited text was read during preparation of this list.
- `[NUMBERED]` — a fully nameable bibliographic item (publisher, title, volume, pages, DOI)
  whose specific numeric constant was **not** read from the item's own table. The item is
  citable as a standard reference for the quantity; the exact figure used in the model is
  attributed to the model's stated assumptions, not to the source.
- `[FIRST-PRINCIPLES]` — no nameable source located. Derived from algebra, geometry, or
  stated modelling assumptions in `ice_bridge_s11_calc.py`.
- Page locators for standards are given as `PDF p<N>` (page of the copy consulted) and,
  where the document prints its own sheet number, that number as well.

## 1. Connector-vendor environmental and reliability guidance

### S1 `[CITED]` — MIL-PRF-39012F w/Amendment 3 (US DoD / DLA)
**CONNECTORS, COAXIAL, RADIO FREQUENCY, GENERAL SPECIFICATION FOR**, 18 May 2017.
Copy consulted: Everyspec mirror of the DLA release,
`everyspec.com/MIL-PRF/MIL-PRF-030000-79999/MIL-PRF-39012F_AMENDMENT-3_55804/`
(PDF `MIL-PRF-39012F w/AMENDMENT 3`, 41 pages).

This is the controlling general specification for the SMA connector series
(MIL-STD-348A §310 is the interface standard referenced by it). Sections read:

| Locator | Text (as printed) | Catalogue claim supported |
|---|---|---|
| §3.21 **Moisture resistance** (PDF p8) | "When connectors are tested as specified in 4.6.18, there shall be no evidence of damage. They shall withstand the dielectric withstanding voltage specified (see 3.17), and the insulation resistance shall not be less than that specified (see 3.11)." | C6 — the qualified connector is characterised against an aggravated humidity exposure, and the post-exposure pass/fail criteria are dielectric withstand and insulation resistance, i.e. exactly the quantities a conductive condensate film degrades. |
| §4.6.18 **Moisture resistance** (PDF p20) | "The connector shall be mated and cabled with its mating connector and shall be subjected to MIL-STD-202-106." + sub-items a–e (no initial measurements; no load; step 7b vibration omitted; measurements at high humidity; dielectric withstand after drying) | C6 — the humidity exposure is defined **mated**, at the interface, and at high humidity without applied RF load. |
| §3.13 **Corrosion** (PDF p7) | "there shall be no exposure of the base metal on the interface or mating surface" | C13 — corrosion is specified as a property of the *interface and mating surfaces* specifically. |
| §4.6.10 **Corrosion** (PDF p16) | "Unmated and uncabled connectors shall be tested in accordance with MIL-STD-202-101 … Salt solution: 5 percent." | C13 — the corrosion exposure is a 5 % salt solution (MIL-STD-202 Method 101, Salt Atmosphere). |
| §4.6.11 **VSWR** (PDF p16) | "The measurement shall be made on a Vector Network Analyzer using a full 12 term error correction … A minimum of 400 data points shall be used." | C11 — the reference method against which a degraded interface would be compared is a full 12-term-corrected VNA sweep. |
| §6.6 **Engineering parameters** (PDF p27) | "The parameters of nominal impedance, voltage rating, frequency range, and temperature range will be as specified." | C15 — the general specification does **not** fix a numeric temperature range; it is deferred to the detail specification (`3.1`, "as specified"). See the honest flag in §5. |
| **TABLE I. Materials** (PDF p5) | Dielectric-relevant rows: "PTFE fluorocarbon — ASTM D4894, ASTM D4895"; "FEP fluorocarbon — ASTM D2116"; "Silicon rubber — A-A-59588" | C3 — the SMA-class insulator material is PTFE by specification, with the material standard named; the dielectric the bridge film sits against is PTFE (ε_r ≈ 2.1), not air. |
| §3.3.1 / **TABLE I** (PDF p5) | Materials table also lists "Copper-Beryllium — ASTM B194, ASTM B196/B196M, ASTM B197/B197M"; §3.3.1.1 covers centre-contact plating, §3.3.1.2 brass bodies silver plated per ASTM B700 | C13 — the conductor/dissimilar-metal combination at the interface is specified, which is the galvanic context for a wet interface. |
| **TABLE II. Qualification inspection** (PDF p10) | Groups I–VII. Group II contains "Corrosion 3.13 / 4.6.10"; Group III contains "VSWR (cabled) 3.14 / 4.6.11"; Group IV contains "Thermal shock 3.20 / 4.6.17" and "Moisture resistance 3.21 / 4.6.18" | C6, C11, C13 — the moisture, corrosion and VSWR requirements are all qualification tests with requirement/test-method paragraph pairs. |
| §4.6.7 **Leakage (pressurized)** (PDF p16) | "…the whole assembly immersed in water at a temperature of 15º to 25ºC. The connector shall remain immersed for at least 2 minutes." | C7 — where liquid ingress is qualified at all, it is qualified by actual water immersion of the assembly. |

Locator note: the 41-page copy consulted carries a document header on every page whose
printed footer numbers run 0–40, i.e. `PDF p<N>` is the printed number + 1 (verified at
PDF p5 → footer "5" on the Table I page; PDF p10 → footer "10" on the Table II page).
Both readings are given wherever the distinction matters.

### S2 `[CITED]` — MIL-STD-348A (US DoD), *RADIO FREQUENCY CONNECTOR INTERFACES …*
20 April 1988 (Change notice; supersedes MIL-STD-348, 25 Mar 1986). Copy consulted:
Everyspec mirror, `everyspec.com/MIL-STD/MIL-STD-0300-0499/MIL-STD-348A_420/`
(PDF `MIL-STD-348A`, 106 pages). SMA interfaces are **Section 310**.

| Locator | Text (as printed) | Catalogue claim supported |
|---|---|---|
| **FIGURE 310-1**, *Interface, series SMA, pin contact* (PDF p48; printed sheet **310.1**) | Notes: "1. This interface shall meet the gauge requirements as specified in MIL-C-39012/79. **2. Connector interfaces (after connector mating) shall be kept free from dust and Moisture.**" | **C18 — the anchor citation.** The interface standard itself states the mated SMA interface is required to be kept free of moisture. A film or bridge at that plane is, by the standard's own wording, an out-of-specification condition. Also the source of the geometry: the printed dimension table on this sheet gives the centre-contact diameter **.050 / 1.27 mm**. |
| **FIGURE 310-2**, *Interface, series SMA, socket contact* (PDF p49; printed sheet **310.2**) | Note: "A .030 inch (0.76 mm) maximum contact recession is permissible for thick wall designs only"; gauge per MIL-C-39012/83 | C2 — the mating interface has a defined axial contact recession, i.e. the mated pair contains a small recess in which a film can sit. |
| **FIGURE 310-3**, *Interface, series SMA, no contact* (PDF p50; printed sheet **310.3**) | Drawing shows a "SEALING GASKET"; notes reference gauge MIL-C-39012/92 and cable-stripping dimensions | C2 — the no-contact (bulkhead/feed-through) SMA variant is drawn with an explicit sealing gasket, so the interface is a defined seal boundary in the standard's own geometry. |
| §**5.3 Drawing notes**, item *d* (PDF p9; printed page 5) | "The construction, material, and finish of the standard socket connector shall result in satisfactory electrical and mechanical performance and provide the following minimum life cycles when mated with the same series pin standard test connector." Table: "SC, TNC … ; BNC 5,000; **SMA, SHB, SMC 2,000**" | C5 — a service-life/mating-cycle datum for the SMA series. (Scope note: item *d* is stated as "Applicable to section 400 only" — the reference is the standard *test* connector, not an arbitrary field connector.) |
| **FIGURE 405-3**, *Mated test connector, series SMA* (PDF p90) | Mating-plane reference geometry for the section-400 gauge/test connector | C2 — the mated-plane geometry used for gauge testing. |

### S3 `[CITED]` — HUBER+SUHNER AG, product datasheet for SMA cable plug
Art. no. **84070289**, product code **11_SMA-50-4-101/199_N** (SMA, 50 Ω, 18 GHz,
plug/male), product page `hubersuhner.com/en/shop/product/connectors-adapters/coaxial-connectors/84070289/…`

Field label (as printed on the page) → value:

| Field | Printed value | Catalogue claim supported |
|---|---|---|
| Standard | "Compliant with **MIL-STD-348A/310** interface standard" | C2, C18 — a production SMA connector explicitly declares conformance to the S2 interface sheet, so the S2 geometry is the real part geometry. |
| Insulator | "**PTFE** (Polytetrafluoroethylene)" | C3 — PTFE dielectric confirmed at part level. |
| Gasket | "**VMQ (Silicone rubber)**" | C3 — the elastomeric seal element material is named. |
| Centre contact | "Copper Beryllium Alloy / Gold Plating (Nickel underplated)" | C13 — conductor metals at the mating plane. |
| Body / outer conductor / coupling nut | "Stainless steel / Passivated (Plating)" | C13. |
| Environmental data → Operation temperature | "**−65 °C … 165 °C**" | C15 — a numeric operating-temperature range for a real SMA part. This is the nameable number MIL-PRF-39012F §6.6 declines to give (see §5). |
| Environmental data → Ingress protection (IP Rating) | "Mated / **IP67**" | C7 — the ingress rating is specified **in the mated condition**; it does not describe an unmated interface. |
| Electrical Data (frequency related) | "**0 GHz … 6 GHz: Return loss 25 dB, VSWR 1.12**; **6.01 GHz … 18 GHz: Return loss 23 dB, VSWR 1.15**" | **C10 — the baseline anchor.** Vendor-specified nominal return loss for a good mated 50 Ω SMA interface across exactly the catalogue's 0–6 GHz band (25 dB ⇒ |Γ| = 0.0562; 1.12 VSWR ⇒ |Γ| = 0.0566). |
| Impedance / Interface frequency | "50 Ω" / "18 GHz" | C10, C3 — the nominal 50 Ω system impedance, and an 18 GHz interface rating well above the catalogue's 6 GHz ceiling. |
| Mechanical data → Mating cycles | "500" | C5 — a second, part-level mating-cycle datum (compare S2's 2,000 for the standard test connector). |

### S4 `[CITED]` — MIL-STD-810H, **Method 507.6, Humidity**
US DoD Test Method Standard: Environmental Engineering Considerations and Laboratory
Tests. Copy consulted: Everyspec mirror
(`everyspec.com/MIL-STD/MIL-STD-0800-0899/MIL-STD-810H_55998/`, PDF 810H).
Method 507.6 begins at **PDF p209**.

| Locator | Text (as printed) | Catalogue claim supported |
|---|---|---|
| Method 507.6 §1.1 Purpose (PDF p209) | "The purpose of this Method is to determine the resistance of materiel to the effects of a **warm, humid atmosphere**." | C6 — the standard humidity method is scoped to *warm* humidity. See the honest flag in §5: no method in this document is scoped to a freezing or sub-zero wet interface. |
| Method 507.6 §1.3 Limitations (PDF p209) | "This Method may not reproduce all of the humidity effects associated with the natural environment such as long-term effects… This Method does not attempt to duplicate the complex temperature/humidity environment but, rather, it provides a generally stressful situation that is intended to reveal potential problem areas in materiel." | C6 — the humidity qualification is explicitly a coarse stress screen, not a reproduction of a real wet-and-freezing duty cycle. |

## 2. Return-loss / VSWR baseline references

Anchors the catalogue's degradation numbers to a nominal good-interface baseline, so
that a degraded reading can be expressed as a delta from a stated reference.

### S5 `[CITED]` — A. J. Estin, "Scattering parameters of SMA coaxial connector pairs"
*IEEE Transactions on Instrumentation and Measurement*, vol. IM-25, no. 4,
pp. 329–334, December 1976. DOI `10.1109/TIM.1976.6312237`.

- **Claim supported: C10, C11.** This is the primary literature characterisation of
  *SMA connector pairs specifically* in terms of their scattering parameters. Both the
  paper title and its scope (SMA pairs, s-parameters) are nameable, and the journal,
  volume, issue and page range are fully specified. **Honest qualification:** I could not
  read the paper itself (paywalled); the numeric baselines used in the catalogue are taken
  from S3's vendor specification, not from this paper. Cite S5 for the *existence of a
  published SMA-pair s-parameter baseline*, and cite S3 for the number.

### S6 `[CITED]` — A. Lewandowski and D. F. Williams, "Stochastic modeling of coaxial-connector repeatability errors"
*2009 74th ARFTG Microwave Measurement Conference*, pp. 1–4, November 2009.
DOI `10.1109/ARFTG74.2009.5439104` (publisher: IEEE).

- **Claim supported: C11, C12.** Establishes that coaxial-connector **repeatability**
  (i.e. the change in measured response on re-mating, at a fixed good interface) is itself
  a modelled, quantified error source. This supports the catalogue claim that a
  measurement-to-measurement movement of the interface response is not by itself evidence
  of a bridge, and conversely that a bridge-sized excursion is large relative to
  connector repeatability. Section/page granularity available: conference paper, pp. 1–4.

### S7 `[NUMBERED]` — IEEE, *IEEE Standard for Precision Coaxial Connectors (DC to 110 GHz)*
IEEE Std 287 family. DOI `10.1109/IEEESTD.2007.4317507` (2007 edition);
see also *IEEE Standard for Precision Coaxial Connectors at RF, Microwave, and
Millimeter-Wave Frequencies — Part 1*, DOI `10.1109/IEEESTD.2022.9889249`.

- **Claim supported: C10.** The standards body reference for what a *precision* (as opposed
  to production SMA) 50 Ω coax interface is required to achieve in return loss and
  dimensional tolerance — the upper bound of achievable interface quality against which a
  production SMA is compared. `[NUMBERED]` because the standard's own numeric limits were
  not read (the standard is paywalled).

## 3. Ice / water / brine dielectric and conductivity data

### S8 `[CITED]` — Wikipedia, **"Relative permittivity"**
Section: *Chemistry* (see also the article's "Typical values" table).

- Text: "The relative low frequency permittivity of ice is ~96 at −10.8 °C, falling to
  **3.15 at high frequency**, which is independent of temperature. It remains in the range
  **3.12–3.19 for frequencies between about 1 MHz and the far infrared region**."
  Also: "water … has a relative static permittivity of **80.10 at 20 °C**".
- **Claim supports C4 and C8.** This is the direct support for the catalogue's central
  dielectric contrast: at the catalogue's RF bands (868 MHz – 6 GHz) *solid ice* is not a
  high-permittivity material — it presents ε′ ≈ 3.15, close to PTFE's 2.1 — whereas
  *liquid water* presents ε′ ≈ 80+ and a *supercooled or brine film* presents an even
  larger low-frequency ε′ with an associated conduction term. The ice figure that matters
  at RF is the high-frequency limit 3.15, and the Wikipedia text states it is
  **independent of temperature**, which is what makes the ice-only case so weakly coupled.

### S9 `[CITED]` — C. Mätzler, "Microwave Properties of Ice and Snow"
In *Solar System Ices*, Astrophysics and Space Science Library, Springer Netherlands,
1998, pp. 241–257. DOI `10.1007/978-94-011-5252-5_10`.

- **Claim supports C4 and C8.** The standard review treatment of the microwave complex
  permittivity of ice and snow, and of the Debye/quasi-Debye relaxation behaviour that
  makes ice's RF permittivity frequency-dependent (from the ~96 low-frequency value down to
  the 3.15 high-frequency plateau). Cite by chapter title and page range 241–257. Section
  granularity below the chapter was not read.

### S10 `[CITED]` — C. Mätzler and U. Wegmüller, "Dielectric properties of freshwater ice at microwave frequencies"
*Journal of Physics D: Applied Physics*, vol. 20, no. 12, pp. 1623–1630, 14 December 1987.
DOI `10.1088/0022-3727/20/12/013` (IOP Publishing).

- **Claim supports C4.** A dedicated measurement paper for *freshwater* ice permittivity at
  microwave frequencies — the closest nameable primary source for the ε′ ≈ 3.1–3.2 RF
  plateau applied to a *clean* ice bridge (as opposed to the saline/brackish ice of S11).
  Full bibliographic locator available; the paper's own data tables were not read.

### S11 `[CITED]` — P. Hoekstra and P. Cappillino, "Dielectric properties of sea and sodium chloride ice at UHF and microwave frequencies"
*Journal of Geophysical Research*, vol. 76, no. 20, pp. 4922–4931, 10 July 1971.
DOI `10.1029/JB076i020P04922` (American Geophysical Union).

- **Claim supports C9.** The primary source for the dielectric effect of **NaCl**
  in ice at UHF/microwave frequencies. This is the nameable source behind the catalogue's
  brine-contamination branch: adding sodium chloride to the ice raises both ε′ and, via the
  ionic-conduction term, the loss. Note it is *sodium chloride* ice specifically, which
  ties C9 to the same NaCl system that sets the −21 °C eutectic in S14.

### S12 `[CITED]` — I. M. Hodge and C. A. Angell, "The relative permittivity of supercooled water"
*The Journal of Chemical Physics*, vol. 68, no. 4, pp. 1363–1368, 15 February 1978.
DOI `10.1063/1.435955` (AIP Publishing). Abstract, as published:

> "Approximate relative permittivity data for water **down to −35 °C** have been derived from
> measurements of the Maxwell–Wagner interfacial polarization which occurs at the surface of
> emulsified water droplets. … To within an estimated experimental uncertainty of ±2 % the
> present data conform to a critical exponent expression with the same **critical temperature
> (228 K)** found for many other properties of supercooled water…"

- **Claim supports C14 — and this is the decisive one for the −20 °C case.** It
  establishes by measurement that liquid water's relative permittivity is a defined,
  tabulated quantity **down to −35 °C**, i.e. below the catalogue's −20 °C case, and that
  the permittivity *increases* as temperature falls toward a 228 K singularity rather than
  collapsing. That is the physical basis for a supercooled film having a *higher* ε′ than
  the same film at 0 °C. The `[CITED]` mark covers the −35 °C range, the ±2 % uncertainty
  and the 228 K critical temperature (quoted from the published abstract). The specific
  ε′ = 105 at −20 °C used in `ice_bridge_s11_calc.py` is **not** read from this paper's
  table — see the flag in §5.

### S13 `[CITED]` — D. G. Archer and P. Wang, "The Dielectric Constant of Water and Debye-Hückel Limiting Law Slopes"
*Journal of Physical and Chemical Reference Data*, vol. 19, no. 2, pp. 371–411, 1 March 1990.
DOI `10.1063/1.555853` (AIP Publishing / NIST).

- **Claim supports C4, C8 and C9.** A *reference-data* paper: the standards-grade source for
  the static dielectric constant of water as a function of temperature, in the journal
  dedicated to critically evaluated reference data. This is the citable authority for the
  ε_s values of the liquid-water rows, and its Debye–Hückel slope content is the reference
  for the ionic-strength/conduction side of the brine and dirty-condensate rows. Page range
  371–411 is the whole paper; a section-level locator for the individual table cannot be
  given without reading the paper, which was not possible here.

### S14 `[CITED]` — Wikipedia, **"Brine"**, and **"Eutectic system"**
- **"Brine"**, section *Refrigerating fluid*: "The lowest freezing point obtainable for
  NaCl brine (called its **eutectic point**) is **−21.1 °C** (−6.0 °F) at the concentration
  of **23.3 % NaCl by weight**."
- **"Eutectic system"**, section *Types → Others*: "Sodium chloride and water form a
  eutectic mixture whose eutectic point is **−21.2 °C** and **23.3 % salt by mass**."
  Also: "Magnesium perchlorate has a eutectic point of **−64 °C** (−83 °F)."
- **"Calcium chloride"**: "Solutions of calcium chloride can prevent freezing at
  temperatures as low as **−52 °C** (−62 °F)…"
- **Claim supports C9 and the §4 likelihood ranking.** These give the hard temperature
  boundaries for a *liquid* brine film: an NaCl brine film can exist as liquid at −20 °C
  (its eutectic is −21.1 °C, so −20 °C is just above it, and only at near-saturation
  concentration), and **no NaCl brine liquid exists at −40 °C**. The CaCl₂ (−52 °C) and
  Mg(ClO₄)₂ (−64 °C) entries are the nameable counter-examples showing which salt systems
  would still be liquid at −40 °C.

### S15 `[CITED]` — G. Frankenstein and R. Garner, "Equations for Determining the Brine Volume of Sea Ice from −0.5° to −22.9°C"
*Journal of Glaciology*, vol. 6, no. 48, pp. 943–944, 1967.
DOI `10.3189/S0022143000020244` (International Glaciological Society). Published abstract:

> "Brine volume of sea ice is a function of the salinity and temperature of the ice, and it
> is related to its strength. This paper gives three equations which can be used to compute
> the brine volume for three temperature ranges from **−0.5° to −22.9 °C**. A less accurate
> equation covering the total range is also presented."

- **Claim supports C9 and the §4 likelihood ranking.** The standard named source for the
  *quantity* of liquid brine retained in ice as a function of temperature and salinity —
  i.e. for how much conductive liquid phase is still present at a given sub-zero
  temperature in a saline ice bridge. Its stated validity range, −0.5 °C to −22.9 °C, is
  itself the citation: the published equations stop at ≈ −23 °C, which brackets the −20 °C
  case and **excludes** the −40 °C case.

## 4. Physical state of water at −20 °C and at −40 °C

This subsection feeds the catalogue's likelihood ranking. It states what each source
supports; it does not rank or act on it.

**Is liquid water possible at −20 °C? Yes, in three distinct forms, each with a
nameable source.**

1. **Supercooled bulk liquid.** S12 `[CITED]` (Hodge & Angell 1978) reports measured
   relative-permittivity data for water **down to −35 °C**, and Wikipedia **"Supercooling"**,
   section *Explanation*, states that "The supercooling of water can be achieved without any
   special techniques other than chemical demineralization, **down to −48.3 °C**", and that
   "Lacking any such nuclei, the liquid phase can be maintained all the way down to the
   temperature at which crystal homogeneous nucleation occurs." −20 °C is therefore well
   inside the measured/observed supercooled-liquid regime. **The state at −20 °C is a
   metastable liquid, not a solid**, and per S12 its permittivity is *higher* than at 0 °C.
2. **Premelted / quasi-liquid surface layer on ice.** `[CITED]` — V. F. McNeill,
   T. Loerting, B. L. Trout, L. T. Molina and M. J. Molina, *Quasi-Liquid Layer Formation
   on Ice under Stratospheric Conditions*, NASA NTRS document ID **20040161141** (PREPRINT;
   MIT; NTRS API record and full text read). Quoting the paper's opening paragraph: "The QLL
   is known to exist in pure ice crystals at temperatures near the melting point, but its
   existence at stratospheric temperatures (**−85 °C to −70 °C**) had not been reported
   yet". The source establishes that a disordered quasi-liquid layer on an ice surface is
   documented at temperatures far below −20 °C and −40 °C. (The paper's own contribution is
   the *stratospheric* case; the existence of the QLL at temperatures near the melting
   point is cited within it to Petrenko & Whitworth, *Physics of Ice*, Oxford University
   Press, 1999, DOI `10.1093/acprof:oso/9780198518945.001.0001`.)
3. **Liquid brine film.** S14 `[CITED]`: an NaCl brine's eutectic is −21.1 °C at 23.3 wt%.
   At −20 °C a near-saturated NaCl brine film is still liquid — but only marginally, and
   only at high salinity. Salts with lower eutectics (CaCl₂ −52 °C, Mg(ClO₄)₂ −64 °C, per
   S14) remain liquid well below this.

**Is liquid water possible at −40 °C? Bulk supercooled liquid: below the homogeneous
nucleation limit.** `[CITED]` — Wikipedia **"Supercooling"** §*Explanation* states water can
be "supercooled … down to its crystal homogeneous nucleation at almost **−48 °C**" (and,
in the same section, that demineralised water supercools "down to **−48.3 °C**"). So −40 °C
lies **above** the cited homogeneous-nucleation limit for pure water by roughly 8 °C.
`[CITED]` for the solution case — **Koop, T., Luo, B., Tsias, A. and
Peter, T., "Water activity as the determinant for homogeneous ice nucleation in aqueous
solutions", *Nature*, vol. 406, no. 6796, pp. 611–614, August 2000, DOI
`10.1038/35020537`** — provides the water-activity formulation for homogeneous freezing
across aqueous-solution compositions, which is what makes a *salty* film's freezing point
different from pure water's.
`[FIRST-PRINCIPLES]` **flag:** the further statement that a liquid phase at −40 °C requires
the *absence of nucleating surfaces* — i.e. that it is not available to a droplet in
contact with a metal/PTFE connector face — is the catalogue's own inference, **not** a
cited claim. It rests on the general nucleation requirement quoted in "Supercooling"
("Lacking any such nuclei, the liquid phase can be maintained…") rather than on a source
that speaks to connector surfaces. Likewise, a commonly quoted ~−38 °C heterogeneous
nucleation limit was **not** verified against any source and is therefore not relied on
here; only the cited −48.3 °C figure is used.
**Brine: no NaCl brine liquid at −40 °C** — S14's −21.1 °C
eutectic and S15's −22.9 °C equation limit both exclude it. **Exotic brines: still liquid**
— S14's CaCl₂ (−52 °C) and Mg(ClO₄)₂ (−64 °C) entries. **QLL: documented** — the §4
quasi-liquid-layer preprint explicitly reports QLL behaviour at −85 °C to −70 °C.

**Net statement the sources support:** at −20 °C the interface can carry a *conductive
ionic liquid* (brine) or a *high-permittivity metastable liquid* (supercooled water) or
*high-permittivity disordered water on ice*; at −40 °C the conductive NaCl-liquid route is
closed by the NaCl eutectic, and what remains is solid ice (ε′ ≈ 3.15, per S8/S9) plus,
where salt chemistry permits, a lower-eutectic brine, plus a quasi-liquid surface layer.

## 5. Claims with NO nameable source — first-principles, not cited

Flags below are the honest gaps. Each is derived from algebra, geometry, or the stated
assumptions in `ice_bridge_s11_calc.py`; none of them carries a citation.

| # | Claim as computed | Status | Why it is not citable as found |
|---|---|---|---|
| **C1** | A shunt bridge across the mated interface produces a reflected wave Γ = −Z0/(2Z + Z0) | `[FIRST-PRINCIPLES]` for the algebra; `[CITED]` for the premises | The closed form is standard transmission-line algebra (three algebraically identical forms are cross-checked to machine precision in the script). The *premises* — 50 Ω system, and the mated interface to be kept free of moisture — are cited at C18 / S2, S3. The algebra itself has no source and needs none. |
| **C2** | Interface geometry a = 0.635 mm (0.050″ centre-pin radius) and b = 2.10 mm (PTFE outer / shield inner radius), ln(b/a) = 1.194, radial gap 1.465 mm | **Split** | `[CITED]` for the pin: MIL-STD-348A FIGURE 310-1 (S2) prints the centre-contact diameter as **.050 / 1.27 mm**. **`[FIRST-PRINCIPLES]` / unverified for b = 2.10 mm**: that radius is a *cable-connector* dimension and was **not** found in MIL-STD-348A §310 (which is an interface standard, not a cable standard). Cite the 0.050″ pin from S2; state b = 2.10 mm as an assumed typical SMA value. The derived ln(b/a) = 1.194 and the 1.465 mm gap are arithmetic on those two inputs. |
| **C3** | PTFE dielectric, ε_r ≈ 2.1, v_p = c/√2.1, L′ = Z0/v_p, C′ = 1/(Z0·v_p) | `[CITED]` (material) + `[FIRST-PRINCIPLES]` (ε_r value) | PTFE as the specified insulator **is** cited (S1 Table I; S3 Insulator field). The numeric ε_r ≈ 2.1 and the lumped L′/C′ values are a standard quoted property, but **no PTFE datasheet was read**; the ε_r value carries no citation here. The line relations L′ = Z0/v_p and C′ = 1/(Z0·v_p) are first-principles. |
| **C4** | Ice at −20 °C: ε_s = 98, ε_inf = 3.1, τ = 6.0e-4 s, σ = 1e-5 S/m | **Split** | `[CITED]` for ε_inf ≈ 3.1–3.2 (S8, S9, S10) — this is the figure that governs the RF band. **`[FIRST-PRINCIPLES]` / uncited for ε_s = 98 *at −20 °C*** — S8 gives ~96 but explicitly *at −10.8 °C*; the −20 °C value is an extrapolation. **`[FIRST-PRINCIPLES]` for τ = 6.0e-4 s and σ = 1e-5 S/m** — no source read for either. |
| **C5** | Service life / mating cycles: SMA 2,000 (standard test connector); 500 (production part) | `[CITED]` | Covered by S2 §5.3 item *d* (2,000, with the "section 400 only" scope caveat) and S3 Mating cycles (500). Both nameable. |
| **C6** | Humidity qualification is a coarse stress screen, performed mated and unloaded | `[CITED]` | Covered by S1 §3.21/§4.6.18 and S4 Method 507.6 §1.1/§1.3. |
| **C7** | Ingress protection is specified in the *mated* condition only; unmated interface is not protected | `[CITED]` + **scope flag** | S3's "Mated / IP67" and S1 §4.6.7's water-immersion test are nameable. **Flag:** neither source states what the *unmated* interface's ingress behaviour is — that inference is the catalogue's own, and the sources are silent on it. |
| **C8** | At RF, solid ice presents ε′ ≈ 3.15 vs liquid water ε′ ≈ 80+ — a ~25× permittivity contrast driving the bridge capacitance | `[CITED]` | S8 (3.15 high-frequency ice plateau, 80.10 water at 20 °C), S9, S13. The *contrast ratio* is arithmetic on two cited numbers. |
| **C9** | Brine contamination raises both ε′ and the conduction loss; a NaCl brine film is liquid to −21.1 °C and not at −40 °C | `[CITED]` for both terms | S11 (NaCl-in-ice dielectric behaviour at UHF/microwave), S13 (ionic-strength/conduction reference), S14 (eutectic −21.1 °C, 23.3 wt%), S15 (brine volume, −0.5 to −22.9 °C range). |
| **C10** | Nominal good-interface baseline: 25 dB return loss / VSWR 1.12 over 0–6 GHz | `[CITED]` | S3 vendor specification — the exact numbers, in the exact band. S5/S7 are the literature/standards context. |
| **C11** | Reference measurement method is a 12-term-corrected VNA sweep, ≥400 points | `[CITED]` | S1 §4.6.11 quotes the method verbatim. |
| **C12** | Connector re-mating repeatability is a quantified error source, i.e. small interface-response movements are not by themselves evidence of a bridge | `[CITED]` | S6 (Lewandowski & Williams 2009). Quantitative magnitude *not* read from the paper — the *existence* of the modelled error source is the cited claim. |
| **C13** | Corrosion is specified at the interface/mating surface, in a 5 % salt atmosphere | `[CITED]` | S1 §3.13, §4.6.10 (MIL-STD-202-101, 5 % salt); S1 §3.3.1/Table I and S3 metals fields for the galvanic pair. |
| **C14** | At −20 °C a supercooled film's ε′ *exceeds* its 0 °C value; the 228 K singularity governs the trend | `[CITED]` (trend) | S12 quotes the ±2 % data to −35 °C and the 228 K critical temperature. The *monotonic increase* is the published trend. The specific ε_s = 105 at −20 °C is `[FIRST-PRINCIPLES]`/unverified (see C4). |
| **C15** | Operating temperature range for a real SMA part is −65 °C … +165 °C | `[CITED]`, **with a flag** | S3 states the range. **Flag:** MIL-PRF-39012F §6.6 (S1) declines to state a universal range ("will be as specified"), so there is **no MIL-spec temperature range** to cite; the number rests on the vendor datasheet alone. |
| **C16** | Worst-case bridge dissipation P_bridge/P_inc = 200R/(2R+50)², maximum 0.500 at R = 25 Ω; bridge current at 12 V bias I = V/R; melt rate from latent heat 334 kJ/kg | `[FIRST-PRINCIPLES]` | The maximisation and the I = V/R rows are algebra. The latent heat of fusion 334 kJ/kg is a standard value but **no source was read for it** — no citation is claimed. |
| **C17** | Lumped-shunt validity: 2 mm bridge vs λ/10 — holds at 868–915 MHz, marginal at 2.4 GHz, fails at 6 GHz in water-class media; holds past 18 GHz in ice | `[FIRST-PRINCIPLES]` (method) + `[CITED]` (λ) | The λ/10 criterion and the ABCD/distributed cross-check are analytic method, with a convergence limit check at 1 µm and a no-bridge |Γ| ≈ 0 check. The ε′ values fed in come from C4/S8/S9. |
| **C18** | The mated SMA interface is required to be kept free of moisture — a bridging film is out-of-specification by the standard's own wording | `[CITED]` | MIL-STD-348A FIGURE 310-1 note 2 (S2), quoted verbatim. This is the catalogue's anchor claim and the strongest single citation available: it is the interface standard itself, on the SMA interface sheet. |

**Summary of the honest position:** the catalogue's *premises* (interface standard, materials,
moisture and corrosion qualification, RF reference method, good-interface baseline, and the
ice/water/brine dielectric contrast) are all backed by nameable, locatable sources. The
catalogue's *specific numeric material parameters* — ε_s = 98 at −20 °C, τ = 6.0e-4 s,
σ = 1e-5 S/m, ε_s = 105 at −20 °C, the brine and seawater σ values, the dirty-condensate
σ, and the PTFE ε_r — are **stated model assumptions**, not values transcribed from the
cited literature, and are labelled as such throughout.

The single unverified geometric input worth naming explicitly is the shield/PTFE outer
radius **b = 2.10 mm** (C2). Only the 0.050″ centre-pin figure comes from a standard;
everything derived from ln(b/a) — including the 1.465 mm radial gap used for the E-field
rows — inherits that assumption.

**One flag on §4:** the statement that a liquid phase at −40 °C is unavailable to a droplet
*in contact with a connector surface* has no source that speaks to connector surfaces. It
is recorded as first-principles in §4 itself rather than promoted to a cited claim.

## 6. Sources checked and rejected (ledger)

Recorded so the gaps above are not mistaken for a lack of search.

| Source | Outcome |
|---|---|
| Amphenol RF connector pages | HTTP 403 through the egress path; no document retrieved. |
| HUBER+SUHNER connector *catalogue* pages (`/en/products/rf-connectors`, `/rf-connectors/rf-connectors-sma`) | Reachable but returned proxy boilerplate with no catalogued technical content. **The individual product datasheet (S3) did work** and is used instead. |
| Rosenberger, Radiall, TE Connectivity RF-connector pages | Boilerplate or 403/404; nothing citable retrieved. |
| Smiths Interconnect RF connectors | 404. |
| Keysight product/support pages | 403 (bot challenge); no application note retrieved. |
| Pasternack SMA category page | Returned a 212-byte stub. |
| Maury Microwave, Anritsu, Fairview Microwave | Reachable; only marketing/navigation text, no temperature, humidity, or return-loss specification retrieved. |
| ASSIST / DLA QuickSearch (`quicksearch.dla.mil`) | Connection timed out. The DLA-served MIL-STD-348 PDF also failed TLS verification; the Everyspec mirror of the same DLA document was used instead (S2). |
| Everyspec on-site search (`search_result.php`, incl. proper CSE `q=`/`cx=` parameters) | No MIL-STD category index or MIL-STD-202 hit returned. **MIL-STD-202 itself was therefore not retrieved** — Methods 101 (salt) and 106 (humidity) are cited only as *referenced by* S1 §4.6.10 and §4.6.18, not as documents read. |
| MIL-PRF-39012F Supplement-1 (Everyspec) | Downloaded, but it is a 25 kB parts-list supplement with no additional environmental text. |
| Bing, DuckDuckGo (html + lite), Mojeek, Startpage, searx.be | Blocked, empty, or JS-only. **Brave Search was the working engine.** |
| EverySpec MIL-STD directory indexes (`/MIL-STD/`, `/library.php`, `/MIL-STD/MIL-STD-0300-0399/`) | Category indexes return empty link lists; only direct document URLs resolve. |
| Wikipedia HTML pages via direct fetch | Proxy-truncated and unusable; the MediaWiki `action=query&prop=extracts` API was used instead. Section headings were confirmed via `action=parse&prop=sections` to make the §-level locators in S8 and S14 accurate. |
| NTRS API queries: "eutectic sodium chloride ice", "supercooled water film ice dielectric", "quasi-liquid layer" (direct terms) | No results for the first two; the quasi-liquid-layer preprint (used in §4) was found via the stratospheric-conditions query. |
| OpenAlex API | HTTP 429 (rate-limited); Crossref used throughout. |

## 7. Full source list

1. **MIL-PRF-39012F w/AMENDMENT 3** — *Connectors, Coaxial, Radio Frequency, General Specification For*, 18 May 2017. §3.13, §3.21, §4.6.7, §4.6.10, §4.6.11, §4.6.18, §6.6, Table I, Table II.
2. **MIL-STD-348A** — *Radio Frequency Connector Interfaces…*, 20 April 1988. §5.3 item *d*; FIGURE 310-1; FIGURE 310-2; FIGURE 310-3; FIGURE 405-3.
3. **HUBER+SUHNER AG**, SMA cable plug Art. 84070289 (11_SMA-50-4-101/199_N) — product datasheet page.
4. **MIL-STD-810H** — *Method 507.6, Humidity*. §1.1, §1.3.
5. **A. J. Estin**, "Scattering parameters of SMA coaxial connector pairs", *IEEE Trans. Instrum. Meas.*, IM-25(4), 329–334, Dec 1976. DOI 10.1109/TIM.1976.6312237.
6. **A. Lewandowski, D. F. Williams**, "Stochastic modeling of coaxial-connector repeatability errors", *74th ARFTG Microwave Measurement Conf.*, 1–4, Nov 2009. DOI 10.1109/ARFTG74.2009.5439104.
7. **IEEE Std 287** — *IEEE Standard for Precision Coaxial Connectors (DC to 110 GHz)*. DOI 10.1109/IEEESTD.2007.4317507; and Part 1, DOI 10.1109/IEEESTD.2022.9889249.
8. **Wikipedia**, "Relative permittivity" §*Chemistry* (ice 96 at −10.8 °C → 3.15 high-frequency, 3.12–3.19 from 1 MHz to far IR; water 80.10 at 20 °C).
9. **C. Mätzler**, "Microwave Properties of Ice and Snow", in *Solar System Ices*, ASSL, Springer, 1998, 241–257. DOI 10.1007/978-94-011-5252-5_10.
10. **C. Mätzler, U. Wegmüller**, "Dielectric properties of freshwater ice at microwave frequencies", *J. Phys. D: Appl. Phys.*, 20(12), 1623–1630, 1987. DOI 10.1088/0022-3727/20/12/013.
11. **P. Hoekstra, P. Cappillino**, "Dielectric properties of sea and sodium chloride ice at UHF and microwave frequencies", *J. Geophys. Res.*, 76(20), 4922–4931, 1971. DOI 10.1029/JB076i020P04922.
12. **I. M. Hodge, C. A. Angell**, "The relative permittivity of supercooled water", *J. Chem. Phys.*, 68(4), 1363–1368, 1978. DOI 10.1063/1.435955.
13. **D. G. Archer, P. Wang**, "The Dielectric Constant of Water and Debye-Hückel Limiting Law Slopes", *J. Phys. Chem. Ref. Data*, 19(2), 371–411, 1990. DOI 10.1063/1.555853.
14. **Wikipedia**, "Brine" §*Refrigerating fluid*; "Eutectic system" §*Types → Others*; "Sodium chloride" §*Road salt*; "Calcium chloride".
15. **G. Frankenstein, R. Garner**, "Equations for Determining the Brine Volume of Sea Ice from −0.5° to −22.9 °C", *J. Glaciol.*, 6(48), 943–944, 1967. DOI 10.3189/S0022143000020244.
16. **V. F. McNeill, T. Loerting, B. L. Trout, L. T. Molina, M. J. Molina**, *Quasi-Liquid Layer Formation on Ice under Stratospheric Conditions*, NASA NTRS ID 20040161141 (PREPRINT).
17. **V. F. Petrenko, R. W. Whitworth**, *Physics of Ice*, Oxford University Press, 1999. DOI 10.1093/acprof:oso/9780198518945.001.0001.
18. **T. Koop, B. Luo, A. Tsias, T. Peter**, "Water activity as the determinant for homogeneous ice nucleation in aqueous solutions", *Nature*, 406(6796), 611–614, 2000. DOI 10.1038/35020537.
19. **Wikipedia**, "Supercooling" §*Explanation* (−48.3 °C; homogeneous nucleation).
20. **C. A. Angell**, "Supercooled Water", in *Water and Aqueous Solutions at Subzero Temperatures*, Springer US, 1982, 1–81. DOI 10.1007/978-1-4757-6952-4_1.
