# Sistema de Cadastro de Pessoa

Aplicação desktop desenvolvida em Python com PySide6 para cadastro de pessoas.

## Funcionalidades

- Cadastro de pessoa física ou jurídica;
- Validação de CPF;
- Validação de CNPJ;
- Validação de e-mail;
- Validação de celular;
- Validação de CEP;
- Consulta automática de endereço pelo CEP;
- Preenchimento automático de logradouro, bairro, cidade e estado;
- Tratamento de erros de consulta da API;
- Salvamento dos dados em banco de dados SQLite;
- Limpeza do formulário;
- Mensagens de erro e confirmação para o usuário.

## Requisitos

- Python 3.10 ou superior;
- Conexão com a internet para consultar o CEP.

## Instalação

Abra o terminal na pasta do projeto e execute:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Depois instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

Execute:

```bash
python cadastro_pyside.py
```

O banco de dados `cadastro.db` será criado automaticamente na primeira execução.

## Organização

- `cadastro_pyside.py` — aplicação principal, interface, validações, consulta de CEP e banco de dados.
- `requirements.txt` — dependências do projeto.
- `.gitignore` — arquivos que não devem ser enviados ao GitHub.
- `static/style.qss` — reservado para estilos externos, caso sejam separados da interface no futuro.

## API de CEP

A consulta de endereço utiliza a API ViaCEP.

## Autor

Projeto desenvolvido para a atividade prática de CJOPOOS.
