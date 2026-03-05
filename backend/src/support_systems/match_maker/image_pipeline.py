from sklearn.cluster import KMeans
import pandas as pd
import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from .image_generator import ImageGenerator
from .image_store import ImageStore

class ImagePipeline:
    def __init__(self, qdrant_host=None, qdrant_port=None):
        qdrant_host = qdrant_host or os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = qdrant_port or int(os.getenv("QDRANT_PORT", 6333))
        self.image_generator = ImageGenerator()
        self.image_store = ImageStore()
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = "student_profiles"
    
    def generate_and_store_images(self, prompts):
        for item in prompts:
            student_id = item["StudentID"]
            prompt = item["Prompt"]
            image_path = self.image_generator.generate_image(prompt)
            self.image_store.save_image(student_id, image_path)
    
    def _prepare_vectors(self, df):
        features = df[["Active_Reflective", "Sensing_Intuitive_ILS", "Visual_Verbal", "Sequential_Global"]].copy()
        features["E_I"] = df["MBTI_Type"].str[0].map({"E": 1, "I": 0})
        features["S_N"] = df["MBTI_Type"].str[1].map({"S": 1, "N": 0})
        features["T_F"] = df["MBTI_Type"].str[2].map({"T": 1, "F": 0})
        features["J_P"] = df["MBTI_Type"].str[3].map({"J": 1, "P": 0})
        return features

    def cluster_and_recommend(self, df, n_clusters=3):
        features = self._prepare_vectors(df)
        
        # Upload to Qdrant
        points = []
        for i, row in df.iterrows():
            vector = features.iloc[i].values.tolist()
            points.append(PointStruct(
                id=i,
                vector=vector,
                payload={"student_id": row["StudentID"], "mbti_type": row["MBTI_Type"]}
            ))
        
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        recommendations = {}
        for i, row in df.iterrows():
            student_id = row["StudentID"]
            vector = features.iloc[i].values.tolist()
            
            # Similar partners (nearest neighbors)
            similar_search = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=3  # Including self
            )
            similar_partners = [hit.payload["student_id"] for hit in similar_search if hit.payload["student_id"] != student_id]
            
            # Complementary partners (negative vector for some traits)
            comp_vector = vector.copy()
            comp_vector[4] = 1 - comp_vector[4]  # Flip E/I
            
            complementary_search = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=comp_vector,
                limit=2
            )
            complementary_partners = [hit.payload["student_id"] for hit in complementary_search if hit.payload["student_id"] != student_id]
            
            recommendations[student_id] = {
                "similar_partners": similar_partners[:2],
                "complementary_partners": complementary_partners[:2]
            }
        return recommendations
