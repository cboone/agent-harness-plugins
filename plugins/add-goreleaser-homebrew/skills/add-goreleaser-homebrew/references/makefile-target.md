# Makefile release-dry-run Target

Add this target to an existing Makefile so developers can test the GoReleaser configuration locally without publishing.

```makefile
release-dry-run: ## Run GoReleaser in dry-run mode (no publish)
	goreleaser release --snapshot --clean
```

## How to Merge into an Existing Makefile

1. **Add to `.PHONY`**: Find the existing `.PHONY` line and append `release-dry-run`. For example:

   ```makefile
   .PHONY: build test lint vet fmt clean cover tidy help release-dry-run
   ```

1. **Append the target**: Add the `release-dry-run` target block at the end of the file, before the `help` target if one exists (so it appears in `make help` output).

1. **Verify the tab character**: The command line under `release-dry-run:` must use a literal tab, not spaces.

## Notes

- `--snapshot` builds the release artifacts locally without creating a GitHub release or publishing to Homebrew
- `--clean` removes any previous snapshot artifacts before building
- The `## ...` comment after the target name is a self-documenting Makefile convention that makes the target appear in `make help` output (when the Makefile includes a help target that greps for `##`)
- This target is optional; only add it if the project has a Makefile
