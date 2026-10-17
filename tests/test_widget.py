import numpy as np

from napari_pykarambola._widget import MinkowskiTensorWidget


def test_minkowski_tensor_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[5:15, 5:15, 5:15] = 1
    layer = viewer.add_labels(label_image)

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'
    widget._run()

    assert list(layer.features['label']) == [1]
    assert 'w000' in layer.features.columns
    assert 'w220_beta' in layer.features.columns


def test_minkowski_tensor_widget_multiple_labels(make_napari_viewer):
    viewer = make_napari_viewer()
    label_image = np.zeros((20, 20, 20), dtype=int)
    label_image[2:6, 2:6, 2:6] = 1
    label_image[10:18, 10:18, 10:18] = 2
    layer = viewer.add_labels(label_image)

    widget = MinkowskiTensorWidget(viewer)
    widget._labels_combo.value = layer
    widget._compute_combo.value = 'all'
    widget._run()

    assert sorted(layer.features['label']) == [1, 2]
    assert len(layer.features) == 2
