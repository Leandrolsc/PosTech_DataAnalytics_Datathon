# Guia do Modelo Preditivo Aderis X

Bem-vindo à documentação do motor de inteligência do Aderis X. Acreditamos que a transparência é fundamental para uma parceria de sucesso. Este guia foi criado para que você compreenda as etapas e o rigor técnico envolvidos na construção do modelo preditivo que o auxilia a tomar as melhores decisões de contratação.

## 1. Premissas e Observações Importantes

O modelo de inteligência foi construído a partir de três fontes de dados: um arquivo de Vagas, um de Candidatos e um terceiro com o Status do processo seletivo de cada aplicante.

As linhas com *infos_basicas.codigo_profissional* devem estar presentes - registros sem esta coluna foram removidos.

A conexão de dados padrão é realizada via arquivos JSON, com suporte para integração total via API ou conexão direta ao banco de dados para automação.

## 2. Coleta e Tratamento dos Dados

Na primeira etapa, realizamos a estruturação individual de cada arquivo de dados (Vagas, Candidatos e Status). Este processo, conhecido como *flattening*, consistiu em desmembrar as informações aninhadas (dicionários) de cada registro, transformando cada "chave" em uma coluna distinta. O objetivo foi converter os dados brutos em um formato tabular (linhas e colunas), que é a estrutura organizada e ideal para a análise dos algoritmos de Machine Learning.

A segunda etapa foi unificar os arquivos já tratados para formar a base de análise final. Para isso, cruzamos o arquivo de candidatos (applicants) com o de status do processo (prospect) utilizando as chaves *infos_basicas_codigo_profissional* e *dict_prospect_codigo*, respectivamente. Na sequência, integramos essa base combinada com os detalhes do arquivo de vagas através do campo *id_vagas*. Essa unificação resultou em uma base de dados coesa, onde a inteligência do Aderis X foi efetivamente treinada.

## 3. Tratamento e Preparação dos Dados (Pré-processamento)

### 3.1. Limpeza e Padronização de Campos

A primeira etapa do pré-processamento focou na limpeza de dados para garantir a consistência das informações. Realizamos a remoção de registros com valores vazios na coluna *informacoes_basicas_tipo_contratacao* e aplicamos tratamentos para eliminar espaços em branco desnecessários antes e depois dos nomes e ao redor de separadores, como vírgulas.

### 3.2. Conversão de Variáveis Categóricas em Numéricas (Encoding)

Para que o modelo pudesse interpretar a hierarquia de qualificações, convertemos variáveis de texto em escalas numéricas. Por exemplo, os níveis de idioma foram mapeados para refletir sua progressão, onde "Nenhum" se tornou 0, "Básico" se tornou 1, "Intermediário" foi mapeado como 2, "Avançado" como 3 e "Fluente" como 4. O mesmo processo foi aplicado aos níveis de formação acadêmica, que foram convertidos para uma escala numérica de 1 a 21, representando desde "Ensino Fundamental Incompleto" até "Doutorado Completo".

### 3.3. Definição da Variável-Alvo (Target)

A etapa final e mais crucial foi a criação da variável que o modelo aprenderia a prever. Consolidamos os diversos status do processo seletivo em duas categorias definitivas: Sucesso (incluindo status como "Contratado" e "Proposta Aceita") e Insucesso (com status como "Não Aprovado" e "Desistiu"). Todos os registros com status "Em Andamento" foram removidos da base de treinamento, pois um modelo supervisionado exige exemplos com resultados já concluídos para aprender com eficácia.

### 3.4. Tratamento de Variáveis Categoriais Nominais (One-Hot Encoding)

Para variáveis onde não existe uma ordem hierárquica natural, como *perfil_vaga_estado* ou *perfil_vaga_viagens_requeridas*, aplicamos a técnica de One-Hot Encoding. Este processo transforma uma única coluna com múltiplas categorias em diversas colunas binárias (de 0 ou 1), uma para cada categoria. Isso permite que o modelo analise o impacto de cada opção de forma independente, sem atribuir pesos ou ordens incorretas.

### 3.5. Desmembramento de Competências e Áreas de Atuação

Colunas como *informacoes_profissionais_area_atuacao* e *perfil_vaga_areas_atuacao* continham múltiplas habilidades ou áreas de atuação dentro de um mesmo campo. Para que o modelo pudesse analisar cada competência individualmente, nós as desmembramos. Cada área de atuação ou habilidade listada tornou-se sua própria coluna, recebendo o valor 1 se o candidato (ou a vaga) a possuísse, e 0 caso contrário.

### 3.6. Criação de Variáveis de Compatibilidade (Feature Engineering)

Além de tratar os dados existentes, criamos novas variáveis para fornecer ao modelo sinais claros de compatibilidade. Por exemplo, criamos as colunas *match_areas_contagem* e *match_areas_percentual*, que medem objetivamente quantas áreas de atuação exigidas pela vaga o candidato possui. Da mesma forma, criamos variáveis de "match" para idiomas e formação, que recebem o valor 1 se o candidato atende ou supera o nível exigido pela vaga, e 0 se não atende, simplificando a análise de compatibilidade para o modelo.

## 4. Modelagem

Com a base de dados tratada e preparada, iniciamos a fase de modelagem. Nossa abordagem consistiu em testar e comparar dois algoritmos poderosos para determinar qual ofereceria a melhor performance preditiva: um modelo de referência (Random Forest) e uma Rede Neural (Multi-Layer Perceptron).

### 4.1. Preparação do Ambiente de Treinamento

Antes de treinar os modelos, estabelecemos um ambiente de teste rigoroso e consistente para ambos:

- **Divisão dos Dados**: A base de dados foi dividida em duas partes: 80% para Treino (para ensinar o modelo) e 20% para Teste (para avaliar sua performance de forma imparcial em dados que ele nunca viu).
- **Balanceamento de Classes (SMOTE)**: Como o número de candidatos de "Insucesso" é naturalmente maior que o de "Sucesso", aplicamos a técnica SMOTE na base de treino. Este método cria exemplos sintéticos da classe minoritária ("Sucesso"), garantindo que o modelo aprenda a identificar os padrões de ambos os desfechos com a mesma importância, evitando vieses.

### 4.2. Modelo de Referência (Baseline): Random Forest

Iniciamos com um modelo Random Forest para estabelecer uma base sólida de performance. Para encontrar a configuração ideal, realizamos testes variando o número de "árvores" do modelo (*n_estimators*) em um intervalo de 10 a 200. O valor de 150 apresentou o melhor resultado e foi definido como parâmetro final, juntamente com o *random_state=42* para garantir a reprodutibilidade dos testes.

### 4.3. Modelo Final: Rede Neural (Multi-Layer Perceptron)

Utilizando a mesma base de treino e teste, desenvolvemos e otimizamos uma Rede Neural. A arquitetura final, que apresentou o melhor desempenho, foi a seguinte:

- **Estrutura**: O modelo é composto por uma camada de entrada, três camadas ocultas com 64, 32 e 16 neurônios, respectivamente, e uma camada de saída.
- **Regularização (Dropout)**: Aplicamos a técnica de Dropout (com taxas de 40% e 20%) após as duas primeiras camadas. Esse mecanismo "desliga" aleatoriamente uma parte dos neurônios durante o treinamento, o que é crucial para combater o overfitting (memorização) e garantir que o modelo generalize bem para novos candidatos.
- **Funções e Otimizador**: Utilizamos a função de ativação ReLU nas camadas ocultas e a Sigmoid na camada de saída, que é ideal para calcular a probabilidade de sucesso. O modelo foi compilado com o otimizador Adam e a função de perda *binary_crossentropy*, padrões de excelência para problemas de classificação binária como este.

## 5. Avaliação do Modelo

Após o treinamento e a otimização de ambos os modelos, realizamos a avaliação final utilizando o conjunto de dados de teste (os 20% que foram separados).

- O modelo Random Forest alcançou uma acurácia de **76%**.
- A Rede Neural (MLP) alcançou uma acurácia final de **78%**.

Apesar de a melhoria ser incremental, a arquitetura da Rede Neural se mostrou mais capaz de capturar as complexas e não-lineares nuances das interações entre os perfis dos candidatos e os requisitos das vagas. Por sua performance superior e maior potencial de generalização, a Rede Neural foi selecionada como o modelo de inteligência oficial do Aderis X.

## 6. Interface da Aplicação (Frontend)

Para dar vida ao Aderis X, utilizamos a framework **Streamlit**, uma solução moderna ideal para criar aplicações de dados de forma ágil e intuitiva. A aplicação final foi estruturada em três seções principais, garantindo uma experiência de uso completa e transparente:

- **Introdução**: A porta de entrada da ferramenta, onde apresentamos o "Porquê" e a visão do Aderis X, conectando o usuário à nossa proposta de valor.
- **A Ferramenta Aderis X**: O coração da aplicação. É nesta seção interativa que o usuário pode pesquisar os dados dos candidatos e das vagas para receber, em tempo real, o score de aderência e os insights gerados pelo nosso modelo.
- **Explicação do Modelo**: A seção atual que você está lendo. Criada para oferecer total transparência sobre a metodologia, as tecnologias e os processos utilizados na construção da inteligência do Aderis X.


## Exemplos de Estrutura dos Datasets

### Exemplo: Dataset de Candidatos (Applicants)
```json
{
  "PROF001": {
    "infos_basicas": {
      "codigo_profissional": "PROF001",
      "nome": "João Silva",
      "status": "Ativo"
    },
    "informacoes_pessoais": {
      "idade": 30,
      "cidade": "São Paulo",
      "estado": "SP"
    },
    "informacoes_profissionais": {
      "area_atuacao": "Tecnologia da Informação, Desenvolvimento de Software",
      "experiencia_anos": 8,
      "cargo_atual": "Desenvolvedor Senior"
    },
    "formacao_e_idiomas": {
      "nivel_academico": "Ensino Superior Completo",
      "curso": "Ciência da Computação",
      "nivel_ingles": "Avançado",
      "nivel_espanhol": "Básico"
    },
    "cargo_atual": {
      "empresa": "Tech Corp",
      "cargo": "Desenvolvedor Senior",
      "tempo_empresa": "3 anos"
    },
    "cv_pt": "Desenvolvedor com 8 anos de experiência em Python, JavaScript, React, Node.js. Trabalhou em projetos de e-commerce, sistemas bancários e aplicações web..."
  }
}
```

### Exemplo: Dataset de Prospects
```json
{
  "VAGA001": {
    "titulo": "Desenvolvedor Full Stack",
    "modalidade": "Presencial",
    "prospects": {
      "1": {
        "codigo": "PROF001",
        "situacao_candidado": "Aprovado",
        "data_inscricao": "2025-01-15",
        "pontuacao": 85
      },
      "2": {
        "codigo": "PROF002",
        "situacao_candidado": "Em avaliação pelo RH",
        "data_inscricao": "2025-01-16",
        "pontuacao": 72
      },
      "3": {
        "codigo": "PROF003",
        "situacao_candidado": "Recusado",
        "data_inscricao": "2025-01-17",
        "pontuacao": 45
      }
    }
  }
}
```

### Exemplo: Dataset de Vagas
```json
{
  "VAGA001": {
    "informacoes_basicas": {
      "titulo_vaga": "Desenvolvedor Full Stack Sênior",
      "tipo_contratacao": "CLT, PJ",
      "prazo_contratacao": "Imediato",
      "prioridade_vaga": "Alta",
      "origem_vaga": "Cliente Direto"
    },
    "perfil_vaga": {
      "principais_atividades": "Desenvolvimento de aplicações web, APIs REST, manutenção de sistemas legados, participação em reuniões técnicas",
      "competencia_tecnicas_e_comportamentais": "Python, JavaScript, React, Node.js, PostgreSQL, Git, metodologias ágeis, trabalho em equipe, comunicação",
      "nivel_profissional": "Sênior",
      "nivel_academico": "Ensino Superior Completo",
      "nivel_ingles": "Intermediário",
      "nivel_espanhol": "Nenhum",
      "estado": "SP",
      "areas_atuacao": "Tecnologia da Informação, Desenvolvimento de Software, Sistemas Web",
      "viagens_requeridas": "Não",
      "demais_observacoes": "Experiência mínima de 5 anos em desenvolvimento web. Conhecimento em cloud computing será um diferencial."
    },
    "beneficios": {
      "vale_refeicao": "R$ 25,00",
      "plano_saude": "Unimed",
      "home_office": "Híbrido 2x semana"
    }
  }
}
```

---

## Padrões e Convenções

### Níveis de Idioma Aceitos
- `"Nenhum"` ou `""` ou `null` → 0
- `"Básico"` → 1
- `"Intermediário"` ou `"Técnico"` → 2
- `"Avançado"` → 3
- `"Fluente"` → 4

### Níveis Acadêmicos Aceitos
- `"Ensino Fundamental Incompleto"` → 1
- `"Ensino Fundamental Cursando"` → 2
- `"Ensino Fundamental Completo"` → 3
- `"Ensino Médio Incompleto"` → 4
- `"Ensino Médio Cursando"` → 5
- `"Ensino Médio Completo"` → 6
- `"Ensino Técnico Incompleto"` → 7
- `"Ensino Técnico Cursando"` → 8
- `"Ensino Técnico Completo"` → 9
- `"Ensino Superior Incompleto"` → 10
- `"Ensino Superior Cursando"` → 11
- `"Ensino Superior Completo"` → 12
- `"Pós Graduação Incompleto"` → 13
- `"Pós Graduação Cursando"` → 14
- `"Pós Graduação Completo"` → 15
- `"Mestrado Incompleto"` → 16
- `"Mestrado Cursando"` → 17
- `"Mestrado Completo"` → 18
- `"Doutorado Incompleto"` → 19
- `"Doutorado Cursando"` → 20
- `"Doutorado Completo"` → 21

### Status de Candidatura
**Sucesso:**
- `"Aprovado"`
- `"Contratado como Hunting"`
- `"Contratado pela Decision"`
- `"Documentação Cooperado"`
- `"Documentação CLT"`
- `"Documentação PJ"`
- `"Proposta Aceita"`

**Insucesso:**
- `"Não Aprovado pelo RH"`
- `"Não Aprovado pelo Cliente"`
- `"Não Aprovado pelo Requisitante"`
- `"Recusado"`
- `"Desistiu da Contratação"`
- `"Desistiu"`
- `"Sem interesse nesta vaga"`

**Andamento (removido do modelo):**
- `"Encaminhado ao Requisitante"`
- `"Inscrito"`
- `"Prospect"`
- `"Entrevista Técnica"`
- `"Em avaliação pelo RH"`
- `"Entrevista com Cliente"`
- `"Encaminhar Proposta"`

### Formatação de Áreas de Atuação
- **Separador**: Use vírgula e espaço (`", "`)
- **Exemplo**: `"Tecnologia da Informação, Desenvolvimento de Software, Sistemas Web"`
- **Evite**: Hífens no final, separadores inconsistentes

---


### Exemplo de Saída Final
```python
# Colunas do dataset final para ML
[
    'id_vaga',
    'dict_prospect_codigo',
    'compatibilidade_vaga_cv_palavras',
    'compatibilidade_vaga_cv_percentual',
    'match_academico',
    'match_ingles',
    'match_espanhol',
    'match_areas_contagem',
    'match_areas_percentual',
    'informacoes_basicas_tipo_contratacao_codificada',
    'informacoes_basicas_prazo_contratacao_codificada',
    'informacoes_basicas_prioridade_vaga_codificada',
    'informacoes_basicas_origem_vaga_codificada',
    'perfil_vaga_estado_codificada',
    'perfil_vaga_nivel profissional_codificado',
    'perfil_vaga_nivel_ingles_codificado',
    'perfil_vaga_nivel_espanhol_codificado',
    'perfil_vaga_viagens_requeridas_codificado',
    'formacao_e_idiomas_nivel_academico_codificado',
    'formacao_e_idiomas_nivel_ingles_codificado',
    'formacao_e_idiomas_nivel_espanhol_codificado',
    'status_geral_codificado',
    # + colunas dinâmicas de áreas de atuação
    'perfil_vaga_areas_atuacao_Tecnologia da Informação',
    'perfil_vaga_areas_atuacao_Desenvolvimento de Software',
    'informacoes_profissionais_area_atuacao_Tecnologia da Informação',
    # ... outras áreas
]
```



## Glossário Técnico

Esta seção define de forma simples os principais termos técnicos mencionados neste guia.

- **Acurácia (Accuracy)**  
  Métrica que mede a porcentagem de previsões corretas que o modelo fez em relação ao total de previsões.  
  Uma acurácia de 78% significa que o modelo acertou 78 de cada 100 previsões no conjunto de teste.

- **API (Interface de Programação de Aplicações)**  
  Uma "ponte" de comunicação que permite que diferentes sistemas de software conversem entre si de forma segura e padronizada, como quando o Aderis X se conecta a um banco de dados externo.

- **Deploy (Implantação)**  
  O processo de pegar o modelo treinado e colocá-lo em um ambiente de produção, tornando-o uma ferramenta funcional e acessível para os usuários finais, como a aplicação Aderis X.

- **Dropout**  
  Técnica usada no treinamento de Redes Neurais que "desliga" aleatoriamente alguns neurônios.  
  Isso força o modelo a aprender de maneira mais robusta e evita que ele apenas memorize os dados de treino (ver *Overfitting*).

- **Encoding (Codificação)**  
  É o processo de converter dados não-numéricos (texto) em um formato numérico que o modelo possa entender.  
  No projeto, usamos a *Codificação Ordinal* (para níveis com hierarquia, como formação acadêmica) e a *One-Hot Encoding*.

- **Feature Engineering**  
  É a arte de criar novas colunas (*features*) a partir dos dados existentes para fornecer ao modelo informações mais úteis e diretas.  
  Por exemplo, em vez de dar ao modelo duas listas de habilidades, nós criamos a coluna *match_areas_percentual*.

- **Flattening (Achatamento)**  
  Processo que transforma dados aninhados e complexos (como em arquivos JSON) em um formato de tabela simples (linhas e colunas), como uma planilha.  
  Isso organiza a informação de uma maneira que o modelo pode processar facilmente.

- **Função de Ativação (ReLU, Sigmoid)**  
  Dentro de uma Rede Neural, é a função que determina se um neurônio deve ser ativado e qual a força do seu sinal.  
  *ReLU* é uma das mais comuns para as camadas internas, e a *Sigmoid* é ideal para a camada final, pois transforma o resultado em uma probabilidade (de 0 a 100%).

- **Função de Perda (Loss Function)**  
  É a métrica que calcula o "erro" do modelo durante o treinamento.  
  O objetivo do treinamento é ajustar os parâmetros do modelo para minimizar o valor desta função, ou seja, para cometer o mínimo de erros possível.

- **JSON (JavaScript Object Notation)**  
  Um formato de arquivo de texto leve e de fácil leitura para troca de dados.  
  É muito comum na web e em APIs para estruturar informações.

- **One-Hot Encoding**  
  Uma técnica de *Encoding* usada para variáveis onde não há ordem natural (ex: estados).  
  Ela cria uma nova coluna para cada categoria possível, marcando com 1 a categoria presente e com 0 as ausentes.

- **Overfitting**  
  Ocorre quando um modelo aprende os dados de treinamento "bem demais", incluindo o ruído e os detalhes irrelevantes, quase como uma memorização.  
  Como resultado, ele perde a capacidade de generalizar e fazer boas previsões para dados novos que nunca viu.

- **Random Forest (Floresta Aleatória)**  
  É um modelo de Machine Learning que opera construindo múltiplas "árvores de decisão" durante o treinamento.  
  A previsão final é feita através de um "voto" da maioria das árvores, o que torna o modelo muito robusto e preciso.  
  É como pedir a opinião de um comitê de especialistas em vez de apenas um.

- **Rede Neural (Multi-Layer Perceptron / MLP)**  
  Um modelo de aprendizado inspirado na estrutura do cérebro humano, composto por camadas de "neurônios" interconectados.  
  É especialmente poderoso para encontrar padrões muito complexos e não-lineares nos dados, como as sutilezas de uma boa contratação.

- **SMOTE (Synthetic Minority Over-sampling Technique)**  
  Técnica usada para lidar com dados desbalanceados (quando temos muito mais exemplos de uma classe do que de outra).  
  O SMOTE cria novos exemplos sintéticos, mas realistas, da classe minoritária (em nosso caso, os candidatos de "Sucesso"), garantindo que o modelo aprenda a identificar ambas as classes com a mesma importância.

- **Streamlit**  
  Uma framework de programação em Python que permite construir e compartilhar aplicações web interativas para projetos de dados e Machine Learning de forma rápida e eficiente.  
  Foi a tecnologia usada para criar a interface do Aderis X.
