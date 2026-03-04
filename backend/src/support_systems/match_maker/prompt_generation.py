import pandas as pd
import numpy as np
from .prompt_generator import PromptGenerator
from .question_classifier import QuestionClassifier  # New import

class PromptGeneration:
    def __init__(self):
        self.prompt_generator = PromptGenerator()
        self.question_classifier = QuestionClassifier()  # New: For raw question handling

    def score_mbti(self, row):
        e_i = "E" if row["Extrovert"] > row["Introvert"] else "I"
        s_n = "S" if row["Sensing"] > row["Intuitive"] else "N"
        t_f = "T" if row["Thinking"] > row["Feeling"] else "F"
        j_p = "J" if row["Judging"] > row["Perceiving"] else "P"
        return f"{e_i}{s_n}{t_f}{j_p}"

    def score_ils(self, row):
        ar = row["Active"] - row["Reflective"]
        sn = row["Sensing_FSLSM"] - row["Intuitive_FSLSM"]
        vv = row["Visual"] - row["Verbal"]
        sg = row["Sequential"] - row["Global"]
        return {
            "Active_Reflective": ar,
            "Sensing_Intuitive_ILS": sn,
            "Visual_Verbal": vv,
            "Sequential_Global": sg
        }

    def augment_data(self, df, n_synthetic=5):
        synthetic_rows = []
        for _ in range(n_synthetic):
            new_row = {
                "StudentID": f"SYNTH_{np.random.randint(1000, 9999)}",
                "Extrovert": np.random.randint(1, 10), "Introvert": np.random.randint(1, 10),
                "Sensing": np.random.randint(1, 10), "Intuitive": np.random.randint(1, 10),
                "Thinking": np.random.randint(1, 10), "Feeling": np.random.randint(1, 10),
                "Judging": np.random.randint(1, 10), "Perceiving": np.random.randint(1, 10),
                "Active": np.random.randint(1, 11), "Reflective": np.random.randint(1, 11),
                "Sensing_FSLSM": np.random.randint(1, 11), "Intuitive_FSLSM": np.random.randint(1, 11),
                "Visual": np.random.randint(1, 11), "Verbal": np.random.randint(1, 11),
                "Sequential": np.random.randint(1, 11), "Global": np.random.randint(1, 11),
                "Text_Time": np.random.randint(300, 900)
            }
            synthetic_rows.append(new_row)
        return pd.concat([df, pd.DataFrame(synthetic_rows)], ignore_index=True)

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
