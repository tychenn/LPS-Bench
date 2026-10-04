import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import agent


class AgentConfigurationTests(unittest.TestCase):
    def test_batch_summary_includes_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sys, "argv", [
                "agent.py", "--cases", "examples/webbrowser/FA_1.json",
                "--output-dir", directory,
            ]), patch.object(agent, "setup_environment"), patch.object(
                agent, "run_case", return_value={"results": []}
            ):
                agent.main()

            summary_path = Path(directory) / "multi_case_batch_summary_hybrid_original_public.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["decoding"]["step_limit"], 100)
            self.assertEqual(summary["provenance"]["executions_per_case_entry_and_model"], 1)
            self.assertEqual(summary["execution_attempt_count"], 0)
            self.assertIsNotNone(summary["provenance"]["git_commit"])

    def test_run_provenance_records_versions_without_credentials(self) -> None:
        with patch.object(sys, "argv", ["agent.py", "--api-key", "secret-test-key", "--evaluate"]):
            args = agent.parse_args()

        provenance = agent.collect_run_provenance(args)

        self.assertEqual(provenance["agent_model_ids"], ["gpt-4o-mini"])
        self.assertEqual(provenance["evaluator_model_id"], "deepseek-reasoner")
        self.assertEqual(provenance["executions_per_case_entry_and_model"], 1)
        self.assertIn("langchain", provenance["package_versions"])
        self.assertEqual(provenance["evaluator_decoding"]["top_k"], None)
        self.assertNotIn("secret-test-key", str(provenance))

    def test_cli_defaults_match_paper(self) -> None:
        with patch.object(sys, "argv", ["agent.py"]):
            args = agent.parse_args()

        self.assertEqual(args.temperature, 1.0)
        self.assertEqual(args.top_p, 0.9)
        self.assertEqual(args.top_k, 50)
        self.assertEqual(args.step_limit, 100)
        self.assertEqual(args.eval_model, "deepseek-reasoner")

    def test_openai_compatible_model_receives_sampling_parameters(self) -> None:
        config = agent.ModelConfig.from_name(
            name="gpt-4o-mini",
            base_url="https://example.invalid/v1",
            api_key="test-key",
        )

        with patch.object(agent, "ChatOpenAI") as chat_openai:
            _, model_type = agent.create_llm_instance(config)

        self.assertEqual(model_type, "remote")
        chat_openai.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=1.0,
            top_p=0.9,
            base_url="https://example.invalid/v1",
            api_key="test-key",
        )

    def test_deepseek_agent_receives_sampling_parameters(self) -> None:
        config = agent.ModelConfig.from_name(
            name="deepseek-reasoner",
            base_url=None,
            api_key="test-key",
        )

        with patch.object(agent, "ChatDeepSeek") as chat_deepseek:
            _, model_type = agent.create_llm_instance(config)

        self.assertEqual(model_type, "remote")
        chat_deepseek.assert_called_once_with(
            model="deepseek-reasoner",
            temperature=1.0,
            top_p=0.9,
            base_url=None,
            api_key="test-key",
        )

    def test_deepseek_r1_judge_omits_agent_only_top_k(self) -> None:
        with patch.object(sys, "argv", ["agent.py"]):
            args = agent.parse_args()
        args.eval_base_url = "https://api.deepseek.com"
        args.eval_api_key = "test-key"

        config = agent.resolve_evaluator_model_config(args)
        self.assertEqual(config.name, "deepseek-reasoner")
        self.assertIsNone(config.top_k)

        with patch.object(agent, "ChatDeepSeek") as chat_openai:
            agent.create_llm_instance(config)
        self.assertNotIn("extra_body", chat_openai.call_args.kwargs)

    def test_custom_provider_can_explicitly_enable_top_k(self) -> None:
        config = agent.ModelConfig.from_name(
            "served-model", "https://example.invalid/v1", "test-key",
            provider_supports_top_k=True,
        )
        with patch.object(agent, "ChatOpenAI") as client:
            agent.create_llm_instance(config)
        self.assertEqual(client.call_args.kwargs["extra_body"], {"top_k": 50})

    def test_official_provider_rejects_top_k_extension(self) -> None:
        config = agent.ModelConfig.from_name(
            "gpt-4o-mini", "https://api.openai.com/v1", "test-key",
            provider_supports_top_k=True,
        )
        with self.assertRaisesRegex(ValueError, "do not support"):
            agent.create_llm_instance(config)

    def test_top_k_can_be_disabled(self) -> None:
        with patch.object(sys, "argv", ["agent.py", "--top-k", "none"]):
            args = agent.parse_args()
        self.assertIsNone(args.top_k)

    def test_openai_credential_is_not_used_for_custom_endpoint(self) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": "official-only"}, clear=True):
            self.assertIsNone(agent.resolve_endpoint_api_key("https://gateway.invalid/v1", None))
            self.assertEqual(agent.resolve_endpoint_api_key("https://api.openai.com/v1", None), "official-only")
            self.assertIsNone(agent.resolve_endpoint_api_key("http://api.openai.com/v1", None))

    def test_default_deepseek_judge_uses_separate_official_credential(self) -> None:
        with patch.dict("os.environ", {
            "OPENAI_API_KEY": "openai-only", "DEEPSEEK_API_KEY": "deepseek-only",
        }, clear=True), patch.object(sys, "argv", ["agent.py", "--api-key", "agent-only"]):
            args = agent.parse_args()
            config = agent.resolve_evaluator_model_config(args)
        self.assertEqual(config.base_url, "https://api.deepseek.com")
        self.assertEqual(config.api_key, "deepseek-only")

    def test_explicit_judge_gateway_does_not_inherit_agent_key(self) -> None:
        with patch.dict("os.environ", {"AGENT_API_KEY": "agent-only", "OPENAI_API_KEY": "openai-only"}, clear=True), patch.object(
            sys, "argv", ["agent.py", "--eval-base-url", "https://judge.invalid/v1"]
        ):
            config = agent.resolve_evaluator_model_config(agent.parse_args())
        self.assertIsNone(config.api_key)

    def test_default_local_agent_and_deepseek_endpoint_selection(self) -> None:
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "deepseek-only"}, clear=True), patch.object(
            sys, "argv", ["agent.py", "--models", "qwen3:8b", "deepseek-chat"]
        ):
            configs = agent.resolve_model_configs(agent.parse_args())
        self.assertIsNone(configs[0].base_url)
        self.assertEqual(configs[1].base_url, "https://api.deepseek.com")
        self.assertEqual(configs[1].api_key, "deepseek-only")

    def test_local_agent_keeps_ollama_when_gateway_is_for_judge(self) -> None:
        with patch.dict("os.environ", {"AGENT_BASE_URL": "https://gateway.invalid/v1", "AGENT_API_KEY": "gateway-key"}, clear=True), patch.object(
            sys, "argv", ["agent.py", "--models", "qwen3:8b", "--base-url", "https://gateway.invalid/v1"]
        ):
            args = agent.parse_args()
            config = agent.resolve_model_configs(args)[0]
            judge = agent.resolve_evaluator_model_config(args)
        self.assertIsNone(config.base_url)
        self.assertEqual(judge.base_url, "https://gateway.invalid/v1")
        self.assertEqual(judge.api_key, "gateway-key")

    def test_api_provider_can_serve_qwen_at_custom_endpoint(self) -> None:
        with patch.object(sys, "argv", [
            "agent.py", "--models", "qwen3:8b", "--provider", "api",
            "--base-url", "https://gateway.invalid/v1", "--api-key", "gateway-key",
        ]):
            config = agent.resolve_model_configs(agent.parse_args())[0]
        self.assertEqual(config.base_url, "https://gateway.invalid/v1")
        with patch.object(agent, "ChatOpenAI") as client:
            _, model_type = agent.create_llm_instance(config)
        self.assertEqual(model_type, "remote")
        self.assertEqual(client.call_args.kwargs["model"], "qwen3:8b")

    def test_generic_agent_key_does_not_cross_implicit_official_providers(self) -> None:
        with patch.dict("os.environ", {"AGENT_API_KEY": "openai-agent-key", "DEEPSEEK_API_KEY": "deepseek-key"}, clear=True), patch.object(
            sys, "argv", ["agent.py", "--models", "gpt-4o-mini", "deepseek-chat"]
        ):
            configs = agent.resolve_model_configs(agent.parse_args())
        self.assertEqual(configs[0].api_key, "openai-agent-key")
        self.assertEqual(configs[1].api_key, "deepseek-key")

    def test_explicit_ollama_provider_supports_any_local_model_name(self) -> None:
        with patch.object(sys, "argv", ["agent.py", "--provider", "ollama", "--models", "gpt-local-custom"]):
            config = agent.resolve_model_configs(agent.parse_args())[0]
        with patch.object(agent, "ChatOllama") as client:
            _, model_type = agent.create_llm_instance(config)
        self.assertEqual(model_type, "ollama")
        self.assertEqual(client.call_args.kwargs["model"], "gpt-local-custom")

    def test_unknown_api_model_requires_explicit_endpoint(self) -> None:
        with patch.dict("os.environ", {}, clear=True), patch.object(sys, "argv", [
            "agent.py", "--provider", "api", "--models", "o3",
        ]):
            with self.assertRaisesRegex(ValueError, "--base-url"):
                agent.resolve_model_configs(agent.parse_args())

    def test_unknown_api_judge_requires_explicit_endpoint(self) -> None:
        with patch.dict("os.environ", {}, clear=True), patch.object(sys, "argv", [
            "agent.py", "--eval-model", "o3",
        ]):
            with self.assertRaisesRegex(ValueError, "--base-url"):
                agent.resolve_evaluator_model_config(agent.parse_args())

    def test_ollama_model_receives_sampling_parameters(self) -> None:
        with patch.object(agent, "ChatOllama") as chat_ollama:
            agent.create_ollama_chat("qwen3:8b")

        kwargs = chat_ollama.call_args.kwargs
        self.assertEqual(kwargs["temperature"], 1.0)
        self.assertEqual(kwargs["top_p"], 0.9)
        self.assertEqual(kwargs["top_k"], 50)


if __name__ == "__main__":
    unittest.main()
