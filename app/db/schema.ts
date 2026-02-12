// Drizzle pgTable definitions matching semantic/*.yaml
import {
  pgTable,
  uuid,
  varchar,
  text,
  real,
  integer,
  timestamp,
  uniqueIndex,
  index,
  check,
} from "drizzle-orm/pg-core";
import { sql } from "drizzle-orm";

export const tasks = pgTable(
  "tasks",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    title: varchar("title", { length: 200 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 }).notNull().default("pending"),
    priority: varchar("priority", { length: 20 }).notNull().default("medium"),
    assignedAgent: varchar("assigned_agent", { length: 30 }),
    sessionId: varchar("session_id", { length: 100 }),
    estimatedCostUsd: real("estimated_cost_usd").notNull().default(0.0),
    actualCostUsd: real("actual_cost_usd").notNull().default(0.0),
    startedAt: timestamp("started_at", { withTimezone: true }),
    completedAt: timestamp("completed_at", { withTimezone: true }),
    dueAt: timestamp("due_at", { withTimezone: true }),
    githubIssueNumber: integer("github_issue_number"),
    githubProjectItemId: varchar("github_project_item_id", { length: 50 }),
    schemaVersion: integer("schema_version").notNull().default(1),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("ix_tasks_status").on(table.status),
    index("ix_tasks_priority").on(table.priority),
    index("ix_tasks_assigned_agent").on(table.assignedAgent),
  ]
);

export const agentActivity = pgTable(
  "agent_activity",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    taskId: uuid("task_id").references(() => tasks.id, {
      onDelete: "set null",
    }),
    subtaskId: uuid("subtask_id"),
    agentName: varchar("agent_name", { length: 50 }).notNull(),
    agentRole: varchar("agent_role", { length: 30 }),
    sessionId: varchar("session_id", { length: 100 }),
    hookEvent: varchar("hook_event", { length: 20 }).notNull(),
    toolName: varchar("tool_name", { length: 50 }),
    toolInputSummary: varchar("tool_input_summary", { length: 2000 }),
    toolResponseSummary: varchar("tool_response_summary", { length: 2000 }),
    durationMs: integer("duration_ms"),
    costUsd: real("cost_usd"),
    numTurns: integer("num_turns"),
    eventAt: timestamp("event_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("ix_agent_activity_task_id").on(table.taskId),
    index("ix_agent_activity_agent_name").on(table.agentName),
    index("ix_agent_activity_hook_event").on(table.hookEvent),
    index("ix_agent_activity_event_at").on(table.eventAt),
  ]
);

export const subtasks = pgTable(
  "subtasks",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    parentTaskId: uuid("parent_task_id")
      .notNull()
      .references(() => tasks.id, { onDelete: "cascade" }),
    subtaskType: varchar("subtask_type", { length: 20 }).notNull(),
    title: varchar("title", { length: 200 }).notNull(),
    status: varchar("status", { length: 20 }).notNull().default("pending"),
    outputSummary: text("output_summary"),
    githubIssueNumber: integer("github_issue_number"),
    githubProjectItemId: varchar("github_project_item_id", { length: 50 }),
    agentActivityId: uuid("agent_activity_id").references(
      () => agentActivity.id,
      { onDelete: "set null" }
    ),
    schemaVersion: integer("schema_version").notNull().default(1),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("ix_subtasks_parent_task_id").on(table.parentTaskId),
    index("ix_subtasks_subtask_type").on(table.subtaskType),
    index("ix_subtasks_status").on(table.status),
  ]
);

export const taskDependencies = pgTable(
  "task_dependencies",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    blockerTaskId: uuid("blocker_task_id")
      .notNull()
      .references(() => tasks.id, { onDelete: "cascade" }),
    blockedTaskId: uuid("blocked_task_id")
      .notNull()
      .references(() => tasks.id, { onDelete: "cascade" }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    check(
      "ck_no_self_dependency",
      sql`${table.blockerTaskId} != ${table.blockedTaskId}`
    ),
    uniqueIndex("uq_dependency").on(table.blockerTaskId, table.blockedTaskId),
    index("ix_task_dependencies_blocker").on(table.blockerTaskId),
    index("ix_task_dependencies_blocked").on(table.blockedTaskId),
  ]
);
