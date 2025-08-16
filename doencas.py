# doencas.py
# Referências:
# - Conjunto de dados de reconhecimento de doenças de plantas:
#   https://www.kaggle.com/datasets/rashikrahmanpritom/plant-disease-recognition-dataset

import streamlit as st
from keras.models import load_model
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
    model_path = "./modelos/keras_model.h5"
    try:
        model = load_model(model_path)
        
        # Verificação detalhada da arquitetura do modelo
        if len(model.inputs) > 1:
            st.error("""
            Erro: Modelo requer múltiplas entradas. 
            Esta versão do aplicativo só suporta modelos com entrada única.
            """)
            return None
            
        # Verificar se o modelo pode processar imagens 224x224x3
        input_shape = model.input_shape
        if input_shape is not None and len(input_shape) == 4:
            if input_shape[1:] != (224, 224, 3):
                st.error(f"""
                Erro: Modelo espera formato de entrada {input_shape[1:]}, 
                mas o aplicativo está preparado para imagens 224x224x3.
                """)
                return None
                
        return model
        
    except Exception as e:
        st.error(f"Erro ao carregar o modelo: {str(e)}")
        return None

@st.cache_data
def get_labels():
    try:
        with open("./modelos/labels.txt", "r", encoding="utf-8") as f:
            labels = [line.strip() for line in f.readlines()]
        return labels
    except Exception as e:
        st.error(f"Erro ao carregar labels: {str(e)}")
        return ["Erro: Arquivo de labels não encontrado"]

def process_image(image, model):
    """Processa a imagem de acordo com os requisitos do modelo"""
    try:
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        
        # Normalização específica para modelos MobileNet/Keras
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array
        
        return model.predict(data, verbose=0)
    except Exception as e:
        st.error(f"Erro no processamento da imagem: {str(e)}")
        return None

def main():
    with st.sidebar:
        st.markdown("<h2 style='margin:0; padding:0; margin-top:0; padding-top:0; margin-bottom:0;'>🐛 Detecção de Doenças</h2>",
                    unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top: 1rem; margin-bottom: 1rem;'>
        <small>Como usar:</small>
        <ol style='padding-left: 1.2rem; margin-top: 0.2rem;'>
            <li><small>Posicione a câmera na folha da planta</small></li>
            <li><small>Certifique-se de boa iluminação</small></li>
            <li><small>Mantenha o foco na área afetada</small></li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar", key="btn_back_doencas", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col2:
            if st.button("🚪 Sair", key="btn_logout_doencas", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()

    # Inicialização de estados
    if 'photo_taken' not in st.session_state:
        st.session_state.photo_taken = False
        st.session_state.picture = None
        st.session_state.prediction = None
        st.session_state.simulated_mode = False

    # Carregar modelo
    model = get_keras_model()
    if model is None:
        st.warning("⚠️ Funcionalidade temporariamente indisponível. Ativando modo simulado.")
        st.session_state.simulated_mode = True
    else:
        labels = get_labels()
        st.session_state.simulated_mode = False

    # Layout principal
    st.markdown("### 🔍 Analisar Planta")
    
    if st.session_state.photo_taken:
        st.image(st.session_state.picture, use_column_width=True, caption="Imagem capturada")
        
        if not st.session_state.simulated_mode and st.session_state.prediction is not None:
            class_index = np.argmax(st.session_state.prediction)
            confidence = st.session_state.prediction[0][class_index]
            
            st.subheader("🔬 Resultado da Análise")
            
            if confidence >= 0.5:
                class_name = labels[class_index]
                st.success(f"**Planta:** {class_name[2:]}")
                st.info(f"**Confiança:** {confidence:.2%}")
                
                st.markdown("### 💡 Recomendações")
                if "saudável" in class_name.lower():
                    st.success("Sua planta parece saudável! Mantenha os cuidados atuais.")
                else:
                    st.warning("""
                    **Ações recomendadas:**
                    - Isolar a planta afetada
                    - Remover folhas muito danificadas
                    - Aplicar tratamento específico
                    - Monitorar evolução
                    """)
            else:
                st.error("Imagem não reconhecida. Por favor, tente novamente com melhor iluminação e foco.")
        
        elif st.session_state.simulated_mode:
            st.markdown("<div class='simulated-mode'>", unsafe_allow_html=True)
            st.subheader("🧪 Modo Simulado (Funcionalidade em Desenvolvimento)")
            st.write("""
            **Esta funcionalidade está em desenvolvimento!**
            
            Resultados simulados para demonstração:
            - 🌿 **Planta:** Tomateiro
            - 🔍 **Doença:** Mancha bacteriana
            - 📊 **Confiança:** 86%
            - 💡 **Recomendação:** 
                - Aplicar fungicida a cada 7 dias
                - Reduzir irrigação foliar
                - Remover folhas muito afetadas
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🔄 Tirar nova foto"):
            st.session_state.photo_taken = False
            st.session_state.picture = None
            st.session_state.prediction = None
            st.rerun()
    
    else:
        picture = st.camera_input("Aponte a câmera para a folha da planta")
        
        if picture:
            try:
                image = Image.open(picture).convert("RGB")
                st.session_state.picture = image
                
                if not st.session_state.simulated_mode:
                    prediction = process_image(image, model)
                    st.session_state.prediction = prediction
                
                st.session_state.photo_taken = True
                st.rerun()
            
            except Exception as e:
                st.error(f"Erro ao processar imagem: {str(e)}")
                st.session_state.simulated_mode = True
                st.session_state.photo_taken = True
                st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ Sobre a Detecção de Doenças")
    st.write("""
    Esta ferramenta utiliza inteligência artificial para identificar possíveis doenças em plantas. 
    Para melhores resultados:
    - Fotografe folhas com sintomas visíveis
    - Certifique-se de boa iluminação
    - Foque na área afetada
    - Evite sombras ou reflexos
    
    **Observação:** Os resultados são indicativos e não substituem análise profissional.
    """)

if __name__ == "__main__":
    main()
