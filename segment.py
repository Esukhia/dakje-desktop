import os
import click
from pytib import Segment
s = Segment()
s.include_user_vocab()


def segment(input, output):
    text = open_file(input)
    segmented = s.segment(text, unknown=0, reinsert_aa=False, space_at_punct=True, distinguish_ra_sa=True,
                          affix_particles=True)
    segmented = segmented.replace('ᛰ', '')
    write_file(output, segmented)


@click.command()
@click.option('--file', default=None, help='input file')
@click.option('--folder', default=None, help='segment all files in a folder')
def segment_folder(folder, file):
    if folder:

        for f in os.listdir(folder):
            segment(folder+'/'+f, f.split('.')[0] + '_segmented.txt')
    elif file:
        segment(file, file.split('.')[0] + '_segmented.txt')


def write_file(file_path, content):
    with open(file_path, 'w', -1, 'utf8') as f:
        f.write(content)


def open_file(file_path):
    try:
        with open(file_path, 'r', -1, 'utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', -1, 'utf-16-le') as f:
            return f.read()


if __name__ == '__main__':
    segment_folder()
