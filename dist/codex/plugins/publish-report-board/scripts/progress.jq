# The progress model and affinity rules of
# skills/publish-report-board/references/progress-model.md, as jq definitions.
# backlog-gather and bugs-gather each read this file and put it ahead of their
# own filters, so an issue reads the same on both boards. Each script turns
# what it gathered into the shapes these definitions take; the derivation
# rules live only here.

def as_list: if type == "array" then . else [] end;
# An ISO 8601 time as seconds since the epoch, accepting a fraction and either
# Z or a numeric offset. Anything else is an error, never an empty result,
# because capture emits nothing on a mismatch and would drop the value silently.
def epoch:
  ([capture("^(?<d>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2})(:(?<s>[0-9]{2}))?(\\.[0-9]+)?(?<z>Z|(?<sign>[+-])(?<h>[0-9]{2}):(?<m>[0-9]{2}))$")] | first)
  | if . == null then error("not an ISO 8601 time") else . end
  | ((.d + ":" + (.s // "00") + "Z") | fromdateiso8601)
    - (if .z == "Z" then 0 else ((.h | tonumber) * 3600 + (.m | tonumber) * 60) * (if .sign == "+" then 1 else -1 end) end);
def utc: if type == "string" then epoch | todateiso8601 else null end;
# The latest of a list of times in UTC, or null when it holds none.
def latest: map(select(type == "string")) | if length == 0 then null else max_by(epoch) | utc end;
def plural($n; $one; $many): "\($n) \(if $n == 1 then $one else $many end)";
def same_text($list): ascii_downcase as $v | any($list[]; ascii_downcase == $v);
def same_repo($repo): ascii_downcase == ($repo | ascii_downcase);

def stage_order: ["started", "branch", "draft", "awaiting-review", "needs-author", "ready-to-merge", "close-out"];
def stage_rank: . as $s | stage_order | index($s);

# Branches that dependency bots open name package versions, not issues.
def bot_branch: test("^(dependabot|renovate)/");
# A branch names issue $n when one segment of its name, between slashes,
# starts with the number, bare or after a word and a - or _ (fix-412),
# issue, gh, or #, and the number ends the segment or a - or _ follows it. So
# feature/412-tags and issue412 name #412; chore/412 does not name #41, and
# checkout-4.2.2 and update-to-v9 name nothing.
def names_issue($n):
  (bot_branch | not)
  and any(split("/")[]; test("^([a-z]+[-_]|issue|gh|#)?\($n)([-_]|$)"; "i"));

# The stage an open pull request reaches. It takes the shape both gathers
# build: isDraft, mergeable, reviewDecision, checks (the rollup state),
# reviewRequests (a count), and number.
def pr_stage:
  if .isDraft then "draft"
  elif .mergeable == "CONFLICTING" or .reviewDecision == "CHANGES_REQUESTED" or (.checks | IN("FAILURE", "ERROR")) then "needs-author"
  elif .reviewDecision == "REVIEW_REQUIRED" or (.checks | IN("PENDING", "EXPECTED")) then "awaiting-review"
  else "ready-to-merge" end;
def pr_next:
  pr_stage as $stage
  | if $stage == "draft" then {nextMove: "author", nextAction: "mark it ready for review"}
    elif $stage == "needs-author" then
      {nextMove: "author", nextAction: (if .mergeable == "CONFLICTING" then "resolve the conflict" elif .reviewDecision == "CHANGES_REQUESTED" then "answer the review" else "fix the checks" end)}
    elif $stage == "awaiting-review" then
      (if .reviewDecision == "REVIEW_REQUIRED" then
         (if .reviewRequests > 0 then {nextMove: "reviewer", nextAction: "wait for review"} else {nextMove: "nobody", nextAction: "request a review"} end)
       else {nextMove: "ci", nextAction: "wait for checks"} end)
    else {nextMove: "author", nextAction: "merge it"} end;
# GitHub reports mergeable as UNKNOWN while it computes the answer, which
# counts as no conflict; the signal says so.
def pr_signal:
  "pull request #\(.number), "
  + (if .isDraft then "draft"
     else
       [(if .reviewDecision == "APPROVED" then "approved"
         elif .reviewDecision == "CHANGES_REQUESTED" then "changes requested"
         elif .reviewDecision == "REVIEW_REQUIRED" then "review required, \(if .reviewRequests == 0 then "no review" else plural(.reviewRequests; "review"; "reviews") end) requested"
         else "no review required" end),
        (if .mergeable == "CONFLICTING" then "merge conflict" elif .mergeable == "UNKNOWN" then "mergeability unknown" else empty end),
        (if .checks == "SUCCESS" then "checks passing"
         elif .checks | IN("FAILURE", "ERROR") then "checks failing"
         elif .checks | IN("PENDING", "EXPECTED") then "checks running"
         else "no checks" end)]
       | join(", ")
     end);

# Joins the refs of each branch name, each {name, local, remote, worktree, at,
# ahead, behind}, into one branch, leaving out the default branch. ahead and
# behind are null when the gather could not count them. The counts come from
# the ref furthest ahead, so a local branch with no commits does not hide work
# pushed from elsewhere.
def join_branches($default):
  group_by(.name)
  | map((map(select(.ahead != null)) | max_by(.ahead)) as $counted
        | {name: .[0].name,
           local: any(.[]; .local == true),
           remote: any(.[]; .remote == true),
           worktree: any(.[]; .worktree == true),
           at: (map(.at) | latest),
           ahead: (if $counted == null then null else $counted.ahead end),
           behind: (if $counted == null then null else $counted.behind end)})
  | map(select(.name != $default));
# A branch carries work while it has commits beyond the default branch, or
# while a worktree has it checked out. One whose commits the gather could not
# count still does, and its signal says so.
def carries_work: .ahead == null or .ahead > 0 or .worktree == true;
def branch_signal:
  "branch \(.name), "
  + (if .ahead == null then "commits ahead unknown" else "\(plural(.ahead; "commit"; "commits")) ahead" end)
  + (if (.behind // 0) > 0 then ", \(.behind) behind" else "" end)
  + (if .local and (.remote | not) then ", local" else "" end);

# The merged pull requests in $repo that link an open issue, read from the
# issue as GitHub returns it, each {number, mergedAt, closes}. A closing
# reference, which includes a manual link, closes it; a cross-reference closes
# it only with a closing keyword. GitHub drops a removed manual link from the
# closing references, so the timeline's connect events are not read.
def merged_links($repo):
  [(.closedByPullRequestsReferences.nodes | as_list | .[] | . + {closes: true}),
   (.timelineItems.nodes | as_list | .[] | select(.__typename == "CrossReferencedEvent") | (.source // {}) + {closes: (.willCloseTarget == true)})]
  | map(select(.number != null and .mergedAt != null and ((.repository.nameWithOwner // "") | same_repo($repo)))
        | {number, mergedAt: (.mergedAt | utc), closes})
  | group_by(.number) | map(.[0] + {closes: any(.[]; .closes)});

# The progress of one open issue, or null when no signal marks work on it.
# $item has number, labels (names), updatedAt, pipeline and pipelineSince
# (null without ZenHub), prs (its open pull requests in the repository, each
# as pr_stage takes it plus headRefName, mergeStateStatus, createdAt,
# updatedAt, and lastReview), and merged (from merged_links). $branches come
# from join_branches; $c holds progressLabels, progressPipelines, quietDays,
# and staleDays; $now is the gather time in epoch seconds; and $host names
# the machine that saw a local branch.
def progress_of($item; $branches; $c; $now; $host):
  $item.number as $n
  | [$item.labels[] | select(same_text($c.progressLabels))] as $labels
  | (if $item.pipeline != null and (($c.progressPipelines // []) | index($item.pipeline)) != null then $item.pipeline else null end) as $pipeline
  | (($labels | length) > 0 or $pipeline != null) as $marked
  | [$item.prs[] | .headRefName] as $heads
  # A pull request and its own head branch carry the issue once.
  | [$branches[] | select((.name | names_issue($n)) and carries_work and (.name as $b | $heads | index($b) | not))] as $free
  # A merged pull request that only mentions the issue counts while a progress
  # label or pipeline says work on it was under way. Without one, a mention is
  # usually a follow-up the pull request left open, not finished work.
  | [$item.merged[] | select(.closes or $marked)] as $merged
  | [($merged | sort_by(.mergedAt | epoch) | reverse | .[]
      | {carrier: {pr: .number}, stage: "close-out", signal: "pull request #\(.number) merged \(.mergedAt | utc | .[0:10])",
         lastActivity: (.mergedAt | utc), since: (.mergedAt | utc), nextMove: "author", nextAction: "close or split"}),
     ($item.prs[] | . as $p
      | (first($branches[] | select(.name == $p.headRefName)) // null) as $head
      | {carrier: {pr: .number}, stage: pr_stage, signal: pr_signal,
         lastActivity: ([.updatedAt, .lastReview, $head.at] | latest), since: (.createdAt | utc),
         behind: (.mergeStateStatus == "BEHIND" or (($head.behind // 0) > 0)), conflict: (.mergeable == "CONFLICTING"), work: true}
        + pr_next),
     ($free[] | (.local and (.remote | not)) as $only_local
      | {carrier: {branch: .name}, stage: "branch", signal: branch_signal, lastActivity: (.at | utc), since: null,
         nextMove: "author", nextAction: (if $only_local then "push it" else "open a pull request" end),
         behind: ((.behind // 0) > 0), local: $only_local, work: true}),
     ($labels[]
      | {carrier: {label: .}, stage: "started", signal: "the \(.) label", lastActivity: ($item.updatedAt | utc), since: null,
         nextMove: "author", nextAction: "open a branch"}),
     ($pipeline | select(. != null)
      | {carrier: {pipeline: .}, stage: "started", signal: "the \(.) pipeline", lastActivity: (($item.pipelineSince // $item.updatedAt) | utc), since: null,
         nextMove: "author", nextAction: "open a branch"})] as $all
  | if ($all | length) == 0 then null
    else
      # The furthest stage carries the issue; among equals, the latest
      # activity, then the first listed.
      ($all | to_entries | sort_by([(.value.stage | stage_rank), (.value.lastActivity | if . == null then 0 else epoch end), -.key]) | last | .value) as $top
      | ($now - ($top.lastActivity | if . == null then $now else epoch end)) as $age
      | [(select($age > $c.staleDays * 86400) | "stale"),
         (select($age > $c.quietDays * 86400 and $age <= $c.staleDays * 86400) | "quiet"),
         (select($top.behind == true) | "behind"),
         (select($top.conflict == true) | "conflict"),
         (select($top.stage != "close-out" and ([$all[] | select(.work == true)] | length) > 1) | "multiple"),
         (select($top.local == true) | "local"),
         (select($top.stage == "close-out" and ($labels | length) > 0) | "leftover-label")] as $flags
      | {stage: $top.stage, carrier: $top.carrier, signal: $top.signal, lastActivity: $top.lastActivity, since: $top.since,
         nextMove: $top.nextMove, nextAction: (if ($flags | index("stale")) != null then "resume or drop" else $top.nextAction end),
         flags: $flags, host: (if $top.local == true then $host else null end),
         extraCarriers: [$all[] | select(. != $top) | .carrier]}
    end;

# A path pattern as an anchored regular expression. ** crosses path segments,
# **/ also matches no segment at all, * and ? stay within one, a trailing /
# covers everything below it, and every other character is literal.
def glob_regex:
  (if endswith("/") then . + "**" else . end)
  | [scan("\\*\\*/|\\*\\*|\\*|\\?|[^*?]")]
  | map(if . == "**/" then "(.*/)?"
        elif . == "**" then ".*"
        elif . == "*" then "[^/]*"
        elif . == "?" then "[^/]"
        else gsub("(?<c>[.+()\\[\\]{}^$|\\\\])"; "\\\(.c)") end)
  | "^" + join("") + "$";
# For each of $areas ({name, paths}) that covers one of $files ({path, via}),
# the area and the first file it covers, as [name, file].
def area_hits($areas; $files):
  $areas[] | . as $area | (.paths | map(glob_regex)) as $res
  | first($files[] | select(.path as $p | any($res[]; . as $re | $p | test($re)))) // empty
  | [$area.name, .];
# The tier 1 and tier 2 reasons of an issue, one per area.
def active_reasons($areas; $files): [area_hits($areas; $files) | "\(.[0]) changed on \(.[1].via)"];
def recent_reasons($areas; $files; $days): [area_hits($areas; $files) | "\(.[0]) changed in \(.[1].via) within \($days) days"];

# The signal kinds uniformity ignores. $held lists every open issue's
# affinity signals: assignees (logins), claims (each in words, such as
# "claimed with the mine label"), author (a login), commented (whether the
# current user commented within the comment days), and active and recent,
# the tier 1 and tier 2 reasons. A kind is ignored when one owner holds it on
# at least the uniformity share of the open issues, and there are at least
# the uniformity minimum of them. The current user is the only owner of
# commented, active, and recent.
def uniformity_ignored($held; $c):
  ($held | length) as $total
  | def uniform($owners): $total >= $c.uniformityMinimum and (([$owners | group_by(.)[] | length] | max // 0) >= $c.uniformityShare * $total);
    [(select(uniform([$held[] | .assignees | unique[]])) | "assigned"),
     (select(uniform([$held[] | select(.claims | length > 0) | if (.assignees | length) > 0 then (.assignees | unique[]) else "unknown" end])) | "claimed"),
     (select(uniform([$held[] | .author])) | "filed"),
     (select(uniform([$held[] | select(.commented) | "you"])) | "commented"),
     (select(uniform([$held[] | select(.active | length > 0) | "you"])) | "active"),
     (select(uniform([$held[] | select(.recent | length > 0) | "you"])) | "recent")];
# The affinity of one issue from its signals $s, shaped as uniformity_ignored
# takes them, leaving out the kinds in $ignored. The owner is the current user
# when assigned; another person when assigned; the assignees of a claim, the
# current user first; the current user by an implicit tier; no one known for a
# claim with no assignee; and otherwise no one.
def affinity_of($s; $ignored; $viewer; $c):
  def on($kind): $ignored | index($kind) | not;
  ($s.assignees | index($viewer) != null) as $assigned_you
  | ($s.assignees | map(select(. != $viewer)) | first) as $other
  | (if on("claimed") then $s.claims else [] end) as $claims
  | [(select(on("active") and ($s.active | length) > 0) | {tier: 1, reasons: $s.active}),
     (select(on("recent") and ($s.recent | length) > 0) | {tier: 2, reasons: $s.recent}),
     (select(on("filed") and $s.author == $viewer) | {tier: 3, reasons: ["filed it"]}),
     (select(on("commented") and $s.commented) | {tier: 3, reasons: ["commented within \($c.affinityCommentDays) days"]})] as $tiers
  | if on("assigned") and $assigned_you then {owner: "you", kind: "explicit", tier: null, reasons: (["assigned"] + $claims)}
    elif on("assigned") and $other != null then {owner: $other, kind: "explicit", tier: null, reasons: ["assigned to @\($other)"]}
    elif ($claims | length) > 0 and $assigned_you then {owner: "you", kind: "explicit", tier: null, reasons: $claims}
    elif ($claims | length) > 0 and $other != null then {owner: $other, kind: "explicit", tier: null, reasons: ($claims + ["assigned to @\($other)"])}
    elif ($tiers | length) > 0 then {owner: "you", kind: "implicit", tier: ($tiers | map(.tier) | min), reasons: [$tiers[] | .reasons[]]}
    elif ($claims | length) > 0 then {owner: "unknown", kind: "explicit", tier: null, reasons: $claims}
    else {owner: null, kind: null, tier: null, reasons: []} end;
