# Inspect syntax, not documentation output or command text stored as data.
def parts:
  [.Parts[]? | if .Type == "DblQuoted" then parts[] else . end];
def literal:
  [parts[] | if .Type == "Lit" or .Type == "SglQuoted" then .Value else null end]
  | if any(.[]; . == null) then null else join("") end;
def command_name: literal | if . == null then null else split("/")[-1] end;
def encoded_word:
  any(.Parts[]? | .. | objects;
    ((.Type? == "SglQuoted" or .Type? == "DblQuoted") and .Dollar? == true)
    or (.Type? == "Lit" and (.Value | contains("\\"))));
def unsupported:
  . + {Reason: ("unsupported argument form: " + (literal // "<dynamic>"))};
def option: literal | if . == null then false else startswith("-") end;
def rooted:
  parts as $p
  | (($p[0].Type == "Lit" or $p[0].Type == "SglQuoted") and ($p[0].Value | startswith("/") or startswith("./")))
    or ($p | length == 1 and .[0].Type == "CmdSubst"
      and (.[0].Stmts | length) == 1
      and (.[0].Stmts[0].Cmd.Args[0] | literal) == "fixture_path");
# Wrapper syntax is data; option scanning never dispatches on a wrapper name.
def wrapper_grammar: {
  command: {flags: [], attached: [], values: {}, short_flags: "p", separator: true, assignments: false, selector: "command", opaque: false, program_flag: null, inspect: {"-v": 0, "-V": 0}, reset: [], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 0},
  exec: {flags: [], attached: [], values: {"-a": 1}, short_flags: "cl", separator: true, assignments: false, selector: "command", opaque: false, program_flag: null, inspect: {}, reset: [], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 0},
  env: {flags: ["--ignore-environment"], attached: ["--unset"], values: {"-u": 1, "--unset": 1}, short_flags: "i", separator: true, assignments: true, selector: "command", opaque: false, program_flag: null, inspect: {}, reset: [], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 0},
  builtin: {flags: [], attached: [], values: {}, short_flags: "", separator: true, assignments: false, selector: "command", opaque: false, program_flag: null, inspect: {}, reset: [], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 0},
  nohup: {flags: [], attached: [], values: {}, short_flags: "", separator: true, assignments: false, selector: "command", opaque: false, program_flag: null, inspect: {"--help": 0, "--version": 0}, reset: [], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 0},
  time: {flags: ["-p"], attached: [], values: {}, short_flags: "", separator: true, assignments: false, selector: "command", opaque: false, program_flag: null, inspect: {}, reset: [], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 0},
  bash: {flags: ["--noprofile", "--norc", "--posix"], attached: [], values: {"-o": 1, "+o": 1, "-O": 1, "+O": 1}, short_flags: "euxc", separator: true, assignments: false, selector: "shell", opaque: true, program_flag: "c", inspect: {}, reset: [], leading: 0, modes: {}, default_mode: null, plus: true, tail_min: 0},
  sh: {flags: [], attached: [], values: {"-o": 1, "+o": 1}, short_flags: "euxc", separator: true, assignments: false, selector: "shell", opaque: true, program_flag: "c", inspect: {}, reset: [], leading: 0, modes: {}, default_mode: null, plus: true, tail_min: 0},
  trap: {flags: [], attached: [], values: {}, short_flags: "", separator: true, assignments: false, selector: "program", opaque: false, program_flag: null, inspect: {"-p": 0, "-l": 0}, reset: ["-"], leading: 0, modes: {}, default_mode: null, plus: false, tail_min: 1},
  capture_child: {flags: ["--error-stdout", "--replay-stdout"], attached: [], values: {"--stdout": 1, "--on-complete": 1, "--error-prefix": 1, "--error-stdout-prefix": 1, "--replace": 2}, short_flags: "", separator: true, assignments: false, selector: "command", opaque: false, program_flag: null, inspect: {}, reset: [], leading: 1, modes: {"--exec-log": {take: 1, selector: "command"}, "--wait-log": {take: 2, selector: "none"}}, default_mode: "--", plus: false, tail_min: 0}
};
def checked_grammar:
  wrapper_grammar as $grammar
  | ["assignments", "attached", "default_mode", "flags", "inspect", "leading", "modes", "opaque", "plus", "program_flag", "reset", "selector", "separator", "short_flags", "tail_min", "values"] as $fields
  | if ($grammar | keys) == ["bash", "builtin", "capture_child", "command", "env", "exec", "nohup", "sh", "time", "trap"] and all($grammar[]; (keys | sort) == ($fields | sort)
      and (.flags | type == "array") and (.attached | type == "array") and (.values | type == "object")
      and (.short_flags | type == "string") and (.inspect | type == "object")
      and (.separator | type == "boolean") and (.assignments | type == "boolean")
      and (all(.values[]; type == "number" and . >= 1 and . == floor))
      and (all(.inspect[]; type == "number" and . >= 0 and . == floor))
      and (.opaque | type == "boolean") and (.modes | type == "object")
      and (all(.modes[]; .take >= 1 and (.selector | IN("command", "none"))))
      and (.plus | type == "boolean") and (.reset | type == "array")
      and (.selector | IN("command", "program", "shell"))
      and (.leading | type == "number" and . >= 0 and . == floor)
      and (.tail_min | type == "number" and . >= 0 and . == floor))
    then $grammar else error("invalid wrapper grammar: missing or invalid field") end;
def plain_word:
  (.Parts | length) == 1 and .Parts[0].Type == "Lit"
  and (.Parts[0].Value | contains("\\") | not);
def assignment:
  .Parts[0].Type == "Lit" and
  (.Parts[0].Value | test("^[A-Za-z_][A-Za-z_0-9]*="));
def wrapper_error($word; $name; $reason):
  ($word // {}) + {Reason: ($name + ": unsupported argument form: " + $reason + " " + ($word | literal // "<dynamic>"))};
# A short value option consumes the cluster's remainder, or the next word.
def short_options($chars; $spec; $prefix; $state):
  if $chars == "" then $state
  else $chars[:1] as $char
    | ($prefix + $char) as $flag
    | if $spec.values[$flag] != null then
        $state + {take: (if ($chars | length) > 1 then 0 else $spec.values[$flag] end)}
      elif ($spec.short_flags | contains($char)) and
           ($prefix == "-" or ($spec.plus and $char != $spec.program_flag)) then
        short_options($chars[1:]; $spec; $prefix;
          $state + {program: ($state.program or ($prefix == "-" and $char == $spec.program_flag))})
      else $state + {bad: true} end
  end;
def scan_wrapper($args; $spec; $state):
  $state.index as $i
  | if $i >= ($args | length) or $state.mode.selector == "none" then $state
    else ($args[$i] | literal) as $value
      | if $spec.assignments and ($args[$i] | assignment) then
          scan_wrapper($args; $spec; $state + {index: ($i + 1), options: false})
        elif $spec.assignments and ($args[$i] | option | not)
          and (any($args[$i] | parts[]; (.Type == "Lit" or .Type == "SglQuoted") and (.Value | contains("=")))) then
          $state + {bad: $args[$i]}
        elif ($args[$i] | plain_word | not) then
          if $state.program and ($args[$i] | option | not) then $state
          elif $spec.selector == "shell" and ($state.options | not) then $state
          else $state + {bad: $args[$i]} end
        elif $state.options and $value == "--" and $spec.separator then
          scan_wrapper($args; $spec; $state + {index: ($i + 1), options: false,
            mode: (if $state.mode == null and $spec.default_mode == "--" then {selector: "command"} else $state.mode end)})
        elif $state.options and $spec.modes[$value] != null then
          $spec.modes[$value] as $mode
          | if $state.mode != null or $i != 1 + $spec.leading or $i + $mode.take >= ($args | length) then
              $state + {bad: $args[$i]}
            else scan_wrapper($args; $spec; $state + {index: ($i + 1 + $mode.take), mode: $mode}) end
        elif $state.mode != null and ($args[$i] | option) then $state + {bad: $args[$i]}
        elif $state.options and (($spec.flags | index($value)) != null) then
          scan_wrapper($args; $spec; $state + {index: ($i + 1)})
        elif $state.options and ($spec.values[$value // ""] != null or $spec.inspect[$value // ""] != null) then
          ($spec.values[$value] // $spec.inspect[$value]) as $take
          | if $i + $take >= ($args | length) and $take > 0 then $state + {bad: $args[$i]}
            else scan_wrapper($args; $spec; $state + {index: ($i + 1 + $take), inspect: ($state.inspect or $spec.inspect[$value] != null)}) end
        elif $state.options and $value != null and ($value | startswith("--"))
          and (any($spec.attached[]; . as $flag | $value | startswith($flag + "="))) then
          scan_wrapper($args; $spec; $state + {index: ($i + 1)})
        elif $state.options and $value != null and ($value | test("^[-+][^-+].*")) then
          short_options($value[1:]; $spec; $value[:1]; {program: $state.program, take: 0}) as $short
          | if $short.bad or $i + $short.take >= ($args | length) then $state + {bad: $args[$i]}
            else scan_wrapper($args; $spec; $state + {index: ($i + 1 + $short.take), program: $short.program}) end
        else $state end
    end;
def normalize($args; $grammar):
  ($args[0] | command_name) as $name
  | if ($args | length) == 0 then {args: [], scripts: [], errors: []}
    elif ($args[0] | encoded_word) then
      {args: [], scripts: [], errors: [wrapper_error($args[0]; "wrapper"; "unsupported encoded command:")]}
    elif $grammar[$name // ""] != null then
      $grammar[$name] as $spec
      | (if ($args[0] | plain_word) then
          scan_wrapper($args; $spec; {index: (1 + $spec.leading), options: true, program: ($spec.selector == "program"), inspect: false, mode: null})
         else {bad: $args[0], index: 1} end) as $scan
      | $args[$scan.index:] as $rest
      | if $scan.bad then {args: [], scripts: [], errors: [wrapper_error($scan.bad; $name; "unsupported spelling, option or mode:")]}
        elif $scan.mode.selector == "none" then
          if ($rest | length) == 0 then {args: [], scripts: [], errors: []}
          else {args: [], scripts: [], errors: [wrapper_error($rest[0]; $name; "leftover operand or mode:")]} end
        elif ($rest[0] | option) or (($rest[0] | literal) != null and ($rest[0] | literal | startswith("+"))) then
          {args: [], scripts: [], errors: [wrapper_error($rest[0]; $name; "unsupported inner option:")]}
        elif $spec.default_mode != null and $scan.mode == null then
          {args: [], scripts: [], errors: [wrapper_error($args[0]; $name; "missing mode separator:")]}
        elif $scan.inspect then {args: [], scripts: [], errors: []}
        elif ($rest | length) <= $spec.tail_min then
          {args: [], scripts: [], errors: [wrapper_error($args[0]; $name; "missing inner operand:")]}
        elif ($spec.reset | index($rest[0] | literal)) != null then {args: [], scripts: [], errors: []}
        elif $scan.program then
          if ($rest[0] | encoded_word) then
            {args: [], scripts: [], errors: [wrapper_error($rest[0]; $name; "unsupported encoded program:")]}
          elif ($rest[0] | literal) != null or $spec.opaque then {args: [], scripts: [$rest[0]], errors: []}
          else {args: [], scripts: [], errors: [wrapper_error($rest[0]; $name; "unsupported dynamic program:")]} end
        elif $spec.selector == "shell" then {args: [], scripts: [], errors: []}
        elif ($rest[0] | plain_word | not) or ($rest[0] | option) or ($rest[0] | assignment)
          or (($rest[0] | literal) != null and ($rest[0] | literal | startswith("+"))) then
          {args: [], scripts: [], errors: [wrapper_error($rest[0]; $name; "unsupported inner operand:")]}
        else normalize($rest; $grammar) end
    elif ($args[0] | option) then {args: [], scripts: [], errors: [($args[0] | unsupported)]}
    else {args: $args, scripts: [], errors: []} end;
def word($text; $position): {Parts: [{Type: "Lit", Value: $text}], Pos: $position};
def raw_calls:
  if type == "object" then
    if .Type? == "TimeClause" and (.Stmt == null or .Stmt.Cmd.Type == "CallExpr") then
      [word("time"; .Pos)] + (if .PosixFormat then [word("-p"; .Pos)] else [] end) + (.Stmt.Cmd.Args // []),
      (.Stmt | if . == null then empty else (.Cmd | del(.Type) | raw_calls), (del(.Cmd) | raw_calls) end)
    else (if .Type? == "CallExpr" and (.Args | length) > 0 then .Args else empty end),
      (.[] | raw_calls) end
  elif type == "array" then .[] | raw_calls else empty end;
def shell_quote: "'" + gsub("'"; "'\\''") + "'";
def render_wrapper($name; $spec; $variant; $inner):
  ([range(0; $spec.leading) | "sample"] | join(" ")) as $leading
  | (if $spec.selector == "shell" then ["-" + $spec.program_flag] else [] end) as $base
  | (if $variant == "combined" then
       ($spec.short_flags | gsub($spec.program_flag // "^$"; "")) as $chars
       | if $chars == "" then ["--unsupported-combined"]
         else ["-" + $chars[:1] + (if $spec.program_flag != null then $spec.program_flag else $chars[:1] end)] end
     elif $variant == "unknown" then ["--unsupported-wrapper-option"]
     elif $variant == "expanded-option" then ["\"${wrapper_option}\""] + $base
     elif $variant == "quoted-option" then $base + ["'--'"]
     else $base end) as $flags
  | ($flags + (if ["separator", "assignment-separator", "leftover"] | index($variant) then ["--"]
        elif $spec.default_mode != null and (["missing", "unknown", "combined", "expanded-option", "quoted-option"] | index($variant) | not) then [$spec.default_mode]
        else [] end)
     + (if $variant == "assignment" or $variant == "assignment-separator" then ["SAMPLE=value"]
        elif $variant == "assignment-quoted-value" then ["SAMPLE='value'"]
        elif $variant == "assignment-expanded-value" then ["SAMPLE=\"${value}\""]
        elif $variant == "assignment-encoded-value" then ["SAMPLE=$'value\\n'"] else [] end)
     + (if $variant == "leftover" then ["--"] else [] end)) as $prefix
  | (if $variant == "quoted-wrapper" then ($name | shell_quote)
     elif $variant == "mixed-wrapper" then ($name[:1] | shell_quote) + $name[1:]
     elif $variant == "escaped-wrapper" then "\\" + $name else $name end) + " " +
    (if $leading == "" then "" else $leading + " " end) +
    ($prefix | if length == 0 then "" else join(" ") + " " end) +
    (if $variant == "missing" then ""
     elif $spec.selector == "command" then $inner
     else ($inner | shell_quote) + (if $spec.tail_min > 0 then " EXIT" else "" end) end);
def wrapper_matrix($grammar):
  [ $grammar | to_entries[] as $entry
    | ["plain", "separator", "combined", "nested", "unknown", "missing", "leftover",
       "quoted-wrapper", "mixed-wrapper", "escaped-wrapper", "quoted-option", "expanded-option",
       "quoted-assignment", "quoted-assignment-name", "invalid-assignment-name", "encoded-command", "encoded-program", "double-mode", "repeated-mode", "reordered-mode"] +
      (if $entry.value.assignments then ["assignment", "assignment-separator", "assignment-quoted-value", "assignment-expanded-value", "assignment-encoded-value"] else [] end) | .[] as $variant
    | [true, false][] as $protected
    | (if $protected then "rm -- \"${path}\"" else "rm \"${path}\"" end) as $inner
    | (if $variant == "nested" then "env -- SAMPLE=value command -p " + $inner
       elif $variant == "quoted-assignment" then "env -- 'SAMPLE=value' " + $inner
       elif $variant == "quoted-assignment-name" then "env -- \"SAMPLE\"=value " + $inner
       elif $variant == "invalid-assignment-name" then "env -- SAMPLE-NAME=value " + $inner
       elif $variant == "encoded-command" then "$'r\\155' " + (if $protected then "-- " else "" end) + "\"${path}\""
       elif $variant == "encoded-program" then "bash -c $'printf x\\n" + $inner + "'"
       elif $variant == "double-mode" then "capture_child - --wait-log first 123 --exec-log second -- " + $inner
       elif $variant == "repeated-mode" then "capture_child - --exec-log first --exec-log second -- " + $inner
       elif $variant == "reordered-mode" then "capture_child - --stdout first --exec-log second -- " + $inner
       else $inner end) as $nested
    | {label: ($entry.key + ":" + $variant + ":" + ($protected | tostring)),
       expected: (if ["unknown", "missing", "leftover", "quoted-wrapper", "mixed-wrapper", "escaped-wrapper", "quoted-option", "expanded-option",
                      "quoted-assignment", "quoted-assignment-name", "invalid-assignment-name", "encoded-command", "encoded-program", "double-mode", "repeated-mode", "reordered-mode"] | index($variant) then "unsupported"
         elif $variant == "combined" and $entry.value.short_flags == "" then "unsupported"
         elif $protected then "pass" else "operand" end),
       program: render_wrapper($entry.key; $entry.value; $variant; $nested)} ] as $cases
  | $cases + [$cases[] | select(.label | test("^command:encoded-(command|program):"))
    | .label |= sub("^command:"; "direct:") | .program |= sub("^command "; "")];
def first_path($args; $index; $flags):
  if $index >= ($args | length) then $index
  elif ($flags | index($args[$index] | literal)) != null then
    first_path($args; $index + 1; $flags)
  else $index end;
def path_errors($args; $index; $flags):
  first_path($args; $index; $flags) as $start
  | if $start >= ($args | length) or ($args[$start] | literal) == "--" then []
    else [$args[$start:][] | select(rooted | not)] end;
# Only listed flags and flag values may precede positional arguments.
def options($args; $index; $flags; $values):
  if $index >= ($args | length) then {index: $index, errors: []}
  else ($args[$index] | literal) as $value
    | if ($flags | index($value)) != null then options($args; $index + 1; $flags; $values)
      elif ($values | index($value)) != null then
        if $index + 1 >= ($args | length) then {index: $index, errors: [($args[$index] | unsupported)]}
        else options($args; $index + 2; $flags; $values) end
      elif $value != "--" and ($args[$index] | option) then
        {index: $index, errors: [($args[$index] | unsupported)]}
      else {index: $index, errors: []} end
  end;
def metadata($args; $minimum; $maximum):
  if ($args | length) < $minimum or ($args | length) > $maximum then
    [($args[0] // {} | unsupported)]
  else [$args[] | select(option) | unsupported] end;
def prefix($args; $index):
  if $index >= ($args | length) then {index: $index, errors: []}
  else ($args[$index] | literal) as $value
    | if ["-C", "--git-dir", "--work-tree"] | index($value) then
        prefix($args; $index + 2)
        | .errors += [$args[$index + 1] | select(rooted | not)]
      elif $value == "-c" then prefix($args; $index + 2)
      elif ["--no-pager", "--literal-pathspecs"] | index($value) then prefix($args; $index + 1)
      else {index: $index, errors: []} end
  end;
def checkout_errors($args):
  options($args; 0; ["-q", "--quiet"]; ["-b", "-B", "--orphan"]) as $scan
  | $args[$scan.index:] as $rest
  | $scan.errors +
    (if ($rest | length) == 0 then
       if any($args[]; literal | IN("-b", "-B", "--orphan")) then []
       else [($args[0] // {} | unsupported)] end
     elif ($rest | length) == 1 then metadata($rest; 1; 1)
     elif ($rest[1] | literal) == "--" then metadata($rest[:1]; 1; 1)
     else [($rest[0] | unsupported)] end);
def git_errors($args):
  prefix($args; 1) as $prefix
  | $prefix.index as $index
  | ($args[$index] | literal) as $command
  | $args[$index + 1:] as $rest
  | $prefix.errors +
    (if $command == "submodule" then
       if ["add", "deinit", "update"] | index($rest[0] | literal) then
         path_errors($rest; 1; ["-q", "--quiet", "-f", "--init", "--recursive"])
       else [($rest[0] | unsupported)] end
     elif ["add", "rm", "mv", "init", "clone", "restore", "reset"] | index($command) then
       path_errors($rest; 0;
         ["-q", "--quiet", "-A", "--all", "-N", "--intent-to-add", "-u", "--update",
          "-r", "-rf", "-f", "--cached", "--bare", "--shared", "--template="])
     elif $command == "checkout" then checkout_errors($rest)
     elif $command == "commit" then
       options($rest; 0; ["-q", "--quiet", "-a", "--all", "--allow-empty"];
         ["-m", "-qm", "-qam", "-am", "--message"]) as $scan
       | $scan.errors + path_errors($rest; $scan.index; [])
     elif $command == "ls-files" then
       path_errors($rest; 0; ["--stage", "-s", "-z", "--cached", "--others", "--exclude-standard", "--error-unmatch"])
     elif $command == "status" then
       path_errors($rest; 0; ["--porcelain=v1", "--untracked-files=all", "--short", "-z"])
     elif $command == "diff" then
       options($rest; 0; ["--cached", "--no-ext-diff", "--no-textconv", "--no-color", "--name-only", "--quiet"]; []) as $scan
       | $rest[$scan.index:] as $revisions
       | ([$revisions | to_entries[] | select((.value | literal) == "--") | .key][0]) as $separator
       | $scan.errors +
         (if ($revisions | length) == 0 then []
          elif $separator != null then metadata($revisions[:$separator]; 0; 2)
          else [($revisions[0] | unsupported)] end)
     elif $command == "hash-object" then
       if any($rest[]; literal == "--stdin") then
         options($rest; 0; ["-w", "--stdin"]; []) as $scan
         | $scan.errors + metadata($rest[$scan.index:]; 0; 0)
       else path_errors($rest; 0; ["-w"]) end
     elif $command == "config" then
       options($rest; 0; ["--bool", "--get"]; []) as $scan
       | $scan.errors + metadata($rest[$scan.index:]; 1; 2)
     elif $command == "rev-parse" then
       options($rest; 0; ["--verify", "--absolute-git-dir", "--is-inside-work-tree"]; []) as $scan
       | $scan.errors + metadata($rest[$scan.index:]; 0; 1)
     elif $command == "cat-file" then
       if ["blob", "tree", "commit", "-e", "-t", "-p"] | index($rest[0] | literal) then
         metadata($rest[1:]; 1; 1)
       else [($rest[0] | unsupported)] end
     elif $command == "update-index" then
       if ($rest | length) == 2 and ($rest[0] | literal) == "--cacheinfo" then []
       else [($rest[0] // $args[$index] | unsupported)] end
     elif $command == "update-ref" or $command == "symbolic-ref" then metadata($rest; 2; 2)
     elif $command == "remote" and ($rest[0] | literal) == "add" then metadata($rest[1:]; 2; 2)
     elif $command == null and ($args | length) == $index + 1
          and ($args[$index] | parts | length == 1 and .[0].Type == "ParamExp"
            and .[0].Param.Value == "@") then []
     else [($args[$index] | unsupported)] end);
checked_grammar as $grammar
| if ($ARGS.named.mode // "check") == "grammar" then $grammar
  elif ($ARGS.named.mode // "check") == "matrix" then wrapper_matrix($grammar)
  else [raw_calls | normalize(.; $grammar)] as $calls
  | {
      errors: [$calls[] as $call
        | $call.args as $args
        | ($args[0] | command_name) as $command
        | ($call.errors +
           (if ["ln", "cp", "mv", "mkdir", "rm", "touch"] | index($command) then
              first_path($args; 1; ["-s", "-sf", "-p", "-r", "-R", "-rf", "-f"]) as $start
              | if $start == ($args | length) then [$args[-1]] else path_errors($args; $start; []) end
            elif $command == "git" then git_errors($args) else [] end))[]
        | {line: (.Pos.Line // 1), command: ($command // "wrapper"), reason: (.Reason // "needs a rooted operand or --")}],
      scripts: [$calls[].scripts[] | literal | select(. != null)]
    } end
