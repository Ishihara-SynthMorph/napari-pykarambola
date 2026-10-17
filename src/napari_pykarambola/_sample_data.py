"""Sample label image for napari-pykarambola.

Provides a small 3D label image with two objects of different shape
complexity: a near-spherical blob (label 1) and a dumbbell (label 2,
two lobes joined by a thin neck) so the Minkowski-tensor widget has
something with non-trivial anisotropy to compute on.
"""

from __future__ import annotations

import numpy as np


def make_sample_data():
    shape = (40, 60, 40)
    image = np.zeros(shape, dtype=np.int32)

    zz, yy, xx = np.mgrid[0 : shape[0], 0 : shape[1], 0 : shape[2]]

    sphere_center = np.array([20, 15, 20])
    sphere_radius = 10
    sphere_mask = (
        (zz - sphere_center[0]) ** 2
        + (yy - sphere_center[1]) ** 2
        + (xx - sphere_center[2]) ** 2
    ) <= sphere_radius**2
    image[sphere_mask] = 1

    lobe_a = np.array([20, 40, 20])
    lobe_b = np.array([20, 52, 20])
    lobe_radius = 7
    neck_radius = 3
    dumbbell_mask = (
        (
            (
                (zz - lobe_a[0]) ** 2
                + (yy - lobe_a[1]) ** 2
                + (xx - lobe_a[2]) ** 2
            )
            <= lobe_radius**2
        )
        | (
            (
                (zz - lobe_b[0]) ** 2
                + (yy - lobe_b[1]) ** 2
                + (xx - lobe_b[2]) ** 2
            )
            <= lobe_radius**2
        )
        | (
            (np.abs(yy - 46) <= 6)
            & ((zz - 20) ** 2 + (xx - 20) ** 2 <= neck_radius**2)
        )
    )
    image[dumbbell_mask & (image == 0)] = 2

    return [(image, {'name': 'pykarambola sample labels'}, 'labels')]
