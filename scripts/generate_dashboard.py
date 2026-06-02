import os, re, glob
from datetime import datetime
import matplotlib.pyplot as plt

log_files = sorted(glob.glob('[0-9]*/*.md'))

data = {}
date_pattern = re.compile(r'###.*(\d{4}-\d{2}-\d{2})')
excercise_pattern = re.compile(r'\* \*\*(.*?)\*\*')
set_pattern = re.compile(r'(\d+)kg\s*x\s*(\d+)')

current_date = None
current_excercise = None

for file_path in log_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            date_match = date_pattern.search(line)
            if date_match:
                current_date = datetime.strptime(date_match.group(1).strip(), "%Y-%m-%d")
                continue

            excercise_match = excercise_pattern.search(line)
            if excercise_match and current_date:
                current_excercise = excercise_match.group(1)
                if current_excercise not in data:
                    data[current_excercise] = {'dates': [], 'max_weight': []}
                continue

            set_match = set_pattern.search(line)
            if set_match and current_date and current_excercise:
                weight = int(set_match.group(1))
                if (not data[current_excercise]['dates']) or (data[current_excercise]['dates'][-1] != current_date):
                    data[current_excercise]['dates'].append(current_date)
                    data[current_excercise]['max_weight'].append(weight)
                else:
                    if weight > data[current_excercise]['max_weight'][-1]:
                        data[current_excercise]['max_weight'][-1] = weight
        f.close()

os.makedirs('public/assets', exist_ok=True)
html_charts = ""

plt.rcParams.update({
    'font.family':      'Iosevka, monospace',
    'text.color':       '#e0e0e0',
    'axes.labelcolor':  '#a0a0a0',
    'axes.edgecolor':   '#333333',
    'xtick.color':      '#888888',
    'ytick.color':      '#888888',
    'figure.facecolor': '#181818',
    'axes.facecolor':   '#181818'
})

for excercise, metrics in data.items():
    if len(metrics['dates']) < 2:
        continue

    clean_name = excercise.lower().replace(" ", "_").replace("/", "_")
    fig, ax = plt.subplots(figsize=(6, 3.2))

    ax.plot(metrics['dates'], metrics['max_weight'], marker='o', color='#d946ef', linewidth=2, markersize=5)
    ax.set_title(f'{excercise}', fontsize=11, fontweight='bold', pad=10)
    ax.grid(True, linestyle=':', alpha=0.3, color='#888888')

    fig.autofmt_xdate()
    plt.tight_layout()

    chart_path = f'public/assets/{clean_name}.png'
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close()

    html_charts += f"""
    <div class="card">
        <h2>{excercise}</h2>
        <img src="assets/{clean_name}.png" alt="{excercise} chart">
    </div>
    """

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Workout Tracker</title>
    <style>
        body {{
            font-family: "Iosevka", "Iosevka Term", monospace;
            backgroud: #181818
            color: #e0e0e0;
            max-width: 950px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        h1 {{
            text-align: center;
            color: #f43f5e;
            font-weight: 600;
            letter-spacing: -0.5px;
        }}
        .meta {{
            text-align: center;
            color: #71717a;
            margin-bottom: 40px;
            font-size: 0.9rem;
        }}
        .grid {{
            display: grid;
            grid-template-colums: repeat(auto-fit, minmax(420px, 1fr));
            gap: 24px;
        }}
        .card {{
            background: #1f1f1f;
            border: 1px solid #2e2e2e;
            border-radius: 6px;
            padding: 20px;
        }}
        .card h2 {{
            margin-top: 0;
            font-size: 1.15rem;
            color: #f4f4f5;
            border-bottom: 1px solid #2e2e2e;
            padding-bottom: 8px;
        }}
        img {{
            max-width: 100%;
            display: block
            margin: 10px auto 0 auto;
        }}
    </style>
</head>
<body>
    <h1>WORKOUT_TRACKER</h1>
    <p class="meta">LAST_SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    <div class="grid">
        {html_charts if html_charts else '<p style="grid-column: 1/-1; text-align: center; color: #71717a;">Need more data brovski</p>'}
    </div>
</body>
</html>
"""

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
    f.close()


