#### Settings ######################################

header_name = 'Morning pages'  # Name of header you want to summarise
display_individual_dates = True  # Entries in bullet points if False
compact_view = True  # Entries on the same line as the dates (N/A for lists or if using bullet points)

# Daily notes directory (note title must have full date info)
daily_folder = '/Users/username/Obsidian/My Vault/Daily'

# Summary of header will go here (header_name.md)
report_folder = '/Users/username/Obsidian/My Vault/Journal Reports'

####################################################

import os
import markdown
import dateutil.parser as dparser
import calendar
import numpy as np
import markdownify as hm

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

contents = []
last_year = None
last_month = None

for i, file in enumerate(ordered_files):

    dt = ordered_dates[i]
    this_year = dt.split('-')[0]
    this_month = dt.split('-')[1]

    f = open(file, 'r')
    html = markdown.markdown(f.read())

    content = extract_content_from_header(html, header_name)

    # If content exists
    if len(content.replace('\n', '')) > 0:

        if last_year != this_year:
            contents.append('<h3>{}</h3>\n'.format(this_year))
        if last_month != this_month:
            contents.append('<h4>{}</h4>\n'.format(calendar.month_name[int(this_month)]))

        last_year = this_year
        last_month = this_month

        if display_individual_dates:
            if compact_view:
                # Display on the same line if content is short
                if content.count('\n') <= 2 and content[:1] == '\n':
                    content = content[1:]
                contents.append("<b>{}</b>: {}".format(dt, content))
                # contents.append("{}: {}".format(dt, content))
            else:
                contents.append("<h5>{}</h5>{}\n".format(dt, content))
        else:
            # Convert paragraphs into bullet points
            content = content.replace('<p>', '<ul>\n<li>')
            content = content.replace('</p>', '</li>\n</ul>')
            contents.append("{}\n".format(content))

if len(contents) == 0:
    raise AttributeError('No contents - are you sure this header exists?')

# Put everything together

all_contents = '<h2>Summary - {}</h2>\n{}'.format(header_name, ''.join(contents))
text_md = hm.markdownify(all_contents)  # Convert html to markdown

# Generate summary note

filename = "{}/Summary: {}.md".format(report_folder, header_name)
with open(filename, 'w') as f:
    f.write(text_md)
