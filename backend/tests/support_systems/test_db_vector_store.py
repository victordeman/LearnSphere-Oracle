import unittest
from unittest.mock import MagicMock, patch
from src.scripts.init_vector_store import init_qdrant

class TestVectorStoreInit(unittest.TestCase):
    @patch("src.scripts.init_vector_store.QdrantClient")
    def test_init_qdrant(self, mock_client):
        # Call the function
        init_qdrant()

        # Verify client was initialized with correct parameters
        mock_client.assert_called_with(host="localhost", port=6333)

        # Verify recreate_collection was called with correct parameters
        mock_client.return_value.recreate_collection.assert_called_once()
        args, kwargs = mock_client.return_value.recreate_collection.call_args
        self.assertEqual(kwargs["collection_name"], "student_profiles")
        self.assertEqual(kwargs["vectors_config"].size, 8)

if __name__ == "__main__":
    unittest.main()
