import argparse

import librosa
import numpy as np
from scipy import signal
import subprocess
import os
import math


def delete_file(file):
    """
    Deletes the specified file.
    Does not throw any exceptions.
    """
    try:
        os.remove(file)
    except:
        # Do nothing if file doesn't exist
        pass


def find_offset(within_file, find_file, window):
    """
    Finds the offset in within_file where find_file may be found.
    It uses at most the first window seconds of find_file for the look up.
    """
    y_within, sr_within = librosa.load(within_file, sr=None)
    y_find, _ = librosa.load(find_file, sr=sr_within)

    c = signal.correlate(y_within, y_find[:sr_within*window], mode='valid', method='fft')
    peak = np.argmax(c)
    offset = round(peak / sr_within, 2)

    return offset


def extract_portion(from_file,
                    start_time_seconds,
                    length_seconds,
                    output_file):
    """
    Extracts the section [start_time_seconds, start_time_seconds + length_seconds] from
    from_file, and saves it in output_file.
    """
    delete_file(output_file)
    command = ['ffmpeg', '-ss', '%.2f' % start_time_seconds,
               '-t', '%.2f' % length_seconds,
               '-i', from_file, output_file]
    subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def parse_titles(title_file):
    """
    Parses the titles file.
    In case of error, returns an empty list.
    """
    try:
        with open(title_file, 'r') as src:
            return [line.strip()
                    for i, line in enumerate(src.readlines())]
    except:
        return []


def get_file_name_for_chapter(chapter_number, titles):
    """
    Given the parsed titles, it creates the file name for chapter number
    chapter_number.
    If a title is not found among the parsed titles, it returns a simple title.
    """
    if len(titles) < chapter_number-1:
        return 'Chapter %02d.wav' % chapter_number
    return 'Chapter %02d - %s.wav' % (chapter_number, titles[chapter_number-1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--separator',
                        metavar='wav audio file',
                        type=str,
                        help='Separator between chapters')

    parser.add_argument('--within',
                        metavar='wav audio file',
                        type=str,
                        help='Within file')

    parser.add_argument('--window',
                        metavar='seconds',
                        type=int,
                        default=10,
                        help='Only use first n seconds of separator')

    parser.add_argument('--chapter_length',
                        metavar='minutes',
                        type=int,
                        default=30,
                        help='Average length of chapter')

    parser.add_argument('--chapter_variability',
                        metavar='minutes',
                        type=int,
                        default=5,
                        help='Maximum divergence a single chapter might have from the average length')

    parser.add_argument('--titles',
                        metavar='txt file',
                        type=str,
                        default=None,
                        help='File containing title of chapters (one per line)')

    args = parser.parse_args()

    titles = parse_titles(args.titles)

    search_offset_seconds = (args.chapter_length - args.chapter_variability) * 60
    search_window_seconds = args.chapter_variability* 2 * 60
    max_chapter_length_seconds = (args.chapter_length + args.chapter_variability) * 60

    start_time_seconds = 0.0
    current_chapter = 1

    # Keep looking for chapters while there's still more than
    while librosa.get_duration(filename=args.within) - start_time_seconds > max_chapter_length_seconds:
        # Create a separate .wav file with the region we want to look into
        # This is necessary because the software can't handle files which are
        # too large
        tmp_file_name = 'tmp_448c56ad9aa108678157e42e59ec8a81.wav'
        extract_portion(args.within,
                        start_time_seconds + search_offset_seconds,
                        max_chapter_length_seconds,
                        tmp_file_name)

        offset = find_offset(tmp_file_name, args.separator, args.window)
        file_length_seconds = search_offset_seconds + offset
        extract_portion(args.within,
                        start_time_seconds,
                        file_length_seconds,
                        get_file_name_for_chapter(current_chapter, titles))
        start_time_seconds += file_length_seconds
        print('Extracted chapter %d (length %02d:%02d.%02d)'
              % (current_chapter,
                 int(file_length_seconds) // 60,
                 int(file_length_seconds) % 60,
                 int(math.modf(file_length_seconds)[0]*100)))
        current_chapter += 1

    # Extract the last chapter too
    extract_portion(args.within,
                    start_time_seconds,
                    librosa.get_duration(filename=args.within) - start_time_seconds,
                    get_file_name_for_chapter(current_chapter, titles))
    print('Extracted chapter %d (length %02d:%02d.%02d)'
            % (current_chapter,
                int(file_length_seconds) // 60,
                int(file_length_seconds) % 60,
                int(math.modf(file_length_seconds)[0]*100)))
    delete_file(tmp_file_name)


if __name__ == '__main__':
    main()
