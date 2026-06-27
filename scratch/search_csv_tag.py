# scratch/search_csv_tag.py
with open("static/css/style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if '.csv-tag' in line or 'csv-tag' in line:
        print(f"Line {i}: {line.strip()}")
