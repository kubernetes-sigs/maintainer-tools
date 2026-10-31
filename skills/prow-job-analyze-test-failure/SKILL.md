---
name: prow-job-analyze-test-failure
description: Analyze failed Prow CI tests from local ARTIFACTS directories or prow.k8s.io URLs
user-invocable: true
license: Apache-2.0
metadata:
  copyright: The Kubernetes Authors
---

## Name

prow-job-analyze-test-failure:prow-job-analyze-test-failure

## Synopsis

Analyze failed tests from Kubernetes Prow CI jobs using either a local `$ARTIFACTS` directory inside a Prow pod or a remote job URL from `prow.k8s.io` or `gcsweb.k8s.io`.

## Description

Diagnoses test failures from Kubernetes Prow CI runs by inspecting JUnit XML files, `build-log.txt`, and cluster dump logs (`cluster-info/`). Supports two execution modes:
1. **Local Artifact Mode**: Operates directly on a local `$ARTIFACTS` directory during post-failure CI triage without making live cluster API calls.
2. **Remote URL Mode**: Downloads job metadata, build logs, and JUnit XML artifacts from the public `kubernetes-ci-logs` GCS bucket.

## Implementation

Follow these steps to analyze the failure:

1. **Determine the input source**:
   - If a local directory path or `$ARTIFACTS` environment variable is provided, use **Local Artifact Mode** (Step 2).
   - If a `prow.k8s.io` or `gcsweb.k8s.io` URL is provided, use **Remote URL Mode** (Step 3).

2. **Local Artifact Mode (in-pod CI triage)**:
   - Treat the live Kubernetes cluster as unreachable and inspect only files under `$ARTIFACTS`.
   - Locate all `junit*.xml` files under `$ARTIFACTS` and extract `<testcase>` blocks containing `<failure>` elements.
   - Inspect `$ARTIFACTS/build-log.txt` (if present) and component logs under `$ARTIFACTS/cluster-info/` or `$ARTIFACTS/*.log` for fatal errors, panics, timeouts, and stack traces matching the failed test cases.
   - Write the root-cause report to `$ARTIFACTS/agy-triage-report.md` and a single-suite JUnit summary to `$ARTIFACTS/junit_agy_triage.xml` so Spyglass renders the triage output.

3. **Remote URL Mode (remote Prow job analysis)**:
   - Parse the job URL to extract `BUCKET_PATH` (the path segment after `kubernetes-ci-logs/`), `BUILD_ID` (the 10+ digit build identifier), and `PROWJOB_NAME`.
   - Create a local working directory and download `prowjob.json`, `build-log.txt`, and `junit*.xml` files using `curl`:

     ```bash
     WORK_DIR=".work/prow-job-analyze-test-failure/$BUILD_ID/artifacts"
     mkdir -p "$WORK_DIR"
     curl -sS -o "$WORK_DIR/prowjob.json" \
       "https://storage.googleapis.com/kubernetes-ci-logs/$BUCKET_PATH/prowjob.json"
     curl -sS -o "$WORK_DIR/build-log.txt" \
       "https://storage.googleapis.com/kubernetes-ci-logs/$BUCKET_PATH/build-log.txt"
     curl -sS "https://storage.googleapis.com/storage/v1/b/kubernetes-ci-logs/o?prefix=$BUCKET_PATH/artifacts/junit&delimiter=/" \
       | grep -oE '"name": "[^"]+junit[^"]*\.xml"' \
       | cut -d'"' -f4 \
       | while read -r file; do
           filename=$(basename "$file")
           curl -sS -o "$WORK_DIR/$filename" \
             "https://storage.googleapis.com/kubernetes-ci-logs/$file"
         done
     ```

4. **Correlate failure evidence**:
   - Search `build-log.txt` and extracted logs for the failed test names.
   - Extract exact error messages, Go stack traces, and timestamps around the failure window.
   - Correlate control-plane, node, or infrastructure errors with the JUnit failure output.

5. **Produce the structured analysis report**:
   - Summarize the job name (`$PROWJOB_NAME` or `$JOB_NAME`), build identifier (`$BUILD_ID`), and failed test names.
   - Include the exact error message and stack trace from JUnit XML.
   - Provide timestamped log excerpts from `build-log.txt` or `cluster-info/` as evidence.
   - State a concrete root-cause classification (infrastructure provisioning, control-plane readiness, network/CNI, or test flake) and remediation steps.
