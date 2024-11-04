
# MD5Sift

**MD5Sift** is a CLI tool written in Python that generates MD5 checksum reports for files within a local directory or network share. It supports filtering files by extension or from a provided list of file names and outputs the results into a CSV report.

## Features

- Calculate MD5 checksums for files in a directory.
- Filter files by extension or from a provided file list.
- Multi-threaded processing for faster checksum generation.
- Progress reporting with verbose mode.
- CSV output of file paths, MD5 hashes, and last modified timestamps.
- Uses only standard Python libraries.

## Requirements

- Python 3.x

## Installation

Clone the repository or download the `md5sift.py` file.

```bash
git clone https://github.com/madebyjake/md5sift.git \
&& cd md5sift
```

## Usage

```bash
python md5sift.py -s <scan_directory> -o <output_file> [OPTIONS]
```

If no `--scan-path` is provided, the tool scans the current directory by default. Similarly, if no `--output` path is provided, the output CSV file will be saved as `md5_report.csv` in the current directory.

### Arguments

- `-s, --scan-path`: Path to the directory to scan. Defaults to the current directory.
- `-o, --output`: Path to the output CSV file. Defaults to `md5_report.csv` in the current directory.
- `-e, --extension`: Only process files with the specified extension (e.g., `.txt`).
- `-f, --filelist`: Path to a CSV file containing specific file names to process.
- `-v, --verbose`: Enable verbose mode for real-time progress reporting.
- `-t, --threads`: Number of threads to use for processing (default: CPU core count).
- `--test`: Run in test mode and specify how many files to process (e.g., `--test 10` for first 10 files).

### Example

```bash
# Basic example to scan the current directory and output the report in the current directory
python md5sift.py

# Example with file extension filter
python md5sift.py -s /path/to/scan -o /path/to/output/report.csv -e .txt

# Example with a file list filter and verbose mode
python md5sift.py -s /path/to/scan -o /path/to/output/report.csv -f /path/to/filelist.csv -v

# Test mode (process first 10 files)
python md5sift.py -s /path/to/scan -o /path/to/output/report.csv --test 10
```

## Logging

MD5Sift uses logging to provide detailed information. By default, logging is set to `INFO` level. Enable verbose mode (`-v`) to get real-time progress reports.

## License

This project is licensed under the MIT License.
