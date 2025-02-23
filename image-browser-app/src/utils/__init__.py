def load_image(image_path):
    from PIL import Image
    return Image.open(image_path)

def list_images(directory):
    import os
    return [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]