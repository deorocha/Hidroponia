# doencas.py

import streamlit as st
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

col1, col2 = st.columns([0.10,0.90], gap=None, vertical_alignment="center", border=False)
with col1:
    st.image('./imagens/doencas.png', width=48)
with col2:
    st.subheader("Detecção de doenças")

@st.cache_resource
def get_keras_model():
    model_path = "modelos/keras_model.h5"
    model = load_model(model_path)
    return model

@st.cache_data
def get_labels():
    # Abrir arquivo com codificação UTF-8
    with open("modelos/labels.txt", "r", encoding="utf-8") as f:
        labels = f.readlines()
    return labels

def main():
    # Botão para voltar ao menu principal
    st.markdown('<a href="/" target="_self"><button style="margin-top:20px;">Voltar ao Menu Principal</button></a>', unsafe_allow_html=True)

    st.markdown(f"""
        <style>
        html, body, [class*="css"] {{
            font-size: 15px;
        }}

        .block-container {{
            padding-top: 3rem;
            padding-bottom: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}
        </style>
    """, unsafe_allow_html=True)

    model = get_keras_model()
    labels = get_labels()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Estado inicial com câmera habilitada
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
