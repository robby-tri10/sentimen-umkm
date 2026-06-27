# scratch/find_muted_css.py
with open("static/css/style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'var(--text-muted)' in line:
        print(f"Line {i}: {line.strip()}")
