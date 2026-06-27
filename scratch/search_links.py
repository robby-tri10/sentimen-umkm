# scratch/search_links.py
import os
import re

templates_dir = r"c:\Users\Robby Tri Ardianto\sentimen-umkm\templates"
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'href=["\'][^"\']*["\']', content)
                if matches:
                    print(f"File: {file}")
                    for match in matches:
                        print(f"  {match}")
