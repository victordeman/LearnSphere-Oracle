import pandas as pd
import numpy as np
from .prompt_generator import PromptGenerator

class PromptGeneration:
    def __init__(self):
        self.prompt_generator = PromptGenerator()
    
    def score_mbti(self, row):
        ei = "E" if row["Extrovert"] > row["Introvert"] else "I"
        sn = "S" if row["Sensing"] > row["Intuitive"] else "N"
        tf = "T" if row["Thinking"] > row["Feeling"] else "F"
        jp = "J" if row["Judging"] > row["Perceiving"] else "P"
        return ei + sn + tf + jp
    
    def score_ils(self, row):
        ar = row["Active"] - row["Reflective"]
        sn = row["Sensing_FSLSM"] - row["Intuitive_FSLSM"]
        vv = row["Visual"] - row["Verbal"]
        sg = row["Sequential"] - row["Global"]
        return {"Active_Reflective": ar, "Sensing_Intuitive_ILS": sn, "Visual_Verbal": vv, "Sequential_Global": sg}
    
    def integrate_sn(self, mbti_type, ils_sn_score):
        mbti_sn = mbti_type[1]
        if (mbti_sn == "S" and ils_sn_score > 0) or (mbti_sn == "N" and ils_sn_score < 0):
            strength = "strongly" if abs(ils_sn_score) >= 9 else "moderately" if abs(ils_sn_score) >= 5 else "mildly"
            return f"{strength} {mbti_sn}-oriented"
        return "mixed S/N preference"
    
    def augment_data(self, df, n_synthetic=50):
        np.random.seed(42)
        synthetic_data = {
            "StudentID": [f"SYN_{i}" for i in range(n_synthetic)],
            "Text_Time": np.random.randint(600, 900, n_synthetic)
        }
        for i in range(n_synthetic):
            is_sensing = np.random.choice([True, False])
            synthetic_data.setdefault("Extrovert", []).append(np.random.randint(0, 6))
            synthetic_data.setdefault("Introvert", []).append(np.random.randint(0, 6))
            synthetic_data.setdefault("Thinking", []).append(np.random.randint(0, 6))
            synthetic_data.setdefault("Feeling", []).append(np.random.randint(0, 6))
            synthetic_data.setdefault("Judging", []).append(np.random.randint(0, 6))
            synthetic_data.setdefault("Perceiving", []).append(np.random.randint(0, 6))
            if is_sensing:
                synthetic_data.setdefault("Sensing", []).append(np.random.randint(4, 6))
                synthetic_data.setdefault("Intuitive", []).append(np.random.randint(0, 2))
                synthetic_data.setdefault("Sensing_FSLSM", []).append(np.random.randint(8, 12))
                synthetic_data.setdefault("Intuitive_FSLSM", []).append(11 - synthetic_data["Sensing_FSLSM"][-1])
            else:
                synthetic_data.setdefault("Sensing", []).append(np.random.randint(0, 2))
                synthetic_data.setdefault("Intuitive", []).append(np.random.randint(4, 6))
                synthetic_data.setdefault("Intuitive_FSLSM", []).append(np.random.randint(8, 12))
                synthetic_data.setdefault("Sensing_FSLSM", []).append(11 - synthetic_data["Intuitive_FSLSM"][-1])
            synthetic_data.setdefault("Active", []).append(np.random.randint(0, 12))
            synthetic_data.setdefault("Reflective", []).append(11 - synthetic_data["Active"][-1])
            synthetic_data.setdefault("Visual", []).append(np.random.randint(0, 12))
            synthetic_data.setdefault("Verbal", []).append(11 - synthetic_data["Visual"][-1])
            synthetic_data.setdefault("Sequential", []).append(np.random.randint(0, 12))
            synthetic_data.setdefault("Global", []).append(11 - synthetic_data["Sequential"][-1])
        df_synthetic = pd.DataFrame(synthetic_data)
        return pd.concat([df, df_synthetic], ignore_index=True)
    
    def process_responses(self, survey_data):
        df = pd.DataFrame(survey_data)
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
