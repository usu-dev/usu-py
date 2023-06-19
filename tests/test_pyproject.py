from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import usu

PATHS = (
    (tomllib, Path(__file__).parent.parent / "pyproject.toml"),
    (usu, Path(__file__).parent / "pyproject.usu"),
)


def load_pyproject(mod, p):
    with p.open("r") as f:
        return mod.loads(f.read())


def check(pyprojects, section):
    assert pyprojects[0][section] == pyprojects[1][section]


def test_pyproject():
    pyprojects = [load_pyproject(mod, p) for mod, p in PATHS]
    check(pyprojects, "project")
    check(pyprojects, "build-system")
    check(pyprojects, "tool")
