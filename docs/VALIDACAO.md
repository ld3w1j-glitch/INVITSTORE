# Validação da entrega · 30/09/2026

## Resultado

**26 testes automatizados passaram**, executados com Python 3.12 em Linux e as dependências de `requirements.txt`. Também foram verificadas 14 combinações de página e largura no Chromium 133, mais a conferência final do editor no celular.

## Fluxos exercitados

- Catálogo, pesquisa e seleção de produtos sem login de cliente.
- Bloqueio de acesso administrativo sem autenticação e rejeição de formulários sem CSRF.
- Criação de produto com responsável automático; tentativa de adulterar o responsável ignorada.
- Bloqueio de edição e exclusão de produtos alheios para administradores comuns.
- Cadastro de foto real, rejeição de conteúdo que não é imagem e limpeza da foto ao excluir o produto.
- Criação e edição de variações, preservação de identificadores e rejeição de opções de outro produto.
- Rejeição de preço inválido e quantidade acima do estoque.
- Preços calculados a partir do banco, inclusive diante de valores adulterados no formulário.
- Uso do WhatsApp e do nome atualizados no perfil.
- Carrinho separado por responsável; a mensagem de cada grupo contém apenas os respectivos itens.
- Bloqueio de envio quando um item do carrinho fica indisponível; remoção do item pelo cliente.
- Criação de administradores pelo principal, desativação e invalidação das sessões.
- Permissões sobre categorias e bloqueio de exclusão de categoria em uso.
- Ordenação pelo preço exibido, incluindo opções com preço diferente do preço base.
- Persistência de contas e produtos ao reinicializar o aplicativo.
- Configuração do Railway: exige volume e mantém a chave gerada entre reinicializações.
- Redefinição de senha e limitação de tentativas de login.

## Navegador

Vitrine e páginas administrativas foram conferidas em 1440 px e 390 px; a vitrine também em 320 px. Não houve transbordamento horizontal da página nos cenários verificados. As tabelas administrativas usam rolagem própria em telas pequenas.

O teste pela interface incluiu login, menu móvel, envio de foto, adição de duas variações, salvamento de produto, atualização visual de preço ao selecionar uma opção e carrinho com dois responsáveis. Não foram registrados erros de JavaScript ou de política de conteúdo nesses fluxos.

A resposta que direciona ao WhatsApp foi interceptada para conferir número, variação, quantidade e total. Não foi enviada nenhuma mensagem. A abertura do aplicativo WhatsApp e o envio manual pelo cliente precisam ser conferidos no dispositivo real após a configuração dos números da loja.

## Inicialização

O cadastro inicial interativo foi executado em um diretório novo e repetido para confirmar que não recria contas nem altera senhas. O bootstrap de produção também foi executado duas vezes, a segunda sem a variável de senha inicial, preservando a conta criada.

Na correção 2.0.1, o servidor de produção foi iniciado duas vezes com um diretório de dados simulado como volume. Em ambas as execuções, `/health` respondeu 200, a primeira conta continuou única e a chave gerada permaneceu idêntica. A montagem real e a interface do Railway dependem da configuração do projeto hospedado.

## Limites desta verificação

O arquivo `.bat` foi preparado para Windows, mas não foi executado nativamente em Windows nesta entrega. O programa Python chamado pelo lançador foi testado. Docker e publicação em uma conta Railway não foram executados; não há URL pública desta entrega.

Os testes e as prévias usam dados temporários. O ZIP não contém banco de dados, contas, chave de sessão ou uploads desses testes. As imagens em `docs/previas/` servem apenas para mostrar a interface com cadastros de demonstração.

Para repetir os testes: instale `requirements-dev.txt` no ambiente virtual e execute `python -m pytest -q` na raiz do projeto.
