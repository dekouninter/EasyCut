# -*- coding: utf-8 -*-
"""Tests for i18n.py — Translation engine and Translator class."""

import pytest
from i18n import Translator, TRANSLATIONS, translator
from __version__ import __version__

SUPPORTED_LANGS = ["en", "pt", "es", "fr", "de", "it", "ja"]

# Keys that MUST exist in every language
REQUIRED_KEYS = [
    "app_title", "version", "tab_download", "tab_batch", "tab_live",
    "tab_following", "tab_history", "tab_settings", "tab_about",
    "msg_error", "msg_warning", "msg_success",
    "download_btn", "download_stop",
    "status_ready", "status_downloading",
    "about_version_info",
]


class TestTranslationsDict:
    def test_translations_is_dict(self):
        assert isinstance(TRANSLATIONS, dict)

    def test_all_7_languages_present(self):
        for lang in SUPPORTED_LANGS:
            assert lang in TRANSLATIONS, f"Language '{lang}' missing"

    def test_no_extra_languages(self):
        for lang in TRANSLATIONS:
            assert lang in SUPPORTED_LANGS, f"Unexpected language '{lang}'"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_language_is_dict(self, lang):
        assert isinstance(TRANSLATIONS[lang], dict)

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_language_not_empty(self, lang):
        assert len(TRANSLATIONS[lang]) > 100, \
            f"Language '{lang}' has only {len(TRANSLATIONS[lang])} keys"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    @pytest.mark.parametrize("key", REQUIRED_KEYS)
    def test_required_key_exists(self, lang, key):
        assert key in TRANSLATIONS[lang], \
            f"Key '{key}' missing in language '{lang}'"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_all_values_are_strings_or_lists(self, lang):
        for key, value in TRANSLATIONS[lang].items():
            assert isinstance(value, (str, list)), \
                f"'{lang}'.'{key}' is {type(value).__name__}, expected str or list"

    def test_key_consistency_across_languages(self):
        """All languages should have the same set of keys."""
        en_keys = set(TRANSLATIONS["en"].keys())
        for lang in SUPPORTED_LANGS[1:]:
            lang_keys = set(TRANSLATIONS[lang].keys())
            missing = en_keys - lang_keys
            assert not missing, \
                f"Language '{lang}' missing keys: {missing}"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_no_empty_values(self, lang):
        """No translation value should be empty."""
        for key, value in TRANSLATIONS[lang].items():
            if isinstance(value, list):
                assert len(value) > 0, f"'{lang}'.'{key}' is empty list"
            else:
                assert value.strip(), f"'{lang}'.'{key}' is empty"


class TestTranslator:
    def test_default_language_is_english(self):
        t = Translator()
        assert t.language == "en"

    def test_set_valid_language(self):
        t = Translator("en")
        assert t.set_language("pt") is True
        assert t.language == "pt"

    def test_set_invalid_language(self):
        t = Translator("en")
        assert t.set_language("zz") is False
        assert t.language == "en"

    def test_invalid_init_language_falls_back_to_en(self):
        t = Translator("invalid")
        assert t.language == "en"

    def test_get_existing_key(self):
        t = Translator("en")
        result = t.get("app_title")
        assert result == "EasyCut"

    def test_get_missing_key_default(self):
        t = Translator("en")
        assert t.get("nonexistent_key_xyz") == ""

    def test_get_missing_key_custom_default(self):
        t = Translator("en")
        assert t.get("nonexistent_key_xyz", "fallback") == "fallback"

    def test_callable_syntax(self):
        t = Translator("en")
        assert t("app_title") == t.get("app_title")

    def test_callable_with_default(self):
        t = Translator("en")
        assert t("nonexistent_xyz", "fb") == "fb"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_each_language_has_app_title(self, lang):
        t = Translator(lang)
        title = t.get("app_title")
        assert title, f"Language '{lang}' app_title is empty"

    def test_version_injection(self):
        """After init, 'version' key matches __version__."""
        t = Translator("en")
        assert t.get("version") == __version__

    def test_version_injection_after_language_switch(self):
        t = Translator("en")
        t.set_language("pt")
        assert t.get("version") == __version__

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_version_injection_all_languages(self, lang):
        t = Translator(lang)
        assert t.get("version") == __version__

    def test_language_switch_changes_translations(self):
        t = Translator("en")
        en_value = t.get("tab_about")
        t.set_language("pt")
        pt_value = t.get("tab_about")
        # At minimum they should both be non-empty
        assert en_value and pt_value
        # They should differ ("About" vs "Sobre")
        assert en_value != pt_value


class TestGlobalTranslator:
    def test_global_instance_exists(self):
        assert translator is not None

    def test_global_instance_is_translator(self):
        assert isinstance(translator, Translator)

    def test_global_instance_callable(self):
        result = translator("app_title")
        assert isinstance(result, str)
