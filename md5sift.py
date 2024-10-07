
import os
import hashlib
import csv
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_md5(file_path: str, verbose: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
    """Calculate the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        if verbose:
            logging.info(f"Calculating MD5 for: {file_path}")
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return file_path, hash_md5.hexdigest(), datetime.fromtimestamp(os.path.getmtime(file_path)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except Exception as e:
        logging.error(f"Error calculating MD5 for {file_path}: {e}")
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
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    verbose: bool = False,
    limit: Optional[int] = None
) -> None:
    """Walk through the directory, calculate MD5 hash, and log to CSV."""
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    try:
        with open(csv_file_path, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["File Name", "MD5 Hash", "Last Modified Time"])

            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = []
                count = 0
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file_extension and not file.endswith(file_extension):
                            continue
                        if file_names and file not in file_names:
                            continue
                        file_path = os.path.join(root, file)
                        futures.append(executor.submit(calculate_md5, file_path, verbose))
                        count += 1
                        if limit and count >= limit:
                            break

                    if limit and count >= limit:
                        break

                for future in as_completed(futures):
                    file_path, md5_hash, modified_time = future.result()
                    if md5_hash:
                        csv_writer.writerow([file_path, md5_hash, modified_time])

                    if verbose:
                        logging.info(f"Processed {file_path}")

    except Exception as e:
        logging.error(f"Error during directory walk or file writing: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate MD5 checksums for files in a directory and save to CSV."
    )
    parser.add_argument("-s", "--scan-path", help="Path to the directory to scan. Defaults to the current directory.", default=os.getcwd())
    parser.add_argument("-o", "--output", help="Path to the output CSV file. Defaults to 'md5_report.csv' in the current directory.", default=os.path.join(os.getcwd(), "md5_report.csv"))
    parser.add_argument("-e", "--extension", help="Only files with this extension will be processed.", default=None)
    parser.add_argument(
        "-f", "--filelist", help="Path to a CSV file containing file names to search for. Only these files will be processed.", default=None
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output to show what the script is doing in real-time.")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads to use for processing (default: max CPU count).", default=None)
    parser.add_argument("--test", type=int, help="Run in test mode and process only the first N files.", default=None)

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

    walk_directory_and_log(scan_path, output_csv_path, file_extension, file_names, verbose, limit=args.test)

    if verbose:
        logging.info(f"File report generated: {output_csv_path}")
    else:
        logging.info("File report generated successfully.")


if __name__ == "__main__":
    main()
