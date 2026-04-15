# Pipeline stages

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

The build is intentionally split into stages so failures are easy to classify.

## Stage 1: Materialize

Copy sources into a fresh temporary workspace for the run. No cross-run cache is assumed in early versions.

## Stage 2: Convert

Turn Markdown (and other supported formats) into HTML fragments or pages, guided by the manifest and converter plugins.

## Stage 3: Site build

Run link checks, post-processing, and packaging. Navigation chrome and prev/next wiring consume the resolved manifest here—not earlier.

## Why separate?

Separating concerns keeps converter bugs from looking like asset pipeline bugs, and keeps diagnostics readable in CI logs.
