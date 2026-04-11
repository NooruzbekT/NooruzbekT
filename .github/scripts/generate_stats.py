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
    'default': '#8f8f8f'
}

def get_color(lang):
    return LANGUAGE_COLORS.get(lang, LANGUAGE_COLORS['default'])

def generate_svg(lang_data):
    top = sorted(lang_data.items(), key=lambda x: x[1], reverse=True)[:8]
    total = sum(v for _, v in top)

    width = 495
    padding = 20
    bar_height = 10
    item_height = 28
    title_h = 40
    bar_section_h = bar_height + 18
    height = title_h + bar_section_h + len(top) * item_height + padding

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>',
        '  .title { font: 600 17px "Segoe UI", Ubuntu, Sans-Serif; fill: #58a6ff; }',
        '  .lang-name { font: 400 13px "Segoe UI", Ubuntu, Sans-Serif; fill: #e6edf3; }',
        '  .lang-pct { font: 600 13px "Segoe UI", Ubuntu, Sans-Serif; fill: #8b949e; }',
        '</style>',
        f'<rect x="0.5" y="0.5" rx="10" ry="10" height="{height - 1}" width="{width - 1}" fill="#0d1117" stroke="#30363d"/>',
        f'<text x="{padding}" y="27" class="title">Most Used Languages</text>',
    ]

    # Proportional top bar
    bar_y = title_h
    bar_total_w = width - padding * 2
    x = padding
    for lang, val in top:
        w = max(2, round(val / total * bar_total_w))
        lines.append(f'<rect x="{x}" y="{bar_y}" width="{w}" height="{bar_height}" rx="3" fill="{get_color(lang)}"/>')
        x += w

    # Language rows
    y = title_h + bar_section_h
    for lang, val in top:
        pct = val / total * 100
        lines.append(f'<circle cx="{padding + 6}" cy="{y + 5}" r="5" fill="{get_color(lang)}"/>')
        lines.append(f'<text x="{padding + 18}" y="{y + 10}" class="lang-name">{lang}</text>')
        lines.append(f'<text x="{width - padding}" y="{y + 10}" text-anchor="end" class="lang-pct">{pct:.1f}%</text>')
        y += item_height

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
