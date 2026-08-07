from pathlib import Path
import json
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / 'examples' / 'governance_v0.8'
CASES = [
    (ROOT / 'spec/FARHP_MultiStimulus_Study_Spec_v0.6.schema.json', sorted((ROOT / 'examples/study_v0.6').glob('study_*.json'))),
    (ROOT / 'spec/FARHP_Group_Analysis_Spec_v0.6.schema.json', [ROOT / 'examples/study_v0.6/group_analysis.json']),
    (ROOT / 'spec/FARHP_Research_Plan_Spec_v0.8.schema.json', [DEPLOY / 'plan.json']),
    (ROOT / 'spec/FARHP_Session_Checkpoint_Spec_v0.8.schema.json', [DEPLOY / 'checkpoint.json']),
    (ROOT / 'spec/FARHP_MultiStimulus_Study_Spec_v0.8.schema.json', [DEPLOY / 'study.json']),
    (ROOT / 'spec/FARHP_Deidentified_Study_Spec_v0.8.schema.json', [DEPLOY / 'deidentified.json']),
    (ROOT / 'spec/FARHP_Audit_Archive_Spec_v0.8.schema.json', [DEPLOY / 'audit.json']),
    (ROOT / 'spec/FARHP_Group_Analysis_Spec_v0.8.schema.json', [DEPLOY / 'group.json']),
]
count = 0
for schema_path, files in CASES:
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for file_path in files:
        errors = sorted(validator.iter_errors(json.loads(file_path.read_text(encoding='utf-8'))), key=lambda e: list(e.path))
        if errors:
            path = '/'.join(map(str, errors[0].path))
            raise AssertionError(f'{file_path.name} [{path}]: {errors[0].message}')
        print(f'PASS {file_path.name}')
        count += 1
print(f'FARHP WebLab schema validation: {count} files PASS')
