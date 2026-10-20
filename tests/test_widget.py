import numpy as np

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
