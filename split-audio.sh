#!/bin/bash

if [ "$#" -ne 1 ]; then
	COURSE_DIR="."
else
	COURSE_DIR="$1"
fi

# Convert input files to .wav and concatenate
for FILE in "$COURSE_DIR"/*.m4b; do
	ffmpeg -i "$FILE" "${FILE%.*}".wav
done

find "$COURSE_DIR" -iname '*.wav' -printf "file '%p'\n" | sort > long_files.txt
ffmpeg -f concat -safe 0 -i long_files.txt -c copy source.wav

# Extract files from source.wav
python3 extract_chapters.py --separator sample.wav --within source.wav --titles "$COURSE_DIR"/titles.txt

# Convert resulting chapters to .mp3
for FILE in Chapter*.wav; do
	ffmpeg -i "$FILE" -acodec libmp3lame "$COURSE_DIR"/"${FILE%.*}".mp3
	rm "$FILE"
done


# Remove temporary .wav files
rm source.wav
for FILE in "$COURSE_DIR"/*.m4b; do
	rm "${FILE%.*}".wav
done
rm long_files.txt

