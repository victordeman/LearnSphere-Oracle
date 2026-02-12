import pandas as pd
import numpy as np
from .prompt_generator import PromptGenerator
from .question_classifier import QuestionClassifier  # New import

class PromptGeneration:
    def __init__(self):
        self.prompt_generator = PromptGenerator()
        self.question_classifier = QuestionClassifier()  # New: For raw question handling

    # Existing methods...

    def integrate_sn(self, mbti_type, ils_sn_score):
        mbti_sn = mbti_type[1]
        abs_score = abs(ils_sn_score)
        if (mbti_sn == "S" and ils_sn_score > 0) or (mbti_sn == "N" and ils_sn_score < 0):
            if abs_score >= 9:
                strength = "strongly"
            elif abs_score >= 5:
                strength = "moderately"
            else:
                strength = "mildly"
            return f"{strength} {mbti_sn}-oriented"
        elif abs_score < 3:
            return "balanced S/N preference"  # Refined: Near-zero is balanced
        else:
            leaning = "S" if ils_sn_score > 0 else "N"
            return f"mixed but leaning {leaning}"  # Refined: Handle misalignments
        return "mixed S/N preference"  # Fallback

    def process_responses(self, survey_data, raw_questions=None, raw_answers=None):
        df = pd.DataFrame(survey_data)
        if raw_questions and raw_answers:  # New: Handle raw input if provided
            raw_scores = self.question_classifier.score_from_answers(raw_questions, raw_answers)
            # Merge raw scores into df (e.g., update columns like Sensing/Intuitive)
            for dim, score in raw_scores.items():
                if dim == "Sensing_Intuitive":
                    df["Sensing"] = score / 2  # Example aggregation; adjust
                    df["Intuitive"] = score / 2
                # Extend for other dims
        df = df[~df[["Active", "Reflective", "Sensing_FSLSM", "Intuitive_FSLSM", "Visual", "Verbal", "Sequential", "Global"]].eq(11).any(axis=1)]
        df = self.augment_data(df)
        df["MBTI_Type"] = df.apply(self.score_mbti, axis=1)
        ils_scores = df.apply(self.score_ils, axis=1)
        df = pd.concat([df, pd.DataFrame(ils_scores.to_list(), index=df.index)], axis=1)
        df["SN_Integration"] = df.apply(lambda row: self.integrate_sn(row["MBTI_Type"], row["Sensing_Intuitive_ILS"]), axis=1)
        prompts = [{"StudentID": row["StudentID"], "Prompt": self.prompt_generator.generate_prompt(row["MBTI_Type"], {
            "Active_Reflective": row["Active_Reflective"],
            "Sensing_Intuitive_ILS": row["Sensing_Intuitive_ILS"],
            "Visual_Verbal": row["Visual_Verbal"],
            "Sequential_Global": row["Sequential_Global"]
        }, row["SN_Integration"])} for _, row in df.iterrows()]
        return df, prompts
