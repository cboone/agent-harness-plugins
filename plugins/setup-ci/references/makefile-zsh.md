# Zsh Makefile

```makefile
.PHONY: check-zsh format-zsh help

check-zsh: ## Run all zsh checks (7-tool pipeline)
	./scripts/check-zsh.zsh

format-zsh: ## Format zsh scripts
	find . -name '*.zsh' -exec shfmt -ln zsh -w {} +

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
