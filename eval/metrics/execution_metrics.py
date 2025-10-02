"""
Execution-level evaluation metrics for SQL queries

Provides metrics for query execution success, performance, and result accuracy.
"""

import time
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.engine import Engine


@dataclass
class ExecutionMetrics:
    """Container for execution evaluation metrics"""

    success: bool
    execution_time: float
    result_count: int
    expected_count: Optional[int]
    result_accuracy: float
    error_message: Optional[str]
    performance_score: float


class ExecutionMetricsCalculator:
    """Calculate execution-related evaluation metrics"""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def execute_query(
        self, engine: Engine, sql: str
    ) -> Tuple[bool, Optional[pd.DataFrame], str, float]:
        """Execute SQL query and return results with timing"""
        start_time = time.time()

        try:
            with engine.begin() as conn:
                df = pd.read_sql(text(sql), conn)
            execution_time = time.time() - start_time

            return True, df, "", execution_time

        except Exception as e:
            execution_time = time.time() - start_time
            return False, None, str(e), execution_time

    def calculate_result_accuracy(
        self, actual_count: int, expected_count: Optional[int]
    ) -> float:
        """Calculate accuracy based on result count"""
        if expected_count is None:
            return 1.0  # No expected count to compare against

        if expected_count == 0:
            return 1.0 if actual_count == 0 else 0.0

        # Use relative accuracy for non-zero expected counts
        accuracy = 1.0 - abs(actual_count - expected_count) / max(
            actual_count, expected_count
        )
        return max(0.0, accuracy)  # Ensure non-negative

    def calculate_performance_score(
        self, execution_time: float, success: bool
    ) -> float:
        """Calculate performance score based on execution time"""
        if not success:
            return 0.0

        # Performance score decreases with execution time
        # Optimal time is < 1 second (score = 1.0)
        # Score decreases linearly after 1 second
        if execution_time <= 1.0:
            return 1.0
        elif execution_time <= 10.0:
            return 1.0 - (execution_time - 1.0) / 9.0 * 0.5  # Linear decrease to 0.5
        else:
            return max(
                0.0, 0.5 - (execution_time - 10.0) / 20.0 * 0.5
            )  # Further decrease

    def evaluate_execution(
        self, engine: Engine, sql: str, expected_count: Optional[int] = None
    ) -> ExecutionMetrics:
        """Evaluate SQL query execution"""

        # Execute query
        success, df, error_msg, execution_time = self.execute_query(engine, sql)

        # Get result count
        result_count = len(df) if df is not None else 0

        # Calculate accuracy
        result_accuracy = self.calculate_result_accuracy(result_count, expected_count)

        # Calculate performance score
        performance_score = self.calculate_performance_score(execution_time, success)

        return ExecutionMetrics(
            success=success,
            execution_time=execution_time,
            result_count=result_count,
            expected_count=expected_count,
            result_accuracy=result_accuracy,
            error_message=error_msg,
            performance_score=performance_score,
        )

    def batch_evaluate_executions(
        self, engine: Engine, sql_queries: list, expected_counts: Optional[list] = None
    ) -> list:
        """Evaluate multiple SQL queries in batch"""
        if expected_counts is None:
            expected_counts = [None] * len(sql_queries)

        results = []
        for sql, expected_count in zip(sql_queries, expected_counts):
            metrics = self.evaluate_execution(engine, sql, expected_count)
            results.append(metrics)

        return results

    def calculate_aggregate_metrics(self, execution_results: list) -> Dict[str, Any]:
        """Calculate aggregate metrics from multiple execution results"""
        if not execution_results:
            return {}

        total_queries = len(execution_results)
        successful_queries = sum(1 for r in execution_results if r.success)
        execution_success_rate = successful_queries / total_queries

        # Average execution time (only for successful queries)
        successful_times = [r.execution_time for r in execution_results if r.success]
        avg_execution_time = (
            sum(successful_times) / len(successful_times) if successful_times else 0.0
        )

        # Average result accuracy
        avg_result_accuracy = (
            sum(r.result_accuracy for r in execution_results) / total_queries
        )

        # Average performance score
        avg_performance_score = (
            sum(r.performance_score for r in execution_results) / total_queries
        )

        # Error analysis
        error_types = {}
        for result in execution_results:
            if not result.success and result.error_message:
                # Categorize errors
                error_msg = result.error_message.lower()
                if "syntax" in error_msg:
                    error_types["syntax_error"] = error_types.get("syntax_error", 0) + 1
                elif "table" in error_msg or "column" in error_msg:
                    error_types["schema_error"] = error_types.get("schema_error", 0) + 1
                elif "timeout" in error_msg:
                    error_types["timeout"] = error_types.get("timeout", 0) + 1
                else:
                    error_types["other"] = error_types.get("other", 0) + 1

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "execution_success_rate": execution_success_rate,
            "avg_execution_time": avg_execution_time,
            "avg_result_accuracy": avg_result_accuracy,
            "avg_performance_score": avg_performance_score,
            "error_types": error_types,
            "max_execution_time": max(r.execution_time for r in execution_results),
            "min_execution_time": min(r.execution_time for r in execution_results),
        }
