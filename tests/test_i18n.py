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


# ---------------------------------------------------------------------------
# i18n Edge Cases
# ---------------------------------------------------------------------------

class TestI18nEdgeCases:
    """Edge case tests for i18n/translation system."""

    def test_missing_key_in_all_languages_returns_default(self):
        """Missing key with no fallback available should return default."""
        t = Translator("en")
        result = t.get("completely_nonexistent_key_xyz_123")
        assert result == ""  # Default is empty string

    def test_missing_key_custom_default(self):
        """Missing key should return custom default if provided."""
        t = Translator("en")
        result = t.get("nonexistent_key_abc", "custom_fallback")
        assert result == "custom_fallback"

    def test_key_with_variable_placeholder_no_variable_provided(self):
        """Key with %(variable)s but no variable provided should not crash."""
        t = Translator("en")
        # about_version_info often contains version placeholders
        result = t.get("about_version_info")
        # Should return the string with placeholder intact or formatted
        assert isinstance(result, str)

    def test_emoji_characters_in_translations(self):
        """Keys with emoji characters should work correctly."""
        t = Translator("en")
        # Test that emoji-containing keys (if any) don't break things
        # Also verify we can handle translations containing emoji
        for lang in SUPPORTED_LANGS:
            t.set_language(lang)
            # All values should be retrievable without error
            for key in TRANSLATIONS[lang]:
                value = t.get(key)
                assert isinstance(value, (str, list))

    def test_very_long_translation_strings(self):
        """Very long translation strings (1000+ chars) should work."""
        t = Translator("en")
        # Find the longest translation in each language
        for lang in SUPPORTED_LANGS:
            t.set_language(lang)
            for key, value in TRANSLATIONS[lang].items():
                if isinstance(value, str) and len(value) > 100:
                    result = t.get(key)
                    assert result == value
                    assert len(result) > 100

    def test_none_key_returns_default(self):
        """None as key should return default without crashing."""
        t = Translator("en")
        try:
            result = t.get(None, "fallback")
            # Should return fallback or handle gracefully
            assert result == "fallback" or result == ""
        except (TypeError, AttributeError):
            pass  # Also acceptable to raise

    def test_empty_string_key_returns_default(self):
        """Empty string as key should return default."""
        t = Translator("en")
        result = t.get("", "fallback")
        assert result == "fallback"

    def test_key_with_special_characters(self):
        """Keys with special characters should be handled."""
        t = Translator("en")
        # Test that special character keys don't crash
        weird_keys = ["key with spaces", "key\twith\ttabs", "key\nwith\nnewlines"]
        for key in weird_keys:
            result = t.get(key, "default")
            assert result == "default"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGS)
    def test_all_string_values_non_empty_after_strip(self, lang):
        """All string translation values should be non-empty after stripping."""
        for key, value in TRANSLATIONS[lang].items():
            if isinstance(value, str):
                assert value.strip(), f"'{lang}'.'{key}' is empty or whitespace-only"

    def test_callable_with_none_key(self):
        """Calling translator(None) should handle gracefully."""
        t = Translator("en")
        try:
            result = t(None, "fb")
            assert result == "fb" or result == ""
        except (TypeError, AttributeError):
            pass  # Also acceptable

    def test_get_list_translation_intact(self):
        """List-type translations should be returned intact."""
        t = Translator("en")
        for key, value in TRANSLATIONS["en"].items():
            if isinstance(value, list):
                result = t.get(key)
                assert result == value
                assert isinstance(result, list)
                break  # Found and tested one list
