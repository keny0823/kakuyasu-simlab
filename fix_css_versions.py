import os
from pathlib import Path

repo = Path(r"c:\Users\since\Blue Ocean\kakuyasu-simlab-repo")
files_to_check = [repo / "index.html"] + list((repo / "output").glob("*.html"))

for file_path in files_to_check:
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        import re
        # Add ?v=3.2 to style.css link safely
        content = re.sub(r'style\.css(?:[?&]v=[0-9.]+)?', 'style.css?v=3.2', content)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
print("Updated HTML files with utf-8 encoding safely.")
