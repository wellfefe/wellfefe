"""Cache public profile panels; keep the last valid image if an upstream fails."""
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import time

PANELS = {
    "stats": "https://github-stats-extended.vercel.app/api?username=wellfefe&show_icons=true&bg_color=0D1117&title_color=EF4444&icon_color=EF4444&text_color=C9D1D9&hide_border=true",
    "languages": "https://github-stats-extended.vercel.app/api/top-langs/?username=wellfefe&layout=compact&bg_color=0D1117&title_color=EF4444&text_color=C9D1D9&hide_border=true",
    "activity": "https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=wellfefe&theme=github_dark",
    "streak": "https://streak-stats.demolab.com?user=wellfefe&locale=pt_BR&hide_border=true&background=0D1117&ring=EF4444&fire=EF4444&currStreakLabel=EF4444&sideLabels=C9D1D9&currStreakNum=F0F3F6&sideNums=F0F3F6&dates=8B949E",
}
def main():
    Path("assets").mkdir(exist_ok=True)
    missing = []
    for name, url in PANELS.items():
        path = Path("assets") / (name + ".svg")
        for attempt in range(3):
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "image/svg+xml"})
                with urlopen(req, timeout=45) as response:
                    body = response.read()
                root = ET.fromstring(body)
                if root.tag != "{http://www.w3.org/2000/svg}svg":
                    raise ValueError("Expected SVG")
                text = " ".join(root.itertext()).lower()
                if any(error in text for error in ("something went wrong", "could not fetch", "rate limit", "deployment_disabled", "deployment_paused")):
                    raise ValueError("Upstream returned an error card")
                path.write_bytes(body)
                print("Updated", path, flush=True)
                break
            except Exception as error:
                print("Could not refresh", name, str(error), flush=True)
                if attempt < 2:
                    time.sleep(3)
        else:
            if not path.exists():
                missing.append(name)
    if missing:
        raise RuntimeError("Missing initial panels: " + ", ".join(missing))
if __name__ == "__main__":
    main()
