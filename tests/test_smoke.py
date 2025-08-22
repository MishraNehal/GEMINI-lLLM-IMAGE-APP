def test_imports():
    import importlib
    for m in ["services.gemini_client", "utils.env", "utils.image_utils"]:
        importlib.import_module(m)