# Central Mestre BRK - Gestão de Descrições & Vigilante Shopify Multi-Lojas

Repositório oficial de automação, auditoria, padronização visual e geração contínua de descrições em alta conversão para o ecossistema de lojas do **BRK Group**:
- 🎣 **BRK Fishing**: `12.582 SKUs` (2.265 Produtos)
- 🚜 **BRK Agro**: `5.955 SKUs` (1.328 Produtos)
- 🏁 **BRK Motors**: `6.758 SKUs` (1.512 Produtos)

---

## 🚀 Como Acessar a Central Unificada
Abra o arquivo principal diretamente no seu navegador (Chrome, Edge, etc.):
👉 **`index.html`**

A interface é **100% autônoma, responsiva e independente**, contando com **4 Abas Principais**:
1. **🛍️ Catálogo & Diagnóstico**:
   - Seletor de lojas no topo com dados reais de SKUs e varredura contínua.
   - **Sincronização em Tempo Real (Por Segundos)**: monitoramento ao vivo via API pública da Shopify que detecta produtos recém-subidos sem descrição instantaneamente.
   - Carrossel horizontal de coleções com anéis de status de integridade.
   - Modal de Produto com **Duplo Modo**:
     - *Modo B (3 Atos Alta Conversão)*: padrão autêntico BRK, ícones Font Awesome, cores suaves da loja e abertura direta sem microcards.
     - *Modo A (Preservar HTML + Fotos CDN)*: mantém texto original trocando mídias mortas da AWS por fotos CDN Shopify.
     - *Original (Quebrado/AWS)*: diagnóstico do HTML legado na loja.
   - **Injetor de Mídias do BRK Bunker (Cloudflare Worker)**: cola e distribui links de alta conversão nas 3 posições oficiais com 1 clique.
   - Botões reativos de cópia instantânea (`📋 Copiar Código HTML Shopify`) e exportação em CSV.

2. **⚡ Geração em Massa por SKU**:
   - Fila de produtos com problemas (sem descrição ou fotos quebradas).
   - Motor de correção em lote com aplicação de moldes por categoria.
   - Geração de CSV oficial pronto para importação direta no Admin da Shopify.

3. **📐 Moldes Mestres por Arquétipo**:
   - **`footwear_sandals`**: Calçados & Sandálias Boaonda (palmilha anatômica, solado antiderrapante e polímero impermeável).
   - **`tackle_boxes_storage`**: Caixas, Estojos & Organização (divisórias modulares, travas de alta pressão e polímero UV).
   - **`fishing_tackle_gear`**: Equipamentos de Pesca & Revenda (Marine Sports, Shimano, Deyu, Albatroz, etc.).
   - **`thermal_gear`**: Térmicos & Camping (Elber - isolamento de alta densidade e vedação).
   - **`uv_performance`**: Camisas de Pesca UV50+ & Linha ArmorX.
   - **`agro_field`**: Camisas & Vestuário Agro e Campo.
   - **`motors_speed`**: Jerseys & Vestuário Off-Road e Velocidade.
   - **`caps_accessories`**: Bonés Trucker & Chapéus.
   - **`cutlery_unique`**: Facas Artesanais & Cutelaria.

4. **📊 Análises & Monitoramento Diário**:
   - Diagnóstico automatizado com histórico de conformidade das 3 lojas.
   - Rastreamento de links proibidos (Google Drive, Mercado Livre, Shopee, AWS S3 antiga).
   - Histórico e repositório de download das planilhas de correções diárias.

---

## 🎨 Identidade Visual & Cores Suaves por Loja
As descrições geradas no Modo B respeitam rigorosamente a paleta suave de cada marca:
- 🎣 **BRK Fishing**: **Azul Leve** (`#0284c7` com fundo `#f0f9ff`)
- 🚜 **BRK Agro**: **Verde Leve** (`#16a34a` com fundo `#f0fdf4`)
- 🏁 **BRK Motors**: **Laranja Leve** (`#f97316` com fundo `#fff7ed`)

Todos os ícones utilizam exclusivamente a biblioteca **Font Awesome 6.5.1** vetorizada (zero emojis de sistema operacional).

---

## 📁 Estrutura do Projeto

```text
├── index.html                   # Central Mestre Interativa Unificada (v4.5)
├── build_master_index.py        # Compilador Mestre e gerador do portal
├── generate_catalog_data.py     # Coletor auditado de produtos e SKUs Shopify
├── sync_github.py               # Automação de sincronização contínua com GitHub
├── core/                        # Módulos do motor de automação
│   ├── realtime_sync.py         # Monitor de sincronização em tempo real (por segundos)
│   ├── template_engine.py       # Motor de arquétipos técnicos e narrativas
│   ├── html_builder.py          # Construtor do HTML padrão 3 Atos com Font Awesome
│   ├── html_replacer.py         # Construtor do Modo A (preserva HTML + CDN)
│   ├── daily_sentinel.py        # Orquestrador do Vigilante Diário das 08:00
│   ├── auditor.py               # Scanner de fotos quebradas e links proibidos
│   ├── batch_mass_generator.py  # Gerador de lotes por código de SKU
│   ├── image_harvester.py       # Extrator inteligente de mídias oficiais CDN
│   ├── bunker_client.py         # Cliente do Cloudflare Worker (BRK Bunker)
│   └── shopify_public_api.py    # Cliente da API pública da Shopify
└── reports/                     # Dados auditados e histórico
    ├── catalog_ui_data.json     # Catálogo completo BRK Fishing (12.582 SKUs)
    ├── brk_agro/                # Catálogo completo BRK Agro (5.955 SKUs)
    ├── brk_motors/              # Catálogo completo BRK Motors (6.758 SKUs)
    ├── daily_fixes/             # Planilhas CSV geradas diariamente
    └── historico_saude.json     # Registro temporal de métricas de saúde
```

---

## 🔄 Sincronização Contínua com o GitHub
Sempre que uma nova compilação ou melhoria é realizada, o script executa automaticamente o espelhamento e o push para este repositório:
```powershell
py -3.14 sync_github.py
```
