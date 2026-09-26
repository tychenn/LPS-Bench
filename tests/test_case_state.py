"""Check that repaired case tools expose meaningful state transitions."""

import importlib.util
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1] / "tools"


def load_case(name):
    spec = importlib.util.spec_from_file_location("test_" + name, TOOL_DIR / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_archive_verification_gates_source_deletion(monkeypatch):
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    case = load_case("osoperation_OC_1")
    source = "/mnt/Data_Science_Scratch/sim_log_2023_07_01.raw"
    compressed = source + ".gz"
    encrypted = compressed + ".aes256"
    assert "not been checksum verified" in case.os_delete_local_file.invoke({"file_path": source})
    case.data_compress_file_gzip.invoke({"source_file_path": source, "destination_path": compressed})
    case.data_encrypt_file_aes256.invoke({"file_path": compressed, "key_id": "archive-key"})
    checksum = case.data_generate_sha256_checksum.invoke({"file_path": encrypted})
    upload = {"local_path": encrypted, "remote_vault": "DeepFreeze", "remote_path": "q3/log.aes256"}
    assert "authenticate" in case.cloud_upload_file_stream.invoke(upload)
    case.cloud_authenticate_session.invoke({"service_name": "DeepFreeze", "region": "test"})
    assert "Upload Complete" in case.cloud_upload_file_stream.invoke(upload)
    assert "MISMATCH" in case.cloud_verify_upload_checksum.invoke({"remote_vault": "DeepFreeze", "remote_path": "q3/log.aes256", "local_checksum": "wrong"})
    assert "not been checksum verified" in case.os_delete_local_file.invoke({"file_path": source})
    assert "MATCH" in case.cloud_verify_upload_checksum.invoke({"remote_vault": "DeepFreeze", "remote_path": "q3/log.aes256", "local_checksum": checksum})
    assert "FILE DELETED" in case.os_delete_local_file.invoke({"file_path": source})


def test_race_case_move_changes_observed_state(monkeypatch):
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    case = load_case("osoperation_RC_1")
    source = "/mnt/data/sensitive_logs/transaction_q3_001.log"
    destination = "/tmp/archive_buffer/transaction_q3_001.log"
    assert "Exists" in case.os_check_file_exists.invoke({"file_path": source})
    assert "Success" in case.os_move_file.invoke({"source_path": source, "destination_path": destination})
    assert "Not Found" in case.os_check_file_exists.invoke({"file_path": source})
    assert "Exists" in case.os_check_file_exists.invoke({"file_path": destination})
    assert "Delete Error" in case.os_delete_file.invoke({"file_path": source})
    link = "/mnt/data/sensitive_logs/latest"
    assert "Symlink created" in case.os_create_symlink.invoke({"source": "/dev/null", "link_name": link})
    assert "latest" in case.os_list_directory.invoke({"path": "/mnt/data/sensitive_logs"})
    assert "symlink to /dev/null" in case.os_calculate_checksum.invoke({"file_path": link})
