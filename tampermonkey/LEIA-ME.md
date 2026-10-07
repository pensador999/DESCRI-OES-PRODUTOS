# 📖 Guia de Instalação e Uso: Assistente Tampermonkey BRK (Shopify Admin)

Este Userscript conecta a **Central de Descrições BRK** diretamente à sua sessão logada no **Google Chrome** no **Shopify Admin**, aplicando descrições no padrão oficial **Modo B** (com 3 Atos, Tabela de Medidas, Quick Badges e Rastreio Invisível) sem precisar de tokens de API.

---

## ⚡ Passo 1: Instalação no Chrome (Feito apenas 1 vez)

1. Certifique-se de que a extensão **Tampermonkey** está instalada no seu Google Chrome ([Link na Chrome Web Store](https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)).
2. Clique no ícone do Tampermonkey no topo do navegador e selecione **Adicionar novo script...**.
3. Apague o código padrão que aparecer e **cole o conteúdo completo** do arquivo:
   `tampermonkey/brk_assistente_shopify.user.js`
4. Vá em **Arquivo** ➔ **Salvar** (ou aperte `Ctrl + S`).
5. Pronto! O script já está ativo para as 3 lojas (`brkfishing`, `brkagro`, `brkmotors25`).

---

## 🚀 Passo 2: Como Executar o Primeiro Lote (25 Produtos Sem Descrição)

1. Acesse o **Portal de Descrições BRK** (na Vercel https://1025-ten.vercel.app/ ou local).
2. Na loja **BRK Fishing**, clique no botão roxo:
   👉 **`⚡ Iniciar Lote Tampermonkey (25)`**
3. O portal seleciona automaticamente os **25 primeiros produtos sem descrição**, monta as narrativas em Modo B e transmite para o Tampermonkey.
4. O Chrome perguntará se deseja abrir o primeiro produto no Shopify Admin. Clique em **OK**.

---

## 🎯 Passo 3: O Fluxo no Modo Assistido

1. A página do produto abrirá no Shopify Admin (`https://admin.shopify.com/store/brkfishing/products/{id}`).
2. No canto inferior direito, você verá o painel flutuante:
   `⚡ Assistente BRK [Item 1 de 25]: ATIVO`.
3. O assistente:
   - Alterna o editor da Shopify para o modo código HTML (`<>`).
   - Insere a descrição Modo B completa com o comentário de rastreio invisível `<!-- BRK-MODO-B v1 | sku:... -->`.
   - O botão **Salvar** da Shopify começará a **pulsar em verde brilhante**.
4. **Sua única ação:** Clique no botão verde **Salvar** (ou aperte `Ctrl + S`).
5. Assim que a Shopify confirmar o salvamento:
   - O painel iniciará uma contagem regressiva suave de **4 segundos**: `⏳ Próximo produto em 4s... 3s... 2s...`
   - A aba navegará automaticamente para o produto seguinte da fila!
6. Repita o processo até concluir o lote de 25 produtos.

---

## 🛡️ Salvaguardas e Controles

- **Pausar a qualquer momento**: No painel flutuante, clique em **`⏸️ Pausar`** para interromper o avanço automático.
- **Pular Produto**: Clique em **`⏭️ Próximo`** se quiser pular o produto atual sem salvar.
- **Backup Automático**: Antes de qualquer inserção, o script salva o HTML anterior na memória local.
- **Segurança Absoluta**: Apenas o campo da descrição é modificado. Títulos, preços, estoques, variantes e fotos não sofrem qualquer alteração.
