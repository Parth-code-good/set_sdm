# app.py
import os
import json
import datetime
import shutil
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlglot import parse, exp

# ---------- Configuration ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_ROOT = os.path.join(BASE_DIR, "userdata")     # per-user data will go here
os.makedirs(DATA_ROOT, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-in-prod")
app.config['DEBUG'] = True
# SQLite app database (for users/projects metadata)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
llm = ChatOpenAI(model="gpt-4o-mini")

# ---------- SQLAlchemy models ----------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    projects = db.relationship("Project", backref="owner", cascade="all,delete-orphan")

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    versions = db.relationship("Version", backref="project", cascade="all,delete-orphan", order_by="Version.created_at")

class Version(db.Model):
    __tablename__ = "versions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., version1
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    schema_file = db.Column(db.String(512))
    test_file = db.Column(db.String(512))
    utility_file = db.Column(db.String(512))
    mermaid_file = db.Column(db.String(512))
    db_file = db.Column(db.String(512))

# Create DB tables if not present
with app.app_context():
    db.create_all()

# ---------- Helpers ----------
def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return inner

def user_dir(user_id):
    p = os.path.join(DATA_ROOT, str(user_id))
    os.makedirs(p, exist_ok=True)
    return p

def project_dir(user_id, project_id):
    p = os.path.join(user_dir(user_id), f"project_{project_id}")
    os.makedirs(p, exist_ok=True)
    return p

def version_dir(user_id, project_id, version_name):
    p = os.path.join(project_dir(user_id, project_id), version_name)
    os.makedirs(p, exist_ok=True)
    return p

# Safe sqlite connector factory for version DBs
import sqlite3
def get_sqlite_conn(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ---------- Reused original LLM/SQL functions (adapted to be inside this file) ----------
def generate_schema_and_diagram(prompt_text):
    print(f"Generating for prompt: {prompt_text}")
    generation_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a database design assistant. You must generate BOTH a complete SQL schema and a valid Mermaid.js ERD diagram. Respond with the SQL first, then the Mermaid.js code inside a 'mermaid' code block.Always generate SQL compatible with SQLite. Use INTEGER PRIMARY KEY AUTOINCREMENT instead of AUTO_INCREMENT. Do not use MySQL-specific syntax."),
        ("user", f"Generate a database model for the following concept: {prompt_text}")
    ])
    chain = generation_prompt | llm
    try:
        response = chain.invoke({"prompt": prompt_text})
        content = response.content
        sql_schema = content.split("```sql")[1].split("```")[0].strip()
        mermaid_code = content.split("```mermaid")[1].split("```")[0].strip()
        return sql_schema, mermaid_code
    except Exception as e:
        print(f"Error generating schema: {e}")
        return f"Error: {e}", "graph TD\n    Error[Error generating diagram]"

"""
def generate_diagram_from_sql(sql_schema):
    print("Generating diagram from existing SQL...")
    diagram_gen_prompt = ChatPromptTemplate.from_messages([
        ("system", 
You are a database diagramming assistant. Given a SQL schema, you must generate a valid Mermaid.js ERD diagram.
Respond with *only* the Mermaid.js code inside a single ```mermaid code block.
Always generate SQL compatible with SQLite. Use INTEGER PRIMARY KEY AUTOINCREMENT instead of AUTO_INCREMENT.
Do not use MySQL-specific syntax.
),
        ("user", f"Here is the SQL schema:\n\n{sql_schema}")
    ])
    chain = diagram_gen_prompt | llm
    try:
        response = chain.invoke({"sql_schema": sql_schema})
        content = response.content
        mermaid_code = content.split("```mermaid")[1].split("```")[0].strip()
        return mermaid_code
    except Exception as e:
        print(f"Error generating diagram from SQL: {e}")
        return "graph TD\n    Error[Error generating diagram from SQL]"
"""
import re


import re

import re

import re

def fix_mermaid_relations(mermaid_code):
    lines = mermaid_code.split("\n")
    cleaned = []

    rel_pattern = re.compile(r"(^\s*\w+\s+[}o|]{1,2}--[|}{]{1,2}\s+\w+\s*:\s*)(.*)$")

    for line in lines:
        match = rel_pattern.match(line)
        if match:
            prefix = match.group(1)

            # take only the first token (FK name)
            label = match.group(2).strip().split()[0]

            cleaned.append(f"{prefix}{label}")
        else:
            cleaned.append(line)

    return "\n".join(cleaned)

def sql_to_mermaid(sql_text):
    print("\n=== DEBUG: Starting SQL → Mermaid Parsing ===\n")

    sql = sql_text.replace("\n", " ").replace("\t", " ")
    sql = re.sub(r"\s+", " ", sql)

    table_blocks = re.findall(
        r"CREATE TABLE\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\);",
        sql,
        re.IGNORECASE
    )

    if not table_blocks:
        print("DEBUG: No CREATE TABLE statements found.")
        return "erDiagram\n    ErrorTable {{ string error }}\n    ErrorTable ||--|| ErrorTable : none"

    mermaid = ["erDiagram"]
    relationships = []

    for table_name, cols_raw in table_blocks:
        print(f"\n--- DEBUG: Processing table: {table_name} ---")

        # ESCAPED braces for f-string
        mermaid.append(f"    {table_name} {{")  # OK, not an f-string that needs escaping

        # Split safe (ignore commas inside parentheses)
        cols = []
        depth = 0
        current = ""
        for ch in cols_raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1

            if ch == "," and depth == 0:
                cols.append(current.strip())
                current = ""
            else:
                current += ch
        if current.strip():
            cols.append(current.strip())

        # Process each column / constraint
        for col_line in cols:
            raw = col_line.strip()

            # Skip constraints
            if re.match(r"^(PRIMARY KEY|FOREIGN KEY|UNIQUE|CHECK|CONSTRAINT)",
                        raw, re.IGNORECASE):
                print(f"  SKIP constraint → {raw}")
                continue

            # Column name + type
            m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z0-9()]+)", raw)
            if not m:
                print(f"  SKIP unrecognized line → {raw}")
                continue

            col_name = m.group(1)
            sql_type = m.group(2).upper()

            # Map SQLite types → Mermaid types
            type_map = {
                "INTEGER": "int",
                "TEXT": "string",
                "REAL": "float",
                "DATETIME": "datetime",
            }
            mermaid_type = type_map.get(sql_type, "string")

            pk = "PK" if "PRIMARY KEY" in raw.upper() else ""

            col_line_out = f"        {mermaid_type} {col_name}"
            if pk:
                col_line_out += " PK"

            print(f"  ADD column → {col_line_out}")
            mermaid.append(col_line_out)

        # Now detect FK constraints globally in block
        fk_matches = re.findall(
            r"FOREIGN KEY\s*\(\s*([A-Za-z_]+)\s*\)\s*REFERENCES\s*([A-Za-z_]+)\s*\(\s*([A-Za-z_]+)\s*\)",
            cols_raw,
            re.IGNORECASE
        )

        for fk_col, ref_table, ref_col in fk_matches:
            print(f"  ADD FK → {table_name}.{fk_col} → {ref_table}.{ref_col}")

            # ESCAPED BRACES: }} and {{
            rel = (
                f"    {table_name} }}o--|| {ref_table} : "
                f"{fk_col} to {ref_col}"
            )

            if rel not in relationships:
                relationships.append(rel)

        # Close block (OK, not part of an f-string)
        mermaid.append("    }")

    mermaid.extend(relationships)

    print("\n=== DEBUG: Completed Successfully ===\n")

    st= "\n".join(mermaid)
    st= fix_mermaid_relations(st)
    return st


def check_schema(sql_schema):
    report = []
    try:
        parsed_expressions = parse(sql_schema)
        if not parsed_expressions:
            report.append({"type": "error", "message": "SQL schema is empty or could not be parsed."})
            return report
        tables = {}
        # First pass: find table names
        for expr in parsed_expressions:
            if isinstance(expr, exp.Create) and expr.kind == 'TABLE':
                table_name = expr.this.this.name
                tables[table_name] = {'pk': False}
                if not table_name.islower():
                    report.append({"type":"warning","table":table_name,"message":f"Naming Convention: Table '{table_name}' is not in lowercase."})
                for constraint in expr.constraints:
                    if isinstance(constraint, exp.PrimaryKey):
                        tables[table_name]['pk'] = True
                for col_def in expr.find_all(exp.ColumnDef):
                    if any(isinstance(c, exp.PrimaryKey) for c in col_def.constraints):
                        tables[table_name]['pk'] = True
        # second pass: check PKs and FKs
        for expr in parsed_expressions:
            if isinstance(expr, exp.Create) and expr.kind == 'TABLE':
                table_name = expr.this.this.name
                if not tables[table_name]['pk']:
                    report.append({"type":"error","table":table_name,"message":f"Missing Primary Key: Table '{table_name}' does not have a PRIMARY KEY defined."})
                for constraint in expr.constraints:
                    if isinstance(constraint, exp.ForeignKey):
                        ref_table = constraint.find(exp.Reference).this.this.name
                        if ref_table not in tables:
                            report.append({"type":"error","table":table_name,"message":f"Invalid Foreign Key: Table '{table_name}' has a FOREIGN KEY that references a non-existent table '{ref_table}'."})
        if not report:
            report.append({"type":"success","message":"All static checks passed!"})
        return report
    except Exception as e:
        return [{"type":"error","message":f"Schema Parsing Error: {str(e)}"}]

def generate_test_suite(sql_schema):
    print("Generating test suite with rationales...")
    test_gen_prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a database test case generator. Given a SQL schema, you must generate a JSON array of test transactions.
Each object in the array must have **four** keys:
Always generate SQL compatible with SQLite. Use INTEGER PRIMARY KEY AUTOINCREMENT instead of AUTO_INCREMENT.
Do not use MySQL-specific syntax.
1. "name": A short description of the test.
2. "type": Either 'normal' or 'edge'.
3. "sql": The full SQL command for the test (e.g., INSERT, UPDATE, SELECT, DELETE).
4. "rationale": A brief, one-sentence explanation for *why* this test is important.

Generate at least 5 normal tests and 5 edge case tests.
Respond with *only* the JSON array inside a single ```json code block.
"""),
        ("user", f"Here is the schema:\n\n{sql_schema}")
    ])
    chain = test_gen_prompt | llm
    try:
        response = chain.invoke({"sql_schema": sql_schema})
        content = response.content
        json_response_str = content.split("```json")[1].split("```")[0].strip()
        test_suite = json.loads(json_response_str)
        return test_suite
    except Exception as e:
        print(f"Error generating test suite: {e}")
        return [{"name":"Error generating test suite","type":"error","sql":str(e),"rationale":"An error occurred during test generation."}]

# ---------- Utility generator (heuristic, can be improved with LLM) ----------
def generate_utility_table_from_schema(sql_text):
    """
    Generates a detailed utility explanation table using an LLM.
    The LLM explains:
      - Why each table exists
      - Why each attribute exists
    """
    # -----------------------------
    # 1. Extract tables + columns
    # -----------------------------
    tables = {}
    pattern = r"CREATE TABLE\s+[`\"]?(\w+)[`\"]?\s*\((.*?)\);"
    matches = re.findall(pattern, sql_text, flags=re.S)

    for table_name, body in matches:
        cols = []
        for line in body.split(","):
            line = line.strip()
            if line == "":
                continue
            col_name = line.split()[0].strip('`"')
            cols.append(col_name)
        tables[table_name] = cols

    # -----------------------------
    # 2. Ask the LLM to explain each table
    # -----------------------------
    final_doc = ["# Utility Table\n\n",
                 "This document explains the purpose of each table and why key attributes exist.\n\n"]

    for table_name, columns in tables.items():

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """You are a database architect. For the given table name and list of columns:
1. Explain in 2–4 sentences **why this table exists** in a business context.
2. For each column, explain its purpose in 1 concise sentence.
Output must be Markdown ONLY."""
             ),
            ("user",
             f"Table name: {table_name}\nColumns: {columns}")
        ])

        chain = prompt | llm
        response = chain.invoke({})

        explanation_md = response.content.strip()

        final_doc.append(f"## Table `{table_name}`\n\n")
        final_doc.append(explanation_md)
        final_doc.append("\n\n---\n\n")

    return "".join(final_doc)


# ---------- Version creation / file management ----------
def create_project(user_obj, project_name):
    project = Project(name=project_name, owner=user_obj)
    db.session.add(project)
    db.session.commit()
    # create folder
    project_dir_path = project_dir(user_obj.id, project.id)
    meta = {"name": project_name, "created_at": project.created_at.isoformat(), "versions": []}
    with open(os.path.join(project_dir_path, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return project

def create_version_for_project(user_obj, project_obj, sql_schema_text, test_suite, mermaid_code=None):
    # determine version number
    version_index = len(project_obj.versions) + 1
    version_name = f"version{version_index}"
    v_dir = version_dir(user_obj.id, project_obj.id, version_name)

    # write schema
    schema_path = os.path.join(v_dir, "schema.sql")
    with open(schema_path, "w") as f:
        f.write(sql_schema_text or "")

    # write tests
    test_path = os.path.join(v_dir, "test_suite.json")
    with open(test_path, "w") as f:
        json.dump(test_suite or [], f, indent=2)

    # write utility.md
    util_path = os.path.join(v_dir, "utility.md")
    util_content = generate_utility_table_from_schema(sql_schema_text or "")
    with open(util_path, "w") as f:
        f.write(util_content)

    # mermaid
    mermaid_path = os.path.join(v_dir, "mermaid.md")
    with open(mermaid_path, "w") as f:
        f.write(mermaid_code or "")

    # create a per-version sqlite DB file
    db_path = os.path.join(v_dir, "backend.db")
    conn = get_sqlite_conn(db_path)
    try:
        if sql_schema_text and sql_schema_text.strip():
            conn.executescript(sql_schema_text)
            conn.commit()
    except Exception as e:
        conn.rollback()
        print("Warning: schema execution failed for new version DB:", e)
    finally:
        conn.close()

    # persist Version record
    version = Version(
        name=version_name,
        project=project_obj,
        schema_file=schema_path,
        test_file=test_path,
        utility_file=util_path,
        mermaid_file=mermaid_path,
        db_file=db_path
    )
    db.session.add(version)
    db.session.commit()
    # update project meta.json
    proj_meta_path = os.path.join(project_dir(user_obj.id, project_obj.id), "meta.json")
    try:
        meta = json.load(open(proj_meta_path))
    except Exception:
        meta = {"name": project_obj.name, "versions": []}
    meta.setdefault("versions", []).append({
        "name": version_name,
        "created_at": version.created_at.isoformat(),
        "schema_file": schema_path,
        "test_file": test_path,
        "utility_file": util_path,
        "db_file": db_path
    })
    with open(proj_meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    return version

def initialize_version_database(schema_path, db_path):
    import sqlite3
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Execute the schema
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()


# ---------- Test and query runners ----------
def run_tests_against_db(db_file, test_suite):
    results = []
    conn = get_sqlite_conn(db_file)
    cur = conn.cursor()

    for t in test_suite:
        name = t.get("name", "<unnamed>")
        sql = t.get("sql", "")
        t_type = t.get("type", "normal")

        try:
            # Start savepoint
            cur.execute("SAVEPOINT test_sp;")

            # Split into individual statements
            statements = [s.strip() for s in sql.split(";") if s.strip()]

            for stmt in statements:
                cur.execute(stmt)

            # Cleanup and rollback to clean state
            cur.execute("ROLLBACK TO test_sp;")
            cur.execute("RELEASE test_sp;")

            results.append({"name": name, "status": "ok", "type": t_type})

        except Exception as e:
            # Ensure cleanup even on failure
            try:
                cur.execute("ROLLBACK TO test_sp;")
                cur.execute("RELEASE test_sp;")
            except:
                pass

            results.append({
                "name": name,
                "status": "error",
                "error": str(e),
                "type": t_type
            })

    conn.close()
    return results


def run_single_query(db_file, sql, commit=False):
    conn = get_sqlite_conn(db_file)
    cur = conn.cursor()

    sql_strip = sql.lstrip().lower()
    savepoint_created = False

    try:
        # READ query
        if sql_strip.startswith("select") or sql_strip.startswith("pragma"):
            cur.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            return {"type": "select", "rows": rows}

        # WRITE query → start savepoint
        cur.execute("SAVEPOINT tmp_sp;")
        savepoint_created = True

        cur.execute(sql)
        affected = cur.rowcount

        if commit:
            conn.commit()
            cur.execute("RELEASE tmp_sp;")
            return {"type": "write", "affected": affected, "note": "committed"}

        else:
            cur.execute("ROLLBACK TO tmp_sp;")
            cur.execute("RELEASE tmp_sp;")
            return {"type": "write", "affected": affected, "note": "rolled back (use commit=True to persist)"}

    except Exception as e:
        # Rollback only if savepoint was created
        if savepoint_created:
            try:
                cur.execute("ROLLBACK TO tmp_sp;")
                cur.execute("RELEASE tmp_sp;")
            except:
                pass

        return {"type": "error", "error": str(e)}

    finally:
        conn.close()


# ---------- LLM-driven schema edits ----------
def ask_llm_modify_schema(old_schema_sql, user_instruction):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a database schema assistant. Given an existing SQL schema and a user's instruction to modify it,
you must output a JSON object with two keys: "edits" and "test_suite".
- "edits" is an array; each element is an object:
  - "action": one of "m" (modify table), "a" (add table), "r" (remove table)
  - "table": affected table name (string)
  - "sql": only for "m" or "a": the full CREATE TABLE statement for the resulting table
  - "rationale": one-sentence explanation
- "test_suite" is an array of test objects with keys: name,type,sql,rationale

Respond with *only* a single ```json block``` containing this object.
"""),
        ("user", f"Here is the current schema:\n\n{old_schema_sql}\n\nInstruction: {user_instruction}")
    ])
    chain = prompt | llm
    try:
        resp = chain.invoke({"old_schema": old_schema_sql, "instruction": user_instruction})
        content = resp.content
        json_text = content.split("```json")[1].split("```")[0].strip()
        parsed = json.loads(json_text)
        return parsed
    except Exception as e:
        print("LLM modification failed:", e)
        return {"error": str(e)}

def _split_create_table_blocks(sql_text):
    tokens = sql_text.split("CREATE TABLE")
    blocks = []
    for t in tokens[1:]:
        try:
            header = t.split("(")[0].strip()
            table_name = header.split()[0].strip('`"')
            if ");" in t:
                sql_block = "CREATE TABLE " + t.split(");", 1)[0] + ");"
            else:
                sql_block = "CREATE TABLE " + t
            blocks.append({"name": table_name, "sql": sql_block.strip()})
        except Exception:
            continue
    return blocks

def apply_llm_edits_and_create_version(user_obj, project_obj, base_version_obj, edits_obj):
    print("editing schema")
    base_schema = ""
    if base_version_obj and base_version_obj.schema_file and os.path.exists(base_version_obj.schema_file):
        base_schema = open(base_version_obj.schema_file).read()
    blocks = {b["name"]: b for b in _split_create_table_blocks(base_schema)}
    edits = edits_obj.get("edits", [])
    for e in edits:
        action = e.get("action")
        tbl = e.get("table")
        if action == "r":
            if tbl in blocks:
                del blocks[tbl]
        elif action in ("m","a"):
            sql = e.get("sql", "")
            if sql:
                blocks[tbl] = {"name": tbl, "sql": sql}
    new_schema = "\n\n".join([b["sql"] for b in blocks.values()])
    new_tests = edits_obj.get("test_suite", [])
    # try to generate mermaid for new schema
    try:
        mermaid = sql_to_mermaid(new_schema)
    except Exception:
        mermaid = ""
    new_version = create_version_for_project(user_obj, project_obj, new_schema, new_tests, mermaid)
    return new_version

# ---------- Flask routes ----------
@app.route("/")
def index():
    return render_template("index.html")

# Auth
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        u = User(username=username, password_hash=hashed)
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists.", "warning")
            return redirect(url_for("register"))
        # create user data dir
        user_dir(u.id)
        session["user_id"] = u.id
        flash("Registered and logged in.", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            flash("Logged in.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))

# Dashboard - list user's projects
@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    projects = user.projects
    return render_template("dashboard.html", projects=projects, user=user)

# Create project
@app.route("/projects/create", methods=["GET","POST"])
@login_required
def create_project_route():
    if request.method == "POST":
        name = request.form.get("project_name") or f"project_{datetime.datetime.utcnow().isoformat()}"
        user = User.query.get(session["user_id"])
        project = create_project(user, name)
        flash("Project created.", "success")
        return redirect(url_for("project_detail", project_id=project.id))
    return render_template("create_project.html")

# Project detail
@app.route("/project/<int:project_id>")
@login_required
def project_detail(project_id):
    user = User.query.get(session["user_id"])
    project = Project.query.get_or_404(project_id)
    if project.user_id != user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    # get versions
    versions = project.versions
    return render_template("project_detail.html", project=project, versions=versions)

# Create version (from schema text or by uploading .sql)
@app.route("/project/<int:project_id>/versions/create", methods=["GET","POST"])
@login_required
def create_version_route(project_id):
    user = User.query.get(session["user_id"])
    project = Project.query.get_or_404(project_id)
    if project.user_id != user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        # prefer uploaded file if provided
        uploaded = request.files.get("sql_file")
        prompt = request.form.get("prompt")
        if uploaded and uploaded.filename:
            sql_text = uploaded.read().decode("utf-8")
            mermaid = sql_to_mermaid(sql_text)
            test_suite = generate_test_suite(sql_text)
            version = create_version_for_project(user, project, sql_text, test_suite, mermaid)
            flash("Version created from uploaded SQL.", "success")
            return redirect(url_for("version_detail", version_id=version.id))
        elif prompt and prompt.strip():
            # generate schema + mermaid via LLM
            sql_text, mermaid = generate_schema_and_diagram(prompt.strip())
            test_suite = []
            if "Error:" not in sql_text:
                test_suite = generate_test_suite(sql_text)
            version = create_version_for_project(user, project, sql_text, test_suite, mermaid)
            flash("Version created from prompt.", "success")
            return redirect(url_for("version_detail", version_id=version.id))
        else:
            flash("Provide a prompt or an SQL file.", "warning")
    return render_template("create_version.html", project=project)

# Version detail / workspace
@app.route("/version/<int:version_id>")
@login_required
def version_detail(version_id):
    user = User.query.get(session["user_id"])
    version = Version.query.get_or_404(version_id)
    project = version.project
    if project.user_id != user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    # load files
    schema = open(version.schema_file).read() if version.schema_file and os.path.exists(version.schema_file) else ""
    tests = []
    if version.test_file and os.path.exists(version.test_file):
        try:
            tests = json.load(open(version.test_file))
        except Exception:
            tests = []
    utility = open(version.utility_file).read() if version.utility_file and os.path.exists(version.utility_file) else ""
    mermaid = sql_to_mermaid(schema) if schema else schema
    print(mermaid)
    return render_template("version_detail.html", project=project, version=version, schema=schema, tests=tests, utility=utility, mermaid=mermaid)

# Run single SQL (AJAX)
@app.route("/version/<int:version_id>/run_query", methods=["POST"])
@login_required
def version_run_query(version_id):
    user = User.query.get(session["user_id"])
    version = Version.query.get_or_404(version_id)
    if version.project.user_id != user.id:
        return jsonify({"error":"unauthorized"}), 403
    sql = request.json.get("sql", "")
    commit = bool(request.json.get("commit", False))
    result = run_single_query(version.db_file, sql, commit=commit)
    return jsonify(result)

# Run tests
@app.route("/version/<int:version_id>/run_tests", methods=["POST"])
@login_required
def version_run_tests(version_id):
    user = User.query.get(session["user_id"])
    version = Version.query.get_or_404(version_id)
    if version.project.user_id != user.id:
        return jsonify({"error":"unauthorized"}), 403
    try:
        tests = json.load(open(version.test_file)) if version.test_file and os.path.exists(version.test_file) else []
    except Exception:
        tests = []
    results = run_tests_against_db(version.db_file, tests)
    return jsonify({"results": results})

# Modify schema via LLM edits -> creates new version
@app.route("/version/<int:version_id>/modify_schema", methods=["POST"])
@login_required
def version_modify_schema(version_id):
    user = User.query.get(session["user_id"])
    base_version = Version.query.get_or_404(version_id)
    if base_version.project.user_id != user.id:
        return jsonify({"error":"unauthorized"}), 403
    instruction = request.json.get("instruction", "")
    if not instruction:
        return jsonify({"error":"instruction missing"}), 400
    old_schema = open(base_version.schema_file).read() if base_version.schema_file and os.path.exists(base_version.schema_file) else ""
    llm_resp = ask_llm_modify_schema(old_schema, instruction)
    if "error" in llm_resp:
        return jsonify({"error": llm_resp["error"]}), 500
    new_version = apply_llm_edits_and_create_version(user, base_version.project, base_version, llm_resp)
    return jsonify({"new_version_id": new_version.id, "new_version_name": new_version.name})

# Download files from a version
@app.route("/version/<int:version_id>/download/<path:filename>")
@login_required
def version_download_file(version_id, filename):
    user = User.query.get(session["user_id"])
    version = Version.query.get_or_404(version_id)
    if version.project.user_id != user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    v_dir = os.path.dirname(version.schema_file) if version.schema_file else None
    if not v_dir or not os.path.exists(os.path.join(v_dir, filename)):
        flash("File not found", "warning")
        return redirect(url_for("version_detail", version_id=version.id))
    return send_from_directory(v_dir, filename, as_attachment=True)

# Misc: delete project (caution)
@app.route("/project/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    user = User.query.get(session["user_id"])
    project = Project.query.get_or_404(project_id)
    if project.user_id != user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    # remove folder on disk
    projdir = project_dir(user.id, project.id)
    try:
        shutil.rmtree(projdir)
    except Exception as e:
        print("Warning: deleting project folder failed:", e)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("dashboard"))
@app.route("/delete_version/<int:project_id>/<int:version_id>", methods=["POST"])
@login_required
def delete_version(project_id, version_id):
    user_id = session["user_id"]

    version = Version.query.filter_by(id=version_id, project_id=project_id).first()
    if not version:
        flash("Version not found.", "error")
        return redirect(url_for("view_project", project_id=project_id))

    # Delete version folder from disk
    v_dir = version_dir(user_id, project_id, version.name)
    if os.path.exists(v_dir):
        shutil.rmtree(v_dir)

    # Delete from DB
    db.session.delete(version)
    db.session.commit()

    flash(f"Version '{version.name}' deleted.", "success")
    return redirect(url_for("project_detail", project_id=project_id))

if __name__ == "__main__":
    app.run(debug=True)
