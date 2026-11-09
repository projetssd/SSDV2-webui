#!/usr/bin/env bash
# Aucun tag fourni par l'utilisateur : seule la référence Git décide.
set -euo pipefail
: "${IMAGE:?IMAGE requis}"
case "${GITHUB_EVENT_NAME:-}" in
  push|workflow_dispatch) ;;
  *) exit 0 ;;
esac
case "${GITHUB_REF:-}" in
  refs/heads/dev) printf '%s:dev\n' "$IMAGE" ;;
  refs/heads/main) printf '%s:latest\n' "$IMAGE" ;;
  *)
    if [[ "${GITHUB_REF:-}" =~ ^refs/tags/(v[a-zA-Z0-9_.-]{0,127})$ ]]; then
      printf '%s:%s\n' "$IMAGE" "${BASH_REMATCH[1]}"
    fi
    ;;
esac
