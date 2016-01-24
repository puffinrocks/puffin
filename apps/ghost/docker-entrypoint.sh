#!/bin/bash
set -e

echo "$*" > /input.txt

if [[ "$*" == npm*start* ]]; then
	for dir in "$GHOST_SOURCE/content"/*/; do
		targetDir="$GHOST_CONTENT/$(basename "$dir")"
		mkdir -p "$targetDir"
		if [ -z "$(ls -A "$targetDir")" ]; then
			tar -c --one-file-system -C "$dir" . | tar xC "$targetDir"
		fi
	done

	chown -R user "$GHOST_CONTENT"

	set -- gosu user "$@"
fi

exec "$@"
