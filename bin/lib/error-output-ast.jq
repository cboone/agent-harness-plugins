# Classify parsed redirects; quoted literal text is inventoried, never reparsed.
def ast_value:
  type == "array" or (type == "object" and (keys != ["Col","Line","Offset"]));
def ast_nodes:
  recurse(if type == "object" or type == "array" then .[] | select(ast_value) else empty end);
def fd_number:
  if test("^[0-9]+$") then sub("^0+";"") | if . == "" then "0" else . end else . end;
def continued_comments:
  ast_nodes | objects | select(has("Hash") and has("Text") and (.Text | contains("\n")));
def plain:
  if .Type == "Lit" then if .Value | contains("\\") then null else .Value end
  elif .Type == "SglQuoted" then if .Dollar? then null else .Value end
  elif .Type == "DblQuoted" then
    if all((.Parts // [])[]; .Type == "Lit" and (.Value | contains("\\") | not))
    then [(.Parts // [])[].Value] | join("") else null end
  else null end;
def word:
  [(.Parts // [])[] | plain] as $parts
  | if all($parts[]; . != null) then $parts | join("") else null end;
def descriptor:
  (.N.Value // (if .Op | startswith("<") then "0" else "1" end)) | fd_number;
def literal_only:
  all((.Parts // [])[];
    .Type == "Lit" or .Type == "SglQuoted" or
    (.Type == "DblQuoted" and all((.Parts // [])[]; .Type == "Lit")));
def strip_options:
  if length > 0 and (.[0] | word) != null and (.[0] | word | startswith("-"))
  then .[1:] | strip_options else . end;
def exec_form:
  if length == 0 then null
  else (.[0] | word) as $name
    | if $name == "command" and (.[1] | word | IN("-v", "-V")) then null
      elif $name | IN("command", "builtin") then .[1:] | strip_options | exec_form
      elif $name == "exec" then "exec redirection"
      elif $name == null and (.[0] | literal_only) then "escaped or quoted exec"
      else null end
  end;
def changes_shell_stdout:
  ast_nodes | objects
  | select(.Cmd.Type? == "CallExpr" and ((.Cmd.Args // []) | exec_form) != null)
  | select(any((.Redirs // [])[]; descriptor == "1"));
def rare_stream_context:
  if .Cmd.Type? == "CoprocClause" then "coproc"
  elif .Cmd.Type? == "CallExpr" and ((.Redirs // []) | length > 0)
  then (.Cmd.Args // []) | exec_form
  else null end
  | select(. != null) as $construct
  | $construct;
def marker:
  . as $comment
  | .Text | capture("^[\\t ]*error-output-allow:[\\t ]*(?<reason>\\S.*)$")
  | [$comment.Hash.Line, .reason];
def call($name; $id):
  .Cmd.Type == "CallExpr" and ([.Cmd.Args[] | word] == [$name, ($id | tostring)]);
def redirected($inherited; $scope; $scrut):
  reduce (.Redirs // [])[] as $r (
    {fds: $inherited, found: []};
    ($r.Word | word) as $target
    | ($r.Op) as $op
    | ($r | descriptor) as $fd
    | (($op | IN("&>", "&>>")) or
       ($op == ">&" and $fd == "1" and
        ($target == null or ($target != "-" and ($target | test("^[0-9]+-?$") | not))))) as $both
    | (($target // "") | rtrimstr("-") | fd_number) as $from
    | (if $op | IN(">&", "<&") then
         if $target == "-" then "closed"
         elif $target != null and ($target | test("^[0-9]+-?$"))
         then .fds[$from] // "unknown"
         elif $target == "/dev/null" then "null" else "file" end
       elif $target == "/dev/null" then "null"
       elif $op | IN("<", "<<", "<<-", "<<<") then "input"
       else "file" end) as $dest
    | (($op | IN(">&", "<&")) and ($target // "" | test("^[0-9]+-$"))) as $move
    | (($op | IN(">&", "<&")) and
         (($move and $from == "2") or $target == null or
          ($target == "-" and ($fd | test("^[0-9]+$") | not)))) as $closes
    | (if $both then .fds["1"] = $dest | .fds["2"] = $dest
       else .fds[$fd] = $dest end)
    | (if $move then .fds[$from] = "closed" else . end)
    | ($scrut and $dest == "stdout") as $live_forward
    | if ($both or $fd == "2" or $closes) and ($dest != "stderr" or $closes)
         and ($include_scope or $closes or ($live_forward | not)) then
        .found += [{
          kind: (if $closes then "discard"
                 elif $live_forward then "live-forward"
                 elif $dest | IN("null", "closed", "input") then "discard" else "capture" end),
          line: $r.Pos.Line, end_line: $r.End.Line,
          column: $r.Pos.Col, end_column: $r.End.Col,
          operator: $op, descriptor: $fd,
          allowed_lines: ($scope + [$r.Pos.Line, $r.OpPos.Line, $r.End.Line] | unique)
        }]
      else . end
  );
def redirects($ends; $inherited; $scrut):
  if type == "array" then .[] | redirects($ends; $inherited; $scrut)
  elif type == "object" then
    . as $node
    | (if (.Type? // "") | IN("CmdSubst", "ProcSubst", "FuncDecl", "CoprocClause")
       then {"0":"stdin", "1":"capture", "2":"stderr"} else $inherited end) as $initial
    | (if (.Cmd.Type? // "") | IN("CallExpr", "BinaryCmd", "CoprocClause")
       then $ends + [.End.Line] else $ends end) as $scope
    | redirected($initial; $scope; $scrut) as $state
    | (if .Type? == "BinaryCmd" and .Op == "|&" then
         {kind:"capture", line:.OpPos.Line, end_line:.OpPos.Line,
          column:.OpPos.Col, end_column:(.OpPos.Col + 2), operator:"|&", descriptor:"2",
          allowed_lines:($scope + [.OpPos.Line,.X.End.Line] | unique)}
       else empty end),
      ($node | rare_stream_context | . as $construct
       | {kind:"stream-context", construct:$construct,
          line:$node.Pos.Line, end_line:$node.End.Line,
          column:$node.Pos.Col, end_column:$node.End.Col,
          operator:$construct, descriptor:"context",
          allowed_lines:($scope+[$node.Pos.Line,$node.End.Line]|unique)}),
      $state.found[],
      ($node | to_entries[] | select(.key != "Comments" and (.value | ast_value)) | . as $entry
       | .value | redirects($scope;
          (if $node.Type? == "BinaryCmd" and ($node.Op | IN("|", "|&")) and $entry.key == "X"
           then $state.fds + {"1":"capture"} else $state.fds end);
          $scrut))
  else empty end;

(($ast | length == 1) and ($units | length == 1)) as $shape
| if ($shape | not) then error("invalid AST input count") else . end
| $ast[0] as $tree
| $units[0] as $u
| if ($tree.Type != "File" or ($tree.Stmts | length) != (3 * ($u | length)))
  then error("AST unit boundaries changed") else . end
| if all(range(0; $u | length); . as $i |
    ($tree.Stmts[3 * $i] | call("__error_output_begin"; $i))
    and ($tree.Stmts[3 * $i + 2] | call("__error_output_end"; $i))
    and $tree.Stmts[3 * $i + 1].Cmd.Type == "Subshell"
    and $tree.Stmts[3 * $i + 1].Cmd.Lparen.Line == $u[$i].open
    and $tree.Stmts[3 * $i + 1].Cmd.Rparen.Line == $u[$i].close)
  then . else error("AST unit boundaries changed") end
| [range(0; $u | length) | . as $i
   | $u[$i] as $unit
   | $tree.Stmts[3 * $i + 1].Cmd as $body
   | [$body | ast_nodes | objects | select(has("Hash") and has("Text")) | marker] as $markers
   | [$body | continued_comments] as $continued
   | ($unit.stream == "stdout" and ([$body | changes_shell_stdout] | length == 0)) as $live_scrut
   | {
       name: $unit.name, file: $unit.file,
       errors: (if ($continued | length) > 0 then
         [{kind:"parse", line:($continued[0].Hash.Line - $unit.body + $unit.origin)}]
         else [$body | redirects([]; {"0":"stdin", "1":"stdout", "2":"stderr"}; $live_scrut) | . as $r
         | select(any($markers[]; .[0] as $line | $r.allowed_lines | index($line)) | not)
         | {kind, construct:(.construct // null), line: (.line - $unit.body + $unit.origin),
            end_line: (.end_line - $unit.body + $unit.origin),
            column, end_column, operator, descriptor,
            allowed_lines: [.allowed_lines[] | . - $unit.body + $unit.origin]}] end),
       strings: (if $include_scope then [
         $body | ast_nodes | objects
         | select(has("Parts") and ((.Type? // "Word") == "Word"))
         | select(.Pos.Line >= $unit.body)
         | {name: $unit.name,
            start_line: (.Pos.Line - $unit.body + $unit.origin),
            end_line: (.End.Line - $unit.body + $unit.origin),
            start_column: .Pos.Col, end_column: .End.Col,
            reason: "Operand text is not reparsed as a shell program; redirection effects and parsed command substitutions remain checked."}
       ] else [] end)
     }
  ] as $results
| {
    units: [$u[] | {name, file, stream}],
    errors: [$results[] | .name as $name | .errors[] | select(.kind != "live-forward") | . + {name: $name}],
    live_forwarding: [$results[] | .name as $name | .errors[] | select(.kind == "live-forward")
      | {name:$name, line, reason:"Scrut asserts this block's live output; no local capture retains the diagnostic."}],
    embedded_strings: [$results[].strings[]],
    policy_exclusions: $excluded
  }
