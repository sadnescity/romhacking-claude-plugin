import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

SYSTEM = {"romhacking", "project-state", "toolchain"}
# Skills that are *only* a phase. Not to be confused with romhack_state.PHASES,
# which lists the seven phases of the flow.
PHASE_SKILLS = {"encoding", "space", "graphics"}
THEMES = {
    "tooling", "recon", "text-search", "tables", "control-codes",
    "dte-mte", "pointers", "expansion", "relocation", "accents", "dump-insert",
    "asm", "compressions", "archives", "filesystem-iso",
    "tiles", "palettes", "fonts", "vwf", "image-formats",
    "glossary", "translation", "qa", "patching",
}


def skill_dirs():
    return sorted(p.parent for p in (ROOT / "skills").glob("*/SKILL.md"))


def skill_text(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
