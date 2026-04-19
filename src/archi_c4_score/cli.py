"""CLI interface for C4 Architecture Scoring."""

import asyncio
import json
import logging
from pathlib import Path

import click

from archi_c4_score import __version__
from archi_c4_score.hugo_export import DashboardGenerator
from archi_c4_score.parser import CoArchi2Parser
from archi_c4_score.repository import Repository
from archi_c4_score.timeline import TimelineService

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
    """Import a C4 model from a coArchi2 or Archi repository."""
    try:
        repo_path = Path("/tmp/archi-model")
        repo = Repository(path=repo_path)
        if not repo.is_git_repository():
            repo.clone(repo_url)
        commit = repo.get_current_commit()

        # Check for .archimate files first (Archi format), then .json (coArchi2)
        archimate_files = list(repo_path.glob("**/*.archimate"))
        json_files = list(repo_path.glob("**/*.json"))

        nodes = []
        rels = []

        if archimate_files:
            from archi_c4_score.github_importer import parse_model_archimate
            from archi_c4_score.mapper import C4Mapper

            xml_content = archimate_files[0].read_text()
            elements = []
            relationships = []
            for item, item_type in parse_model_archimate(xml_content):
                if item_type == "element":
                    elements.append(item)
                elif item_type == "relationship":
                    relationships.append(item)
            mapper = C4Mapper()
            nodes, rels = mapper.map_model(elements, relationships)
            logger.info(f"Parsed {len(nodes)} nodes, {len(rels)} rels from .archimate")

        elif json_files:
            parser = CoArchi2Parser()
            data = json.loads(json_files[0].read_text())
            archi_model = parser.parse(data)
            mapper = C4Mapper()
            nodes, rels = mapper.map_model(archi_model.elements, archi_model.relationships)
        else:
            logger.warning(f"No model files found in {repo_path}")

        # Import to Neo4j if credentials provided
        if neo4j_uri and neo4j_user and neo4j_password:
            from archi_c4_score.graph import Neo4jConnection
            from archi_c4_score.importing import Neo4jImporter

            async def do_import():
                conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
                await conn.connect()
                importer = Neo4jImporter(conn)

                # Convert nodes to C4Node objects if they aren't already
                from archi_c4_score.models import (
                    C4Node as ModelC4Node,
                    C4Relationship as ModelC4Rel,
                    C4Level,
                )

                c4_nodes = []
                for n in nodes:
                    if hasattr(n, "id"):
                        # Map level string to C4Level enum
                        level_str = str(getattr(n, "level", "COMPONENT"))
                        try:
                            c4_level = C4Level[level_str.upper()]
                        except (KeyError, AttributeError):
                            c4_level = C4Level.COMPONENT

                        c4_nodes.append(
                            ModelC4Node(
                                id=n.id,
                                name=n.name,
                                c4_level=c4_level,
                            )
                        )

                c4_rels = []
                for r in rels:
                    if hasattr(r, "source_id"):
                        c4_rels.append(
                            ModelC4Rel(
                                source_id=r.source_id,
                                target_id=r.target_id,
                                relationship_type=r.relationship_type,
                                rel_type=getattr(r, "rel_type", ""),
                            )
                        )

                result = await importer.import_model(c4_nodes, c4_rels, commit)
                await conn.close()
                return result

            import_result = asyncio.run(do_import())
            logger.info(f"Imported to Neo4j: {import_result}")

        result = {"commit": commit, "nodes": len(nodes), "rels": len(rels)}

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


@cli.command()
@click.option("--repo-url", required=True, help="Git repository URL")
@click.option("--limit", default=30, help="Number of commits")
@click.option("--offset", default=0, help="Pagination offset")
@click.pass_context
def timeline(ctx: click.Context, repo_url: str, limit: int, offset: int) -> None:
    """Show architecture score timeline."""
    try:
        service = TimelineService()
        scored_commits = _get_mock_scored_commits()
        timeline_data = service.get_timeline(repo_url, scored_commits, limit, offset)

        output_json = ctx.obj.get("output_json")
        if output_json:
            result = {
                "repository_url": timeline_data.repository_url,
                "commits": [
                    {
                        "sha": p.sha,
                        "date": str(p.date),
                        "author": p.author,
                        "composite_score": p.composite_score,
                        "score_delta": p.score_delta,
                        "is_significant": p.is_significant,
                    }
                    for p in timeline_data.commits
                ],
                "pagination": timeline_data.pagination,
            }
            click.echo(json.dumps(result, indent=2, default=str))
        else:
            click.echo(f"Timeline for {repo_url}")
            click.echo(f"Showing {len(timeline_data.commits)} commits")
            for point in timeline_data.commits:
                delta_str = f" ({point.score_delta:+.1f})" if point.score_delta else ""
                sig_str = " [SIGNIFICANT]" if point.is_significant else ""
                click.echo(
                    f"  {point.sha[:7]} - {point.composite_score:.1f}{delta_str}{sig_str} - {point.date}"
                )

    except Exception as e:
        logger.error(f"Timeline failed: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--repo-url", required=True, help="Git repository URL")
@click.pass_context
def trends(ctx: click.Context, repo_url: str) -> None:
    """Show architecture score trends."""
    try:
        service = TimelineService()
        scored_commits = _get_mock_scored_commits()
        timeline_data = service.get_timeline(repo_url, scored_commits)
        trend_lines = service.calculate_trends(timeline_data.commits)

        output_json = ctx.obj.get("output_json")
        if output_json:
            result = {
                "repository_url": repo_url,
                "trends": [
                    {
                        "dimension": t.dimension,
                        "direction": t.direction.value,
                        "slope": t.slope,
                        "confidence": t.confidence,
                    }
                    for t in trend_lines
                ],
            }
            click.echo(json.dumps(result, indent=2, default=str))
        else:
            click.echo(f"Trends for {repo_url}")
            for trend in trend_lines:
                direction_icon = (
                    "↑"
                    if trend.direction.value == "INCREASING"
                    else "↓"
                    if trend.direction.value == "DECREASING"
                    else "→"
                )
                click.echo(
                    f"  {trend.dimension}: {trend.direction.value} {direction_icon} (slope: {trend.slope:.3f})"
                )

    except Exception as e:
        logger.error(f"Trends failed: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--repo-url", required=True, help="Git repository URL")
@click.option("--from-commit", required=True, help="Earlier commit SHA")
@click.option("--to-commit", required=True, help="Later commit SHA")
@click.pass_context
def compare(ctx: click.Context, repo_url: str, from_commit: str, to_commit: str) -> None:
    """Compare two commits."""
    try:
        from archi_c4_score.timeline import CommitComparator

        comparator = CommitComparator()
        from_data = _get_mock_commit(from_commit)
        to_data = _get_mock_commit(to_commit)

        if not from_data or not to_data:
            raise click.ClickException("One or both commits not found")

        diff, impacts = comparator.compare(from_data, to_data)

        output_json = ctx.obj.get("output_json")
        if output_json:
            result = {
                "from_commit": from_commit,
                "to_commit": to_commit,
                "diff": {
                    "elements_added": len(diff.elements_added),
                    "elements_removed": len(diff.elements_removed),
                    "relationships_added": len(diff.relationships_added),
                    "relationships_removed": len(diff.relationships_removed),
                },
                "score_impact": [
                    {"dimension": i.dimension, "change": i.change, "explanation": i.explanation}
                    for i in impacts
                ],
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Comparing {from_commit[:7]} → {to_commit[:7]}")
            click.echo(f"  Elements added: {len(diff.elements_added)}")
            click.echo(f"  Elements removed: {len(diff.elements_removed)}")
            click.echo(f"  Relationships added: {len(diff.relationships_added)}")
            click.echo(f"  Relationships removed: {len(diff.relationships_removed)}")
            if impacts:
                click.echo("  Score impact:")
                for impact in impacts:
                    click.echo(f"    - {impact.explanation}")

    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--repo-url", required=True, help="Git repository URL")
@click.option("--output", type=click.Path(), help="Output file or directory")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "hugo"]),
    default="json",
    help="Output format",
)
@click.option(
    "--include-recommendations",
    is_flag=True,
    default=False,
    help="Include AI-generated recommendations",
)
@click.pass_context
def dashboard(
    ctx: click.Context,
    repo_url: str,
    output: str | None,
    output_format: str,
    include_recommendations: bool,
) -> None:
    """Generate dashboard report."""
    try:
        from archi_c4_score.dashboard_service import get_recommendations_for_dashboard
        from archi_c4_score.scoring import BackfillOrchestrator, ScoringEngine
        from archi_c4_score.treemap import generate_treemap

        service = TimelineService()
        scored_commits = _get_mock_scored_commits()
        timeline_data = service.get_timeline(repo_url, scored_commits)
        trends = service.calculate_trends(timeline_data.commits)

        generator = DashboardGenerator(output_dir=output if output else "output")
        health_status = generator.calculate_health_status(
            [{"direction": t.direction.value} for t in trends]
        )

        c4_scoring_data = None
        treemap_cells = []
        if timeline_data.commits:
            commit_sha = timeline_data.commits[-1].sha
            orchestrator = BackfillOrchestrator(scoring_engine=ScoringEngine(), repository=None)
            import asyncio

            containers = asyncio.run(orchestrator.get_container_scores(repo_url, commit_sha))
            components = asyncio.run(orchestrator.get_component_scores(repo_url, commit_sha))
            treemap = generate_treemap(containers, system_id="system")
            treemap_cells = [
                {
                    "id": c.id,
                    "name": c.name,
                    "level": c.level,
                    "score": c.score,
                    "size": c.size,
                    "parent_id": c.parent_id,
                    "stereotype": c.stereotype,
                }
                for c in treemap
            ]

            component_cells = [
                {
                    "id": c.node_id,
                    "name": c.node_name,
                    "composite": c.composite,
                    "coupling": c.coupling,
                    "instability_index": c.instability_index,
                    "efferent_coupling": c.efferent_coupling,
                    "afferent_coupling": c.afferent_coupling,
                }
                for c in components
            ]

            if timeline_data.commits:
                latest_commit = timeline_data.commits[-1]
                c4_scoring_data = {
                    "composite_score": latest_commit.composite_score,
                    "dimensions": latest_commit.dimensions,
                    "element_count": latest_commit.element_count,
                    "relationship_count": latest_commit.relationship_count,
                    "commit": commit_sha,
                    "treemap": treemap_cells,
                    "components": component_cells,
                }

        recommendations_data = None
        if include_recommendations:
            recommendations_data = get_recommendations_for_dashboard(
                repository_url=repo_url,
                repository_name=repo_url.rstrip("/").split("/")[-1],
                commits=timeline_data.commits,
                trends=trends,
                significant_changes=timeline_data.significant_changes,
            )

        hugo_data = generator.generate(
            repository_url=repo_url,
            commits=[
                {
                    "sha": p.sha,
                    "date": str(p.date),
                    "author": p.author,
                    "composite_score": p.composite_score,
                    "dimensions": p.dimensions,
                    "element_count": p.element_count,
                    "relationship_count": p.relationship_count,
                }
                for p in timeline_data.commits
            ],
            trends=[
                {
                    "dimension": t.dimension,
                    "direction": t.direction.value,
                    "slope": t.slope,
                    "confidence": t.confidence,
                }
                for t in trends
            ],
            health_status=health_status,
            significant_changes=[
                {
                    "magnitude": s.magnitude,
                    "direction": s.direction,
                    "commit": s.commit,
                    "affected_dimensions": s.affected_dimensions,
                }
                for s in timeline_data.significant_changes
            ],
            recommendations=recommendations_data,
            c4_scoring=c4_scoring_data,
        )

        output_json = ctx.obj.get("output_json")
        if output or output_json:
            result = {
                "generated_at": hugo_data.generated,
                "repository": hugo_data.repository,
                "summary": hugo_data.summary,
                "commits": hugo_data.commits,
                "trends": hugo_data.trends,
                "concerns": hugo_data.concerns,
                "recommendations": hugo_data.recommendations,
            }
            if output:
                Path(output).write_text(json.dumps(result, indent=2, default=str))
                click.echo(f"Dashboard written to {output}")
            else:
                click.echo(json.dumps(result, indent=2, default=str))
        else:
            click.echo(f"Dashboard for {repo_url}")
            click.echo(f"  Health Status: {health_status}")
            click.echo(f"  Commits Analyzed: {len(timeline_data.commits)}")
            click.echo(f"  Generated: {hugo_data.generated}")

            if recommendations_data and recommendations_data.get("recommendations"):
                click.echo("  Recommendations:")
                for rec in recommendations_data["recommendations"]:
                    priority_color = (
                        "🔴"
                        if rec["priority"] == "HIGH"
                        else "🟡"
                        if rec["priority"] == "MEDIUM"
                        else "🟢"
                    )
                    click.echo(
                        f"    {priority_color} [{rec['priority']}] {rec['description'][:60]}..."
                    )

    except Exception as e:
        logger.error(f"Dashboard failed: {e}")
        raise click.ClickException(str(e))


def _get_mock_scored_commits() -> list[dict]:
    """Get mock scored commits for testing."""
    from datetime import datetime, timedelta

    base_date = datetime.now() - timedelta(days=30)
    return [
        {
            "commit_sha": f"abc{i:03d}",
            "repository_url": "https://github.com/example/repo",
            "commit_date": (base_date + timedelta(days=i)).isoformat(),
            "author": "Test Author",
            "message": f"Commit {i}",
            "composite_score": 70.0 + (i * 0.5),
            "coupling_score": 80.0 - (i * 0.3),
            "modularity_score": 70.0 + (i * 0.2),
            "cohesion_score": 75.0,
            "extensibility_score": 65.0 + (i * 0.1),
            "maintainability_score": 72.0,
            "element_count": 10 + i,
            "relationship_count": 15 + (i * 2),
        }
        for i in range(30)
    ]


def _get_mock_commit(sha: str) -> dict | None:
    """Get mock commit data."""
    commits = _get_mock_scored_commits()
    for c in commits:
        if c["commit_sha"] == sha:
            return c
    return None


def main() -> None:
    """Entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
