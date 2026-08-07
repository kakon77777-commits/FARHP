"""FARHP-Core v0.3: phase transformation and controlled-listening research prototype."""

from .analyzer import AnalysisConfig, analyze_frame, analyze_waveform, estimate_f0_yin
from .codebook import TorusCodebook
from .model import FARHPFrame, FARHPTrajectory
from .quantizer import CircularScalarQuantizer
from .reconstructor import reconstruct_frame, reconstruct_trajectory
from .synth import VOWEL_FORMANTS, dynamic_synthetic_vowel, harmonic_synthesize, synthetic_vowel
from .tracking import TrackingConfig, analyze_trajectory, estimate_f0_candidates, track_f0_viterbi
from .transform import PhaseTransformReport, apply_phase_condition, geodesic_interpolate, transfer_phase_style
from .experiment import create_blind_listening_pack
from .utils import circular_distance, torus_distance, wrap_phase

__all__ = [
    "AnalysisConfig",
    "CircularScalarQuantizer",
    "FARHPFrame",
    "FARHPTrajectory",
    "TorusCodebook",
    "TrackingConfig",
    "VOWEL_FORMANTS",
    "analyze_frame",
    "analyze_trajectory",
    "analyze_waveform",
    "circular_distance",
    "dynamic_synthetic_vowel",
    "estimate_f0_candidates",
    "estimate_f0_yin",
    "harmonic_synthesize",
    "reconstruct_frame",
    "reconstruct_trajectory",
    "synthetic_vowel",
    "torus_distance",
    "track_f0_viterbi",
    "wrap_phase",
    "PhaseTransformReport",
    "apply_phase_condition",
    "geodesic_interpolate",
    "transfer_phase_style",
    "create_blind_listening_pack",
]

__version__ = "0.3.0"
