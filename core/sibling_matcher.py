"""
Motor Inteligente de Busca de Produtos Homólogos / Irmãos no Site (Sibling Matcher).
Permite reutilizar a estrutura, benefícios reais e especificações técnicas de produtos
semelhantes que já possuem descrição rica e homologada no catálogo da loja,
adaptando apenas o título, variante/cor e imagens do novo produto.
"""

import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional, Tuple

class SiblingMatcher:
    def __init__(self, catalog_products: Optional[List[Dict[str, Any]]] = None):
        self.catalog = catalog_products or []
        self._index_candidates()

    def set_catalog(self, catalog_products: List[Dict[str, Any]]):
        self.catalog = catalog_products
        self._index_candidates()

    def _index_candidates(self):
        """Indexa produtos que possuem descrição existente rica (> 150 caracteres de texto limpo)."""
        self.rich_candidates = []
        for p in self.catalog:
            html = p.get("original_body_html") or p.get("body_html") or ""
            clean_text = self._strip_html(html)
            if len(clean_text) >= 150:
                norm_title = self.normalize_title(p.get("title", ""))
                self.rich_candidates.append({
                    "product": p,
                    "clean_text": clean_text,
                    "norm_title": norm_title,
                    "specs": self.extract_specs_from_html(html)
                })

    @staticmethod
    def _strip_html(html: str) -> str:
        if not html:
            return ""
        text = re.sub(r'<[^>]+>', ' ', html)
        return " ".join(text.split())

    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Normaliza o título removendo variações superficiais como tamanhos,
        cores finais, códigos de SKU e conectivos.
        """
        if not title:
            return ""
        t = title.lower().strip()
        # Remover parenteses e colchetes
        t = re.sub(r'\([^\)]*\)|\[[^\]]*\]', ' ', t)
        # Remover tamanhos comuns (ex: tam g, tamanho 42, 30lbs, etc)
        t = re.sub(r'\b(tam|tamanho)\s*[:\-]?\s*([a-z0-9]+)\b', ' ', t)
        t = re.sub(r'\b(pp|p|m|g|gg|xg|xgg|exg|g1|g2|g3)\b', ' ', t)
        t = re.sub(r'\b(3[4-9]|4[0-8])\b', ' ', t)  # Numeração calçados
        # Remover sufixos de cores comuns
        cores = [
            "preto", "preta", "azul", "marinho", "vermelho", "vermelha", "verde",
            "amarelo", "amarela", "branco", "branca", "cinza", "grafite", "marrom",
            "laranja", "rosa", "bege", "bordo", "camuflado", "camuflada"
        ]
        tokens = t.split()
        filtered = [tok for tok in tokens if tok not in cores and len(tok) > 1]
        return " ".join(filtered)

    @classmethod
    def extract_specs_from_html(cls, html: str) -> List[Dict[str, str]]:
        """Extrai especificações de listas (<li>) ou tabelas (<tr><td>) no HTML existente."""
        specs = []
        if not html:
            return specs

        # 1. Procurar em <li>
        li_matches = re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL | re.IGNORECASE)
        for li in li_matches:
            clean_li = cls._strip_html(li).strip()
            if ":" in clean_li:
                parts = clean_li.split(":", 1)
                k = parts[0].strip(" -•*")
                v = parts[1].strip()
                if 2 <= len(k) <= 35 and 2 <= len(v) <= 120:
                    specs.append({"label": k, "default": v})

        # 2. Procurar em <tr> <td>
        tr_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        for tr in tr_matches:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL | re.IGNORECASE)
            if len(tds) >= 2:
                k = cls._strip_html(tds[0]).strip(" -•*:")
                v = cls._strip_html(tds[1]).strip()
                if 2 <= len(k) <= 35 and 2 <= len(v) <= 120:
                    specs.append({"label": k, "default": v})

        # Desduplicar preservando ordem
        seen = set()
        unique = []
        for s in specs:
            key = s["label"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(s)

        return unique[:8]

    def find_best_sibling(self, target_product: Dict[str, Any], min_score: float = 0.68) -> Optional[Dict[str, Any]]:
        """
        Busca o produto irmão mais semelhante que já tenha descrição rica homologada.
        Retorna um dicionário com os detalhes do irmão ou None se não atingir a pontuação mínima.
        """
        target_title = target_product.get("title", "")
        target_norm = self.normalize_title(target_title)
        target_cat = (target_product.get("category") or "").lower()
        target_vendor = (target_product.get("vendor") or "").lower()
        target_handle = target_product.get("handle") or ""

        if not target_norm or not self.rich_candidates:
            return None

        best_score = 0.0
        best_candidate = None

        target_tokens = set(target_norm.split())

        for cand in self.rich_candidates:
            cand_p = cand["product"]
            # Não comparar consigo mesmo
            if cand_p.get("handle") == target_handle:
                continue

            cand_norm = cand["norm_title"]
            cand_tokens = set(cand_norm.split())

            # 1. Similaridade por SequenceMatcher
            seq_score = SequenceMatcher(None, target_norm, cand_norm).ratio()

            # 2. Similaridade de Tokens Jaccard
            inter = len(target_tokens & cand_tokens)
            union = len(target_tokens | cand_tokens)
            jaccard_score = inter / union if union > 0 else 0.0

            # 3. Bônus por Categoria ou Vendor compartilhado
            cand_vendor = (cand_p.get("vendor") or "").lower()
            bonus = 0.0
            if target_vendor and target_vendor == cand_vendor:
                bonus += 0.08
            cand_cat = (cand_p.get("category") or "").lower()
            if target_cat and target_cat == cand_cat:
                bonus += 0.05

            final_score = min(1.0, (seq_score * 0.6 + jaccard_score * 0.4) + bonus)

            if final_score > best_score:
                best_score = final_score
                best_candidate = cand

        if best_candidate and best_score >= min_score:
            sibling_p = best_candidate["product"]
            return {
                "sibling_title": sibling_p.get("title"),
                "sibling_handle": sibling_p.get("handle"),
                "sibling_category": sibling_p.get("category"),
                "sibling_vendor": sibling_p.get("vendor"),
                "similarity_score": round(best_score, 2),
                "extracted_specs": best_candidate["specs"],
                "clean_text_sample": best_candidate["clean_text"][:250],
                "original_html": sibling_p.get("original_body_html") or sibling_p.get("body_html") or ""
            }

        return None
