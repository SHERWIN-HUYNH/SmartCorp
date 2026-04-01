import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.qdrant_api import QdrantAPI
from app.schemas.qdrant import Point, Vector, SparseVector, Payload, HybridSearchRequest, DeletePointsRequest


class TestQdrantAPI:
    """Unit tests for QdrantAPI class."""

    @pytest.fixture
    def api_client(self):
        """Create QdrantAPI instance."""
        return QdrantAPI(host="http://localhost:6333", collection="test_collection")

    def test_init(self, api_client):
        """Test QdrantAPI initialization."""
        assert api_client.host == "http://localhost:6333"
        assert api_client.collection == "test_collection"

    def test_create_collection(self, api_client):
        """Test create_collection method."""
        with patch('app.core.qdrant_api.requests.put') as mock_put:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_put.return_value = mock_response

            result = api_client.create_collection(vector_size=128)

            mock_put.assert_called_once()
            call_args = mock_put.call_args
            assert call_args[0][0] == "http://localhost:6333/collections/test_collection"
            payload = call_args[1]['json']
            assert payload['vectors']['dense']['size'] == 128
            assert result == {"status": "ok"}

    def test_delete_collection(self, api_client):
        """Test delete_collection method."""
        with patch('app.core.qdrant_api.requests.delete') as mock_delete:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_delete.return_value = mock_response

            result = api_client.delete_collection()

            mock_delete.assert_called_once_with("http://localhost:6333/collections/test_collection")
            assert result == {"status": "ok"}

    def test_get_collection_info(self, api_client):
        """Test get_collection_info method."""
        with patch('app.core.qdrant_api.requests.get') as mock_get:
            mock_info = {"status": "ok", "result": {"vectors_count": 100}}
            mock_response = Mock()
            mock_response.json.return_value = mock_info
            mock_get.return_value = mock_response

            result = api_client.get_collection_info()

            mock_get.assert_called_once_with("http://localhost:6333/collections/test_collection")
            assert result == mock_info

    def test_upsert_points(self, api_client):
        """Test upsert_points method."""
        with patch('app.core.qdrant_api.requests.put') as mock_put:
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

            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_put.return_value = mock_response

            result = api_client.upsert_points(points)

            mock_put.assert_called_once()
            assert result == {"status": "ok"}

    def test_delete_points(self, api_client):
        """Test delete_points method."""
        with patch('app.core.qdrant_api.requests.post') as mock_post:
            delete_request = DeletePointsRequest(ids=["id1", "id2"])

            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_post.return_value = mock_response

            result = api_client.delete_points(delete_request)

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:6333/collections/test_collection/points/delete"
            assert result == {"status": "ok"}

    def test_count_points(self, api_client):
        """Test count_points method."""
        with patch('app.core.qdrant_api.requests.post') as mock_post:
            mock_count = {"result": {"count": 42}}
            mock_response = Mock()
            mock_response.json.return_value = mock_count
            mock_post.return_value = mock_response

            result = api_client.count_points()

            mock_post.assert_called_once_with(
                "http://localhost:6333/collections/test_collection/points/count",
                json={}
            )
            assert result == mock_count

    def test_hybrid_search(self, api_client):
        """Test hybrid_search method."""
        with patch('app.core.qdrant_api.requests.post') as mock_post:
            request = HybridSearchRequest(
                dense_vector=[0.1, 0.2, 0.3],
                sparse_indices=[0, 1],
                sparse_values=[0.5, 0.6],
                limit=5
            )

            mock_search_result = {
                "result": {
                    "points": [
                        {
                            "id": "point1",
                            "score": 0.9,
                            "payload": {"content": "test"}
                        }
                    ]
                },
                "status": "ok"
            }

            mock_response = Mock()
            mock_response.json.return_value = mock_search_result
            mock_post.return_value = mock_response

            result = api_client.hybrid_search(request)

            mock_post.assert_called_once()
            assert result == mock_search_result

    def test_hybrid_search_with_filter(self, api_client):
        """Test hybrid_search with role_allowed filter."""
        with patch('app.core.qdrant_api.requests.post') as mock_post:
            request = HybridSearchRequest(
                dense_vector=[0.1, 0.2, 0.3],
                sparse_indices=[0, 1],
                sparse_values=[0.5, 0.6],
                limit=5,
                role_allowed=["admin"]
            )

            mock_response = Mock()
            mock_response.json.return_value = {"result": {"points": []}, "status": "ok"}
            mock_post.return_value = mock_response

            result = api_client.hybrid_search(request)

            # Verify the call was made
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert "filter" in payload
            assert payload["filter"]["must"][0]["key"] == "role_allowed"
            assert payload["filter"]["must"][0]["match"]["any"] == ["admin"]