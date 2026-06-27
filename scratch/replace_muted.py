# scratch/replace_muted.py
import re

files_to_modify = [
    "templates/dashboard.html",
    "templates/index.html",
    "templates/perbandingan.html",
    "templates/rekomendasi.html"
]

for filepath in files_to_modify:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace color:var(--text-muted) and color: var(--text-muted)
    new_content = re.sub(r'color:\s*var\(--text-muted\)', 'color:var(--text-secondary)', content)
    
    # Specifically for the border-color or icon background color if any, let's look at the perbandingan.html line 425:
    # color:var(--text-muted) -> color:var(--text-secondary) (this regex will match and replace it too, which is perfect)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"Updated {filepath}")
