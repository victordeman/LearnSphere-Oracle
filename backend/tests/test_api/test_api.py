from fastapi.testclient import TestClient
from src.main import app
import unittest
from unittest.mock import MagicMock, patch

class TestMatchAPI(unittest.TestCase):
    def setUp(self):
        pass

    @patch("src.support_systems.match_maker.image_pipeline.QdrantClient")
    def test_get_matches(self, mock_qdrant_class):
        # Setup mock
        mock_client = mock_qdrant_class.return_value
        
        mock_hit_similar = MagicMock()
        mock_hit_similar.payload = {"student_id": "STUDENT_2"}
        
        mock_hit_comp = MagicMock()
        mock_hit_comp.payload = {"student_id": "STUDENT_2"}

        mock_client.search.side_effect = [
            [mock_hit_similar], [mock_hit_comp], 
            [mock_hit_similar], [mock_hit_comp]
        ]

        # Patch the instance in the app
        with patch("src.main.image_pipeline.qdrant_client", mock_client):
            client = TestClient(app)
            test_data = {
                "survey_data": [
                    {
                        "StudentID": "STUDENT_1",
                        "Extrovert": 8, "Introvert": 1,
                        "Sensing": 7, "Intuitive": 2,
                        "Thinking": 6, "Feeling": 3,
                        "Judging": 9, "Perceiving": 0,
                        "Active": 10, "Reflective": 1,
                        "Sensing_FSLSM": 9, "Intuitive_FSLSM": 2,
                        "Visual": 8, "Verbal": 3,
                        "Sequential": 7, "Global": 4,
                        "Text_Time": 500
                    },
                    {
                        "StudentID": "STUDENT_2",
                        "Extrovert": 2, "Introvert": 7,
                        "Sensing": 1, "Intuitive": 8,
                        "Thinking": 3, "Feeling": 6,
                        "Judging": 0, "Perceiving": 9,
                        "Active": 1, "Reflective": 10,
                        "Sensing_FSLSM": 2, "Intuitive_FSLSM": 9,
                        "Visual": 3, "Verbal": 8,
                        "Sequential": 4, "Global": 7,
                        "Text_Time": 600
                    }
                ]
            }
            response = client.post("/match", json=test_data)
            if response.status_code != 200:
                print(f"Error detail: {response.json()}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("recommendations", response.json())
            self.assertIn("STUDENT_1", response.json()["recommendations"])

if __name__ == "__main__":
    unittest.main()
