"""
Evaluation framework for Text-to-SQL Assistant

This module provides comprehensive evaluation capabilities including:
- Precision/Recall metrics for SQL generation
- Component-level accuracy analysis
- Execution success rate tracking
- Automated benchmarking and testing
- Report generation and visualization
"""

from .evaluator import Text2SQLEvaluator
from .benchmark import BenchmarkRunner
from .report_generator import ReportGenerator

__all__ = [
    "Text2SQLEvaluator",
    "BenchmarkRunner", 
    "ReportGenerator"
]

__version__ = "1.0.0"
