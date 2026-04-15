# Performance notes

Static generators usually spend time in three places: IO, Markdown conversion, and link analysis.

## IO

Batch file reads where possible. Avoid walking huge trees unless the manifest asks for it.

## Conversion

Pure Python Markdown engines vary in speed. Pick one, then optimize with profiling—not guesses.

## Link checking

Internal checks are cheap. External checks are not—gate them behind flags.

## Parallelism

Parallelize per manifest leaf once determinism is defined. Keep ordering reproducible for debugging.
