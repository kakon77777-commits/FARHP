from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .analyzer import AnalysisConfig, analyze_frame
from .inspector import save_frame_plot, save_trajectory_plot
from .io import (
    load_frame,
    load_json,
    load_trajectory,
    read_wav,
    save_frame,
    save_json,
    save_trajectory,
    write_wav,
)
from .quantizer import CircularScalarQuantizer
from .reconstructor import reconstruct_frame, reconstruct_trajectory
from .schema import validate_spec_object
from .synth import dynamic_synthetic_vowel, synthetic_vowel
from .tracking import TrackingConfig, analyze_trajectory
from .transform import apply_phase_condition, transfer_phase_style
from .experiment import create_blind_listening_pack
from .utils import rms, torus_distance


def _center_frame(x: np.ndarray, sample_rate_hz: int, length_sec: float) -> np.ndarray:
    n = int(round(length_sec * sample_rate_hz))
    if x.size < n:
        return np.pad(x, (0, n - x.size))
    start = (x.size - n) // 2
    return x[start : start + n]


def cmd_demo(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    waveform, _, _ = synthetic_vowel(
        args.vowel,
        f0_hz=args.f0,
        sample_rate_hz=args.sample_rate,
        duration_sec=args.duration,
        k_max=args.k_max,
    )
    write_wav(out / "synthetic_vowel.wav", args.sample_rate, waveform)
    frame_wave = _center_frame(waveform, args.sample_rate, args.frame_length)
    config = AnalysisConfig(k_max=args.k_max, window="hann")
    frame = analyze_frame(frame_wave, args.sample_rate, frame_time_sec=args.duration / 2, config=config)
    save_frame(out / "farhp_frame.json", frame)
    reconstructed = reconstruct_frame(frame, normalize=True)
    write_wav(out / "reconstructed_frame.wav", args.sample_rate, reconstructed)
    save_frame_plot(frame, frame_wave, out / "farhp_inspector.png")

    quantizer = CircularScalarQuantizer(args.levels)
    q = quantizer.encode(frame.phase_vector())
    q_decoded = quantizer.decode(q)
    quant_error = torus_distance(frame.phase_vector(), q_decoded, mask=frame.phase_mask())
    report = {
        "estimated_f0_hz": frame.f0_hz,
        "target_f0_hz": args.f0,
        "f0_absolute_error_hz": abs(frame.f0_hz - args.f0),
        "f0_confidence": frame.f0_confidence,
        "applicability_grade": frame.applicability_grade,
        "harmonics": frame.k_max,
        "valid_harmonics": int(np.sum(frame.mask)),
        "scalar_quantizer_levels": args.levels,
        "quantization_torus_rmse_rad": quant_error,
        "quantization_bound_rad": quantizer.worst_case_error_rad,
        "frame_rms": rms(frame_wave),
        "reconstruction_rms": rms(reconstructed),
        "note": "Harmonic-only frame reconstruction; residual/noise components are excluded.",
    }
    save_json(out / "demo_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _tracking_config(args: argparse.Namespace) -> TrackingConfig:
    return TrackingConfig(
        frame_length_sec=args.frame_length,
        hop_length_sec=args.hop_length,
        f0_min_hz=args.f0_min,
        f0_max_hz=args.f0_max,
        k_max=args.k_max,
    )


def _trajectory_report(trajectory, true_f0: np.ndarray | None = None) -> dict[str, object]:
    f0 = np.asarray([np.nan if value is None else value for value in trajectory.f0_hz], dtype=float)
    report: dict[str, object] = {
        "frame_count": trajectory.frame_count,
        "voiced_ratio": trajectory.voiced_ratio,
        "mean_track_confidence": float(np.mean(trajectory.track_confidence)),
        "median_anchor_prediction_residual_rad": float(
            np.nanmedian(
                [np.nan if value is None else abs(value) for value in trajectory.anchor_residual_rad]
            )
        ),
        "f0_min_hz": float(np.nanmin(f0)),
        "f0_max_hz": float(np.nanmax(f0)),
    }
    if true_f0 is not None:
        indices = np.clip(
            np.rint(np.asarray(trajectory.frame_times_sec) * trajectory.sample_rate_hz).astype(int),
            0,
            true_f0.size - 1,
        )
        reference = true_f0[indices]
        valid = np.isfinite(f0)
        report["f0_mae_hz"] = float(np.mean(np.abs(f0[valid] - reference[valid])))
        report["f0_rmse_hz"] = float(np.sqrt(np.mean(np.square(f0[valid] - reference[valid]))))
    return report


def cmd_demo_track(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    waveform, true_f0, _ = dynamic_synthetic_vowel(
        args.vowel,
        f0_start_hz=args.f0_start,
        f0_end_hz=args.f0_end,
        sample_rate_hz=args.sample_rate,
        duration_sec=args.duration,
        k_max=args.k_max,
    )
    write_wav(out / "dynamic_synthetic_vowel.wav", args.sample_rate, waveform)
    trajectory = analyze_trajectory(waveform, args.sample_rate, config=_tracking_config(args))
    save_trajectory(out / "farhp_trajectory.json", trajectory)
    reconstruction = reconstruct_trajectory(trajectory, normalize=True)
    write_wav(out / "trajectory_reconstruction.wav", args.sample_rate, reconstruction)
    save_trajectory_plot(trajectory, waveform, out / "trajectory_inspector.png")
    report = _trajectory_report(trajectory, true_f0=true_f0)
    report["note"] = (
        "Dynamic synthetic-vowel regression fixture. The reconstruction is harmonic-only and "
        "is not a natural-speech quality claim."
    )
    save_json(out / "trajectory_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    fs, x = read_wav(args.wav)
    frame_wave = _center_frame(x, fs, args.frame_length)
    frame = analyze_frame(frame_wave, fs, config=AnalysisConfig(k_max=args.k_max))
    save_frame(args.out, frame)
    return 0


def cmd_track(args: argparse.Namespace) -> int:
    fs, waveform = read_wav(args.wav)
    trajectory = analyze_trajectory(waveform, fs, config=_tracking_config(args))
    save_trajectory(args.out, trajectory)
    if args.plot:
        save_trajectory_plot(trajectory, waveform, args.plot)
    print(json.dumps(_trajectory_report(trajectory), ensure_ascii=False, indent=2))
    return 0


def cmd_reconstruct(args: argparse.Namespace) -> int:
    frame = load_frame(args.json)
    waveform = reconstruct_frame(frame, normalize=True)
    write_wav(args.out, frame.sample_rate_hz, waveform)
    return 0


def cmd_reconstruct_track(args: argparse.Namespace) -> int:
    trajectory = load_trajectory(args.json)
    waveform = reconstruct_trajectory(trajectory, normalize=True)
    write_wav(args.out, trajectory.sample_rate_hz, waveform)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate_spec_object(load_json(args.json), args.schema)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    frame = load_frame(args.json)
    waveform = reconstruct_frame(frame, normalize=False)
    save_frame_plot(frame, waveform, args.out)
    return 0



def cmd_transform_track(args: argparse.Namespace) -> int:
    trajectory = load_trajectory(args.json)
    transformed, report = apply_phase_condition(
        trajectory, args.mode, strength=args.strength, seed=args.seed
    )
    save_trajectory(args.out, transformed)
    if args.wav:
        waveform = reconstruct_trajectory(transformed, normalize=True)
        write_wav(args.wav, transformed.sample_rate_hz, waveform)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_morph_track(args: argparse.Namespace) -> int:
    content = load_trajectory(args.content)
    style = load_trajectory(args.style)
    transformed, report = transfer_phase_style(content, style, strength=args.strength)
    save_trajectory(args.out, transformed)
    if args.wav:
        waveform = reconstruct_trajectory(transformed, normalize=True)
        write_wav(args.wav, transformed.sample_rate_hz, waveform)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_blind_pack(args: argparse.Namespace) -> int:
    content = load_trajectory(args.content)
    style = load_trajectory(args.style)
    report = create_blind_listening_pack(content, style, args.out, seed=args.seed)
    print(json.dumps({
        "output": str(args.out),
        "sample_count": len(report["mapping"]),
        "conditions": sorted(report["objective_metrics"]),
        "note": report["warning"],
    }, ensure_ascii=False, indent=2))
    return 0

def _add_tracking_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--frame-length", type=float, default=0.080)
    parser.add_argument("--hop-length", type=float, default=0.010)
    parser.add_argument("--f0-min", type=float, default=70.0)
    parser.add_argument("--f0-max", type=float, default=350.0)
    parser.add_argument("--k-max", type=int, default=24)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="farhp", description="FARHP-Core v0.3 research prototype")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run the stationary synthetic-vowel closed-loop demonstration")
    demo.add_argument("--out", default="artifacts/demo")
    demo.add_argument("--vowel", default="a")
    demo.add_argument("--f0", type=float, default=125.0)
    demo.add_argument("--sample-rate", type=int, default=16000)
    demo.add_argument("--duration", type=float, default=0.8)
    demo.add_argument("--frame-length", type=float, default=0.08)
    demo.add_argument("--k-max", type=int, default=24)
    demo.add_argument("--levels", type=int, default=16)
    demo.set_defaults(func=cmd_demo)

    demo_track = sub.add_parser("demo-track", help="run the nonstationary trajectory demonstration")
    demo_track.add_argument("--out", default="artifacts/trajectory_demo")
    demo_track.add_argument("--vowel", default="a")
    demo_track.add_argument("--f0-start", type=float, default=110.0)
    demo_track.add_argument("--f0-end", type=float, default=165.0)
    demo_track.add_argument("--sample-rate", type=int, default=16000)
    demo_track.add_argument("--duration", type=float, default=1.2)
    _add_tracking_arguments(demo_track)
    demo_track.set_defaults(func=cmd_demo_track)

    analyze = sub.add_parser("analyze", help="analyze the center frame of a WAV file")
    analyze.add_argument("wav")
    analyze.add_argument("--out", required=True)
    analyze.add_argument("--frame-length", type=float, default=0.08)
    analyze.add_argument("--k-max", type=int, default=24)
    analyze.set_defaults(func=cmd_analyze)

    track = sub.add_parser("track", help="analyze an entire WAV file as a FARHP trajectory")
    track.add_argument("wav")
    track.add_argument("--out", required=True)
    track.add_argument("--plot")
    _add_tracking_arguments(track)
    track.set_defaults(func=cmd_track)

    recon = sub.add_parser("reconstruct", help="reconstruct a harmonic frame from FARHP JSON")
    recon.add_argument("json")
    recon.add_argument("--out", required=True)
    recon.set_defaults(func=cmd_reconstruct)

    recon_track = sub.add_parser("reconstruct-track", help="reconstruct a harmonic trajectory")
    recon_track.add_argument("json")
    recon_track.add_argument("--out", required=True)
    recon_track.set_defaults(func=cmd_reconstruct_track)


    transform = sub.add_parser("transform-track", help="apply a controlled FARHP-only phase condition")
    transform.add_argument("json")
    transform.add_argument("--mode", choices=["identity", "zero", "alternating", "random_static", "random_smooth"], required=True)
    transform.add_argument("--strength", type=float, default=1.0)
    transform.add_argument("--seed", type=int, default=7)
    transform.add_argument("--out", required=True)
    transform.add_argument("--wav")
    transform.set_defaults(func=cmd_transform_track)

    morph = sub.add_parser("morph-track", help="transfer or interpolate FARHP style onto a content trajectory")
    morph.add_argument("content")
    morph.add_argument("style")
    morph.add_argument("--strength", type=float, default=1.0)
    morph.add_argument("--out", required=True)
    morph.add_argument("--wav")
    morph.set_defaults(func=cmd_morph_track)

    blind = sub.add_parser("blind-pack", help="create a randomized blind-listening pack")
    blind.add_argument("content")
    blind.add_argument("style")
    blind.add_argument("--out", required=True)
    blind.add_argument("--seed", type=int, default=20260726)
    blind.set_defaults(func=cmd_blind_pack)

    validate = sub.add_parser("validate", help="validate frame JSON against FARHP-Spec schema")
    validate.add_argument("json")
    validate.add_argument("--schema", required=True)
    validate.set_defaults(func=cmd_validate)

    inspect = sub.add_parser("inspect", help="render a diagnostic PNG from FARHP frame JSON")
    inspect.add_argument("json")
    inspect.add_argument("--out", required=True)
    inspect.set_defaults(func=cmd_inspect)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
