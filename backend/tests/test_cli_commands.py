"""Exercises the actual `flask <command>` CLI wrappers via Flask's test
CLI runner - the underlying business functions (seed_data, register_model,
promote_to_admin, seed_recommendation_data) already have their own direct
unit tests; this file covers the click.command layer itself (argument
parsing, option defaults, the echoed confirmation message), which was
previously only ever exercised by manually running `flask ...` by hand.
"""

import json
from datetime import date

from app.models import AIModelFile, Exercise, SriLankanFood, User


def test_seed_command_loads_real_reference_data(app, db):
    result = app.test_cli_runner().invoke(args=["seed"])

    assert result.exit_code == 0
    assert "Database seeded." in result.output
    assert SriLankanFood.query.count() > 0
    assert Exercise.query.count() > 0


def test_seed_recommendations_command_loads_real_datasets(app, db):
    result = app.test_cli_runner().invoke(args=["seed-recommendations"])

    assert result.exit_code == 0
    assert "Loaded" in result.output
    assert "meal records" in result.output
    assert "workout records" in result.output


def test_register_model_command_registers_and_echoes_summary(app, db, tmp_path):
    metadata = {
        "version": "v_cli_test",
        "file_path": "ai_model/saved_models/v_cli_test.keras",
        "accuracy": 0.6,
        "trained_date": "2026-01-01T00:00:00+00:00",
    }
    metadata_path = tmp_path / "v_cli_test.json"
    metadata_path.write_text(json.dumps(metadata))

    result = app.test_cli_runner().invoke(args=["register-model", str(metadata_path)])

    assert result.exit_code == 0
    assert "Registered model v_cli_test" in result.output
    assert AIModelFile.query.filter_by(version="v_cli_test").first() is not None


def test_promote_admin_command_promotes_existing_user(app, db):
    user = User(
        full_name="CLI Test User",
        date_of_birth=date(1995, 1, 1),
        age=29,
        gender="male",
        email="cli_promote@example.com",
        username="cli_promote_user",
        password_hash="x",
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    result = app.test_cli_runner().invoke(args=["promote-admin", "cli_promote@example.com"])

    assert result.exit_code == 0
    assert "is now an admin" in result.output
    assert User.query.filter_by(username="cli_promote_user").first().role == "admin"


def test_promote_admin_command_reports_error_for_unknown_email(app, db):
    result = app.test_cli_runner().invoke(args=["promote-admin", "nobody@example.com"])

    assert result.exit_code != 0
