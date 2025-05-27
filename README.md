# Word Frequency Counter with Multithreading

A Python program that counts word frequencies in a text file using multiple threads for efficient processing.

## Features
- Splits large files into segments for parallel processing
- Handles word boundaries correctly
- Provides both per-thread intermediate results and final consolidated counts
- Configurable number of threads/segments

## Prerequisites
- Python 3.6+
- No additional packages required

## Run
- cd word-frequency-counter

## Basic Command
- python word_counter.py <input_file> <num_segments>

## Run with 4 segments
python word_counter.py sample.txt 4

# Arguments
Argument	Description
<input_file>	Path to text file to analyze
<num_segments>	Number of segments/threads to use (integer ≥ 1)
