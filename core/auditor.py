"""
Motor de Auditoria e Análise de Qualidade e Conversão de Descrições Shopify.
Identifica links de fotos quebradas, calcula o Score de Conversão e classifica os produtos em arquétipos.
"""

import re
import requests
from typing import Dict, Any, List, Set, Tuple
from urllib.parse import urlparse
from core.config import SCORE_WEIGHTS, HTTP_HEADERS

class CatalogAuditor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)
        self.url_cache: Dict[str, Tuple[bool, int]] = {} # url -> (is_ok, status_code)

    def check_image_url(self, url: str) -> Tuple[bool, int]:
        """
        Verifica se a URL da imagem está acessível (Status 200).
        Usa cache para evitar requisições repetidas da mesma imagem.
        """
        if not url or not url.startswith("http"):
            # Trata links relativos ou schema-less (ex: //cdn.shopify.com/...)
            if url and url.startswith("//"):
                url = "https:" + url
            else:
                return (False, 400)

        if url in self.url_cache:
            return self.url_cache[url]

        try:
            # Tenta HEAD primeiro para economizar banda
            res = self.session.head(url, timeout=5, allow_redirects=True)
            if res.status_code == 200:
                self.url_cache[url] = (True, 200)
                return (True, 200)
            elif res.status_code in [403, 405]:
                # Alguns servidores bloqueiam HEAD; tenta GET leve
                res = self.session.get(url, timeout=5, stream=True)
                is_ok = (res.status_code == 200)
                self.url_cache[url] = (is_ok, res.status_code)
                return (is_ok, res.status_code)
            else:
                self.url_cache[url] = (False, res.status_code)
                return (False, res.status_code)
        except requests.RequestException:
            self.url_cache[url] = (False, 0)
            return (False, 0)

    def extract_images(self, html_content: str) -> List[Dict[str, str]]:
        """Extrai todas as tags <img> com src e alt do HTML."""
        if not html_content:
            return []
        
        images = []
        # Regex tolerante para tags img
        img_pattern = re.compile(r'<img\s+[^>]*?src=["\']([^"\']+)["\'][^>]*?>', re.IGNORECASE)
        for match in img_pattern.finditer(html_content):
            src = match.group(1).strip()
            # Busca alt se houver
            tag_str = match.group(0)
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', tag_str, re.IGNORECASE)
            alt = alt_match.group(1) if alt_match else ""
            images.append({"src": src, "alt": alt})
        return images

    def classify_archetype(self, title: str, product_type: str = "", tags: List[str] = None) -> str:
        """
        Classifica o produto em um dos 3 Arquétipos de Negócio:
        - CUTELARIA_ARTESANAL: Facas personalizadas, lâminas, bainhas.
        - REVENDA_ACESSORIOS: Varas, carretilhas, molinetes, linhas de pesca, iscas, bonés, óculos.
        - LINHAGEM_VESTUARIO: Camisas, calças, bermudas com variações de cor/tecido.
        """
        text = f"{title} {product_type} {' '.join(tags or [])}".lower()
        
        # 1. Cutelaria e Peças Únicas
        if any(w in text for w in ["faca", "facas", "cutelaria", "bainha", "damasco", "artesanal", "afiador", "canivete", "chaira", "lâmina", "lamina"]):
            return "CUTELARIA_ARTESANAL"
            
        # 2. Equipamentos de Pesca, Acessórios e Revenda
        if any(w in text for w in [
            "vara", "molinete", "carretilha", "isca", "anzol", "chumbada", "alicate",
            "linha multifilamento", "linha monofilamento", "linha fluorocarbon",
            "boné", "bone", "chapéu", "chapeu", "óculos", "oculos", "estojo", "bolsa de pesca"
        ]):
            return "REVENDA_ACESSORIOS"
            
        # 3. Linhagens de Vestuário (Camisas, Bermudas, Proteção UV)
        if any(w in text for w in ["camisa", "camiseta", "armorx", "manga", "uv50", "uv30", "jaqueta", "bermuda", "calça", "calca", "vestuario", "dry", "baby look"]):
            return "LINHAGEM_VESTUARIO"

        # Fallback inteligente
        return "LINHAGEM_VESTUARIO" if any(w in text for w in ["masculin", "feminin", "infantil"]) else "REVENDA_ACESSORIOS"

    def audit_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza a auditoria completa de um produto.
        Retorna diagnóstico com status, score, imagens quebradas e recomendações.
        """
        title = product.get("title", "")
        handle = product.get("handle", "")
        body_html = product.get("body_html") or ""
        product_type = product.get("product_type", "")
        tags = product.get("tags") or []
        archetype = self.classify_archetype(title, product_type, tags)

        # Extração de Variantes e SKUs logo no início
        variants = product.get("variants", [])
        variants_skus = [v.get("sku") for v in variants if v.get("sku")]
        master_sku = variants_skus[0] if variants_skus else "SEM-SKU"
        if len(master_sku) > 4 and any(c.isdigit() for c in master_sku):
            base_sku_match = re.match(r'^([A-Z0-9]+?)(PP|P|M|G|GG|G1|G2|G3|[0-9]{2})?$', master_sku)
            base_sku = base_sku_match.group(1) if base_sku_match else master_sku
        else:
            base_sku = master_sku
        total_skus = len(variants_skus) if variants_skus else len(variants)
        if total_skus == 0:
            total_skus = 1

        issues: List[str] = []
        broken_images: List[str] = []
        external_images: List[str] = []
        healthy_images: List[str] = []
        
        score = 100

        # 1. Verificação de ausência de descrição
        clean_text = re.sub(r'<[^>]+>', ' ', body_html).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        word_count = len(clean_text.split()) if clean_text else 0

        is_placeholder_or_empty = (
            not body_html.strip()
            or word_count == 0
            or clean_text.lower() in ["a", "p", "br", "-", ".", "none", "null", "undefined"]
            or (word_count < 20 and not any(tag in body_html.lower() for tag in ["<p", "<div", "<table", "<ul"]))
            or word_count < 5
        )

        if is_placeholder_or_empty:
            return {
                "id": product.get("id"),
                "title": title,
                "handle": handle,
                "master_sku": base_sku,
                "variants_skus": variants_skus,
                "total_skus_count": total_skus,
                "affected_skus_count": total_skus,
                "is_out_of_standard": True,
                "standard_violations": ["Produto totalmente sem descrição ou com placeholder/caractere único."],
                "archetype": archetype,
                "status": "SEM_DESCRICAO",
                "score": 0,
                "word_count": word_count,
                "total_images": 0,
                "broken_images_count": 0,
                "external_images_count": 0,
                "issues": ["Produto cadastrado sem nenhuma descrição real."],
                "broken_urls": [],
                "recommendation": "Gerar descrição completa em 3 Atos a partir do arquétipo correspondente."
            }

        # 2. Análise de Imagens no Corpo da Descrição
        images = self.extract_images(body_html)
        for img in images:
            src = img["src"]
            is_ok, status_code = self.check_image_url(src)
            
            if not is_ok:
                broken_images.append(src)
                score += SCORE_WEIGHTS["broken_image_penalty"]
            else:
                healthy_images.append(src)
                # Verifica se é hospedagem externa vulnerável
                parsed = urlparse(src)
                if "shopify.com" not in parsed.netloc and "brkfishing.com.br" not in parsed.netloc:
                    external_images.append(src)
                    score += SCORE_WEIGHTS["external_host_penalty"]

        if broken_images:
            issues.append(f"{len(broken_images)} foto(s) quebrada(s) ou inacessível(is) no corpo da descrição.")

        if external_images:
            issues.append(f"{len(external_images)} foto(s) em servidores externos não-Shopify (risco iminente de quebra).")

        # 3. Análise de Qualidade Textual e Argumentos de Conversão
        if word_count < SCORE_WEIGHTS["min_word_count"]:
            score += SCORE_WEIGHTS["short_text_penalty"]
            issues.append(f"Texto muito raso ({word_count} palavras). Pouco persuasivo para conversão.")

        lower_body = body_html.lower()
        if archetype == "LINHAGEM_VESTUARIO":
            if not any(k in lower_body for k in ["uv50", "proteção solar", "protecao", "solar", "tecido", "respirável", "secagem"]):
                score += SCORE_WEIGHTS["missing_tech_specs"]
                issues.append("Falta destaque para tecnologias principais (UV50+, respirabilidade, secagem rápida).")
            if not any(k in lower_body for k in ["medida", "tamanho", "tabela", "guia"]):
                score += SCORE_WEIGHTS["missing_sizing"]
                issues.append("Ausência de guia/tabela de medidas para redução de devoluções.")

        # Extração das Variantes e SKUs agrupados
        variants = product.get("variants", [])
        variants_skus = [v.get("sku") for v in variants if v.get("sku")]
        master_sku = variants_skus[0] if variants_skus else "SEM-SKU"
        # Se for um SKU composto como CAX001PP, extrai o prefixo base
        if len(master_sku) > 4 and any(c.isdigit() for c in master_sku):
            base_sku_match = re.match(r'^([A-Z0-9]+?)(PP|P|M|G|GG|G1|G2|G3|[0-9]{2})?$', master_sku)
            base_sku = base_sku_match.group(1) if base_sku_match else master_sku
        else:
            base_sku = master_sku

        # Classificação do Status Final e Avaliação do "Nosso Padrão"
        score = max(0, min(100, score))
        standard_violations = []

        if broken_images:
            status = "IMAGENS_QUEBRADAS"
            standard_violations.append(f"{len(broken_images)} foto(s) com erro 404 (links quebrados).")
        elif is_placeholder_or_empty or word_count < 20:
            status = "SEM_DESCRICAO"
            standard_violations.append("Produto sem descrição real ou com texto insuficiente.")
        elif external_images:
            status = "FOTOS_EXTERNAS"
            standard_violations.append(f"{len(external_images)} foto(s) fora da CDN oficial da Shopify.")
        elif score < 75 or word_count < 60:
            status = "BAIXA_CONVERSAO"
            standard_violations.append("Texto muito raso ou sem argumentos técnicos de conversão.")
        elif len(images) > 3:
            status = "EXCESSO_FOTOS"
            standard_violations.append(f"{len(images)} fotos no corpo (o padrão é de no máximo 3 fotos).")
        else:
            status = "SAUDAVEL"

        is_out_of_standard = (status != "SAUDAVEL")
        total_skus = len(variants_skus) if variants_skus else len(variants)
        if total_skus == 0:
            total_skus = 1
        affected_skus = total_skus if is_out_of_standard else 0

        # 4. Detecção de Links Externos Proibidos (AWS S3, Drive, MercadoLivre, Shopee, etc.)
        prohibited_domains = [
            r"use-brk-images-s3\.s3\.us-east-1\.amazonaws\.com",
            r"drive\.google\.com",
            r"docs\.google\.com",
            r"mercadolivre\.com",
            r"mlstatic\.com",
            r"shopee\.com\.br",
            r"photobucket\.com",
            r"imageshack\.us",
            r"imgur\.com",
            r"dropbox\.com"
        ]
        prohibited_regex = re.compile("|".join(prohibited_domains), re.IGNORECASE)
        prohibited_links = []
        for link in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', body_html, re.IGNORECASE):
            if prohibited_regex.search(link):
                prohibited_links.append(link)

        # 5. Detecção de SKUs Órfãos / Variantes sem Código
        orphaned_variants = []
        for v in variants:
            sku_val = str(v.get("sku") or "").strip()
            if not sku_val or sku_val.lower() in ["sem-sku", "null", "undefined"]:
                orphaned_variants.append(v.get("title", "Variante Sem Nome"))

        if prohibited_links:
            issues.append(f"{len(prohibited_links)} link(s) externo(s) proibido(s) detectado(s).")
            standard_violations.append(f"{len(prohibited_links)} link(s) externo(s) não autorizado(s).")
        if orphaned_variants:
            issues.append(f"{len(orphaned_variants)} variante(s) sem código de SKU.")

        return {
            "id": product.get("id"),
            "title": title,
            "handle": handle,
            "master_sku": base_sku,
            "variants_skus": variants_skus,
            "total_skus_count": total_skus,
            "affected_skus_count": affected_skus,
            "is_out_of_standard": is_out_of_standard,
            "standard_violations": standard_violations,
            "archetype": archetype,
            "status": status,
            "score": score,
            "word_count": word_count,
            "total_images": len(images),
            "broken_images_count": len(broken_images),
            "external_images_count": len(external_images),
            "issues": issues,
            "broken_urls": broken_images,
            "prohibited_links": prohibited_links,
            "orphaned_variants": orphaned_variants,
            "recommendation": (
                "Substituir urgente por template modular e migrar fotos para Shopify CDN."
                if status in ["IMAGENS_QUEBRADAS", "FOTOS_EXTERNAS"]
                else ("Enriquecer com especificações e benefícios em 3 atos." if status == "BAIXA_CONVERSAO" else "Manter no padrão.")
            )
        }
