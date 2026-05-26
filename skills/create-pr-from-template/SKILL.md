---
name: create-pr-from-template
description: Create a GitHub pull request from the current branch
user-invocable: true
license: Apache-2.0
metadata:
  copyright: The Kubernetes Authors
---

## Name

create-pr-from-template:create-pr-from-template

## Synopsis

Create a GitHub pull request from the current branch.

## Description

Creates a GitHub pull request from the current branch by analyzing commits, looking for PR templates, and generating a descriptive title and body.

## Implementation

1. **Check for PR templates**: Look for pull request templates in the repository at these common locations:
   - `.github/pull_request_template.md`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/` (directory with multiple templates)
   - `docs/pull_request_template.md`
   - `pull_request_template.md`

2. **Determine the base branch**: Use `main` as the default base branch. Check the repo's default branch if unsure.

3. **Generate the PR title**: Create a concise, descriptive title from the commits on the current branch that are not on the base branch.

4. **Generate the PR body**:
   - If a PR template exists in the repo, use it as the structure and fill it in based on the changes.
   - If no template exists, generate a clear PR description summarizing the changes.
   - Always include the following section at the bottom of the PR body:

     ```
     ---
     > **AI Assistance Disclosure**: This pull request was created with the assistance of AI.
     ```

5. **Create the PR**: Use `gh pr create` to create the pull request. Show the user the title and body before creating it, and ask for confirmation.
