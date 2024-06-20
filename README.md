# lu-estilo-api

A Lu Estilo é uma empresa de confecção que está buscando novas oportunidades de negócio, mas o time comercial não possui nenhuma ferramenta que facilite novos canais de vendas.

Para ajudar o time comercial, você deve desenvolver uma API RESTful utilizando FastAPI que forneça dados e funcionalidades para facilitar a comunicação entre o time comercial, os clientes e a empresa. Essa API deve ser consumida por uma interface Front-End, que será desenvolvida por outro time.

API construída com FastAPI, Postgres, Alembic, Sentry, Pytest e Swagger

Aplicação rodando em nuvem:

`https://lu-api-2zto7jlh2q-rj.a.run.app/`

Como rodar localmente:

Construir o Dockerfile com

`docker build -t lu-api .`

Rodar a imagem com

`docker run -d --name mycontainer -p 8000:8000 lu-api`

A aplicação iniciará em

`localhost:8000`

Veja a documentação Swagger em

`https://lu-api-2zto7jlh2q-rj.a.run.app/docs`

`localhost:8000/docs`