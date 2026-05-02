# Ruby Makefile

```makefile
.PHONY: test lint clean help

test: ## Run tests
	bundle exec rake test

lint: ## Run RuboCop
	bundle exec rubocop

clean: ## Remove build artifacts
	rm -rf tmp coverage

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
```
