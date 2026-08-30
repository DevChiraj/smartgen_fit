"""CLI command: registers a Module 9 trained model into ai_model_files.

    flask register-model ai_model/saved_models/v20260719_120000.json
"""

import click

from app.services.ai_model_registration_service import register_model


def register_model_command(app):
    @app.cli.command("register-model")
    @click.argument("metadata_path")
    def register_model_cli(metadata_path):
        model_file = register_model(metadata_path)
        click.echo(
            f"Registered model {model_file.version} "
            f"(id={model_file.model_id}, accuracy={model_file.accuracy}, active=True)"
        )
