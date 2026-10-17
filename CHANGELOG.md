# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

### Added

- `MinkowskiTensorWidget`, a napari widget that computes Minkowski tensors
  for every object in a `Labels` layer and writes scalar results
  (`w000`, `w100`, `w200`, `w300`, and `*_beta`/`*_trace`/`*_trace_ratio`
  for the rank-2 tensor family) to `labels_layer.features`.
- Sample data: a synthetic 3D label image with a near-spherical blob and a
  dumbbell shape, available via `File > Open Sample`.

[Unreleased]: https://github.com/Ishihara-SynthMorph/napari-pykarambola/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ishihara-SynthMorph/napari-pykarambola/releases/tag/v0.1.0
