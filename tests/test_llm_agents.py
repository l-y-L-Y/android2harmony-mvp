import json
import unittest

from android2harmony.llm_agents import LLMAgentRunner, LLMRefineOptions, enhance_artifact_with_llm, refine_arkui_page_with_llm


class LLMAgentRunnerTest(unittest.TestCase):
    def test_agent_runner_uses_llm_and_records_success(self):
        calls = []

        def fake_call(prompt: str, system: str, max_tokens: int) -> str:
            calls.append((prompt, system, max_tokens))
            return '{"agent":"ok","value":1}'

        runner = LLMAgentRunner(LLMRefineOptions(all_agents=True, max_agent_tokens=123), call_fn=fake_call)

        result = runner.run(
            agent_name="understanding-agent",
            prompt="input",
            system="system",
            fallback_content="{}",
            validator=lambda text: json.loads(text) is not None,
        )

        self.assertEqual(result, '{"agent":"ok","value":1}')
        self.assertEqual(len(calls), 1)
        self.assertEqual(runner.summary()["agents"][0]["status"], "used")
        self.assertEqual(runner.summary()["agents"][0]["model"], "mimo-v2.5-pro")

    def test_agent_runner_falls_back_when_llm_output_is_invalid(self):
        runner = LLMAgentRunner(
            LLMRefineOptions(all_agents=True),
            call_fn=lambda prompt, system, max_tokens: "not-json",
        )

        result = runner.run(
            agent_name="planning-agent",
            prompt="input",
            system="system",
            fallback_content='{"fallback":true}',
            validator=lambda text: json.loads(text) is not None,
        )

        self.assertEqual(result, '{"fallback":true}')
        record = runner.summary()["agents"][0]
        self.assertEqual(record["status"], "fallback")
        self.assertIn("validation failed", record["reason"])

    def test_agent_runner_retries_once_after_invalid_output(self):
        responses = iter(["", '{"ok":true}'])
        runner = LLMAgentRunner(
            LLMRefineOptions(all_agents=True),
            call_fn=lambda prompt, system, max_tokens: next(responses),
        )

        result = runner.run(
            agent_name="test-generation-agent",
            prompt="input",
            system="system",
            fallback_content="{}",
            validator=lambda text: json.loads(text) is not None,
        )

        self.assertEqual(result, '{"ok":true}')
        self.assertEqual(runner.summary()["agents"][0]["status"], "used")
        self.assertIn("after retry", runner.summary()["agents"][0]["reason"])

    def test_enhance_artifact_merges_json_review(self):
        runner = LLMAgentRunner(
            LLMRefineOptions(all_agents=True),
            call_fn=lambda prompt, system, max_tokens: '```json\n{"findings":["ok"],"risks":[],"recommendations":["keep rules"]}\n```',
        )

        result = enhance_artifact_with_llm(
            runner=runner,
            agent_name="api-mapping-agent",
            artifact_path="agent-workspace/02-planning/api-mapping.json",
            content='{"enhanced":false}',
            context="project context",
        )

        payload = json.loads(result)
        self.assertEqual(payload["enhanced"], False)
        self.assertEqual(payload["llmReview"]["findings"], ["ok"])

    def test_enhance_artifact_rejects_empty_markdown(self):
        runner = LLMAgentRunner(
            LLMRefineOptions(all_agents=True),
            call_fn=lambda prompt, system, max_tokens: "",
        )

        result = enhance_artifact_with_llm(
            runner=runner,
            agent_name="code-migration-agent",
            artifact_path="agent-workspace/03-migration/code-migration-tasks.md",
            content="# fallback",
            context="project context",
        )

        self.assertEqual(result, "# fallback")
        self.assertEqual(runner.summary()["agents"][0]["status"], "fallback")

    def test_detail_page_refinement_falls_back_when_key_bindings_are_lost(self):
        rule_page = """@Entry
@Component
struct ActivityDetail {
  detailInfo: Object | undefined = undefined
  loadDetail(name: string): void {}
  detailField(name: string, fallback: string = ''): string { return fallback }
  build() {
    Text(`HP ${this.detailField('hp', '-')}`)
    Text(this.detailField('height', '-'))
  }
}
"""
        broken_llm_page = """@Entry
@Component
struct ActivityDetail {
  detailInfo: Object | undefined = undefined
  loadDetail(name: string): void {}
  build() {
    Text(this.detailField('heightString', '11 M'))
    Text('HP')
  }
}
"""
        runner = LLMAgentRunner(
            LLMRefineOptions(enabled=True, all_agents=True),
            call_fn=lambda prompt, system, max_tokens: broken_llm_page,
        )

        result = refine_arkui_page_with_llm("ActivityDetail", "<layout />", rule_page, runner.options, runner=runner)

        self.assertEqual(result.strip(), rule_page.strip())
        self.assertEqual(runner.summary()["agents"][0]["status"], "fallback")

    def test_page_refinement_falls_back_when_router_import_is_missing(self):
        rule_page = """@Entry
@Component
struct ActivityMain {
  build() { Text('ok') }
}
"""
        broken_llm_page = """@Entry
@Component
struct ActivityMain {
  build() { Button('Back').onClick(() => router.back()) }
}
"""
        runner = LLMAgentRunner(
            LLMRefineOptions(enabled=True, all_agents=True),
            call_fn=lambda prompt, system, max_tokens: broken_llm_page,
        )

        result = refine_arkui_page_with_llm("ActivityMain", "<layout />", rule_page, runner.options, runner=runner)

        self.assertEqual(result.strip(), rule_page.strip())
        self.assertEqual(runner.summary()["agents"][0]["status"], "fallback")


if __name__ == "__main__":
    unittest.main()
