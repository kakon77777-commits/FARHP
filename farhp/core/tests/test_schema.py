from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

from farhp.analyzer import AnalysisConfig, analyze_frame
from farhp.schema import validate_spec_object
from farhp.synth import synthetic_vowel


class TestSchema(unittest.TestCase):
    def test_reference_output_validates(self) -> None:
        root = Path(os.environ.get("FARHP_PROJECT_ROOT", Path(__file__).resolve().parents[1]))
        schema = root / "spec" / "FARHP_Spec_v0.1.schema.json"
        x, _, _ = synthetic_vowel(duration_sec=0.2, k_max=12)
        fs = 16000
        frame = analyze_frame(x[960:2240], fs, config=AnalysisConfig(k_max=12))
        errors = validate_spec_object(frame.to_spec_object(), schema)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
