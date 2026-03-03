# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub's private vulnerability reporting:

1. Go to the repository's **Security** tab (in the top navigation bar, next to Issues/Pull Requests)
1. Click "Report a vulnerability" in the left sidebar under Advisories
1. Fill out the form with details

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 24 hours
- **Initial assessment:** Within 48 hours
- **Resolution target:** Depends on severity, but as soon as possible

### What Qualifies as a Security Issue

- Injection vulnerabilities (SQL, command, template, etc.)
- Sensitive data exposure
- Authentication or authorization bypass
- Cross-site scripting (XSS) or cross-site request forgery (CSRF)
- Path traversal or directory traversal
- Credential exposure risks

### Out of Scope

- Issues in upstream dependencies (report to them directly)
- Issues requiring physical access to the machine
- Social engineering attacks

## Notes

This template contains the following placeholders for substitution:

| Placeholder                 | Replace with                |
| --------------------------- | --------------------------- |
| `PROJECT-NAME`              | Repository/project name     |
| `GITHUB-OWNER/PROJECT-NAME` | Full GitHub owner/repo path |

The "What Qualifies" section is intentionally generic. The SKILL.md workflow
may add project-specific entries (e.g., "container escape vulnerabilities" for
container tools, "credential exposure" for CLI tools that handle secrets).

This file is placed at `.github/SECURITY.md` in the target project.
