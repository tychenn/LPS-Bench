"""Exercise generation contracts without constructing API clients."""
import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import agent

SOURCE = Path(__file__).resolve().parents[1] / "multi-agent_pipeline.py"
spec = importlib.util.spec_from_file_location("generation_pipeline_under_test", SOURCE)
pipeline = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pipeline
spec.loader.exec_module(pipeline)


def draft(filename="noop.py"):
    return {"merged": {
        "case": {"instruction": "Read confirmed target", "MCP": {"file": filename, "tools": ["noop"]},
                 "evaluator": {"file": "false_assumption.py", "criterion": "Preserve target"}},
        "artifacts": {"mcp_file": {"filename": filename, "content_py": 'def noop():\n    return "ok"\n'}},
    }}


def make_pipeline(tmp_path, approved):
    obj = pipeline.MultiAgentPipeline.__new__(pipeline.MultiAgentPipeline)
    obj.pipeline_config = pipeline.PipelineConfig(max_iterations=1)
    obj.artifact_dir = tmp_path / "artifacts" / "mcp_files"
    obj.repository = pipeline.CaseRepository(str(tmp_path / "approved_cases"))
    def evaluate(reviewed):
        assert "content_py" in reviewed["artifacts"]["mcp_file"]
        assert not obj.artifact_dir.exists()
        return approved, "reviewed"
    obj.evaluator = SimpleNamespace(evaluate=evaluate)
    obj._execute_round = lambda *args: ({}, {}, {}, {}, None, draft())
    return obj


def test_raw_json_and_python_fence_are_parsed_separately():
    metadata = {"MCP": {"file": "noop.py", "tools": ["noop"]}}
    raw = json.dumps(metadata) + '\n\n```python\ndef noop():\n    return "ok"\n```'
    parsed, code = pipeline.extract_json_and_code(raw)
    assert parsed == metadata
    assert "def noop" in code


@pytest.mark.parametrize("filename", ["../../agent.py", "/tmp/agent.py", "folder/agent.py", "..\\agent.py"])
def test_generated_filename_cannot_escape_artifact_directory(tmp_path, filename):
    obj = pipeline.MultiAgentPipeline.__new__(pipeline.MultiAgentPipeline)
    obj.artifact_dir = tmp_path / "artifacts"
    with pytest.raises(ValueError, match="basename"):
        obj._persist_artifacts(draft(filename))
    assert not obj.artifact_dir.exists()


def test_rejected_draft_never_writes_python_source(tmp_path):
    obj = make_pipeline(tmp_path, False)
    result = obj.run("template")
    assert result["status"] == "max_iterations_reached"
    assert not list(tmp_path.rglob("*.py"))


def test_approved_export_loads_with_runner_and_preserves_previous_artifacts(tmp_path):
    obj = make_pipeline(tmp_path, True)
    result = obj.run("template")
    case_path = obj.repository.storage_dir / f'case_{result["case_id"]}.json'
    exported = agent.load_case(case_path)
    assert "case" not in exported
    assert exported["instruction"] == "Read confirmed target"
    first = agent.load_tools_from_mcp_config(exported["MCP"], case_path=case_path)[0]
    assert first() == "ok"
    previous_files = list(obj.artifact_dir.glob("*.py"))
    assert len(previous_files) == 1
    fresh = obj._persist_artifacts(copy.deepcopy(draft()), obj.repository.storage_dir)
    assert len(list(obj.artifact_dir.glob("*.py"))) == 2
    assert fresh["merged"]["case"]["MCP"]["file"] != exported["MCP"]["file"]
    assert first() == "ok"
