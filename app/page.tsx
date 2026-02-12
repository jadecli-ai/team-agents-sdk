import { db } from "@/lib/db";
import { tasks, agentActivity } from "./db/schema";
import { count, sum, eq, sql } from "drizzle-orm";

async function getStats() {
  const [taskCounts] = await db
    .select({
      total: count(),
      totalCost: sum(tasks.actualCostUsd),
    })
    .from(tasks);

  const statusCounts = await db
    .select({
      status: tasks.status,
      count: count(),
    })
    .from(tasks)
    .groupBy(tasks.status);

  const recentActivity = await db
    .select({
      agentName: agentActivity.agentName,
      hookEvent: agentActivity.hookEvent,
      toolName: agentActivity.toolName,
      eventAt: agentActivity.eventAt,
    })
    .from(agentActivity)
    .orderBy(sql`${agentActivity.eventAt} DESC`)
    .limit(10);

  return { taskCounts, statusCounts, recentActivity };
}

const statusColors: Record<string, string> = {
  pending: "bg-yellow-500/20 text-yellow-300",
  in_progress: "bg-blue-500/20 text-blue-300",
  blocked: "bg-red-500/20 text-red-300",
  completed: "bg-emerald-500/20 text-emerald-300",
  failed: "bg-red-600/20 text-red-400",
  cancelled: "bg-gray-500/20 text-gray-400",
};

export default async function DashboardPage() {
  const { taskCounts, statusCounts, recentActivity } = await getStats();

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">Dashboard</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
          <p className="text-sm text-gray-400">Total Tasks</p>
          <p className="text-3xl font-bold mt-1">{taskCounts.total}</p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
          <p className="text-sm text-gray-400">Total Cost</p>
          <p className="text-3xl font-bold mt-1">
            ${Number(taskCounts.totalCost || 0).toFixed(2)}
          </p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
          <p className="text-sm text-gray-400">Status Breakdown</p>
          <div className="flex flex-wrap gap-2 mt-2">
            {statusCounts.map((s) => (
              <span
                key={s.status}
                className={`px-2 py-1 rounded text-xs font-medium ${statusColors[s.status ?? ""] ?? "bg-gray-700 text-gray-300"}`}
              >
                {s.status}: {s.count}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Recent Agent Activity</h3>
        <div className="rounded-lg border border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-900">
              <tr>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">
                  Agent
                </th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">
                  Event
                </th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">
                  Tool
                </th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {recentActivity.map((a, i) => (
                <tr key={i} className="hover:bg-gray-900/50">
                  <td className="px-4 py-3">{a.agentName}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded bg-gray-800 text-xs">
                      {a.hookEvent}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400">
                    {a.toolName ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {a.eventAt?.toISOString().slice(0, 19).replace("T", " ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
