import streamlit as st

def exibir():
    """
    Cria a página no Streamlit que lê e exibe o conteúdo do arquivo texto_ml.md.
    """
    st.title("📄 Guia e Documentação do Projeto")
    st.markdown("---")

    texto_ml_path = 'texto_ml.md'

    try:
        with open(texto_ml_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        st.markdown(readme_content, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error(f"Erro: O arquivo texto_ml.md` não foi encontrado no caminho esperado: {texto_ml_path}")
        st.info("Por favor, certifique-se de que o arquivo `texto_ml.md` está no diretório raiz do seu projeto Streamlit.")
