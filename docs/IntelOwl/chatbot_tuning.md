# Chatbot: Fine-tuning & Prompting

This guide covers choosing and customizing the language model behind the chatbot, tuning the prompt,
and packaging a custom model. It is aimed at operators who want to change the default model or
improve answer quality. For the environment variables referenced here see the
[chatbot configuration](./advanced_configuration.md#chatbot).

## How the model is wired

The chatbot uses [Ollama](https://ollama.com/) as a local LLM runtime and LangChain's native
**tool-calling** agent. At build time the backend creates a `ChatOllama` client
(`api_app/chatbot_manager/agent/agent.py`) pointed at `OLLAMA_BASE_URL` (default
`http://ollama:11434`) with `temperature=0` and a fixed context window, binds the chatbot tools to
it through the tool-calling API, and runs a tool-call → observation loop until the model replies with
plain text.

Two consequences matter for tuning:

- The model **must support Ollama tool calling**. A model that cannot emit tool calls will not work.
- The backend sets the prompt and the key inference parameters itself (see below), so they are the
  levers you tune — not a model's baked-in defaults.

## Choosing a model

The default is **`qwen2.5:3b`**. It is chosen on purpose: it is the smallest model that reliably
picks the right tool and answers from the tool output with **usable latency on a CPU-only deploy**
(for comparison, a 7B model such as `mistral` was markedly slower on CPU — minutes per agent round,
often hitting the turn timeout). On stronger
hardware you can switch to any larger tool-capable Ollama model for better answer quality.

Requirements for a replacement model:

- it supports tool calling in Ollama;
- the Ollama server is recent enough to **stream while tools are bound** — IntelOwl pins the Ollama
  image to `ollama/ollama:0.30.7` for this reason (versions older than 0.8.0 cannot stream with
  tools); keep this in mind if you run Ollama yourself.

## Pointing to a different model

Set the `OLLAMA_MODEL` secret to the model tag you want (it is pulled automatically on first start).
Keep the **three** places that reference the default in sync if you change the baked-in default
rather than just overriding the secret:

- `intel_owl/settings/chatbot.py` — `OLLAMA_MODEL` default;
- `docker/env_file_app_template` — `OLLAMA_MODEL`;
- `docker/entrypoints/ollama.sh` — `DEFAULT_MODEL` (the entrypoint that pulls the model).

For a normal deployment you only set the `OLLAMA_MODEL` secret; the entrypoint pulls it on startup.

## The context window (`num_ctx`)

The backend requests an **8192-token** context window (`_NUM_CTX` in `agent.py`). This is
deliberate: Ollama's default of 2048 tokens silently truncates the prompt (the system prompt plus
the tool schemas already approach ~2.2k tokens), which drops tool definitions and wrecks tool
selection. 8192 fits the prompt, the conversation history and the tool observations comfortably and
keeps the prompt prefix stable across iterations (so follow-up rounds hit Ollama's KV cache).

If you move to a larger model with a bigger context window and longer conversations, raising
`_NUM_CTX` is the knob — at the cost of more memory and slower evaluation.

## The system prompt

The assistant's instructions live in plain text at
`api_app/chatbot_manager/agent/system_prompt.txt`. This — not a model's built-in system message — is
what shapes the assistant's behavior, because the backend sends it as the agent's system prompt on
every turn. The file is organized in sections:

- `[Role]` — who the assistant is and its answer style (concise, data-driven, cite the tools used);
- `[Tools — when to use each]` — one line per tool telling the model when to call it;
- `[Rules]` — hard constraints (only the current user's data; call the right tool instead of
  guessing; `analyze_observable` only previews and never claims it launched anything);
- `[Response style]` — formatting expectations.

To tune behavior, edit this file. Practical prompting tips for small local models:

- Keep tool descriptions short and action-oriented ("Use for …"); they compete for context space.
- State hard guarantees in `[Rules]` (data scoping, the preview-only analysis guardrail) — small
  models follow short imperative rules better than long prose.
- When you add a new tool, add a matching one-line entry under `[Tools — when to use each]` so the
  model knows when to reach for it (see [adding a chatbot tool](./contribute.md)).

## Building a custom model with a Modelfile

Use an Ollama [Modelfile](https://docs.ollama.com/modelfile) to **package the weights** you want to
run — for example a specific quantization, or a fine-tuned model imported from a local GGUF file:

```dockerfile
# Modelfile
FROM qwen2.5:3b-instruct-q4_K_M
# or import your own weights:
# FROM ./my-finetuned-model.gguf
```

Build and register it, then point the chatbot at it:

```bash
ollama create intelowl-llm -f Modelfile
# then set the secret:
OLLAMA_MODEL=intelowl-llm
```

Important: the backend sets `num_ctx`, `temperature` and the system prompt explicitly on every call,
so a Modelfile's `SYSTEM` and its `PARAMETER num_ctx` / `PARAMETER temperature` are overridden for the
chatbot (other `PARAMETER` directives the backend does not set still apply). Use the Modelfile to
choose *which weights* run; use `system_prompt.txt` (and `_NUM_CTX` in
`agent.py`) to change *how the assistant behaves*.

## Validating a model before rollout

After switching or building a model, confirm it actually tool-calls before relying on it:

1. Bring up the stack with the Ollama service and wait for the model to finish pulling.
2. Open the chat and send a question that must use a tool, e.g. **"Show my recent jobs"** or
   **"Summarize job #<id>"**.
3. Verify the assistant calls a tool (a tool/status indicator appears) and answers from real data,
   rather than replying generically. The same check works through the REST endpoint
   `POST /api/chatbot/sessions/message`.

If the model answers without ever calling a tool, it is not tool-calling reliably — pick a different
model or a less aggressively quantized variant.

## Out of scope

Actual model training (LoRA/PEFT fine-tuning, dataset preparation, GGUF conversion of trained
adapters) is outside the scope of this guide. This page covers selecting, configuring, prompting and
packaging existing tool-capable models.
