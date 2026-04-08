import os
import re
from pathlib import Path

repo = Path(r"c:\Users\since\Blue Ocean\kakuyasu-simlab-repo")
files_to_check = [repo / "index.html"] + list((repo / "output").glob("*.html"))

def remove_punctuation_from_text(html):
    # Split by tags
    parts = re.split(r'(<[^>]+>)', html)
    for i in range(len(parts)):
        if not parts[i].startswith('<'):
            # It's text outside tags
            # Remove 。 (replace with empty string)
            # Replace 、 with a space to keep words separated
            parts[i] = parts[i].replace("。", "").replace("、", " ")
    return ''.join(parts)

for file_path in files_to_check:
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        content = remove_punctuation_from_text(content)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
print("Removed ALL '。' and '、' from all HTML files.")
