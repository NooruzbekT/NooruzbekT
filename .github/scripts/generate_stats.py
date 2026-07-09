import os
import requests
from collections import defaultdict

LANGUAGE_COLORS = {
    'Python': '#3572A5',
    'Java': '#b07219',
    'JavaScript': '#f1e05a',
    'TypeScript': '#2b7489',
    'C++': '#f34b7d',
    'C': '#555555',
    'C#': '#178600',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'Go': '#00ADD8',
    'Rust': '#dea584',
    'Shell': '#89e051',
    'Kotlin': '#F18E33',
    'Swift': '#ffac45',
    'PHP': '#4F5D95',
    'Ruby': '#701516',
    'Jupyter Notebook': '#DA5B0B',
    'Dockerfile': '#384d54',
    'Mermaid': '#ff3670',
    'CSS': '#563d7c',
    'SCSS': '#c6538c',
    'Vue': '#41b883',
    'default': '#8f8f8f'
}

def get_color(lang):
    return LANGUAGE_COLORS.get(lang, LANGUAGE_COLORS['default'])

def generate_svg(lang_data):
    import math

    top = sorted(lang_data.items(), key=lambda x: x[1], reverse=True)[:8]
    total = sum(v for _, v in top) or 1

    width = 495
    padding = 25
    title_h = 52

    # Donut geometry (left side)
    cx, r, sw = 118, 62, 22
    donut_cy = title_h + 20 + r + sw / 2
    circ = 2 * math.pi * r
    gap = 3  # visual gap between segments (in path units)

    # Legend geometry (right side)
    legend_x = 235
    legend_top = title_h + 18
    row_h = 24
    legend_bottom = legend_top + len(top) * row_h

    height = max(donut_cy + r + sw / 2, legend_bottom) + padding

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height:.0f}" '
        f'viewBox="0 0 {width} {height:.0f}" fill="none">',
        '<style>',
        '  .title { font: 600 18px "Segoe UI", Ubuntu, Sans-Serif; fill: #58a6ff; }',
        '  .lang-name { font: 400 13px "Segoe UI", Ubuntu, Sans-Serif; fill: #e6edf3; }',
        '  .lang-pct { font: 700 13px "Segoe UI", Ubuntu, Sans-Serif; fill: #8b949e; }',
        '  @keyframes fadein { from { opacity: 0; transform: translateY(6px); } '
        'to { opacity: 1; transform: translateY(0); } }',
        '  .row { animation: fadein 0.5s ease forwards; opacity: 0; }',
        '</style>',
        f'<rect x="0.5" y="0.5" rx="12" ry="12" height="{height - 1:.0f}" width="{width - 1}" '
        'fill="#0d1117" stroke="#30363d"/>',
        f'<text x="{padding}" y="33" class="title">Most Used Languages</text>',
    ]

    # Background ring
    lines.append(
        f'<circle cx="{cx}" cy="{donut_cy:.1f}" r="{r}" stroke="#21262d" stroke-width="{sw}"/>'
    )

    # Donut segments with draw-in animation
    cumulative = 0.0
    for i, (lang, val) in enumerate(top):
        frac = val / total
        seg = frac * circ
        dash = max(0.5, seg - gap)
        rot = cumulative * 360 - 90  # start at top, clockwise
        lines.append(
            f'<circle cx="{cx}" cy="{donut_cy:.1f}" r="{r}" stroke="{get_color(lang)}" '
            f'stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-dasharray="{dash:.2f} {circ - dash:.2f}" '
            f'stroke-dashoffset="{seg:.2f}" '
            f'transform="rotate({rot:.2f} {cx} {donut_cy:.1f})">'
            f'<animate attributeName="stroke-dashoffset" from="{seg:.2f}" to="0" '
            f'dur="0.9s" begin="{0.1 * i:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1"/></circle>'
        )
        cumulative += frac

    # Center label: top language percentage
    top_pct = top[0][1] / total * 100 if top else 0
    lines.append(
        f'<text x="{cx}" y="{donut_cy - 3:.1f}" text-anchor="middle" '
        f'font-family="Segoe UI, Ubuntu, Sans-Serif" font-size="20" font-weight="700" '
        f'fill="#e6edf3">{top_pct:.0f}%</text>'
    )
    lines.append(
        f'<text x="{cx}" y="{donut_cy + 15:.1f}" text-anchor="middle" '
        f'font-family="Segoe UI, Ubuntu, Sans-Serif" font-size="10" fill="#8b949e">'
        f'{(top[0][0].split()[0] if len(top[0][0]) > 11 else top[0][0]) if top else ""}</text>'
    )

    # Legend rows
    y = legend_top + 12
    for i, (lang, val) in enumerate(top):
        pct = val / total * 100
        delay = 0.1 * i + 0.2
        lines.append(f'<g class="row" style="animation-delay: {delay:.2f}s">')
        lines.append(f'<circle cx="{legend_x + 5}" cy="{y - 4}" r="5.5" fill="{get_color(lang)}"/>')
        lines.append(f'<text x="{legend_x + 18}" y="{y}" class="lang-name">{lang}</text>')
        lines.append(
            f'<text x="{width - padding}" y="{y}" text-anchor="end" class="lang-pct">{pct:.1f}%</text>'
        )
        lines.append('</g>')
        y += row_h

    lines.append('</svg>')
    return '\n'.join(lines)

def main():
    token = os.environ.get('GITHUB_TOKEN')
    username = 'NooruzbekT'

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Fetch all non-fork repos
    repos, page = [], 1
    while True:
        r = requests.get(
            f'https://api.github.com/users/{username}/repos?per_page=100&page={page}',
            headers=headers
        )
        data = r.json()
        if not isinstance(data, list) or not data:
            break
        repos.extend([repo for repo in data if not repo.get('fork')])
        if len(data) < 100:
            break
        page += 1

    # Aggregate language bytes across all repos
    lang_bytes = defaultdict(int)
    for repo in repos:
        r = requests.get(
            f'https://api.github.com/repos/{username}/{repo["name"]}/languages',
            headers=headers
        )
        if r.status_code == 200:
            for lang, count in r.json().items():
                lang_bytes[lang] += count

    if not lang_bytes:
        print("No language data found")
        return

    svg = generate_svg(dict(lang_bytes))
    with open('lang-stats.svg', 'w') as f:
        f.write(svg)
    print(f"Done: {len(lang_bytes)} languages found")

if __name__ == '__main__':
    main()
