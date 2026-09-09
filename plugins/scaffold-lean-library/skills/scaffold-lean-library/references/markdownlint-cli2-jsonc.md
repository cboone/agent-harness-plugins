# markdownlint-cli2 Config Template

Use this template for `.markdownlint-cli2.jsonc`.

```jsonc
{
  "config": {
    "default": true,
    "MD013": false,
    "MD024": {
      "siblings_only": true
    },
    "MD033": {
      "allowed_elements": ["br", "details", "summary", "sub", "sup"]
    },
    "MD046": {
      "style": "fenced"
    }
  },
  "ignores": [
    ".lake/**",
    "references/extractions/**",
    "references/transcriptions/**"
  ]
}
```

## Notes

- `MD013` is disabled because Lean and math prose in this project family do not enforce a hard line length.
- The reference-material ignores are harmless when paper-backed mode is disabled.
