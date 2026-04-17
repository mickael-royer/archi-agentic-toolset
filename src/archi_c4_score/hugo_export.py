"""Hugo export for architecture timeline dashboard."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Concern:
    """Top architectural concern from analysis."""

    dimension: str
    description: str
    magnitude: float
    introduced_at: str


@dataclass
class HugoTimelineData:
    """Timeline data in Hugo-compatible format."""

    generated: str
    repository: dict[str, str]
    summary: dict[str, Any]
    commits: list[dict[str, Any]]
    trends: list[dict[str, Any]]
    concerns: list[dict[str, Any]]
    recommendations: dict[str, Any]
    schema_url: str = "https://architoolset.dev/schemas/timeline-v1.json"


class DashboardGenerator:
    """Generate Hugo-compatible dashboard output."""

    HUGO_SHORTCODE = """{{ $data := index .Site.Data "timeline" }}
{{ if $data }}
<div class="archi-timeline">
  <canvas id="timelineChart"></canvas>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const commits = {{ $data.commits | jsonify }};
    const labels = commits.map(c => c.sha.substring(0,7));
    const scores = commits.map(c => c.composite_score);
    
    new Chart(document.getElementById('timelineChart'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Composite Score',
          data: scores,
          borderColor: '#3498db',
          backgroundColor: 'rgba(52, 152, 219, 0.1)',
          fill: true,
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Architecture Score Timeline'
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            title: {
              display: true,
              text: 'Score'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Commit'
            }
          }
        }
      }
    });
  </script>
</div>
{{ end }}
"""

    def __init__(self, output_dir: Path | str = Path("output")) -> None:
        """Initialize dashboard generator."""
        self.output_dir = Path(output_dir)
        self.data_dir = self.output_dir / "data"
        self.content_dir = self.output_dir / "content" / "architecture"
        self.shortcodes_dir = self.output_dir / "layouts" / "shortcodes"

    def generate(
        self,
        repository_url: str,
        commits: list[dict[str, Any]],
        trends: list[dict[str, Any]],
        health_status: str,
        significant_changes: list[dict[str, Any]],
        recommendations: dict[str, Any] | None = None,
    ) -> HugoTimelineData:
        """Generate complete Hugo dashboard data."""
        repo_name = repository_url.rstrip("/").split("/")[-1]

        date_range = {}
        if commits:
            sorted_commits = sorted(commits, key=lambda c: c.get("date", ""))
            date_range = {
                "start": sorted_commits[0].get("date"),
                "end": sorted_commits[-1].get("date"),
            }

        concerns = self._generate_concerns(commits, trends)

        data = HugoTimelineData(
            generated=datetime.utcnow().isoformat() + "Z",
            repository={
                "url": repository_url,
                "name": repo_name,
            },
            summary={
                "health_status": health_status,
                "commits_analyzed": len(commits),
                "date_range": date_range,
            },
            commits=commits,
            trends=trends,
            concerns=concerns,
            recommendations=recommendations
            or {
                "recommendations": [],
                "llm_available": False,
            },
        )

        self._write_json(data)
        self._write_shortcode()

        return data

    def _generate_concerns(
        self,
        commits: list[dict[str, Any]],
        trends: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate top 3 concerns from analysis."""
        concerns: list[Concern] = []

        for trend in trends:
            if trend.get("direction") == "DECREASING":
                concerns.append(
                    Concern(
                        dimension=trend["dimension"],
                        description=f"{trend['dimension'].capitalize()} score shows declining trend",
                        magnitude=min(100, abs(trend["slope"]) * 100),
                        introduced_at=commits[-1]["sha"] if commits else "",
                    )
                )

        sorted_concerns = sorted(concerns, key=lambda c: c.magnitude, reverse=True)
        return [
            {
                "dimension": c.dimension,
                "description": c.description,
                "magnitude": c.magnitude,
                "introduced_at": c.introduced_at,
            }
            for c in sorted_concerns[:3]
        ]

    def _write_json(self, data: HugoTimelineData) -> None:
        """Write timeline.json to Hugo data directory."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        output = {
            "$schema": data.schema_url,
            "generated": data.generated,
            "repository": data.repository,
            "summary": data.summary,
            "commits": data.commits,
            "trends": data.trends,
            "concerns": data.concerns,
            "recommendations": data.recommendations,
        }

        (self.data_dir / "timeline.json").write_text(json.dumps(output, indent=2, default=str))

    def _write_shortcode(self) -> None:
        """Write Chart.js timeline shortcode."""
        self.shortcodes_dir.mkdir(parents=True, exist_ok=True)
        (self.shortcodes_dir / "archi-timeline.html").write_text(self.HUGO_SHORTCODE)

    def calculate_health_status(
        self,
        trends: list[dict[str, Any]],
    ) -> str:
        """Calculate overall health status from trends."""
        if not trends:
            return "STABLE"

        increasing = sum(1 for t in trends if t.get("direction") == "INCREASING")
        decreasing = sum(1 for t in trends if t.get("direction") == "DECREASING")

        if decreasing > increasing:
            return "DECLINING"
        elif increasing > decreasing:
            return "IMPROVING"
        return "STABLE"
