from __future__ import annotations

import socket
import threading
import webbrowser
from decimal import Decimal, InvalidOperation
from typing import Callable

import oracledb
from flask import Flask, flash, redirect, render_template_string, request, session, url_for

from bank_db import BankClientError, OracleBankClient, QueryResult

DEFAULT_ORACLE_USER = "dbbook"
DEFAULT_ORACLE_PASSWORD = "password"
DEFAULT_ORACLE_HOST = "192.168.8.246"
DEFAULT_ORACLE_PORT = 1521
DEFAULT_ORACLE_SERVICE_NAME = "xepdb1"
DEFAULT_DATASET = "Persons"

app = Flask(__name__)
app.config["SECRET_KEY"] = "bank-gui-local-secret"

client = OracleBankClient()

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bank Procedure GUI</title>
  <style>
    body { margin: 0; padding: 24px; font-family: "Segoe UI", Tahoma, sans-serif; color: #1c2430; background: linear-gradient(180deg, #f9fbff 0%, #eef3fb 100%); }
    h1, h2, h3 { margin: 0 0 10px; } p { margin: 0 0 12px; color: #5d6979; }
    .page, .stack, form { display: grid; gap: 12px; } .page { gap: 16px; }
    .hero, .card { background: #fff; border: 1px solid #d8deea; border-radius: 18px; box-shadow: 0 16px 40px rgba(18,35,66,.08); }
    .hero, .card { padding: 18px; } .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
    .form-grid { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }
    .actions, .status { display: flex; gap: 10px; flex-wrap: wrap; align-items: end; }
    label { display: grid; gap: 6px; font-size: 14px; font-weight: 600; }
    input, select, button, textarea { width: 100%; border: 1px solid #d8deea; border-radius: 12px; padding: 10px 12px; font: inherit; background: #fff; color: #1c2430; box-sizing: border-box; }
    textarea { resize: vertical; min-height: 84px; } button { width: auto; cursor: pointer; background: #1b5cff; color: white; border: 0; font-weight: 700; }
    button.secondary { background: #e8efff; color: #1b5cff; }
    .pill { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px; font-size: 14px; font-weight: 600; }
    .good { background: #e7f7ed; color: #117a37; } .bad { background: #fdeaea; color: #a12b2b; }
    .messages { display: grid; gap: 10px; } .message { padding: 12px 14px; border-radius: 14px; font-weight: 600; }
    .message.success { background: #e7f7ed; color: #117a37; } .message.error { background: #fdeaea; color: #a12b2b; }
    .small { font-size: 13px; color: #5d6979; }
    .table-wrap { overflow: auto; border: 1px solid #d8deea; border-radius: 14px; }
    table { width: 100%; border-collapse: collapse; min-width: 720px; background: white; }
    th, td { padding: 10px 12px; border-bottom: 1px solid #d8deea; text-align: left; vertical-align: top; font-size: 14px; }
    th { position: sticky; top: 0; background: #f2f6fc; }
  </style>
</head>
<body>
{% macro render_result(result, empty_message='No rows to show.') -%}
  <div class="table-wrap">
    {% if result and result.columns %}
      <table>
        <thead><tr>{% for column in result.columns %}<th>{{ column }}</th>{% endfor %}</tr></thead>
        <tbody>
          {% if result.rows %}
            {% for row in result.rows %}
              <tr>{% for value in row %}<td>{{ "" if value is none else value }}</td>{% endfor %}</tr>
            {% endfor %}
          {% else %}
            <tr><td colspan="{{ result.columns|length }}" class="small">{{ empty_message }}</td></tr>
          {% endif %}
        </tbody>
      </table>
    {% else %}
      <div style="padding:16px;" class="small">{{ empty_message }}</div>
    {% endif %}
  </div>
{%- endmacro %}

<div class="page">
  <section class="hero">
    <div>
      <h1>Bank Procedure GUI</h1>
      {% if god_mode %}
        <p>GOD mode shows the full toolbox view.</p>
      {% elif logged_in %}
        <p>Role-based view for the logged-in person.</p>
      {% else %}
        <p>Log in with one p-tal. Type <code>GOD</code> for the full toolbox view.</p>
      {% endif %}
    </div>
    <div class="status">
      <span class="pill {{ 'good' if connected else 'bad' }}">{{ 'Connected' if connected else 'Disconnected' }}</span>
      {% if god_mode %}
        <span class="pill good">GOD</span>
      {% elif logged_in and user_profile %}
        <span class="pill good">{{ user_profile.access_type }}</span>
        <span class="small">{{ user_profile.full_name or user_profile.p_tal }}</span>
        <span class="small">p_id {{ user_profile.person_id }}</span>
        <span class="small">p-tal {{ user_profile.p_tal }}</span>
      {% endif %}
      <span class="small">User {{ oracle_user }}</span>
      <span class="small">{{ oracle_host }}:{{ oracle_port }}/{{ oracle_service_name }}</span>
      <span class="small">Birth mode {{ birth_mode }}</span>
    </div>
    {% if connect_error %}<div class="message error">{{ connect_error }}</div>{% endif %}
    {% if not logged_in %}
      <form method="post" action="{{ url_for('login') }}" class="actions">
        <label style="min-width:280px;">P-tal or GOD<input type="text" name="login_code" placeholder="250300514"></label>
        <div><button type="submit">Log in</button></div>
      </form>
      <p class="small">Use digits only for p-tal.</p>
    {% else %}
      <div class="actions">
        <form method="post" action="{{ url_for('reconnect') }}"><button type="submit">Reconnect</button></form>
        <form method="post" action="{{ url_for('logout') }}"><button type="submit" class="secondary">Log out</button></form>
      </div>
    {% endif %}
  </section>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      <section class="messages">
        {% for category, message in messages %}
          <div class="message {{ category }}">{{ message }}</div>
        {% endfor %}
      </section>
    {% endif %}
  {% endwith %}

  {% if god_mode %}
    <section class="card stack">
      <h2>Dataset Browser</h2>
      <form method="get" action="{{ url_for('index') }}" class="actions">
        <label>Dataset
          <select name="dataset">
            {% for dataset_name in dataset_names %}
              <option value="{{ dataset_name }}" {% if dataset_name == selected_dataset %}selected{% endif %}>{{ dataset_name }}</option>
            {% endfor %}
          </select>
        </label>
        <div><button type="submit">Load dataset</button></div>
      </form>
      {% if dataset_error %}<div class="message error">{{ dataset_error }}</div>{% endif %}
      {{ render_result(result, 'No columns to show yet.') }}
    </section>

    <section class="card stack">
      <h2>Person Lookup</h2>
      <form method="get" action="{{ url_for('index') }}" class="actions">
        <label>P-tal<input type="text" name="lookup_ptal" value="{{ lookup_ptal or '' }}" placeholder="250300514"></label>
        <input type="hidden" name="dataset" value="{{ selected_dataset }}">
        <div><button type="submit">Load person dashboard</button></div>
      </form>
      {% if person_lookup_error %}<div class="message error">{{ person_lookup_error }}</div>{% endif %}
      {% if person_dashboard %}
        {% for section in person_dashboard.sections %}
          <div class="stack">
            <div style="font-weight:700;">{{ section.title }}</div>
            {{ render_result(section.result, 'No rows for this person.') }}
          </div>
        {% endfor %}
      {% endif %}
    </section>

    <section class="grid">
      <article class="card"><h2>Setup</h2><form method="post" action="{{ url_for('seed_defaults') }}"><button type="submit">Seed defaults</button></form></article>
      <article class="card">
        <h2>Create Person</h2>
        <form method="post" action="{{ url_for('create_person') }}">
          <div class="form-grid">
            <label>First name<input type="text" name="first_name"></label>
            <label>Last name<input type="text" name="last_name"></label>
            <label>Birth date<input type="text" name="birth_date" placeholder="01011990"></label>
            <label>Gender<select name="gender"><option value="m">m</option><option value="k">k</option></select></label>
            <label>Bustad id<input type="number" name="bustad_id" value="1"></label>
          </div>
          <button type="submit">Create person</button>
        </form>
      </article>
      <article class="card">
        <h2>Create Customer</h2>
        <form method="post" action="{{ url_for('create_customer') }}">
          <div class="form-grid">
            <label>Person id<input type="number" name="person_id"></label>
            <label>Password<input type="text" name="password"></label>
          </div>
          <button type="submit">Create customer</button>
        </form>
      </article>
      <article class="card">
        <h2>Create Account</h2>
        <form method="post" action="{{ url_for('create_account') }}">
          <div class="form-grid">
            <label>Customer id<input type="number" name="customer_id"></label>
            <label>Account type<select name="account_type"><option value="000">000</option><option value="100">100</option><option value="200" selected>200</option><option value="300">300</option><option value="400">400</option></select></label>
          </div>
          <button type="submit">Create account</button>
        </form>
      </article>
      <article class="card">
        <h2>Bootstrap First Admin</h2>
        <form method="post" action="{{ url_for('bootstrap_admin') }}">
          <div class="form-grid">
            <label>Person id<input type="number" name="person_id"></label>
            <label>Title<input type="text" name="title" value="Leidari"></label>
            <label>Salary<input type="text" name="salary" value="30000"></label>
          </div>
          <button type="submit">Bootstrap admin</button>
        </form>
      </article>
      <article class="card">
        <h2>Family</h2>
        <form method="post" action="{{ url_for('create_marriage') }}"><div class="form-grid"><label>Person 1 id<input type="number" name="person_one_id"></label><label>Person 2 id<input type="number" name="person_two_id"></label></div><button type="submit">Create marriage</button></form>
        <form method="post" action="{{ url_for('end_marriage') }}"><div class="form-grid"><label>Person 1 id<input type="number" name="person_one_id"></label><label>Person 2 id<input type="number" name="person_two_id"></label></div><button type="submit" class="secondary">End marriage</button></form>
        <form method="post" action="{{ url_for('add_child') }}"><div class="form-grid"><label>Parent 1 id<input type="number" name="parent_one_id"></label><label>Parent 2 id<input type="number" name="parent_two_id"></label><label>Child id<input type="number" name="child_id"></label></div><button type="submit">Add child</button></form>
      </article>
      <article class="card">
        <h2>Staff</h2>
        <form method="post" action="{{ url_for('create_staff') }}"><div class="form-grid"><label>Admin person id<input type="number" name="admin_person_id"></label><label>Person id<input type="number" name="person_id"></label><label>Title<input type="text" name="title"></label><label>Salary<input type="text" name="salary"></label></div><button type="submit">Create staff</button></form>
        <form method="post" action="{{ url_for('update_staff') }}"><div class="form-grid"><label>Admin staff person id<input type="number" name="admin_staff_id"></label><label>Staff person id<input type="number" name="staff_id"></label><label>New title<input type="text" name="title"></label><label>New salary<input type="text" name="salary"></label><label>New access type<input type="text" name="access_type" placeholder="ADMIN"></label></div><button type="submit" class="secondary">Update staff role</button></form>
      </article>
      <article class="card">
        <h2>Drafts</h2>
        <form method="post" action="{{ url_for('create_draft') }}"><div class="form-grid"><label>User person id<input type="number" name="user_person_id"></label><label>Amount<input type="text" name="amount"></label><label>Draft type<select name="draft_type"><option value="FLYTING" selected>FLYTING</option><option value="INNSETING">INNSETING</option><option value="UTTOKA">UTTOKA</option></select></label><label>From account<input type="text" name="from_account"></label><label>To account<input type="text" name="to_account"></label></div><label>Own text<textarea name="own_text"></textarea></label><label>Recipient text<textarea name="recipient_text"></textarea></label><button type="submit">Create draft</button></form>
        <form method="post" action="{{ url_for('book_draft') }}"><div class="form-grid"><label>Staff person id<input type="number" name="staff_id"></label><label>Draft id<input type="number" name="draft_id"></label></div><button type="submit">Book draft</button></form>
        <form method="post" action="{{ url_for('reject_draft') }}"><div class="form-grid"><label>Staff person id<input type="number" name="staff_id"></label><label>Draft id<input type="number" name="draft_id"></label></div><button type="submit" class="secondary">Reject draft</button></form>
      </article>
    </section>
  {% elif logged_in and user_profile %}
    <section class="card stack">
      <h2>My Views</h2>
      {% if person_lookup_error %}<div class="message error">{{ person_lookup_error }}</div>{% endif %}
      {% if person_dashboard %}
        {% for section in person_dashboard.sections %}
          <div class="stack">
            <div style="font-weight:700;">{{ section.title }}</div>
            {{ render_result(section.result, 'No rows in this view for this person.') }}
          </div>
        {% endfor %}
      {% endif %}
    </section>

    <section class="grid">
      <article class="card">
        <h2>Create Draft</h2>
        {% if user_profile.is_customer %}
          <form method="post" action="{{ url_for('create_draft') }}">
            <div class="form-grid">
              <label>Amount<input type="text" name="amount"></label>
              <label>Draft type<select name="draft_type"><option value="FLYTING" selected>FLYTING</option><option value="INNSETING">INNSETING</option><option value="UTTOKA">UTTOKA</option></select></label>
              <label>From account<input type="text" name="from_account"></label>
              <label>To account<input type="text" name="to_account"></label>
            </div>
            <label>Own text<textarea name="own_text"></textarea></label>
            <label>Recipient text<textarea name="recipient_text"></textarea></label>
            <button type="submit">Create draft</button>
          </form>
        {% else %}
          <p class="small">This person is not a customer, so draft creation is hidden.</p>
        {% endif %}
      </article>

      {% if user_profile.is_staff %}
        <article class="card">
          <h2>Draft Work Queue</h2>
          {{ render_result(draft_queue, 'No draft rows found.') }}
          <form method="post" action="{{ url_for('book_draft') }}"><div class="form-grid"><label>Draft id<input type="number" name="draft_id"></label></div><button type="submit">Book draft</button></form>
          <form method="post" action="{{ url_for('reject_draft') }}"><div class="form-grid"><label>Draft id<input type="number" name="draft_id"></label></div><button type="submit" class="secondary">Reject draft</button></form>
        </article>
      {% endif %}

      {% if user_profile.is_admin %}
        <article class="card">
          <h2>Admin Actions</h2>
          <form method="post" action="{{ url_for('create_staff') }}"><div class="form-grid"><label>Person id<input type="number" name="person_id"></label><label>Title<input type="text" name="title"></label><label>Salary<input type="text" name="salary"></label></div><button type="submit">Create staff</button></form>
          <form method="post" action="{{ url_for('update_staff') }}"><div class="form-grid"><label>Staff person id<input type="number" name="staff_id"></label><label>New title<input type="text" name="title"></label><label>New salary<input type="text" name="salary"></label><label>New access type<input type="text" name="access_type" placeholder="ADMIN"></label></div><button type="submit" class="secondary">Update staff role</button></form>
        </article>
      {% endif %}
    </section>
  {% endif %}
</div>
</body>
</html>
"""


def _connect(force: bool = False) -> str:
    if force and client.is_connected:
        client.close()
    if client.is_connected:
        return client.birth_mode
    dsn = oracledb.makedsn(DEFAULT_ORACLE_HOST, DEFAULT_ORACLE_PORT, service_name=DEFAULT_ORACLE_SERVICE_NAME)
    return client.connect(DEFAULT_ORACLE_USER, DEFAULT_ORACLE_PASSWORD, dsn)


def _is_god() -> bool:
    return session.get("mode") == "god"


def _session_profile() -> dict | None:
    return session.get("user_profile")


def _is_logged_in() -> bool:
    return _is_god() or _session_profile() is not None


def _current_profile(refresh: bool = False) -> dict | None:
    if _is_god():
        return None
    profile = _session_profile()
    if not profile:
        return None
    if refresh:
        profile = client.fetch_login_profile(str(profile["p_tal"]))
        session["user_profile"] = profile
    return profile


def _redirect_target(dataset: str | None = None) -> str:
    if _is_god():
        return url_for("index", dataset=dataset or _current_dataset())
    return url_for("index")


def _run_action(label: str, action: Callable[[], None], dataset: str | None = None):
    try:
        _connect(force=True)
        if not _is_god() and _session_profile():
            _current_profile(refresh=True)
        action()
        flash(f"{label} succeeded.", "success")
    except Exception as exc:
        flash(f"{label} failed: {exc}", "error")
    return redirect(_redirect_target(dataset))


def _current_dataset() -> str:
    requested = request.args.get("dataset") or request.form.get("dataset") or DEFAULT_DATASET
    return requested if requested in OracleBankClient.DATASETS else DEFAULT_DATASET


def _require_god() -> None:
    if not _is_god():
        raise BankClientError("Only GOD mode can use this action.")


def _require_logged_in() -> dict:
    if _is_god():
        raise BankClientError("GOD mode does not use a person profile for this action.")
    profile = _current_profile(refresh=False)
    if not profile:
        raise BankClientError("Log in with a valid p-tal first.")
    return profile


def _require_staff() -> dict:
    profile = _require_logged_in()
    if not profile.get("is_staff"):
        raise BankClientError("Only staff or admin can do this.")
    return profile


def _require_admin() -> dict:
    profile = _require_logged_in()
    if not profile.get("is_admin"):
        raise BankClientError("Only admin can do this.")
    return profile


def _required_str(name: str) -> str:
    value = request.form.get(name, "").strip()
    if not value:
        raise BankClientError(f"{name.replace('_', ' ').title()} is required.")
    return value


def _optional_str(name: str) -> str | None:
    value = request.form.get(name, "").strip()
    return value or None


def _required_int(name: str) -> int:
    raw_value = _required_str(name)
    try:
        return int(raw_value)
    except ValueError as exc:
        raise BankClientError(f"{name.replace('_', ' ').title()} must be a whole number.") from exc


def _optional_int(name: str) -> int | None:
    raw_value = _optional_str(name)
    if raw_value is None:
        return None
    try:
        return int(raw_value)
    except ValueError as exc:
        raise BankClientError(f"{name.replace('_', ' ').title()} must be a whole number.") from exc


def _required_decimal(name: str) -> Decimal:
    raw_value = _required_str(name)
    try:
        return Decimal(raw_value)
    except InvalidOperation as exc:
        raise BankClientError(f"{name.replace('_', ' ').title()} must be numeric.") from exc


def _optional_decimal(name: str) -> Decimal | None:
    raw_value = _optional_str(name)
    if raw_value is None:
        return None
    try:
        return Decimal(raw_value)
    except InvalidOperation as exc:
        raise BankClientError(f"{name.replace('_', ' ').title()} must be numeric.") from exc


@app.get("/")
def index():
    selected_dataset = _current_dataset()
    lookup_ptal = (request.args.get("lookup_ptal") or "").strip()
    connected = False
    connect_error = None
    dataset_error = None
    person_lookup_error = None
    result = QueryResult(columns=[], rows=[])
    person_dashboard = None
    draft_queue = None
    user_profile = _session_profile()
    god_mode = _is_god()

    try:
        _connect(force=True)
        connected = client.is_connected
        if god_mode:
            result = client.fetch_dataset(selected_dataset)
            if lookup_ptal:
                person_dashboard = client.fetch_person_dashboard(lookup_ptal)
        elif user_profile:
            user_profile = _current_profile(refresh=True)
            person_dashboard = client.fetch_person_dashboard(str(user_profile["p_tal"]))
            if user_profile.get("is_staff"):
                draft_queue = client.fetch_dataset("Drafts")
    except Exception as exc:
        connected = client.is_connected
        if god_mode:
            if lookup_ptal and result.columns:
                person_lookup_error = str(exc)
            else:
                dataset_error = str(exc)
                if not connected:
                    connect_error = str(exc)
        elif user_profile:
            person_lookup_error = str(exc)
            if not connected:
                connect_error = str(exc)
        else:
            connect_error = str(exc)

    return render_template_string(
        TEMPLATE,
        connected=connected,
        logged_in=_is_logged_in(),
        god_mode=god_mode,
        birth_mode=client.birth_mode,
        connect_error=connect_error,
        dataset_error=dataset_error,
        dataset_names=list(OracleBankClient.DATASETS.keys()),
        selected_dataset=selected_dataset,
        lookup_ptal=lookup_ptal,
        person_dashboard=person_dashboard,
        person_lookup_error=person_lookup_error,
        result=result,
        draft_queue=draft_queue,
        user_profile=user_profile,
        oracle_user=DEFAULT_ORACLE_USER,
        oracle_host=DEFAULT_ORACLE_HOST,
        oracle_port=DEFAULT_ORACLE_PORT,
        oracle_service_name=DEFAULT_ORACLE_SERVICE_NAME,
    )


@app.post("/login")
def login():
    login_code = _required_str("login_code")
    try:
        _connect(force=True)
        session.clear()
        if login_code.upper() == "GOD":
            session["mode"] = "god"
            flash("Logged in as GOD.", "success")
        else:
            profile = client.fetch_login_profile(login_code)
            session["mode"] = "user"
            session["user_profile"] = profile
            flash(f"Logged in as {profile['full_name'] or profile['p_tal']} ({profile['access_type']}).", "success")
    except Exception as exc:
        flash(f"Login failed: {exc}", "error")
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("index"))


@app.post("/reconnect")
def reconnect():
    try:
        birth_mode = _connect(force=True)
        if not _is_god() and _session_profile():
            _current_profile(refresh=True)
        flash(f"Connected to Oracle. Birth mode detected as {birth_mode}.", "success")
    except Exception as exc:
        flash(f"Reconnect failed: {exc}", "error")
    return redirect(_redirect_target(_current_dataset()))


@app.post("/seed-defaults")
def seed_defaults():
    return _run_action("Seed defaults", lambda: (_require_god(), client.seed_defaults()), "Account types")


@app.post("/create-person")
def create_person():
    return _run_action(
        "Create person",
        lambda: (_require_god(), client.create_person(_required_str("first_name"), _required_str("last_name"), _required_str("birth_date"), _required_str("gender"), _required_int("bustad_id"))),
        "Persons",
    )


@app.post("/create-customer")
def create_customer():
    return _run_action(
        "Create customer",
        lambda: (_require_god(), client.create_customer(_required_int("person_id"), _required_str("password"))),
        "Customers",
    )


@app.post("/create-account")
def create_account():
    return _run_action(
        "Create account",
        lambda: (_require_god(), client.create_account(_required_int("customer_id"), _required_str("account_type"))),
        "Accounts",
    )


@app.post("/bootstrap-admin")
def bootstrap_admin():
    return _run_action(
        "Bootstrap admin",
        lambda: (_require_god(), client.bootstrap_admin(_required_int("person_id"), _required_str("title"), _required_decimal("salary"))),
        "Staff",
    )


@app.post("/create-marriage")
def create_marriage():
    return _run_action(
        "Create marriage",
        lambda: (_require_god(), client.marry(_required_int("person_one_id"), _required_int("person_two_id"))),
        "Marriages",
    )


@app.post("/end-marriage")
def end_marriage():
    return _run_action(
        "End marriage",
        lambda: (_require_god(), client.divorce(_required_int("person_one_id"), _required_int("person_two_id"))),
        "Marriages",
    )


@app.post("/add-child")
def add_child():
    return _run_action(
        "Add child",
        lambda: (_require_god(), client.add_child(_required_int("parent_one_id"), _optional_int("parent_two_id"), _required_int("child_id"))),
        "Children",
    )


@app.post("/create-staff")
def create_staff():
    def action() -> None:
        if _is_god():
            client.create_staff(_required_int("admin_person_id"), _required_int("person_id"), _required_str("title"), _required_decimal("salary"))
            return
        profile = _require_admin()
        client.create_staff(int(profile["person_id"]), _required_int("person_id"), _required_str("title"), _required_decimal("salary"))

    return _run_action("Create staff", action, "Staff")


@app.post("/update-staff")
def update_staff():
    def action() -> None:
        if _is_god():
            client.update_staff(_required_int("admin_staff_id"), _required_int("staff_id"), _optional_str("title"), _optional_decimal("salary"), _optional_str("access_type"))
            return
        profile = _require_admin()
        client.update_staff(int(profile["person_id"]), _required_int("staff_id"), _optional_str("title"), _optional_decimal("salary"), _optional_str("access_type"))

    return _run_action("Update staff", action, "Staff")


@app.post("/create-draft")
def create_draft():
    def action() -> None:
        if _is_god():
            client.create_draft(_required_int("user_person_id"), _required_decimal("amount"), _optional_str("from_account"), _optional_str("to_account"), _optional_str("own_text"), _optional_str("recipient_text"), _required_str("draft_type"))
            return
        profile = _require_logged_in()
        client.create_draft(int(profile["person_id"]), _required_decimal("amount"), _optional_str("from_account"), _optional_str("to_account"), _optional_str("own_text"), _optional_str("recipient_text"), _required_str("draft_type"))

    return _run_action("Create draft", action, "Drafts")


@app.post("/book-draft")
def book_draft():
    def action() -> None:
        if _is_god():
            client.book_draft(_required_int("staff_id"), _required_int("draft_id"))
            return
        profile = _require_staff()
        client.book_draft(int(profile["person_id"]), _required_int("draft_id"))

    return _run_action("Book draft", action, "Drafts")


@app.post("/reject-draft")
def reject_draft():
    def action() -> None:
        if _is_god():
            client.reject_draft(_required_int("staff_id"), _required_int("draft_id"))
            return
        profile = _require_staff()
        client.reject_draft(int(profile["person_id"]), _required_int("draft_id"))

    return _run_action("Reject draft", action, "Drafts")


def _find_open_port(preferred: int = 8765) -> int:
    for port in range(preferred, preferred + 25):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("Could not find a free localhost port for the GUI.")


if __name__ == "__main__":
    port = _find_open_port()
    url = f"http://127.0.0.1:{port}/"
    print(f"Starting bank GUI at {url}")
    try:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    except Exception:
        pass
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=False)
