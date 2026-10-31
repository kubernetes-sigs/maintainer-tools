CONTAINER_ENGINE ?= $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)
SKILLSAW_IMAGE ?= ghcr.io/stbenjam/skillsaw:0.10.1
PROJECT_DIR ?= $(CURDIR)
ARTIFACTS ?= $(PROJECT_DIR)/_artifacts

.PHONY: verify
verify: verify-skills-lint verify-skills-install

.PHONY: verify-skills-lint
verify-skills-lint: ## Lint agent skills with skillsaw
	$(_skills_lint_recipe)

.PHONY: verify-skills-install
verify-skills-install: ## Verify all skills can be discovered and installed via npx skills
	$(_skills_install_recipe)

# Validates skills against https://agentskills.io/specification
define _skills_lint_recipe
mkdir -p $(ARTIFACTS)
$(CONTAINER_ENGINE) run --rm -v $(PROJECT_DIR):/workspace:Z -v $(ARTIFACTS):/out:Z $(SKILLSAW_IMAGE) --output /out/skillsaw-summary.html
endef

# Validates skills can be installed by https://www.npmjs.com/package/skills
define _skills_install_recipe
@tmpdir=$$(mktemp -d); \
trap 'rm -rf "$$tmpdir"' EXIT; \
(cd "$$tmpdir" && npx --yes skills add "$(PROJECT_DIR)" --all -y); \
for skill_md in "$(PROJECT_DIR)"/skills/*/SKILL.md; do \
	skill_name=$$(basename "$$(dirname "$$skill_md")"); \
	if [ ! -f "$$tmpdir/.agents/skills/$$skill_name/SKILL.md" ]; then \
		echo "ERROR: Skill $$skill_name was not installed by npx skills"; \
		exit 1; \
	fi; \
done
endef
