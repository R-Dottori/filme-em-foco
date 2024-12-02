# Filme em Foco

## Projeto
Nesse projeto criaremos um aplicativo utilizando a biblioteca Streamlit,
incluindo instruções de instalação e criação do repositório.

O objetivo do aplicativo é exibir de maneira intuitiva e interativa dados
sobre filmes, sessões de cinema, recomendações e opiniões da audiência.

## Instalação e Uso
1 - Criar um novo ambiente virtual: "python -m venv .venv_app"

2 - Ativar o ambiente: ".venv_app/Scripts/activate"

3 - Instalar as dependências: "python -m pip install -r requirements.txt"

4 - Configurar o arquivo ".env" com a chave da API do Gemini (GEMINI_KEY)

5 - Rodar a API: "uvicorn src.api:app"

6 - Rodar o aplicativo do Streamlit: "streamlit run ./src/filme_foco.py"
