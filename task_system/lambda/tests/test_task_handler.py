import json
import pytest
from unittest.mock import patch, MagicMock, call
import os
import sys
from datetime import datetime

# Add the lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'task_processor'))

from task_handler import (
    process,
    process_task,
    handle_high_priority_task,
    handle_normal_priority_task,
    handle_low_priority_task
)


class TestHandlePriorityTasks:
    """Tests for individual priority handlers"""

    def test_handle_high_priority_task_prints_correct_message(self, capsys):
        """Test that high priority handler prints correct format"""
        handle_high_priority_task(
            task_id="123",
            task_type="email",
            description="Send email",
            created_at="2025-11-09T10:00:00"
        )
        captured = capsys.readouterr()
        assert "[HIGH PRIORITY]" in captured.out
        assert "123" in captured.out
        assert "email" in captured.out
        assert "Send email" in captured.out

    def test_handle_normal_priority_task_prints_correct_message(self, capsys):
        """Test that normal priority handler prints correct format"""
        handle_normal_priority_task(
            task_id="456",
            task_type="notification",
            description="Send notification",
            created_at="2025-11-09T10:00:00"
        )
        captured = capsys.readouterr()
        assert "[NORMAL PRIORITY]" in captured.out
        assert "456" in captured.out
        assert "notification" in captured.out
        assert "Send notification" in captured.out

    def test_handle_low_priority_task_prints_correct_message(self, capsys):
        """Test that low priority handler prints correct format"""
        handle_low_priority_task(
            task_id="789",
            task_type="cleanup",
            description="Cleanup logs",
            created_at="2025-11-09T10:00:00"
        )
        captured = capsys.readouterr()
        assert "[LOW PRIORITY]" in captured.out
        assert "789" in captured.out
        assert "cleanup" in captured.out
        assert "Cleanup logs" in captured.out


class TestProcessTask:
    """Tests for the process_task function"""

    @patch('task_handler.handle_high_priority_task')
    def test_routes_high_priority_correctly(self, mock_high):
        """Test that high priority tasks are routed correctly"""
        process_task(
            task_id="task-1",
            task_type="email",
            description="Test",
            priority="high",
            created_at="2025-11-09T10:00:00"
        )
        mock_high.assert_called_once_with(
            "task-1",
            "email",
            "Test",
            "2025-11-09T10:00:00"
        )

    @patch('task_handler.handle_normal_priority_task')
    def test_routes_normal_priority_correctly(self, mock_normal):
        """Test that normal priority tasks are routed correctly"""
        process_task(
            task_id="task-2",
            task_type="notification",
            description="Test",
            priority="normal",
            created_at="2025-11-09T10:00:00"
        )
        mock_normal.assert_called_once_with(
            "task-2",
            "notification",
            "Test",
            "2025-11-09T10:00:00"
        )

    @patch('task_handler.handle_low_priority_task')
    def test_routes_low_priority_correctly(self, mock_low):
        """Test that low priority tasks are routed correctly"""
        process_task(
            task_id="task-3",
            task_type="cleanup",
            description="Test",
            priority="low",
            created_at="2025-11-09T10:00:00"
        )
        mock_low.assert_called_once_with(
            "task-3",
            "cleanup",
            "Test",
            "2025-11-09T10:00:00"
        )

    def test_raises_error_for_unknown_priority(self):
        """Test that unknown priority raises TypeError (bug in original code)"""
        with pytest.raises(TypeError, match="'NoneType' object is not callable"):
            process_task(
                task_id="task-4",
                task_type="unknown",
                description="Test",
                priority="urgent",  # Invalid priority
                created_at="2025-11-09T10:00:00"
            )


class TestProcessFunction:
    """Tests for the main process Lambda handler function"""

    @patch('task_handler.process_task')
    def test_processes_single_sqs_record(self, mock_process_task):
        """Test processing a single SQS message"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'test-123',
                        'task_type': 'email',
                        'description': 'Send welcome email',
                        'priority': 'high',
                        'created_at': '2025-11-09T10:00:00'
                    })
                }
            ]
        }

        result = process(event, None)

        assert result['statusCode'] == 200
        assert 'Tasks processed successfully' in result['body']
        mock_process_task.assert_called_once_with(
            'test-123',
            'email',
            'Send welcome email',
            'high',
            '2025-11-09T10:00:00'
        )

    @patch('task_handler.process_task')
    def test_processes_multiple_sqs_records(self, mock_process_task):
        """Test processing multiple SQS messages"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'task_type': 'email',
                        'description': 'Email 1',
                        'priority': 'high',
                        'created_at': '2025-11-09T10:00:00'
                    })
                },
                {
                    'body': json.dumps({
                        'task_id': 'task-2',
                        'task_type': 'notification',
                        'description': 'Notification 1',
                        'priority': 'normal',
                        'created_at': '2025-11-09T10:01:00'
                    })
                }
            ]
        }

        result = process(event, None)

        assert result['statusCode'] == 200
        assert mock_process_task.call_count == 2

    @patch('task_handler.process_task')
    def test_uses_default_description_when_missing(self, mock_process_task):
        """Test that missing description uses default"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'task_type': 'email',
                        'priority': 'high',
                        'created_at': '2025-11-09T10:00:00'
                    })
                }
            ]
        }

        process(event, None)

        call_args = mock_process_task.call_args[0]
        assert call_args[2] == 'No description provided'

    @patch('task_handler.process_task')
    def test_uses_default_priority_when_missing(self, mock_process_task):
        """Test that missing priority uses default"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'task_type': 'email',
                        'description': 'Test',
                        'created_at': '2025-11-09T10:00:00'
                    })
                }
            ]
        }

        process(event, None)

        call_args = mock_process_task.call_args[0]
        assert call_args[3] == 'normal'

    @patch('task_handler.process_task')
    def test_generates_timestamp_when_missing(self, mock_process_task):
        """Test that missing created_at generates timestamp"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'task_type': 'email',
                        'description': 'Test',
                        'priority': 'high'
                    })
                }
            ]
        }

        process(event, None)

        call_args = mock_process_task.call_args[0]
        # Should have a timestamp (ISO format)
        assert 'T' in call_args[4]  # ISO format contains 'T'

    @patch('task_handler.process_task')
    def test_raises_exception_on_processing_error(self, mock_process_task):
        """Test that exceptions during processing are raised"""
        mock_process_task.side_effect = ValueError("Processing error")

        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'task_type': 'email',
                        'description': 'Test',
                        'priority': 'high',
                        'created_at': '2025-11-09T10:00:00'
                    })
                }
            ]
        }

        with pytest.raises(ValueError, match="Processing error"):
            process(event, None)

    @patch('task_handler.process_task')
    def test_handles_malformed_json_in_record(self, mock_process_task):
        """Test that malformed JSON raises an exception"""
        event = {
            'Records': [
                {
                    'body': 'invalid-json'
                }
            ]
        }

        with pytest.raises(json.JSONDecodeError):
            process(event, None)

    @patch('task_handler.process_task')
    def test_handles_missing_task_id(self, mock_process_task):
        """Test that missing task_id raises KeyError"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_type': 'email',
                        'description': 'Test'
                    })
                }
            ]
        }

        with pytest.raises(KeyError):
            process(event, None)

    @patch('task_handler.process_task')
    def test_handles_missing_task_type(self, mock_process_task):
        """Test that missing task_type raises KeyError"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'description': 'Test'
                    })
                }
            ]
        }

        with pytest.raises(KeyError):
            process(event, None)

    @patch('task_handler.process_task')
    def test_prints_received_event(self, mock_process_task, capsys):
        """Test that received event is printed for debugging"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-1',
                        'task_type': 'email',
                        'description': 'Test',
                        'priority': 'high',
                        'created_at': '2025-11-09T10:00:00'
                    })
                }
            ]
        }

        process(event, None)

        captured = capsys.readouterr()
        assert "Received event:" in captured.out

    @patch('task_handler.process_task')
    def test_prints_processing_messages(self, mock_process_task, capsys):
        """Test that processing messages are printed"""
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'task_id': 'task-123',
                        'task_type': 'email',
                        'description': 'Test',
                        'priority': 'high',
                        'created_at': '2025-11-09T10:00:00'
                    })
                }
            ]
        }

        process(event, None)

        captured = capsys.readouterr()
        assert "Processing task task-123:" in captured.out
        assert "Task task-123 processed successfully." in captured.out
