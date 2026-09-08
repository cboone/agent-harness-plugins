# cspell Config Template

Use this template for `cspell.jsonc`.

```jsonc
{
  "version": "0.2",
  "language": "en",
  "dictionaryDefinitions": [
    {
      "name": "project-words",
      "path": "./cspell-words.txt",
      "addWords": true,
    },
  ],
  "dictionaries": ["project-words"],
  "ignorePaths": [".git", ".git/", ".git/**", ".lake/**", "lake-manifest.json", "references/extractions/**", "references/transcriptions/**"],
  "ignoreRegExpList": ["/`[^`]*`/g", "/\\$[^$]*\\$/g", "/\\$\\$[\\s\\S]*?\\$\\$/g", "/\\\\\\[[\\s\\S]*?\\\\\\]/g", "/\\\\\\([\\s\\S]*?\\\\\\)/g", "/@[A-Za-z][A-Za-z0-9_:-]*/g", "/\\\\cite[a-zA-Z*]*\\{[^}]+\\}/g"],
}
```

## Notes

- The ignore patterns cover inline code, LaTeX math, Pandoc citation keys, and Lean/Lake build output.
- Add domain vocabulary and author surnames to `cspell-words.txt` as the project grows.
