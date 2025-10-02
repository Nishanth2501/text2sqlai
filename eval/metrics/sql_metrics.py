"""
SQL-level evaluation metrics for Text-to-SQL generation

Provides precision, recall, and F1-score calculations for SQL queries
at various levels of granularity.
"""

import re
import sqlparse
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter


@dataclass
class SQLMetrics:
    """Container for SQL evaluation metrics"""

    exact_match: float
    precision: float
    recall: float
    f1_score: float
    component_scores: Dict[str, Dict[str, float]]
    execution_success: bool
    syntax_valid: bool


class SQLMetricsCalculator:
    """Calculate various SQL evaluation metrics"""

    def __init__(self):
        self.component_weights = {
            "select": 0.25,
            "where": 0.25,
            "join": 0.20,
            "group_by": 0.15,
            "order_by": 0.10,
            "having": 0.05,
        }

    def normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison"""
        if not sql:
            return ""

        # Remove extra whitespace and normalize case
        sql = re.sub(r"\s+", " ", sql.strip().lower())

        # Remove trailing semicolons
        sql = sql.rstrip(";")

        # Normalize LIMIT clauses
        sql = re.sub(r"limit\s+\d+", "limit 200", sql)

        return sql

    def extract_sql_components(self, sql: str) -> Dict[str, List[str]]:
        """Extract SQL components for comparison"""
        components = {
            "select": [],
            "where": [],
            "join": [],
            "group_by": [],
            "order_by": [],
            "having": [],
        }

        try:
            parsed = sqlparse.parse(sql)[0]
            self._extract_from_parsed(parsed, components)
        except Exception:
            # Fallback to regex-based extraction
            self._extract_with_regex(sql, components)

        return components

    def _extract_from_parsed(self, statement, components: Dict[str, List[str]]):
        """Extract components from parsed SQL"""
        for token in statement.flatten():
            if token.ttype is sqlparse.tokens.Keyword:
                keyword = token.value.lower()
                if keyword in components:
                    # Extract relevant parts after keyword
                    pass

    def _extract_with_regex(self, sql: str, components: Dict[str, List[str]]):
        """Fallback regex-based component extraction"""
        # SELECT columns
        select_match = re.search(
            r"select\s+(.*?)(?:\s+from|\s+where|\s+group|\s+order|\s+having|$)",
            sql,
            re.IGNORECASE,
        )
        if select_match:
            select_clause = select_match.group(1)
            components["select"] = [col.strip() for col in select_clause.split(",")]

        # WHERE conditions
        where_match = re.search(
            r"where\s+(.*?)(?:\s+group|\s+order|\s+having|$)", sql, re.IGNORECASE
        )
        if where_match:
            where_clause = where_match.group(1)
            components["where"] = [
                cond.strip()
                for cond in re.split(
                    r"\s+and\s+|\s+or\s+", where_clause, flags=re.IGNORECASE
                )
            ]

        # JOIN operations
        join_matches = re.findall(r"join\s+(\w+)", sql, re.IGNORECASE)
        components["join"] = join_matches

        # GROUP BY
        group_match = re.search(
            r"group\s+by\s+(.*?)(?:\s+having|\s+order|$)", sql, re.IGNORECASE
        )
        if group_match:
            group_clause = group_match.group(1)
            components["group_by"] = [col.strip() for col in group_clause.split(",")]

        # ORDER BY
        order_match = re.search(r"order\s+by\s+(.*?)(?:\s+limit|$)", sql, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1)
            components["order_by"] = [col.strip() for col in order_clause.split(",")]

    def calculate_precision_recall(
        self, predicted: List[str], ground_truth: List[str]
    ) -> Tuple[float, float]:
        """Calculate precision and recall for two lists"""
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

    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calculate F1 score from precision and recall"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def calculate_component_metrics(
        self, predicted_sql: str, ground_truth_sql: str
    ) -> Dict[str, Dict[str, float]]:
        """Calculate component-level metrics"""
        pred_components = self.extract_sql_components(predicted_sql)
        gt_components = self.extract_sql_components(ground_truth_sql)

        component_scores = {}
        total_precision = 0.0
        total_recall = 0.0
        total_weight = 0.0

        for component in self.component_weights:
            if component in pred_components and component in gt_components:
                precision, recall = self.calculate_precision_recall(
                    pred_components[component], gt_components[component]
                )
                f1 = self.calculate_f1_score(precision, recall)

                component_scores[component] = {
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                }

                weight = self.component_weights[component]
                total_precision += precision * weight
                total_recall += recall * weight
                total_weight += weight

        # Overall weighted metrics
        if total_weight > 0:
            component_scores["overall"] = {
                "precision": total_precision / total_weight,
                "recall": total_recall / total_weight,
                "f1_score": self.calculate_f1_score(
                    total_precision / total_weight, total_recall / total_weight
                ),
            }

        return component_scores

    def validate_sql_syntax(self, sql: str) -> bool:
        """Validate SQL syntax"""
        try:
            sqlparse.parse(sql)
            return True
        except Exception:
            return False

    def calculate_exact_match(self, predicted_sql: str, ground_truth_sql: str) -> float:
        """Calculate exact match score (normalized comparison)"""
        pred_norm = self.normalize_sql(predicted_sql)
        gt_norm = self.normalize_sql(ground_truth_sql)

        return 1.0 if pred_norm == gt_norm else 0.0

    def evaluate_sql(
        self, predicted_sql: str, ground_truth_sql: str, execution_success: bool = True
    ) -> SQLMetrics:
        """Calculate comprehensive SQL evaluation metrics"""

        # Exact match
        exact_match = self.calculate_exact_match(predicted_sql, ground_truth_sql)

        # Component-level metrics
        component_scores = self.calculate_component_metrics(
            predicted_sql, ground_truth_sql
        )

        # Overall precision/recall from components
        overall_precision = component_scores.get("overall", {}).get("precision", 0.0)
        overall_recall = component_scores.get("overall", {}).get("recall", 0.0)
        overall_f1 = component_scores.get("overall", {}).get("f1_score", 0.0)

        # Syntax validation
        syntax_valid = self.validate_sql_syntax(predicted_sql)

        return SQLMetrics(
            exact_match=exact_match,
            precision=overall_precision,
            recall=overall_recall,
            f1_score=overall_f1,
            component_scores=component_scores,
            execution_success=execution_success,
            syntax_valid=syntax_valid,
        )
