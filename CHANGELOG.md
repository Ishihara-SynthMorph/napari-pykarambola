# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `roi_id` column in `labels_layer.features`, set to the Labels layer's
  name, for compatibility with napari-feature-classifier (which requires
  both `label` and `roi_id`).
- `MinkowskiTensorWidget` can now add a `Surface` layer built from the
  per-label meshes computed internally, colored by any scalar written to
  `labels_layer.features` (e.g. `w220_beta`). Requires pykarambola>=0.7.0,
  which ships `return_meshes`/`combine_label_meshes`
  ([pykarambola#176](https://github.com/Ishihara-SynthMorph/pykarambola/pull/176)).
- README demo walking through the Surface visualization on a real
  segmentation (`demo.py`, segmenting scikit-image's `cells3d` nuclei
  channel), with a comparison callout to napari-skimage-regionprops.

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
