# Publicar a InvitStore

O projeto inclui Dockerfile e configuração para Railway, mantendo a organização Flask. Os passos de hospedagem abaixo não foram executados em uma conta do usuário nesta entrega.

## Railway

1. Coloque o conteúdo da pasta `InvitStore_Web_v2` na raiz de um repositório privado e conecte-o a um serviço Railway. O `Dockerfile` é usado para construir a aplicação.
2. Adicione **um volume persistente montado em `/data`**. Isso preserva o SQLite e as fotos entre reinicializações e novas publicações.
3. Configure estas variáveis no serviço:

| Variável | Valor |
|---|---|
| `APP_ENV` | `production` |
| `DATA_DIR` | `/data` |
| `SECRET_KEY` | Chave aleatória com pelo menos 32 caracteres |
| `ADMIN_NAME` | Nome público do principal |
| `ADMIN_EMAIL` | E-mail de acesso do principal |
| `ADMIN_WHATSAPP` | WhatsApp brasileiro com DDD, preferencialmente `55` + DDD + número |
| `ADMIN_PASSWORD` | Senha escolhida, entre 10 e 128 caracteres |

Para gerar uma chave: `python -c "import secrets; print(secrets.token_hex(32))"`.

4. Publique com **uma réplica**. O processo usa Gunicorn com um worker e quatro threads, compatível com o banco SQLite desta versão.
5. Gere o domínio HTTPS no serviço. Defina `PUBLIC_BASE_URL` como a URL completa, por exemplo `https://sua-loja.up.railway.app`, e publique essa configuração.
6. Opcionalmente, defina `TRUSTED_HOSTS` com os domínios permitidos separados por vírgula, sem protocolo. Inclua os hosts necessários às verificações de saúde da plataforma; uma lista incorreta bloqueia requisições legítimas.
7. Entre em `/login`, confira o WhatsApp no perfil e cadastre uma categoria e um produto. Faça um pedido de teste e confirme o destinatário e os valores na mensagem, antes de enviá-la.

As variáveis `ADMIN_*` são usadas somente se o banco não tiver nenhuma conta. Reiniciar ou publicar novamente não troca as senhas existentes. Depois da primeira criação, remova `ADMIN_PASSWORD` das variáveis do serviço. Use o painel ou o comando de recuperação para redefinir senhas.

O `/health` verifica a conexão com o banco. Em produção, os cookies administrativos exigem HTTPS. Mantenha `SECRET_KEY` estável entre publicações; trocá-la encerra sessões e carrinhos.

## Outra hospedagem com Docker

Use o mesmo Dockerfile, configure as variáveis acima, exponha a porta definida por `PORT` (padrão 8080), monte `/data` em armazenamento persistente e coloque HTTPS à frente da aplicação. Não use múltiplas réplicas com este SQLite. A implantação com Docker exige revisão das permissões do volume no provedor escolhido.

## Atualizações

Faça backup de `/data` com a aplicação parada antes de substituir os arquivos. O banco foi criado para esta InvitStore; não copie o banco do projeto de referência, pois os esquemas são diferentes. Futuras alterações do esquema precisarão de migrações específicas; `create_all` só cria tabelas ausentes.

Referências oficiais consultadas:

- [Volumes Railway](https://docs.railway.com/volumes)
- [Referência de volumes](https://docs.railway.com/volumes/reference)
- [Flask-WTF: CSRF](https://flask-wtf.readthedocs.io/en/latest/csrf/)
- [WhatsApp: conversa em um clique](https://faq.whatsapp.com/5913398998672934/?locale=pt_BR)
