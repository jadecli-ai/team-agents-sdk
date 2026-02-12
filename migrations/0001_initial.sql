-- 0001_initial.sql
-- Neon Postgres DDL for jadecli-team-agents-sdk task system
-- Generated from semantic/*.yaml

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    assigned_agent VARCHAR(30),
    session_id VARCHAR(100),
    estimated_cost_usd REAL NOT NULL DEFAULT 0.0,
    actual_cost_usd REAL NOT NULL DEFAULT 0.0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    due_at TIMESTAMPTZ,
    github_issue_number INTEGER,
    github_project_item_id VARCHAR(50),
    schema_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS ix_tasks_priority ON tasks (priority);
CREATE INDEX IF NOT EXISTS ix_tasks_assigned_agent ON tasks (assigned_agent);

-- Agent activity table (before subtasks, since subtasks references it)
CREATE TABLE IF NOT EXISTS agent_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    subtask_id UUID,  -- FK added after subtasks table exists
    agent_name VARCHAR(50) NOT NULL,
    agent_role VARCHAR(30),
    session_id VARCHAR(100),
    hook_event VARCHAR(20) NOT NULL,
    tool_name VARCHAR(50),
    tool_input_summary VARCHAR(2000),
    tool_response_summary VARCHAR(2000),
    duration_ms INTEGER,
    cost_usd REAL,
    num_turns INTEGER,
    event_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_agent_activity_task_id ON agent_activity (task_id);
CREATE INDEX IF NOT EXISTS ix_agent_activity_agent_name ON agent_activity (agent_name);
CREATE INDEX IF NOT EXISTS ix_agent_activity_hook_event ON agent_activity (hook_event);
CREATE INDEX IF NOT EXISTS ix_agent_activity_event_at ON agent_activity (event_at);

-- Subtasks table
CREATE TABLE IF NOT EXISTS subtasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    subtask_type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    output_summary TEXT,
    github_issue_number INTEGER,
    github_project_item_id VARCHAR(50),
    agent_activity_id UUID REFERENCES agent_activity(id) ON DELETE SET NULL,
    schema_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_subtasks_parent_task_id ON subtasks (parent_task_id);
CREATE INDEX IF NOT EXISTS ix_subtasks_subtask_type ON subtasks (subtask_type);
CREATE INDEX IF NOT EXISTS ix_subtasks_status ON subtasks (status);

-- Add FK from agent_activity.subtask_id → subtasks.id
ALTER TABLE agent_activity
    ADD CONSTRAINT fk_agent_activity_subtask
    FOREIGN KEY (subtask_id) REFERENCES subtasks(id) ON DELETE SET NULL;

-- Task dependencies (many-to-many)
CREATE TABLE IF NOT EXISTS task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blocker_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    blocked_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_no_self_dependency CHECK (blocker_task_id != blocked_task_id),
    CONSTRAINT uq_dependency UNIQUE (blocker_task_id, blocked_task_id)
);

CREATE INDEX IF NOT EXISTS ix_task_dependencies_blocker ON task_dependencies (blocker_task_id);
CREATE INDEX IF NOT EXISTS ix_task_dependencies_blocked ON task_dependencies (blocked_task_id);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_subtasks_updated_at
    BEFORE UPDATE ON subtasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
