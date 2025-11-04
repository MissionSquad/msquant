"""HuggingFace Hub API service for searching models and datasets."""
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
from huggingface_hub import list_models, list_datasets, model_info, dataset_info
from huggingface_hub.hf_api import ModelInfo, DatasetInfo
import logging

logger = logging.getLogger(__name__)


@dataclass
class HFSearchResult:
    """Represents a search result from HuggingFace Hub."""
    id: str
    author: Optional[str]
    description: Optional[str]
    downloads: Optional[int]
    likes: Optional[int]
    tags: List[str]
    last_modified: Optional[str]
    created_at: Optional[str]
    library_name: Optional[str] = None  # For models
    pipeline_tag: Optional[str] = None  # For models

    def get_hub_url(self, repo_type: str) -> str:
        """Get the HuggingFace Hub URL for this item."""
        return f"https://huggingface.co/{repo_type}s/{self.id}"


class HuggingFaceService:
    """Service for interacting with HuggingFace Hub API."""

    def __init__(self):
        """Initialize the HuggingFace service."""
        self._cache: Dict[str, Any] = {}

    def search_models(
        self,
        query: str = "",
        limit: int = 20,
        sort: str = "downloads",
        direction: int = -1
    ) -> List[HFSearchResult]:
        """
        Search for models on HuggingFace Hub.

        Args:
            query: Search query string
            limit: Maximum number of results to return (max 100)
            sort: Property to sort by (downloads, likes, trending, etc.)
            direction: Sort direction (-1 for descending, 1 for ascending)

        Returns:
            List of HFSearchResult objects

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If API call fails
        """
        # Validate inputs
        if not isinstance(query, str):
            raise ValueError(f"query must be a string, got {type(query)}")
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError(f"limit must be an integer between 1 and 100, got {limit}")
        if sort not in ["downloads", "likes", "trending", "author", "id", "created", "modified"]:
            raise ValueError(f"Invalid sort parameter: {sort}")
        if direction not in [-1, 1]:
            raise ValueError(f"direction must be -1 or 1, got {direction}")

        try:
            logger.info(f"Searching models: query={query}, limit={limit}, sort={sort}")

            # Convert direction: -1 stays as -1, 1 becomes None (for ascending)
            hf_direction: Optional[Literal[-1]] = -1 if direction == -1 else None

            # Use huggingface_hub library to search models
            models = list_models(
                search=query if query else None,
                limit=limit,
                sort=sort,
                direction=hf_direction
            )

            results = []
            for model in models:
                try:
                    result = self._model_to_search_result(model)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to process model {getattr(model, 'id', 'unknown')}: {e}")
                    continue

            logger.info(f"Found {len(results)} models")
            return results

        except Exception as e:
            logger.error(f"Failed to search models: {e}")
            raise RuntimeError(f"Failed to search models: {str(e)}") from e

    def search_datasets(
        self,
        query: str = "",
        limit: int = 20,
        sort: str = "downloads",
        direction: int = -1
    ) -> List[HFSearchResult]:
        """
        Search for datasets on HuggingFace Hub.

        Args:
            query: Search query string
            limit: Maximum number of results to return (max 100)
            sort: Property to sort by (downloads, likes, trending, etc.)
            direction: Sort direction (-1 for descending, 1 for ascending)

        Returns:
            List of HFSearchResult objects

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If API call fails
        """
        # Validate inputs
        if not isinstance(query, str):
            raise ValueError(f"query must be a string, got {type(query)}")
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError(f"limit must be an integer between 1 and 100, got {limit}")
        if sort not in ["downloads", "likes", "trending", "author", "id", "created", "modified"]:
            raise ValueError(f"Invalid sort parameter: {sort}")
        if direction not in [-1, 1]:
            raise ValueError(f"direction must be -1 or 1, got {direction}")

        try:
            logger.info(f"Searching datasets: query={query}, limit={limit}, sort={sort}")

            # Convert direction: -1 stays as -1, 1 becomes None (for ascending)
            hf_direction: Optional[Literal[-1]] = -1 if direction == -1 else None

            # Use huggingface_hub library to search datasets
            datasets = list_datasets(
                search=query if query else None,
                limit=limit,
                sort=sort,
                direction=hf_direction
            )

            results = []
            for dataset in datasets:
                try:
                    result = self._dataset_to_search_result(dataset)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to process dataset {getattr(dataset, 'id', 'unknown')}: {e}")
                    continue

            logger.info(f"Found {len(results)} datasets")
            return results

        except Exception as e:
            logger.error(f"Failed to search datasets: {e}")
            raise RuntimeError(f"Failed to search datasets: {str(e)}") from e

    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.

        Args:
            model_id: The model repository ID (e.g., 'meta-llama/Llama-3.1-8B')

        Returns:
            Dictionary containing detailed model information

        Raises:
            ValueError: If model_id is invalid
            RuntimeError: If API call fails
        """
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("model_id must be a non-empty string")

        try:
            logger.info(f"Fetching model details for: {model_id}")
            info = model_info(model_id, files_metadata=False)

            # Extract card data for description
            card_data = getattr(info, 'card_data', None) or getattr(info, 'cardData', None)
            description = ""

            if card_data:
                # Try to get description from card_data
                if hasattr(card_data, 'get'):
                    description = card_data.get('description', '') or card_data.get('model-index', {}).get('results', [{}])[0].get('task', {}).get('name', '')
                elif hasattr(card_data, 'to_dict'):
                    card_dict = card_data.to_dict()
                    description = card_dict.get('description', '')

            # Fallback to checking for description attribute
            if not description:
                description = getattr(info, 'description', '')

            return {
                'id': info.id,
                'author': getattr(info, 'author', None),
                'description': description,
                'downloads': getattr(info, 'downloads', 0),
                'likes': getattr(info, 'likes', 0),
                'tags': getattr(info, 'tags', []),
                'library_name': getattr(info, 'library_name', None),
                'pipeline_tag': getattr(info, 'pipeline_tag', None),
                'last_modified': str(getattr(info, 'lastModified', '')),
                'created_at': str(getattr(info, 'created_at', '')),
                'card_data': card_data,
            }

        except Exception as e:
            logger.error(f"Failed to get model details for {model_id}: {e}")
            raise RuntimeError(f"Failed to get model details: {str(e)}") from e

    def get_dataset_details(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific dataset.

        Args:
            dataset_id: The dataset repository ID (e.g., 'wikitext')

        Returns:
            Dictionary containing detailed dataset information

        Raises:
            ValueError: If dataset_id is invalid
            RuntimeError: If API call fails
        """
        if not isinstance(dataset_id, str) or not dataset_id.strip():
            raise ValueError("dataset_id must be a non-empty string")

        try:
            logger.info(f"Fetching dataset details for: {dataset_id}")
            info = dataset_info(dataset_id, files_metadata=False)

            # Extract card data for description
            card_data = getattr(info, 'card_data', None) or getattr(info, 'cardData', None)
            description = ""

            if card_data:
                # Try to get description from card_data
                if hasattr(card_data, 'get'):
                    description = card_data.get('description', '') or card_data.get('dataset_summary', '')
                elif hasattr(card_data, 'to_dict'):
                    card_dict = card_data.to_dict()
                    description = card_dict.get('description', '') or card_dict.get('dataset_summary', '')

            # Fallback to checking for description attribute
            if not description:
                description = getattr(info, 'description', '')

            return {
                'id': info.id,
                'author': getattr(info, 'author', None),
                'description': description,
                'downloads': getattr(info, 'downloads', 0),
                'likes': getattr(info, 'likes', 0),
                'tags': getattr(info, 'tags', []),
                'last_modified': str(getattr(info, 'lastModified', '')),
                'created_at': str(getattr(info, 'created_at', '')),
                'card_data': card_data,
            }

        except Exception as e:
            logger.error(f"Failed to get dataset details for {dataset_id}: {e}")
            raise RuntimeError(f"Failed to get dataset details: {str(e)}") from e

    def _model_to_search_result(self, model: ModelInfo) -> HFSearchResult:
        """Convert ModelInfo to HFSearchResult."""
        return HFSearchResult(
            id=model.id,
            author=getattr(model, 'author', None),
            description=None,  # Description not available in list results
            downloads=getattr(model, 'downloads', 0),
            likes=getattr(model, 'likes', 0),
            tags=getattr(model, 'tags', []) or [],
            last_modified=str(getattr(model, 'lastModified', '')),
            created_at=str(getattr(model, 'created_at', '')),
            library_name=getattr(model, 'library_name', None),
            pipeline_tag=getattr(model, 'pipeline_tag', None),
        )

    def _dataset_to_search_result(self, dataset: DatasetInfo) -> HFSearchResult:
        """Convert DatasetInfo to HFSearchResult."""
        return HFSearchResult(
            id=dataset.id,
            author=getattr(dataset, 'author', None),
            description=getattr(dataset, 'description', None),
            downloads=getattr(dataset, 'downloads', 0),
            likes=getattr(dataset, 'likes', 0),
            tags=getattr(dataset, 'tags', []) or [],
            last_modified=str(getattr(dataset, 'lastModified', '')),
            created_at=str(getattr(dataset, 'created_at', '')),
        )
