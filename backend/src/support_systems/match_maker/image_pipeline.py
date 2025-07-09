from sklearn.cluster import KMeans

class ImagePipeline:
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.image_store = ImageStore()
    
    def generate_and_store_images(self, prompts):
        for item in prompts:
            student_id = item["StudentID"]
            prompt = item["Prompt"]
            image_path = self.image_generator.generate_image(prompt)
            self.image_store.save_image(student_id, image_path)
    
    def cluster_and_recommend(self, df, n_clusters=3):
        features = df[["Active_Reflective", "Sensing_Intuitive_ILS", "Visual_Verbal", "Sequential_Global"]].copy()
        features["E_I"] = df["MBTI_Type"].str[0].map({"E": 1, "I": 0})
        features["S_N"] = df["MBTI_Type"].str[1].map({"S": 1, "N": 0})
        features["T_F"] = df["MBTI_Type"].str[2].map({"T": 1, "F": 0})
        features["J_P"] = df["MBTI_Type"].str[3].map({"J": 1, "P": 0})
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df["Cluster"] = kmeans.fit_predict(features)
        
        recommendations = {}
        for student_id in df["StudentID"]:
            cluster = df[df["StudentID"] == student_id]["Cluster"].iloc[0]
            mbti_type = df[df["StudentID"] == student_id]["MBTI_Type"].iloc[0]
            potential_partners = df[(df["Cluster"] == cluster) & (df["StudentID"] != student_id)]["StudentID"].tolist()
            complementary_mbti = df[(df["MBTI_Type"].str[0] != mbti_type[0]) & (df["StudentID"] != student_id)]["StudentID"].tolist()
            recommendations[student_id] = {
                "similar_partners": potential_partners[:2],
                "complementary_partners": complementary_mbti[:2]
            }
        return recommendations
