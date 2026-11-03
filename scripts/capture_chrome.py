"""Capture how Chrome reads and serializes CSS colors, as ground truth for the tests.

    python scripts/capture_chrome.py CHROME_EXE WORK_DIR

Every input (generated from a fixed seed) is assigned to the ``color`` property of an
element in a standards-mode page; the result records whether Chrome accepted it and the
computed value it serializes. The page runs once in headless Chrome and the results are
written to tests/fixtures/chrome-computed-color.json. WORK_DIR holds the page and a
throwaway browser profile.

Inputs never start or end with whitespace and hold no comment, escape or other CSS-wide
syntax, which the library leaves out on purpose (see GUIDE.md).
"""

from __future__ import annotations

import html
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hexrgba import NAMED_COLORS  # noqa: E402

SEED = 20261023
# Look-alikes too: no-break space, Kelvin sign, dotless i and long s (which fold in Unicode).
NOISE = "#0123456789abcdefABCDEFgGxXkKrRnN \t\n" + "".join(map(chr, (0xA0, 0x212A, 0x131, 0x17F)))
PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>capture</title></head>
<body><div id="probe"></div><pre id="out"></pre>
<script type="application/json" id="data">DATA</script>
<script>
const inputs = JSON.parse(document.getElementById("data").textContent);
const probe = document.getElementById("probe");
const rows = inputs.map((text) => {
  probe.style.color = "";
  probe.style.color = text;
  const valid = probe.style.color !== "";
  return [text, valid, valid ? getComputedStyle(probe).color : null];
});
document.getElementById("out").textContent = JSON.stringify({agent: navigator.userAgent, rows});
</script></body></html>
"""


def _mixed(text: str, rng: random.Random) -> str:
    return "".join(ch.upper() if rng.random() < 0.5 else ch for ch in text)


def inputs() -> list[str]:
    rng = random.Random(SEED)
    cases = [f"#ff00ff{alpha:02x}" for alpha in range(256)]
    for name in [*NAMED_COLORS, "transparent"]:
        cases += [name, name.upper(), _mixed(name, rng)]
    for size in (3, 4, 6, 8):
        cases += [
            "#" + _mixed("".join(rng.choice("0123456789abcdef") for _ in range(size)), rng)
            for _ in range(400)
        ]
    keywords = [*NAMED_COLORS, "transparent"]
    cases = list(dict.fromkeys(cases))
    seen = set(cases)
    while len(cases) < 6000:
        if rng.random() < 0.4:
            chars = list(rng.choice(keywords))
            for _ in range(rng.randrange(3)):
                chars.insert(rng.randrange(len(chars) + 1), rng.choice(NOISE))
            text = "".join(chars)
        else:
            text = "".join(rng.choice(NOISE) for _ in range(rng.randrange(1, 11)))
        if text and not text[0].isspace() and not text[-1].isspace() and text not in seen:
            cases.append(text)
            seen.add(text)
    return cases


def main() -> int:
    chrome, work = sys.argv[1], Path(sys.argv[2]).resolve()
    work.mkdir(parents=True, exist_ok=True)
    cases = inputs()
    data = json.dumps(cases).replace("<", "\\u003c")
    page = work / "capture.html"
    page.write_text(PAGE.replace("DATA", data), encoding="utf-8")
    done = subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            f"--user-data-dir={work / 'profile'}",
            "--dump-dom",
            page.as_uri(),
        ],
        capture_output=True,
        timeout=300,
        check=True,
    )
    found = re.search(r'<pre id="out">(.*?)</pre>', done.stdout.decode("utf-8"), re.S)
    assert found, done.stderr.decode("utf-8", "replace")[-2000:]
    result = json.loads(html.unescape(found.group(1)))
    assert [row[0] for row in result["rows"]] == cases
    fixture = {
        "source": "headless Chrome, scripts/capture_chrome.py (CSS color property, standards mode)",
        "agent": result["agent"],
        "captured": "2026-10-23",
        "seed": SEED,
        "rows": result["rows"],
    }
    out = ROOT / "tests" / "fixtures" / "chrome-computed-color.json"
    out.write_text(json.dumps(fixture, ensure_ascii=True, indent=0) + "\n", encoding="utf-8")
    print(f"{len(cases)} inputs, {sum(r[1] for r in result['rows'])} accepted, {result['agent']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
