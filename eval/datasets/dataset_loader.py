"""
Dataset loader for evaluation datasets

Supports loading various Text-to-SQL datasets including:
- Custom JSON datasets
- Spider dataset format
- WikiSQL dataset format
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Question:
    """Container for a single evaluation question"""

    id: str
    question: str
    sql: str
    expected_result_count: Optional[int] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    schema: Optional[str] = None


@dataclass
class Dataset:
    """Container for evaluation dataset"""

    name: str
    version: str
    description: str
    schema: Dict[str, Any]
    questions: List[Question]
    total_questions: int


class DatasetLoader:
    """Load and manage evaluation datasets"""

    def __init__(self, datasets_dir: str = "eval/datasets"):
        self.datasets_dir = Path(datasets_dir)

    def load_custom_dataset(self, dataset_file: str) -> Dataset:
        """Load custom JSON dataset"""
        dataset_path = self.datasets_dir / "custom" / dataset_file

        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert questions to Question objects
        questions = []
        for q_data in data.get("questions", []):
            question = Question(
                id=q_data.get("id", ""),
                question=q_data.get("question", ""),
                sql=q_data.get("sql", ""),
                expected_result_count=q_data.get("expected_result_count"),
                difficulty=q_data.get("difficulty"),
                tags=q_data.get("tags", []),
                schema=q_data.get("schema"),
            )
            questions.append(question)

        return Dataset(
            name=data.get("dataset_name", "Unknown"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            schema=data.get("schema", {}),
            questions=questions,
            total_questions=len(questions),
        )

    def load_spider_dataset(self, dataset_dir: str) -> Dataset:
        """Load Spider dataset format"""
        # This is a placeholder for Spider dataset loading
        # In a real implementation, you would parse Spider's specific format
        raise NotImplementedError("Spider dataset loading not yet implemented")

    def load_wikisql_dataset(self, dataset_file: str) -> Dataset:
        """Load WikiSQL dataset format"""
        # This is a placeholder for WikiSQL dataset loading
        # In a real implementation, you would parse WikiSQL's specific format
        raise NotImplementedError("WikiSQL dataset loading not yet implemented")

    def list_available_datasets(self) -> Dict[str, List[str]]:
        """List all available datasets"""
        datasets = {}

        # Check custom datasets
        custom_dir = self.datasets_dir / "custom"
        if custom_dir.exists():
            custom_files = [f.name for f in custom_dir.glob("*.json")]
            datasets["custom"] = custom_files

        # Check Spider datasets
        spider_dir = self.datasets_dir / "spider"
        if spider_dir.exists():
            spider_files = [f.name for f in spider_dir.glob("*.json")]
            datasets["spider"] = spider_files

        # Check WikiSQL datasets
        wikisql_dir = self.datasets_dir / "wikisql"
        if wikisql_dir.exists():
            wikisql_files = [f.name for f in wikisql_dir.glob("*.json")]
            datasets["wikisql"] = wikisql_files

        return datasets

    def filter_dataset_by_difficulty(
        self, dataset: Dataset, difficulty: str
    ) -> Dataset:
        """Filter dataset by difficulty level"""
        filtered_questions = [
            q for q in dataset.questions if q.difficulty == difficulty
        ]

        return Dataset(
            name=f"{dataset.name} ({difficulty})",
            version=dataset.version,
            description=f"{dataset.description} - Filtered by {difficulty} difficulty",
            schema=dataset.schema,
            questions=filtered_questions,
            total_questions=len(filtered_questions),
        )

    def filter_dataset_by_tags(self, dataset: Dataset, tags: List[str]) -> Dataset:
        """Filter dataset by tags"""
        filtered_questions = [
            q
            for q in dataset.questions
            if q.tags and any(tag in q.tags for tag in tags)
        ]

        return Dataset(
            name=f"{dataset.name} ({', '.join(tags)})",
            version=dataset.version,
            description=f"{dataset.description} - Filtered by tags: {', '.join(tags)}",
            schema=dataset.schema,
            questions=filtered_questions,
            total_questions=len(filtered_questions),
        )

    def get_dataset_statistics(self, dataset: Dataset) -> Dict[str, Any]:
        """Get statistics about the dataset"""
        stats = {
            "total_questions": dataset.total_questions,
            "difficulty_distribution": {},
            "tag_distribution": {},
            "avg_question_length": 0,
            "avg_sql_length": 0,
        }

        if not dataset.questions:
            return stats

        # Calculate difficulty distribution
        for question in dataset.questions:
            if question.difficulty:
                stats["difficulty_distribution"][question.difficulty] = (
                    stats["difficulty_distribution"].get(question.difficulty, 0) + 1
                )

        # Calculate tag distribution
        for question in dataset.questions:
            if question.tags:
                for tag in question.tags:
                    stats["tag_distribution"][tag] = (
                        stats["tag_distribution"].get(tag, 0) + 1
                    )

        # Calculate average lengths
        question_lengths = [len(q.question) for q in dataset.questions]
        sql_lengths = [len(q.sql) for q in dataset.questions]

        stats["avg_question_length"] = sum(question_lengths) / len(question_lengths)
        stats["avg_sql_length"] = sum(sql_lengths) / len(sql_lengths)

        return stats

    def save_dataset(
        self, dataset: Dataset, filename: str, dataset_type: str = "custom"
    ):
        """Save dataset to file"""
        output_dir = self.datasets_dir / dataset_type
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename

        # Convert Dataset object to dictionary
        data = {
            "dataset_name": dataset.name,
            "version": dataset.version,
            "description": dataset.description,
            "schema": dataset.schema,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "sql": q.sql,
                    "expected_result_count": q.expected_result_count,
                    "difficulty": q.difficulty,
                    "tags": q.tags,
                    "schema": q.schema,
                }
                for q in dataset.questions
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Dataset saved to: {output_path}")
