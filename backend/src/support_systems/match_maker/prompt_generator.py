class PromptGenerator:
    def generate_prompt(self, mbti_type, ils_scores, sn_integrated):
        ar = ils_scores["Active_Reflective"]
        vv = ils_scores["Visual_Verbal"]
        sg = ils_scores["Sequential_Global"]

        ar_label = "Active" if ar > 0 else "Reflective"
        ar_strength = "strongly" if abs(ar) >= 9 else "moderately" if abs(ar) >= 5 else "mildly"
        vv_label = "Visual" if vv > 0 else "Verbal"
        vv_strength = "strongly" if abs(vv) >= 9 else "moderately" if abs(vv) >= 5 else "mildly"
        sg_label = "Sequential" if sg > 0 else "Global"
        sg_strength = "strongly" if abs(sg) >= 9 else "moderately" if abs(sg) >= 5 else "mildly"

        prompt = (
            f"Create a visually symbolic and detailed illustration representing a collaboration style {mbti_type} "
            f"with {ar_strength} {ar_label}, {vv_strength} {vv_label}, and {sg_strength} {sg_label} learning approaches, "
            f"emphasizing a {sn_integrated} preference for information processing and learning. "
            f"- **Setting**: A metaphorical scene (e.g., a team workspace, learning hub, or abstract mindscape) reflecting {mbti_type} traits. "
            f"- **Collaboration Style ({mbti_type})**: Depict traits like {'outgoing' if mbti_type[0] == 'E' else 'introspective'}, "
            f"{'practical' if mbti_type[1] == 'S' else 'imaginative'}, {'logical' if mbti_type[2] == 'T' else 'empathetic'}, "
            f"and {'structured' if mbti_type[3] == 'J' else 'adaptable'}. "
            f"- **Learning Approach**: Show {ar_label} engagement (e.g., {'group activities' if ar_label == 'Active' else 'solitary reflection'}), "
            f"{vv_label} input (e.g., {'diagrams' if vv_label == 'Visual' else 'text-based notes'}), and {sg_label} understanding "
            f"(e.g., {'step-by-step plans' if sg_label == 'Sequential' else 'holistic insights'}). "
            f"- **Information Preference**: Highlight the {sn_integrated} approach with elements like "
            f"{'detailed tools and charts' if 'Sensing' in sn_integrated else 'abstract patterns and visions'}. "
            f"- **Mood and Style**: Use {'vibrant' if mbti_type[0] == 'E' else 'calm'} colors, with "
            f"{'warm' if mbti_type[2] == 'F' else 'cool'} tones, and a {'structured' if mbti_type[3] == 'J' else 'dynamic'} composition. "
            f"**Stable Diffusion Parameters**: Style: 'symbolic illustration, detailed, educational theme, cinematic lighting', "
            f"Negative Prompt: 'blurry, dark, distorted', Steps: 50, CFG Scale: 7.5"
        )
        return prompt
