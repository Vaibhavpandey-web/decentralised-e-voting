import numpy as np
from PIL import Image

# 1. Load the .npy file
array = np.load('63.npy')

# 2. Normalize the array if necessary (Important!)
# If your array consists of floats from 0.0 to 1.0:
if array.dtype != np.uint8:
    # Scale to 0-255 and convert to uint8
    array = (255 * (array - np.min(array)) / np.ptp(array)).astype(np.uint8)

# 3. Convert the NumPy array to a Pillow Image object
# If the image is RGB, Pillow handles (H, W, 3) automatically.
# If grayscale, it handles (H, W).
image = Image.fromarray(array)

# 4. Save as JPG
image.save('output_image.jpg')
print("Successfully saved as output_image.jpg")