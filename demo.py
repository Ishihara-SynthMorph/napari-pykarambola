import napari
import numpy as np
from scipy import ndimage as ndi
from skimage import data, feature, filters, morphology, segmentation

cells = data.cells3d()  # (60, 2, 256, 256): z, channel, y, x
membranes, nuclei = cells[:, 0], cells[:, 1]

# segment nuclei: smooth -> threshold -> fill holes -> watershed split touching nuclei
smoothed = filters.gaussian(nuclei, sigma=2)
binary = smoothed > filters.threshold_otsu(smoothed)
binary = ndi.binary_fill_holes(binary)
binary = morphology.remove_small_objects(binary, max_size=999)

distance = ndi.distance_transform_edt(binary)
coords = feature.peak_local_max(distance, min_distance=15, labels=binary)
mask = np.zeros(distance.shape, dtype=bool)
mask[tuple(coords.T)] = True
markers, _ = ndi.label(mask)
labels = segmentation.watershed(-distance, markers, mask=binary)
labels = morphology.remove_small_objects(labels, max_size=499).astype(np.int32)

viewer = napari.Viewer()
viewer.add_image(
    membranes, name='membranes', colormap='green', blending='additive'
)
viewer.add_image(nuclei, name='nuclei', colormap='blue', blending='additive')
viewer.add_labels(labels, name='nuclei segmentation')
napari.run()
