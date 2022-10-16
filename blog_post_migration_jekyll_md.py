"""
This scripts take Jekyll blog posts from a particular directory and converts
them to the Quarto format.
"""

import os
import shutil
from pathlib import Path

input_dir = Path("/Users/aet/Documents/git_projects/Website/home/_posts/")
end_dir = Path("/Users/aet/Dropbox/noodling/quarto-blog/blog/posts/")

file_names = [x for x in input_dir.glob("*.md")]

date_strs = [x.name[:10] for x in file_names]
post_title_strs = [x.name[11:].split(".")[0].lower() for x in file_names]
# Create a new directory for each
for date, file, title_str in zip(date_strs, file_names, post_title_strs):
    os.mkdir(end_dir / title_str)
    dest_file = end_dir / title_str / "index.md"
    shutil.copyfile(file, dest_file)
    # Now write an extra line with data into each of the new files
    with open(dest_file, "r") as f:
        contents = f.readlines()
    contents.insert(1, f'date: "{date}"\n')
    with open(dest_file, "w") as f:
        contents = "".join(contents)
        f.write(contents)
