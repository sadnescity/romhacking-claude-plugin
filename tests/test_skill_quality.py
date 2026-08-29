import re

import pytest

import roles
from roles import ROOT, THEMES, skill_dirs

# Historical tools that the sources prescribe and that must not appear as an
# instruction: name the capability, not the product. Generic names are made
# specific to avoid false positives on common words.
FORBIDDEN = [
    r"thingy", r"translhextion", r"hex ?workshop", r"searchr", r"tile layer pro",
    r"tile molester", r"\bjabba\b", r"lunar expand", r"lunar ?ips", r"cdmage",
    r"iso ?buster", r"imgburn", r"toc changer", r"ecc regen", r"\bxtractor\b",
    r"rexrypta", r"\batlas\b", r"cartographer", r"binpatcher", r"ppf ?studio",
    r"ppf-?o-?matic", r"nesticle", r"genecyst", r"no\$gb", r"zsnes", r"snes9x",
]
FORBIDDEN_RE = re.compile("|".join(FORBIDDEN), re.I)

# Generic patterns carry \b: `xtractor` without a word boundary would fire
# inside "archive extractors", and a guardrail that punishes correct prose ends
# up switched off.

# The four mandatory movements of a theme skill, preceded by the chapter's
# explanation: a skill must teach someone who does not know the subject, not
# only assist someone who already does.
MOVEMENTS = ("## What this is", "## Recognize", "## Analyze", "## Implement", "## Verify")


def _is_exempt(line: str) -> bool:
    """A historical note and a bibliographic citation are not prescriptions.

    The SOURCES: line and the "→" pointers list the real titles of the sources,
    and one of them is "L'HexWorkshop e le table": citing it is correct, and a
    guardrail that forbade it would force a falsified bibliography.
    """
    stripped = line.lstrip()
    return (stripped.startswith("Historically:")
            or stripped.startswith("SOURCES:")
            or stripped.startswith("→"))


def test_no_tool_is_prescribed():
    offenders = []
    for skill in skill_dirs():
        for lineno, line in enumerate((skill / "SKILL.md").read_text(encoding="utf-8").splitlines(), 1):
            if FORBIDDEN_RE.search(line) and not _is_exempt(line):
                offenders.append(f"{skill.name}:{lineno}: {line.strip()[:70]}")
    assert not offenders, (
        "A historical tool appears outside a `Historically:` note.\n"
        "Name the capability, not the product:\n" + "\n".join(offenders)
    )


@pytest.mark.parametrize("name", sorted(THEMES))
def test_theme_skill_has_four_movements(name):
    text = roles.skill_text(name)
    missing = [m for m in MOVEMENTS if m not in text]
    assert not missing, f"{name}: missing sections {missing}"


@pytest.mark.parametrize("name", sorted(THEMES))
def test_the_explanation_comes_before_the_procedure(name):
    """Whoever opens the skill without knowing the subject must find the explanation first."""
    text = roles.skill_text(name)
    if "## What this is" not in text:
        pytest.fail(f"{name}: the chapter explanation is missing")
    assert text.index("## What this is") < text.index("## Recognize"), \
        f"{name}: the explanation must precede the procedure"


@pytest.mark.parametrize("name", sorted(THEMES))
def test_theme_skill_cites_its_sources(name):
    text = roles.skill_text(name)
    assert re.search(r"^SOURCES:", text, re.M), f"{name}: the SOURCES: line is missing"


def test_the_accents_skill_states_the_addition_rule():
    """Accents are added: removing an original glyph is not an option."""
    text = roles.skill_text("accents")
    assert "never take an existing one away" in text.lower(), \
        "missing the rule: accents are extra characters"
    assert "hiragana" in text.lower(), \
        "missing the one legitimate exception: an alphabet the target language does not use"


def test_the_dump_skill_offers_a_choice_of_formats():
    """The working format is the project's choice, not an imposition."""
    text = roles.skill_text("dump-insert")
    for fmt in ("marked script", "TSV", "PO"):
        assert fmt in text, f"the skill does not offer the {fmt} format"
    assert "line break here is a line break in the game" in text, \
        "missing the rule that makes a script readable"


def test_the_dump_skill_requires_a_space_plan():
    """Handing over a script without saying how much room there is is half the job."""
    text = roles.skill_text("dump-insert")
    assert "space plan is half a dump" in text
    for mode in ("pointed", "sequential", "fixed"):
        assert mode in text, f"the skill does not explain {mode} addressing"


def test_the_tables_skill_warns_about_several_tables():
    text = roles.skill_text("tables")
    assert "several tables" in text.lower(), \
        "missing the warning that a game may have one table per context"


def test_no_skill_points_at_one_that_does_not_exist():
    """A reference to a missing skill is a dead end for whoever follows it."""
    existing = {d.name for d in skill_dirs()}
    referenced = re.compile(r"`([a-z][a-z0-9-]{2,})`")
    dangling = []
    for skill in skill_dirs():
        for lineno, line in enumerate((skill / "SKILL.md").read_text(encoding="utf-8").splitlines(), 1):
            for name in referenced.findall(line):
                if name in existing:
                    continue
                if "skill" in line.lower():
                    dangling.append(f"{skill.name}:{lineno}: `{name}`")
    assert not dangling, (
        "references to skills that do not exist:\n"
        + "\n".join(dangling)
    )


# A further-reading pointer: arrow, linked title, and the reason to go there.
READ_MORE_RE = re.compile(r"^→ .*\[.+?\]\(https?://\S+?\).* — .+", re.M)


@pytest.mark.parametrize("name", sorted(THEMES))
def test_a_theme_points_at_its_sources_where_it_explains(name):
    """Citing at the bottom is attribution; pointing at the right place is teaching.

    Whoever reads a chapter's explanation must find right there — not at the
    bottom — where to go deeper, and what they will find.
    """
    text = roles.skill_text(name)
    links = READ_MORE_RE.findall(text)
    assert links, f"{name}: no further-reading pointer in the body"
    assert "### Read more" in text, f"{name}: the pointers are not in a recognisable section"
    assert text.index("### Read more") < text.index("## Recognize"), \
        f"{name}: the pointers must close the explanation, not follow the procedure"


@pytest.mark.parametrize("name", sorted(THEMES))
def test_every_read_more_says_what_you_will_find_there(name):
    """A link without a reason is a link nobody opens."""
    bare = []
    for line in roles.skill_text(name).splitlines():
        if line.startswith("→") and not READ_MORE_RE.match(line):
            bare.append(line.strip()[:70])
    assert not bare, f"{name}: pointers without title, link or reason:\n" + "\n".join(bare)


def test_the_reasons_are_specific_rather_than_generic():
    """'For more' is not a reason: it must say what is there that is not here.

    Generic phrasings are rejected in English and in Italian.
    """
    generic = ("for more", "to learn more", "further reading", "more details",
               "additional information", "per approfondire", "per saperne di più")
    offenders = []
    for skill in skill_dirs():
        for lineno, line in enumerate((skill / "SKILL.md").read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("→"):
                continue
            reason = line.split(" — ", 1)[-1].lower()
            if len(reason.split()) < 5 or any(g in reason for g in generic):
                offenders.append(f"{skill.name}:{lineno}")
    assert not offenders, "pointers with a generic or missing reason: " + ", ".join(offenders)


# The plugin teaches a method; it does not tell how it was built: no local
# paths, no development history, no references to internal documents the reader
# does not have. Traces are blocked in English and in Italian.
DEV_TRACES = re.compile(
    r"/Users/|/home/\w|[A-Z]:\\Users"                       # local paths
    r"|\bwaves?\b|\bondat[ae]\b"                              # delivery waves
    r"|\bspec(ification)? ?§|\bspecifica del plugin\b|\bplugin spec(ification)?\b"
    r"|field[- ]test|prova sul campo|dev(elopment)? (log|diary)|diario di sviluppo"
    r"|not written yet|non ancora scritt",
    re.I,
)


def test_no_development_traces_or_local_paths():
    files = [p for p in ROOT.glob("skills/*/SKILL.md")]
    files += list((ROOT / "scripts").glob("*.py"))
    files += [ROOT / "README.md", ROOT / "CONTRIBUTING.md",
              ROOT / "references" / "SOURCES.md", ROOT / ".claude-plugin" / "plugin.json"]
    offenders = []
    for path in files:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if DEV_TRACES.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()[:70]}")
    assert not offenders, "development traces or local paths:\n" + "\n".join(offenders)
