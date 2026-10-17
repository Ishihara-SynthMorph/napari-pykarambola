import numpy as np

from napari_pykarambola._sample_data import make_sample_data


def test_make_sample_data():
    layers = make_sample_data()
    assert len(layers) == 1
    data, meta, layer_type = layers[0]
    assert layer_type == 'labels'
    assert data.ndim == 3
    assert np.issubdtype(data.dtype, np.integer)
    assert set(np.unique(data)) == {0, 1, 2}
