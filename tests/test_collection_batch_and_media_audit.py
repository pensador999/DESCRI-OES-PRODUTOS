import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.product_db import (
    load_store_database,
    load_super_ofertas_audit,
    audit_live_gallery_and_variants,
    sanitize_product,
)


def test_super_ofertas_audit_data_loaded():
    audit = load_super_ofertas_audit()
    assert len(audit) >= 91, f"Expected >= 91 products in Super Ofertas audit, got {len(audit)}"

    # Iron Head 70 (7873393885250) must be present and report unlinked variant 'IT'
    iron = audit.get("7873393885250")
    assert iron is not None
    assert iron["has_unlinked_variants"] is True
    assert "IT" in iron["unlinked_variants"]
    assert iron["has_low_res_images"] is True
    assert iron["needs_media_fix"] is True


def test_brk_fishing_db_includes_all_91_super_ofertas():
    db = load_store_database("brk_fishing")
    assert db is not None
    so_list = db.get("super_ofertas") or []
    assert len(so_list) >= 91, f"Expected >= 91 products in db['super_ofertas'], got {len(so_list)}"

    # Check Iron Head 70 is indexed by ID and handle
    iron_p = db["by_id"].get("7873393885250")
    assert iron_p is not None
    assert iron_p.get("in_super_ofertas") is True

    sanitized = sanitize_product(iron_p, "brk_fishing")
    assert sanitized["in_super_ofertas"] is True
    assert sanitized["archetype_id"] == "fishing_lures"
    assert sanitized["layout_type"] == "3 Atos + Ficha Técnica"
    assert sanitized["has_official_mode_b"] is True
    assert "IT" in sanitized["media_audit"]["unlinked_variants"]
    # Ensure no clothing size guide is injected into fishing lure description
    assert '<div class="brk-size-guide">' not in sanitized["mode_b_html"]


def test_super_ofertas_media_filter_counts():
    db = load_store_database("brk_fishing")
    so_list = db["super_ofertas"]

    needs_fix = [p for p in so_list if p["media_audit"]["needs_media_fix"]]
    unlinked = [p for p in so_list if p["media_audit"]["has_unlinked_variants"]]
    dups = [p for p in so_list if p["media_audit"]["has_duplicate_images"]]
    low_res = [p for p in so_list if p["media_audit"]["has_low_res_images"]]
    criticos = [
        p for p in so_list
        if p["media_audit"]["has_unlinked_variants"] or p["media_audit"]["has_duplicate_images"]
    ]

    assert len(needs_fix) >= 80
    assert len(unlinked) >= 30
    assert len(dups) >= 20
    assert len(low_res) >= 70
    assert len(criticos) >= 40


def test_tampermonkey_script_v5_2_and_portal_collection_buttons():
    tm_path = os.path.join(BASE_DIR, "tampermonkey", "brk_assistente_shopify.user.js")
    with open(tm_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert 'const SCRIPT_VERSION = "' in code
    assert 'value="super_ofertas"' in code
    assert 'value="COLECAO_COMPLETA"' in code
    assert 'value="FOCO_ISCAS"' in code
    assert 'value="CRITICOS_FOTOS_CORES"' in code
    assert 'function renderMediaAuditAlertBox(prod)' in code
    assert 'pauseOnMediaError' in code
    assert 'brk-inp-collection' in code
    assert 'brk-prio-iscas-42' in code or 'FOCO_ISCAS' in code

    idx_path = os.path.join(BASE_DIR, "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        idx_html = f.read()
    assert 'id="btn-tm-queue"' in idx_html

    app_js_path = os.path.join(BASE_DIR, "js", "app.js")
    with open(app_js_path, "r", encoding="utf-8") as f:
        app_js = f.read()
    assert "async function sendCollectionToTampermonkey(" in app_js
    assert "function sendCustomCollectionFromPortal(" in app_js

