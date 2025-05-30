import re
import random

TEAM_ID = "8fa85f64-5717-4562-b3fc-2c963f66afc3"
TASKS_SQL = "init_tasks.sql"
WEEKS_SQL = "init_week.sql"
OUTPUT_SQL = "init_week.generated.sql"

# Step 1: Extract task IDs
with open(TASKS_SQL, "r") as f:
    tasks_sql = f.read()

task_pattern = re.compile(
    r"\(\s*'([a-f0-9\-]+)'.*?'[^']*',\s*NULL,\s*'{}'".format(TEAM_ID)
)
task_ids = task_pattern.findall(tasks_sql)
print(f"Found {len(task_ids)} tasks for team {TEAM_ID}")

# Step 2: Parse init_week.sql
with open(WEEKS_SQL, "r") as f:
    week_lines = f.readlines()


# SQL tuple parser
def parse_sql_tuple(s):
    fields = []
    curr = ""
    in_quote = False
    in_brace = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == "'" and (not curr or curr[-1] != "\\"):
            in_quote = not in_quote
            curr += c
        elif c == "{" and not in_quote:
            in_brace += 1
            curr += c
        elif c == "}" and not in_quote:
            in_brace -= 1
            curr += c
        elif c == "," and not in_quote and in_brace == 0:
            fields.append(curr.strip())
            curr = ""
        else:
            curr += c
        i += 1
    if curr:
        fields.append(curr.strip())
    return fields


# Field indices in week table
col_indices = {
    "completed_tasks": 8,
    "missed_deadlines": 7,
}

new_week_lines = []
for line in week_lines:
    if "INSERT INTO" not in line or "VALUES" not in line:
        new_week_lines.append(line)
        continue

    # Extract only the value tuple portion (after VALUES)
    values_match = re.search(r"VALUES\s*\((.*)\)\s*;", line, re.IGNORECASE)
    if not values_match:
        new_week_lines.append(line)
        continue

    tuple_str = values_match.group(1)
    fields = parse_sql_tuple(tuple_str)

    # Randomly generate completed and missed task lists
    completed = random.sample(task_ids, k=random.randint(0, min(5, len(task_ids))))
    missed = random.sample(
        [tid for tid in task_ids if tid not in completed],
        k=random.randint(0, min(2, len(task_ids) - len(completed))),
    )

    completed_sql = "'{" + ",".join(completed) + "}'"
    missed_sql = "'{" + ",".join(missed) + "}'"

    fields[col_indices["completed_tasks"]] = completed_sql
    fields[col_indices["missed_deadlines"]] = missed_sql

    # Rebuild updated tuple
    new_tuple = "(" + ", ".join(fields) + ")"
    updated_line = re.sub(
        r"VALUES\s*\(.*\)\s*;", f"VALUES {new_tuple};", line, flags=re.IGNORECASE
    )
    new_week_lines.append(updated_line)

# Step 3: Write output
with open(OUTPUT_SQL, "w") as f:
    f.writelines(new_week_lines)

print(f"✅ Updated weeks written to {OUTPUT_SQL}")
