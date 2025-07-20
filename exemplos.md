
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