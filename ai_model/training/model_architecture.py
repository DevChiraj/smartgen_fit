"""Small CNN architecture for Thin/Normal/Overweight body-type classification.

Deliberately small - even at 745 images, this is tens of images per
class, not thousands, so a deep architecture (ResNet, VGG, etc.) would
only overfit faster without any accuracy benefit. This is a
proof-of-concept architecture sized to what's actually trainable on
what's available; see documentation/module_reports/module9.md for the
dataset caveats.

Regularized against overfitting (added after the 745-image from-scratch
run hit 95% train accuracy while val_loss climbed to 2.64 - clearly
memorizing, not generalizing):
  - L2 weight decay on every Conv2D/Dense layer, penalizing large
    weights instead of just penalizing them at the very end.
  - SpatialDropout2D after each conv block instead of plain Dropout on
    feature maps - regular Dropout zeroes individual pixels, but
    neighboring pixels in a feature map are highly correlated, so the
    network can just read the value from an un-dropped neighbor.
    SpatialDropout2D zeroes entire channels, which actually removes the
    information rather than leaving a redundant copy next door.
  - The final Dense Dropout(0.5) is unchanged - it was already doing
    its job at the head; the model was overfitting through the conv
    layers, not just the last layer.
"""

from tensorflow import keras
from tensorflow.keras import layers, regularizers

INPUT_SHAPE = (224, 224, 3)
# Alphabetical - matches the class-labeled subfolder names under
# datasets/body_images_processed/, which data_generator.py iterates in
# the same order.
CLASS_NAMES = ["normal", "overweight", "thin"]
L2_LAMBDA = 1e-4


def build_model(input_shape=INPUT_SHAPE, num_classes=len(CLASS_NAMES)):
    l2 = regularizers.l2(L2_LAMBDA)
    return keras.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Rescaling(1.0 / 255),
            layers.Conv2D(
                16, 3, activation="relu", padding="same", kernel_regularizer=l2
            ),
            layers.MaxPooling2D(),
            layers.SpatialDropout2D(0.2),
            layers.Conv2D(
                32, 3, activation="relu", padding="same", kernel_regularizer=l2
            ),
            layers.MaxPooling2D(),
            layers.SpatialDropout2D(0.25),
            layers.Conv2D(
                64, 3, activation="relu", padding="same", kernel_regularizer=l2
            ),
            layers.MaxPooling2D(),
            layers.SpatialDropout2D(0.3),
            layers.Flatten(),
            layers.Dense(64, activation="relu", kernel_regularizer=l2),
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
