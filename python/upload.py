import argparse
import csv
import os
import paygsdk
import time


# Python's csv module limits cell sizes to 131072 characters (i.e., 2^17, or
# 128k).  Some CSVs have extremely long text, so we set max cell size to four
# times that; bear in mind that that's already longer than the 500,000
# characters that the API allows in a document.
csv.field_size_limit(2 ** 19)

# Number of documents to load at once
BLOCK_SIZE = 1000

DATE_FORMATS = [
    '%Y-%m-%dT%H:%M:%S.%fZ',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y-%m-%d',
    '%m/%d/%Y',
    '%m/%d/%y',
    '%m/%d/%y %H:%M'
]

FIELD_TYPES = ['date', 'number', 'score', 'string']


def upload_documents(client, project_id, input_file, offset=0, max_len=0, skip_build=False, skip_sentiment_build=False):
    # convert max_len into None if it's 0, to allow indexing later
    if not max_len:
        max_len = None

    # Extract the documents from the CSV file and upload them in batches.
    with open(input_file, 'r', encoding='utf-8-sig') as file:
        for i, docs in parse_csv_file(file, max_len):

            done = False
            tries = 0
            while (not done):
                try:
                    # i is where the file pointer is after the read (at the end of docs)
                    if i-len(docs) >= offset:
                        print('Uploading at {}, {} new documents'.format((i-len(docs)), len(docs)))
                        resp = client.upload(project_id, docs)
                        done = True
                    elif i > offset:
                        # need to do a partial write
                        print('Uploading at {}, {} new documents'.format(offset, (i-offset)))
                        resp = client.upload(project_id, docs=docs[offset-(i-len(docs)):])
                        done = True
                    else:
                        done = True
                except ConnectionError:
                    tries = tries + 1
                    if tries > 5:
                        print('Upload failed - connection error aborting')
                        raise
    print('Done uploading.')

    options = {}
    if skip_sentiment_build:
        options['sentiment_configuration'] = {'type': 'none'}

    if not skip_build:
        resp = client.build(project_id, skip_sentiment_build)
        if resp is None:
            print('Build started')
        else:
            print(f'error: {resp}')

    return True


def parse_csv_file(file, max_text_length):
    """
    Given a file and a length at which to truncate document text, yield batches
    of documents suitable for uploading.
    """
    # Note that we don't use a DictReader here because there may be
    # multiple columns with the same header
    reader = csv.reader(file)

    # Parse the first row of the CSV as a header row, storing the results in
    # a list whose elements are:
    # * for text/title: the string "text" or "title"
    # * for metadata fields: the pair (data_type, field_name)
    # * for unparseable headers: None
    columns = []
    for col_num, cell in enumerate(next(reader), start=1):
        data_type, _, data_name = cell.partition('_')
        data_type = data_type.strip().lower()
        if data_type in ('text', 'title') and not data_name:
            columns.append(data_type)
        elif data_type in FIELD_TYPES:
            columns.append((data_type, data_name))
        else:
            print('Uninterpretable header "{}" in column'
                  ' {}'.format(cell, col_num))
            columns.append(None)

    # If there is not exactly one "text" column, raise an error
    text_count = columns.count('text')
    if text_count != 1:
        raise RuntimeError('Must have exactly one text column,'
                           ' found {}'.format(text_count))

    docs = []
    i = None
    for i, row in enumerate(reader, start=1):
        new_doc = {'metadata': []}
        for header, cell_value in zip(columns, row):
            # For each cell in the row: if the header was unparseable, skip it;
            # if the header is text/title, add that to the document; otherwise,
            # parse it as metadata
            if header is None:
                continue
            elif header == 'text':
                new_doc['text'] = cell_value[:max_text_length]
            elif header == 'title':
                new_doc['title'] = cell_value
            else:
                # Blank cells indicate no metadata value
                cell_value = cell_value.strip()
                if not cell_value:
                    continue
                try:
                    metadata_field = parse_metadata_field(header, cell_value)
                    new_doc['metadata'].append(metadata_field)
                except ValueError as e:
                    print(
                        'Metadata error in document {}: {}'.format(i, str(e))
                    )
        docs.append(new_doc)

        if len(docs) >= BLOCK_SIZE:
            yield i, docs
            docs = []

    if i is None:
        raise RuntimeError('No documents found')

    if docs:
        yield i, docs


def parse_metadata_field(type_and_name, cell_value):
    """
    Given a (type, name) pair and a value, return a metadata dict with type,
    name, and the parsed value.  Raises a ValueError if "value" cannot be
    parsed as the given type.
    """
    data_type, field_name = type_and_name
    value = None
    if data_type == 'date':
        if cell_value.isnumeric():
            value = int(cell_value)
        else:
            for df in DATE_FORMATS:
                try:
                    value = int(time.mktime(time.strptime(cell_value, df)))
                except ValueError:
                    continue
                break
    elif data_type in ('number', 'score'):
        try:
            value = float(cell_value.strip())
        except ValueError:
            pass
    elif data_type == 'string':
        value = cell_value
    if value is None:
        raise ValueError(
            'Cannot parse "{}" value "{}" as {}'.format(
                field_name, cell_value, data_type
            )
        )
    return {'type': data_type, 'name': field_name, 'value': value}


# curl -X POST -H "Authorization: Token $LUMI_PAYG_TOKEN" http://44.202.215.50:5002/api/v5/projects/<project_id>/upload
def main():
    parser = argparse.ArgumentParser(
        description=('Upload documents to a Luminoso Payg project')
    )

    parser.add_argument('project_id', help="Specify the project id")
    parser.add_argument('input_file', help='CSV file with project data')
    parser.add_argument(
        '-m', '--max_text_length', default=0, type=int, required=False,
        help='The maximum length to limit text fields'
    )
    parser.add_argument(
        '-s', '--skip_build', action='store_true', default=False,
        help='Skip the project build after upload'
    )
    parser.add_argument(
        '-ss', '--skip_sentiment_build', action='store_true', default=False,
        help='Allows the build to skip the sentiment build'
    )
    parser.add_argument(
        '-b', '--wait_for_build_complete', action='store_true', default=False,
        help='Wait for the build to complete'
    )
    args = parser.parse_args()

    input_file = args.input_file
    project_id = args.project_id
    max_len = args.max_text_length

    token = os.environ["LUMI_PAYG_TOKEN"]
    client = paygsdk.LumiPaygSdk(token=token)

    rc = upload_documents(client, project_id, input_file,
                          max_len=max_len,
                          skip_build=args.skip_build,
                          skip_sentiment_build=args.skip_sentiment_build)

    print(f"{rc}")


if __name__ == '__main__':
    main()