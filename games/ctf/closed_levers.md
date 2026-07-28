# Closed levers — CTF

These are inherited claims from upstream commit messages, not measurements
made by this optimizer lab. They should not be proposed as fresh levers
without an explicit reason to revisit them.

| Lever | Recorded verdict | Evidence source |
|---|---|---|
| Rear-guard experiment | `REFUTED, do not ship` | Upstream commit message in CTF history |
| Ender-screen experiment | `REFUTED, do not ship` | Upstream commit message in CTF history |
| Race-interceptor experiment | `REFUTED, do not ship` | Upstream commit message in CTF history |
| Offensive arc-breacher variant | `RETIRE, don't A/B` | Upstream arc-breacher audit commit message |
| Respawn-rally hold | Late-game rally holds converted decisive games into mutual-loss draws; upstream commit recorded beacon `42/48` mutual and mirror `19/48` mutual examples | Upstream `respawnRally` iteration-2 commit message |

These entries are not proof that every related mechanic is bad. They record
the narrower inherited verdicts and their stated evidence.

## Current compile-time knobs

The current upstream baseline source treats these behavior switches as
default-off unless passed as Nim `-d:` defines. `artlogNoCurl` is in the
artifact logger module and is also default-off. These are controls to measure,
not closed levers.

| Knob | Default | Control |
|---|---|---|
| `taunt` | off | Optional Bedrock/canned taunt worker and taunt shouts |
| `rushAll` | off | Assigns every seat the `MidTop` role |
| `zonePhalanx` | off | Alternate lane-pair/phalanx duty system |
| `campNade` | off | Grenades against stationary remembered enemies after fogging |
| `statue` | off | Zero-input standing test mode |
| `shoutCoord` | off | Gameplay coordination shouts |
| `siege` | off | Siege/barrage/advance coordination |
| `nadeRelay` | off | Grenade pickup/respawn relay shouts |
| `shoutThief` | off | Thief position-fix shouts |
| `carryDebug` | off | Carry-state debug logging |
| `counterPunch` | off | Late counter-push after losing the own heart |
| `targetCall` | off | Target callouts for mate convergence/grenade response |
| `stickyBreak` | off | One-shot sticky stalemate breaker |
| `v57Debug` | off | Late-push/thief/grenade debug logging |
| `nadeCluster` | off | Grenades against remembered enemy clusters |
| `swarm` | off | Defensive roles assist a teammate carrier |
| `holdFront` | off | Caps phalanx front creep |
| `centerScan` | off | Center-corridor scan while crossing midfield |
| `nadeDebug` | off | Grenade-detour/debug probes |
| `thiefCommit` | off | Longer thief-fix commitment and carrier prediction |
| `artlogNoCurl` | off | Removes libcurl; disables hosted HTTP artifact delivery |

The Docker build also passes ordinary build controls `release` and
`useMalloc`, and records the injected set through the `buildDefines` string
define. Historical branch-only defines are not current controls.
