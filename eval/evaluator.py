"""
Main Text-to-SQL evaluator

Orchestrates the evaluation process including:
- Loading datasets
- Generating SQL predictions
- Calculating metrics
- Executing queries
- Generating reports
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.nlp.generator import T2SQLGenerator
from src.db.introspect import get_schema_summary, to_compact_schema
from .datasets.dataset_loader import DatasetLoader, Dataset, Question
from .metrics.sql_metrics import SQLMetricsCalculator, SQLMetrics
from .metrics.execution_metrics import ExecutionMetricsCalculator, ExecutionMetrics
from .metrics.component_metrics import ComponentMetricsCalculator, ComponentMetrics
from src.utils.logger import get_logger

logger = get_logger("text2sql.evaluator")


@dataclass
class EvaluationResult:
    """Container for evaluation results"""

    question_id: str
    question: str
    predicted_sql: str
    ground_truth_sql: str
    sql_metrics: SQLMetrics
    execution_metrics: ExecutionMetrics
    component_metrics: ComponentMetrics
    generation_time: float
    total_time: float


@dataclass
class AggregateEvaluationResults:
    """Container for aggregate evaluation results"""

    dataset_name: str
    total_questions: int
    successful_generations: int
    successful_executions: int

    # SQL Metrics
    avg_exact_match: float
    avg_precision: float
    avg_recall: float
    avg_f1_score: float

    # Execution Metrics
    execution_success_rate: float
    avg_execution_time: float
    avg_result_accuracy: float

    # Component Metrics
    component_scores: Dict[str, Dict[str, float]]

    # Performance Metrics
    avg_generation_time: float
    total_evaluation_time: float

    # Error Analysis
    error_types: Dict[str, int]
    failed_questions: List[str]


class Text2SQLEvaluator:
    """Main evaluator for Text-to-SQL generation"""

    def __init__(self, database_url: str = "sqlite:///data/demo.sqlite"):
        self.database_url = database_url
        self.engine = create_engine(database_url, future=True)

        # Initialize metric calculators
        self.sql_calculator = SQLMetricsCalculator()
        self.execution_calculator = ExecutionMetricsCalculator()
        self.component_calculator = ComponentMetricsCalculator()

        # Initialize dataset loader
        self.dataset_loader = DatasetLoader()

        logger.info(f"Initialized Text2SQL Evaluator with database: {database_url}")

    def evaluate_question(
        self, question: Question, model: T2SQLGenerator
    ) -> EvaluationResult:
        """Evaluate a single question"""
        start_time = time.time()

        logger.info(f"Evaluating question: {question.id}")

        # Generate SQL
        generation_start = time.time()
        try:
            predicted_sql = model.generate(question.question)
            generation_time = time.time() - generation_start
            generation_success = True
        except Exception as e:
            logger.error(f"SQL generation failed for {question.id}: {str(e)}")
            predicted_sql = ""
            generation_time = time.time() - generation_start
            generation_success = False

        # Calculate SQL metrics
        sql_metrics = self.sql_calculator.evaluate_sql(
            predicted_sql, question.sql, execution_success=generation_success
        )

        # Execute query if generation was successful
        execution_metrics = None
        if generation_success and predicted_sql:
            execution_metrics = self.execution_calculator.evaluate_execution(
                self.engine, predicted_sql, question.expected_result_count
            )
        else:
            execution_metrics = ExecutionMetrics(
                success=False,
                execution_time=0.0,
                result_count=0,
                expected_count=question.expected_result_count,
                result_accuracy=0.0,
                error_message="SQL generation failed",
                performance_score=0.0,
            )

        # Calculate component metrics
        component_metrics = self.component_calculator.calculate_component_metrics(
            predicted_sql, question.sql
        )

        total_time = time.time() - start_time

        return EvaluationResult(
            question_id=question.id,
            question=question.question,
            predicted_sql=predicted_sql,
            ground_truth_sql=question.sql,
            sql_metrics=sql_metrics,
            execution_metrics=execution_metrics,
            component_metrics=component_metrics,
            generation_time=generation_time,
            total_time=total_time,
        )

    def evaluate_dataset(
        self, dataset: Dataset, model_name: Optional[str] = None
    ) -> AggregateEvaluationResults:
        """Evaluate entire dataset"""
        logger.info(f"Starting evaluation of dataset: {dataset.name}")
        logger.info(f"Total questions: {dataset.total_questions}")

        start_time = time.time()

        # Get schema for model initialization
        tables, cols = get_schema_summary(self.engine)
        schema_txt = to_compact_schema(tables, cols)

        # Initialize model
        model = T2SQLGenerator(schema_txt=schema_txt, model_name=model_name)

        # Evaluate each question
        results = []
        failed_questions = []
        error_types = {}

        for i, question in enumerate(dataset.questions):
            logger.info(
                f"Processing question {i + 1}/{dataset.total_questions}: {question.id}"
            )

            try:
                result = self.evaluate_question(question, model)
                results.append(result)

                # Track errors
                if not result.sql_metrics.syntax_valid:
                    error_types["syntax_error"] = error_types.get("syntax_error", 0) + 1
                if not result.execution_metrics.success:
                    error_types["execution_error"] = (
                        error_types.get("execution_error", 0) + 1
                    )

            except Exception as e:
                logger.error(f"Evaluation failed for {question.id}: {str(e)}")
                failed_questions.append(question.id)
                error_types["evaluation_error"] = (
                    error_types.get("evaluation_error", 0) + 1
                )

        # Calculate aggregate results
        aggregate_results = self._calculate_aggregate_results(
            dataset, results, failed_questions, error_types, time.time() - start_time
        )

        logger.info(f"Evaluation completed in {time.time() - start_time:.2f} seconds")
        return aggregate_results

    def _calculate_aggregate_results(
        self,
        dataset: Dataset,
        results: List[EvaluationResult],
        failed_questions: List[str],
        error_types: Dict[str, int],
        total_time: float,
    ) -> AggregateEvaluationResults:
        """Calculate aggregate results from individual evaluations"""

        if not results:
            return AggregateEvaluationResults(
                dataset_name=dataset.name,
                total_questions=dataset.total_questions,
                successful_generations=0,
                successful_executions=0,
                avg_exact_match=0.0,
                avg_precision=0.0,
                avg_recall=0.0,
                avg_f1_score=0.0,
                execution_success_rate=0.0,
                avg_execution_time=0.0,
                avg_result_accuracy=0.0,
                component_scores={},
                avg_generation_time=0.0,
                total_evaluation_time=total_time,
                error_types=error_types,
                failed_questions=failed_questions,
            )

        # Calculate averages
        avg_exact_match = sum(r.sql_metrics.exact_match for r in results) / len(results)
        avg_precision = sum(r.sql_metrics.precision for r in results) / len(results)
        avg_recall = sum(r.sql_metrics.recall for r in results) / len(results)
        avg_f1_score = sum(r.sql_metrics.f1_score for r in results) / len(results)

        # Execution metrics
        successful_executions = sum(1 for r in results if r.execution_metrics.success)
        execution_success_rate = successful_executions / len(results)
        avg_execution_time = sum(
            r.execution_metrics.execution_time for r in results
        ) / len(results)
        avg_result_accuracy = sum(
            r.execution_metrics.result_accuracy for r in results
        ) / len(results)

        # Performance metrics
        avg_generation_time = sum(r.generation_time for r in results) / len(results)

        # Component scores (average across all results)
        component_scores = {}
        if results:
            first_result = results[0]
            for component_type in first_result.component_metrics.components:
                component_scores[component_type] = {
                    "precision": sum(
                        r.component_metrics.components[component_type].precision
                        for r in results
                    )
                    / len(results),
                    "recall": sum(
                        r.component_metrics.components[component_type].recall
                        for r in results
                    )
                    / len(results),
                    "f1_score": sum(
                        r.component_metrics.components[component_type].f1_score
                        for r in results
                    )
                    / len(results),
                }

        return AggregateEvaluationResults(
            dataset_name=dataset.name,
            total_questions=dataset.total_questions,
            successful_generations=len(results),
            successful_executions=successful_executions,
            avg_exact_match=avg_exact_match,
            avg_precision=avg_precision,
            avg_recall=avg_recall,
            avg_f1_score=avg_f1_score,
            execution_success_rate=execution_success_rate,
            avg_execution_time=avg_execution_time,
            avg_result_accuracy=avg_result_accuracy,
            component_scores=component_scores,
            avg_generation_time=avg_generation_time,
            total_evaluation_time=total_time,
            error_types=error_types,
            failed_questions=failed_questions,
        )

    def save_results(
        self,
        results: AggregateEvaluationResults,
        output_dir: str = "results/benchmarks",
    ):
        """Save evaluation results to file"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{results.dataset_name}_{timestamp}.json"
        filepath = output_path / filename

        # Convert results to dictionary
        results_dict = asdict(results)

        # Save to JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {filepath}")
        return filepath

    def compare_models(
        self, dataset: Dataset, model_names: List[str]
    ) -> Dict[str, AggregateEvaluationResults]:
        """Compare multiple models on the same dataset"""
        results = {}

        for model_name in model_names:
            logger.info(f"Evaluating model: {model_name}")
            model_results = self.evaluate_dataset(dataset, model_name)
            results[model_name] = model_results

        return results
