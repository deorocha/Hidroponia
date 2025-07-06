# doencas_imagem.py

import streamlit as st
from tensorflow.keras.models import load_model  # Alterado aqui
from PIL import Image, ImageOps
import numpy as np

# Carregamento do CSS customizado externo
try:
    with open('./styles/style.css') as f:
        css_external = f.read()
    st.markdown(f"<style>{css_external}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo style.css não encontrado em ./styles/. Verifique o caminho.")
except Exception as e:
    st.error(f"Erro ao carregar style.css: {e}")

@st.cache_resource
def get_keras_model():
    model_path = "modelos/keras_model.h5"
    model = load_model(model_path)
    return model

@st.cache_data
def get_labels():
    with open("modelos/labels.txt", "r", encoding="utf-8") as f:
        labels = f.readlines()
    return labels

def main():
    model = get_keras_model()
    labels = get_labels()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    if 'photo_taken' not in st.session_state:
        st.session_state.photo_taken = False
        st.session_state.picture = None
        st.session_state.prediction = None

    if st.session_state.photo_taken:
        st.image(st.session_state.picture, use_container_width=True)
        
        if st.session_state.prediction is not None:
            class_index = np.argmax(st.session_state.prediction)
            confidence = st.session_state.prediction[0][class_index]
            
            st.subheader("Resultado da Análise")
            
            if confidence >= 0.5:
                class_name = labels[class_index]
                st.write(f"**Fruta:** {class_name[2:]}")
                st.write(f"**Conf.:** {confidence:.2%}")
            else:
                st.error("Imagem não reconhecida.")
        
        if st.button("Tirar nova foto"):
            st.session_state.photo_taken = False
            st.session_state.picture = None
            st.session_state.prediction = None
            st.rerun()
            
    else:
        picture = st.camera_input("Tire uma foto")
        
        if picture:
            image = Image.open(picture).convert("RGB")
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            image_array = np.asarray(image)
            
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
            data[0] = normalized_image_array
            
            prediction = model.predict(data, verbose=0)
            
            st.session_state.photo_taken = True
            st.session_state.picture = image
            st.session_state.prediction = prediction
            st.rerun()

if __name__ == "__main__":
    main()
