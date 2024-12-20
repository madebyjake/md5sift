#!/usr/bin/env python3

import os
import hashlib
import csv
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Set, Tuple

# Configure logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_hash(file_path: str, algorithm: str, verbose: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
    """Calculate the hash of a file using the specified algorithm."""
    # Select the hash function based on the provided algorithm
    algorithm_lower = algorithm.lower()
    if algorithm_lower == 'md5':
        hash_func = hashlib.md5()
    elif algorithm_lower == 'sha1':
        hash_func = hashlib.sha1()
    elif algorithm_lower == 'sha256':
        hash_func = hashlib.sha256()
    else:
        # Unsupported algorithm: log warning and fallback to MD5
        logging.warning(f"Unsupported algorithm: {algorithm}. Falling back to MD5.")
        hash_func = hashlib.md5()

    try:
        if verbose:
            logging.info(f"Calculating {algorithm.upper()} for: {file_path}")
        # Open the file in binary read mode
        with open(file_path, "rb") as f:
            # Read the file in chunks to avoid using too much memory
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        # Get the last modified time of the file
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        # Return the file path, computed hash, and modified time
        return file_path, hash_func.hexdigest(), modified_time
    except Exception as e:
        # Log any errors that occur during hashing
        logging.error(f"Error calculating {algorithm.upper()} for {file_path}: {e}")
        return file_path, None, None


def load_file_names(csv_file_path: str) -> Set[str]:
    """Load file names from a CSV file."""
    file_names = set()
    try:
        with open(csv_file_path, mode="r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row:
                    file_names.add(row[0])
    except Exception as e:
        logging.error(f"Error reading file names from {csv_file_path}: {e}")
    return file_names


def walk_directory_and_log(
    directory: str,
    csv_file_path: str,
    algorithm: str = 'md5',
    exclude_paths: Optional[Set[str]] = None,
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    verbose: bool = False,
    limit: Optional[int] = None,
    threads: Optional[int] = None
) -> None:
    """Walk through the directory, calculate hash, and log to CSV."""
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    processed_files_count = 0

    try:
        with open(csv_file_path, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["File Name", "Hash", "Last Modified Time"])

            max_workers = threads if threads else os.cpu_count()

            if verbose and threads:
                logging.info(f"Using {threads} threads for processing.")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                count = 0
                for root, dirs, files in os.walk(directory):
                    # Exclude specified directories if provided
                    if exclude_paths:
                        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_paths]

                    for file in files:
                        file_path = os.path.join(root, file)
                        if exclude_paths and file_path in exclude_paths:
                            continue
                        if file_extension and not file.endswith(file_extension):
                            continue
                        if file_names and file not in file_names:
                            continue
                        futures.append(executor.submit(calculate_hash, file_path, algorithm, verbose))
                        count += 1
                        if limit and count >= limit:
                            break

                    if limit and count >= limit:
                        break

                for future in as_completed(futures):
                    file_path, hash_value, modified_time = future.result()
                    if hash_value:
                        csv_writer.writerow([file_path, hash_value, modified_time])
                        processed_files_count += 1

                    if verbose and file_path:
                        logging.info(f"Processed {file_path}")

    except Exception as e:
        logging.error(f"Error during directory walk or file writing: {e}")

    # If no files were successfully processed, log a warning
    if processed_files_count == 0:
        logging.warning("No files were processed. Check your filters, directory, or exclude paths.")


def main():
    # Set up the argument parser for command-line options
    parser = argparse.ArgumentParser(
        description="Generate checksums for files in a directory and save to CSV."
    )
    parser.add_argument("-s", "--scan-path", help="Path to the directory to scan. Defaults to the current directory.", default=os.getcwd())
    parser.add_argument("-o", "--output", help="Path to the output CSV file. Defaults to 'hash_report.csv' in the current directory.", default=os.path.join(os.getcwd(), "hash_report.csv"))
    parser.add_argument("-e", "--extension", help="Only files with this extension will be processed.", default=None)
    parser.add_argument(
        "-f", "--filelist", help="Path to a CSV file containing file names to search for. Only these files will be processed.", default=None
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output to show what the script is doing in real-time.")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads to use for processing (default: max CPU count).", default=None)
    parser.add_argument("--test", type=int, help="Run in test mode and process only the first N files.", default=None)
    parser.add_argument("-a", "--algorithm", help="Hashing algorithm to use (md5, sha1, sha256). Defaults to md5.", default="md5")
    parser.add_argument("--exclude", nargs='*', help="Paths to exclude from scanning.", default=[])

    # Parse the provided command-line arguments
    args = parser.parse_args()

    scan_path = args.scan_path
    output_csv_path = args.output

    if not os.path.exists(scan_path):
        logging.error(f"Error: The provided path {scan_path} does not exist.")
        return

    if not os.path.isdir(scan_path):
        logging.error(f"Error: The provided path {scan_path} is not a directory.")
        return

    file_extension = args.extension
    verbose = args.verbose
    algorithm = args.algorithm
    exclude_paths = set(args.exclude) if args.exclude else None

    file_names = None
    if args.filelist:
        if os.path.exists(args.filelist):
            file_names = load_file_names(args.filelist)
            if verbose:
                logging.info(f"Loaded {len(file_names)} file names from {args.filelist}")
            if not file_names:
                logging.warning(f"Warning: No file names loaded from {args.filelist}.")
        else:
            logging.error(f"Error: The file list {args.filelist} does not exist.")
            return

    if verbose:
        logging.info(f"Processing files in: {scan_path}")
        if file_extension:
            logging.info(f"Filtering for files with extension: {file_extension}")
        if file_names:
            logging.info(f"Filtering for specific file names from: {args.filelist}")
        logging.info(f"Writing output to: {output_csv_path}")

    walk_directory_and_log(
        directory=scan_path,
        csv_file_path=output_csv_path,
        algorithm=algorithm,
        exclude_paths=exclude_paths,
        file_extension=file_extension,
        file_names=file_names,
        verbose=verbose,
        limit=args.test,
        threads=args.threads
    )

    if verbose:
        logging.info(f"File report generated: {output_csv_path}")
    else:
        logging.info("File report generated successfully.")


if __name__ == "__main__":
    main()