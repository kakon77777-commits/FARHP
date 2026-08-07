from pathlib import Path

from farhp.analyzer import AnalysisConfig, analyze_frame
from farhp.io import save_frame, write_wav
from farhp.reconstructor import reconstruct_frame
from farhp.synth import synthetic_vowel

out = Path("artifacts/quickstart")
out.mkdir(parents=True, exist_ok=True)
fs = 16000
waveform, _, _ = synthetic_vowel("a", sample_rate_hz=fs)
frame_wave = waveform[int(0.36 * fs):int(0.44 * fs)]
frame = analyze_frame(frame_wave, fs, config=AnalysisConfig(k_max=24))
reconstructed = reconstruct_frame(frame, normalize=True)
write_wav(out / "input.wav", fs, frame_wave)
write_wav(out / "reconstructed.wav", fs, reconstructed)
save_frame(out / "frame.json", frame)
print(frame.to_spec_object()["analysis"])
