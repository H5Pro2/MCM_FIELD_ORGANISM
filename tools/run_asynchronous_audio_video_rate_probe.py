from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.asynchronous_audio_video_rate_probe import run_asynchronous_audio_video_rate_probe

print(json.dumps(asdict(run_asynchronous_audio_video_rate_probe()), indent=2, sort_keys=True))
