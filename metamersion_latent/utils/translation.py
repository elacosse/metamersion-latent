import os

import deepl


def translate(text: str, language: str = "PT") -> str:
    translator = deepl.Translator(os.getenv("DEEPL_API_KEY"))
    result = translator.translate_text("Hello, world!", target_lang=language)
    return result.text
