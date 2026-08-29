"""References must point at something that exists.

Links rot silently: a blog closes, an id changes. The network test does not run
in the normal suite, but it must be run before every release:

    python3 -m pytest tests/test_links.py -m network -q
"""
import re
import urllib.error
import urllib.request

import pytest

from roles import ROOT

URL_RE = re.compile(r"https?://[^\s)>\"]+")
UA = "Mozilla/5.0 (compatible; romhacking-plugin-linkcheck)"


SKIP_HOSTS = ("localhost", "127.0.0.1")


def _all_urls() -> dict[str, list[str]]:
    """Every cited URL, excluding instructions that target local services."""
    found: dict[str, list[str]] = {}
    files = list((ROOT / "skills").glob("*/SKILL.md")) + [ROOT / "references" / "SOURCES.md"]
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            for url in URL_RE.findall(line):
                url = url.rstrip(".,;)`\"'")
                if any(host in url for host in SKIP_HOSTS):
                    continue
                found.setdefault(url, []).append(path.name)
    return found


def test_every_url_is_well_formed():
    """Offline: syntax, malformed schemes, unencoded spaces."""
    bad = []
    for url in _all_urls():
        if " " in url:
            bad.append(f"{url}: unencoded space")
        # web.archive.org embeds the archived URL, so two schemes are legitimate
        schemes = url.count("://")
        if schemes != 1 and "web.archive.org" not in url:
            bad.append(f"{url}: malformed scheme ({schemes} occurrences of ://)")
        if url.endswith(("(", "[", "**")):
            bad.append(f"{url}: markup caught inside the URL")
    assert not bad, "\n".join(bad)


def test_local_documents_referenced_exist():
    """References to files in this repository must exist."""
    missing = []
    for path in (ROOT / "skills").glob("*/SKILL.md"):
        for match in re.findall(r"\]\((?!https?:)([^)]+)\)", path.read_text(encoding="utf-8")):
            if not (ROOT / match.lstrip("/")).exists():
                missing.append(f"{path.parent.name}: {match}")
    assert not missing, "broken local references:\n" + "\n".join(missing)


@pytest.mark.network
@pytest.mark.parametrize("url", sorted(_all_urls()))
def test_the_url_answers(url):
    """Online: every URL answers. Run before a release."""
    request = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            assert response.status < 400, f"{url} -> {response.status}"
    except urllib.error.HTTPError as error:
        if error.code in (403, 405, 429):
            pytest.skip(f"{url} -> {error.code}: refuses HEAD or crawlers, not dead")
        pytest.fail(f"{url} -> HTTP {error.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        pytest.fail(f"{url} unreachable: {error}")
