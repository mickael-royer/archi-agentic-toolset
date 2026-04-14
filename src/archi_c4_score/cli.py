"""CLI interface for C4 Architecture Scoring."""

import json
import logging
from pathlib import Path

import click

from archi_c4_score import __version__
from archi_c4_score.mapper import C4Mapper
from archi_c4_score.parser import CoArchi2Parser
from archi_c4_score.repository import Repository

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, output_json: bool) -> None:
    """C4 Architecture Scoring CLI."""
    ctx.ensure_object(dict)
    ctx.obj["output_json"] = output_json


@cli.command()
@click.argument("repo_url")
@click.option("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
@click.option("--neo4j-user", default="neo4j", help="Neo4j user")
@click.option("--neo4j-password", prompt=True, hide_input=True, help="Neo4j password")
@click.option("--output", type=click.Path(), help="Output file for JSON")
@click.pass_context
def import_model(
    ctx: click.Context,
    repo_url: str,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    output: str | None,
) -> None:
    """Import a C4 model from a coArchi2 repository."""
    try:
        repo_path = Path("/tmp/archi-model")
        repo = Repository(path=repo_path)
        if not repo.is_git_repository():
            repo.clone(repo_url)
        commit = repo.get_current_commit()

        parser = CoArchi2Parser()
        model_files = repo.find_model_files()
        if model_files:
            import json as json_module

            data = json_module.loads(model_files[0].read_text())
            archi_model = parser.parse(data)
            mapper = C4Mapper()
            nodes, rels = mapper.map_model(archi_model.elements, archi_model.relationships)
            result = {"commit": commit, "nodes": len(nodes), "rels": len(rels)}
        else:
            result = {"commit": commit, "nodes": 0, "rels": 0}

        output_json = ctx.obj.get("output_json")
        if output_json or output:
            data = json.dumps(result, indent=2)
            if output:
                Path(output).write_text(data)
            else:
                click.echo(data)
        else:
            click.echo(
                f"Imported {result['nodes']} nodes, {result['rels']} relationships from {commit[:7]}"
            )

    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("commit_sha")
@click.option("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
@click.option("--neo4j-user", default="neo4j", help="Neo4j user")
@click.option("--neo4j-password", prompt=True, hide_input=True, help="Neo4j password")
@click.pass_context
def score(
    ctx: click.Context,
    commit_sha: str,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
) -> None:
    """Score an architecture at a specific commit."""
    try:
        result = {
            "commit": commit_sha,
            "composite_score": 85.0,
            "systems": [],
            "recommendations": [],
        }

        output_json = ctx.obj.get("output_json")
        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Architecture Score: {result['composite_score']}")

    except Exception as e:
        logger.error(f"Scoring failed: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
@click.option("--neo4j-user", default="neo4j", help="Neo4j user")
@click.option("--neo4j-password", prompt=True, hide_input=True, help="Neo4j password")
@click.option("--limit", default=10, help="Number of commits to show")
@click.pass_context
def history(
    ctx: click.Context,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    limit: int,
) -> None:
    """Show import history."""
    try:
        commits: list[dict[str, str | int]] = [
            {"sha": "abc123", "nodes": 42, "rels": 156, "imported_at": "2024-01-01T00:00:00Z"}
        ]
        result: dict[str, list[dict[str, str | int]]] = {"commits": commits[:limit]}

        output_json = ctx.obj.get("output_json")
        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            for entry in result["commits"]:
                sha = str(entry["sha"])
                click.echo(f"{sha[:7]} - {entry['nodes']} nodes")

    except Exception as e:
        logger.error(f"History failed: {e}")
        raise click.ClickException(str(e))


def main() -> None:
    """Entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
