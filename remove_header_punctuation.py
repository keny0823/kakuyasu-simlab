import os
import re
from pathlib import Path

repo = Path(r"c:\Users\since\Blue Ocean\kakuyasu-simlab-repo")
files_to_check = [repo / "index.html"] + list((repo / "output").glob("*.html"))

def remove_punctuation(match):
    # match.group(0) is the entire heading tag including content
    text = match.group(0)
    # Remove `。` and `、`
    text = text.replace("。", "").replace("、", "")
    return text

for file_path in files_to_check:
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Regex to find all h1 to h6 tags and their contents
        # This will safely replace inside the entire block of <hX>...</hX>
        content = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', remove_punctuation, content, flags=re.DOTALL)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
print("Removed '。' and '、' from all headings.")
