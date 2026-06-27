# scratch/replace_aplikasi.py
with open("templates/landing.html", "r", encoding="utf-8") as f:
    content = f.read()

# Show matches before replacement
import re
matches = re.findall(r'\baplikasi\b', content, re.IGNORECASE)
print(f"Found {len(matches)} matches of 'aplikasi'")

# Replace
content_new = re.sub(r'\baplikasi\b', 'website', content)
content_new = re.sub(r'\bAplikasi\b', 'Website', content_new)

with open("templates/landing.html", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Replacement done!")
