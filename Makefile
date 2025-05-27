# Colors for pretty output - used to make the terminal output more readable
BLUE := \033[36m  # Cyan color for highlighting commands and targets
BOLD := \033[1m   # Bold text for headers and important information
RESET := \033[0m  # Reset formatting to default

# Set the default target to help - this runs when you just type 'make'
.DEFAULT_GOAL := help

# Mark targets as phony - these don't represent actual files
.PHONY: help verify install fmt test marimo clean

##@ Development Setup

venv:  # Create a Python virtual environment using uv
	@printf "$(BLUE)Creating virtual environment...$(RESET)\n"
	@curl -LsSf https://astral.sh/uv/install.sh | sh  # Download and install uv package manager
	@uv venv --python 3.12  # Create a Python 3.12 virtual environment

install: venv ## Install all dependencies using uv
	@printf "$(BLUE)Installing dependencies...$(RESET)\n"
	@uv sync --dev --frozen --all-extras # Install dependencies from pyproject.toml with dev dependencies, using the lock file

##@ Code Quality

fmt: venv ## Run code formatting and linting
	@printf "$(BLUE)Running formatters and linters...$(RESET)\n"
	@uv pip install pre-commit  # Install pre-commit tool for managing git hooks
	@uv run pre-commit install  # Install pre-commit hooks in the git repository
	@uv run pre-commit run --all-files  # Run all pre-commit hooks on all files

##@ Testing

test: install ## Run all tests
	@printf "$(BLUE)Running tests...$(RESET)\n"
	@uv pip install pytest  # Install pytest testing framework
	@uv run pytest src/tests  # Run all tests in the src/tests directory

##@ Cleanup

clean: ## Clean generated files and directories
	@printf "$(BLUE)Cleaning project...$(RESET)\n"
	@git clean -d -X -f  # Remove all untracked files and directories that are ignored by git

##@ Marimo & Jupyter

marimo: install ## Start a Marimo server
	@printf "$(BLUE)Start Marimo server...$(RESET)\n"
	@uv pip install marimo  # Install marimo interactive notebook tool
	@uv run marimo edit book/marimo  # Start marimo server in edit mode for the book/marimo directory

##@ Help

help: ## Display this help message
	@printf "$(BOLD)Usage:$(RESET)\n"
	@printf "  make $(BLUE)<target>$(RESET)\n\n"
	@printf "$(BOLD)Targets:$(RESET)\n"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(BLUE)%-15s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BOLD)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)
