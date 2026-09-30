# Correção do erro SECRET_KEY no Railway · 2.0.1

A captura enviada mostrou a mensagem `Defina SECRET_KEY com pelo menos 32 caracteres no ambiente de produção.` O processo encerrava antes de criar o banco e a primeira conta.

Nesta versão, a chave é criada automaticamente em `/data/secret.key` quando `SECRET_KEY` não está definida. Ela permanece estável se o volume `/data` for mantido. Uma chave definida manualmente continua válida e deve conter pelo menos 32 caracteres.

## Atualizar o serviço existente

1. Atualize **o mesmo repositório e serviço** que já está ligado ao Railway com os arquivos deste ZIP. Se a raiz do repositório for a pasta da aplicação, copie o conteúdo interno de `InvitStore_Web_v2`, incluindo `Dockerfile`, `config.py` e `start_production.sh`. Faça o commit e envie a atualização.
2. No projeto Railway, conecte um **Volume** a esse serviço e defina **Mount Path `/data`**. O volume guarda o banco SQLite, as fotos e a chave. Ele deve estar montado antes da inicialização.
3. No serviço, abra **Variables** e configure os dados da primeira conta:

   - `ADMIN_NAME` → seu nome público;
   - `ADMIN_EMAIL` → seu e-mail de acesso;
   - `ADMIN_WHATSAPP` → seu WhatsApp com DDD (por exemplo, `35987654321`);
   - `ADMIN_PASSWORD` → uma senha forte com 10 a 128 caracteres, criada por você.

   O Dockerfile já define `APP_ENV=production` e `DATA_DIR=/data`. Não é necessário adicionar `SECRET_KEY` com esta versão. Se ela já existir no Railway, mantenha-a, desde que tenha ao menos 32 caracteres.

4. Aplique as alterações e publique. A primeira inicialização criará o administrador. Depois de conseguir entrar em `/login`, você pode retirar `ADMIN_PASSWORD` das variáveis; os próximos reinícios não redefinem a senha.

Se aparecer `Configure um volume persistente montado em /data`, verifique se o volume está conectado **ao serviço InvitStore** e se o caminho configurado é exatamente `/data`. Se aparecer `Primeira instalação: configure ADMIN_NAME...`, preencha os quatro dados da primeira conta no serviço e aplique as mudanças.

Ao atualizar o serviço, preserve o volume existente; nunca substitua `/data` por uma pasta no repositório. Caso a loja já tenha dados de outra implantação, faça backup antes de alterar o armazenamento.
