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

    The per-label meshes produced internally by marching_cubes are kept
    around so a Surface layer, colored by any computed scalar, can be
    added afterwards without a duplicate marching_cubes pass.
    """

    def __init__(self, viewer: 'napari.viewer.Viewer'):
        super().__init__()
        self._viewer = viewer
        self._last_labels_layer = None
        self._last_results = None
        self._last_meshes = None

        self._labels_combo = create_widget(
            label='Labels layer', annotation='napari.layers.Labels'
        )
        self._compute_combo = ComboBox(
            label='Compute', choices=['standard', 'all'], value='standard'
        )
        self._run_button = PushButton(text='Compute Minkowski tensors')
        self._run_button.changed.connect(self._run)

        self._color_combo = ComboBox(label='Color surface by', choices=[])
        self._surface_button = PushButton(
            text='Visualize as Surface', enabled=False
        )
        self._surface_button.changed.connect(self._add_surface)

        self.extend(
            [
                self._labels_combo,
                self._compute_combo,
                self._run_button,
                self._color_combo,
                self._surface_button,
            ]
        )

    def _run(self):
        from pykarambola.api import minkowski_tensors_from_label_image

        labels_layer = self._labels_combo.value
        if labels_layer is None:
            return

        # return_meshes=True reuses the marching_cubes mesh already
        # produced internally, so visualizing as a Surface afterwards
        # doesn't re-run marching_cubes.
        #
        # labels_layer.scale carries the layer's physical voxel spacing in
        # the same (Z, Y, X) axis order as labels_layer.data, which matches
        # the (sz, sy, sx) convention minkowski_tensors_from_label_image's
        # spacing parameter forwards unchanged to marching_cubes -- so no
        # axis reordering is needed here.
        results, meshes = minkowski_tensors_from_label_image(
            labels_layer.data,
            compute=self._compute_combo.value,
            spacing=tuple(labels_layer.scale),
            return_meshes=True,
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

        self._last_labels_layer = labels_layer
        self._last_results = results
        self._last_meshes = meshes

        scalar_columns = [c for c in features.columns if c != 'label']
        self._color_combo.choices = scalar_columns
        if scalar_columns:
            self._color_combo.value = scalar_columns[0]
        self._surface_button.enabled = bool(meshes)

    def _add_surface(self):
        from pykarambola.api import combine_label_meshes

        if not self._last_meshes:
            return

        scalar = self._color_combo.value
        color_by = None
        if scalar is not None:
            color_by = {
                label_id: label_result[scalar]
                for label_id, label_result in self._last_results.items()
            }

        verts, faces, values, _ = combine_label_meshes(
            self._last_meshes, color_by=color_by
        )

        layer_name = f'{self._last_labels_layer.name} surface'
        if scalar is not None:
            layer_name += f' ({scalar})'
        self._viewer.add_surface((verts, faces, values), name=layer_name)
