## Preparando ambiente de desenvolvimento

Passo 1: Levantar o banco de dados Postgresql de desenvolvimento:

```sh
docker-compose up
```

Passo 2: Rodar as migrations da aplicação machine teaching

```sh
python manage.py migrate
```

Passo 3: Iniciar a aplicação em modo de desenvolvimento

```sh
python manage.py runserver
```

## Enviando para produção

```sh
heroku login
heroku container:push web --app machine-teaching-ufrj
heroku container:release web --app machine-teaching-ufrj
```

## TODO

1. Criar arquivo seed.sql, para popular o banco de dados de desenvolvimento com dados fake
