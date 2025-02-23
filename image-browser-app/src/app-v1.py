import streamlit as st
import os
from PIL import Image
from utils import load_image, list_images

def main():
    st.title("Image Browser Application")
    
    # Upload images
    uploaded_files = st.file_uploader("Choose images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Load and display the image
            image = load_image(uploaded_file)
            st.image(image, caption=uploaded_file.name, use_column_width=True)
    
    # Display images from a directory
    st.sidebar.header("Browse Images")
    image_directory = st.sidebar.text_input("Enter image directory", "")
    
    if image_directory and os.path.isdir(image_directory):
        images = list_images(image_directory)
        selected_image = st.sidebar.selectbox("Select an image", images)
        
        if selected_image:
            image_path = os.path.join(image_directory, selected_image)
            image = load_image(image_path)
            st.image(image, caption=selected_image, use_column_width=True)

if __name__ == "__main__":
    main()