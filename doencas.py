# doencas.py

import streamlit as st
import numpy as np
import os
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model, save_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

model_path = "modelos/keras_model.h5"
classes = open("modelos/labels.txt", "r").readlines()

# Verifica se o modelo existe, caso contrário cria um dummy
if not os.path.exists(model_path):
    st.warning("Modelo não encontrado, criando modelo dummy...")
    dummy_model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(len(classes), activation='softmax')
    ])
    dummy_model.compile(optimizer='adam', loss='categorical_crossentropy')
    save_model(dummy_model, model_path)

@st.cache_resource
def load_keras_model():
    """Carrega o modelo Keras uma vez e mantém em cache"""
    return load_model(model_path)

def preprocess_image(img, target_size=(224, 224)):
    """Pré-processa a imagem para o formato do modelo"""
    # Garante que a imagem está no formato RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img = img.resize(target_size)
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)

def main():
    st.title("Detecção de doenças")
    
    # Inicializa o estado da sessão
    if 'image_captured' not in st.session_state:
        st.session_state.image_captured = False
    
    # Debug: mostra o caminho do modelo
    # st.sidebar.info(f"Modelo carregado de: {os.path.abspath(model_path)}")
    
    # Contêiner para a imagem capturada
    image_container = st.empty()
    
    # Injetar JavaScript para traduzir o botão da câmera
    st.markdown(
        """
        <script>
        // Função para traduzir o botão da câmera
        function translateCameraButton() {
            // Encontra todos os botões no documento
            const buttons = document.querySelectorAll('button');
            
            // Procura pelo botão com texto 'Take Photo'
            buttons.forEach(button => {
                if (button.textContent.includes('Take Photo')) {
                    button.textContent = 'Tirar Foto';
                }
            });
        }
        
        // Executa a tradução quando a página carrega
        document.addEventListener('DOMContentLoaded', translateCameraButton);
        
        // Configura um observador para detectar quando novos componentes são adicionados
        const observer = new MutationObserver(translateCameraButton);
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Se nenhuma imagem foi capturada ainda, mostra a câmera
    if not st.session_state.image_captured:
        img_file = st.camera_input("Capture uma imagem")
        
        if img_file is not None:
            # Armazena a imagem capturada no estado da sessão
            st.session_state.captured_image = img_file
            st.session_state.image_captured = True
            # Atualiza a página imediatamente para remover a câmera
            st.rerun()
    
    # Se uma imagem foi capturada, mostra apenas ela
    if st.session_state.image_captured:
        img = Image.open(st.session_state.captured_image)
        image_container.image(img, caption="Imagem Capturada", use_container_width=True)
        
        # Botão para recapturar
        if st.button("Capturar nova imagem"):
            st.session_state.image_captured = False
            if 'captured_image' in st.session_state:
                del st.session_state.captured_image
            st.rerun()
        
        # Carrega o modelo
        try:
            model = load_keras_model()
            # st.sidebar.success("Modelo carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar o modelo: {e}")
            st.error("Verifique se o caminho do modelo está correto")
            st.stop()
        
        # Pré-processamento
        processed_img = preprocess_image(img)
        
        # Predição
        with st.spinner("Analisando imagem..."):
            try:
                predictions = model.predict(processed_img)
                if len(predictions[0]) != len(classes):
                    st.error(f"Número de classes no modelo ({len(predictions[0])}) não corresponde às classes definidas ({len(classes)})")
                    st.stop()
                
                # Remove qualquer caractere de nova linha e espaços em branco
                clean_classes = [c.strip() for c in classes]
                predicted_index = np.argmax(predictions)
                predicted_class = clean_classes[predicted_index]
                confidence = np.max(predictions) * 100
            except Exception as e:
                st.error(f"Erro durante a predição: {e}")
                return
        
        # Resultados
        st.success(f"Predição: **{predicted_class}** ({confidence:.2f}% de confiança)")
        
        # Detalhes das probabilidades
        st.subheader("Probabilidades por Classe:")
        for i, class_name in enumerate(clean_classes):
            prob = predictions[0][i] * 100
            st.progress(int(prob), text=f"{class_name}: {prob:.2f}%")

if __name__ == "__main__":
    main()
