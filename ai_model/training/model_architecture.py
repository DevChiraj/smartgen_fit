"""Small CNN architecture for Thin/Normal/Overweight body-type classification.

Deliberately small - the current dataset is tens of images, not
thousands, so a deep architecture (ResNet, VGG, etc.) would only
overfit faster without any accuracy benefit. This is a proof-of-concept
architecture sized to what's actually trainable on what's available;
see documentation/module_reports/module9.md for the dataset caveats.
"""

from tensorflow import keras
from tensorflow.keras import layers

INPUT_SHAPE = (224, 224, 3)
# Alphabetical - matches the class-labeled subfolder names under
# datasets/body_images_processed/, which data_generator.py iterates in
# the same order.
CLASS_NAMES = ["normal", "overweight", "thin"]


def build_model(input_shape=INPUT_SHAPE, num_classes=len(CLASS_NAMES)):
    return keras.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Rescaling(1.0 / 255),
            layers.Conv2D(16, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation="softmax"),
        ],
        name="smartgen_fit_body_type_cnn",
    )


def compile_model(model, learning_rate=1e-3):
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
