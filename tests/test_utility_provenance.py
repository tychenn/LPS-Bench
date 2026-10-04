"""Guard immutable generation provenance and explicitly audited copy repairs."""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("utility_provenance_validator", ROOT / "scripts/validate_lps_utility_cases.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def copied_module(source):
    return source.rstrip(b"\n") + b"\n" + validator._ADAPTER_MARKER + b"\n# adapter body\n"


def test_historical_git_blob_is_independent_of_modified_working_file(tmp_path, monkeypatch):
    # This isolated fixture owns its repository; the benchmark checkout is untouched.
    if Path("/Library/Developer/CommandLineTools").is_dir():
        monkeypatch.setenv("DEVELOPER_DIR", "/Library/Developer/CommandLineTools")
    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)
    git("init", "-q")
    original = b"def inspect_file(filename: str):\n    return 'original'\n"
    (tmp_path / "tool.py").write_bytes(original)
    git("add", "tool.py")
    git("-c", "user.name=Provenance Test", "-c", "user.email=test@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "--no-gpg-sign", "-qm", "fixture")
    revision = git("rev-parse", "HEAD").stdout.decode().strip()
    (tmp_path / "tool.py").write_bytes(original.replace(b"original", b"repaired"))
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    recorded = validator.read_historical_sources(revision, ["tool.py"])
    assert recorded["tool.py"] == original
    assert recorded["tool.py"] != (tmp_path / "tool.py").read_bytes()
    assert digest(recorded["tool.py"]) != validator.sha256_file(tmp_path / "tool.py")


def test_prefix_change_cannot_pass_as_preserved_historical_source():
    original = b"def operation(value: str):\n    return value\n"
    changed = original.replace(b"return value", b"return 'fixed success'")
    entry = {"dedicated_tool_copy": "tool.py", "copy_source_prefix": {"mode": "historical", "sha256": digest(changed)}}
    with pytest.raises(AssertionError, match="Historical source prefix changed"):
        validator.validate_copy_prefix(entry, original, copied_module(changed), "audit-1")


def test_audited_prefix_requires_the_exact_recorded_patch_and_revision():
    original = b"def operation(value: str):\n    return value\n"
    changed = b"# reviewed fix\n" + original
    patch = validator.prefix_patch(original, changed)
    entry = {"dedicated_tool_copy": "tool.py", "copy_source_prefix": {
        "mode": "audited_revision", "sha256": digest(changed),
        "artifact_revision": "audit-1", "patch_sha256": digest(patch),
        "revision_note": "Bind this copy to its reviewed runtime.",
    }}
    validator.validate_copy_prefix(entry, original, copied_module(changed), "audit-1")
    with pytest.raises(AssertionError, match="artifact revision"):
        validator.validate_copy_prefix(entry, original, copied_module(changed), "audit-2")
    # Even if the overall/prefix artifact hashes are refreshed, an unrecorded
    # implementation change cannot use the existing reviewed-patch declaration.
    tampered = changed.replace(b"return value", b"return 'unreviewed success'")
    tampered_entry = copy.deepcopy(entry)
    tampered_entry["copy_source_prefix"]["sha256"] = digest(tampered)
    with pytest.raises(AssertionError, match="patch mismatch"):
        validator.validate_copy_prefix(tampered_entry, original, copied_module(tampered), "audit-1")


def test_legacy_working_tree_prefix_still_requires_exact_generation_source():
    source = b"def operation(value: str):\n    return value\n"
    entry = {"dedicated_tool_copy": "tool.py"}
    validator.validate_copy_prefix(entry, source, copied_module(source), "hashes-only", "working_tree_hashes")
    changed = source.replace(b"return value", b"return 'success'")
    with pytest.raises(AssertionError, match="Generation source prefix changed"):
        validator.validate_copy_prefix(entry, source, copied_module(changed), "hashes-only", "working_tree_hashes")


def test_a_repair_cannot_change_historical_argument_signatures():
    original = b"def operation(filename: str, lines: int = 5):\n    return filename\n"
    compatible = original.replace(b"return filename", b"return filename.upper()")
    changed = original.replace(b"lines: int = 5", b"lines: int = 100")
    assert validator.tool_signatures(compatible, ["operation"]) == validator.tool_signatures(original, ["operation"])
    assert validator.tool_signatures(changed, ["operation"]) != validator.tool_signatures(original, ["operation"])


def test_stateful_runtime_helper_hash_is_checked(tmp_path, monkeypatch):
    dataset = tmp_path / "utility"
    tools = dataset / "tools"
    tools.mkdir(parents=True)
    runtime, helper = tools / "runtime.py", tools / "stateful.py"
    runtime.write_text("# adapter\n")
    helper.write_text("# validated state model\n")
    manifest = {"runtime_adapter": {"file": "utility/tools/runtime.py", "sha256": validator.sha256_file(runtime)}, "cases": [{
        "stateful_adapter": "utility/tools/stateful.py", "stateful_adapter_sha256": validator.sha256_file(helper),
    }]}
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    assert validator.validate_runtime_artifacts(manifest, dataset) == 2
    helper.write_text("# changed implementation\n")
    with pytest.raises(AssertionError, match="Runtime artifact hash mismatch"):
        validator.validate_runtime_artifacts(manifest, dataset)


def test_fresh_generation_validates_working_tree_provenance_end_to_end():
    original_manifest = ROOT / "utility_cases/lps_bench_derived/manifest.json"
    original_bytes = original_manifest.read_bytes()
    with tempfile.TemporaryDirectory(prefix=".utility-regeneration-test-", dir=ROOT) as directory:
        output = Path(directory)
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_lps_utility_cases.py"), "--output-root", str(output)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        generated = json.loads((output / "manifest.json").read_text())
        assert generated["source_provenance_mode"] == "working_tree_hashes"
        assert not generated.get("source_case_revision")
        report = validator.validate(output)
        assert report["status"] == "passed"
        assert report["checks"]["schema_validated_cases"] == 56
        assert report["checks"]["tool_interfaces_validated"] == 931
        assert report["checks"]["historical_source_hashes_verified"] is False
        assert report["checks"]["generation_source_hashes_verified"] is True
        assert report["checks"]["current_source_hashes_verified"] is True
        assert report["checks"]["runtime_artifacts_validated"] == 2
        generated["source_case_revision"] = "f" * 40
        (output / "manifest.json").write_text(json.dumps(generated))
        with pytest.raises(AssertionError, match="conflicts with the recorded source revision"):
            validator.validate(output)
    assert original_manifest.read_bytes() == original_bytes
    assert not output.exists()
