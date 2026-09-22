import sys
import unittest
from unittest.mock import patch

import agent


class AgentConfigurationTests(unittest.TestCase):
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
            extra_body={"top_k": 50},
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
            extra_body={"top_k": 50},
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

        with patch.object(agent, "ChatOpenAI") as chat_openai:
            agent.create_llm_instance(config)
        self.assertNotIn("extra_body", chat_openai.call_args.kwargs)

    def test_ollama_model_receives_sampling_parameters(self) -> None:
        with patch.object(agent, "ChatOllama") as chat_ollama:
            agent.create_ollama_chat("qwen3:8b")

        kwargs = chat_ollama.call_args.kwargs
        self.assertEqual(kwargs["temperature"], 1.0)
        self.assertEqual(kwargs["top_p"], 0.9)
        self.assertEqual(kwargs["top_k"], 50)


if __name__ == "__main__":
    unittest.main()
