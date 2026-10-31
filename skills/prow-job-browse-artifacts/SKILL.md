---
name: prow-job-browse-artifacts
description: Download, extract, and browse Prow CI job artifacts from prow.k8s.io or local directories
user-invocable: true
license: Apache-2.0
metadata:
  copyright: The Kubernetes Authors
---

## Name

prow-job-browse-artifacts:prow-job-browse-artifacts

## Synopsis

Download, decompress, and generate an interactive HTML file browser for Kubernetes Prow CI job artifacts.

## Description

Downloads artifacts from Kubernetes Prow CI jobs at [prow.k8s.io](https://prow.k8s.io) (or processes an existing local `$ARTIFACTS` directory), recursively extracts nested `.tar`, `.tar.gz`, `.tgz`, and `.gz` archives, and generates a self-contained HTML artifact browser with regex and file-type filtering.

## Implementation

Follow these steps to download, extract, and browse Prow artifacts:

1. **Determine the artifact source and skill directory**:
   - Locate `SKILL_DIR` as the directory containing this `SKILL.md` file (for example, `.agents/skills/prow-job-browse-artifacts` when installed via `npx skills`, or `skills/prow-job-browse-artifacts` in a repository checkout).
   - If given a `prow.k8s.io` or `gcsweb.k8s.io` URL, parse `BUCKET_PATH` (the path after `kubernetes-ci-logs/`), `BUILD_ID` (10+ digit identifier), and `PROWJOB_NAME`.
   - Set `WORK_DIR=".work/prow-job-browse-artifacts/$BUILD_ID"` and create `$WORK_DIR/artifacts` and `$WORK_DIR/tmp`.

2. **Download job metadata and artifacts from GCS**:
   - Use `gcloud storage cp` to fetch `prowjob.json`, `build-log.txt`, and the `artifacts/` directory from the public `gs://kubernetes-ci-logs` bucket:

     ```bash
     gcloud storage cp "gs://kubernetes-ci-logs/$BUCKET_PATH/prowjob.json" \
       "$WORK_DIR/artifacts/prowjob.json" --no-user-output-enabled
     gcloud storage cp "gs://kubernetes-ci-logs/$BUCKET_PATH/build-log.txt" \
       "$WORK_DIR/artifacts/build-log.txt" --no-user-output-enabled
     gcloud storage cp -r "gs://kubernetes-ci-logs/$BUCKET_PATH/artifacts/" \
       "$WORK_DIR/tmp/" --no-user-output-enabled
     ```

3. **Extract nested archives**:
   - Run [`scripts/extract_archives.py`](./scripts/extract_archives.py) to copy downloaded files and recursively decompress `.tar`, `.tar.gz`, `.tgz`, and `.gz` archives:

     ```bash
     python3 "$SKILL_DIR/scripts/extract_archives.py" \
       "$WORK_DIR/tmp" \
       "$WORK_DIR/artifacts"
     ```

4. **Generate the interactive HTML report**:
   - Run [`scripts/generate_html_report.py`](./scripts/generate_html_report.py) to produce `$WORK_DIR/artifacts-browser.html`:

     ```bash
     python3 "$SKILL_DIR/scripts/generate_html_report.py" \
       "$WORK_DIR/artifacts" \
       "$PROWJOB_NAME" \
       "$BUILD_ID" \
       "$GCSWEB_URL"
     ```

5. **Present the results**:
   - Report the total file count, extracted archive count, and path to `$WORK_DIR/artifacts-browser.html`.
