#!/usr/bin/env python3
"""
Streamlit UI for Text-to-SQL Evaluation

Provides an interactive interface for:
- Running evaluations
- Viewing results
- Comparing language models
- Analyzing performance
"""

import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eval.benchmark import BenchmarkRunner
from eval.datasets.dataset_loader import DatasetLoader
from eval.report_generator import ReportGenerator
from src.utils.logger import get_logger

logger = get_logger("text2sql.evaluation_ui")

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize components
@st.cache_resource
def get_benchmark_runner():
    return BenchmarkRunner()


@st.cache_resource
def get_dataset_loader():
    return DatasetLoader()


@st.cache_resource
def get_report_generator():
    return ReportGenerator()


def main():
    st.title("📊 Text-to-SQL Evaluation Dashboard")
    st.markdown(
        "Comprehensive evaluation and benchmarking for Text-to-SQL language models"
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Database URL
        database_url = st.text_input(
            "Database URL",
            value="sqlite:///data/demo.sqlite",
            help="SQLAlchemy database URL",
        )

        # Language model selection
        model_name = st.text_input(
            "Language Model Name",
            value="google/flan-t5-base",
            help="HuggingFace language model identifier",
        )

        # Dataset selection
        dataset_loader = get_dataset_loader()
        available_datasets = dataset_loader.list_available_datasets()

        if available_datasets.get("custom"):
            dataset_name = st.selectbox(
                "Dataset",
                options=available_datasets["custom"],
                help="Select evaluation dataset",
            )
        else:
            st.warning(
                "No datasets found. Please add datasets to eval/datasets/custom/"
            )
            return

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🚀 Run Evaluation", "📈 View Results", "⚖️ Compare Models", "📊 Analytics"]
    )

    with tab1:
        run_evaluation_tab(dataset_name, model_name, database_url)

    with tab2:
        view_results_tab()

    with tab3:
        compare_models_tab(dataset_name, database_url)

    with tab4:
        analytics_tab()


def run_evaluation_tab(dataset_name, model_name, database_url):
    st.header("🚀 Run New Evaluation")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Evaluation parameters
        st.subheader("Evaluation Parameters")

        # Difficulty filter
        difficulty_filter = st.selectbox(
            "Difficulty Filter",
            options=[None, "easy", "medium", "hard"],
            help="Filter questions by difficulty level",
        )

        # Tag filter
        tag_filter = st.multiselect(
            "Tag Filter",
            options=[
                "select",
                "where",
                "join",
                "aggregation",
                "group_by",
                "order_by",
                "basic",
                "filtering",
            ],
            help="Filter questions by tags",
        )

        # Advanced settings
        with st.expander("Advanced Settings"):
            max_questions = st.number_input(
                "Max Questions",
                min_value=1,
                max_value=1000,
                value=10,
                help="Limit number of questions to evaluate",
            )

            timeout = st.number_input(
                "Timeout (seconds)",
                min_value=10,
                max_value=300,
                value=30,
                help="Timeout for SQL generation",
            )

    with col2:
        st.subheader("Quick Actions")

        if st.button("🎯 Run Evaluation", type="primary"):
            run_evaluation(
                dataset_name, model_name, difficulty_filter, tag_filter, max_questions
            )

        if st.button("📊 View Latest Results"):
            st.session_state.active_tab = "results"
            st.rerun()

        if st.button("⚖️ Compare Models"):
            st.session_state.active_tab = "compare"
            st.rerun()


def run_evaluation(
    dataset_name, model_name, difficulty_filter, tag_filter, max_questions
):
    """Run evaluation with progress tracking"""

    with st.spinner("Initializing evaluation..."):
        runner = get_benchmark_runner()

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Loading dataset...")
        progress_bar.progress(10)

        # Load dataset
        dataset_loader = get_dataset_loader()
        dataset = dataset_loader.load_custom_dataset(f"{dataset_name}.json")

        # Apply filters
        if difficulty_filter:
            dataset = dataset_loader.filter_dataset_by_difficulty(
                dataset, difficulty_filter
            )

        if tag_filter:
            dataset = dataset_loader.filter_dataset_by_tags(dataset, tag_filter)

        # Limit questions if specified
        if max_questions < len(dataset.questions):
            dataset.questions = dataset.questions[:max_questions]
            dataset.total_questions = len(dataset.questions)

        status_text.text(
            f"Running evaluation on {dataset.total_questions} questions..."
        )
        progress_bar.progress(30)

        # Run evaluation
        results = runner.evaluator.evaluate_dataset(dataset, model_name)

        progress_bar.progress(90)
        status_text.text("Generating report...")

        # Save results
        runner.evaluator.save_results(results, str(runner.results_dir))

        # Generate report
        report_generator = get_report_generator()
        report_path = report_generator.generate_html_report(
            results, str(runner.results_dir)
        )

        progress_bar.progress(100)
        status_text.text("Evaluation completed!")

        # Display results summary
        display_results_summary(results, report_path)

    except Exception as e:
        st.error(f"Evaluation failed: {str(e)}")
        logger.error(f"Evaluation failed: {str(e)}")


def display_results_summary(results, report_path):
    """Display evaluation results summary"""

    st.success("✅ Evaluation completed successfully!")

    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("F1 Score", f"{results.avg_f1_score:.3f}")

    with col2:
        st.metric("Exact Match", f"{results.avg_exact_match:.3f}")

    with col3:
        st.metric("Execution Success", f"{results.execution_success_rate:.3f}")

    with col4:
        st.metric("Total Questions", results.total_questions)

    # Detailed metrics
    st.subheader("📊 Detailed Metrics")

    metrics_data = {
        "Metric": [
            "Precision",
            "Recall",
            "Result Accuracy",
            "Generation Time",
            "Execution Time",
        ],
        "Value": [
            f"{results.avg_precision:.3f}",
            f"{results.avg_recall:.3f}",
            f"{results.avg_result_accuracy:.3f}",
            f"{results.avg_generation_time:.3f}s",
            f"{results.avg_execution_time:.3f}s",
        ],
    }

    st.table(pd.DataFrame(metrics_data))

    # Component analysis
    if results.component_scores:
        st.subheader("🔍 Component Analysis")

        component_data = []
        for component, scores in results.component_scores.items():
            if component != "overall":
                component_data.append(
                    {
                        "Component": component.replace("_", " ").title(),
                        "Precision": f"{scores.get('precision', 0):.3f}",
                        "Recall": f"{scores.get('recall', 0):.3f}",
                        "F1 Score": f"{scores.get('f1_score', 0):.3f}",
                    }
                )

        if component_data:
            st.table(pd.DataFrame(component_data))

    # Report link
    st.subheader("📄 Full Report")
    st.markdown(f"📊 [View detailed HTML report](file://{report_path})")


def view_results_tab():
    st.header("📈 View Evaluation Results")

    runner = get_benchmark_runner()

    # Get available results
    results_dir = Path(runner.results_dir)
    if not results_dir.exists():
        st.warning("No evaluation results found. Run an evaluation first.")
        return

    result_files = list(results_dir.glob("evaluation_*.json"))
    if not result_files:
        st.warning("No evaluation files found.")
        return

    # Select result file
    result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    selected_file = st.selectbox(
        "Select Result File",
        options=result_files,
        format_func=lambda x: f"{x.stem} ({datetime.fromtimestamp(x.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})",
    )

    if selected_file:
        try:
            with open(selected_file, "r") as f:
                results_data = json.load(f)

            display_historical_results(results_data)

        except Exception as e:
            st.error(f"Error loading results: {str(e)}")


def display_historical_results(results_data):
    """Display historical evaluation results"""

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("F1 Score", f"{results_data.get('avg_f1_score', 0):.3f}")

    with col2:
        st.metric("Exact Match", f"{results_data.get('avg_exact_match', 0):.3f}")

    with col3:
        st.metric(
            "Execution Success", f"{results_data.get('execution_success_rate', 0):.3f}"
        )

    with col4:
        st.metric("Total Questions", results_data.get("total_questions", 0))

    # Performance visualization
    st.subheader("📊 Performance Visualization")

    # Create performance chart
    metrics = ["F1 Score", "Exact Match", "Precision", "Recall", "Result Accuracy"]
    values = [
        results_data.get("avg_f1_score", 0),
        results_data.get("avg_exact_match", 0),
        results_data.get("avg_precision", 0),
        results_data.get("avg_recall", 0),
        results_data.get("avg_result_accuracy", 0),
    ]

    fig = px.bar(
        x=metrics,
        y=values,
        title="Evaluation Metrics",
        labels={"x": "Metric", "y": "Score"},
    )
    fig.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)

    # Component analysis
    if "component_scores" in results_data:
        component_scores = results_data["component_scores"]

        if component_scores:
            st.subheader("🔍 Component Analysis")

            components = []
            f1_scores = []

            for component, scores in component_scores.items():
                if component != "overall":
                    components.append(component.replace("_", " ").title())
                    f1_scores.append(scores.get("f1_score", 0))

            if components:
                fig = px.bar(
                    x=components,
                    y=f1_scores,
                    title="Component F1 Scores",
                    labels={"x": "Component", "y": "F1 Score"},
                )
                fig.update_layout(yaxis_range=[0, 1])
                st.plotly_chart(fig, use_container_width=True)


def compare_models_tab(dataset_name, database_url):
    st.header("⚖️ Compare Models")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Model Comparison")

        # Model inputs
        models_input = st.text_area(
            "Model Names (one per line)",
            value="google/flan-t5-base\nmicrosoft/DialoGPT-medium",
            help="Enter model names, one per line",
        )

        models = [m.strip() for m in models_input.split("\n") if m.strip()]

        # Comparison parameters
        with st.expander("Comparison Settings"):
            max_questions = st.number_input(
                "Max Questions per Model",
                min_value=1,
                max_value=100,
                value=5,
                help="Limit questions for faster comparison",
            )

    with col2:
        st.subheader("Actions")

        if st.button("🔄 Run Comparison", type="primary"):
            if len(models) < 2:
                st.error("Please enter at least 2 models for comparison")
                return

            run_model_comparison(dataset_name, models, max_questions)


def run_model_comparison(dataset_name, models, max_questions):
    """Run model comparison"""

    with st.spinner("Running model comparison..."):
        try:
            runner = get_benchmark_runner()

            # Load and limit dataset
            dataset_loader = get_dataset_loader()
            dataset = dataset_loader.load_custom_dataset(f"{dataset_name}.json")

            if max_questions < len(dataset.questions):
                dataset.questions = dataset.questions[:max_questions]
                dataset.total_questions = len(dataset.questions)

            # Run comparison
            comparison_results = runner.run_model_comparison(dataset_name, models)

            # Display results
            display_comparison_results(comparison_results)

        except Exception as e:
            st.error(f"Model comparison failed: {str(e)}")


def display_comparison_results(comparison_results):
    """Display model comparison results"""

    st.success("✅ Model comparison completed!")

    # Comparison table
    st.subheader("📊 Comparison Results")

    comparison_data = []
    for model_name, results in comparison_results.items():
        comparison_data.append(
            {
                "Model": model_name,
                "F1 Score": f"{results.avg_f1_score:.3f}",
                "Exact Match": f"{results.avg_exact_match:.3f}",
                "Execution Success": f"{results.execution_success_rate:.3f}",
                "Generation Time": f"{results.avg_generation_time:.3f}s",
                "Execution Time": f"{results.avg_execution_time:.3f}s",
            }
        )

    st.table(pd.DataFrame(comparison_data))

    # Comparison chart
    st.subheader("📈 Performance Comparison")

    models = list(comparison_results.keys())
    f1_scores = [results.avg_f1_score for results in comparison_results.values()]

    fig = px.bar(
        x=models,
        y=f1_scores,
        title="F1 Score Comparison",
        labels={"x": "Model", "y": "F1 Score"},
    )
    fig.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)


def analytics_tab():
    st.header("📊 Analytics Dashboard")

    runner = get_benchmark_runner()

    # Get benchmark summary
    summary = runner.get_benchmark_summary()

    if "benchmarks" not in summary:
        st.warning("No benchmark data available for analytics.")
        return

    benchmarks = summary["benchmarks"]

    if not benchmarks:
        st.warning("No benchmarks found.")
        return

    # Convert to DataFrame for analysis
    df = pd.DataFrame(benchmarks)
    df["f1_score"] = pd.to_numeric(df["f1_score"])
    df["execution_success_rate"] = pd.to_numeric(df["execution_success_rate"])

    # Performance trends
    st.subheader("📈 Performance Trends")

    if len(df) > 1:
        # F1 Score trend
        fig_f1 = px.line(
            df,
            x=df.index,
            y="f1_score",
            title="F1 Score Trend Over Time",
            labels={"x": "Benchmark Index", "y": "F1 Score"},
        )
        st.plotly_chart(fig_f1, use_container_width=True)

        # Execution success trend
        fig_exec = px.line(
            df,
            x=df.index,
            y="execution_success_rate",
            title="Execution Success Rate Trend",
            labels={"x": "Benchmark Index", "y": "Execution Success Rate"},
        )
        st.plotly_chart(fig_exec, use_container_width=True)

    # Summary statistics
    st.subheader("📊 Summary Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Benchmarks", len(df))
        st.metric("Average F1 Score", f"{df['f1_score'].mean():.3f}")

    with col2:
        st.metric("Best F1 Score", f"{df['f1_score'].max():.3f}")
        st.metric(
            "Average Execution Success", f"{df['execution_success_rate'].mean():.3f}"
        )


if __name__ == "__main__":
    main()
