# Agent Skills

This directory contains shared AI agent skills for OSS Kubernetes development.

## What are Agent Skills?

Agent skills are specialized instructions, guidelines, and tools that AI agents use to assist with software development and maintenance tasks. They help ensure that AI agents follow project conventions, best practices, and security guidelines.

## Installation

Install skills into your project or global agent environment using the [`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
# List available skills in this repository
npx skills add kubernetes-sigs/maintainer-tools --list

# Install a specific skill
npx skills add kubernetes-sigs/maintainer-tools --skill commit-from-changes
npx skills add kubernetes-sigs/maintainer-tools --skill create-pr-from-template
```

## Structure

Skills are organized into subdirectories, each representing a distinct skill. A skill directory typically contains:

- `SKILL.md`: The main instruction file for the skill, including YAML frontmatter with metadata (name, description).
- `references/` (optional): Supporting documentation or reference materials used by the skill.
- `scripts/` (optional): Helper scripts used by the skill.

## Available Skills

- [`commit-from-changes`](./commit-from-changes/SKILL.md): Stage and commit changes with a Kubernetes-style commit message.
- [`create-pr-from-template`](./create-pr-from-template/SKILL.md): Create a GitHub pull request from the current branch using the repository's PR template when available.

## Contributing

To contribute a new skill:

1. Create a new subdirectory under `skills/`.
2. Add a `SKILL.md` file with the required frontmatter and clear instructions.
3. Add any necessary reference files or scripts.
4. Update this README to list the new skill.
5. Run `make verify` to lint and validate installation with `npx skills`.
6. Open a Pull Request.
