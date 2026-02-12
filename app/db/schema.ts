// Auto-generated from semantic/*.yaml — do not edit manually
import { pgTable, uuid, varchar, text, real, integer, timestamp } from "drizzle-orm/pg-core";

export const tasks = pgTable("tasks", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: varchar("title", { length: 200 }).notNull(),
  description: text("description"),
  status: varchar("status", { length: 20 }).notNull().default("pending"),
  priority: varchar("priority", { length: 20 }).notNull().default("medium"),
  assigned_agent: varchar("assigned_agent", { length: 30 }),
  session_id: varchar("session_id", { length: 100 }),
  estimated_cost_usd: real("estimated_cost_usd").notNull().default(0.0),
  actual_cost_usd: real("actual_cost_usd").notNull().default(0.0),
  started_at: timestamp("started_at", { withTimezone: true }),
  completed_at: timestamp("completed_at", { withTimezone: true }),
  due_at: timestamp("due_at", { withTimezone: true }),
  github_issue_number: integer("github_issue_number"),
  github_project_item_id: varchar("github_project_item_id", { length: 50 }),
  schema_version: integer("schema_version").notNull().default(1),
  created_at: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export const subtasks = pgTable("subtasks", {
  id: uuid("id").primaryKey().defaultRandom(),
  parent_task_id: uuid("parent_task_id").notNull(),
  subtask_type: varchar("subtask_type", { length: 20 }).notNull(),
  title: varchar("title", { length: 200 }).notNull(),
  status: varchar("status", { length: 20 }).notNull().default("pending"),
  output_summary: text("output_summary"),
  github_issue_number: integer("github_issue_number"),
  github_project_item_id: varchar("github_project_item_id", { length: 50 }),
  agent_activity_id: uuid("agent_activity_id"),
  schema_version: integer("schema_version").notNull().default(1),
  created_at: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export const task_dependencies = pgTable("task_dependencies", {
  id: uuid("id").primaryKey().defaultRandom(),
  blocker_task_id: uuid("blocker_task_id").notNull(),
  blocked_task_id: uuid("blocked_task_id").notNull(),
  created_at: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const agent_activity = pgTable("agent_activity", {
  id: uuid("id").primaryKey().defaultRandom(),
  task_id: uuid("task_id"),
  subtask_id: uuid("subtask_id"),
  agent_name: varchar("agent_name", { length: 50 }).notNull(),
  agent_role: varchar("agent_role", { length: 30 }),
  session_id: varchar("session_id", { length: 100 }),
  hook_event: varchar("hook_event", { length: 20 }).notNull(),
  tool_name: varchar("tool_name", { length: 50 }),
  tool_input_summary: varchar("tool_input_summary", { length: 2000 }),
  tool_response_summary: varchar("tool_response_summary", { length: 2000 }),
  duration_ms: integer("duration_ms"),
  cost_usd: real("cost_usd"),
  num_turns: integer("num_turns"),
  event_at: timestamp("event_at", { withTimezone: true }).notNull().defaultNow(),
  created_at: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const mlflow_traces = pgTable("mlflow_traces", {
  id: uuid("id").primaryKey().defaultRandom(),
  clone_id: varchar("clone_id", { length: 50 }).notNull(),
  experiment_name: varchar("experiment_name", { length: 200 }).notNull(),
  run_id: varchar("run_id", { length: 64 }).notNull(),
  start_time: timestamp("start_time", { withTimezone: true }).notNull(),
  end_time: timestamp("end_time", { withTimezone: true }),
  duration_ms: integer("duration_ms"),
  status: varchar("status", { length: 20 }).notNull(),
  total_tokens: integer("total_tokens"),
  estimated_cost_usd: real("estimated_cost_usd"),
  model_id: varchar("model_id", { length: 100 }),
  synced_at: timestamp("synced_at", { withTimezone: true }).notNull().defaultNow(),
  created_at: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});
