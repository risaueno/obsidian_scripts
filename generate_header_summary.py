#### Settings ######################################

# (1)
header_name = 'To do'
# (2)
daily_folder = '/Users/user/Obsidian/My Vault/1_Journal/Daily'
# (3)
report_folder = '/Users/user/Obsidian/My Vault/1_Journal/Daily Summary'
# (4)
display_transclusion = True
# (5)
display_type = 'dates'  # Choose from: 'dates', 'dates_compact', 'bullet'

# Description
# (1) Name of header you want to summarise (make sure this exists in your dailies)
# (2) Daily notes directory (note title must have full date info)
# (3) Summary of header will go here (header_name.md)
# (4) Display summary entries as transclusion (links to original entries).
# Recommended for To do lists - checking boxes will also check it in the daily note and vice versa
# If False, summary entries will consist of text copied (unlinked) from daily notes
# This is recommended for a cleaner diary view (but if summarising headers that has sub-headers, setting display_transclusion=True may generate a prettier report).
# (5) Display mode options (N/A for transclusion) - 'date': dated entries as headers, 'dates_compact': dates and contents in same line view, 'bullet': undated entries in bullet points (N/A for lists and multiple paragraphs)

####################################################

# Advanced settings (for using external inputs):
# Usage (with 3 inputs): `python generate_header_summary.py header_name display_transclusion display_type`

use_external_input = False

if use_external_input:
    import sys

    # Set the variables you want to override with external inputs
    header_name = sys.argv[1]  # Input 1
    display_transclusion = True if sys.argv[2] == 'true' else False  # Input 2
    display_type = sys.argv[3]  # Input 3

    print("[{}, transclusion={}, display={}]".format(header_name, display_transclusion, display_type))

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


def content_exists(html):
    import re
    text_content = html.replace('\n', '')
    regex = re.compile('<h.>|</h.>')
    matches = re.findall(regex, text_content)
    for i in range(int(len(matches) / 2)):
        text_content = re.sub('{}.*?{}'.format(matches[i], matches[i + 1]),'', text_content, flags=re.DOTALL)
    if len(text_content) > 0:
        return True
    else:
        return False


# Get info from daily directory

all_files = [entry.path for entry in os.scandir(daily_folder)]
filenames = [file.partition(daily_folder + '/')[2] for file in all_files]
try:
    dates = [dparser.parse(file, fuzzy=True).strftime('%Y-%m-%d') for file in filenames]
    sort_idx = np.argsort(dates)[::-1]
except ValueError as e:
    raise Exception("Titles of daily files must contain dates") from e

ordered_files = [all_files[i] for i in sort_idx]
ordered_dates = [dates[i] for i in sort_idx]

contents = []
last_year = None
last_month = None

# Read daily files and collect relevant data

if display_transclusion:

    for i, file in enumerate(ordered_files):

        dt = ordered_dates[i]
        this_year = dt.split('-')[0]
        this_month = dt.split('-')[1]

        f = open(file, 'r')
        html = markdown.markdown(f.read())
        content = extract_content_from_header(html, header_name)

        if content_exists(content):

            if last_year != this_year:
                contents.append('## {}\n'.format(this_year))
            if last_month != this_month:
                contents.append('### {}\n'.format(calendar.month_name[int(this_month)]))

            last_year = this_year
            last_month = this_month

            filename = file.partition(daily_folder + '/')[2].partition('.md')[0]
            if display_type == 'dates':
                contents.append('##### {}\n'.format(dt))
            elif display_type == 'dates_compact':
                contents.append('{} \n'.format(dt))
            contents.append('![[{}#{}]]\n'.format(filename, header_name))

    # Put everything together

    contents = ''.join(contents)
    title = '<h1>Summary - {}</h1>\n'.format(header_name)
    text_md = hm.markdownify(title) + contents

else:

    for i, file in enumerate(ordered_files):

        dt = ordered_dates[i]
        this_year = dt.split('-')[0]
        this_month = dt.split('-')[1]

        f = open(file, 'r')
        html = markdown.markdown(f.read())
        content = extract_content_from_header(html, header_name)

        # if len(content.replace('\n', '')) > 0:
        if content_exists(content):

            if last_year != this_year:
                contents.append('<h2>{}</h2>\n'.format(this_year))
            if last_month != this_month:
                contents.append('<h3>{}</h3>\n'.format(calendar.month_name[int(this_month)]))

            last_year = this_year
            last_month = this_month

            if display_type == 'dates_compact':
                # Display on the same line if content is short
                if content.count('\n') <= 2 and content[:1] == '\n':
                    content = content[1:]
                contents.append("<b>{}</b>: {}".format(dt, content))

            elif display_type == 'dates':
                contents.append("<h4>{}</h4>{}\n".format(dt, content))
            elif display_type == 'bullet':
                # Convert paragraphs into bullet points
                content = content.replace('<p>', '<ul>\n<li>')
                content = content.replace('</p>', '</li>\n</ul>')
                contents.append("{}\n".format(content))
            else:
                raise AttributeError("display_type = {} not recognised".format(display_type))

    if len(contents) == 0:
        raise AttributeError('No contents - are you sure this header exists?')

    # Put everything together

    all_contents = '<h1>Summary - {}</h1>\n{}'.format(header_name, ''.join(contents))
    text_md = hm.markdownify(all_contents)

# Generate summary note

filename = "{}/Summary - {}.md".format(report_folder, header_name)
with open(filename, 'w') as f:
    f.write(text_md)
