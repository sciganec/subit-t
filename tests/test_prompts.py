"""Tests for assistant prompt profiles."""

from subit_t.prompts import build_assistant_extra, get_assistant_profile, list_assistants


def test_list_assistants_contains_expected_profiles():
    assistants = set(list_assistants())
    assert {"general", "review", "research", "incident", "planner", "coding"} <= assistants


def test_get_assistant_profile_falls_back_to_general():
    profile = get_assistant_profile("does-not-exist")
    assert profile.name == "general"


def test_build_assistant_extra_contains_profile_instructions():
    extra = build_assistant_extra("review")
    assert "Assistant profile: Code Review Assistant" in extra
    assert "Prioritize findings over summaries." in extra
