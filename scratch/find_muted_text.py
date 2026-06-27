# scratch/find_muted_text.py
import os
import re

templates_dir = "templates"
for file in os.listdir(templates_dir):
    if file.endswith('.html'):
        filepath = os.path.join(templates_dir, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find elements with text-muted inline color or style using it
            matches = re.findall(r'color:\s*var\(--text-muted\)', content, re.IGNORECASE)
            if matches:
                print(f"File: {file} - found {len(matches)} inline instances of var(--text-muted)")
                
                # print lines with context
                for i, line in enumerate(content.splitlines(), 1):
                    if 'color:var(--text-muted)' in line or 'color: var(--text-muted)' in line:
                        print(f"  Line {i}: {line.strip()}")
