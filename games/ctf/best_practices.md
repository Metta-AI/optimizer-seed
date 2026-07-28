# Best practices — CTF

These are operational practices established during setup. They are not
claims about policy strength.

- Use `softmax set-token "$SOFTMAX_USER_API_TOKEN"` before Coworld calls.
- Verify the active player identity before upload or submission.
- Treat `coworld episodes --limit 50` and `--limit 200` as unreliable: they
  returned HTTP 500 during setup. Use a page size of 20.
- XP requests have a maximum of 100 episodes.
- Smoke-test policy liveness before interpreting competitive metrics; v47 was
  disqualified after completing zero episodes in a round.
- Record the full source commit, image digest, policy version, and build
  defines for every candidate.
- CTF A/Bs should pin all 16 seats and mirror even/odd assignment so each
  policy plays both sides.
- League submission is human-gated. Uploads are inert and do not imply
  submission.

## Build and upload

From `~/repos/coworld-ctf`:

```bash
docker build \
  -f players/baseline/Dockerfile \
  -t ctf-mainline:<short-sha> \
  .

coworld upload-policy ctf-mainline:<short-sha> \
  --name ctf-autoresearch \
  --tag source_commit=<full-sha>
```

The pure-mainline H1 build used no extra `NIM_DEFINES`. The Dockerfile passes
`-d:release`, `-d:useMalloc`, and records them through `buildDefines`.

## Local/debug commands

Compile the reference bot:

```bash
nim c players/baseline/baseline.nim
```

Run a source-level 16-player self-play client set against a local CTF server:

```bash
for i in $(seq 0 15); do
  token="0xBADA55_$i"
  url="ws://localhost:2000/player?slot=$i&token=$token"
  COWORLD_PLAYER_WS_URL="$url" ./players/baseline/baseline.out &
done
wait
```

The local runner shape, once a manifest is hydrated with local game images,
is:

```bash
coworld run-episode /path/to/hydrated/coworld_manifest.json \
  ctf-mainline:<short-sha> --variant default --episodes 1
```
