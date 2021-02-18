## Obsidian: Summarise daily entries

Python scripts to generate summary pages from historical daily notes by entries under headers (generate_header_summary.py) and generate a table to summarise tracked habits from daily notes (generate_habit_table.py).

### Usage

Python 3.7
1. Install dependencies `pip install numpy markdownify Tomark`
2. Edit settings at the top of the .py script
3. Run script `python generate_header_summary.py`
4. Summary notes should appear automatically in Obsidian in spefified folder

### Note

- Early prototype for personal use and not tested extensively :)
- If you use a header that has sub-headers it doesn't display quite as nicely
- Habit tracking only works for checked/unchecked boxes for now
