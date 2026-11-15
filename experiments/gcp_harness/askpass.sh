#!/bin/sh
# Returns the token that `gh` is currently authenticated with.
# Used via GIT_ASKPASS so the secret never appears in argv or the process table.
case "$1" in
  Username*) printf 'x-access-token' ;;
  *)         gh auth token ;;
esac
