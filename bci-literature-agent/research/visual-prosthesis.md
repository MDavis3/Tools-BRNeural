# Cortical Visual Prosthesis Research: Summary for Blackrock 2028 Goal

## Executive Summary
Blackrock has announced plans for first-in-human Neuralace visual prosthesis demonstrations by 2028. This summary covers the current state of cortical visual prosthesis research, key challenges, and strategic recommendations.

## Current Visual Prosthesis Landscape

### Retinal Prostheses (Bypass Eye)
| Device | Electrodes | Status | Company |
|--------|------------|--------|---------|
| Argus II | 60 | FDA approved 2013, discontinued | Second Sight |
| Alpha-IMS/AMS | 1,600 | CE Mark, discontinued | Retina Implant AG |
| PRIMA | 378 | Clinical trials | Pixium Vision |

**Limitation:** Require intact optic nerve and visual cortex - not suitable for complete blindness.

### Cortical Prostheses (Direct Brain Stimulation)
| Device | Electrodes | Status | Institution |
|--------|------------|--------|-------------|
| Orion | 60 | 5-year feasibility complete | Cortigent/Vivani |
| Intracortical Visual Prosthesis | 625 | Research | Monash University |
| ICVP | 400 | Clinical trials | Illinois/NIH |
| **Neuralace Visual** | **10,000+** | **Planned 2028** | **Blackrock** |

## Orion Visual Cortical Prosthesis: Current Gold Standard

### System Overview
- 60 electrodes on visual cortex surface
- External glasses with camera
- Wireless data/power transmission
- Stimulation creates phosphenes (spots of light)

### 5-Year Clinical Results (2023)
**Key Findings:**
1. All 6 participants completed study
2. Improved real-world task performance:
   - Navigating sidewalks
   - Finding doorways
   - Locating objects
3. Stable phosphene perception over 5 years
4. No serious adverse events

**Limitations:**
- Only 60 phosphenes = very low "resolution"
- Approximately 20/10,000 visual acuity equivalent
- Useful for mobility but not reading or faces

### FDA Breakthrough Device Designation (2024)
Orion received Breakthrough Device status - indicates FDA support for expedited review.

## The Challenge: Visual Acuity Requirements

### What's Needed for Useful Vision
| Task | Required Resolution | Estimated Electrodes |
|------|---------------------|---------------------|
| Mobility/obstacle avoidance | 20/2000 | ~100 |
| Face recognition | 20/200 | ~1,000 |
| Reading large text | 20/100 | ~2,500 |
| Normal reading | 20/40 | ~10,000+ |

### The 10,000 Channel Opportunity
Neuralace's 10,000+ channel count could enable:
- Large text reading
- Basic face recognition
- Greatly improved mobility
- More natural phosphene integration

## Key Scientific Challenges

### 1. Phosphene Mapping
**Problem:** Electrode position doesn't linearly map to visual field
**Current approach:** Individual calibration of each electrode
**Challenge at scale:** 10,000 electrodes = massive calibration burden

**Solutions being explored:**
- Machine learning for automated mapping
- Standardized electrode placement protocols
- Adaptive algorithms that learn over time

### 2. Phosphene Quality
**Observations from trials:**
- Phosphene size varies (0.1° to 5°)
- Brightness perception varies
- Some electrodes produce no phosphene
- Phosphenes can be colored, patterned

**Implications for Neuralace:**
- Need redundancy (not all electrodes will work)
- Stimulation parameters require individual optimization

### 3. Temporal Dynamics
**Challenge:** Creating smooth, continuous vision from discrete stimulation
- Individual phosphenes fade within 100-500 ms
- Rapid sequential stimulation needed for motion
- Interaction effects between adjacent electrodes

### 4. Cortical Coverage
**V1 (primary visual cortex) anatomy:**
- Surface area: ~3,000 mm²
- Central vision (fovea) representation: very small cortical area
- Peripheral vision: larger cortical area

**Implication:** High electrode density in foveal representation area is critical.

## Emerging Technologies Relevant to Neuralace Visual Prosthesis

### 1. High-Density Surface Arrays (UCSD 2025)
- 1,024 channels achieved on cortical surface
- Micro-slit implantation - minimally invasive
- Could be scaled to multiple arrays covering V1

### 2. Optogenetic Approaches
- Gene therapy to make neurons light-sensitive
- LED-based stimulation instead of electrical
- Potentially higher spatial resolution

**Note:** Not compatible with traditional BCI approach but worth monitoring.

### 3. Current Steering
- Use multiple electrodes to shape stimulation field
- Create virtual electrodes between physical electrodes
- Could effectively increase resolution beyond channel count

### 4. Closed-Loop Systems
- Record neural activity while stimulating
- Adapt stimulation based on brain response
- Could improve phosphene consistency

## Strategic Recommendations for Blackrock

### Near-Term (2024-2025)
1. **Initiate collaboration with Nader Pouratian** (Orion PI)
   - Learn from 5-year clinical experience
   - Understand FDA pathway
   - Identify safety concerns

2. **Develop V1 electrode placement strategy**
   - Work with neuroradiologists on targeting
   - Consider multiple Neuralace arrays to cover V1
   - Prioritize foveal representation

3. **Build phosphene mapping algorithms**
   - Partner with Stanford ML groups
   - Develop automated calibration
   - Create simulation tools

### Medium-Term (2025-2027)
1. **Animal studies with high-channel visual stimulation**
   - Non-human primates for cortical mapping
   - Demonstrate stable long-term stimulation

2. **Develop integrated camera/processor system**
   - Real-time image to stimulation conversion
   - Low-latency critical for usability

3. **FDA Pre-Submission meetings**
   - Early engagement on regulatory pathway
   - Build on Orion's Breakthrough Device precedent

### 2028 First-in-Human
1. **Patient selection criteria**
   - Complete blindness (both eyes)
   - No cortical damage
   - Strong motivation for rehabilitation

2. **Realistic expectations**
   - Focus on mobility improvement
   - Don't promise "sight restoration"
   - Plan for extensive training/rehabilitation

## Competitive Intelligence

### Monash University (Australia)
- 625-electrode intracortical system
- Tiles placed across visual cortex
- Currently in clinical trials

### Second Sight/Cortigent
- Orion is only cortical prosthesis with 5-year human data
- Company acquired by Vivani Medical
- Uncertain commercial future

### Potential New Entrants
- Neuralink has mentioned visual restoration
- University of Pittsburgh working on visual BCI
- Multiple academic groups advancing technology

## Key Metrics for Success

| Metric | Orion Current | Neuralace Target |
|--------|---------------|------------------|
| Electrode count | 60 | 10,000+ |
| Visual acuity equivalent | 20/10,000 | 20/500 |
| Calibration time | Days | Hours |
| Implant procedure | Craniotomy | Micro-slit |
| First-in-human | 2017 | 2028 |

## Critical Success Factors

1. **Channel count matters:** 10,000+ is a genuine differentiator
2. **Minimally invasive:** Neuralace's flexible design advantage
3. **FDA relationship:** Build early, leverage Orion precedent
4. **Realistic claims:** Mobility improvement is achievable; "sight" is not
5. **Rehabilitation program:** Device alone isn't enough - training essential
