# Language-Specific Libraries for Secret Handling

Code patterns and library recommendations for each major language.

## Rust: type-system-enforced secret safety

Rust's type system makes it uniquely suited for secret handling.

### Key libraries

| Crate | Purpose |
|-------|---------|
| `secrecy` | `SecretString` / `SecretBox<T>` wrappers that print `[[REDACTED]]` on `Debug` and require `expose_secret()` to access |
| `zeroize` | Guarantees memory zeroing via `core::ptr::write_volatile` and atomic fences |
| `rpassword` | Echo-suppressed password prompts |
| `clap` | `hide_env_values(true)` prevents env var values from leaking into `--help` |

### Example

```rust
use secrecy::{SecretString, ExposeSecret};
use rpassword::prompt_password;
use clap::Parser;

#[derive(Parser, Debug)]  // Debug is safe: SecretString prints [[REDACTED]]
struct Cli {
    #[arg(long, env = "API_KEY", hide_env_values = true)]
    api_key: Option<String>,
}

fn get_api_key(cli: &Cli) -> SecretString {
    if let Some(key) = &cli.api_key {
        return SecretString::new(key.clone().into());
    }
    SecretString::new(prompt_password("Enter API key: ").unwrap().into())
}
```

### TTY detection

```rust
std::io::stdin().is_terminal()  // Rust 1.70+
```

## Go: standard library covers the basics

### Key libraries

| Package | Purpose |
|---------|---------|
| `golang.org/x/term` | `term.ReadPassword()` disables echo by manipulating terminal flags |
| `github.com/awnumar/memguard` | mlock'd memory enclaves with guard pages (note: Go GC introduces caveats) |

### Example: custom SecretString type

```go
import (
    "fmt"
    "syscall"
    "golang.org/x/term"
)

// SecretString prevents accidental logging of secret values.
type SecretString struct{ value string }

func (s SecretString) String() string  { return "[REDACTED]" }
func (s SecretString) GoString() string { return "[REDACTED]" }
func (s SecretString) Expose() string  { return s.value }

func ReadSecret(prompt string) (SecretString, error) {
    fmt.Print(prompt)
    key, err := term.ReadPassword(int(syscall.Stdin))
    if err != nil {
        return SecretString{}, err
    }
    fmt.Println()
    return SecretString{value: string(key)}, nil
}
```

### TTY detection

```go
term.IsTerminal(int(os.Stdin.Fd()))
```

### Atomic file creation with correct permissions

```go
f, err := os.OpenFile(credPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o600)
if err != nil {
    return err
}
defer f.Close()
```

## Python: rich ecosystem

### Key libraries

| Library | Purpose |
|---------|---------|
| `keyring` | Cross-platform keychain access (macOS Keychain, Windows Credential Locker, Linux Secret Service) |
| `click` | `password_option()` combines echo suppression with confirmation prompting |
| `getpass` | Standard library echo-suppressed prompts (Python 3.13 added `echo_char` for asterisks) |
| `pydantic` | `SecretStr` type that redacts on repr |

### Example: Click with keyring

```python
import keyring
import click

@click.command()
@click.option("--token", envvar="API_TOKEN",
              prompt="API Token", hide_input=True)
def login(token):
    keyring.set_password("myapp", "default", token)
    click.echo("Token stored in system keychain.")
```

### Atomic file creation

```python
import os

fd = os.open(cred_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(credentials)
```

### TTY detection

```python
sys.stdin.isatty()
```

## Node.js

### Key libraries

| Package | Purpose |
|---------|---------|
| `@inquirer/prompts` | Interactive password input with masking |
| `keytar` (deprecated) / `@anthropic/node-keytar` | Native keychain access |

### TTY detection

```javascript
process.stdin.isTTY
```

## Ruby

### Key libraries

| Library | Purpose |
|---------|---------|
| `IO::console` | Standard library: `$stdin.getpass` for echo-suppressed input |
| `tty-prompt` | Rich interactive prompts with customizable mask characters |

### TTY detection

```ruby
$stdin.tty?
```

## Cross-language TTY detection summary

| Language | TTY check |
|----------|-----------|
| Rust | `std::io::stdin().is_terminal()` (1.70+) |
| Go | `term.IsTerminal(int(os.Stdin.Fd()))` |
| Python | `sys.stdin.isatty()` |
| Node.js | `process.stdin.isTTY` |
| Ruby | `$stdin.tty?` |
