# Split-audio-by-separator
## Introduction
These scripts can split several audio files into separate chunks, using an audio sample as separator. It is useful when a series of audio files of roughly the same length have been concatenated into one or various files, and there is some jingle or sound effect at the beginning or end of each section. It does so by performing a cross-correlation between the source audio file and the specified acoustic separator, and splitting the source audio file around the points where the cross-correlation is maximum.

Some potential use cases could be splitting an audiobook into chapters, or a course into its individual lessons.

## Motivation
I acquired several online courses in audio format, each composed of numerous lectures of roughly the same length. All the lectures from each course were bundled in a single file, with a jingle in between lectures. These scripts automated the separation of each course into individual files, one per lesson.

## Important note on usefulness
This project is not really intended for general use as is (e.g. it presupposes the extension of the input files), and was mostly done as a learning experience. The format in which the courses came, `.m4b`, is an audiobook format: it is a collection of audio files, and it internally contains the necessary metadata to extract the individual sections from it without any audio processing. Thus, there are better tools available for the job in that case (see for example [this script](https://gist.github.com/nitrag/a188b8969a539ce0f7a64deb56c00277)).

## Dependencies
This project is intended to be run on a Linux environment, with the following tools installed:
* ffmpeg
* python3
* The Python packages specified in `requirements.txt`

## Usage
To run the script, simply create a directory for the project to be split. Place in said directory the `.m4b` files (you may use a different input format if you slightly update the `split-audio.sh` script). You may also optionally include a `titles.txt` file, containing the title you want to give to each section, one name per line.

Then, place the acoustic separator, `sample.wav`, in the same directory as these scripts, and run:
```
$ split-audio.sh <project_directory>
```
The output `.mp3` files will be found in the project directory.

### Example
```
$ tree
.
├── extract_chapters.py
├── philosophy-course
│   ├── Part1.m4b
│   ├── Part2.m4b
│   └── titles.txt
├── requirements.txt
├── sample.wav
└── split-audio.sh

$ ./split-audio.sh philosophy-course
```

## Acknowledgements
The code for finding the jingle inside the directory draws heavily from [this tutorial](https://dev.to/hiisi13/find-an-audio-within-another-audio-in-10-lines-of-python-1866) by Dmitry Kozhedubov.
