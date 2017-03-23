import logging
import re
from collections import namedtuple
import requests
from bs4 import BeautifulSoup

PROJECT_URL = 'http://cordis.europa.eu/project/rcn/{}_en.html'

def extract_entry(doc, name):
    try:
        regex = re.compile('{0}[ ]*:?[ ]*'.format(name), re.IGNORECASE)
        text = doc.find(text=regex)

        if not text:
            return ''

        p = text.parent.nextSibling
        while p is not None and not p.strip():
            p = p.nextSibling

        if p is None:
            p = text.parent.text

        return re.sub(regex, '', p).strip(": \t\n|\\/")
    except:
        logging.error("FAILED ON ``{1}'': {0}".format(doc, name))
        raise

def extract_date(text):
    match = re.match(r'\d\d\d\d-\d\d-\d\d', text)
    return match.group(0) if match else None

def clean_currency(text):
    return text.replace('EUR', '').replace(' ', '')

def clean_abstract(text):
    return text.strip().replace('<p>', '').replace('</p>', '').replace('<br/>', '\n')

def get_project(rcn):
    project_page = requests.get(PROJECT_URL.format(rcn)).text
    parsed_page = BeautifulSoup(project_page)

    # Go to https://github.com/pieterheringa/cordis-scraper/blob/master/down.py
    # to see how to extract more attributes

    record = {}

    dates_section = parsed_page.find(attrs={'class': 'projdates'})
    if dates_section:
	start_date = extract_date(extract_entry(dates_section, 'From'))
	if start_date:
        	record['start_date'] = start_date
	end_date = extract_date(extract_entry(dates_section, 'To'))
	if end_date:
        	record['end_date'] = end_date

    details_section = parsed_page.find(attrs={'class': 'projdet'})
    record['cost'] = clean_currency(extract_entry(details_section, 'Total cost:'))
    record['funding'] = clean_currency(extract_entry(details_section, 'EU contribution:'))

    abstract_section = parsed_page.find(attrs={'class': 'tech'})
    record['abstract'] = clean_abstract(abstract_section.decode_contents())

    return record
