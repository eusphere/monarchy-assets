#!/bin/sh
# Build the Healer from nothing, in the order the stages depend on each other.
#   HEALER_RES      mesh resolution of the cloth (1.0 full, 0.6 for quick trials)
#   HEALER_BLEND    file to build (default src/healer-claude.blend)
#   HEALER_RENDERS  where stage renders go
#   START_AT        stage name to resume from (needs LOG_DIR from the earlier run)
# Each stage logs to $LOG_DIR/<stage>.log; the script stops at the first failure.
set -e
cd "$(dirname "$0")/../.."
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
FILE="${HEALER_BLEND:-src/healer-claude.blend}"
LOG_DIR="${LOG_DIR:-/tmp}"
# START_AT=<stage> resumes from the snapshot taken before that stage in an earlier run.
SKIPPING="${START_AT:-}"
stage() {
    name="$1"; shift
    if [ -n "$SKIPPING" ]; then
        if [ "$SKIPPING" != "$name" ]; then return 0; fi
        SKIPPING=""
        cp "$LOG_DIR/before-$name.blend" "$FILE"
    fi
    if [ -f "$FILE" ]; then cp "$FILE" "$LOG_DIR/before-$name.blend"; fi
    echo "== $name $(date +%H:%M:%S)"
    "$@" > "$LOG_DIR/$name.log" 2>&1
    if grep -q "Traceback" "$LOG_DIR/$name.log"; then
        echo "$name failed; see $LOG_DIR/$name.log"; exit 1
    fi
}
stage 01_base      "$BLENDER" -b --python tools/healer_claude/01_base.py
stage 02_skirt     "$BLENDER" -b "$FILE" --python tools/healer_claude/02_skirt.py
stage 03_headwrap  env HEALER_VEIL=0 "$BLENDER" -b "$FILE" --python tools/healer_claude/03_veil.py
stage 04_cowl      "$BLENDER" -b "$FILE" --python tools/healer_claude/04_cowl.py
stage 03_veil      "$BLENDER" -b "$FILE" --python tools/healer_claude/03_veil.py
stage 05_headpiece "$BLENDER" -b "$FILE" --python tools/healer_claude/05_headpiece.py
stage 06_materials "$BLENDER" -b "$FILE" --python tools/healer_claude/06_materials.py
stage 07_fit       "$BLENDER" -b "$FILE" --python tools/healer_claude/07_fit.py
stage 08_posture   "$BLENDER" -b "$FILE" --python tools/healer_claude/08_posture.py
stage 09_bind      "$BLENDER" -b "$FILE" --python tools/healer_claude/09_bind.py
echo "== done $(date +%H:%M:%S)"
