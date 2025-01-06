#!/usr/bin/env python3

import os
import hashlib
import csv
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Set, Tuple

import click

# Configure logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_hash(file_path: str, algorithm: str, verbose: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
    """Calculate the hash of a file using the specified algorithm."""
    algorithm_lower = algorithm.lower()
    if algorithm_lower == 'md5':
        hash_func = hashlib.md5()
    elif algorithm_lower == 'sha1':
        hash_func = hashlib.sha1()
    elif algorithm_lower == 'sha256':
        hash_func = hashlib.sha256()
    else:
        logging.warning(f"Unsupported algorithm: {algorithm}. Falling back to MD5.")
        hash_func = hashlib.md5()

    try:
        if verbose:
            logging.info(f"Calculating {algorithm.upper()} for: {file_path}")
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        return file_path, hash_func.hexdigest(), modified_time
    except Exception as e:
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

    if processed_files_count == 0:
        logging.warning("No files were processed. Check your filters, directory, or exclude paths.")


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option(
    '-s', '--scan-path',
    default=os.getcwd(),
    help="Path to the directory to scan. Defaults to the current directory."
)
@click.option(
    '-o', '--output',
    default=os.path.join(os.getcwd(), "hash_report.csv"),
    help="Path to the output CSV file. Defaults to 'hash_report.csv' in the current directory."
)
@click.option(
    '-e', '--extension',
    default=None,
    help="Only files with this extension will be processed."
)
@click.option(
    '-f', '--filelist',
    default=None,
    help="Path to a CSV file containing file names to search for. Only these files will be processed."
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    default=False,
    help="Enable verbose output to show what the script is doing in real-time."
)
@click.option(
    '-t', '--threads',
    type=int,
    default=None,
    help="Number of threads to use for processing (default: max CPU count)."
)
@click.option(
    '--test',
    type=int,
    default=None,
    help="Run in test mode and process only the first N files."
)
@click.option(
    '-a', '--algorithm',
    default='md5',
    help="Hashing algorithm to use (md5, sha1, sha256). Defaults to md5."
)
@click.option(
    '--exclude',
    multiple=True,
    default=[],
    help="Paths to exclude from scanning (can be specified multiple times)."
)
def main(scan_path, output, extension, filelist, verbose, threads, test, algorithm, exclude):
    """
    Generate checksums for files in a directory and save to CSV
    using the specified hashing algorithm.
    """
    if not os.path.exists(scan_path):
        logging.error(f"Error: The provided path {scan_path} does not exist.")
        return

    if not os.path.isdir(scan_path):
        logging.error(f"Error: The provided path {scan_path} is not a directory.")
        return

    exclude_paths = set(exclude) if exclude else None

    file_names = None
    if filelist:
        if os.path.exists(filelist):
            file_names = load_file_names(filelist)
            if verbose:
                logging.info(f"Loaded {len(file_names)} file names from {filelist}")
            if not file_names:
                logging.warning(f"Warning: No file names loaded from {filelist}.")
        else:
            logging.error(f"Error: The file list {filelist} does not exist.")
            return

    if verbose:
        logging.info(f"Processing files in: {scan_path}")
        if extension:
            logging.info(f"Filtering for files with extension: {extension}")
        if file_names:
            logging.info(f"Filtering for specific file names from: {filelist}")
        logging.info(f"Writing output to: {output}")

    walk_directory_and_log(
        directory=scan_path,
        csv_file_path=output,
        algorithm=algorithm,
        exclude_paths=exclude_paths,
        file_extension=extension,
        file_names=file_names,
        verbose=verbose,
        limit=test,
        threads=threads
    )

    if verbose:
        logging.info(f"File report generated: {output}")
    else:
        logging.info("File report generated successfully.")


if __name__ == "__main__":
    main()
