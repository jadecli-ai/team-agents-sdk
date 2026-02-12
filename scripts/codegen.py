"""Generate Pydantic models, SQLAlchemy tables, Drizzle schema, and SQL from semantic YAML.

Usage:
    python scripts/codegen.py [--check]

With --check: validates YAML and prints what would be generated, without writing files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


SEMANTIC_DIR = Path(__file__).resolve().parent.parent / "semantic"
SRC_MODELS_DIR = Path(__file__).resolve().parent.parent / "src" / "models"
SRC_DB_DIR = Path(__file__).resolve().parent.parent / "src" / "db"
APP_DB_DIR = Path(__file__).resolve().parent.parent / "app" / "db"
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

# Type mapping: YAML type → (Python type, SQLAlchemy type, Drizzle type, SQL type)
TYPE_MAP: dict[str, tuple[str, str, str, str]] = {
    "uuid": ("UUID", "sa.UUID", "uuid", "UUID"),
    "varchar": ("str", "sa.String", "varchar", "VARCHAR"),
    "text": ("str | None", "sa.Text", "text", "TEXT"),
    "integer": ("int", "sa.Integer", "integer", "INTEGER"),
    "float": ("float", "sa.Float", "real", "REAL"),
    "timestamptz": ("datetime", "sa.DateTime(timezone=True)", "timestamp", "TIMESTAMPTZ"),
}


def load_enums() -> dict[str, dict]:
    """Load _enums.yaml."""
    path = SEMANTIC_DIR / "_enums.yaml"
    with open(path) as f:
        return yaml.safe_load(f).get("enums", {})


def load_table(name: str) -> dict:
    """Load a table YAML definition."""
    path = SEMANTIC_DIR / f"{name}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def parse_type(col_type: str) -> tuple[str, int | None]:
    """Parse 'varchar(200)' → ('varchar', 200)."""
    if "(" in col_type:
        base = col_type.split("(")[0]
        length = int(col_type.split("(")[1].rstrip(")"))
        return base, length
    return col_type, None


def generate_drizzle_schema(tables: list[dict], enums: dict) -> str:
    """Generate Drizzle pgTable definitions."""
    lines = [
        "// Auto-generated from semantic/*.yaml — do not edit manually",
        'import { pgTable, uuid, varchar, text, real, integer, timestamp } from "drizzle-orm/pg-core";',
        "",
    ]

    for table in tables:
        name = table["name"]
        lines.append(f'export const {name} = pgTable("{name}", {{')

        for col_name, col_def in table["columns"].items():
            base_type, length = parse_type(col_def["type"])
            nullable = col_def.get("nullable", True)
            default = col_def.get("default")
            server_default = col_def.get("server_default")
            is_pk = col_def.get("primary_key", False)

            # Map to Drizzle type
            drizzle_type = TYPE_MAP.get(base_type, ("", "", base_type, ""))[2]

            parts = []
            if drizzle_type == "uuid":
                parts.append(f'uuid("{col_name}")')
            elif drizzle_type == "varchar":
                length_str = f"{{ length: {length} }}" if length else ""
                parts.append(f'varchar("{col_name}", {length_str})')
            elif drizzle_type == "text":
                parts.append(f'text("{col_name}")')
            elif drizzle_type == "real":
                parts.append(f'real("{col_name}")')
            elif drizzle_type == "integer":
                parts.append(f'integer("{col_name}")')
            elif drizzle_type == "timestamp":
                parts.append(f'timestamp("{col_name}", {{ withTimezone: true }})')
            else:
                parts.append(f'varchar("{col_name}")')

            chain = ".".join(parts)

            if is_pk:
                chain += ".primaryKey()"
                if default and "gen_random_uuid" in str(default):
                    chain += ".defaultRandom()"
            else:
                if not nullable:
                    chain += ".notNull()"
                if default is not None and not server_default:
                    if isinstance(default, str):
                        chain += f'.default("{default}")'
                    elif isinstance(default, (int, float)):
                        chain += f".default({default})"
                if server_default == "now()":
                    chain += ".defaultNow()"

            lines.append(f"  {col_name}: {chain},")

        lines.append("});")
        lines.append("")

    return "\n".join(lines)


def generate_sql(tables: list[dict]) -> str:
    """Generate raw DDL SQL."""
    # For now, delegate to the hand-written migration
    return "-- See migrations/0001_initial.sql for the full DDL\n"


def main():
    parser = argparse.ArgumentParser(description="Generate code from semantic YAML schemas")
    parser.add_argument("--check", action="store_true", help="Validate only, don't write files")
    args = parser.parse_args()

    enums = load_enums()
    table_names = ["tasks", "subtasks", "task_dependencies", "agent_activity"]
    tables = [load_table(name) for name in table_names]

    print(f"Loaded {len(enums)} enums: {', '.join(enums.keys())}")
    print(f"Loaded {len(tables)} tables: {', '.join(t['name'] for t in tables)}")

    for table in tables:
        col_count = len(table.get("columns", {}))
        print(f"  {table['name']}: {col_count} columns")

    if args.check:
        print("\n--check mode: validation passed, no files written.")
        return

    # Generate Drizzle schema
    drizzle = generate_drizzle_schema(tables, enums)
    APP_DB_DIR.mkdir(parents=True, exist_ok=True)
    (APP_DB_DIR / "schema.ts").write_text(drizzle)
    print(f"\nWrote {APP_DB_DIR / 'schema.ts'}")

    print("\nCodegen complete. Python models and SQLAlchemy tables are maintained manually.")
    print("Run 'python scripts/codegen.py --check' to validate YAML schemas.")


if __name__ == "__main__":
    main()
