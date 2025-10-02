"""
Benchmark runner for systematic evaluation

Provides systematic benchmarking capabilities including:
- Scheduled evaluations
- Model comparison
- Performance regression testing
- Continuous integration support
"""

import time
import json
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .evaluator import Text2SQLEvaluator, AggregateEvaluationResults
from .datasets.dataset_loader import DatasetLoader
from .report_generator import ReportGenerator
from src.utils.logger import get_logger

logger = get_logger("text2sql.benchmark")


class BenchmarkRunner:
    """Systematic benchmark runner for Text-to-SQL evaluation"""

    def __init__(
        self,
        database_url: str = "sqlite:///data/demo.sqlite",
        results_dir: str = "results/benchmarks",
    ):
        self.database_url = database_url
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.evaluator = Text2SQLEvaluator(database_url)
        self.dataset_loader = DatasetLoader()
        self.report_generator = ReportGenerator()

        logger.info(f"Initialized BenchmarkRunner with results_dir: {results_dir}")

    def run_benchmark(
        self,
        dataset_name: str,
        model_name: Optional[str] = None,
        difficulty_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None,
    ) -> AggregateEvaluationResults:
        """Run benchmark evaluation"""

        logger.info(f"Starting benchmark: {dataset_name}")

        # Load dataset
        dataset = self.dataset_loader.load_custom_dataset(f"{dataset_name}.json")

        # Apply filters if specified
        if difficulty_filter:
            dataset = self.dataset_loader.filter_dataset_by_difficulty(
                dataset, difficulty_filter
            )
            logger.info(f"Filtered by difficulty: {difficulty_filter}")

        if tag_filter:
            dataset = self.dataset_loader.filter_dataset_by_tags(dataset, tag_filter)
            logger.info(f"Filtered by tags: {tag_filter}")

        # Run evaluation
        results = self.evaluator.evaluate_dataset(dataset, model_name)

        # Save results
        self.evaluator.save_results(results, str(self.results_dir))

        # Generate report
        report_path = self.report_generator.generate_html_report(
            results, str(self.results_dir)
        )
        logger.info(f"Report generated: {report_path}")

        return results

    def run_model_comparison(
        self, dataset_name: str, model_names: List[str]
    ) -> Dict[str, AggregateEvaluationResults]:
        """Compare multiple models on the same dataset"""

        logger.info(f"Running model comparison on {dataset_name}")
        logger.info(f"Models: {model_names}")

        # Load dataset
        dataset = self.dataset_loader.load_custom_dataset(f"{dataset_name}.json")

        # Run comparisons
        comparison_results = self.evaluator.compare_models(dataset, model_names)

        # Save comparison results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_file = (
            self.results_dir / f"model_comparison_{dataset_name}_{timestamp}.json"
        )

        comparison_data = {
            "dataset": dataset_name,
            "timestamp": timestamp,
            "models": {
                name: self._results_to_dict(results)
                for name, results in comparison_results.items()
            },
        }

        with open(comparison_file, "w", encoding="utf-8") as f:
            json.dump(comparison_data, f, indent=2, ensure_ascii=False)

        # Generate comparison report
        report_path = self.report_generator.generate_comparison_report(
            comparison_results, str(self.results_dir)
        )

        logger.info(f"Comparison results saved: {comparison_file}")
        logger.info(f"Comparison report generated: {report_path}")

        return comparison_results

    def run_regression_test(
        self,
        dataset_name: str,
        baseline_model: str,
        current_model: str,
        threshold: float = 0.95,
    ) -> bool:
        """Run regression test to ensure model performance hasn't degraded"""

        logger.info(f"Running regression test: {baseline_model} vs {current_model}")

        # Run evaluations
        comparison_results = self.run_model_comparison(
            dataset_name, [baseline_model, current_model]
        )

        baseline_results = comparison_results[baseline_model]
        current_results = comparison_results[current_model]

        # Check if current model meets threshold of baseline performance
        baseline_f1 = baseline_results.avg_f1_score
        current_f1 = current_results.avg_f1_score

        performance_ratio = current_f1 / baseline_f1 if baseline_f1 > 0 else 0

        regression_passed = performance_ratio >= threshold

        logger.info(f"Regression test {'PASSED' if regression_passed else 'FAILED'}")
        logger.info(f"Baseline F1: {baseline_f1:.4f}")
        logger.info(f"Current F1: {current_f1:.4f}")
        logger.info(
            f"Performance ratio: {performance_ratio:.4f} (threshold: {threshold})"
        )

        return regression_passed

    def run_full_evaluation_suite(
        self, datasets: List[str], models: List[str]
    ) -> Dict[str, Any]:
        """Run comprehensive evaluation suite"""

        logger.info("Starting full evaluation suite")
        logger.info(f"Datasets: {datasets}")
        logger.info(f"Models: {models}")

        suite_results = {
            "timestamp": datetime.now().isoformat(),
            "datasets": datasets,
            "models": models,
            "results": {},
        }

        for dataset in datasets:
            logger.info(f"Evaluating dataset: {dataset}")
            suite_results["results"][dataset] = {}

            for model in models:
                logger.info(f"Evaluating model: {model} on {dataset}")
                try:
                    results = self.run_benchmark(dataset, model)
                    suite_results["results"][dataset][model] = self._results_to_dict(
                        results
                    )
                except Exception as e:
                    logger.error(
                        f"Evaluation failed for {model} on {dataset}: {str(e)}"
                    )
                    suite_results["results"][dataset][model] = {"error": str(e)}

        # Save suite results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suite_file = self.results_dir / f"evaluation_suite_{timestamp}.json"

        with open(suite_file, "w", encoding="utf-8") as f:
            json.dump(suite_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Evaluation suite completed. Results saved: {suite_file}")

        return suite_results

    def _results_to_dict(self, results: AggregateEvaluationResults) -> Dict[str, Any]:
        """Convert results to dictionary for JSON serialization"""
        return {
            "dataset_name": results.dataset_name,
            "total_questions": results.total_questions,
            "successful_generations": results.successful_generations,
            "successful_executions": results.successful_executions,
            "avg_exact_match": results.avg_exact_match,
            "avg_precision": results.avg_precision,
            "avg_recall": results.avg_recall,
            "avg_f1_score": results.avg_f1_score,
            "execution_success_rate": results.execution_success_rate,
            "avg_execution_time": results.avg_execution_time,
            "avg_result_accuracy": results.avg_result_accuracy,
            "component_scores": results.component_scores,
            "avg_generation_time": results.avg_generation_time,
            "total_evaluation_time": results.total_evaluation_time,
            "error_types": results.error_types,
            "failed_questions": results.failed_questions,
        }

    def list_available_datasets(self) -> Dict[str, List[str]]:
        """List available datasets for benchmarking"""
        return self.dataset_loader.list_available_datasets()

    def get_benchmark_summary(self) -> Dict[str, Any]:
        """Get summary of all benchmark results"""

        if not self.results_dir.exists():
            return {"message": "No benchmark results found"}

        # Find all result files
        result_files = list(self.results_dir.glob("evaluation_*.json"))

        if not result_files:
            return {"message": "No evaluation files found"}

        summary = {
            "total_benchmarks": len(result_files),
            "latest_benchmark": max(result_files, key=lambda x: x.stat().st_mtime).name,
            "benchmarks": [],
        }

        for result_file in result_files:
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                summary["benchmarks"].append(
                    {
                        "file": result_file.name,
                        "dataset": data.get("dataset_name", "Unknown"),
                        "f1_score": data.get("avg_f1_score", 0),
                        "execution_success_rate": data.get("execution_success_rate", 0),
                        "total_questions": data.get("total_questions", 0),
                    }
                )
            except Exception as e:
                logger.warning(f"Could not read result file {result_file}: {str(e)}")

        return summary


def main():
    """Command-line interface for benchmark runner"""
    parser = argparse.ArgumentParser(description="Text-to-SQL Benchmark Runner")

    parser.add_argument(
        "--dataset", type=str, default="demo_dataset", help="Dataset name to evaluate"
    )
    parser.add_argument(
        "--model", type=str, default=None, help="Model name to evaluate"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        default=None,
        choices=["easy", "medium", "hard"],
        help="Filter by difficulty level",
    )
    parser.add_argument(
        "--tags", type=str, nargs="+", default=None, help="Filter by tags"
    )
    parser.add_argument(
        "--compare", type=str, nargs="+", default=None, help="Compare multiple models"
    )
    parser.add_argument("--regression", action="store_true", help="Run regression test")
    parser.add_argument(
        "--baseline", type=str, default=None, help="Baseline model for regression test"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Performance threshold for regression test",
    )
    parser.add_argument(
        "--suite", action="store_true", help="Run full evaluation suite"
    )

    args = parser.parse_args()

    # Initialize benchmark runner
    runner = BenchmarkRunner()

    if args.suite:
        # Run full evaluation suite
        datasets = ["demo_dataset"]
        models = [args.model] if args.model else ["google/flan-t5-base"]
        runner.run_full_evaluation_suite(datasets, models)

    elif args.compare:
        # Run model comparison
        runner.run_model_comparison(args.dataset, args.compare)

    elif args.regression and args.baseline:
        # Run regression test
        current_model = args.model or "google/flan-t5-base"
        success = runner.run_regression_test(
            args.dataset, args.baseline, current_model, args.threshold
        )
        exit(0 if success else 1)

    else:
        # Run single benchmark
        runner.run_benchmark(args.dataset, args.model, args.difficulty, args.tags)


if __name__ == "__main__":
    main()
