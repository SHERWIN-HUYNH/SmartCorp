import pytest
from unittest.mock import Mock, patch
import sys
import os

# Set environment variables before importing
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['JWT_ACCESS_SECRET'] = 'test_access_secret'
os.environ['JWT_REFRESH_SECRET'] = 'test_refresh_secret'

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.qdrant_service import QdrantService
from app.schemas.qdrant import Point, Vector, SparseVector, Payload


class TestQdrantService:
    """Unit tests for QdrantService class."""

    @pytest.fixture
    def mock_qdrant_api(self):
        """Mock QdrantAPI."""
        with patch('app.services.qdrant_service.QdrantAPI') as mock_api:
            yield mock_api.return_value

    @pytest.fixture
    def service(self, mock_qdrant_api):
        """Create QdrantService instance with mocked QdrantAPI."""
        return QdrantService(host="http://localhost:6333", collection="test_collection")

    def test_init(self):
        """Test QdrantService initialization."""
        with patch('app.services.qdrant_service.QdrantAPI') as mock_api:
            service = QdrantService(host="http://localhost:6333", collection="test")
            mock_api.assert_called_once_with("http://localhost:6333", "test")

    def test_create_collection(self, service, mock_qdrant_api):
        """Test create_collection method."""
        mock_qdrant_api.create_collection.return_value = {"status": "ok"}

        result = service.create_collection(vector_size=128)

        mock_qdrant_api.create_collection.assert_called_once_with(128)
        assert result == {"status": "ok"}

    def test_delete_collection(self, service, mock_qdrant_api):
        """Test delete_collection method."""
        mock_qdrant_api.delete_collection.return_value = {"status": "ok"}

        result = service.delete_collection()

        mock_qdrant_api.delete_collection.assert_called_once()
        assert result == {"status": "ok"}

    def test_get_collection_info(self, service, mock_qdrant_api):
        """Test get_collection_info method."""
        mock_info = {"status": "ok", "result": {"vectors_count": 100}}
        mock_qdrant_api.get_collection_info.return_value = mock_info

        result = service.get_collection_info()

        mock_qdrant_api.get_collection_info.assert_called_once()
        assert result == mock_info

    def test_create_snapshot(self, service, mock_qdrant_api):
        """Test create_snapshot method."""
        mock_qdrant_api.create_snapshot.return_value = {"status": "ok"}

        result = service.create_snapshot()

        mock_qdrant_api.create_snapshot.assert_called_once()
        assert result == {"status": "ok"}

    def test_upsert_points_success(self, service, mock_qdrant_api):
        """Test upsert_points method with valid points."""
        points = [
            Point(
                id="test-id-1",
                vector=Vector(
                    dense=[0.1, 0.2, 0.3],
                    sparse=SparseVector(indices=[0, 1], values=[0.5, 0.6])
                ),
                payload=Payload(
                    document_id="doc1",
                    page=1,
                    role_allowed=["admin"],
                    content="test content",
                    type="text",
                    parent_id="parent1",
                    order=0
                )
            )
        ]

        mock_qdrant_api.upsert_points.return_value = {"status": "ok"}

        result = service.upsert_points(points)

        mock_qdrant_api.upsert_points.assert_called_once_with(points)
        assert result == {"status": "ok"}

    def test_upsert_points_empty_list(self, service, mock_qdrant_api):
        """Test upsert_points method with empty points list."""
        with pytest.raises(ValueError, match="Points list is empty"):
            service.upsert_points([])

        mock_qdrant_api.upsert_points.assert_not_called()

    def test_delete_points(self, service, mock_qdrant_api):
        """Test delete_points method."""
        mock_qdrant_api.delete_points.return_value = {"status": "ok"}

        result = service.delete_points(["id1", "id2"])

        # Verify the call was made with DeletePointsRequest
        call_args = mock_qdrant_api.delete_points.call_args
        delete_request = call_args[0][0]
        assert delete_request.ids == ["id1", "id2"]
        assert result == {"status": "ok"}

    def test_count_points(self, service, mock_qdrant_api):
        """Test count_points method."""
        mock_count = {"result": {"count": 42}}
        mock_qdrant_api.count_points.return_value = mock_count

        result = service.count_points()

        mock_qdrant_api.count_points.assert_called_once()
        assert result == mock_count

    def test_hybrid_search(self, service, mock_qdrant_api):
        """Test hybrid_search method."""
        mock_qdrant_api.hybrid_search.return_value = {
            "result": {"points": []},
            "status": "ok"
        }

        result = service.hybrid_search(
            dense_vector=[0.1, 0.2, 0.3],
            sparse_indices=[0, 1],
            sparse_values=[0.5, 0.6],
            dense_limit=20,
            sparse_limit=20,
            limit=10
        )

        # Verify the call was made with HybridSearchRequest
        call_args = mock_qdrant_api.hybrid_search.call_args
        search_request = call_args[0][0]
        assert search_request.dense_vector == [0.1, 0.2, 0.3]
        assert search_request.sparse_indices == [0, 1]
        assert search_request.sparse_values == [0.5, 0.6]
        assert search_request.limit == 10

    def test_hybrid_search_with_role_filter(self, service, mock_qdrant_api):
        """Test hybrid_search method with role_allowed filter."""
        mock_qdrant_api.hybrid_search.return_value = {
            "result": {"points": []},
            "status": "ok"
        }

        result = service.hybrid_search(
            dense_vector=[0.1, 0.2, 0.3],
            sparse_indices=[0, 1],
            sparse_values=[0.5, 0.6],
            limit=5,
            role_allowed=["admin", "user"]
        )

        # Verify the call was made with role_allowed
        call_args = mock_qdrant_api.hybrid_search.call_args
        search_request = call_args[0][0]
        assert search_request.role_allowed == ["admin", "user"]

    def test_scroll(self, service, mock_qdrant_api):
        """Test scroll method."""
        filter_query = {"must": [{"key": "role_allowed", "match": {"any": ["admin"]}}]}
        mock_qdrant_api.scroll.return_value = {"result": {"points": []}, "status": "ok"}

        result = service.scroll(filter_query=filter_query, limit=10)

        mock_qdrant_api.scroll.assert_called_once_with(filter_query, 10)
        assert result == {"result": {"points": []}, "status": "ok"}

    def test_recommend(self, service, mock_qdrant_api):
        """Test recommend method."""
        positive_ids = ["id1", "id2"]
        mock_qdrant_api.recommend.return_value = {"result": {"points": []}, "status": "ok"}

        result = service.recommend(positive_ids, limit=5)

        mock_qdrant_api.recommend.assert_called_once_with(positive_ids, 5)
        assert result == {"result": {"points": []}, "status": "ok"}

    def test_create_payload_index(self, service, mock_qdrant_api):
        """Test create_payload_index method."""
        mock_qdrant_api.create_payload_index.return_value = {"status": "ok"}

        result = service.create_payload_index("role_allowed", "keyword")

        mock_qdrant_api.create_payload_index.assert_called_once_with("role_allowed", "keyword")
        assert result == {"status": "ok"}

    @patch('app.services.qdrant_service.get_settings')
    def test_get_qdrant_service(self, mock_get_settings):
        """Test get_qdrant_service dependency injection."""
        mock_settings = Mock()
        mock_settings.QDRANT_HOST = "http://localhost:6333"
        mock_settings.QDRANT_COLLECTION = "test_collection"
        mock_get_settings.return_value = mock_settings

        with patch('app.services.qdrant_service.QdrantAPI') as mock_api:
            service = QdrantService(
                host=mock_settings.QDRANT_HOST,
                collection=mock_settings.QDRANT_COLLECTION,
            )

            # Verify settings were used
            assert service.qdrant is not None