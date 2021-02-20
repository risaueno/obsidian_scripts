#### Settings ######################################

# (1)
header_name = 'Habits'
# (2)
daily_folder = '/Users/user/Obsidian/My Vault/1_Journal/Daily'
# (3)
report_folder = '/Users/user/Obsidian/My Vault/1_Journal/Daily Summary'
# (4)
tracked_items = ['Sleep 8h', 'Exercise', 'Learn French', 'Meditate']
items_are_html_emojis = False
# (5)
check_mark_symbol = '&#10004;'  # e.g. '&#9989;' (green tick), '&#10004;' (simple tick)

# Description
# (1) Looks under the following header in each daily note (may not work well if it has sub-headers under it)
# (2) Daily notes directory (note title must have year, month and day)
# (3) Summary of header will go here (saved as Summary - header_name.md)
# (4) Items (e.g. habits) you want in the tracker table. Set items_are_html_emojis to True if items are emojis
# If using emoji, items needs to be in HTML format e.g. '&#128522;'. To convert, see https://unicode.org/emoji/charts/full-emoji-list.html, https://www.compart.com/en/unicode/
# (5) Checkmark symbol

####################################################

# Advanced settings (for using external inputs):
# Usage (with header_name as 1 input): `python generate_header_summary.py header_name`

use_external_input = False

if use_external_input:
    import sys

    # Set the variables you want to override with external inputs
    header_name = sys.argv[1]  # Input 1

    # Specify your items for each header here
    if header_name == 'Habits':
        tracked_items = ['Sleep 8h', 'Exercise', 'Learn French', 'Meditate']
    elif header_name == 'Mood':
        tracked_items = ['&#128522;', '&#128524;', '&#128578;', '&#129335;', '&#128533;', '&#128579;', '&#128557;']
        items_are_html_emojis = True

    print("[{} (table)]".format(header_name))

####################################################


import os
import datetime
import markdown
import dateutil.parser as dparser
import calendar
import numpy as np
import markdownify as hm
from tomark import Tomark
import collections

# Get info from daily directory

def extract_content_from_header(html, header_name):
    partitions = html.partition('>{}<'.format(header_name))
    header_code = partitions[0][-3:] + '>'
    content = '<{}'.format(partitions[-1]).partition(header_code)[0][5:]
    return content


all_files = [entry.path for entry in os.scandir(daily_folder)]

filenames = [file.partition(daily_folder + '/')[2] for file in all_files]
try:
    dates = [dparser.parse(file, fuzzy=True).strftime('%Y-%m-%d') for file in filenames]
    sort_idx = np.argsort(dates)[::-1]
except ValueError as e:
    raise Exception("Titles of daily files must contain dates") from e


ordered_files = [all_files[i] for i in sort_idx]
ordered_dates = [dates[i] for i in sort_idx]

start_date = datetime.datetime.strptime(ordered_dates[-1], '%Y-%m-%d')
end_date = datetime.datetime.strptime(ordered_dates[0], '%Y-%m-%d')
all_dates = []
for a in range((end_date - start_date).days + 1):
    d = datetime.date(start_date.year, start_date.month, start_date.day) + datetime.timedelta(a)
    all_dates.append(d.strftime('%Y-%m-%d'))


# Read files and generate dict for table

try:
    if items_are_html_emojis:
        tracked_items = [hm.markdownify(item) for item in tracked_items]  # Convert back to emoji
except NameError:
    pass

item_dict = []
for ymd in all_dates:
    d = {k: '' for k in ['Date'] + tracked_items}
    d['Date'] = ymd
    if ymd in ordered_dates:
        file = ordered_files[ordered_dates.index(ymd)]
        f = open(file, 'r')
        html = markdown.markdown(f.read())
        content = extract_content_from_header(html, header_name)


        for item in tracked_items:
            if item in content:
                partitions = content.partition(item)
                if 'x' in partitions[0][-4:]:
                    d[item] = check_mark_symbol
            else:
                d[item] = ''

    item_dict.append(d)

# Split data into year and month

all_ym = ['{}-{}'.format(datetime.datetime.strptime(d, '%Y-%m-%d').year, datetime.datetime.strptime(d, '%Y-%m-%d').month) for d in all_dates]
unique_ym = np.unique(all_ym)
ym_split = collections.defaultdict(list)
for row in item_dict:
    y = int(row['Date'].split('-')[0])
    m = int(row['Date'].split('-')[1])
    ym_split['{}-{}'.format(y, m)].append(row)

sections = []
for ym, item_dict_split in ym_split.items():

    section_contents = []
    this_year = ym.split('-')[0]
    year_header = '<h3>{}</h3>\n'.format(this_year)
    section_contents.append(hm.markdownify(year_header))
    this_month = ym.split('-')[1]
    month_header = '<h4>{}</h4>\n'.format(calendar.month_name[int(this_month)])
    section_contents.append(hm.markdownify(month_header))
    section_contents.append(Tomark.table(item_dict_split))

    sections.append(''.join(section_contents))

# Reverse order of contents (newest at the top) and put everything together

text_md = hm.markdownify('<h2>Summary - {}</h2>\n'.format(header_name)) + '\n' + ''.join(sections[::-1])

# Generate summary note

filename = "{}/Summary - {}.md".format(report_folder, header_name)
with open(filename, 'w') as f:
    f.write(text_md)
