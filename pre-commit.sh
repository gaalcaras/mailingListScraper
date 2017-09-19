#!/bin/sh

# Stash unstaged changes before running tests
# to avoid testing code that isn't part of the
# prospective commit.
STASH_NAME="pre-commit-$(date +%s)"
git stash save -q --keep-index "$STASH_NAME"

# Run tests
printf "Running tests:\n"
./run-tests.sh
RESULT=$?

# Restore stash
STASHES=$(git stash list)
if [ "$STASHES" = "$STASH_NAME" ]; then
  git stash pop -q
fi

# Act on test results
[ $RESULT -ne 0 ] && exit 1
exit 0
