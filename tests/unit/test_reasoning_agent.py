import os
from types import SimpleNamespace

import pytest

from agents.recorder import Recorder
from agents.templates.reasoning_agent import (
    ReasoningActionResponse,
    ReasoningAgent,
)


@pytest.mark.unit
class TestReasoningAgentRecording:
    def test_save_screen_image_includes_recording_guid(self, temp_recordings_dir):
        agent = object.__new__(ReasoningAgent)
        agent.action_counter = 12
        agent.game_id = "test-game"
        agent.recorder = Recorder(prefix="test-game.reasoningagent", guid="recording-guid")

        latest_frame = SimpleNamespace(
            guid="frame-guid",
            levels_completed=3,
            state=SimpleNamespace(name="NOT_FINISHED"),
        )

        screen = agent.save_screen_image(b"fake-png-data", latest_frame)

        assert screen["recording_guid"] == "recording-guid"
        assert screen["frame_guid"] == "frame-guid"
        assert screen["relative_path"].startswith(
            os.path.join(
                "reasoning_screens", "test-game", "recording-guid"
            )
        )
        assert os.path.exists(screen["path"])

    def test_record_reasoning_response_writes_association(self, temp_recordings_dir):
        agent = object.__new__(ReasoningAgent)
        agent.game_id = "test-game"
        agent.action_counter = 7
        agent.recorder = Recorder(prefix="test-game.reasoningagent", guid="recording-guid")
        agent._latest_screen_record = {
            "recording_guid": "recording-guid",
            "frame_guid": "frame-guid",
            "filename": "0007_lvl00_not_finished_frame-guid.png",
            "relative_path": os.path.join(
                "reasoning_screens",
                "test-game",
                "recording-guid",
                "0007_lvl00_not_finished_frame-guid.png",
            ),
            "path": os.path.join(
                temp_recordings_dir,
                "reasoning_screens",
                "test-game",
                "recording-guid",
                "0007_lvl00_not_finished_frame-guid.png",
            ),
        }

        latest_frame = SimpleNamespace(guid="frame-guid")
        response_message = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "ACTION1",
                        "arguments": "{\"reason\":\"test\"}",
                    },
                }
            ],
        }
        action_response = ReasoningActionResponse(
            name="ACTION1",
            reason="Test reasoning.",
            short_description="Test action",
            hypothesis="Test hypothesis.",
            aggregated_findings="Test findings.",
        )

        agent.record_reasoning_response(
            latest_frame=latest_frame,
            response_message=response_message,
            action_response=action_response,
        )

        events = agent.recorder.get()
        assert len(events) == 1
        event = events[0]["data"]
        assert event["event"] == "reasoning_response"
        assert event["frame_guid"] == "frame-guid"
        assert event["screen"]["recording_guid"] == "recording-guid"
        assert event["parsed_response"]["reason"] == "Test reasoning."
        assert '"name": "ACTION1"' in event["assistant_message"]
