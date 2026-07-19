from PIL import Image

from model_architecture import CLASS_NAMES, build_model, compile_model
from predict import predict_body_type


def _make_throwaway_model(tmp_path):
    """Builds and saves a tiny untrained model so the test exercises the
    real pipeline (load -> detect -> crop -> denoise -> normalize ->
    resize -> predict) without depending on the real trained artifact,
    which is a gitignored binary that may not exist on a fresh clone."""
    model = compile_model(build_model())
    model_path = tmp_path / "throwaway.keras"
    model.save(model_path)
    return model_path


def _make_test_image(tmp_path):
    path = tmp_path / "test.jpg"
    Image.new("RGB", (300, 500), color=(180, 140, 120)).save(path)
    return path


def test_predict_body_type_returns_valid_label_and_confidence(tmp_path):
    model_path = _make_throwaway_model(tmp_path)
    image_path = _make_test_image(tmp_path)

    label, confidence = predict_body_type(str(image_path), str(model_path))

    assert label in CLASS_NAMES
    assert 0.0 <= confidence <= 1.0


def test_predict_body_type_caches_loaded_model(tmp_path, monkeypatch):
    import predict as predict_module

    model_path = _make_throwaway_model(tmp_path)
    image_path = _make_test_image(tmp_path)
    predict_module._model_cache.clear()

    load_calls = []
    original_load_model = predict_module.keras.models.load_model

    def counting_load_model(path):
        load_calls.append(path)
        return original_load_model(path)

    monkeypatch.setattr(predict_module.keras.models, "load_model", counting_load_model)

    predict_body_type(str(image_path), str(model_path))
    predict_body_type(str(image_path), str(model_path))

    assert len(load_calls) == 1
