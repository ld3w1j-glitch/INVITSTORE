# InvitStore · Loja e painel administrativo

Versão 2.4.0 · Projeto Flask com catálogo público e pedidos pelo WhatsApp.

A identidade segue a InvitStore: a marca vetorial exportada do arquivo Illustrator `design/marca-invitstore-original.ai`, tons de creme, marrom e terracota, títulos Bookman e textos Lato. Logotipo, selo, símbolo e etiqueta são utilizados como SVG na loja. A versão 2.2.0 incorpora os ornamentos vetoriais do cartaz oficial: volutas, raios, estrelas, ondas, florões, cenas e objetos do cotidiano.

Os novos arquivos ficam em `app/static/img/decor/`. Eles aparecem no destaque da página inicial, nas divisões editoriais, nos grupos de categoria, na página de produto, no resumo do pedido e no rodapé. Todos são decorativos e possuem fundo transparente.

A versão 2.3.0 também permite cadastrar até 8 imagens por produto e uma imagem opcional para cada variação. A página pública exibe miniaturas, troca a foto quando o cliente seleciona uma variação e oferece ampliação ao passar o mouse sobre a imagem principal.

A versão 2.4.0 refina toda a experiência pública: carrossel editorial com controle de pausa, hierarquia visual mais forte, vitrine premium, navegação fixa, melhor leitura de produto e pedido, microinterações acessíveis e aplicação consistente dos elementos gráficos da marca.

## Começar no Windows

1. Instale **Python 3.12** pelo [site oficial](https://www.python.org/downloads/). Durante a instalação, marque **Add Python to PATH**. Python 3.11 ou superior é necessário.
2. Extraia o ZIP inteiro em uma pasta nova. Não execute dentro do ZIP nem substitua os arquivos da loja anterior.
3. Abra **start_windows.bat**. Na primeira vez, ele instala as dependências; é necessário acesso à internet.
4. No terminal, informe o nome público, e-mail, WhatsApp com DDD e uma senha de pelo menos 10 caracteres. A senha não aparece enquanto você digita. Confirme-a.
5. A loja abre em `http://127.0.0.1:5000`. Entre em `/login` com o e-mail e a senha que acabou de criar.

Mantenha o terminal aberto. Para encerrar, pressione Ctrl+C. Nas próximas execuções, as contas e os produtos são preservados. Não existe senha padrão.

**Este endereço é local.** Para o público acessar pela internet, publique a aplicação seguindo `docs/PUBLICACAO.md`. Em Railway, conecte um volume em `/data` e configure `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_WHATSAPP` e `ADMIN_PASSWORD` antes da primeira execução. A chave `SECRET_KEY` é gerada automaticamente nesse volume se você não informá-la. Esta entrega contém o código e a configuração; não inclui uma hospedagem já publicada.

## Linux e macOS

Com Python 3.11+ e suporte a `venv` instalado, execute na pasta do projeto:

```bash
sh start_linux.sh
```

O programa usa Waitress para o servidor local. A abertura automática do navegador depende do ambiente; se necessário, abra o endereço exibido no terminal.

## Primeiro cadastro

1. Em **Meu perfil**, confira seu nome público e seu WhatsApp. O nome aparece na vitrine e o telefone recebe as solicitações.
2. Em **Categorias**, cadastre os grupos de produtos.
3. Em **Produtos → Novo produto**, informe nome, descrição, categoria, preço e estoque. Escolha a imagem principal e, se desejar, adicione outros ângulos do produto.
4. Se houver opções, adicione variações como “Preto / G” ou “Natural / 500 ml”. Cada opção tem estoque e imagem próprios e pode usar o preço base ou outro preço.
5. Em **Administradores**, o administrador principal cria as contas da equipe. Cada novo administrador cadastra e gerencia os próprios produtos.

O catálogo começa vazio para receber seus produtos reais. As versões da marca no site são institucionais e não representam estoque à venda.

Há prévias da interface em `docs/previas/`, com cadastros temporários usados na revisão visual.

## Como o pedido funciona

- O cliente navega, pesquisa, filtra e monta o pedido **sem criar uma conta**.
- Ao cadastrar um produto, o sistema grava automaticamente o administrador conectado como responsável. O formulário não permite trocar esse vínculo.
- “Pedir pelo WhatsApp” prepara uma mensagem com produto, código, variação, quantidade, preço unitário e total.
- “Adicionar ao meu pedido” permite selecionar vários itens. Itens de responsáveis diferentes formam grupos separados, cada um com seu próprio botão de WhatsApp.
- O número e o nome vêm do perfil atual do responsável. Alterar o WhatsApp no perfil atualiza o destino de todos os produtos dele.
- Preço e disponibilidade são conferidos no servidor antes do redirecionamento. Valores enviados pelo navegador não substituem os valores cadastrados.
- O WhatsApp abre com a mensagem pronta. **O cliente ainda precisa enviá-la**. Frete, entrega e pagamento são combinados na conversa.

Abrir o WhatsApp não comprova uma venda. Por isso, o estoque **não é descontado automaticamente**: atualize-o no painel após confirmar a venda. Esta versão não registra pagamentos, reservas nem histórico de pedidos confirmados.

## Permissões

| Ação | Principal | Outros administradores | Visitante |
|---|---|---|---|
| Navegar e preparar pedidos | Sim | Sim | Sim |
| Criar produtos | Sim | Sim | Não |
| Editar e excluir produtos | Todos | Somente os próprios | Não |
| Criar categorias | Sim | Sim | Não |
| Editar categorias | Todas | Somente as que criou | Não |
| Criar e desativar administradores | Sim | Não | Não |
| Alterar nome e WhatsApp do próprio perfil | Sim | Sim | Não |

As categorias são compartilhadas. Desativar uma categoria retira da vitrine todos os produtos dela; o painel mostra esse aviso. Desativar um administrador oculta seus produtos e encerra suas sessões. Uma categoria com produtos não pode ser excluída.

## Fotos, banco e backup

Os dados locais ficam em `instance/`: `invitstore.db`, `uploads/` e `secret.key`. Copie a pasta inteira com a loja desligada para fazer um backup consistente. Proteja esse backup: ele contém contas e dados da loja.

As fotos aceitam JPG, PNG ou WebP, com limite de 8 MB e 20 megapixels por arquivo. O servidor verifica o conteúdo, remove metadados e salva WebP com até 1800 px. Cada produto pode ter até 8 imagens em sua galeria; as variações podem receber uma imagem opcional adicional.

Esta versão usa **SQLite**, indicada para uma única instância da aplicação. Não aponta automaticamente para PostgreSQL. Em hospedagem, banco e fotos precisam de volume persistente.

## Recuperar uma senha

Na pasta do projeto, usando o terminal e o ambiente virtual:

```bat
.venv\Scripts\python.exe -m flask --app run redefinir-senha seu@email.com
```

No Linux/macOS, troque o executável por `.venv/bin/python`. O comando solicita e confirma a nova senha e encerra as sessões anteriores. Ele exige acesso ao servidor; não é uma rota pública.

## Desenvolvimento e verificação

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes cobrem permissões, CSRF, fotos, variações, integridade dos preços, carrinho por responsável, mudanças de estoque, atualização de contatos e persistência. Consulte `docs/VALIDACAO.md` para os resultados da entrega.

Estrutura: `app/site` (loja), `app/admin` (painel), `app/auth` (acesso), `app/models` (banco), `app/services` (pedidos, validação e fotos), `app/templates` e `app/static` (interface).

Créditos da identidade fornecida: Washington Luis de Oliveira Ladeira. Licenças das fontes e respectivas origens em `licenses/`.
