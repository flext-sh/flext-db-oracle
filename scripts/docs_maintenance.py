#!/usr/bin/env python3
"""Documentation Maintenance & Quality Assurance Framework.

Comprehensive documentation maintenance system for flext-db-oracle with:
- Automated quality audits and validation
- Link checking and reference validation
- Style consistency and accessibility compliance
- Content optimization and enhancement
- Automated synchronization and reporting

Usage:
    python scripts/docs_maintenance.py --audit
    python scripts/docs_maintenance.py --validate
    python scripts/docs_maintenance.py --optimize
    python scripts/docs_maintenance.py --comprehensive

Author: FLEXT Documentation Team
Version: 1.0.0
"""

import argparse
import asyncio
import logging
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml
from flext_core import FlextCore

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class MaintenanceConfig:
    """Configuration for documentation maintenance system."""

    version: str = "1.0.0"
    project: str = "flext-db-oracle"
    audit_enabled: bool = True
    max_age_days: int = 90
    min_word_count: int = 100
    max_broken_links: int = 0
    validate_markdown: bool = True
    validate_links: bool = True
    validate_references: bool = True
    auto_correct: bool = False
    suggestions_only: bool = True


@dataclass
class AuditResult:
    """Results of documentation audit."""

    file_path: Path
    issues: list[dict[str, object]] = field(default_factory=list)
    statistics: dict[str, object] = field(default_factory=dict)
    score: float = 0.0
    severity_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def total_issues(self) -> int:
        """Get total number of issues."""
        return len(self.issues)

    @property
    def critical_issues(self) -> int:
        """Get number of critical severity issues."""
        return self.severity_counts.get("critical", 0)

    @property
    def health_score(self) -> float:
        """Calculate health score based on issues and severity."""
        if not self.issues:
            return 100.0

        # Weight issues by severity
        weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        total_weight = sum(
            weights.get(issue.get("severity", "low"), 1) for issue in self.issues
        )

        # Base score reduction
        base_score = max(0, 100 - (total_weight * 2))
        return round(base_score, 1)


@dataclass
class MaintenanceReport:
    """Comprehensive maintenance report."""

    timestamp: datetime
    config: MaintenanceConfig
    files_audited: int = 0
    total_issues: int = 0
    critical_issues: int = 0
    average_score: float = 0.0
    file_results: list[AuditResult] = field(default_factory=list)
    summary: dict[str, object] = field(default_factory=dict)
    recommendations: FlextCore.Types.StringList = field(default_factory=list)


class DocumentationAuditor:
    """Comprehensive documentation auditor with quality assurance."""

    def __init__(self, config: MaintenanceConfig) -> None:
        """Initialize documentation auditor with configuration."""
        self.config = config
        self.docs_path = Path("docs")
        self.project_root = Path()

        # Markdown validation patterns
        self.markdown_patterns = {
            "heading_hierarchy": re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE),
            "broken_internal_links": re.compile(r"\[([^\]]+)\]\(([^)]+)\)"),
            "code_blocks": re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL),
            "emphasis_consistency": re.compile(r"(\*\*\*|\*\*|__|_)(.*?)\1"),
            "list_consistency": re.compile(r"^(\s*)([-*+])\s+", re.MULTILINE),
        }

        # Quality thresholds
        self.quality_thresholds = {
            "max_headings_per_level": 10,
            "min_paragraph_length": 50,
            "max_consecutive_lists": 5,
            "max_code_block_ratio": 0.6,  # Max 60% of content in code blocks
        }

    def discover_files(self) -> list[Path]:
        """Discover all documentation files."""
        files = []

        # Find markdown files
        for pattern in ["*.md", "*.mdx"]:
            files.extend(self.project_root.rglob(pattern))

        # Filter to docs directory and root level docs
        doc_files = [
            file_path
            for file_path in files
            if str(file_path).startswith("docs/")
            or file_path.name in {"README.md", "CLAUDE.md", "CHANGELOG.md"}
        ]

        logger.info(f"Discovered {len(doc_files)} documentation files")
        return sorted(doc_files)

    async def audit_file(self, file_path: Path) -> AuditResult:
        """Perform comprehensive audit of a single documentation file."""
        result = AuditResult(file_path=file_path)

        try:
            content = await asyncio.to_thread(file_path.read_text, encoding="utf-8")
            result.statistics = self._analyze_content(content)
            result.issues = await self._validate_content(file_path, content)

        except Exception:
            logger.exception(f"Error auditing {file_path}")
            result.issues.append({
                "type": "file_error",
                "severity": "critical",
                "message": "Failed to read file",
                "line": 0,
            })

        result.score = result.health_score
        return result

    def _analyze_content(self, content: str) -> dict[str, object]:
        """Analyze content statistics."""
        lines = content.split("\n")
        words = re.findall(r"\b\w+\b", content)

        # Heading analysis
        headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
        heading_levels = [len(level) for level, _ in headings]

        # Link analysis
        external_links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", content)
        internal_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

        # Code analysis
        code_blocks = len(re.findall(r"```", content)) // 2
        inline_code = len(re.findall(r"`[^`]+`", content))

        # List analysis
        unordered_lists = len(re.findall(r"^[\s]*[-*+]\s+", content, re.MULTILINE))
        ordered_lists = len(re.findall(r"^[\s]*\d+\.\s+", content, re.MULTILINE))

        return {
            "line_count": len(lines),
            "word_count": len(words),
            "character_count": len(content),
            "heading_count": len(headings),
            "heading_levels": heading_levels,
            "external_links": len(external_links),
            "internal_links": len(internal_links),
            "code_blocks": code_blocks,
            "inline_code": inline_code,
            "unordered_lists": unordered_lists,
            "ordered_lists": ordered_lists,
            "avg_words_per_line": len(words) / len(lines) if lines else 0,
        }

    async def _validate_content(
        self, file_path: Path, content: str
    ) -> list[dict[str, object]]:
        """Validate content quality and identify issues."""
        issues = []

        # Age validation
        if self.config.audit_enabled:
            file_age = self._get_file_age(file_path)
            if file_age > self.config.max_age_days:
                issues.append({
                    "type": "stale_content",
                    "severity": "medium",
                    "message": f"File is {file_age} days old (max: {self.config.max_age_days})",
                    "line": 0,
                    "suggestion": "Review and update content for freshness",
                })

        # Content length validation
        word_count = len(re.findall(r"\b\w+\b", content))
        if word_count < self.config.min_word_count:
            issues.append({
                "type": "insufficient_content",
                "severity": "low",
                "message": f"Content too short ({word_count} words, min: {self.config.min_word_count})",
                "line": 0,
                "suggestion": "Add more detailed content and examples",
            })

        # Markdown syntax validation
        if self.config.validate_markdown:
            issues.extend(self._validate_markdown_syntax(content))

        # Link validation
        if self.config.validate_links:
            issues.extend(await self._validate_links(content))

        # Reference validation
        if self.config.validate_references:
            issues.extend(self._validate_internal_references(file_path, content))

        # Style consistency
        issues.extend(self._validate_style_consistency(content))

        # Accessibility
        issues.extend(self._validate_accessibility(content))

        return issues

    def _get_file_age(self, file_path: Path) -> int:
        """Get file age in days."""
        mtime = file_path.stat().st_mtime
        age_seconds = time.time() - mtime
        return int(age_seconds / (24 * 3600))

    def _validate_markdown_syntax(self, content: str) -> list[dict[str, object]]:
        """Validate markdown syntax."""
        # Heading hierarchy validation
        headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
        levels = [len(level) for level, _ in headings]

        # Check for skipped heading levels
        issues = [
            {
                "type": "heading_hierarchy",
                "severity": "medium",
                "message": f"Skipped heading level: {levels[i]} → {levels[i + 1]}",
                "line": 0,
                "suggestion": "Use consecutive heading levels or adjust hierarchy",
            }
            for i in range(len(levels) - 1)
            if levels[i + 1] > levels[i] + 1
        ]

        # Code block validation
        code_blocks = re.findall(r"```(\w+)?\n(.*?)\n```", content, re.DOTALL)
        for i, (lang, code) in enumerate(code_blocks):
            if not lang and len(code.strip()) > 50:
                issues.append({
                    "type": "code_block_language",
                    "severity": "low",
                    "message": f"Code block {i + 1} missing language specification",
                    "line": 0,
                    "suggestion": "Add language specifier after opening ```",
                })

        # List consistency
        list_items = re.findall(r"^(\s*)([-*+])\s+", content, re.MULTILINE)
        markers = [marker for _, marker in list_items]
        if len(set(markers)) > 1:
            issues.append({
                "type": "list_consistency",
                "severity": "low",
                "message": f"Mixed list markers: {set(markers)}",
                "line": 0,
                "suggestion": "Use consistent list markers throughout document",
            })

        return issues

    async def _validate_links(self, content: str) -> list[dict[str, object]]:
        """Validate external links."""
        issues = []
        external_links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", content)

        for _text, url in external_links:
            try:
                # Basic URL validation
                parsed = urlparse(url)
                if not parsed.netloc:
                    issues.append({
                        "type": "invalid_url",
                        "severity": "high",
                        "message": f"Invalid URL format: {url}",
                        "line": 0,
                        "suggestion": "Fix URL format or remove broken link",
                    })
                    continue

                # Optional: Check if URL is reachable (commented out for performance)
                # try:
                #     response = await asyncio.get_event_loop().run_in_executor(
                #         None, lambda: urlopen(url, timeout=5)
                #     )
                #     if response.status >= 400:
                #         issues.append({
                #             'type': 'broken_link',
                #             'severity': 'high',
                #             'message': f'Broken link (HTTP {response.status}): {url}',
                #             'line': 0,
                #             'suggestion': 'Update or remove broken link'
                #         })
                # except (URLError, HTTPError, OSError):
                #     issues.append({
                #         'type': 'unreachable_link',
                #         'severity': 'medium',
                #         'message': f'Unreachable link: {url}',
                #         'line': 0,
                #         'suggestion': 'Verify link accessibility or update URL'
                #     })

            except Exception as e:
                issues.append({
                    "type": "link_validation_error",
                    "severity": "low",
                    "message": f"Link validation failed for {url}: {e}",
                    "line": 0,
                    "suggestion": "Review link format and accessibility",
                })

        return issues

    def _validate_internal_references(
        self, _file_path: Path, content: str
    ) -> list[dict[str, object]]:
        """Validate internal references and cross-links."""
        issues = []

        # Find internal links (relative paths, anchors)
        internal_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

        for _text, link in internal_links:
            if (
                not link.startswith(("http://", "https://", "mailto:"))
                and not link.startswith("#")
                and not Path(link).exists()
            ):
                # Try relative to docs directory
                docs_path = self.docs_path / link
                if not docs_path.exists():
                    issues.append({
                        "type": "broken_internal_link",
                        "severity": "high",
                        "message": f"Broken internal link: {link}",
                        "line": 0,
                        "suggestion": "Fix file path or remove broken reference",
                    })

        return issues

    def _validate_style_consistency(self, content: str) -> list[dict[str, object]]:
        """Validate style consistency."""
        issues = []

        # Check for mixed emphasis styles
        bold_patterns = [
            re.findall(r"\*\*([^*]+)\*\*", content),  # **bold**
            re.findall(r"__([^_]+)__", content),  # __bold__
        ]

        if len(bold_patterns[0]) > 0 and len(bold_patterns[1]) > 0:
            issues.append({
                "type": "emphasis_inconsistency",
                "severity": "low",
                "message": "Mixed bold emphasis styles (**text** and __text__)",
                "line": 0,
                "suggestion": "Use consistent emphasis style throughout document",
            })

        # Check for excessive code blocks
        total_lines = len(content.split("\n"))
        code_lines = len(re.findall(r"^```", content, re.MULTILINE))
        code_ratio = code_lines / total_lines if total_lines > 0 else 0

        if code_ratio > self.quality_thresholds["max_code_block_ratio"]:
            issues.append({
                "type": "excessive_code",
                "severity": "low",
                "message": f"High code block ratio ({code_ratio:.1%})",
                "line": 0,
                "suggestion": "Balance code examples with explanatory text",
            })

        return issues

    def _validate_accessibility(self, content: str) -> list[dict[str, object]]:
        """Validate accessibility compliance."""
        issues = []

        # Check for images without alt text
        images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
        for alt_text, src in images:
            if not alt_text.strip():
                issues.append({
                    "type": "missing_alt_text",
                    "severity": "medium",
                    "message": f"Image missing alt text: {src}",
                    "line": 0,
                    "suggestion": "Add descriptive alt text for accessibility",
                })

        # Check for links without descriptive text
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for text, _url in links:
            if text.lower() in {"here", "click here", "link", "read more"}:
                issues.append({
                    "type": "non_descriptive_link",
                    "severity": "low",
                    "message": f'Non-descriptive link text: "{text}"',
                    "line": 0,
                    "suggestion": "Use descriptive link text for better accessibility",
                })

        return issues


class ContentOptimizer:
    """Content optimization and enhancement utilities."""

    def __init__(self, config: MaintenanceConfig) -> None:
        """Initialize content optimizer with configuration."""
        self.config = config

    def optimize_file(
        self, _file_path: Path, audit_result: AuditResult
    ) -> FlextCore.Types.StringList:
        """Optimize content based on audit results."""
        optimizations = []

        if not self.config.auto_correct:
            # Generate suggestions only
            optimizations.extend(
                f"- {issue['suggestion']} ({issue['type']})"
                for issue in audit_result.issues
                if issue.get("suggestion")
            )

            return optimizations

        # TODO(@flext-team): Implement automatic corrections - #123
        # This would modify files directly based on issue types

        return optimizations


class ReportGenerator:
    """Generate comprehensive maintenance reports."""

    def __init__(self, config: MaintenanceConfig) -> None:
        """Initialize report generator with configuration."""
        self.config = config
        self.reports_dir = Path("docs/reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_report(self, maintenance_report: MaintenanceReport) -> Path:
        """Generate comprehensive maintenance report."""
        timestamp = maintenance_report.timestamp.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"maintenance_report_{timestamp}.md"

        content = self._build_report_content(maintenance_report)
        report_file.write_text(content)

        logger.info(f"Generated maintenance report: {report_file}")
        return report_file

    def _build_report_content(self, report: MaintenanceReport) -> str:
        """Build comprehensive report content."""
        lines = [
            "# Documentation Maintenance Report",
            "",
            f"**Generated**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project**: {report.config.project}",
            f"**Version**: {report.config.version}",
            "",
            "## Executive Summary",
            "",
            f"- **Files Audited**: {report.files_audited}",
            f"- **Total Issues**: {report.total_issues}",
            f"- **Critical Issues**: {report.critical_issues}",
            f"- **Average Health Score**: {report.average_score:.1f}%",
            "",
            "## Issue Summary by Severity",
        ]

        # Severity breakdown
        severity_counts = defaultdict(int)
        for result in report.file_results:
            for severity, count in result.severity_counts.items():
                severity_counts[severity] += count

        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            lines.append(f"- **{severity.title()}**: {count}")

        lines.extend([
            "",
            "## File Results",
            "",
            "| File | Health Score | Issues | Critical | High | Medium | Low |",
            "|------|--------------|--------|----------|------|--------|-----|",
        ])

        lines.extend(
            f"| {result.file_path.name} | {result.score}% | {result.total_issues} | "
            f"{result.severity_counts.get('critical', 0)} | "
            f"{result.severity_counts.get('high', 0)} | "
            f"{result.severity_counts.get('medium', 0)} | "
            f"{result.severity_counts.get('low', 0)} |"
            for result in sorted(report.file_results, key=lambda x: x.score)
        )

        # Recommendations
        if report.recommendations:
            lines.extend([
                "",
                "## Recommendations",
                "",
                "\n".join(f"- {rec}" for rec in report.recommendations),
            ])

        return "\n".join(lines)


async def run_audit(config: MaintenanceConfig) -> MaintenanceReport:
    """Run comprehensive documentation audit."""
    logger.info("Starting documentation audit...")

    auditor = DocumentationAuditor(config)
    ContentOptimizer(config)
    report_generator = ReportGenerator(config)

    # Discover files
    files = auditor.discover_files()

    # Audit each file
    results = []
    total_issues = 0
    critical_issues = 0
    total_score = 0.0

    for file_path in files:
        logger.info(f"Auditing {file_path}")
        result = await auditor.audit_file(file_path)
        results.append(result)

        total_issues += result.total_issues
        critical_issues += result.critical_issues
        total_score += result.score

        # Update severity counts
        for severity, count in result.severity_counts.items():
            result.severity_counts[severity] = count

    # Calculate averages
    average_score = total_score / len(results) if results else 0.0

    # Generate recommendations
    recommendations = generate_recommendations(results, config)

    # Create maintenance report
    report = MaintenanceReport(
        timestamp=datetime.now(UTC),
        config=config,
        files_audited=len(results),
        total_issues=total_issues,
        critical_issues=critical_issues,
        average_score=round(average_score, 1),
        file_results=results,
        recommendations=recommendations,
    )

    # Generate and save report
    report_file = report_generator.generate_report(report)

    logger.info(f"Audit complete. Report saved to {report_file}")
    logger.info(
        f"Summary: {len(results)} files, {total_issues} issues, {average_score:.1f}% average score"
    )

    return report


def generate_recommendations(
    results: list[AuditResult], config: MaintenanceConfig
) -> FlextCore.Types.StringList:
    """Generate actionable recommendations based on audit results."""
    recommendations = []

    # Analyze patterns across all files
    all_issues = []
    for result in results:
        all_issues.extend(result.issues)

    issue_types = Counter(issue["type"] for issue in all_issues)

    # Top issue types
    if issue_types:
        top_issues = issue_types.most_common(5)
        recommendations.append("**Most Common Issues:**")
        for issue_type, count in top_issues:
            recommendations.append(f"  - {issue_type}: {count} occurrences")

    # Critical issues
    critical_count = sum(
        1 for issue in all_issues if issue.get("severity") == "critical"
    )
    if critical_count > 0:
        recommendations.append(
            f"**CRITICAL: Address {critical_count} critical issues immediately**"
        )

    # Stale content
    stale_files = [
        r.file_path
        for r in results
        if any(issue["type"] == "stale_content" for issue in r.issues)
    ]
    if stale_files:
        recommendations.append(
            f"**Review {len(stale_files)} stale files (> {config.max_age_days} days old)**"
        )

    # Quality improvements
    low_score_files = [r for r in results if r.score < 70.0]
    if low_score_files:
        recommendations.append(
            f"**Improve quality of {len(low_score_files)} low-scoring files (< 70%)**"
        )

    return recommendations


async def run_validation(config: MaintenanceConfig) -> bool:
    """Run validation checks."""
    logger.info("Running validation checks...")

    auditor = DocumentationAuditor(config)
    files = auditor.discover_files()

    all_valid = True
    for file_path in files:
        result = await auditor.audit_file(file_path)
        if result.critical_issues > 0:
            logger.error(f"❌ {file_path}: {result.critical_issues} critical issues")
            all_valid = False
        elif result.total_issues > 0:
            logger.warning(f"⚠️  {file_path}: {result.total_issues} issues")
        else:
            logger.info(f"✅ {file_path}: No issues")

    return all_valid


def run_optimization(config: MaintenanceConfig) -> None:
    """Run content optimization."""
    logger.info("Running content optimization...")

    auditor = DocumentationAuditor(config)
    ContentOptimizer(config)

    files = auditor.discover_files()

    for file_path in files:
        logger.info(f"Optimizing {file_path}")
        # TODO: Implement optimization logic
        logger.info(f"Optimization suggestions for {file_path}: (not implemented yet)")


async def run_comprehensive(config: MaintenanceConfig) -> MaintenanceReport:
    """Run comprehensive maintenance suite."""
    logger.info("Running comprehensive documentation maintenance...")

    # Run audit
    report = await run_audit(config)

    # Run validation
    is_valid = await run_validation(config)

    # Run optimization
    run_optimization(config)

    # Update report with validation results
    report.summary["validation_passed"] = is_valid

    logger.info("Comprehensive maintenance complete")
    return report


def load_config() -> MaintenanceConfig:
    """Load maintenance configuration."""
    config_path = Path("docs/maintenance_config.yaml")

    if config_path.exists():
        try:
            with Path(config_path).open(encoding="utf-8") as f:
                data = yaml.safe_load(f)

            return MaintenanceConfig(
                version=data.get("version", "1.0.0"),
                project=data.get("project", "flext-db-oracle"),
                audit_enabled=data.get("audit", {}).get("enabled", True),
                max_age_days=data.get("audit", {})
                .get("thresholds", {})
                .get("max_age_days", 90),
                min_word_count=data.get("audit", {})
                .get("thresholds", {})
                .get("min_word_count", 100),
                validate_markdown=data.get("validation", {}).get(
                    "markdown_syntax", True
                ),
                validate_links=data.get("validation", {}).get("link_validation", True),
                validate_references=data.get("validation", {}).get(
                    "internal_references", True
                ),
                auto_correct=data.get("optimization", {}).get("auto_correct", False),
                suggestions_only=data.get("optimization", {}).get(
                    "suggestions_only", True
                ),
            )
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")

    return MaintenanceConfig()


def main() -> None:
    """Main entry point for documentation maintenance."""
    parser = argparse.ArgumentParser(
        description="Documentation Maintenance & Quality Assurance Framework"
    )
    parser.add_argument(
        "--audit", action="store_true", help="Run comprehensive documentation audit"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Run validation checks only"
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Run content optimization"
    )
    parser.add_argument(
        "--comprehensive", action="store_true", help="Run complete maintenance suite"
    )
    parser.add_argument("--config", type=str, help="Path to configuration file")

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Determine operation
    if args.audit:
        operation = run_audit
    elif args.validate:
        operation = run_validation
    elif args.optimize:
        operation = run_optimization
    elif args.comprehensive:
        operation = run_comprehensive
    else:
        parser.print_help()
        return

    # Run operation
    try:
        if asyncio.iscoroutinefunction(operation):
            result = asyncio.run(operation(config))
            if isinstance(result, MaintenanceReport):
                print("\nMaintenance Report Generated:")
                print(f"  Files Audited: {result.files_audited}")
                print(f"  Total Issues: {result.total_issues}")
                print(f"  Critical Issues: {result.critical_issues}")
                print(f"  Average Score: {result.average_score}%")
                print(
                    f"  Report: docs/reports/maintenance_report_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.md"
                )
        else:
            operation(config)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception:
        logger.exception("Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
