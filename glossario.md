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
