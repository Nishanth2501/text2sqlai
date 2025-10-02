"""
Component-level evaluation metrics for SQL queries

Provides detailed analysis of SQL query components including:
- SELECT clause accuracy
- WHERE condition accuracy
- JOIN operation accuracy
- GROUP BY accuracy
- ORDER BY accuracy
"""

import re
import sqlparse
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ComponentAnalysis:
    """Container for component-level analysis"""

    component_type: str
    predicted_items: List[str]
    ground_truth_items: List[str]
    precision: float
    recall: float
    f1_score: float
    exact_match: bool


@dataclass
class ComponentMetrics:
    """Container for all component metrics"""

    components: Dict[str, ComponentAnalysis]
    overall_precision: float
    overall_recall: float
    overall_f1_score: float
    component_importance: Dict[str, float]


class ComponentMetricsCalculator:
    """Calculate detailed component-level metrics for SQL queries"""

    def __init__(self):
        # Component importance weights for overall scoring
        self.component_weights = {
            "select_columns": 0.30,
            "where_conditions": 0.25,
            "join_operations": 0.20,
            "group_by_columns": 0.10,
            "order_by_columns": 0.10,
            "aggregate_functions": 0.05,
        }

    def extract_select_columns(self, sql: str) -> List[str]:
        """Extract SELECT columns from SQL query"""
        try:
            # Use regex to extract SELECT clause
            select_match = re.search(
                r"select\s+(.*?)(?:\s+from|\s+where|\s+group|\s+order|\s+having|$)",
                sql,
                re.IGNORECASE,
            )
            if not select_match:
                return []

            select_clause = select_match.group(1)
            # Split by comma and clean up
            columns = []
            for col in select_clause.split(","):
                col = col.strip()
                # Remove aliases (AS keyword)
                col = re.sub(r"\s+as\s+\w+", "", col, flags=re.IGNORECASE)
                # Remove aggregate functions for column comparison
                col = re.sub(r"\w+\s*\([^)]*\)", "AGG_FUNC", col)
                columns.append(col)

            return columns
        except Exception:
            return []

    def extract_where_conditions(self, sql: str) -> List[str]:
        """Extract WHERE conditions from SQL query"""
        try:
            where_match = re.search(
                r"where\s+(.*?)(?:\s+group|\s+order|\s+having|$)", sql, re.IGNORECASE
            )
            if not where_match:
                return []

            where_clause = where_match.group(1)
            # Split by AND/OR and clean up
            conditions = []
            for condition in re.split(
                r"\s+and\s+|\s+or\s+", where_clause, flags=re.IGNORECASE
            ):
                condition = condition.strip()
                # Normalize operators
                condition = re.sub(r"\s*=\s*", " = ", condition)
                condition = re.sub(r"\s*>\s*", " > ", condition)
                condition = re.sub(r"\s*<\s*", " < ", condition)
                condition = re.sub(
                    r"\s*like\s+", " LIKE ", condition, flags=re.IGNORECASE
                )
                conditions.append(condition)

            return conditions
        except Exception:
            return []

    def extract_join_operations(self, sql: str) -> List[str]:
        """Extract JOIN operations from SQL query"""
        try:
            join_matches = re.findall(
                r"join\s+(\w+)(?:\s+on\s+([^join]*?))?(?=\s+join|\s+where|\s+group|\s+order|\s+having|$)",
                sql,
                re.IGNORECASE,
            )
            joins = []
            for match in join_matches:
                table = match[0]
                condition = match[1].strip() if match[1] else ""
                join_info = f"JOIN {table}"
                if condition:
                    join_info += f" ON {condition}"
                joins.append(join_info)

            return joins
        except Exception:
            return []

    def extract_group_by_columns(self, sql: str) -> List[str]:
        """Extract GROUP BY columns from SQL query"""
        try:
            group_match = re.search(
                r"group\s+by\s+(.*?)(?:\s+having|\s+order|$)", sql, re.IGNORECASE
            )
            if not group_match:
                return []

            group_clause = group_match.group(1)
            columns = [col.strip() for col in group_clause.split(",")]
            return columns
        except Exception:
            return []

    def extract_order_by_columns(self, sql: str) -> List[str]:
        """Extract ORDER BY columns from SQL query"""
        try:
            order_match = re.search(
                r"order\s+by\s+(.*?)(?:\s+limit|$)", sql, re.IGNORECASE
            )
            if not order_match:
                return []

            order_clause = order_match.group(1)
            columns = []
            for col in order_clause.split(","):
                col = col.strip()
                # Remove ASC/DESC for comparison
                col = re.sub(r"\s+(asc|desc)", "", col, flags=re.IGNORECASE)
                columns.append(col)
            return columns
        except Exception:
            return []

    def extract_aggregate_functions(self, sql: str) -> List[str]:
        """Extract aggregate functions from SQL query"""
        try:
            # Find all aggregate functions in SELECT clause
            select_match = re.search(
                r"select\s+(.*?)(?:\s+from|\s+where|\s+group|\s+order|\s+having|$)",
                sql,
                re.IGNORECASE,
            )
            if not select_match:
                return []

            select_clause = select_match.group(1)
            agg_functions = re.findall(
                r"\b(count|sum|avg|min|max|distinct)\s*\([^)]*\)",
                select_clause,
                re.IGNORECASE,
            )
            return [func.lower() for func in agg_functions]
        except Exception:
            return []

    def calculate_component_precision_recall(
        self, predicted: List[str], ground_truth: List[str]
    ) -> Tuple[float, float]:
        """Calculate precision and recall for component lists"""
        if not ground_truth:
            return 1.0 if not predicted else 0.0
        if not predicted:
            return 0.0, 0.0

        pred_set = set(predicted)
        gt_set = set(ground_truth)

        true_positives = len(pred_set & gt_set)
        precision = true_positives / len(pred_set) if pred_set else 0.0
        recall = true_positives / len(gt_set) if gt_set else 0.0

        return precision, recall

    def calculate_component_f1(self, precision: float, recall: float) -> float:
        """Calculate F1 score for component"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def analyze_component(
        self,
        component_type: str,
        predicted_items: List[str],
        ground_truth_items: List[str],
    ) -> ComponentAnalysis:
        """Analyze a specific SQL component"""
        precision, recall = self.calculate_component_precision_recall(
            predicted_items, ground_truth_items
        )
        f1_score = self.calculate_component_f1(precision, recall)
        exact_match = predicted_items == ground_truth_items

        return ComponentAnalysis(
            component_type=component_type,
            predicted_items=predicted_items,
            ground_truth_items=ground_truth_items,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            exact_match=exact_match,
        )

    def calculate_component_metrics(
        self, predicted_sql: str, ground_truth_sql: str
    ) -> ComponentMetrics:
        """Calculate comprehensive component-level metrics"""

        # Extract components from both queries
        predicted_components = {
            "select_columns": self.extract_select_columns(predicted_sql),
            "where_conditions": self.extract_where_conditions(predicted_sql),
            "join_operations": self.extract_join_operations(predicted_sql),
            "group_by_columns": self.extract_group_by_columns(predicted_sql),
            "order_by_columns": self.extract_order_by_columns(predicted_sql),
            "aggregate_functions": self.extract_aggregate_functions(predicted_sql),
        }

        ground_truth_components = {
            "select_columns": self.extract_select_columns(ground_truth_sql),
            "where_conditions": self.extract_where_conditions(ground_truth_sql),
            "join_operations": self.extract_join_operations(ground_truth_sql),
            "group_by_columns": self.extract_group_by_columns(ground_truth_sql),
            "order_by_columns": self.extract_order_by_columns(ground_truth_sql),
            "aggregate_functions": self.extract_aggregate_functions(ground_truth_sql),
        }

        # Analyze each component
        component_analyses = {}
        weighted_precision = 0.0
        weighted_recall = 0.0
        total_weight = 0.0

        for component_type in self.component_weights:
            analysis = self.analyze_component(
                component_type,
                predicted_components[component_type],
                ground_truth_components[component_type],
            )
            component_analyses[component_type] = analysis

            # Add to weighted averages
            weight = self.component_weights[component_type]
            weighted_precision += analysis.precision * weight
            weighted_recall += analysis.recall * weight
            total_weight += weight

        # Calculate overall metrics
        overall_precision = (
            weighted_precision / total_weight if total_weight > 0 else 0.0
        )
        overall_recall = weighted_recall / total_weight if total_weight > 0 else 0.0
        overall_f1_score = self.calculate_component_f1(
            overall_precision, overall_recall
        )

        return ComponentMetrics(
            components=component_analyses,
            overall_precision=overall_precision,
            overall_recall=overall_recall,
            overall_f1_score=overall_f1_score,
            component_importance=self.component_weights,
        )
