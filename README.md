# md5sift

**md5sift** is a CLI tool written in Python designed to generate checksum reports for files across local directories or network shares. It offers **filtering by file extensions or predefined file lists** and produces reports in **CSV format**.

## Features

- **Bulk Checksum Generation:** Calculate hashes for multiple files in a directory.
- **File Filtering:** Filter files by extension or from a provided file list.
- **Multi-threaded Processing:** Faster checksum generation with multi-threading.
- **CSV Output:** Generate comprehensive CSV reports including file paths, MD5 hashes, and timestamps.
- **Algorithm Options:** Supports hashing algorithms (`md5`, `sha1`, `sha256`).
- **Verbose Mode:** Real-time progress updates.
- **Test Mode:** Process a subset of files for quick validation.

## Installation

md5sift can be installed and run as a Python script or via an RPM package.

### Python Installation

#### Requirements:
- Python 3.x  
- Git (optional)  

#### Setup:

**Option 1:** Clone from GitHub:
```bash
git clone https://github.com/madebyjake/md5sift.git && cd md5sift
```

**Option 2:** Download ZIP and extract.

### RPM Installation

To install via RPM package:

1. Download the RPM from the [Releases](https://github.com/madebyjake/md5sift/releases) page.
2. Install using a package manager:

```bash
sudo rpm -ivh md5sift-<ver>-1.noarch.rpm      # using RPM
sudo yum install md5sift-<ver>-1.noarch.rpm   # using YUM
sudo dnf install md5sift-<ver>-1.noarch.rpm   # using DNF
```

*Replace `<ver>` with the package version.*

To build the RPM package from source, refer to the [Building the RPM Package](#building-the-rpm-package) section.

## Usage

Depending on the chosen installation method, md5sift can be run as a Python script or via the command-line interface.

**NOTE:**
- Default scan path is the current directory if `-s`/`--scan-path` isn’t provided.
- Default output file is `hash_report.csv` in the current directory if `-o`/`--output` isn’t specified.

### Python Script Execution

Run directly using Python:

```bash
python3 md5sift.py -s <scan_directory> -o <output_file> [OPTIONS]
```

### Command-Line Interface (CLI)

After RPM installation, run:

```bash
md5sift -s <scan_directory> -o <output_file> [OPTIONS]
```

### Arguments

| Argument          | Description                                                                |
|-------------------|----------------------------------------------------------------------------|
| `-s, --scan-path` | Path to the directory to scan. Defaults to the current directory.          |
| `-o, --output`    | Path to the output CSV file. Defaults to `md5_report.csv`.                 |
| `-e, --extension` | Filter files by specific extension (e.g., `.txt`).                         |
| `-f, --filelist`  | Path to a CSV file containing specific file names to process.              |
| `-v, --verbose`   | Enable verbose mode for progress updates.                                  |
| `-t, --threads`   | Number of threads (default: CPU core count).                               |
| `--test`          | Run in test mode and process a limited number of files.                    |
| `-a, --algorithm` | Hashing algorithm (`md5`, `sha1`, `sha256`). Defaults to `md5`.            |
| `--exclude`       | Paths or directories to exclude from scanning.                             |
| `-h, --help`      | Show help message.                                                         |
| `--version`       | Show version information.                                                  |

### Examples

Below are some examples of how to use md5sift (rpm package) with different options:

**Scan a Directory and Save to CSV**
```bash
md5sift -s /path/to/scan -o /path/to/output/report.csv
```

**Filter by File Extension**
```bash
md5sift -s /path/to/scan -o /path/to/output/report.csv -e .txt
```

**Use a File List and Verbose Mode**
```bash
md5sift -s /path/to/scan -o /path/to/output/report.csv -f /path/to/filelist.csv -v
```

**Test Mode (Process First 10 Files)**
```bash
md5sift -s /path/to/scan -o /path/to/output/report.csv --test 10
```

**Use SHA-256 and Exclude Directories**
```bash
md5sift -s /path/to/scan -o /path/to/output/report.csv -a sha256 --exclude /path/to/exclude_dir
```

## Logging
- By default, `INFO` level logging is enabled.
- Use `-v` (`--verbose`) for real-time progress updates.

## Building the RPM Package

1. To build the RPM package, install the required dependencies:

```bash
sudo dnf install rpm-build python3-devel python3-setuptools
```

2. From the project root directory to generate the md5sift.spec file:

```bash
python3 setup.py genspec
```

3. Build the RPM package:

```bash
python3 setup.py bdist_rpm
```

The RPM package will be generated in the `dist/` directory.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidance.

## Support

Please open an [issue](https://github.com/madebyjake/md5sift/issues) for support or feedback.
