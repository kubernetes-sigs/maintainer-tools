CONTAINER_ENGINE ?= $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)
SKILLSAW_IMAGE ?= ghcr.io/stbenjam/skillsaw:0.10.1
PROJECT_DIR ?= $(CURDIR)
ARTIFACTS ?= $(PROJECT_DIR)/_artifacts

.PHONY: verify
verify: verify-skills-lint

.PHONY: verify-skills-lint
verify-skills-lint: ## Lint agent skills with skillsaw
	$(_skills_lint_recipe)

# Validates skills against https://agentskills.io/specification
define _skills_lint_recipe
mkdir -p $(ARTIFACTS)
$(CONTAINER_ENGINE) run --rm -v $(PROJECT_DIR):/workspace:Z -v $(ARTIFACTS):/out:Z $(SKILLSAW_IMAGE) --output /out/skillsaw-summary.html
endef
