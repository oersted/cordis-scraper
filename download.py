import csv
import json
import sys
import tqdm

from cordis_scraper import get_project

dataset_path = sys.argv[1]
output_path = sys.argv[2]

with open(dataset_path, 'r') as dataset_file:
    record_count = sum(1 for line in dataset_file)

dataset_file = open(dataset_path, 'r')
output_path = open(output_path, 'w')

dataset_reader = csv.reader(dataset_file, delimiter=';')
next(dataset_reader)  # dump header

for row in tqdm.tqdm(dataset_reader, total=record_count):
    rcn = row[0]
    project = get_project(rcn)
    project['rcn'] = rcn
    json_line = json.dumps(project)
    output_path.write(json_line + '\n')

dataset_file.close()
output_path.close()