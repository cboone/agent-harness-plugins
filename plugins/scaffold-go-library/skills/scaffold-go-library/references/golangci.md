# .golangci.yml Template

Use this template for `.golangci.yml`. Replace `GITHUB-USERNAME` and `PROJECT-NAME` with the actual values.

```yaml
# golangci-lint configuration for PROJECT-NAME
# https://golangci-lint.run/usage/configuration/

version: "2"

run:
  timeout: 5m

formatters:
  enable:
    - gofmt
    - goimports

  settings:
    goimports:
      local-prefixes:
        - github.com/GITHUB-USERNAME/PROJECT-NAME

linters:
  enable:
    # Quality
    - bodyclose
    - durationcheck
    - errcheck
    - gocritic
    - gocyclo
    - ineffassign
    - nilerr
    - revive
    - staticcheck
    - unused
    # Style
    - godot

  settings:
    gocyclo:
      min-complexity: 15

    godot:
      capital: false
      scope: declarations

    revive:
      rules:
        - name: blank-imports
        - name: context-as-argument
        - name: context-keys-type
        - name: dot-imports
        - name: error-naming
        - name: error-return
        - name: error-strings
        - name: exported
        - name: increment-decrement
        - name: indent-error-flow
        - name: package-comments
        - name: range
        - name: receiver-naming
        - name: time-naming
        - name: unexported-return
        - name: var-declaration
        - name: var-naming
```

## Notes

- Uses golangci-lint v2 configuration format (`version: "2"`)
- `goimports` local-prefixes ensures project imports are grouped separately
- Quality linters catch real bugs: `errcheck` (unchecked errors), `nilerr` (nil error returns), `bodyclose` (unclosed HTTP bodies), `staticcheck` (comprehensive static analysis), `unused` (dead code), `ineffassign` (ineffectual assignments)
- Style linters enforce consistency: `godot` (comment periods), `revive` (comprehensive style rules)
- `gocyclo` threshold of 15 is reasonable for library code -- lower than application code
- The revive rules list covers the most commonly accepted Go style conventions
