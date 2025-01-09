
# Importações
import streamlit as st
import requests
import pandas as pd
import json
import google.generativeai as genai
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk



# Configurações
st.set_page_config(
    page_title='Filme em Foco',
    page_icon='🎥',
)

api_key = os.getenv('GEMINI_KEY')
genai.configure(api_key=api_key)
modelo = genai.GenerativeModel('gemini-1.5-flash')


nltk.download('stopwords')

pag_1_title = 'Recomendações'
pag_2_title = 'Análise de Sentimentos'
pag_3_title = 'Filmes Em Cartaz'
pag_4_title = 'Outros Filmes'
pag_5_title = 'Opções'


if all(key not in st.session_state for key in ['base_filmes', 'df_base', 'em_cartaz_df', 'em_cartaz_json', 'historico_chatbot', 'infos_usuario']):
    try:
        resp_filmes = requests.get('http://127.0.0.1:8000/top_250').text
        st.session_state['base_filmes'] = json.loads(resp_filmes)
        st.session_state['df_base'] = pd.DataFrame(st.session_state['base_filmes'])
        resp_cartaz = requests.get('http://127.0.0.1:8000/em_cartaz').text
        em_cartaz_json = json.loads(resp_cartaz)
        em_cartaz_df = pd.DataFrame(em_cartaz_json)
        st.session_state['em_cartaz_df'] = em_cartaz_df
        st.session_state['em_cartaz_json'] = em_cartaz_json
        st.session_state['historico_chatbot'] = ''
        st.session_state['infos_usuario'] = ''
    except:
        st.error('Erro ao comunicar com a API.')



# Funções de Uso Geral
def chatbot(prompt):
    with open('./cache/infos_usuario.txt', 'r', encoding='utf-8') as arquivo:
        historico_usuario = arquivo.read()
        
    instrucoes = f"""
    Você é um chatbot altamente sofisticado e especialista em cinema.

    Você tem acesso aos filmes que estão atualmente em cartaz.
    Priorize que as sugestões sejam para os filmes em cartaz, caso algum encaixe nos gostos do usuário.

    Você também tem acesso a uma base de dados de filmes com as seguintes colunas:
    titulo - titulo_original - ano - duracao - diretor - roteirista - elenco - nota - num_votos - sinopse - genero - verba - receita
    A duração dos filmes na coluna duracao está em minutos. Por exemplo: 120 = 2 horas; 60 = 1 hora; 90 = 1 hora e 30 minutos.
    Caso a coluna de verba e/ou receita estejam iguais a 0, considere que o dado não foi coletado corretamente e não que esses sejam os valores observados.
    Você SEMPRE tem acesso a essa base, independente do seu histórico de mensagens.
    Caso existam conflitos entre as informações da base e seu treinamento prévio, dê prioridade para a base fornecida.
    
    Um de seus objetivos é dar sugestões de filmes para os usuários, baseando-se na base de dados, nos filmes em cartaz e nas preferências do usuário.
    Caso sinta que a pergunta do usuário não é suficiente para gerar uma resposta adequada, indique como o usuário pode incrementar a sua pergunta.
    MESMO ASSIM, sempre complete a sugestão, ainda que a resposta não seja ideal.
    Se nenhum dos filmes em cartaz for parecido com o pedido do usuário, indique um filme da outra base.

    Você tem acesso a todo o histórico de conversas da sessão que estiver rodando.
    Consulte o histórico, mas não exiba seu conteúdo a não ser que seja explicitamente solicitado.
    Caso o histórico de mensagens esteja vazio, ignore-o.

    Durante a conversa, separe informações importantes sobre os gostos do usuário.
    Isso inclui filmes que gosta, gêneros que desgosta e outros interesses para além do cinema.
    Salve também informações básicas que identifiquem o usuário, como nome, sobrenome, apelido, idade.
    NUNCA inclua informações sigilosas como número de documentos.
    NUNCA inclua aspectos da personalidade do usuário, mesmo que sejam descritos pelo próprio usuário.
    Salve essas informações de maneira objetiva, iniciando esse segmento com "[INFOS_USUARIO]".
    Você terá acesso ao histórico de informações que coletou do usuário.
    Se existir mais de uma informação sobre um tópico mas que não seja conflitante, considere ambas.
    Se as informações forem diretamente conflitantes, considere somente a mais recente.
    Crie esse segmento SOMENTE se identificar novas informações na PERGUNTA DO USUÁRIO.
    Não gere nenhuma informação adicional caso não identifique algo relevante na pergunta.
    As informações passadas são consideradas, mas não precisam ser exibidas a não ser que sejam explicitamente solicitadas.
    Caso as informações estejam vazias, ignore-as.

    • Exemplo de informações importantes:
    "Boa noite! Me chamo João" -- [INFOS_USUARIO] Nome do usuário é João
    "Meu filme favorito é Chinatown mas não gosto muito do Jack Nicholson" -- [INFOS_USUARIO] Filme favorito é Chinatown / Não gosta tanto do ator Jack Nicholson
    "Estou bem... me indica um filme?" -- Nenhuma informação relevante
    "Meu filme favorito é Karate Kid" -- [INFOS_USUARIO] Filme favorito é Karate Kid (nesse caso, ainda considere Chinatown)
    "Eu sou muito alegre!" -- Não considere informações sobre a personalidade
    "Adoro filmes alegres" -- Nesse caso, o usuário está falando sobre seus interesses -- [INFOS_USUARIO] Gosta de filmes alegres
    "Eu sou a Ana! Tudo bem com você?" -- [INFOS_USUARIO] Nome do usuário é Ana (nesse caso, provavelmente desconsidere o nome João)

    Ao final de tudo, responda a pergunta do usuário, iniciando o segmento da resposta com "[RESPOSTA_CHATBOT]".
    Tente manter as respostas concissas, curtas e direto ao ponto.
    Tente completar as sugestões sempre, mesmo que não tenha informações o suficiente.

    • Base de Filmes:
    {st.session_state['base_filmes']}

    • Filmes Atualmente em Cartaz:
    {st.session_state['em_cartaz_json']}

    • Histórico de Mensagens:
    {st.session_state['historico_chatbot']}

    • Informações do Usuário:
    {historico_usuario}
    
    • Pergunta do Usuário:
    {prompt}
    """

    respostas_bruto = modelo.generate_content(instrucoes).text.split('[')
    for segmento in respostas_bruto:
        if 'INFOS_USUARIO' in segmento:
            pos = segmento.find(']') + 1
            infos_usuario = segmento[pos:]
            with open('./cache/infos_usuario.txt', 'a', encoding='utf-8') as arquivo:
                arquivo.write(infos_usuario)

        if 'RESPOSTA_CHATBOT' in segmento:
            pos = segmento.find(']') + 1
            resposta = segmento[pos:]
            st.session_state['historico_chatbot'] += '• Pergunta do Usuário:\n'
            st.session_state['historico_chatbot'] += prompt.strip()
            st.session_state['historico_chatbot'] += '\n• Resposta do Chatbot:\n'
            st.session_state['historico_chatbot'] += resposta.strip()
            st.session_state['historico_chatbot'] += '\n\n'

    try:
        return resposta
    except:
        return 'Desculpa! Não foi possível gerar uma resposta.'


def analise_sentimentos(filme):
    if filme['analises'] != '[]':
        analises = '---'.join(filme['analises'])
        resultado = modelo.generate_content(f"""
                Você é um especialista em cinema.
                Realize a análise de sentimentos de cada opinião de usuário abaixo.
                As opiniões estão separadas por "---".
                Ao final conte quantas análises são positivas e quantas negativas.
                Além disso, crie um resumo da opinião do público, em português.
                Responda SOMENTE com os resultados.

                Exemplo de resposta:
                    POSITIVAS = 15
                    NEGATIVAS = 3
                    CONSENSO = O consenso é este...

                    {analises}
                    """).text
        pos_posit = resultado.find('POSITIVAS')
        pos_negat = resultado.find('NEGATIVAS')
        pos_cons = resultado.find('CONSENSO')
        analises_pos = int(resultado[pos_posit + 11:pos_negat].strip())
        analises_neg = int(resultado[pos_negat + 11:pos_cons].strip())
        num_analises = analises_pos + analises_neg
        consenso = resultado[pos_cons + 10:].strip()
    else:
        num_analises = 0
        analises_pos = 0
        analises_neg = 0
        consenso = 0
    
    if num_analises > 5:
        perc_pos = round(analises_pos / num_analises * 100)
        perc_neg = round(analises_neg / num_analises * 100)
        st.write(f'Consenso das Opiniões: {consenso}')
        st.write(f'Avaliações Positivas: {perc_pos}%')
        st.write(f'Avaliações Negativas: {perc_neg}%')
        fig, ax = plt.subplots()
        ax.bar(['Análises Positivas', 'Análises Negativas'], [perc_pos, perc_neg], color=['green', 'red'])
        ax.set_title('Visualização')
        ax.set_ylabel('Percentual')
        st.pyplot(fig)
    else:
        st.write('Não há avaliações suficientes para realizar a análise.')

# Conteúdo das Páginas
def pagina_um():
    st.title('Filme em Foco')

    st.header('Alfred Hitchbot')

    avatares = {
    'human': 'user',
    'ai': 'assistant'
    }

    st.chat_message('assistant').write("""Olá! Sou o Alfred Hitchbot, um assistente virtual especializado em cinema.

    \nMe faça qualquer pergunta!

    \nSe quiser uma sugestão de filme, me conte um pouquinho sobre o que está procurando, como seu filme favorito ou um gênero específico.
    """)

    if st.session_state['historico_chatbot'] != '':
        for mensagem in st.session_state['historico_chatbot'].split('• Pergunta do Usuário'):
            if mensagem != '':
                pos_bot = mensagem.find('• Resposta do Chatbot')
                st.chat_message('user').write(mensagem[2:pos_bot].strip())
                st.chat_message('assistant').write(mensagem[pos_bot + 23:].strip())

    if prompt := st.chat_input('Digite sua mensagem'):
        st.chat_message('user').write(prompt)
        with st.spinner('Processando...'):
            resposta = chatbot(prompt)
            st.chat_message('assistant').write(resposta)

def pagina_dois():
    st.title(pag_2_title)
    opcoes_sel = [filme['titulo'] for filme in st.session_state['em_cartaz_json']]
    selecao = st.selectbox('Escolha um filme:', options=opcoes_sel)
    filme_sel = next(filme for filme in st.session_state['em_cartaz_json'] if filme['titulo'] == selecao)
    if st.button('Gerar análise'):
        with st.spinner('Processando...'):
            analise_sentimentos(filme_sel)
    

def pagina_tres():
    st.title(pag_3_title)
    try:
        for filme in st.session_state['em_cartaz_json']:
            poster, infos = st.columns(2)
            with poster:
                st.image(filme['poster'])
            with infos:
                st.markdown(f"""
                # {filme['titulo']}
                ### {filme['ano']} - {filme['duracao']} minutos

                Direção: {''.join(filme['diretor']).replace('[','').replace(']','').replace("'", '').replace('"', '')}

                Elenco: {''.join(filme['elenco']).replace('[','').replace(']','').replace("'", '').replace('"', '')}

                Sinopse:
                {filme['sinopse']}

                [Ver sessões](https://www.ingresso.com/filme/{filme['titulo'].lower().replace(' ','-').replace(':','')})
                """)
    except:
        st.error('Erro ao carregar os filmes em cartaz.')



def pagina_quatro():
    st.title(pag_4_title)
    st.header('Lista de Filmes')
    st.write(st.session_state['df_base'])

    st.header('Visualizações')

    generos_bruto = [genero for genero in st.session_state['df_base']['genero']]
    generos = []
    for genero in generos_bruto:
        genero = genero.replace('[', '').replace(']', '').replace(',', '').replace("'", '')
        genero = genero.split()
        for x in genero:
            if x == 'Adicionar' or x == 'aviso' or x == 'de' or x == 'conteúdo' or x == 'científica' or x == 'Filme':
                pass
            else:
                if x == 'Ficção':
                    x = 'Ficção Científica'
                if x == 'noir':
                    x = 'Noir'
                generos.append(x)

    df_generos = pd.DataFrame(generos, columns=['genero'])

    plt.figure()
    sns.countplot(data=df_generos, y='genero', hue='genero', order=df_generos['genero'].value_counts().index)
    plt.title('Frequência de Gêneros')
    plt.xlabel('Contagem')
    plt.ylabel('Gênero')
    st.pyplot(plt)

    with st.spinner('Carregando...'):
        sinopses = ' '.join(st.session_state['df_base']['sinopse'].astype(str))
        stop_words = set(stopwords.words('portuguese'))
        nuvem = WordCloud(
            width=1000, 
            height=500,
            background_color='white',
            stopwords=stop_words,
        ).generate(sinopses)

        plt.figure()
        plt.imshow(nuvem)
        plt.axis('off')
        plt.title('Nuvem de Palavras das Sinopses')
        st.pyplot(plt)


def pagina_cinco():
    st.title(pag_5_title)
    if st.button('Apagar cache do usuário'):
        with open('./cache/infos_usuario.txt', 'w', encoding='utf-8') as arquivo:
            arquivo.write('')
        st.success('Cache apagado.')



# Menu de Navegação
st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title, pag_4_title, pag_5_title))
if pagina == pag_1_title:
    pagina_um()
elif pagina == pag_2_title:
    pagina_dois()
elif pagina == pag_3_title:
    pagina_tres()
elif pagina == pag_4_title:
    pagina_quatro()
else:
    pagina_cinco()
