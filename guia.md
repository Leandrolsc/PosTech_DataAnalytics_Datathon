# Guia do Modelo Preditivo Aderis X

Bem-vindo à documentação do motor de inteligência do Aderis X. Acreditamos que a transparência é fundamental para uma parceria de sucesso. Este guia foi criado para que você compreenda as etapas e o rigor técnico envolvidos na construção do modelo preditivo que o auxilia a tomar as melhores decisões de contratação.

## 1. Premissas e Observações Importantes

O modelo de inteligência foi construído a partir de três fontes de dados: um arquivo de Vagas, um de Candidatos e um terceiro com o Status do processo seletivo de cada aplicante.

As linhas com `infos_basicas.codigo_profissional` devem estar presentes - registros sem esta coluna foram removidos.

A conexão de dados padrão é realizada via arquivos JSON, com suporte para integração total via API ou conexão direta ao banco de dados para automação.

## 2. Coleta e Tratamento dos Dados

Na primeira etapa, realizamos a estruturação individual de cada arquivo de dados (Vagas, Candidatos e Status). Este processo, conhecido como *flattening*, consistiu em desmembrar as informações aninhadas (dicionários) de cada registro, transformando cada "chave" em uma coluna distinta. O objetivo foi converter os dados brutos em um formato tabular (linhas e colunas), que é a estrutura organizada e ideal para a análise dos algoritmos de Machine Learning.

A segunda etapa foi unificar os arquivos já tratados para formar a base de análise final. Para isso, cruzamos o arquivo de candidatos (applicants) com o de status do processo (prospect) utilizando as chaves `infos_basicas_codigo_profissional` e `dict_prospect_codigo`, respectivamente. Na sequência, integramos essa base combinada com os detalhes do arquivo de vagas através do campo `id_vagas`. Essa unificação resultou em uma base de dados coesa, onde a inteligência do Aderis X foi efetivamente treinada.

## 3. Tratamento e Preparação dos Dados (Pré-processamento)

### 3.1. Limpeza e Padronização de Campos

A primeira etapa do pré-processamento focou na limpeza de dados para garantir a consistência das informações. Realizamos a remoção de registros com valores vazios na coluna `informacoes_basicas_tipo_contratacao` e aplicamos tratamentos para eliminar espaços em branco desnecessários antes e depois dos nomes e ao redor de separadores, como vírgulas.

### 3.2. Conversão de Variáveis Categóricas em Numéricas (Encoding)

Para que o modelo pudesse interpretar a hierarquia de qualificações, convertemos variáveis de texto em escalas numéricas. Por exemplo, os níveis de idioma foram mapeados para refletir sua progressão, onde "Nenhum" se tornou 0, "Básico" se tornou 1, "Intermediário" foi mapeado como 2, "Avançado" como 3 e "Fluente" como 4. O mesmo processo foi aplicado aos níveis de formação acadêmica, que foram convertidos para uma escala numérica de 1 a 21, representando desde "Ensino Fundamental Incompleto" até "Doutorado Completo".

### 3.3. Definição da Variável-Alvo (Target)

A etapa final e mais crucial foi a criação da variável que o modelo aprenderia a prever. Consolidamos os diversos status do processo seletivo em duas categorias definitivas: Sucesso (incluindo status como "Contratado" e "Proposta Aceita") e Insucesso (com status como "Não Aprovado" e "Desistiu"). Todos os registros com status "Em Andamento" foram removidos da base de treinamento, pois um modelo supervisionado exige exemplos com resultados já concluídos para aprender com eficácia.

### 3.4. Tratamento de Variáveis Categoriais Nominais (One-Hot Encoding)

Para variáveis onde não existe uma ordem hierárquica natural, como `perfil_vaga_estado` ou `perfil_vaga_viagens_requeridas`, aplicamos a técnica de One-Hot Encoding. Este processo transforma uma única coluna com múltiplas categorias em diversas colunas binárias (de 0 ou 1), uma para cada categoria. Isso permite que o modelo analise o impacto de cada opção de forma independente, sem atribuir pesos ou ordens incorretas.

### 3.5. Desmembramento de Competências e Áreas de Atuação

Colunas como `informacoes_profissionais_area_atuacao` e `perfil_vaga_areas_atuacao` continham múltiplas habilidades ou áreas de atuação dentro de um mesmo campo. Para que o modelo pudesse analisar cada competência individualmente, nós as desmembramos. Cada área de atuação ou habilidade listada tornou-se sua própria coluna, recebendo o valor 1 se o candidato (ou a vaga) a possuísse, e 0 caso contrário.

### 3.6. Criação de Variáveis de Compatibilidade (Feature Engineering)

Além de tratar os dados existentes, criamos novas variáveis para fornecer ao modelo sinais claros de compatibilidade. Por exemplo, criamos as colunas `match_areas_contagem` e `match_areas_percentual`, que medem objetivamente quantas áreas de atuação exigidas pela vaga o candidato possui. Da mesma forma, criamos variáveis de "match" para idiomas e formação, que recebem o valor 1 se o candidato atende ou supera o nível exigido pela vaga, e 0 se não atende, simplificando a análise de compatibilidade para o modelo.

## 4. Modelagem

Com a base de dados tratada e preparada, iniciamos a fase de modelagem. Nossa abordagem consistiu em testar e comparar dois algoritmos poderosos para determinar qual ofereceria a melhor performance preditiva: um modelo de referência (Random Forest) e uma Rede Neural (Multi-Layer Perceptron).

### 4.1. Preparação do Ambiente de Treinamento

Antes de treinar os modelos, estabelecemos um ambiente de teste rigoroso e consistente para ambos:

- **Divisão dos Dados**: A base de dados foi dividida em duas partes: 80% para Treino (para ensinar o modelo) e 20% para Teste (para avaliar sua performance de forma imparcial em dados que ele nunca viu).
- **Balanceamento de Classes (SMOTE)**: Como o número de candidatos de "Insucesso" é naturalmente maior que o de "Sucesso", aplicamos a técnica SMOTE na base de treino. Este método cria exemplos sintéticos da classe minoritária ("Sucesso"), garantindo que o modelo aprenda a identificar os padrões de ambos os desfechos com a mesma importância, evitando vieses.

### 4.2. Modelo de Referência (Baseline): Random Forest

Iniciamos com um modelo Random Forest para estabelecer uma base sólida de performance. Para encontrar a configuração ideal, realizamos testes variando o número de "árvores" do modelo (`n_estimators`) em um intervalo de 10 a 200. O valor de 150 apresentou o melhor resultado e foi definido como parâmetro final, juntamente com o `random_state=42` para garantir a reprodutibilidade dos testes.

### 4.3. Modelo Final: Rede Neural (Multi-Layer Perceptron)

Utilizando a mesma base de treino e teste, desenvolvemos e otimizamos uma Rede Neural. A arquitetura final, que apresentou o melhor desempenho, foi a seguinte:

- **Estrutura**: O modelo é composto por uma camada de entrada, três camadas ocultas com 64, 32 e 16 neurônios, respectivamente, e uma camada de saída.
- **Regularização (Dropout)**: Aplicamos a técnica de Dropout (com taxas de 40% e 20%) após as duas primeiras camadas. Esse mecanismo "desliga" aleatoriamente uma parte dos neurônios durante o treinamento, o que é crucial para combater o overfitting (memorização) e garantir que o modelo generalize bem para novos candidatos.
- **Funções e Otimizador**: Utilizamos a função de ativação ReLU nas camadas ocultas e a Sigmoid na camada de saída, que é ideal para calcular a probabilidade de sucesso. O modelo foi compilado com o otimizador Adam e a função de perda `binary_crossentropy`, padrões de excelência para problemas de classificação binária como este.

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
