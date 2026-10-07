# 📖 Guia de Instalação e Uso: Assistente Tampermonkey BRK (Conectado ao Banco Real v2.0)

Este Userscript conecta sua navegação no **Google Chrome** no **Shopify Admin** diretamente ao **Banco de Dados Real do Projeto BRK** (via API Serverless Vercel `https://1025-ten.vercel.app/api/product_db`).

Ele puxa os produtos reais do catálogo (`data/stores/*.json`), com suas descrições oficiais no padrão **Modo B** (3 Atos, Tabela de Medidas, Quick Badges e Rastreio Invisível `<!-- BRK-MODO-B v1 -->`), preenchendo o editor Polaris via React Setter nativo e operando em **Modo Assistido** com pausa de 4 segundos.

---

## ⚡ Passo 1: Instalação no Chrome (Feito apenas 1 vez)

1. Certifique-se de que a extensão **Tampermonkey** está instalada no seu Google Chrome ([Link na Chrome Web Store](https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)).
2. Clique no ícone do Tampermonkey no topo do navegador e selecione **Adicionar novo script...**.
3. Apague o código padrão que aparecer e **cole o conteúdo completo** do arquivo:
   `tampermonkey/brk_assistente_shopify.user.js`
4. Vá em **Arquivo** ➔ **Salvar** (ou aperte `Ctrl + S`).
5. **Permissão de Conexão**: Na primeira vez que rodar, se o Tampermonkey exibir um aviso perguntando se permite conectar a `1025-ten.vercel.app`, clique em **Sempre Permitir neste Domínio**.
6. Pronto! O script já está ativo para as 3 lojas (`brkfishing`, `brkagro`, `brkmotors25`).

---

## 🚀 Passo 2: Como Usar Diretamente no Shopify Admin

### Opção A: Iniciar um Lote de 25 Produtos Sem Descrição (Recomendado)
1. Abra a listagem de produtos da loja no Chrome:
   👉 **BRK Fishing**: `https://admin.shopify.com/store/brkfishing/products`
2. No canto inferior direito, o painel do assistente exibirá:
   `🟢 BANCO DE DADOS BRK`
   - Total de produtos no banco
   - Contagem de produtos sem descrição
   - Botão: **`[▶️ Iniciar Lote 25 (Sem Descrição)]`**
3. Clique em **`[▶️ Iniciar Lote 25 (Sem Descrição)]`**.
4. O script consulta o banco de dados em tempo real, obtém os 25 produtos com status `SEM_DESCRICAO` da BRK Fishing e abre automaticamente o primeiro produto!

---

### Opção B: Injetar em Qualquer Produto Aberto Avulso
1. Abra qualquer página de edição de produto na Shopify (ex: `https://admin.shopify.com/store/brkfishing/products/8421653250114`).
2. O assistente identifica automaticamente o ID do produto e consulta o banco real na Vercel.
3. O painel mostrará o SKU real, Título e Status:
   - Clique em **`⚡ Injetar Modo B`** para aplicar a descrição no editor.
   - Ou clique em **`📋 Copiar HTML`** para copiar o código para a área de transferência.

---

## 🎯 Passo 3: O Fluxo no Modo Assistido

1. Quando a página do produto carrega com o lote ativo:
   - O assistente alterna o editor para o modo de código HTML (`<>`).
   - Insere a descrição Modo B completa usando o descriptor nativo do React.
   - O botão **Salvar** no topo da Shopify começa a **pulsar em verde brilhante**.
2. **Sua ação:** Clique no botão verde **Salvar** (ou tecle `Ctrl + S`).
3. Assim que você clica em Salvar:
   - O painel exibe: `⏱️ Salvo! Avançando em 4s... 3s... 2s...`
   - Após a pausa de 4 segundos, o navegador carrega automaticamente o próximo produto da fila!
4. O processo se repete com fluidez até a conclusão dos 25 produtos.

---

## 🛡️ Salvaguardas e Controles

- **Pausa e Interrupção**: Você pode clicar em `⏹️ Parar Lote` ou `⏭️ Pular/Próximo` a qualquer momento.
- **Backup Automático**: Antes de substituir qualquer texto, o script salva o HTML anterior na memória local.
- **Isolamento Total**: Apenas o campo de descrição (`body_html`) é tocado. Títulos, variantes, fotos, preços e SEO permanecem 100% intactos.
