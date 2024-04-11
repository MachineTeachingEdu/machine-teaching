<!-- Table of contents -->
<details>
<summary>Table of Contents</summary>

- [Machine Teaching](#machine-teaching)
  - [Levantando ambiente de desenvolvimento](#levantando-ambiente-de-desenvolvimento)
    - [Levantando ambiente de desenvolvimento (com Docker)](#levantando-ambiente-de-desenvolvimento-com-docker)
    - [Levantando ambiente de desenvolvimento (sem Docker)](#levantando-ambiente-de-desenvolvimento-sem-docker)
  - [Deploy](#deploy)



## Levantando ambiente de desenvolvimento

### Levantando ambiente de desenvolvimento (com Docker)

```sh
# O comando abaixo executa as seguintes tarefas:
# - levanta o banco de dados Postgresql de desenvolvimento + Django Server:
# - executa as migrations da aplicação machine teaching
# - inicia a aplicação em modo de desenvolvimento

docker-compose up
```

### Levantando ambiente de desenvolvimento (sem Docker)

Passo 1: Levantar o banco de dados Postgresql de desenvolvimento:

```sh
docker-compose up machine_teaching_db
```

Passo 2: Rodar as migrations da aplicação machine teaching

```sh
python manage.py migrate
```

Passo 3: Iniciar a aplicação em modo de desenvolvimento

```sh
python manage.py runserver
```

## Deploy


O processo de deploy envolve:
1. Criar uma imagem docker da aplicação
2. Enviar a imagem docker da aplicação para o google artifacts registry
3. Atualizar a instância de Google Cloud Run com a nova imagem

As etapas 1 e 2 estão automatizadas no arquivo Makefile. 
Basta executar o comando a seguir:
```sh
make deploy
```
IMPORTANTE: Para que o Docker consiga enviar a imagem para o Google Artifacts Registry, é necessário estar logado no Google Cloud. Para isso, execute o comando `gcloud auth login` e siga as instruções do link a seguir: https://cloud.google.com/artifact-registry/docs/docker/authentication
