# Path hack.
import sys
import os

sys.path.insert(0, os.path.abspath('..'))

import argparse
import csv

from aspire.web import create_app
from aspire.domain.Rater import Rater
from aspire.repo import RatingManualRepository

parser = argparse.ArgumentParser(description="Provided a rating_manual_id and csv file location, runs a rater and "
                                             "saves results")
parser.add_argument('--rating-manual-id', '-id', required=True, help='The id of the rating manual to use',
                    dest='rating_manual_id')
parser.add_argument('--csv', required=True, help='The path to the CSV file', dest='file_path')
args = parser.parse_args()

rating_manual_id = args.rating_manual_id
file_path = args.file_path

with open(file_path) as csv_file:
    reader = csv.DictReader(csv_file)
    rows = [row for row in reader]

app = create_app()
repository = RatingManualRepository.RatingManualRepository(app.session)

if not rows or len(rows) == 0:
    raise Exception("No Data To Process!")

keys = {}
for count, row in enumerate(rows):
    print("Processing Row #" + str(count))
    manual = repository.get(1)
    rater = Rater(manual)
    rate = rater.rate(row.copy())
    row['rate'] = rate
    if count == 1:
        keys = row.keys()

with open(file_path, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, keys)
    writer.writeheader()
    writer.writerows(rows)

print("Done!")
