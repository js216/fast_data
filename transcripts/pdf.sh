#!/bin/sh
#
# Generate one PDF per subdirectory, containing all
# interesting source files. Output goes to transcripts/*.pdf.
# Does not modify any other files.

set -eu

REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="$REPO/transcripts"

# Top-level dirs to skip entirely
SKIP_DIRS="transcripts manual fpga"

# Top-level dirs that emit one PDF per listed subdir instead of a combined PDF.
# Format: "<dir>:<sub1>,<sub2>,..." entries separated by whitespace.
SPLIT_DIRS="stm32mp135_test_board:baremetal,bootloader"

# Typst preamble: page setup, mono font, line-numbered code blocks
preamble() {
    cat <<'TYP'
#set page(width: 6.2in, height: 8.3in, margin: (bottom: 0.7in, rest: 0.4in), numbering: "1/1")
#set text(font: "Liberation Mono", size: 10pt)
#show raw.where(block: true): it => {
  let lines = it.text.split("\n")
  grid(columns: (auto, 1fr), column-gutter: 0.6em, row-gutter: 0.4em,
    ..lines.enumerate().map(((i, l)) => (
      align(right, text(fill: luma(170), str(i + 1))),
      raw(l, lang: it.lang),
    )).flatten())
}
TYP
}

# Map file extension to Typst/syntect language name
lang_for() {
    case "$1" in
        rs)       echo rust ;;
        c|h)      echo c ;;
        s|S)      echo asm ;;
        py)       echo python ;;
        lua)      echo lua ;;
        sh)       echo bash ;;
        js)       echo javascript ;;
        css)      echo css ;;
        html)     echo html ;;
        toml)     echo toml ;;
        typ)      echo typst ;;
        nw)       echo text ;;
        ldf)      echo text ;;
        v)        echo verilog ;;
        md)       echo markdown ;;
        *)        return 1 ;;
    esac
}

# Expand top-level dirs into the list of dirs to PDF. A cargo workspace
# (Cargo.toml containing [workspace]) emits one PDF per workspace member
# (subdir with its own Cargo.toml) instead of one combined PDF.
dirs=""
for dir in "$REPO"/*/; do
    name="$(basename -- "$dir")"

    skip=0
    for s in $SKIP_DIRS; do
        [ "$name" = "$s" ] && skip=1 && break
    done
    [ "$skip" = 1 ] && continue

    split=""
    for entry in $SPLIT_DIRS; do
        case "$entry" in "$name:"*) split="${entry#*:}"; break ;; esac
    done

    if [ -n "$split" ]; then
        IFS=, ; for sub in $split; do
            [ -d "$dir$sub" ] && dirs="$dirs$dir$sub/
"
        done ; unset IFS
    elif [ -f "$dir/Cargo.toml" ] && grep -q '^\[workspace\]' "$dir/Cargo.toml"; then
        for sub in "$dir"*/; do
            [ -f "$sub/Cargo.toml" ] || continue
            dirs="$dirs$sub
"
        done
    else
        dirs="$dirs$dir
"
    fi
done

printf '%s' "$dirs" | while IFS= read -r dir; do
    [ -z "$dir" ] && continue
    rel="${dir#"$REPO"/}"
    rel="${rel%/}"
    name="$(printf '%s' "$rel" | tr / -)"

    # Collect source files, pruning generated / build directories
    files="$(find "$dir" \
        \( -name target -o -name build -o -name .cargo -o -name .claude \
           -o -name __pycache__ -o -name cache \
           -o -name drivers -o -name nonfree \) -prune \
        -o \( -path '*/src/ui' -prune \) \
        -o -name 'prebaked.rs' -prune \
        -o -type f \( \
              -name '*.rs' -o -name '*.c' -o -name '*.h' \
           -o -name '*.s' -o -name '*.S' \
           -o -name '*.py' -o -name '*.lua' -o -name '*.sh' \
           -o -name '*.js' -o -name '*.css' -o -name '*.html' \
           -o -name '*.toml' -o -name '*.typ' \
           -o -name '*.nw' -o -name '*.ldf' -o -name '*.v' \
           -o -name '*.md' \
           -o -name 'Makefile' \
        \) -print 2>/dev/null | sort)"

    # Skip directories with no source files
    [ -z "$files" ] && continue

    pdf="$OUTDIR/${name}.pdf"
    echo "==> $name -> $(basename -- "$pdf")"

    # Generate Typst markup and pipe to compiler
    {
        preamble
        echo "$files" | while IFS= read -r f; do
            [ -z "$f" ] && continue
            rel="${f#"$REPO"/}"
            ext="${f##*.}"
            bname="$(basename -- "$f")"
            if [ "$bname" = "Makefile" ]; then
                lang="makefile"
            else
                lang="$(lang_for "$ext")" || lang="text"
            fi
            echo "= \`$rel\`"
            echo "#raw(read(\"/$rel\"), lang: \"$lang\", block: true)"
        done
    } | typst compile --root "$REPO" - "$pdf"
done

echo "Done."
