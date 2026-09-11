#!/bin/sh
# Returns the rob-paprocki keyring token that `gh` is authenticated with.
# Used via GIT_ASKPASS so the secret never appears in argv or the process table.
case "$1" in
  Username*) printf 'x-access-token' ;;
  *)         gh auth token ;;
esac
