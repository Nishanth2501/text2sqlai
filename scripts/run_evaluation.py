#!/usr/bin/env python3
"""
Command-line evaluation script for Text-to-SQL Assistant

Usage:
    python scripts/run_evaluation.py --dataset demo_dataset
    python scripts/run_evaluation.py --dataset demo_dataset --model google/flan-t5-base
    python scripts/run_evaluation.py --compare --models google/flan-t5-base microsoft/DialoGPT-medium
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eval.benchmark import BenchmarkRunner
from eval.datasets.dataset_loader import DatasetLoader
from src.utils.logger import get_logger

logger = get_logger("text2sql.evaluation_cli")


def main():
    parser = argparse.ArgumentParser(description="Text-to-SQL Evaluation CLI")

    # Dataset options
    parser.add_argument(
        "--dataset", type=str, default="demo_dataset", help="Dataset name to evaluate"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        help="Filter by difficulty level",
    )
    parser.add_argument("--tags", type=str, nargs="+", help="Filter by tags")

    # Model options
    parser.add_argument(
        "--model",
        type=str,
        default="google/flan-t5-base",
        help="Language model name to evaluate",
    )
    parser.add_argument(
        "--models", type=str, nargs="+", help="Multiple language models for comparison"
    )

    # Evaluation options
    parser.add_argument(
        "--compare", action="store_true", help="Compare multiple models"
    )
    parser.add_argument("--regression", action="store_true", help="Run regression test")
    parser.add_argument(
        "--baseline", type=str, help="Baseline language model for regression test"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Performance threshold for regression test",
    )

    # Output options
    parser.add_argument(
        "--output", type=str, default="results", help="Output directory for results"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Database options
    parser.add_argument(
        "--database",
        type=str,
        default="sqlite:///data/demo.sqlite",
        help="Database URL",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel("DEBUG")

    # Initialize benchmark runner
    runner = BenchmarkRunner(args.database, args.output)

    try:
        if args.compare and args.models:
            # Language model comparison
            logger.info(f"Running model comparison on {args.dataset}")
            logger.info(f"Language models: {args.models}")

            results = runner.run_model_comparison(args.dataset, args.models)

            # Print summary
            print("\n" + "=" * 80)
            print("LANGUAGE MODEL COMPARISON SUMMARY")
            print("=" * 80)

            for model_name, result in results.items():
                print(f"\n{model_name}:")
                print(f"  F1 Score: {result.avg_f1_score:.3f}")
                print(f"  Exact Match: {result.avg_exact_match:.3f}")
                print(f"  Execution Success: {result.execution_success_rate:.3f}")
                print(f"  Avg Generation Time: {result.avg_generation_time:.3f}s")

        elif args.regression and args.baseline:
            # Regression test
            logger.info(f"Running regression test: {args.baseline} vs {args.model}")

            success = runner.run_regression_test(
                args.dataset, args.baseline, args.model, args.threshold
            )

            print("\n" + "=" * 80)
            print("REGRESSION TEST RESULT")
            print("=" * 80)
            print(f"Status: {'PASSED' if success else 'FAILED'}")
            print(f"Threshold: {args.threshold}")

            if not success:
                sys.exit(1)

        else:
            # Single evaluation
            logger.info(f"Running evaluation on {args.dataset} with model {args.model}")

            results = runner.run_benchmark(
                args.dataset, args.model, args.difficulty, args.tags
            )

            # Print summary
            print("\n" + "=" * 80)
            print("EVALUATION SUMMARY")
            print("=" * 80)
            print(f"Dataset: {results.dataset_name}")
            print(f"Total Questions: {results.total_questions}")
            print(f"Successful Generations: {results.successful_generations}")
            print(f"Successful Executions: {results.successful_executions}")
            print(f"Execution Success Rate: {results.execution_success_rate:.3f}")
            print(f"\nMetrics:")
            print(f"  Exact Match: {results.avg_exact_match:.3f}")
            print(f"  Precision: {results.avg_precision:.3f}")
            print(f"  Recall: {results.avg_recall:.3f}")
            print(f"  F1 Score: {results.avg_f1_score:.3f}")
            print(f"  Result Accuracy: {results.avg_result_accuracy:.3f}")
            print(f"\nPerformance:")
            print(f"  Avg Generation Time: {results.avg_generation_time:.3f}s")
            print(f"  Avg Execution Time: {results.avg_execution_time:.3f}s")
            print(f"  Total Evaluation Time: {results.total_evaluation_time:.3f}s")

            if results.error_types:
                print(f"\nErrors:")
                for error_type, count in results.error_types.items():
                    print(f"  {error_type}: {count}")

            if results.failed_questions:
                print(f"\nFailed Questions: {len(results.failed_questions)}")
                for qid in results.failed_questions[:5]:  # Show first 5
                    print(f"  {qid}")
                if len(results.failed_questions) > 5:
                    print(f"  ... and {len(results.failed_questions) - 5} more")

        print("\n" + "=" * 80)
        print("EVALUATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        print(f"\nERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
