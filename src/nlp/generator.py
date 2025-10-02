import torch
import time
from typing import Optional, Dict, Any
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from src.nlp.prompt import build_prompt
from src.nlp.fewshots import FEWSHOTS
from src.utils.logger import get_logger, log_performance
from config.config import config

logger = get_logger("text2sql.generator")


class T2SQLGenerator:
    """Optimized Text-to-SQL Generator with caching and performance monitoring"""

    _instance: Optional["T2SQLGenerator"] = None
    _model_cache: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        """Singleton pattern for model caching"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        schema_txt: str,
        fewshots: str = FEWSHOTS,
        model_name: str = None,
        enable_caching: bool = None,
    ):
        if hasattr(self, "_initialized"):
            return

        self.schema_txt = schema_txt
        self.fewshots = fewshots
        self.model_name = model_name or config.MODEL_NAME
        self.enable_caching = (
            enable_caching
            if enable_caching is not None
            else config.ENABLE_MODEL_CACHING
        )

        logger.info(f"Initializing T2SQLGenerator with model: {self.model_name}")
        self._load_model()
        self._initialized = True

    @log_performance
    def _load_model(self):
        """Load model and tokenizer with caching"""
        cache_key = f"{self.model_name}_{self.enable_caching}"

        if self.enable_caching and cache_key in self._model_cache:
            logger.info("Loading model from cache")
            cached_data = self._model_cache[cache_key]
            self.tok = cached_data["tokenizer"]
            self.model = cached_data["model"]
        else:
            logger.info("Loading model from HuggingFace")
            try:
                # Load tokenizer
                self.tok = AutoTokenizer.from_pretrained(
                    self.model_name, cache_dir=config.MODEL_CACHE_DIR
                )

                # Load model with optimizations
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    cache_dir=config.MODEL_CACHE_DIR,
                    torch_dtype=torch.float16
                    if torch.cuda.is_available()
                    else torch.float32,
                    low_cpu_mem_usage=True,
                )

                # Set model to evaluation mode
                self.model.eval()

                # Cache the model if enabled
                if self.enable_caching:
                    self._model_cache[cache_key] = {
                        "tokenizer": self.tok,
                        "model": self.model,
                    }
                    logger.info("Model cached for future use")

                logger.info("Model loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load model: {str(e)}")
                raise

    @log_performance
    def generate(
        self,
        question: str,
        max_new_tokens: int = None,
        num_beams: int = None,
        timeout: int = None,
    ) -> str:
        """
        Generate SQL from natural language question

        Args:
            question: Natural language question
            max_new_tokens: Maximum tokens to generate
            num_beams: Number of beams for generation
            timeout: Generation timeout in seconds

        Returns:
            Generated SQL query
        """
        max_new_tokens = max_new_tokens or config.MAX_TOKENS
        num_beams = num_beams or config.NUM_BEAMS
        timeout = timeout or config.QUERY_TIMEOUT

        logger.info(f"Generating SQL for question: '{question[:50]}...'")

        try:
            # Build prompt
            prompt = build_prompt(self.schema_txt, question, self.fewshots)

            # Tokenize with proper length limits
            ids = self.tok(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=config.MAX_INPUT_LENGTH,
            ).input_ids

            # Generate with timeout
            start_time = time.time()
            with torch.inference_mode():
                out = self.model.generate(
                    ids,
                    max_new_tokens=max_new_tokens,
                    num_beams=num_beams,
                    do_sample=False,  # Deterministic output
                    early_stopping=True,
                    pad_token_id=self.tok.eos_token_id,
                )

            generation_time = time.time() - start_time

            # Decode result
            sql = self.tok.decode(out[0], skip_special_tokens=True).strip()

            logger.info(f"SQL generated in {generation_time:.3f}s: {sql[:100]}...")

            # Check timeout
            if generation_time > timeout:
                logger.warning(
                    f"Generation took {generation_time:.3f}s (timeout: {timeout}s)"
                )

            return sql

        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_type": type(self.model).__name__,
            "tokenizer_type": type(self.tok).__name__,
            "vocab_size": self.tok.vocab_size,
            "max_input_length": config.MAX_INPUT_LENGTH,
            "max_output_tokens": config.MAX_TOKENS,
            "caching_enabled": self.enable_caching,
            "cuda_available": torch.cuda.is_available(),
            "model_dtype": str(self.model.dtype)
            if hasattr(self.model, "dtype")
            else "unknown",
        }

    @classmethod
    def clear_cache(cls):
        """Clear model cache"""
        cls._model_cache.clear()
        cls._instance = None
        logger.info("Model cache cleared")
