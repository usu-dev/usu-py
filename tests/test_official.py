import json
from pathlib import Path

import pytest
import usu

OFFICIAL_TESTS = Path(__file__).parent / "official"


def compare(d: Path):
    usu_in = usu.loads((d / "in.usu").read_text())
    json_out = json.loads((d / "out.json").read_text())
    assert usu_in == json_out


def test_official():
    if not OFFICIAL_TESTS.is_dir():
        pytest.skip(
            "Missing official test suite. Clone from github with: "
            "git clone git@github.com:usu-dev/tests.git tests/official"
        )

    for d in (Path(__file__).parent / "official" / "cases").iterdir():
        compare(d)
