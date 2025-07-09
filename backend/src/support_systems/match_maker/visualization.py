import streamlit as st

def visualize_recommendations(df, recommendations, image_store):
    st.title("Match Maker: Partner Recommendations for Team Projects")
    for student_id in df["StudentID"]:
        st.subheader(f"Student: {student_id}")
        profile = df[df["StudentID"] == student_id]
        st.write(f"Collaboration Style: {profile['MBTI_Type'].iloc[0]}")
        st.write(f"Learning Approach: AR={profile['Active_Reflective'].iloc[0]}, S/N={profile['Sensing_Intuitive_ILS'].iloc[0]}, "
                 f"VV={profile['Visual_Verbal'].iloc[0]}, SG={profile['Sequential_Global'].iloc[0]}")
        st.write(f"Information Preference: {profile['SN_Integration'].iloc[0]}")
        image = image_store.retrieve_image(student_id)
        if image:
            st.image(image, caption=f"Visual Representation of {student_id}'s Profile")
        recs = recommendations[student_id]
        st.write("Recommended Partners (Similar Traits):", recs["similar_partners"])
        st.write("Recommended Partners (Complementary Traits):", recs["complementary_partners"])
