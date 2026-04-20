# Recording Format

This document describes the JSONL recording format produced by ARC-AGI-3-Agents and how to resolve the corresponding reasoning screenshots for visualization systems.

## File Types

### Recording JSONL

Typical filename:

```text
<game_id>.<agent_name>.<model>.<observe_mode>.<reasoning_effort>.<recording_guid>.recording.jsonl
```

Example:

```text
ls20-9607627b.reasoningagent.gpt-5.1.with-observe.high.d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e.recording.jsonl
```

`recording_guid` is the stable run identifier for the entire recording file.

### Reasoning Screenshots

Typical path:

```text
recordings/reasoning_screens/<game_id>/<recording_guid>/<filename>.png
```

Example:

```text
recordings/reasoning_screens/ls20-9607627b/d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e/0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png
```

Screenshot filename fields:

- `0012`: `action_counter`, zero-padded to 4 digits
- `lvl00`: `levels_completed`, zero-padded to 2 digits
- `not_finished`: frame state, lowercased
- `2ec...`: `frame_guid`

## JSONL Envelope

Every line in a `.recording.jsonl` file is one event:

```json
{
  "timestamp": "2026-04-20T07:26:10.289063+00:00",
  "data": { ... }
}
```

- `timestamp`: event write time in UTC ISO-8601 format
- `data`: event payload

Consumers should parse the file line-by-line and inspect `data` to determine the event type.

## Event Types

## 1. Frame Event

Frame events are written after each environment step. They contain the game state after the chosen action has been applied.

Typical shape:

```json
{
  "game_id": "ls20-9607627b",
  "frame": [[[...]]],
  "state": "NOT_FINISHED",
  "levels_completed": 0,
  "win_levels": 7,
  "action_input": {
    "id": 1,
    "data": {},
    "reasoning": {
      "model": "gpt-5.1",
      "reasoning_effort": "high",
      "reasoning_tokens": 1234,
      "total_reasoning_tokens": 5678,
      "agent_type": "reasoning_agent",
      "hypothesis": "...",
      "aggregated_findings": "...",
      "response_preview": "...",
      "action_chosen": "ACTION1",
      "short_description": "...",
      "screen": {
        "recording_guid": "d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e",
        "frame_guid": "2ec6641a-2657-4f77-82ca-6c0900092a7e",
        "filename": "0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png",
        "relative_path": "reasoning_screens/ls20-9607627b/d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e/0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png",
        "path": "recordings/reasoning_screens/ls20-9607627b/d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e/0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png"
      },
      "game_context": {
        "score": 0,
        "state": "NOT_FINISHED",
        "action_counter": 12,
        "frame_count": 13
      }
    }
  },
  "guid": "2ec6641a-2657-4f77-82ca-6c0900092a7e",
  "full_reset": false,
  "available_actions": [1, 2, 3, 4]
}
```

Key fields:

- `guid`: the frame identifier for this post-action frame
- `action_input.id`: action applied to produce this frame
- `action_input.reasoning`: analysis metadata attached by the agent
- `action_input.reasoning.screen`: direct screenshot association for the reasoning step that selected this action

For visualization, the frame event is usually the main timeline primitive.

## 2. Token Event

Token events track model usage.

Typical shape:

```json
{
  "tokens": 16075,
  "total_tokens": 1714019,
  "assistant": "{\n  \"role\": \"assistant\",\n  \"tool_calls\": [...]\n}"
}
```

Key fields:

- `tokens`: tokens consumed by the most recent model call
- `total_tokens`: cumulative tokens for the run
- `assistant`: serialized assistant message for that call

Notes:

- In older recordings, `assistant` may be `null`.
- In newer reasoning-agent recordings, this field contains the serialized assistant tool-call message.

## 3. Reasoning Response Event

Reasoning agents now write a dedicated event with both the raw assistant output and the parsed semantic fields used by the agent.

Typical shape:

```json
{
  "event": "reasoning_response",
  "game_id": "ls20-9607627b",
  "action_counter": 12,
  "frame_guid": "2ec6641a-2657-4f77-82ca-6c0900092a7e",
  "screen": {
    "recording_guid": "d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e",
    "frame_guid": "2ec6641a-2657-4f77-82ca-6c0900092a7e",
    "filename": "0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png",
    "relative_path": "reasoning_screens/ls20-9607627b/d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e/0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png",
    "path": "recordings/reasoning_screens/ls20-9607627b/d6cae5cd-3fd8-47b0-a848-bc0fd6678e0e/0012_lvl00_not_finished_2ec6641a-2657-4f77-82ca-6c0900092a7e.png"
  },
  "assistant_message": "{\n  \"role\": \"assistant\",\n  \"tool_calls\": [...]\n}",
  "parsed_response": {
    "name": "ACTION1",
    "reason": "...",
    "short_description": "...",
    "hypothesis": "...",
    "aggregated_findings": "..."
  }
}
```

This is the best event type for rendering a reasoning panel in a UI.

Recommended usage:

- Render `parsed_response.reason` as the detailed step explanation
- Render `parsed_response.short_description` as the card title
- Render `parsed_response.hypothesis` as the current working theory
- Render `parsed_response.aggregated_findings` as cumulative findings
- Use `screen.path` or `screen.relative_path` for the screenshot shown alongside this reasoning step

## 4. Final Scorecard Event

At cleanup, some runs may append scorecard data for the game. The exact shape depends on `scorecard.get(game_id)`.

Consumers should treat any event with neither `frame`, nor `tokens`, nor `event == "reasoning_response"` as metadata/finalization unless stricter typing is added later.

## How To Resolve The Screenshot For A Step

Preferred lookup order:

1. Read the `reasoning_response` event for a step and use `data.screen.path`.
2. If unavailable, use `data.screen.relative_path` resolved against `RECORDINGS_DIR`.
3. If unavailable, read the subsequent frame event and use `data.action_input.reasoning.screen.path`.
4. If unavailable, reconstruct the path using:

```text
recordings/reasoning_screens/<game_id>/<recording_guid>/<action_counter>_lvl<levels_completed>_<state_lower>_<frame_guid>.png
```

Where:

- `game_id` comes from the recording filename or frame event
- `recording_guid` comes from the `.recording.jsonl` filename
- `action_counter` comes from `reasoning_response.action_counter` or `action_input.reasoning.game_context.action_counter`
- `levels_completed` comes from the frame event
- `state_lower` is `state.lower()`
- `frame_guid` comes from `reasoning_response.frame_guid`, `screen.frame_guid`, or frame event `guid`

## Recommended Visualization Join Strategy

For each recording:

1. Parse the recording filename to get `game_id` and `recording_guid`.
2. Stream all JSONL events in order.
3. Group `reasoning_response` events by `action_counter`.
4. Group frame events by their arrival order and by `action_input.reasoning.game_context.action_counter` when present.
5. Attach screenshots using `screen.path`.
6. Use token events to show per-step and cumulative usage.

Recommended timeline card model:

```json
{
  "recording_guid": "...",
  "game_id": "...",
  "action_counter": 12,
  "action_name": "ACTION1",
  "frame_guid": "2ec...",
  "state_after": "NOT_FINISHED",
  "levels_completed_after": 0,
  "reason": "...",
  "short_description": "...",
  "hypothesis": "...",
  "aggregated_findings": "...",
  "reasoning_tokens": 1234,
  "total_reasoning_tokens": 5678,
  "screenshot_path": "recordings/reasoning_screens/...",
  "assistant_message": "{...}"
}
```

## Compatibility Notes

- Older recordings may not contain `reasoning_response` events.
- Older recordings may not contain `action_input.reasoning.screen`.
- Older token events may have `assistant: null`.
- For older runs, screenshot correlation may require fallback reconstruction using filename conventions and neighboring frame metadata.

## Stability Notes

The JSONL stream is append-only and intended for analysis/debugging. Consumers should:

- ignore unknown fields
- tolerate missing optional fields
- use `event == "reasoning_response"` when present instead of inferring semantics from `assistant`
- prefer explicit `screen.path` over filename reconstruction
