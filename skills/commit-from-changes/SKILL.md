---
name: commit-from-changes
description: Stage and commit changes with a Kubernetes-style commit message
user-invocable: true
license: Apache-2.0
metadata:
  copyright: The Kubernetes Authors
---

## Name

commit-from-changes:commit-from-changes

## Synopsis

Stage and commit changes with a Kubernetes-style commit message.

## Description

Generates a commit for the current changes following Kubernetes commit message conventions. Stages all changes if nothing is staged, reviews the diff, and produces a commit message with a capitalized imperative subject line under 72 characters and a body that explains the reason for the change.

## Implementation

Generate a commit for the current changes following these rules:

1. Run `git diff --cached --stat` and `git diff --stat` to understand what has changed. If nothing is staged, stage all changes with `git add -A`.
2. Run `git diff --cached` to review the full staged diff.
3. Generate a commit message in Kubernetes style:
   - Subject line: start with a capitalized imperative verb (e.g., Fix, Add, Update, Remove, Refactor)
   - Subject line should be concise (under 50 characters) and describe WHAT changed
   - If the change is scoped to a specific component or package, prefix with it (e.g., "pkg/controller: Fix race condition in queue processing")
   - Add a blank line after the subject
   - Body should explain WHY the change was made if not obvious from the subject
   - Wrap body lines at 72 characters
4. NEVER use Co-authored-by in any commit messages
5. Do not use GitHub keywords that automatically close issues (e.g., "Fixes #123", "Closes #456") or @mentions in commit messages
6. Show the generated commit message to the user and ask for approval before committing
7. Commit with the approved message using `git commit`
