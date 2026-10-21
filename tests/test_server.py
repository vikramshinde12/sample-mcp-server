"""Unit tests for sample-mcp-server."""

import pytest
from sample_mcp_server.server import (
    app,
    calculate,
    get_system_info,
    analyze_text,
    add_note,
    list_notes,
    clear_notes,
    system_info_resource,
    all_notes_resource,
    code_review,
    summarize_notes,
)


def test_calculate_valid_expressions():
    assert "2 + 2 = 4" in calculate("2 + 2")
    assert "sqrt(16) = 4.0" in calculate("sqrt(16)")
    assert "3 * 4 + 5 = 17" in calculate("3 * 4 + 5")


def test_calculate_disallowed_tokens():
    with pytest.raises(ValueError, match="forbidden"):
        calculate("import os")

    with pytest.raises(ValueError, match="forbidden"):
        calculate("__import__('os').system('ls')")


def test_get_system_info():
    info = get_system_info()
    assert "platform" in info
    assert "system" in info
    assert "python_version" in info
    assert "utc_timestamp" in info


def test_analyze_text():
    sample = "Hello world! This is a test sentence. Let's count words."
    metrics = analyze_text(sample)
    assert metrics["word_count"] == 10
    assert metrics["sentence_count"] == 3
    assert metrics["character_count_total"] == len(sample)
    assert metrics["estimated_reading_time_minutes"] > 0

    empty_metrics = analyze_text("")
    assert empty_metrics["word_count"] == 0
    assert empty_metrics["character_count_total"] == 0


def test_notes_lifecycle():
    # Clear any previous notes
    clear_notes()
    assert len(list_notes()) == 0

    # Add notes
    msg1 = add_note("MCP Guide", "Model Context Protocol connects LLMs to tools.")
    assert "stored successfully" in msg1

    msg2 = add_note("TODO", "Publish repo to GitHub.")
    assert "stored successfully" in msg2

    notes = list_notes()
    assert len(notes) == 2
    assert notes[0]["title"] == "MCP Guide"

    # Test resource rendering
    resource_text = all_notes_resource()
    assert "MCP Guide" in resource_text
    assert "Model Context Protocol connects LLMs to tools." in resource_text

    # Clear notes
    clear_msg = clear_notes()
    assert "Cleared 2 notes" in clear_msg
    assert len(list_notes()) == 0


def test_system_info_resource():
    content = system_info_resource()
    assert "# System Info" in content
    assert "Platform:" in content


def test_prompts():
    prompt1 = code_review("def foo():\n    return 42\n", "python")
    assert "def foo():" in prompt1
    assert "thorough code review" in prompt1

    add_note("Project Vision", "Build extensible AI tooling.")
    prompt2 = summarize_notes()
    assert "Project Vision" in prompt2
    clear_notes()


@pytest.mark.asyncio
async def test_mcp_app_interface():
    # Verify app exposes tools and resources through MCP protocol interfaces
    tools = await app.list_tools()
    tool_names = {t.name for t in tools}
    assert "calculate" in tool_names
    assert "get_system_info" in tool_names
    assert "analyze_text" in tool_names
    assert "add_note" in tool_names
    assert "list_notes" in tool_names
    assert "clear_notes" in tool_names

    res = await app.call_tool("calculate", {"expression": "10 * 10"})
    assert "100" in str(res)
