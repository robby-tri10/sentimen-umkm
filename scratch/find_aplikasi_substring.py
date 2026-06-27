# scratch/find_aplikasi_substring.py
with open("templates/landing.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.findall(r'aplikasi', content, re.IGNORECASE)
print(f"Found {len(matches)} occurrences of 'aplikasi' as substring.")
