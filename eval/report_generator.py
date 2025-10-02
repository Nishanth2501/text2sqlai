"""
Report generator for evaluation results

Generates comprehensive HTML reports for evaluation results including:
- Summary metrics
- Component-level analysis
- Error analysis
- Performance trends
- Model comparisons
"""

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .evaluator import AggregateEvaluationResults
from src.utils.logger import get_logger

logger = get_logger("text2sql.reports")


class ReportGenerator:
    """Generate comprehensive evaluation reports"""

    def __init__(self):
        self.template_dir = Path("eval/templates")
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_report(
        self, results: AggregateEvaluationResults, output_dir: str = "results/reports"
    ) -> str:
        """Generate HTML report for evaluation results"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_report_{results.dataset_name}_{timestamp}.html"
        filepath = output_path / filename

        # Generate HTML content
        html_content = self._generate_report_html(results)

        # Save HTML file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {filepath}")
        return str(filepath)

    def generate_comparison_report(
        self,
        comparison_results: Dict[str, AggregateEvaluationResults],
        output_dir: str = "results/reports",
    ) -> str:
        """Generate comparison report for multiple models"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_comparison_report_{timestamp}.html"
        filepath = output_path / filename

        # Generate comparison HTML content
        html_content = self._generate_comparison_html(comparison_results)

        # Save HTML file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Comparison report generated: {filepath}")
        return str(filepath)

    def _generate_report_html(self, results: AggregateEvaluationResults) -> str:
        """Generate HTML content for single evaluation report"""

        # Component scores table
        component_table = self._generate_component_table(results.component_scores)

        # Error analysis
        error_analysis = self._generate_error_analysis(results.error_types)

        # Performance metrics
        performance_metrics = self._generate_performance_metrics(results)

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text-to-SQL Evaluation Report - {results.dataset_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #7f8c8d;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-card .subtitle {{
            font-size: 0.8em;
            opacity: 0.8;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.3s ease;
        }}
        .error-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            margin: 5px 0;
        }}
        .error-count {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Text-to-SQL Evaluation Report</h1>
            <p>Dataset: {results.dataset_name} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Overall F1 Score</h3>
                <div class="value">{results.avg_f1_score:.3f}</div>
                <div class="subtitle">Weighted Average</div>
            </div>
            <div class="metric-card">
                <h3>Exact Match</h3>
                <div class="value">{results.avg_exact_match:.3f}</div>
                <div class="subtitle">Complete SQL Match</div>
            </div>
            <div class="metric-card">
                <h3>Execution Success</h3>
                <div class="value">{results.execution_success_rate:.3f}</div>
                <div class="subtitle">Query Execution Rate</div>
            </div>
            <div class="metric-card">
                <h3>Result Accuracy</h3>
                <div class="value">{results.avg_result_accuracy:.3f}</div>
                <div class="subtitle">Result Count Accuracy</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Dataset Summary</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Questions</td><td>{results.total_questions}</td></tr>
                <tr><td>Successful Generations</td><td>{results.successful_generations}</td></tr>
                <tr><td>Successful Executions</td><td>{results.successful_executions}</td></tr>
                <tr><td>Average Precision</td><td>{results.avg_precision:.3f}</td></tr>
                <tr><td>Average Recall</td><td>{results.avg_recall:.3f}</td></tr>
                <tr><td>Average Generation Time</td><td>{results.avg_generation_time:.3f}s</td></tr>
                <tr><td>Average Execution Time</td><td>{results.avg_execution_time:.3f}s</td></tr>
                <tr><td>Total Evaluation Time</td><td>{results.total_evaluation_time:.3f}s</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Component-Level Analysis</h2>
            {component_table}
        </div>
        
        <div class="section">
            <h2>Performance Metrics</h2>
            {performance_metrics}
        </div>
        
        <div class="section">
            <h2>Error Analysis</h2>
            {error_analysis}
        </div>
        
        {self._generate_failed_questions_section(results.failed_questions)}
        
        <div class="footer">
            <p>Generated by Text-to-SQL Evaluation Framework</p>
        </div>
    </div>
</body>
</html>
        """

        return html_template

    def _generate_component_table(
        self, component_scores: Dict[str, Dict[str, float]]
    ) -> str:
        """Generate component scores table HTML"""
        if not component_scores:
            return "<p>No component scores available</p>"

        rows = ""
        for component, scores in component_scores.items():
            if component == "overall":
                continue
            precision = scores.get("precision", 0)
            recall = scores.get("recall", 0)
            f1 = scores.get("f1_score", 0)

            rows += f"""
            <tr>
                <td>{component.replace("_", " ").title()}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {precision * 100}%"></div>
                    </div>
                    {precision:.3f}
                </td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {recall * 100}%"></div>
                    </div>
                    {recall:.3f}
                </td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {f1 * 100}%"></div>
                    </div>
                    {f1:.3f}
                </td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1 Score</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    def _generate_error_analysis(self, error_types: Dict[str, int]) -> str:
        """Generate error analysis HTML"""
        if not error_types:
            return "<p>No errors encountered during evaluation</p>"

        error_items = ""
        for error_type, count in error_types.items():
            error_items += f"""
            <div class="error-item">
                <span>{error_type.replace("_", " ").title()}</span>
                <span class="error-count">{count}</span>
            </div>
            """

        return f"""
        <div>
            <h3>Error Types</h3>
            {error_items}
        </div>
        """

    def _generate_performance_metrics(self, results: AggregateEvaluationResults) -> str:
        """Generate performance metrics HTML"""
        return f"""
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Average Generation Time</td><td>{results.avg_generation_time:.3f}s</td></tr>
            <tr><td>Average Execution Time</td><td>{results.avg_execution_time:.3f}s</td></tr>
            <tr><td>Total Evaluation Time</td><td>{results.total_evaluation_time:.3f}s</td></tr>
            <tr><td>Queries per Second</td><td>{results.total_questions / results.total_evaluation_time:.2f}</td></tr>
        </table>
        """

    def _generate_failed_questions_section(self, failed_questions: List[str]) -> str:
        """Generate failed questions section HTML"""
        if not failed_questions:
            return ""

        failed_list = "".join([f"<li>{qid}</li>" for qid in failed_questions])

        return f"""
        <div class="section">
            <h2>Failed Questions</h2>
            <p>The following questions failed during evaluation:</p>
            <ul>{failed_list}</ul>
        </div>
        """

    def _generate_comparison_html(
        self, comparison_results: Dict[str, AggregateEvaluationResults]
    ) -> str:
        """Generate comparison report HTML"""

        # Create comparison table
        comparison_table = self._generate_comparison_table(comparison_results)

        # Create performance comparison
        performance_comparison = self._generate_performance_comparison(
            comparison_results
        )

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .comparison-table th {{
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: 600;
        }}
        .comparison-table td {{
            padding: 12px 15px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
        }}
        .comparison-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .best-score {{
            background-color: #d4edda;
            font-weight: bold;
            color: #155724;
        }}
        .metric-row {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Model Comparison Report</h1>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="section">
            <h2>Performance Comparison</h2>
            {comparison_table}
        </div>
        
        <div class="section">
            <h2>Detailed Metrics</h2>
            {performance_comparison}
        </div>
    </div>
</body>
</html>
        """

        return html_template

    def _generate_comparison_table(
        self, comparison_results: Dict[str, AggregateEvaluationResults]
    ) -> str:
        """Generate model comparison table"""
        models = list(comparison_results.keys())

        # Find best scores for highlighting
        best_f1 = max(results.avg_f1_score for results in comparison_results.values())
        best_exact = max(
            results.avg_exact_match for results in comparison_results.values()
        )
        best_exec = max(
            results.execution_success_rate for results in comparison_results.values()
        )

        header_row = (
            "<tr><th>Metric</th>"
            + "".join([f"<th>{model}</th>" for model in models])
            + "</tr>"
        )

        rows = [
            ("F1 Score", lambda r: r.avg_f1_score, best_f1),
            ("Exact Match", lambda r: r.avg_exact_match, best_exact),
            ("Execution Success", lambda r: r.execution_success_rate, best_exec),
            ("Precision", lambda r: r.avg_precision, None),
            ("Recall", lambda r: r.avg_recall, None),
            ("Result Accuracy", lambda r: r.avg_result_accuracy, None),
            ("Generation Time", lambda r: r.avg_generation_time, None),
            ("Execution Time", lambda r: r.avg_execution_time, None),
        ]

        table_rows = ""
        for metric_name, metric_func, best_value in rows:
            row = f'<tr class="metric-row"><td>{metric_name}</td>'

            for model, results in comparison_results.items():
                value = metric_func(results)

                # Highlight best score
                css_class = (
                    "best-score"
                    if best_value is not None and abs(value - best_value) < 0.001
                    else ""
                )

                if "Time" in metric_name:
                    row += f'<td class="{css_class}">{value:.3f}s</td>'
                else:
                    row += f'<td class="{css_class}">{value:.3f}</td>'

            row += "</tr>"
            table_rows += row

        return f"""
        <table class="comparison-table">
            <thead>{header_row}</thead>
            <tbody>{table_rows}</tbody>
        </table>
        """

    def _generate_performance_comparison(
        self, comparison_results: Dict[str, AggregateEvaluationResults]
    ) -> str:
        """Generate detailed performance comparison"""
        comparison_html = ""

        for model, results in comparison_results.items():
            comparison_html += f"""
            <h3>{model}</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Questions</td><td>{results.total_questions}</td></tr>
                <tr><td>Successful Generations</td><td>{results.successful_generations}</td></tr>
                <tr><td>Successful Executions</td><td>{results.successful_executions}</td></tr>
                <tr><td>Failed Questions</td><td>{len(results.failed_questions)}</td></tr>
            </table>
            """

        return comparison_html
