<!-- markdownlint-disable MD041 relative-links -->
<!-- This is a template file; relative links target the destination project. -->

## Description

<!-- Describe your changes -->

## Related Issue

<!-- Link to the issue this PR addresses -->

Fixes #

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Checklist

- [ ] I have read the [CONTRIBUTING](../CONTRIBUTING.md) guide
- [ ] My code follows the project's style guidelines
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass
- [ ] I have updated the documentation if needed

## Notes

This template is placed at `.github/PULL_REQUEST_TEMPLATE.md` in the target
project.

The SKILL.md workflow customizes the checklist based on detected tooling:

- If a specific test command is detected, the "tests pass" item references it
  (e.g., "All new and existing tests pass (`make test`)")
- If a CHANGELOG exists, an item is added:
  "I have updated CHANGELOG.md if this is a user-facing change"
- The CONTRIBUTING link path is adjusted if the template is in `.github/`
  (uses `../CONTRIBUTING.md`)
