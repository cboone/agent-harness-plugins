# Helpers the report-board tests include with jq -L to give an issue or bug
# progress and affinity without spelling out every field.

# A progress object at $stage, carried by $carrier, with no flags.
def progress($stage; $carrier): {
  stage: $stage,
  carrier: $carrier,
  signal: "sample signal",
  lastActivity: "2026-08-30T12:00:00Z",
  since: null,
  nextMove: "author",
  nextAction: "open a pull request",
  flags: [],
  host: null,
  extraCarriers: []
};

# Affinity with no owner, as every issue carries when nothing says otherwise.
def no_affinity: {owner: null, kind: null, tier: null, reasons: []};

# Applies f to the backlog issue numbered $n.
def on($n; f): (.issues[] | select(.number == $n)) |= f;

# Applies f to the bug numbered $n.
def on_bug($n; f): (.bugs[] | select(.number == $n)) |= f;
