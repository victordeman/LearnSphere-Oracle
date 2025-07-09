class ImageGenerator:
    def __init__(self):
        pass
    
    def generate_image(self, prompt):
        return f"image_{hash(prompt)}.png"
