from model_architecture import CLASS_NAMES, INPUT_SHAPE, build_model, compile_model


def test_build_model_input_shape():
    model = build_model()
    assert model.input_shape == (None,) + INPUT_SHAPE


def test_build_model_output_units_match_class_count():
    model = build_model()
    assert model.output_shape == (None, len(CLASS_NAMES))


def test_compile_model_sets_optimizer_and_loss():
    model = compile_model(build_model())
    assert model.optimizer is not None
    assert model.loss == "sparse_categorical_crossentropy"
