# Jules dispatcher

This tool dispatches eligible Flow issues to Jules without allowing agent work
to outrun review capacity.

The dispatcher queries live Jules sessions, open GitHub pull requests and open
issues on every run. Local `jules_dispatch_state.json` is an audit cache, not
an ownership database.

An issue is deferred when a live session already covers it, an open pull
request references it, or an open pull request has a strongly overlapping
title. Eligible issues are ordered so security, regressions, broken CI,
release work and compiler blockers come before cleanup and micro-optimisation.

Two environment variables provide backpressure:

```text
JULES_MAX_ACTIVE=8
JULES_MAX_AGENT_PRS=12
```

When either limit is reached, the dispatcher exits successfully without
creating more sessions. Provider-capacity refusal also stops the dispatch
cycle instead of spinning.

Successful dispatch writes a GitHub issue comment containing the Jules session
claim. The claim lease is the live Jules session itself: once it disappears
from `jules remote list --session`, the comment is historical and does not
block future work.

Every run writes `jules_dispatch_decisions.jsonl`, with one JSON object per
issue decision. This makes dispatch, deferral, overlap and backpressure
decisions auditable.
