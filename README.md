# pesquisa-cpf-cnpj
Interface Vue CRUD para pesquisas de CPF e CNPJ em servidor Python+Flask via API




# Frontend Vue.js - Instalação e Execução

Este é o parte do frontend desenvolvido com **Vue.js**. Para rodá-lo corretamente, você precisará de **Node.js** versão 22 ou superior. Abaixo estão as instruções para instalar, executar e entender o funcionamento do sistema.

## Requisitos

- **Node.js versão 22 ou superior**: Para verificar a versão instalada, execute `node --version` no terminal.

## Instalação e Execução



### 1. Instalando as Dependências

Abra o terminal e navegue até a pasta do projeto. Em seguida, instale as dependências do projeto com o comando:

```bash
npm install
```

### 2. Iniciando o Projeto

Após a instalação das dependências, inicie o projeto com o seguinte comando:

```bash
npm run dev
```

### 3. Acessando a Aplicação

Com o servidor iniciado, acesse o frontend em seu navegador. O sistema pedirá informações de configuração inicial, como a **porta** e o **servidor**. Após configurar, você será redirecionado para a **tela de login**.

### 4. Tela de Login

Na tela de login, insira suas credenciais. Se você não tiver um registro, o sistema irá redirecioná-lo para a tela de **registro**.

### 5. Tela de Registro

Caso não tenha conta, você poderá se registrar. Preencha os campos solicitados e siga os passos para criar um novo usuário.

### 6. Saindo da Conta

Para sair, basta clicar na opção de **Sair do Sistema** na interface. Isso desconectará o usuário e fechará a conexão com o servidor.


# Backend  - Instalação e Execução

Este projeto backend é implementado utilizando **Flask** e requer algumas bibliotecas para funcionar corretamente. Para rodá-lo, siga as instruções abaixo.

## Requisitos

### Para o Backend:

- **Python 3.x**
- **Pip**: O gerenciador de pacotes Python para instalar as dependências e necessario ter o PIP instalado.
### Dependências

Para garantir o correto funcionamento do sistema, instale as bibliotecas necessárias com o comando abaixo:

```bash
pip install tkinter multiprocessing Flask Flask-JWT-Extended Werkzeug Flask-SQLAlchemy SQLAlchemy Flask-CORS waitress
```

### 2. Configuração do Banco de Dados

O código utiliza dois bancos de dados que são selecionados na gui do BACK:  **CNPJ** e **CPF**. 



### 3. Seleção da Porta

O código permite escolher a porta na qual o servidor  será executado. No código, e o próprio sistema irá buscar o IP local. 

