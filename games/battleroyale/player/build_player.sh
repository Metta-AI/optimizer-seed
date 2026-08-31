#!/usr/bin/env bash
# Build the Battle Royale player image(s).
#
#   player/build_player.sh                 -> br-baseline:latest (baseline, legacy doctrine)
#   player/build_player.sh <doctrine>      -> br-<doctrine>:latest (one baked env change)
#
# The baseline is Nim and must be built with the game repo ROOT as context. We
# clone the pinned game source under .src/ (gitignored) so builds are
# reproducible without vendoring the whole game tree.
#
# A "doctrine" build is a thin wrapper over the baseline image that bakes exactly
# one env var (CTF_BOT_FFA_DOCTRINE=<doctrine>) — our one-attributable-change
# unit. See docs/ENV_VARIATION.md in the game repo for the full knob list.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$LAB_DIR/.src/coworld-battle-royale"
GAME_REPO="https://github.com/Metta-AI/coworld-battle-royale.git"
GAME_COMMIT="8025b3437d1018b5e4c94c4d07e9841a53d3f7d4"

DOCTRINE="${1:-}"

# --- ensure pinned source ---
if [ ! -d "$SRC_DIR/.git" ]; then
  mkdir -p "$(dirname "$SRC_DIR")"
  git clone "$GAME_REPO" "$SRC_DIR"
fi
git -C "$SRC_DIR" fetch --depth 1 origin "$GAME_COMMIT" 2>/dev/null || git -C "$SRC_DIR" fetch origin
git -C "$SRC_DIR" checkout -q "$GAME_COMMIT"

# --- always build the baseline first (the base image) ---
echo "Building br-baseline:latest (baseline, legacy doctrine) ..."
docker build --platform=linux/amd64 \
  -f "$SRC_DIR/players/baseline/Dockerfile" \
  -t br-baseline:latest \
  "$SRC_DIR"

if [ -z "$DOCTRINE" ]; then
  echo "Done: br-baseline:latest"
  exit 0
fi

# --- doctrine wrapper: exactly one baked env change ---
TAG="br-${DOCTRINE}:latest"
echo "Building $TAG (CTF_BOT_FFA_DOCTRINE=$DOCTRINE) ..."
docker build --platform=linux/amd64 \
  -f "$LAB_DIR/player/Dockerfile.doctrine" \
  --build-arg "DOCTRINE=$DOCTRINE" \
  -t "$TAG" \
  "$LAB_DIR/player"
echo "Done: $TAG"
