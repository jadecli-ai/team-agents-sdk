/**
 * Neon serverless database client with Drizzle ORM.
 *
 * @depends_on app/db/schema.ts
 * @depended_by app/page.tsx
 * @semver major
 */
import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "@/app/db/schema";

const sql = neon(process.env.POSTGRES_URL!);
export const db = drizzle(sql, { schema });
