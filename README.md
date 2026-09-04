# Sistema de Cadastro de Pessoas

Aplicação desktop desenvolvida em Python com PySide6 para realizar o cadastro de pessoas.

## Funcionalidades

- Cadastro de pessoa física ou jurídica;
- Seleção entre CPF e CNPJ;
- Validação de CPF;
- Validação de CNPJ;
- Validação de e-mail;
- Validação de celular;
- Validação de CEP;
- Consulta automática de endereço através do CEP;
- Preenchimento automático de logradouro, bairro, cidade e estado;
- Cadastro dos dados em banco de dados SQLite;
- Botão para consultar o CEP;
- Botão para cadastrar os dados;
- Botão para limpar o formulário;
- Mensagens de erro para orientar o usuário quando houver informações inválidas;
- Tratamento de erros durante a consulta do endereço e no salvamento dos dados.

## Tecnologias utilizadas

- Python
- PySide6
- SQLite
- Requests
- API ViaCEP

## Como executar

### 1. Instalar as dependências

No terminal, dentro da pasta do projeto, execute:

pip install -r requirements.txt

### 2. Executar a aplicação

Execute:

python cadastro_pyside.py

O banco de dados SQLite será criado automaticamente quando a aplicação for executada.

## Consulta de endereço

A aplicação utiliza a API ViaCEP para consultar o endereço a partir do CEP informado pelo usuário.

Quando a consulta é realizada com sucesso, os campos de:

- Logradouro;
- Bairro;
- Cidade;
- Estado

são preenchidos automaticamente.

## Banco de dados

Os cadastros são armazenados em um banco de dados SQLite chamado `cadastro.db`.

O banco é criado automaticamente pela aplicação, não sendo necessário criar o arquivo manualmente.

## Estrutura do projeto

```text
Cadastro-de-Pessoas---POOS/
│
├── cadastro_pyside.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Projeto

Atividade prática de desenvolvimento de sistema desktop com Python e PySide6.
