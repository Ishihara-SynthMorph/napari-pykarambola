import numpy as np
import pytest

from napari_pykarambola._widget import MinkowskiTensorWidget


def _run_and_wait(widget, qtbot, timeout=10000):
    """Trigger the threaded ``_run`` and block until it completes.

    ``_run`` only *starts* the background worker, so we need to pump the
    Qt event loop until the worker's ``returned``/``errored`` signal has
    fired before asserting on anything the ``returned`` callback writes.
    """
    widget._run()
    assert widget._worker is not None
    with qtbot.waitSignal(
        widget._worker.returned, timeout=timeout, raising=True
    ):
        pass


def test_minkowski_tensor_widget(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[5:15, 5:15, 5:15] = 1
    layer = viewer.add_labels(label_image)

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'
    _run_and_wait(widget, qtbot)

    assert list(layer.features['label']) == [1]
    assert 'w000' in layer.features.columns
    assert 'w220_beta' in layer.features.columns
    assert widget._run_button.enabled


def test_minkowski_tensor_widget_multiple_labels(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[2:6, 2:6, 2:6] = 1
    label_image[10:18, 10:18, 10:18] = 2
    layer = viewer.add_labels(label_image)

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'
    _run_and_wait(widget, qtbot)

    assert sorted(layer.features['label']) == [1, 2]
    assert len(layer.features) == 2
    assert widget._run_button.enabled


def test_minkowski_tensor_widget_runs_in_background(make_napari_viewer, qtbot):
    """The run button should be disabled while the worker is in flight."""
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[5:15, 5:15, 5:15] = 1
    layer = viewer.add_labels(label_image)

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'

    widget._run()
    # Best-effort: for a tiny image the worker may finish before we get
    # here, so don't make this assertion a hard requirement.
    if widget._worker.is_running:
        assert not widget._run_button.enabled

    with qtbot.waitSignal(
        widget._worker.returned, timeout=10000, raising=True
    ):
        pass

    assert widget._run_button.enabled
    assert list(layer.features['label']) == [1]
    assert 'w000' in layer.features.columns
    assert 'w220_beta' in layer.features.columns


def test_minkowski_tensor_widget_anisotropic_scale(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[5:15, 5:15, 5:15] = 1

    # Unscaled baseline.
    layer_unit = viewer.add_labels(label_image.copy())
    widget_unit = MinkowskiTensorWidget(viewer)
    widget_unit._labels_combo.value = layer_unit
    widget_unit._compute_combo.value = 'standard'
    _run_and_wait(widget_unit, qtbot)
    w000_unit = layer_unit.features.loc[
        layer_unit.features['label'] == 1, 'w000'
    ].iloc[0]

    # Same shape, but with an anisotropic scale: z is stretched 2x,
    # y/x stay at unit spacing. layer.scale is (z, y, x), matching the
    # data array's axis order.
    scale = (2.0, 1.0, 1.0)
    layer_scaled = viewer.add_labels(label_image.copy())
    layer_scaled.scale = scale
    widget_scaled = MinkowskiTensorWidget(viewer)
    widget_scaled._labels_combo.value = layer_scaled
    widget_scaled._compute_combo.value = 'standard'
    _run_and_wait(widget_scaled, qtbot)
    w000_scaled = layer_scaled.features.loc[
        layer_scaled.features['label'] == 1, 'w000'
    ].iloc[0]

    # Volume should scale by the product of the per-axis scale factors.
    scale_product = scale[0] * scale[1] * scale[2]
    assert w000_scaled / w000_unit == pytest.approx(scale_product, rel=0.05)


def test_minkowski_tensor_widget_roi_id(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[2:6, 2:6, 2:6] = 1
    label_image[10:18, 10:18, 10:18] = 2
    layer = viewer.add_labels(label_image, name='my_labels')

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'
    _run_and_wait(widget, qtbot)

    assert 'roi_id' in layer.features.columns
    assert all(layer.features['roi_id'] == layer.name)


def test_minkowski_tensor_widget_add_surface(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[2:6, 2:6, 2:6] = 1
    label_image[10:18, 10:18, 10:18] = 2
    layer = viewer.add_labels(label_image)

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'
    _run_and_wait(widget, qtbot)

    assert widget._surface_button.enabled
    assert 'w220_beta' in widget._color_combo.choices

    n_layers_before = len(viewer.layers)
    widget._color_combo.value = 'w220_beta'
    widget._add_surface()

    assert len(viewer.layers) == n_layers_before + 1
    surface_layer = viewer.layers[-1]

    n_verts_expected = sum(len(v) for v, _f in widget._last_meshes.values())
    n_faces_expected = sum(len(f) for _v, f in widget._last_meshes.values())
    verts, faces, values = surface_layer.data
    assert len(verts) == n_verts_expected
    assert len(faces) == n_faces_expected
    assert len(values) == n_verts_expected
