import unittest
import pandas as pd
from src.support_systems.match_maker.prompt_generation import PromptGeneration

class TestMatchMaker(unittest.TestCase):
    def setUp(self):
        self.prompt_gen = PromptGeneration()
        self.test_data = {
            "StudentID": ["TEST_1"],
            "Extrovert": [1], "Introvert": [4],
            "Sensing": [1], "Intuitive": [4],
            "Thinking": [2], "Feeling": [3],
            "Judging": [1], "Perceiving": [4],
            "Active": [3], "Reflective": [8],
            "Sensing_FSLSM": [2], "Intuitive_FSLSM": [9],
            "Visual": [9], "Verbal": [2],
            "Sequential": [3], "Global": [8],
            "Text_Time": [600]
        }
    
    def test_mbti_scoring(self):
        df = pd.DataFrame(self.test_data)
        df["MBTI_Type"] = df.apply(self.prompt_gen.score_mbti, axis=1)
        self.assertEqual(df["MBTI_Type"].iloc[0], "INFP")
    
    def test_ils_scoring(self):
        df = pd.DataFrame(self.test_data)
        ils_scores = self.prompt_gen.score_ils(df.iloc[0])
        self.assertEqual(ils_scores["Active_Reflective"], -5)
        self.assertEqual(ils_scores["Sensing_Intuitive_ILS"], -7)

if __name__ == "__main__":
    unittest.main()
