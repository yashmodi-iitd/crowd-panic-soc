# Crowd Panic as a Self-Organised Critical System

> **Individual Project — Complexity Science**  

---

## Overview

This repository contains the simulation code and report for modelling **crowd panic** through the lens of **Self-Organised Criticality (SOC)**.

A crowd under stress is modelled as a 2-D lattice of agents that can be *calm*, *anxious*, or *panicking*. When the social connectivity reaches a critical value, the distribution of panic cascade sizes follows a **power law** — the hallmark of SOC — meaning that catastrophic, crowd-wide panics are always possible and cannot be predicted from typical behaviour.

---

## Key Concepts

| SOC Concept | Crowd Analogue |
|-------------|----------------|
| **Noise** (slow driving) | Spontaneous panic ignition — rumours, loud noises, physiological stress |
| **Avalanche** (fast relaxation) | Cascade propagation of panic through socially connected agents |
| **Connectivity** (control parameter) | Social / observational links between crowd members (density, line-of-sight, technology) |
| **Critical state** | Power-law avalanche size distribution; maximal susceptibility to perturbations |

---

## Repository Structure

```
crowd-panic-soc/
├── simulation.py          # Main simulation and plotting code
├── figures/               # Generated figures (PDF)
│   ├── fig_snapshot.pdf
│   ├── fig_timeseries.pdf
│   ├── fig_avalanche_dist.pdf
│   ├── fig_mean_vs_k.pdf
│   └── fig_power_law.pdf
├── crowd_panic_soc.tex    # LaTeX source of the manuscript
├── crowd_panic_soc.pdf    # Compiled PDF report
└── README.md              # This file
```

---

## Installation

Requires **Python 3.8+**.

```bash
git clone https://github.com/[username]/crowd-panic-soc.git
cd crowd-panic-soc
pip install numpy matplotlib
```

No other dependencies are needed.

---

## Usage

Run the full simulation (generates all figures):

```bash
python simulation.py
```

This will:
1. Generate spatial snapshots of the crowd during a panic cascade
2. Plot the temporal evolution of the panic fraction
3. Run the connectivity sweep (`k = 1 … 5`) and collect avalanche distributions
4. Fit and display the power-law at the critical connectivity `k* = 3`

All figures are saved to `./figures/`.

---

## Model Summary

- **Grid:** N × N square lattice of agents (`N = 40` default)
- **States:** CALM (0), ANXIOUS (1), PANICKING (2)
- **Connectivity radius k:** Moore neighbourhood of radius k
- **Noise rate ε = 0.002:** probability per agent per step of spontaneous panic
- **Propagation threshold θ = 0.30:** fraction of panicking neighbours required to spread panic
- **Recovery rate ρ = 0.05:** probability per step that a panicking agent calms down

### Key finding

At **k* = 3**, the avalanche-size distribution follows:

```
P(s) ∝ s^{−α},   α ≈ 0.27
```

indicating a self-organised critical state.

---

## Report

The full manuscript (`crowd_panic_soc.pdf`) is structured as a peer-reviewed journal article and includes:

- Justification of crowd panic as an SOC candidate
- Description of noise, avalanche, and connectivity in the crowd context
- Full model equations and parameter table
- Simulation results with figures
- Power-law analysis and connectivity sweep
- Discussion of SOC implications for crowd safety
- List of AI prompts used

---

## Acknowledgements

- **Per Bak, Chao Tang, Kurt Wiesenfeld** — foundational SOC theory (1987)
- **Dirk Helbing et al.** — panic dynamics framework (2000)
- **Anthropic Claude (claude-sonnet-4, April 2026)** — AI assistance for model design, code structure, and LaTeX typesetting

---

## License

MIT License — free to use with attribution.
