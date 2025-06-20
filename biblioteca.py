# biblioteca.py

import streamlit as st

st.title("📚 Biblioteca")

def main():
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

        .st-emotion-cache-1f3w014 {{
            height: 2rem;
            width : 2rem;
            background-color: GREEN;
        }}
        </style>
    """, unsafe_allow_html=True)

    # ------------------------------
    # Sidebar (menu)
    st.sidebar.header("📚 Parâmetros de entrada")

    # Simulação de interação
    #user_input = st.text_input("Digite algo:")
    #if user_input:
    #    st.write(f"📺: Você disse: {user_input}")

    instr = 'Hi there! Enter what you want to let me know here.'

    with st.form('chat_input_form'):
        # Create two columns; adjust the ratio to your liking
        col1, col2 = st.columns([3,1]) 

        # Use the first column for text input
        with col1:
            prompt = st.text_input(
                instr,
                value=instr,
                placeholder=instr,
                label_visibility='collapsed'
            )
        # Use the second column for the submit button
        with col2:
            submitted = st.form_submit_button('Chat')
        
        if prompt and submitted:
            # Do something with the inputted text here
            st.write(f"Você disse: {prompt}")

if __name__ == "__main__":
    main()
