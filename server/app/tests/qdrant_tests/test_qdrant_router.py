import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os

# Set environment variables before importing
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['JWT_ACCESS_SECRET'] = 'test_access_secret'
os.environ['JWT_REFRESH_SECRET'] = 'test_refresh_secret'

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.routers.qdrant import router
from app.schemas.qdrant import Point, Vector, SparseVector, Payload, HybridSearchRequest, DeletePointsRequest
from app.services.qdrant_service import get_qdrant_service


@pytest.fixture
def mock_service():
    """Create a mock QdrantService.
    
    All methods return success responses by default to ensure tests
    verify the endpoint logic without depending on actual service implementation.
    """
    service = MagicMock()
    # Set default return values for all methods
    service.create_collection.return_value = {"status": "ok"}
    service.get_collection_info.return_value = {"status": "ok", "result": {"vectors_count": 0}}
    service.delete_collection.return_value = {"status": "ok"}
    service.create_snapshot.return_value = {"status": "ok"}
    service.upsert_points.return_value = {"status": "ok"}
    service.delete_points.return_value = {"status": "ok"}
    service.count_points.return_value = {"result": {"count": 0}}
    service.hybrid_search.return_value = {"result": {"points": []}, "status": "ok"}
    service.scroll.return_value = {"result": {"points": []}, "status": "ok"}
    service.recommend.return_value = {"result": {"points": []}, "status": "ok"}
    service.create_payload_index.return_value = {"status": "ok"}
    return service


@pytest.fixture
def client(mock_service):
    """Create TestClient with dependency overrides for mocking.
    
    Uses FastAPI's dependency_overrides to replace get_qdrant_service
    with our mock. This ensures all endpoints use the mocked service.
    
    All service methods are mocked, so these tests verify:
    - Correct HTTP request/response handling
    - Proper parameter passing to backend services
    - Correct status codes and response formats
    
    Destructive operations like delete_collection are MOCKED and do NOT
    affect any real collections or data. This ensures tests are isolated
    and safe to run multiple times.
    """
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)

    # Override the dependency to use our mock service
    app.dependency_overrides[get_qdrant_service] = lambda: mock_service
    
    # Store mock_service for tests to access
    app.state.mock_service = mock_service

    client_instance = TestClient(app)
    
    yield client_instance
    
    # Cleanup: remove the override after the test
    app.dependency_overrides.clear()


class TestQdrantRouter:
    """Unit tests for Qdrant router endpoints.
    
    IMPORTANT: All service methods are mocked, so these tests verify:
    - Correct HTTP request/response handling
    - Proper parameter passing to backend services
    - Correct status codes and response formats
    
    Destructive operations like delete_collection are MOCKED and do NOT
    affect any real collections or data. This ensures tests are isolated
    and safe to run multiple times.
    """

    # ============== COLLECTION MANAGEMENT ENDPOINTS ==============

    def test_create_collection_success(self, client):
        """Test POST /qdrant/collection success."""
        mock_service = client.app.state.mock_service
        mock_service.create_collection.return_value = {"status": "ok"}

        response = client.post("/qdrant/collection")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_service.create_collection.assert_called_once()

    def test_create_collection_error(self, client):
        """Test POST /qdrant/collection with error."""
        mock_service = client.app.state.mock_service
        mock_service.create_collection.side_effect = Exception("Connection failed")

        response = client.post("/qdrant/collection")

        assert response.status_code == 500
        assert "Connection failed" in response.json()["detail"]

    def test_get_collection(self, client):
        """Test GET /qdrant/collection."""
        mock_service = client.app.state.mock_service
        mock_info = {"status": "ok", "result": {"vectors_count": 100}}
        mock_service.get_collection_info.return_value = mock_info

        response = client.get("/qdrant/collection")

        assert response.status_code == 200
        assert response.json() == mock_info
        mock_service.get_collection_info.assert_called_once()

    def test_delete_collection_mocked(self, client):
        """Test DELETE /qdrant/collection with mocked service.
        
        NOTE: This test uses a MOCKED service, so no actual collection is deleted.
        The mock ensures the endpoint correctly passes the delete request to the
        service layer. No real collections are affected by this test.
        """
        mock_service = client.app.state.mock_service
        mock_service.delete_collection.return_value = {"status": "ok"}

        response = client.delete("/qdrant/collection")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_service.delete_collection.assert_called_once()

    def test_snapshot(self, client):
        """Test POST /qdrant/snapshot."""
        mock_service = client.app.state.mock_service
        mock_service.create_snapshot.return_value = {"status": "ok"}

        response = client.post("/qdrant/snapshot")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_service.create_snapshot.assert_called_once()

    # ============== POINT MANAGEMENT ENDPOINTS ==============

    def test_upsert_points(self, client):
        """Test POST /qdrant/points."""
        mock_service = client.app.state.mock_service
        mock_service.upsert_points.return_value = {"status": "ok"}

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

        response = client.post("/qdrant/points", json=[point.model_dump() for point in points])

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_service.upsert_points.assert_called_once_with(points)

    def test_delete_points(self, client):
        """Test DELETE /qdrant/points.
        
        NOTE: This test uses a MOCKED service, so no actual points are deleted.
        """
        import json
        mock_service = client.app.state.mock_service
        mock_service.delete_points.return_value = {"status": "ok"}

        delete_request = DeletePointsRequest(ids=["id1", "id2"])

        response = client.request(
            "DELETE",
            "/qdrant/points",
            headers={"Content-Type": "application/json"},
            content=delete_request.model_dump_json().encode()
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_service.delete_points.assert_called_once_with(["id1", "id2"])

    def test_count_points(self, client):
        """Test GET /qdrant/points/count."""
        mock_service = client.app.state.mock_service
        mock_count = {"result": {"count": 42}}
        mock_service.count_points.return_value = mock_count

        response = client.get("/qdrant/points/count")

        assert response.status_code == 200
        assert response.json() == mock_count
        mock_service.count_points.assert_called_once()

    # ============== SEARCH ENDPOINTS ==============

    def test_hybrid_search(self, client):
        """Test POST /qdrant/search."""
        mock_service = client.app.state.mock_service
        mock_result = {"result": {"points": []}, "status": "ok"}
        mock_service.hybrid_search.return_value = mock_result

        search_request = HybridSearchRequest(
            dense_vector=[0.1, 0.2, 0.3],
            sparse_indices=[0, 1],
            sparse_values=[0.5, 0.6],
            limit=5
        )

        response = client.post("/qdrant/search", json=search_request.model_dump())

        assert response.status_code == 200
        assert response.json() == mock_result
        mock_service.hybrid_search.assert_called_once_with(
            dense_vector=[0.1, 0.2, 0.3],
            sparse_indices=[0, 1],
            sparse_values=[0.5, 0.6],
            dense_limit=20,
            sparse_limit=20,
            limit=5,
            role_allowed=None
        )

    def test_hybrid_search_with_filter(self, client):
        """Test POST /qdrant/search with role_allowed filter."""
        mock_service = client.app.state.mock_service
        mock_result = {"result": {"points": []}, "status": "ok"}
        mock_service.hybrid_search.return_value = mock_result

        search_request = HybridSearchRequest(
            dense_vector=[0.1, 0.2, 0.3],
            sparse_indices=[0, 1],
            sparse_values=[0.5, 0.6],
            limit=5,
            role_allowed=["admin"]
        )

        response = client.post("/qdrant/search", json=search_request.model_dump())

        assert response.status_code == 200
        mock_service.hybrid_search.assert_called_once_with(
            dense_vector=[0.1, 0.2, 0.3],
            sparse_indices=[0, 1],
            sparse_values=[0.5, 0.6],
            dense_limit=20,
            sparse_limit=20,
            limit=5,
            role_allowed=["admin"]
        )

    def test_scroll(self, client):
        """Test POST /qdrant/scroll."""
        mock_service = client.app.state.mock_service
        mock_result = {"result": {"points": []}, "status": "ok"}
        mock_service.scroll.return_value = mock_result

        scroll_request = {"filter_query": {"must": [{"key": "role_allowed", "match": {"any": ["admin"]}}]}, "limit": 10}

        response = client.post("/qdrant/scroll", json=scroll_request)

        assert response.status_code == 200
        assert response.json() == mock_result
        mock_service.scroll.assert_called_once_with(
            {"must": [{"key": "role_allowed", "match": {"any": ["admin"]}}]}, 10
        )

    def test_recommend(self, client):
        """Test POST /qdrant/recommend."""
        mock_service = client.app.state.mock_service
        mock_result = {"result": {"points": []}, "status": "ok"}
        mock_service.recommend.return_value = mock_result

        recommend_request = {"positive_ids": ["id1", "id2"], "limit": 5}

        response = client.post("/qdrant/recommend", json=recommend_request)

        assert response.status_code == 200
        assert response.json() == mock_result
        mock_service.recommend.assert_called_once_with(["id1", "id2"], 5)

    # ============== INDEX MANAGEMENT ENDPOINTS ==============

    def test_create_index(self, client):
        """Test POST /qdrant/payload/index."""
        mock_service = client.app.state.mock_service
        mock_service.create_payload_index.return_value = {"status": "ok"}

        response = client.post("/qdrant/payload/index?field_name=role_allowed&field_type=keyword")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_service.create_payload_index.assert_called_once_with("role_allowed", "keyword")