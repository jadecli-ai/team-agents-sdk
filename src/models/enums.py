"""Enum definitions matching semantic/_enums.yaml."""

from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    blocked = "blocked"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class AgentRole(str, Enum):
    team_lead = "team_lead"
    code_reviewer = "code_reviewer"
    test_runner = "test_runner"
    web_crawler = "web_crawler"
    research_analyst = "research_analyst"


class SubtaskType(str, Enum):
    git_hook = "git_hook"
    agent_hook = "agent_hook"
    validation = "validation"
    notification = "notification"
