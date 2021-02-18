#### Settings ######################################

# Daily notes directory (note title must have full date info)
daily_folder = '/Users/username/Obsidian/My Vault/Daily'

# Looks under the following header in each daily note
header_name = 'Habits'

# Habits you want in the habit tracker table
habits_tracked = ['Sleep 8h', 'Exercise', 'Learn French', 'Meditate']

# Summary of header will go here (saved as header_name.md)
report_folder = '/Users/username/Obsidian/My Vault/Journal Reports'

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


def extract_content_from_header(html, header_name):
    partitions = html.partition('>{}<'.format(header_name))
    header_code = partitions[0][-3:] + '>'
    content = '<{}'.format(partitions[-1]).partition(header_code)[0][5:]
    return content

all_files = [entry.path for entry in os.scandir(daily_folder)]
try:
    dates = [dparser.parse(file, fuzzy=True).strftime('%Y-%m-%d') for file in all_files]
    sort_idx = np.argsort(dates)[::-1]
except ValueError as e:
    raise Exception("Titles of daily files must contain dates") from e

ordered_files = [all_files[i] for i in sort_idx]
ordered_dates = [dates[i] for i in sort_idx]

start_date = datetime.datetime.strptime(ordered_dates[-1], '%Y-%m-%d')
end_date = datetime.datetime.strptime(ordered_dates[0], '%Y-%m-%d')
all_dates = []
for a in range((end_date - start_date).days):
    d = datetime.date(start_date.year, start_date.month, start_date.day) + datetime.timedelta(a)
    all_dates.append(d.strftime('%Y-%m-%d'))


habit_dict = []

for ymd in all_dates:
    d = {k: '' for k in ['Date'] + habits_tracked}
    d['Date'] = ymd

    if ymd in ordered_dates:
        file = ordered_files[ordered_dates.index(ymd)]
        f = open(file, 'r')
        html = markdown.markdown(f.read())
        content = extract_content_from_header(html, header_name)

        for habit in habits_tracked:
            if habit in content:
                partitions = content.partition(habit)
                if 'x' in partitions[0][-4:]:
                    d[habit] = '&#9745;'
            else:
                d[habit] = ''

    habit_dict.append(d)


all_ym = ['{}-{}'.format(datetime.datetime.strptime(d, '%Y-%m-%d').year, datetime.datetime.strptime(d, '%Y-%m-%d').month) for d in all_dates]
unique_ym = np.unique(all_ym)

ym_split = collections.defaultdict(list)
for row in habit_dict:
    y = int(row['Date'].split('-')[0])
    m = int(row['Date'].split('-')[1])
    ym_split['{}-{}'.format(y, m)].append(row)

sections = []
for ym, habit_dict_split in ym_split.items():

    section_contents = []
    this_year = ym.split('-')[0]
    year_header = '<h3>{}</h3>\n'.format(this_year)
    section_contents.append(hm.markdownify(year_header))
    this_month = ym.split('-')[1]
    month_header = '<h4>{}</h4>\n'.format(calendar.month_name[int(this_month)])
    section_contents.append(hm.markdownify(month_header))
    section_contents.append(Tomark.table(habit_dict_split))

    sections.append(''.join(section_contents))

text_md = hm.markdownify('<h2>{}</h2>\n'.format(header_name)) + '\n' + ''.join(sections[::-1])

filename = "{}/Summary - {}.md".format(report_folder, header_name)
with open(filename, 'w') as f:
    f.write(text_md)
