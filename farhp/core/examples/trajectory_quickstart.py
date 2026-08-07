from pathlib import Path

from farhp.inspector import save_trajectory_plot
from farhp.io import save_trajectory, write_wav
from farhp.reconstructor import reconstruct_trajectory
from farhp.synth import dynamic_synthetic_vowel
from farhp.tracking import TrackingConfig, analyze_trajectory

out = Path("artifacts/trajectory_quickstart")
out.mkdir(parents=True, exist_ok=True)

waveform, _, _ = dynamic_synthetic_vowel(duration_sec=1.2)
config = TrackingConfig(frame_length_sec=0.080, hop_length_sec=0.010, k_max=24)
trajectory = analyze_trajectory(waveform, 16000, config=config)
reconstructed = reconstruct_trajectory(trajectory)

write_wav(out / "input.wav", 16000, waveform)
write_wav(out / "reconstructed.wav", 16000, reconstructed)
save_trajectory(out / "trajectory.json", trajectory)
save_trajectory_plot(trajectory, waveform, out / "trajectory.png")

print(f"frames={trajectory.frame_count}, voiced_ratio={trajectory.voiced_ratio:.3f}")
