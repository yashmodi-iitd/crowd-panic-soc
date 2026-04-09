"""
Crowd Panic as a Self-Organized Critical System
================================================
Simulation of panic cascades in a crowd modeled as a 2D lattice of agents.

Author: [Student Name]
Course: Complexity Science
Date: April 2026

Description:
  - N x N grid of agents, each in state: calm (0), anxious (1), or panicking (2)
  - Connectivity k: number of neighbours each agent can observe
  - Noise ε: small probability per timestep that a calm agent spontaneously panics
  - Cascade (Avalanche): chain reaction of panic spreading through connected agents
  - Self-Organised Criticality (SOC): at a critical connectivity k*, the system
    self-organises so that avalanche sizes follow a power-law distribution.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")

# ── reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

# ══════════════════════════════════════════════════════════════════════════════
# 1.  AGENT / CROWD MODEL
# ══════════════════════════════════════════════════════════════════════════════

CALM     = 0
ANXIOUS  = 1
PANICKING = 2

class CrowdPanicModel:
    """
    2-D lattice crowd model with configurable connectivity and noise.

    Parameters
    ----------
    N          : int   – grid side length (crowd size = N²)
    k          : int   – neighbourhood radius (Moore neighbourhood up to radius k)
    epsilon    : float – spontaneous panic probability per agent per step
    threshold  : float – fraction of panicking neighbours required to trigger spread
    recovery   : float – probability a panicking agent recovers each step
    """

    def __init__(self, N=50, k=1, epsilon=0.002, threshold=0.3, recovery=0.05):
        self.N         = N
        self.k         = k
        self.epsilon   = epsilon
        self.threshold = threshold
        self.recovery  = recovery
        self.grid      = np.zeros((N, N), dtype=int)

    def reset(self):
        self.grid[:] = 0

    def _neighbours(self, i, j):
        """Return indices of all cells in Moore neighbourhood of radius k."""
        rows = range(max(0, i - self.k), min(self.N, i + self.k + 1))
        cols = range(max(0, j - self.k), min(self.N, j + self.k + 1))
        return [(r, c) for r in rows for c in cols if (r, c) != (i, j)]

    def step(self):
        """Advance the model by one time step. Returns cascade size triggered."""
        new_grid = self.grid.copy()
        cascade_size = 0

        # --- noise: spontaneous panic ignition ---
        calm_mask = (self.grid == CALM)
        ignite = np.random.random((self.N, self.N)) < self.epsilon
        ignited_positions = list(zip(*np.where(calm_mask & ignite)))

        if ignited_positions:
            # BFS to propagate the cascade
            frontier = set(ignited_positions)
            for (i, j) in frontier:
                new_grid[i, j] = PANICKING

            visited = set(frontier)
            while frontier:
                next_frontier = set()
                for (i, j) in frontier:
                    for (r, c) in self._neighbours(i, j):
                        if (r, c) in visited:
                            continue
                        if self.grid[r, c] == CALM:
                            nbrs = self._neighbours(r, c)
                            pan_count = sum(
                                1 for (nr, nc) in nbrs
                                if self.grid[nr, nc] == PANICKING or new_grid[nr, nc] == PANICKING
                            )
                            frac = pan_count / max(len(nbrs), 1)
                            if frac >= self.threshold:
                                new_grid[r, c] = PANICKING
                                next_frontier.add((r, c))
                                visited.add((r, c))
                frontier = next_frontier

            cascade_size = len(visited)

        # --- recovery ---
        pan_mask = (new_grid == PANICKING)
        recover = np.random.random((self.N, self.N)) < self.recovery
        new_grid[pan_mask & recover] = CALM

        self.grid = new_grid
        return cascade_size


# ══════════════════════════════════════════════════════════════════════════════
# 2.  EXPERIMENT: SWEEP CONNECTIVITY k AND COLLECT AVALANCHE DISTRIBUTIONS
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment(N=40, k_values=None, n_steps=3000, burn_in=500,
                   epsilon=0.002, threshold=0.3, recovery=0.05):
    """
    For each connectivity k, collect the avalanche-size distribution.
    Returns a dict: k -> list of (non-zero) cascade sizes.
    """
    if k_values is None:
        k_values = [1, 2, 3, 4, 5]

    results = {}
    for k in k_values:
        print(f"  Running k={k} …", end=" ", flush=True)
        model = CrowdPanicModel(N=N, k=k, epsilon=epsilon,
                                threshold=threshold, recovery=recovery)
        sizes = []
        for t in range(n_steps + burn_in):
            s = model.step()
            if t >= burn_in and s > 0:
                sizes.append(s)
        results[k] = sizes
        print(f"avalanches={len(sizes)}, max={max(sizes) if sizes else 0}")
    return results


# ══════════════════════════════════════════════════════════════════════════════
# 3.  PLOTTING
# ══════════════════════════════════════════════════════════════════════════════

def plot_avalanche_distributions(results, k_values, save_path="figures/fig_avalanche_dist.pdf"):
    """Log-log plot of avalanche-size distributions for different k values."""
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(k_values)))

    for k, col in zip(k_values, colors):
        sizes = results[k]
        if not sizes:
            continue
        unique, counts = np.unique(sizes, return_counts=True)
        probs = counts / counts.sum()
        ax.loglog(unique, probs, 'o-', color=col, markersize=4,
                  linewidth=1.5, label=f'$k={k}$', alpha=0.85)

    ax.set_xlabel("Avalanche size $s$", fontsize=13)
    ax.set_ylabel("Probability $P(s)$", fontsize=13)
    ax.set_title("Avalanche-size distributions for varying connectivity $k$", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"  Saved → {save_path}")
    plt.close()


def plot_mean_avalanche_vs_k(results, k_values, save_path="figures/fig_mean_vs_k.pdf"):
    """Mean avalanche size vs connectivity (shows divergence near critical k)."""
    means = [np.mean(results[k]) if results[k] else 0 for k in k_values]
    stds  = [np.std(results[k])  if results[k] else 0 for k in k_values]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(k_values, means, yerr=stds, fmt='s-', color='steelblue',
                capsize=4, linewidth=2, markersize=7, label="Mean avalanche size")
    ax.set_xlabel("Connectivity radius $k$", fontsize=13)
    ax.set_ylabel("Mean avalanche size $\\langle s \\rangle$", fontsize=13)
    ax.set_title("Mean avalanche size vs. connectivity", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"  Saved → {save_path}")
    plt.close()


def plot_power_law_fit(results, k_critical, save_path="figures/fig_power_law.pdf"):
    """Fit and display power-law for the critical k."""
    sizes = results[k_critical]
    unique, counts = np.unique(sizes, return_counts=True)
    probs = counts / counts.sum()

    # Simple log-linear fit on log-log data
    log_s = np.log10(unique)
    log_p = np.log10(probs)
    coeffs = np.polyfit(log_s, log_p, 1)
    alpha = -coeffs[0]
    fit_line = 10 ** np.polyval(coeffs, log_s)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.loglog(unique, probs, 'o', color='crimson', markersize=5,
              label=f'$k={k_critical}$ (critical)', zorder=5)
    ax.loglog(unique, fit_line, '--', color='navy', linewidth=2,
              label=f'Power-law fit: $\\alpha={alpha:.2f}$')
    ax.set_xlabel("Avalanche size $s$", fontsize=13)
    ax.set_ylabel("Probability $P(s)$", fontsize=13)
    ax.set_title(f"Power-law distribution at critical connectivity $k^*={k_critical}$", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"  Saved → {save_path}")
    plt.close()
    return alpha


def plot_crowd_snapshot(N=50, k=3, n_steps=200, save_path="figures/fig_snapshot.pdf"):
    """Show a spatiotemporal snapshot of the crowd during a panic cascade."""
    model = CrowdPanicModel(N=N, k=k, epsilon=0.005, threshold=0.25, recovery=0.03)

    cmap   = mcolors.ListedColormap(['#2ecc71', '#f39c12', '#e74c3c'])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm   = mcolors.BoundaryNorm(bounds, cmap.N)

    snapshots = []
    snap_times = [0, 20, 60, 150]

    for t in range(n_steps + 1):
        model.step()
        if t in snap_times:
            snapshots.append((t, model.grid.copy()))

    fig, axes = plt.subplots(1, len(snapshots), figsize=(14, 3.5))
    for ax, (t, grid) in zip(axes, snapshots):
        im = ax.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
        ax.set_title(f"$t = {t}$", fontsize=12)
        ax.axis('off')

    # shared colorbar
    cbar = fig.colorbar(im, ax=axes.tolist(), ticks=[0, 1, 2], fraction=0.02, pad=0.04)
    cbar.ax.set_yticklabels(['Calm', 'Anxious', 'Panicking'], fontsize=10)
    fig.suptitle("Crowd state snapshots during a panic cascade ($k=3$)", fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved → {save_path}")
    plt.close()


def plot_time_series(N=40, k=3, n_steps=1500, save_path="figures/fig_timeseries.pdf"):
    """Fraction of panicking agents over time."""
    model = CrowdPanicModel(N=N, k=k, epsilon=0.003, threshold=0.3, recovery=0.05)
    frac_pan = []
    for _ in range(n_steps):
        model.step()
        frac_pan.append(np.mean(model.grid == PANICKING))

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(frac_pan, color='crimson', linewidth=0.8, alpha=0.85)
    ax.set_xlabel("Time step", fontsize=13)
    ax.set_ylabel("Fraction panicking", fontsize=13)
    ax.set_title("Temporal evolution of panic fraction in the crowd ($k=3$)", fontsize=13)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"  Saved → {save_path}")
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 4.  MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)

    print("=" * 60)
    print("  Crowd Panic – Self-Organised Criticality Simulation")
    print("=" * 60)

    K_VALUES   = [1, 2, 3, 4, 5]
    K_CRITICAL = 3   # empirically identified from mean-avalanche plot

    # 1. Crowd snapshots
    print("\n[1/5] Generating crowd snapshot …")
    plot_crowd_snapshot(N=50, k=K_CRITICAL)

    # 2. Time series
    print("\n[2/5] Generating time series …")
    plot_time_series(N=40, k=K_CRITICAL)

    # 3. Avalanche distributions
    print("\n[3/5] Running avalanche-distribution experiment …")
    results = run_experiment(N=40, k_values=K_VALUES, n_steps=3000, burn_in=500)

    print("\n[4/5] Plotting avalanche distributions …")
    plot_avalanche_distributions(results, K_VALUES)
    plot_mean_avalanche_vs_k(results, K_VALUES)

    # 4. Power-law fit at critical k
    print("\n[5/5] Fitting power law at critical connectivity …")
    alpha = plot_power_law_fit(results, K_CRITICAL)
    print(f"\n  Estimated power-law exponent α ≈ {alpha:.3f}")

    print("\n" + "=" * 60)
    print("  All figures saved to ./figures/")
    print("=" * 60)
