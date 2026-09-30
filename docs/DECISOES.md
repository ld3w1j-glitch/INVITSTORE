# Decisões da versão 2

## Estrutura

A referência local `Chapa-do-Bairro-main(4).zip` foi inspecionada para manter o padrão Flask, módulos Python, templates HTML e arquivos estáticos. A InvitStore tem banco e regras próprios, adequados a múltiplos administradores. Não é uma atualização compatível com o banco do projeto de referência ou das versões antigas da InvitStore.

## Responsável pelo produto

O vínculo é `Product.owner_id → User.id`. A criação usa o usuário autenticado; um campo enviado pelo navegador não pode atribuir outro responsável. O principal pode administrar todo o catálogo, preservando o responsável original ao editar.

O WhatsApp é lido do perfil ao preparar a mensagem. Copiar o telefone para cada produto criaria contatos desatualizados quando o responsável mudasse de número. A relação evita esse problema.

## Pedidos e estoque

O carrinho guarda somente identificadores e quantidades na sessão assinada. A mensagem é montada com os preços atuais do banco, após validar produto, categoria, administrador, opção e estoque. Uma variação de outro produto é rejeitada.

Itens de responsáveis diferentes viram solicitações separadas. Não há um único número fixo para toda a loja.

O redirecionamento não confirma que a mensagem foi enviada nem que a compra foi concluída. Esta versão deixa a confirmação e a baixa de estoque a cargo do administrador. Reservas, pagamentos e histórico de pedidos poderão ser módulos posteriores.

## Persistência e acesso

SQLite e fotos ficam no mesmo diretório de dados, facilitando o backup de uma instalação. Hospedagem requer volume persistente e uma réplica. O banco começa vazio; o primeiro administrador escolhe suas credenciais.

Há proteção CSRF nos formulários, senhas com hash, limitação de tentativas de login, invalidação de sessões ao desativar contas ou redefinir senhas e validação do conteúdo das fotos. Essas verificações foram exercitadas nos testes; não constituem uma auditoria independente de segurança.

## Identidade e interface

Paleta baseada no manual: creme `#F6EFDF`, espresso `#3E2A1F`, cacau `#6B4A3A`, bege `#DCC9B1` e terra `#8C6A52`. A marca é o arquivo original fornecido, enquadrado em SVG. As fontes ficam no próprio projeto.

O cliente não precisa entrar. O painel funciona em desktop e celular, com envio de foto pelo dispositivo e campos para opções de produtos. As prévias incluídas usam dados temporários apenas para mostrar o layout; esses cadastros não fazem parte da instalação.

## Fontes técnicas

- [Flask](https://flask.palletsprojects.com/)
- [Flask-WTF e CSRF](https://flask-wtf.readthedocs.io/en/latest/csrf/)
- [Conversa em um clique no WhatsApp](https://faq.whatsapp.com/5913398998672934/?locale=pt_BR)
- [Persistência com volumes Railway](https://docs.railway.com/volumes/reference)
- [Lato](https://github.com/google/fonts/tree/main/ofl/lato)
- [URW Base35](https://github.com/ArtifexSoftware/urw-base35-fonts)
