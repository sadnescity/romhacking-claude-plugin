"""Fixtures for the optional integration tests on real data.

    ROMHACK_TEST_ROM       an untouched ROM; tests that need it in iNES format
                           are skipped for other formats
    ROMHACK_TEST_PROJECT   the directory of a project (ROMHACK.md, tables)
                           working on that ROM

Without the variables, or with paths that do not exist, those tests are
skipped: no ROM ever enters the repository.
"""
import os
import pathlib

import pytest

import ines


def _path_from_env(name: str) -> pathlib.Path:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} is not set")
    path = pathlib.Path(value).expanduser()
    if not path.exists():
        pytest.skip(f"{name} points at a missing path: {path}")
    return path


def synthetic_ines(prg_banks: int = 2, chr_banks: int = 1) -> bytes:
    """A minimal valid iNES image: each PRG bank filled with its own index."""
    header = ines.MAGIC + bytes([prg_banks, chr_banks]) + bytes(10)
    prg = b"".join(bytes([i]) * ines.PRG_BANK for i in range(prg_banks))
    return header + prg + b"\xC7" * (chr_banks * ines.CHR_BANK)


@pytest.fixture(scope="session")
def synthetic_rom():
    return synthetic_ines()


@pytest.fixture(scope="session")
def rom_path():
    return _path_from_env("ROMHACK_TEST_ROM")


@pytest.fixture(scope="session")
def rom_bytes(rom_path):
    return rom_path.read_bytes()


@pytest.fixture(scope="session")
def ines_rom(rom_bytes):
    if not rom_bytes.startswith(ines.MAGIC):
        pytest.skip("the test ROM is not in iNES format")
    return rom_bytes


@pytest.fixture(scope="session")
def project_dir():
    path = _path_from_env("ROMHACK_TEST_PROJECT")
    if not (path / "ROMHACK.md").exists():
        pytest.skip(f"no ROMHACK.md in {path}")
    return path
