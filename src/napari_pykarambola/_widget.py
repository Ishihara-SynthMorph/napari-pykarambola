"""Widget for computing Minkowski tensors on a napari Labels layer."""

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from magicgui.widgets import ComboBox, Container, PushButton, create_widget

if TYPE_CHECKING:
    import napari

# Scalar outputs that can live as flat columns in layer.features.
# Full tensors (w020, w220, ...), eigenvectors, and the per-l msm_ql/msm_wl
# arrays are intentionally excluded here -- see the module docstring in
# README.md for why they aren't flattened into the table.
_SCALAR_SUFFIXES = ('_beta', '_trace', '_trace_ratio')
_SCALAR_BASE = {'w000', 'w100', 'w200', 'w300'}


def _extract_scalars(label_result: dict) -> dict:
    scalars = {}
    for key, value in label_result.items():
        if key in _SCALAR_BASE or key.endswith(_SCALAR_SUFFIXES):
            scalars[key] = float(value)
    return scalars


class MinkowskiTensorWidget(Container):
    """Compute Minkowski tensors for every object in a Labels layer.

    Scalar results (betas, traces, trace ratios, and base scalar
    functionals) are written to ``labels_layer.features``, one row per
    label, so they're immediately usable by downstream plugins such as
    napari-clusters-plotter and napari-feature-classifier.
    """

    def __init__(self, viewer: 'napari.viewer.Viewer'):
        super().__init__()
        self._viewer = viewer

        self._labels_combo = create_widget(
            label='Labels layer', annotation='napari.layers.Labels'
        )
        self._compute_combo = ComboBox(
            label='Compute', choices=['standard', 'all'], value='standard'
        )
        self._run_button = PushButton(text='Compute Minkowski tensors')
        self._run_button.changed.connect(self._run)

        self.extend(
            [
                self._labels_combo,
                self._compute_combo,
                self._run_button,
            ]
        )

    def _run(self):
        from pykarambola.api import minkowski_tensors_from_label_image

        labels_layer = self._labels_combo.value
        if labels_layer is None:
            return

        results = minkowski_tensors_from_label_image(
            labels_layer.data,
            compute=self._compute_combo.value,
        )

        rows = []
        for label_id, label_result in results.items():
            row = {'label': label_id}
            row.update(_extract_scalars(label_result))
            rows.append(row)

        features = pd.DataFrame(rows).set_index('label')
        # Reindex to the layer's full label set so unlabeled (0) and any
        # labels marching_cubes dropped don't desync features from the
        # layer's own label ids.
        all_labels = np.unique(labels_layer.data)
        all_labels = all_labels[all_labels != 0]
        features = features.reindex(all_labels).reset_index()
        labels_layer.features = features
