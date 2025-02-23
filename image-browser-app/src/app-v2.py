import streamlit as st
import os
from PIL import Image

# Function to get list of image files in the directory
def get_image_files(directory, file_types):
    return [f for f in os.listdir(directory) if f.lower().endswith(file_types)]

# Function to load an image
def load_image(image_path):
    return Image.open(image_path)

# Streamlit app
def main():
    st.title("Image Browser App")

    # Sidebar for user input
    st.sidebar.title("Image Source")
    folder = st.sidebar.text_input("Enter the folder path containing images:", "")
    uploaded_files = st.sidebar.file_uploader("Or upload images", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

    # User input for image file types
    file_types = st.sidebar.text_input("Enter the image file types (comma-separated, e.g., .png,.jpg,.jpeg):", ".png,.jpg,.jpeg")
    file_types = tuple(file_types.split(','))

    image_files = []
    if folder:
        image_files = get_image_files(folder, file_types)
    elif uploaded_files:
        image_files = uploaded_files

    if image_files:
        # Session state to keep track of current image index
        if 'index' not in st.session_state:
            st.session_state.index = 0

        # Navigation buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("<<"):
                st.session_state.index = 0
        with col2:
            if st.button("<"):
                if st.session_state.index > 0:
                    st.session_state.index -= 1
        with col3:
            if st.button(">"):
                if st.session_state.index < len(image_files) - 1:
                    st.session_state.index += 1
        with col4:
            if st.button(">>"):
                st.session_state.index = len(image_files) - 1

        # Display current image
        if folder:
            image_path = os.path.join(folder, image_files[st.session_state.index])
            image = load_image(image_path)
            st.image(image, caption=image_files[st.session_state.index])
            st.write(f"Filename: {image_files[st.session_state.index]}")
        else:
            image = Image.open(image_files[st.session_state.index])
            st.image(image, caption=image_files[st.session_state.index].name)
            st.write(f"Filename: {image_files[st.session_state.index].name}")
    else:
        st.write("Please enter a folder path or upload images.")

if __name__ == "__main__":
    main()