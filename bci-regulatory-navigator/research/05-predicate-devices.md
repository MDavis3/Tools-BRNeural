# FDA Predicate Devices for Brain-Computer Interfaces

## Overview

Predicate devices are legally marketed devices that can be used to support a 510(k) substantial equivalence claim. This document catalogs key predicates for BCI regulatory submissions.

---

## Class II Cortical Electrodes (21 CFR 882.1310)

### Regulation Text
> "A cortical electrode is an electrode which is temporarily placed on the surface of the brain for stimulating the brain or recording the brain's electrical activity."

**Product Code:** GYC
**Classification:** Class II (Special Controls)

---

## Key Predicate Devices

### 1. Ad-Tech Subdural Electrodes

| Field | Value |
|-------|-------|
| **510(k) Number** | K191186 |
| **Clearance Date** | January 2020 |
| **Manufacturer** | Ad-Tech Medical Instrument Corp. |
| **Regulation** | 21 CFR 882.1310 |
| **Product Code** | GYC |

#### Intended Use
Temporary implantation (<30 days) on cortical surface for:
- Recording electrical signals
- Monitoring electrical signals
- Stimulation of electrical signals

#### Clinical Applications
- Localization of epileptogenic foci
- Functional brain mapping
- Pre-surgical planning

#### Technical Characteristics
- Silicone elastomer substrate
- Platinum/iridium contacts
- Insulated lead-wires
- Various geometries: strip, grid, dual-sided, inter-hemispheric

#### Significance as Predicate
- **Primary predicate** for Precision Neuroscience Layer 7-T
- Well-established safety profile
- Decades of clinical use
- Same intended use as modern BCI electrodes

---

### 2. NeuroOne Evo Cortical Electrode

| Field | Value |
|-------|-------|
| **510(k) Number** | K192764 |
| **Clearance Date** | 2020 |
| **Manufacturer** | NeuroOne Medical Technologies |
| **Regulation** | 21 CFR 882.1310 |
| **Product Code** | GYC |

#### Intended Use
Temporary cortical recording and stimulation

#### Technical Characteristics
- **Polyimide thin-film array** (key difference from Ad-Tech)
- Higher channel density than traditional grids
- Flexible substrate

#### Significance as Predicate
- Demonstrates FDA acceptance of polyimide materials
- Bridge between traditional electrodes and modern BCIs
- **Reference predicate** for Precision Neuroscience

---

### 3. Blackrock NeuroPort Cortical Microelectrode Array System

| Field | Value |
|-------|-------|
| **510(k) Number** | K110010 |
| **Original Clearance** | K070272 (August 2007) |
| **Manufacturer** | Blackrock Microsystems (now Blackrock Neurotech) |
| **Regulation** | 21 CFR 882.1310 |
| **Product Code** | GYC |

#### Intended Use
- Temporary (<30 day) cortical recording
- Neural activity monitoring
- Research applications

#### Technical Characteristics
- Silicon substrate
- 96 microelectrodes
- Platinum or iridium oxide tips
- Intracortical penetrating electrodes

#### Significance
- **Gold standard** for intracortical BCI research
- Only FDA-cleared intracortical array for human use under IDE
- Basis for Blackrock's MoveAgain system

---

### 4. PMT/DIXI Depth Electrodes

| Field | Value |
|-------|-------|
| **510(k) Number** | K170896 |
| **Manufacturer** | PMT Corporation / DIXI Medical |
| **Regulation** | 21 CFR 882.1310 |
| **Product Code** | GYE (Depth Electrode) |

#### Intended Use
Temporary depth recording for epilepsy monitoring (SEEG)

#### Significance
- Demonstrates pathway for penetrating electrodes
- Different product code (GYE) for depth vs surface

---

### 5. Medtronic DBS Lead

| Field | Value |
|-------|-------|
| **PMA Number** | P960009 |
| **Manufacturer** | Medtronic |
| **Class** | III |

#### Significance
- **NOT a 510(k) predicate** (Class III, PMA)
- Demonstrates regulatory pathway for permanent implants
- Establishes safety precedent for chronic neural stimulation

---

## Product Code Reference

### GYC - Cortical Electrode
- Surface electrodes (subdural grids, strips)
- Temporary use (<30 days)
- Class II

### GYE - Depth Electrode
- Penetrating/subsurface electrodes
- Class II (with special controls)

### GWF - Electroencephalograph
- Recording equipment (not electrodes)
- Class II

### LYY - Cranial Electrotherapy Stimulator
- External stimulation devices
- Class II

### PHL - Implanted Brain Stimulator for Pain
- Class III (PMA required)

---

## Predicate Selection Strategy

### Decision Tree

```
Is your device a surface electrode?
├── YES → Consider GYC predicates (Ad-Tech, NeuroOne)
│         Is it temporary (<30 day)?
│         ├── YES → Strong 510(k) case
│         └── NO → Consider PMA or De Novo
└── NO → Is it a depth/penetrating electrode?
         ├── YES → Consider GYE predicates or K110010
         │         Is it temporary (<30 day)?
         │         ├── YES → 510(k) may be possible
         │         └── NO → Likely PMA
         └── Is it a complete BCI system?
                  └── YES → Likely PMA (Class III)
                           Consider Breakthrough designation
```

### Key Considerations

1. **Match Intended Use Exactly**
   - Same patient population
   - Same clinical application
   - Same duration of implantation

2. **Technological Differences Are Acceptable If:**
   - Same or lower risk profile
   - Bench testing demonstrates equivalence
   - No new questions of safety/effectiveness

3. **Document Material Changes**
   - Biocompatibility testing for new materials
   - Animal studies if significant changes
   - FDA may require additional data

4. **Use Multiple Predicates Strategically**
   - Primary predicate: Same intended use
   - Reference predicates: Similar technology

---

## 510(k) Clearance Database

### Recent Cortical Electrode Clearances

| 510(k) | Device | Company | Date |
|--------|--------|---------|------|
| K242618 | Layer 7-T | Precision Neuroscience | March 2025 |
| K192764 | Evo Cortical | NeuroOne | 2020 |
| K191186 | Subdural Electrodes | Ad-Tech | January 2020 |
| K151354 | INTEGRA Cortical | INTEGRA | December 2015 |
| K110010 | NeuroPort Array | Blackrock | 2011 |
| K070272 | NeuroPort Electrode | Blackrock | August 2007 |

---

## Implications for Blackrock

### Current Portfolio
- NeuroPort (K110010) is cleared as Class II predicate
- Could serve as predicate for similar devices

### MoveAgain Strategy Options

**Option 1: 510(k) for Components**
- Clear electrode array via 510(k) (predicate: K110010)
- Pursue separate pathway for full system

**Option 2: De Novo for Full System**
- Novel device type argument
- Creates new classification

**Option 3: PMA for Full System**
- Class III pathway
- Most rigorous but clearest for full BCI

### Neuralace Strategy Options

**Option 1: 510(k) as Enhanced Electrode**
- Predicate: NeuroPort (K110010) or Ad-Tech (K191186)
- Limit to temporary recording
- Novel form factor may raise questions

**Option 2: De Novo**
- Novel technology argument
- Higher channel count justifies new classification

---

## References

1. FDA 510(k) Database
2. 21 CFR 882 Subpart B - Neurological Diagnostic Devices
3. Precision Neuroscience K242618 Summary
4. FDA Product Classification Database
