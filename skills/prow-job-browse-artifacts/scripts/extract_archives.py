#!/usr/bin/env python3
"""Extract and recursively decompress Prow job artifact archives.

This script handles the extraction of archived artifacts from Kubernetes Prow CI jobs,
automatically processing nested tar.gz, tgz, and gz archives.

Compatible with: Claude Code, Gemini CLI, OpenAI Codex, GitHub Copilot CLI, Opencode

Usage:
    python3 extract_archives.py <source-directory> <output-directory>

Example:
    python3 extract_archives.py ./tmp ./artifacts
"""

import os
import sys
import tarfile
import gzip
import shutil
from pathlib import Path


def human_readable_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def extract_tar_archive(tar_path, extract_to):
    """Extract a tar archive (including .tar.gz and .tgz)."""
    try:
        print(f"  Extracting: {tar_path}")
        with tarfile.open(tar_path, 'r:*') as tar:
            tar.extractall(path=extract_to)
        return True
    except Exception as e:
        print(f"  ERROR: Failed to extract {tar_path}: {e}", file=sys.stderr)
        return False


def gunzip_file(gz_path):
    """Gunzip a .gz file (not a tar.gz)."""
    try:
        # Output file is the same name without .gz extension
        output_path = gz_path[:-3] if gz_path.endswith('.gz') else gz_path + '.decompressed'

        print(f"  Decompressing: {gz_path}")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return True, output_path
    except Exception as e:
        print(f"  ERROR: Failed to decompress {gz_path}: {e}", file=sys.stderr)
        return False, None


def process_archives(base_path):
    """Recursively find and extract archives."""
    archives_processed = 0
    errors = []

    print("\nProcessing archives...")

    # Keep processing until no more archives are found
    # (since extracting one archive might create new archives)
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        found_archives = False

        # Walk directory tree
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                file_path = os.path.join(root, filename)

                # Handle .tar, .tar.gz and .tgz files
                if filename.endswith('.tar') or filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                    parent_dir = os.path.dirname(file_path)
                    if extract_tar_archive(file_path, parent_dir):
                        os.remove(file_path)
                        archives_processed += 1
                        found_archives = True
                    else:
                        errors.append(f"Failed to extract: {file_path}")

                # Handle plain .gz files (not .tar.gz)
                elif filename.endswith('.gz') and not filename.endswith('.tar.gz'):
                    success, output_path = gunzip_file(file_path)
                    if success:
                        os.remove(file_path)
                        archives_processed += 1
                        found_archives = True
                    else:
                        errors.append(f"Failed to decompress: {file_path}")

        # If no archives were found in this iteration, we're done
        if not found_archives:
            break

    if iteration >= max_iterations:
        print(f"\nWARNING: Stopped after {max_iterations} iterations. Some nested archives may remain.", file=sys.stderr)

    return archives_processed, errors


def copy_files(source_dir, dest_dir):
    """Copy all files from source to destination."""
    files_copied = 0

    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            src_path = os.path.join(root, filename)
            rel_path = os.path.relpath(src_path, source_dir)
            dest_path = os.path.join(dest_dir, rel_path)

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            files_copied += 1

    return files_copied


def count_files_and_size(base_path):
    """Count total files and calculate total size."""
    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(base_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                total_files += 1
                total_size += os.path.getsize(file_path)
            except:
                pass

    return total_files, total_size


def main():
    if len(sys.argv) != 3:
        print("Usage: extract_archives.py <source-directory> <output-directory>")
        print("  <source-directory>: Directory containing downloaded artifacts")
        print("  <output-directory>: Directory to extract to")
        sys.exit(1)

    source_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Validate inputs
    if not os.path.exists(source_dir):
        print(f"ERROR: Source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print("Prow Artifact Extraction")
    print("=" * 80)

    # Step 1: Copy files to output directory
    print(f"\nStep 1: Copying files to output directory")
    print(f"  From: {source_dir}")
    print(f"  To: {output_dir}")

    files_copied = copy_files(source_dir, output_dir)
    print(f"  Copied {files_copied} files")

    # Step 2: Process archives in output directory
    print(f"\nStep 2: Processing archives")
    archives_processed, errors = process_archives(output_dir)

    # Final statistics
    print("\n" + "=" * 80)
    print("Extraction Complete")
    print("=" * 80)

    total_files, total_size = count_files_and_size(output_dir)

    print(f"\nStatistics:")
    print(f"  Total files: {total_files:,}")
    print(f"  Total size: {human_readable_size(total_size)}")
    print(f"  Archives processed: {archives_processed}")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    print(f"\nExtracted to: {output_dir}")
    print("")


if __name__ == '__main__':
    main()
