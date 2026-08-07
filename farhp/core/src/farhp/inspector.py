from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .model import FARHPFrame, FARHPTrajectory


def save_frame_plot(frame: FARHPFrame, waveform: np.ndarray, path: str | Path) -> None:
    t = np.arange(waveform.size) / frame.sample_rate_hz
    k = np.asarray(frame.harmonic_indices)
    amplitude = np.asarray(frame.amplitudes)
    psi = np.asarray(frame.farhp_rad)

    fig = plt.figure(figsize=(10, 8), constrained_layout=True)
    grid = fig.add_gridspec(3, 1)
    ax1 = fig.add_subplot(grid[0, 0])
    ax1.plot(t, waveform)
    ax1.set_title("Waveform")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")

    ax2 = fig.add_subplot(grid[1, 0])
    ax2.stem(k, amplitude)
    ax2.set_title("Harmonic amplitudes")
    ax2.set_xlabel("Harmonic index")
    ax2.set_ylabel("Amplitude")

    ax3 = fig.add_subplot(grid[2, 0])
    ax3.scatter(k[1:], psi[1:])
    ax3.set_title("FARHP coordinates")
    ax3.set_xlabel("Harmonic index")
    ax3.set_ylabel("Phase (rad)")
    ax3.set_ylim(-np.pi, np.pi)
    ax3.set_yticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    ax3.set_yticklabels(["-π", "-π/2", "0", "π/2", "π"])

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _to_float_matrix(rows: list[list[float | None]]) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value for value in row] for row in rows], dtype=float)


def save_trajectory_plot(
    trajectory: FARHPTrajectory,
    waveform: np.ndarray,
    path: str | Path,
    *,
    max_harmonics: int = 12,
) -> None:
    times = np.asarray(trajectory.frame_times_sec, dtype=float)
    f0 = np.asarray([np.nan if value is None else value for value in trajectory.f0_hz], dtype=float)
    confidence = np.asarray(trajectory.track_confidence, dtype=float)
    anchor = np.asarray(
        [np.nan if value is None else value for value in trajectory.anchor_unwrapped_rad], dtype=float
    )
    psi = _to_float_matrix(trajectory.farhp_unwrapped_rad)
    t_audio = np.arange(waveform.size) / trajectory.sample_rate_hz

    fig = plt.figure(figsize=(12, 11), constrained_layout=True)
    grid = fig.add_gridspec(5, 1)
    ax1 = fig.add_subplot(grid[0, 0])
    ax1.plot(t_audio, waveform)
    ax1.set_title("Waveform")
    ax1.set_ylabel("Amplitude")

    ax2 = fig.add_subplot(grid[1, 0], sharex=ax1)
    ax2.plot(times, f0)
    ax2.set_title("Tracked fundamental frequency")
    ax2.set_ylabel("F0 (Hz)")

    ax3 = fig.add_subplot(grid[2, 0], sharex=ax1)
    ax3.plot(times, confidence)
    ax3.set_ylim(0, 1.05)
    ax3.set_title("Track confidence")
    ax3.set_ylabel("Confidence")

    ax4 = fig.add_subplot(grid[3, 0], sharex=ax1)
    ax4.plot(times, anchor)
    ax4.set_title("Unwrapped anchor phase")
    ax4.set_ylabel("Phase (rad)")

    ax5 = fig.add_subplot(grid[4, 0], sharex=ax1)
    if psi.size:
        count = min(max_harmonics, psi.shape[1])
        for index in range(1, count):
            ax5.plot(times, psi[:, index], linewidth=0.9, label=f"k={index + 1}")
    ax5.set_title("Unwrapped FARHP trajectories")
    ax5.set_xlabel("Time (s)")
    ax5.set_ylabel("Phase (rad)")
    if max_harmonics <= 12:
        ax5.legend(ncol=4, fontsize=7)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)
