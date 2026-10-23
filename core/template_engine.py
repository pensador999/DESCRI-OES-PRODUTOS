"""
Motor de Moldes Mestres, Arquétipos Especializados e Extração de Especificações Técnicas.
Padrão Autêntico BRK Group (Fishing, Agro, Motors).

Arquétipos Especializados por Categoria Real:
1. uv_performance: Camisas de Pesca / Manga Longa UV50+ Dry Fit
2. agro_field: Camisetas e Vestuário Agro & Campo
3. motors_speed: Jerseys e Vestuário Trilha, Velocidade & Off-Road
4. hats_safari_outdoor: Chapéus de Pesca, Safári, Australiano com Aba 360° e Protetor de Nuca
5. caps_trucker_snapback: Bonés Trucker, Snapback e Aba Curva
6. fishing_lures: Iscas Artificiais (Superfície, Meia-Água, Fundo, Plugs, Jigs, Softs)
7. neck_gaiters_balaclavas: Bandanas, Tubenecks, Buffs e Balaclavas Tubulares Seamless
8. sun_sleeves_manguitos: Manguitos Anatômicos de Proteção Solar com Silicone no Bíceps
9. footwear_sandals_boaonda: Sandálias, Babuches, Clogs e Chinelos Ortopédicos/Antiderrapantes
10. closed_footwear_sneakers: Tênis e Calçados Fechados de Alta Tração
11. drinkware_thermo: Copos, Garrafas e Canecas Térmicas em Inox 18/8 com Vácuo
12. tackle_boxes_storage: Caixas de Pesca, Maletas, Estojos e Organização de Tralhas
13. overalls_workwear: Macacões, Jardineiras e Vestuário Operacional/Trilha
14. books_publications: Livros, Guias de Fauna/Pesca e Publicações Editoriais
15. cutlery_unique: Cutelaria, Facas Artesanais e Lâminas
16. fishing_tackle_gear: Varas, Carretilhas, Molinetes, Linhas e Alicates de Precisão

Preserva rigorosamente 100% dos dados técnicos reais da peça sem alucinar especificações.
"""

import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple

KNOWN_BRANDS = [
    'Rapala', 'Deyu', 'Marine Sports', 'Marine', 'Daisen', 'Albatroz', 
    'Boaonda', 'American Hat', 'Elber', 'Maruri', 'Daiwa', 'Shimano', 
    'Loomis', 'Monster 3X', 'Moriah', 'Kowalsky', 'VMC', 'Mustad', 
    'Crown', 'Ottoni', 'Pesca Brasil', 'Sumax', 'Saint', 'Jogá', 'Joga',
    "Cutelaria D'Avila", "D'Avila", "D'avila", 'Karandá', 'Karanda',
    'Pralana', 'Nelson Nakamura', 'Yara', 'Jackall', 'Sunline',
    'Spiderwire', 'Okuma', 'Coleman', 'CCM'
]

KNOWN_SHOPIFY_DUP_IMAGE_TOKENS = {
    '0130fa478fe94fbd808e04a745ee4a96', '02539031efdb45bf80aa2ff07750588e', '02bce54ffdae4737bb5cb3e65005a9ed', '074d5ba735b4483990428b74a35b7ed1',
    '07f53a4c219149f4ae6734d196d54620', '0900789cc8c1460abd7df610904c4b2d', '09b4d40da2274d05b2fd0c2c5d868a55', '09c44b69f2b649ef9d8231a30021d36a',
    '0b12bc26bd6d4a4da12ee35cc0d3c616', '0b6247882ff24f63a7d106240fe5bd89', '0bd070689a8f4402be998734076dd2c8', '0bd1ffe19a9d47158d0e9e1750def8cd',
    '0c5e319cca3b40f6897bf96d9577a79f', '0e23c5eea4be458e92e74f121ec48b39', '0e3d4728d00a4c92970906d3311d6408', '0fb7c8ba7f0840c6911a0aebc7d1cf5a',
    '109a04128bc948b9a56797e0f732b00f', '10d106b973e3438286b054bf3e9f5c12', '119a7881885f43eeab36697519b2affe', '123ecc4f111f41688371d047a376887c',
    '1420181cbd1043e884b6094186b0f526', '1475b5209eab42b79cde7956bb0e76ab', '1750954608038-01_masc.jpg', '1750954608038-01_masc_91379c43-6657-4f6a-9d59-f80edaabe345.jpg',
    '1750954608038-01_masc_a1e40c2a-873f-4d53-9122-870039114d3b.jpg', '1750954608038-01_masc_cae84974-db9e-4cf5-bba1-78e49197cbdf.jpg', '1750954608038-01_masc_d4332740-c512-4c78-8c0f-5e87e5c859dc.jpg', '1750956158411-01_masc.jpg',
    '1750956158411-01_masc_1fa45ffb-b5f4-4d26-879d-4a29deae6abf.jpg', '1750956158411-01_masc_2314255d-07d1-466b-bd3d-de4cd2b620a7.jpg', '1750956158411-01_masc_8efe0125-a8cc-4ce6-abe7-a3f283414190.jpg', '1750956158411-01_masc_dfe0103b-9fa8-4bdb-ba1e-4f9d440ca513.jpg',
    '1752686429164-8_frente.jpg', '1752686430113-9_costas.jpg', '1a42261505774a85820f21db66796dc9', '1b32fa89d94d46ac82a8db5f0a9b081b',
    '1b35d5d1a2e54303bc6065f224a792c3', '1f419c603ecc426b828ee12fce2d45b6', '200845a16d7441d0855fb6329afce98d', '2017048dd2444a01a1dc6c3df73a3957',
    '2139af2a6d544758920a32a55cdfb30c', '2202db9f16554b568b1c176552a25748', '22b981cd6d8545cebf8381ccb8345083', '2429e08baf0a466bb0750fedf65f3838',
    '24838a29cc8244ac8664a032f3df232a', '27b94edbeb7c450e98ee8dbc19fb41f9', '2819e7f2c7f64ef4947388c495ea5392', '2920f776fd8e4428929702b9eb8eec45',
    '2b50f7c907054a5d95898bb0ce0ed105', '2be597f4817a4d9abfd0b8d0af8bea0b', '2bfaabf2469f4b59b6af1a36419f12eb', '2e34835beffb4c6aa34f2899bf5edd91',
    '2e6e3e83159d4fcf85d1094f4179d73b', '2f20b7136d2a42ceb42cb48b4a7367a3', '2f308d8d89e4447db1eb726596554dc6', '2f5e84430f264a3c9d39062d5b940611',
    '2fc34f0b0156487fb0ce14ac31bab947', '333ecce931d743d9afc42368942a886a', '33b4b44ea9cf4be0899966e3809c95e9', '341c9efb19a44453a9993015ffb22db1',
    '360991b7830e440fa55e68926bcdf4b4', '366d55c7ea3e46aaad0d60fcd3d0f9b5', '36901243a1fe4d5bb5654529e78e183f', '3735795d965b439eb86a5b89ed4c590d',
    '37e780617282406c800fd178a5b61a7f', '388b8179206d4d98852eb1cdbcda1fd6', '39b168f6f7c54e66835cda4f45e6e3db', '3d9adeab42e543acace85e28d34079b5',
    '3e1b3c9de58943c685da0ead456752a9', '409bce9db3624834af448d3120a63c12', '43b261897af24ba3b4a103bdfc64e788', '46727814b21e45f6883a218a944d0f9a',
    '4a10d6b747254e1685c0565f2f4867df', '4b01c34c8d6e477eb6a7cdff4d7e6666', '4c2921805fcd4187b1b2039d8bf521d2', '4c510b958cce45718e74cd86389229f1',
    '4cb5be6dbd2b4618b1e7da8d55c64145', '4d79af9439ab459dbf5413881e64dd6e', '4eda9bfd52894efc9d64796c6ba6b513', '4f7c178c274a4de59c7efa679b0296da',
    '4f84e2aad02f46efbf1e68ca2a954aad', '4fcdc6f74baf485d8a3b61241e59056b', '53248c610b324174a15c5e29c37b8ae7', '54374e8640964923916a8c79166b6f1e',
    '5575f62ca4014656ab4fbc7f036a90a9', '5607730a884f4af0a4f2db6ab6e3895e', '56a03f9923464be4b38febd23f085242', '576d2723fe1342c1bfe07d2a303c869d',
    '59674c7c8efe483084a090c9a02183e9', '599a7fdfed5d4df0a9964f2bec1e0902', '59b85d0331884bbfa63b0103d1a9cb2f', '5c2cf6a5f8ee447d902760c873b81368',
    '5d33e1fbdcdd436cb9f9a9d87d292005', '5e51f4a3e2ee49ffa871fad9bcaa4fcf', '5fb20ebea1914f3090e46410fdf66b86', '617fa9e526914c898d26e0abe5878dd6',
    '63a10590d393408dbdc086bd8f1173d6', '644d0ef00c5845db9619b7bc5455d5eb', '663d68eae93847bfaa8622da60651504', '66d05fc41cae4f5ab799cb61b1041102',
    '67a247e2f67848f5af7543adf8a1fff4', '69cc449c95d148dcb271f7b5127cc57f', '6bd5f20f2f484faea8da46cb2a004485', '6c584b43b17e4708ab5a853661b19184',
    '6e540ab30fb14ed69b1b73edc500c9f1', '6e691a1ac6e048a7821b8bcf499acd13', '6f5c474f9c594489875f083a0bb177fc', '70873852b5e045e8be6cc8c3e35317d3',
    '70fdf10f6fd244f4a074997f7aed4cbc', '72b0431e143e4981af6a0e09617b261c', '738c36cd8db64a099a172242b7cdd099', '73f2a135929c42709ab16646a4f8cb8d',
    '756600c792604ae1ac5d756ff5f77199', '773234af5942435197abf66f209860e1', '78bd16a7c3744d0aac11bda274bd369a', '792d1cd7f1c648859e48a0b77253323f',
    '792fc6ff6baa495184bfb90eaf9940e1', '7ce3f9c005f34642bdd3f94b7b8b0993', '7d612095efce48e59bc0eba6a988da16', '7fc2b61c8b5c4fd29c3255b3ed8be5a0',
    '80f2837593b1469fb55b21e73b347566', '81481598901048c4bf7cd4cfc8b61548', '8262dbf88f0549ec95ef6a60e76ceb3e', '82ee07f87b934e0f9a345ba530e57a0b',
    '83df9409d1c54d3791ac88fe037050e5', '85d1baf420ae40d99ef62a94403c540b', '870ffc7c817d4d879a76ec5e4e0b4525', '87c4e0e271eb4d5cab59cb100346a8b0',
    '87e0198755514d75a106b4fcceec1870', '880019dbae7c40479a9e7d592d783225', '8b14d4f17c564a1d89b391e38e9b7a93', '8d6f9e9fe5bd48eb9bc408a08162abdb',
    '8ddd73ca7e054abaab34e962ccd07f2f', '8ef0dbfea2ae4182bcd8b1892a15c238', '8ef33820b0574209b3aec89a81331f56', '8efa6c227fb541c2b48134003438dc6d',
    '8f3324f3600945f3891f80198ab483a4', '9124809cfc1746f6afb48bfbfd86ef9a', '924d0c66d64041899728ab18771677a0', '964df29bfaf84a0abd2356c784a1d82f',
    '97065dd51b0f4957bcddb1886e6c461d', '97e753a3c4844448a3dec11c3e1c29c9', '98b58fc3cfaa4ff89a31df2d1323bd48', '9a943601f8f24f66add5fe52dade723d',
    '9aa15896d03f44f5b4ad94f6fa90af88', '9b8fe3c4edc147d2b31e1e1dcfb8f534', '9bf8e1e957a34492b41485b6a470cd98', '9c0bd95bc2904bd5961ee88314dc5383',
    '9c1284001d9944608acc2dae4a36c888', '9d8931bd154b40bebe804a1d06c99e34', '9dd8f5d344e54e87bfc2251b6b675d55', '9e42b6851079451e9cb456356529cf52',
    '9ea61be537964c43be14efb42f20cd9a', 'a00f3f91d0024158bcd065ce2025f179', 'a085713739a24f92975fa42a48c893c3', 'a0ec6f9ce03c401b948a291b7f3c8119',
    'a1ef49e2e2404cfd96f3462db4ecd911', 'a3354d559c064477a566d0399934e3b6', 'a3b3db5355344e44b9e5194a46e1af91', 'a41e2520f0334d45a52c744412166c0b',
    'a50e3d52ea2e42b08b6a8307c114e8c9', 'a5969d79260840d4859ab293178c5c75', 'a5fc231c2ee04fdebede6c7446c8d185', 'a957d576889045ad97ce8d6228895e57',
    'aabc408c343040e1986dc28b382a1b8f', 'aba6a317ae514ba7b18e77ac0610deab', 'ac5d7aac75c54e239a8ac3541d4a20bf', 'ad6c1d776939419395d0d408f843891c',
    'ad6ebca104e94248b28d2e6f2609cb97', 'ae98edd304924309b69af0881c126f89', 'b07902021382425e873c07431563bcbc', 'b12b03ea038d4cc289191d32487528d9',
    'b1560d73013547f9ad239a557e9daa80', 'b30c206c171f469792b516ba4e3d442a', 'b3a155fe185e45c9ab05f66960d09512', 'b64e144795e64b258dab792411e8fe17',
    'b7d9df5733b14850a1fb74862ab74e18', 'b847dcad60e4437787f4afebc28a45d1', 'b8f5b75cab344afbbbdfd59bcc21a6c0', 'b91380e34dfe48a98ec184d66486cb54',
    'be5534ff14a24ef79cfcd54de1a5b16e', 'bf5c9610034f4fc7839736654846ebfa', 'bf7493bde73d477f98e254fb15e42025', 'bfb14f0ae7dd4addae1d9b091bd50342',
    'bfd6a01a86a34b91acde28c3d7d6947e', 'bff288ad7be84bb4987c10741114419f', 'c14f205a2cd646e3aa09b36762639610', 'c15674b7eb9941f886f47d82df5305bc',
    'c15f012455fc4be395e4a98c0bd4e574', 'c2376731105c4cfb9b94f2517a4a179e', 'c2fe47b2142f4fafa377941743881abe', 'c42f922b43f74651859c4d41eec0f097',
    'c55f50d6bb944f7ba84d6c2c3ca4f2bb', 'c6a4654607214347b9d0f8f1df28ae02', 'c7f9037243d0404cb134f0b7c3cc47f0', 'cab17a0cccca47f2884f25efde8b8e42',
    'cb2bb07ad82347b5856bdcde10200b86', 'cb5b0db3a9e045328e683d0cc1966104', 'cf2fc9bf51d94d8b86fd7f035d46d036', 'd0ea5ec87f0349f68e70e391d09a8363',
    'd3920c717c55416794c070500ed224e4', 'd492749f64f849b08462595a1eb29f9a', 'd5222baad8da454f832a5d3fb0bedda1', 'd595a026cb0f41269f49a5ebd5374c1f',
    'd608c18612e542d8a4eb9ef532ab2bc1', 'd79ff16ced6340ef90d4e339bcb6572e', 'd930950665cb4b089277345fc4e7f8b5', 'da70e9fa00204babb2231735df758f95',
    'dba7086f487943b29eed3a58da0ef1c1', 'dea06687c3dd4a1ca2003ac0dda2a436', 'e0ac0b0e251f47538ae061cb0cc01f86', 'e1e9b05ce7ab482ea29f16337499084b',
    'e306d28dd244493b8b38527d66ac3527', 'e32e9b28ebda4b09a456e0ba8c0c2524', 'e65169c353154aaeb557d806ae1cf296', 'ecfc45c9c4cb4d108d9657bc1c1d83db',
    'ef03305e5d674c4c902f05d58d2682aa', 'ef99a23a13544c738802a6be70c0ba0a', 'f06206dd58594f51b9472c9acc58d9bf', 'f0ca4b7d9883484a8b1bbf70f66d6f51',
    'f12c325d6ccb415f8bdb6f9c23470d5f', 'f256198473974784b27181ba18ff70cd', 'f364e233d28f4c0b9fe312316b0f0ec2', 'f399744e19924d3f8fdeaf6e50ec2f2b',
    'f409ce350e5542b180c80390d388edab', 'f685a6ebe7e4479ca59d2492b3f59db6', 'f7542336b44e468e8c3e57c5e263ac42', 'f78f55cb63f64aa3b59a0980b93165e0',
    'f9ce986a86e543f8b6d288714093825a', 'fa6530264a684924a8f261eb8fc73011', 'fb17213952f84ecca5ec7b02ec3304be', 'fb9def04c9174ae3a29a572694315f4d',
    'fbb9f22bb404418fb41e242a94b8ae21', 'fedcc88e79524f51ae0e6900a6dc7730', 'ff03f85c460f4aac930bcfab9e761b7c', 'ff854bc26d574957bca986fe0049263f',
    'whgf96p_7db6902a-a660-49dd-b94f-647a3bf0246a.png',
    '1747241373161-1_26c28b00-27db-4da9-8465-dc316f7886f0.jpg', '1747241373161-1_cc8c87ae-aeed-42ac-9b10-bdb82369d1ec.jpg',
    '1755280665111-1_3b0361b6-672f-4044-8f71-0911820337c4.jpg', '1755280665111-1_5af80f26-4bae-4242-a3ad-be4c0d5045e7.jpg', '1755280665111-1_e01d7d43-c885-441b-b8fa-043c9dd8cb71.jpg',
    '1755280683947-3_80d04785-8d46-4bb1-bc46-8a44295b6d31.jpg', '1755280683947-3_a8c3df9c-ad14-4a09-9547-b2e5452869a7.jpg', '1755280683947-3_ad5e5a9c-9510-404a-a7a5-20cb91ef3c0c.jpg', '1755280683947-3_b388179b-8844-461d-a560-059062537b35.jpg',
    '1755284793848-1_4021911a-3767-4643-8444-34a1afe5cf4e.jpg', '1755284793848-1_60240d1d-1967-4eb3-9c41-d246c26ba3b9.jpg', '1755284793848-1_adb77146-3446-4eb5-a03d-8828daca9720.jpg', '1755284793848-1_bc281fea-5771-4942-9d77-1cc92bd3615c.jpg',
    '1755636679693-pot65.jpg', '7krczor.jpg', 'rtu1vnr.jpg', 'rqkfmex.jpg', 'w5jqror.jpg', 'tmen4pb.jpg', 'tl9jr33.jpg', 'xt9vq0l.jpg', 'ktvyxmy.jpg', 'p9ppfas.jpg',
    '4kb8nwd_022211e7-1083-4c11-9578-30954a77b8d3.jpg', '4kb8nwd_2314bf0e-1301-4b17-bee5-545f804ee29e.jpg', '4kb8nwd_a3d3b756-697e-4d2a-847d-0272f6d71109.jpg',
    'e8wk7re_48fc67d5-74da-4df9-9558-5b8698aa1399.jpg', 'greuip3_47e2aa4f-1ab1-4ba2-ae8c-3a7433f2b029.png',
    'kgiuj0f_80121748-8cee-4de4-9a6f-6338b35ba416.jpg', 'klzuhmq_dd9122c3-cfe8-437e-ae45-fd0cae28d089.png', 'klzuhmq_e7991a94-4037-4980-a461-d1a53bf92d1e.png',
    'kt1l6ns_1faf788f-8538-4fe2-a506-79da7ed99af9.png', 'kt1l6ns_6447884f-5824-4cb4-a73a-402386a8aefe.png', 'kt1l6ns_858acd0f-41ba-4a8b-a12c-09839a70d414.png', 'kt1l6ns_b73b6cc5-58f0-4e5b-aeb0-ee4cb22e182f.png',
    'kzjgobf_d2e54349-0e18-4cf0-87c1-f97cebccb1b4.jpg', 'ocrgtf9_ea874bce-967a-4c06-b13d-ed5f478f5009.png', 'u6vsxm0_d30ba6e8-7e65-4c01-82ce-e529e1ff199c.png',
    'xhffzmt_4e9fc008-3542-4a5a-ac49-fcd54553cb5a.png', 'xhffzmt_c878cf46-ae8b-4791-8de4-aebcfa2b7b2b.png', 'xhffzmt_ce259353-5bef-424a-a04d-834a6e5f83b6.png',
    'xvsvhpi_bb1ceb7d-16d9-4e9c-86f8-f0aa35be0b5d.png',
}


class TemplateEngine:
    def __init__(self):
        self.known_brands = KNOWN_BRANDS
        self.templates = {
            # 1. Camisas UV Performance
            "uv_performance": {
                "id": "uv_performance",
                "name": "Camisas UV50+ Performance & Pesca",
                "fa_icon": "fa-solid fa-shirt",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["camisa", "pesca", "uv", "manga longa", "dry", "solar", "fishing"],
                "default_tagline": "Máxima Proteção Solar e Respirabilidade Ativa no Ar Livre",
                "act1": {
                    "tag": "Design & Identidade",
                    "fa_icon": "fa-solid fa-palette",
                    "title": "ESTAMPA EM ALTA DEFINIÇÃO E MODELAGEM ANATÔMICA",
                    "desc_tmpl": "Desenvolvida para pescadores e entusiastas do ar livre, a {title} combina visual marcante com corte que proporciona liberdade total de movimentos durante os arremessos e manobras."
                },
                "act2": {
                    "tag": "Performance & Conforto",
                    "fa_icon": "fa-solid fa-sun",
                    "title": "PROTEÇÃO SOLAR UV50+ COM SECAGEM ULTRA RÁPIDA",
                    "desc_tmpl": "Confeccionada em tecido tecnológico de absorção instantânea de suor, bloqueia até 98% dos raios UVA e UVB, mantendo a sensação de frescor e conforto térmico mesmo sob sol intenso o dia todo."
                },
                "act3": {
                    "tag": "Durabilidade & Acabamento",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COSTURAS PLANAS REFORÇADAS E ACABAMENTO PREMIUM",
                    "desc_tmpl": "Acabamento de alto padrão com costuras planas anti-atrito, caimento anatômico no dorso e ombros para total liberdade de movimentos, além de punhos anatômicos que mantêm o ajuste firme e não laceiam."
                },
                "base_specs": [
                    {"label": "Prazo de Produção", "default": "10 dias úteis"},
                    {"label": "Composição", "default": "90% Poliéster 10% Elastano"},
                    {"label": "Tecido", "default": "XTech Pro"},
                    {"label": "Tecnologia", "default": "Secagem Rápida, Tecido Leve, Proteção Solar"},
                    {"label": "Modelagem", "default": "Anatômica e confortável"},
                    {"label": "Proteção", "default": "Proteção UV50+ (não sai na lavagem)"},
                ],
                "care_tips": "Lavar à mão ou em máquina no ciclo suave com sabão neutro. Não usar amaciante nem alvejante à base de cloro. Secar à sombra (dispensa uso de ferro de passar)."
            },

            # 2. Agro & Campo
            "agro_field": {
                "id": "agro_field",
                "name": "Força, Campo & Tradição",
                "fa_icon": "fa-solid fa-tractor",
                "theme_color": "#15803d",
                "theme_bg": "#f0fdf4",
                "category_keywords": ["agro", "campo", "rural", "camiseta", "fazenda", "trator", "algodao"],
                "default_tagline": "Resistência para o Campo e Estilo Autêntico para Qualquer Momento",
                "act1": {
                    "tag": "Origem & Estilo",
                    "fa_icon": "fa-solid fa-wheat-awn",
                    "title": "ORGULHO RURAL COM VISUAL CONTEMPORÂNEO",
                    "desc_tmpl": "A {title} celebra a identidade do homem e da mulher do campo com estampas exclusivas de alta durabilidade e caimento equilibrado para todas as ocasiões."
                },
                "act2": {
                    "tag": "Conforto Térmico",
                    "fa_icon": "fa-solid fa-seedling",
                    "title": "TOQUE MACIO E RESPIRAÇÃO NATURAL DO TECIDO",
                    "desc_tmpl": "Produzida com matéria-prima selecionada que garante sensação agradável sobre a pele, excelente respirabilidade e resistência ideal para enfrentar longas jornadas com conforto."
                },
                "act3": {
                    "tag": "Resistência & Acabamento",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "GOLA COM REFORÇO OMBRO A OMBRO E COSTURA DUPLA",
                    "desc_tmpl": "Estrutura robusta desenvolvida para manter a forma e a cor vivas mesmo após sucessivas lavagens, sem deformar ou desbotar."
                },
                "base_specs": [
                    {"label": "Composição", "default": "Algodão Premium com toque aveludado"},
                    {"label": "Gola", "default": "Gola redonda com reforço canelado e fita ombro a ombro"},
                    {"label": "Costura", "default": "Pesponto duplo reforçado nas barras e mangas"},
                    {"label": "Toque", "default": "Macio, anti-pilling (não cria bolinhas)"},
                    {"label": "Uso Recomendado", "default": "Trabalho rural, eventos do agronegócio e dia a dia"}
                ],
                "care_tips": "Lavar com cores semelhantes. Não alvejar. Secar ao ar livre e passar em temperatura média pelo avesso para preservar a estampa intacta."
            },

            # 3. Motors & Off-Road
            "motors_speed": {
                "id": "motors_speed",
                "name": "Trilha, Velocidade & Off-Road",
                "fa_icon": "fa-solid fa-motorcycle",
                "theme_color": "#e11d48",
                "theme_bg": "#fff1f2",
                "category_keywords": ["jersey", "moto", "cross", "off-road", "trilha", "speed", "velocidade"],
                "default_tagline": "Aerodinâmica e Ventilação Máxima para Trilhas e Pistas",
                "act1": {
                    "tag": "Visual & Identidade",
                    "fa_icon": "fa-solid fa-gauge-high",
                    "title": "GRAFISMOS VIBRANTES SUBLIMADOS DE ALTA RESOLUÇÃO",
                    "desc_tmpl": "Projetada para os apaixonados por adrenalina e velocidade, a {title} se destaca pelas cores vivas e identidade forte nas pistas e trilhas."
                },
                "act2": {
                    "tag": "Ventilação & Aerodinâmica",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "TECIDO MICROPERFURADO COM TROCA TÉRMICA CONTÍNUA",
                    "desc_tmpl": "Painéis estratégicos que aceleram o fluxo de ar, permitindo usar protetores e coletes sem acúmulo excessivo de calor ou peso de umidade."
                },
                "act3": {
                    "tag": "Resistência a Impactos",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "CORTE TRASEIRO ALONGADO E PUNHOS ELÁSTICOS",
                    "desc_tmpl": "A modelagem mais longa na parte traseira impede que a peça saia de dentro da calça durante a pilotagem severa, proporcionando ajuste firme e seguro."
                },
                "base_specs": [
                    {"label": "Tecido", "default": "Poliéster esportivo ventilado de alta tenacidade"},
                    {"label": "Corte Traseiro", "default": "Cauda alongada tipo Drop-tail para melhor encaixe na calça"},
                    {"label": "Punhos", "default": "Elásticos de compressão suave que não prendem a circulação"},
                    {"label": "Sublimação", "default": "Cores ultra pigmentadas que não desbotam com lama e sol"}
                ],
                "care_tips": "Após a trilha ou pista, remover o excesso de barro com água antes da lavagem. Não lavar a seco nem utilizar ferro sobre as áreas sublimadas."
            },

            # 4. Chapéus de Pesca / Safári / Australiano (Novo Padrão D2C Oficial BRK)
            "hats_safari_outdoor": {
                "id": "hats_safari_outdoor",
                "name": "Chapéus de Pesca, Safári & Outdoor",
                "layout_format": "d2c_headwear",
                "fa_icon": "fa-solid fa-hat-cowboy-side",
                "theme_color": "#d97706",
                "theme_bg": "#fffbeb",
                "category_keywords": ["chapeu", "chapéu", "safari", "safári", "australiano", "pescador", "nuca", "palha"],
                "default_tagline": "Proteção Solar 360° UV50+, Cordão Anti-Vento, Produto Premium & Caixa BRK",
                "details_grid": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg",
                        "title": "Aba 360° UV50+",
                        "desc": "Aba circular ampla com costuras reforçadas, bloqueando os raios solares diretos no rosto, orelhas e pescoço com máxima cobertura."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg",
                        "title": "Cordão Jugular Anti-Vento",
                        "desc": "Ajuste seguro sob o queixo com trava regulável, mantendo o chapéu firme mesmo sob rajadas de vento e navegação rápida."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg",
                        "title": "Protetor de Nuca Integrado",
                        "desc": "Cobertura estendida para a nuca que previne queimaduras solares durante longas jornadas sob sol intenso."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg",
                        "title": "Tecido Respirável & Leve",
                        "desc": "Construção de secagem rápida com ilhoses de ventilação lateral para dissipação imediata de calor e sensação de frescor contínuo."
                    }
                ],
                "info_characteristics": [
                    "Copa anatômica com ilhoses laterais que garantem circulação de ar constante.",
                    "Aba larga circular de 360° com fator de proteção UV50+ permanente.",
                    "Cordão jugular com trava ajustável de segurança contra quedas e vento forte.",
                    "Protetor de nuca para proteção solar total na região posterior do pescoço.",
                    "Tecido tecnológico leve de secagem ultra rápida e alta resistência ao desgaste."
                ],
                "info_care": [
                    "Lavar à mão com água fria e sabão neutro.",
                    "Não lavar em máquina e não torcer para preservar a estrutura da aba.",
                    "Secar estendido à sombra em superfície plana.",
                    "Não usar alvejantes, amaciantes ou produtos à base de cloro.",
                    "Guardar sem dobrar a aba estruturada para manter o caimento original."
                ],
                "split_sections": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/13-Tags.webp?v=1785788893",
                        "title": "PRODUTO PREMIUM BRK",
                        "highlight": "Cada chapéu BRK é desenvolvido pensando na proteção de quem enfrenta longas jornadas ao ar livre.",
                        "p1": "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem padrão de proteção solar certificado.",
                        "p2": "Construído com materiais leves e resistentes, oferece o máximo de conforto térmico para pescarias e trabalho sob sol forte."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/CAIXA-BRK.webp?v=1785788895",
                        "title": "ENTREGA SEGURA BRK",
                        "highlight": "A sua experiência começa antes mesmo de abrir a caixa.",
                        "p1": "O chapéu é enviado em embalagem protegida BRK, projetada para evitar deformações na aba durante o transporte.",
                        "p2": "Seu novo chapéu chega pronto para encarar o sol com proteção e estilo incomparáveis."
                    }
                ],
                "act1": {
                    "tag": "Aba 360° & Cobertura",
                    "fa_icon": "fa-solid fa-hat-cowboy-side",
                    "title": "PROTEÇÃO SOLAR PANORÂMICA DE ROSTO, ORELHAS E NUCA",
                    "desc_tmpl": "Projetado para longas horas sob sol intenso nas pescarias e expedições, o(a) {title} oferece cobertura circular ampla que evita queimaduras solares e reduz a fadiga visual."
                },
                "act2": {
                    "tag": "Conforto & Fixação",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "CORDÃO JUGULAR COM TRAVA AJUSTÁVEL ANTI-VENTO",
                    "desc_tmpl": "Equipado com cordão ajustável com presilha de travamento no queixo, garantindo que o chapéu permaneça firme mesmo durante a navegação em alta velocidade ou rajadas de vento."
                },
                "act3": {
                    "tag": "Ventilação & Secagem",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TECIDO LEVE COM ILHOSES DE RESPIRAÇÃO",
                    "desc_tmpl": "Estrutura maleável e respirável que dissipa o calor da cabeça, não retém umidade e pode ser dobrado com facilidade para transporte na mochila ou tralha."
                },
                "base_specs": [
                    {"label": "Modelo da Aba", "default": "Aba larga 360° reforçada com costuras de sustentação"},
                    {"label": "Proteção Solar", "default": "Fator UV50+ bloqueador de radiação solar nociva"},
                    {"label": "Fixação", "default": "Cordão jugular com regulador de pressão tipo tanca"},
                    {"label": "Ventilação", "default": "Ilhoses laterais para circulação e troca térmica"},
                    {"label": "Embalagem de Envio", "default": "Embalagem protetora personalizada BRK"}
                ],
                "care_tips": "Lavar à mão com sabão neutro e água fria. Não torcer a aba para não deformar a estrutura. Secar à sombra."
            },

            # 5. Bonés Trucker & Aba Curva (Novo Padrão D2C Oficial BRK)
            "caps_trucker_snapback": {
                "id": "caps_trucker_snapback",
                "name": "Bonés Trucker & Snapback",
                "layout_format": "d2c_headwear",
                "fa_icon": "fa-solid fa-hat-baseball",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["bone", "boné", "trucker", "snapback", "aba curva", "aba reta", "viseira"],
                "default_tagline": "Aba Moldável, Interno em Tear, Produto Premium & Entrega Segura na Caixa BRK",
                "details_grid": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg",
                        "title": "Aba Moldável",
                        "desc": "Aba estruturada com diversas costuras e moldável, garantindo durabilidade e proteção extra contra o sol."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg",
                        "title": "Interno em Tear",
                        "desc": "Acabamento interno em tear com costuras reforçadas, pensado para aguentar longas jornadas de pesca e uso outdoor."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg",
                        "title": "Etiqueta BRK de Qualidade",
                        "desc": "Etiqueta BRK aplicada com acabamento premium, garantindo autenticidade e padrão de qualidade rigoroso."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg",
                        "title": "Design Exclusivo",
                        "desc": "Arte exclusiva BRK inspirada na vida ao ar livre, para você se destacar em qualquer ambiente."
                    }
                ],
                "info_characteristics": [
                    "Copa estruturada estilo trucker, com frente firme e tela traseira que favorece a ventilação.",
                    "Aba moldável com costuras reforçadas, oferecendo conforto e proteção para o rosto e os olhos.",
                    "Tamanho único com regulagem traseira, se ajustando com precisão à maioria dos formatos de cabeça.",
                    "Ideal para pesca esportiva, atividades ao ar livre, trabalho no campo e uso no dia a dia.",
                    "Acabamento interno pensado para máximo conforto mesmo em longas jornadas de uso contínuo."
                ],
                "info_care": [
                    "Não lave o boné na máquina e não utilize água quente.",
                    "Para limpeza, use um pano macio levemente úmido com sabão neutro nas áreas sujas.",
                    "Retire o excesso de sabão com outro pano levemente úmido apenas com água.",
                    "Deixe secar à sombra, em superfície plana, longe de fontes diretas de calor.",
                    "Não utilize alvejante, não passe a ferro e não leve à secadora."
                ],
                "split_sections": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/13-Tags.webp?v=1785788893",
                        "title": "PRODUTO PREMIUM BRK",
                        "highlight": "Cada boné BRK é desenvolvido pensando no pescador que vive a pesca esportiva intensamente.",
                        "p1": "As etiquetas exclusivas BRK reforçam a autenticidade do produto e garantem que você está usando um item de alta performance.",
                        "p2": "Da escolha dos materiais ao acabamento final, tudo é pensado para entregar conforto, durabilidade e estilo em qualquer pescaria."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/CAIXA-BRK.webp?v=1785788895",
                        "title": "ENTREGA SEGURA BRK",
                        "highlight": "A sua experiência começa antes mesmo de abrir a caixa.",
                        "p1": "O boné é enviado em embalagem protegida e personalizada BRK, pensado para chegar até você em perfeitas condições.",
                        "p2": "Assim, seu novo boné de pesca chega pronto para encarar a próxima aventura, seja na beira do rio, na represa ou em alto mar."
                    }
                ],
                "act1": {
                    "tag": "Aba Moldável & Copa",
                    "fa_icon": "fa-solid fa-hat-baseball",
                    "title": "ABA MOLDÁVEL COM COSTURAS REFORÇADAS E COPA ESTRUTURADA",
                    "desc_tmpl": "O {title} destaca-se pela frente firme e acabamento com costuras reforçadas, mantendo o formato clássico trucker intacto e oferecendo proteção superior contra o sol."
                },
                "act2": {
                    "tag": "Interno em Tear & Ventilação",
                    "fa_icon": "fa-solid fa-wind",
                    "title": "ACABAMENTO INTERNO EM TEAR E TELA TRASEIRA RESPIRÁVEL",
                    "desc_tmpl": "Construção interna resistente em tear com carneira macia e tela traseira que garante circulação constante de ar para evitar acúmulo de suor."
                },
                "act3": {
                    "tag": "Autenticidade & Envio",
                    "fa_icon": "fa-solid fa-box",
                    "title": "ETIQUETAS OFICIAIS BRK E ENVIO EM CAIXA PROTETORA EXCLUSIVA",
                    "desc_tmpl": "Autenticidade garantida por etiquetas de alto padrão e envio em caixa rígida personalizada BRK para chegar impecável sem amassar."
                },
                "base_specs": [
                    {"label": "Modelo da Copa", "default": "Trucker clássico com lateral e traseira em tela respirável"},
                    {"label": "Aba", "default": "Aba curva estruturada e moldável com diversas costuras de reforço"},
                    {"label": "Fechamento", "default": "Snapback regulável de alta resistência (tamanho único ajustável)"},
                    {"label": "Acabamento Interno", "default": "Tear reforçado com carneira acolchoada anti-suor"},
                    {"label": "Embalagem de Envio", "default": "Caixa personalizada protetora BRK (anti-deformação)"}
                ],
                "care_tips": "Limpar com pano macio levemente úmido e sabão neutro. Não mergulhar a copa em água nem lavar em máquina para manter a estrutura e curvatura intactas."
            },

            # 6. Iscas Artificiais
            "fishing_lures": {
                "id": "fishing_lures",
                "name": "Iscas Artificiais & Alta Atratividade",
                "fa_icon": "fa-solid fa-fish-fins",
                "theme_color": "#0ea5e9",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["isca", "iscas", "plug", "jig", "frog", "soft", "meia-água", "superfície", "superficie", "popper", "stick", "twitch", "crankbait", "minnow", "spinnerbait"],
                "default_tagline": "Nado Ultra Realista, Rattling Irresistível e Garatéias Afiadas a Laser",
                "act1": {
                    "tag": "Ação & Nado Errático",
                    "fa_icon": "fa-solid fa-fish-fins",
                    "title": "NADO REALISTA QUE ESTIMULA O ATAQUE DE PREDADORES",
                    "desc_tmpl": "Desenvolvida com hidrodinâmica refinada, a {title} produz vibrações e movimentação errática na água, provocando ataques ferozes por agressividade e territorialidade."
                },
                "act2": {
                    "tag": "Sonoridade & Balanceamento",
                    "fa_icon": "fa-solid fa-bell",
                    "title": "SISTEMA DE RATTLING COM ESFERAS SONORAS INTERNAS",
                    "desc_tmpl": "Possui esferas calibradas que emitem frequências sonoras atrativas a longas distâncias, além de concentrar o peso no centro de gravidade para arremessos longos e precisos."
                },
                "act3": {
                    "tag": "Poder de Fisgada",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "GARATÉIAS DE ALTA RESISTÊNCIA E PINTURA HOLOGRÁFICA",
                    "desc_tmpl": "Armada com garatéias afiadas quimicamente para penetração instantânea na boca dos predadores, combinada a acabamento com cores holográficas ultra reflexivas."
                },
                "base_specs": [
                    {"label": "Ação do Trabalho", "default": "Trabalho atrativo de superfície/meia-água com nado provocante"},
                    {"label": "Garatéias", "default": "Aço carbono reforçado afiadas quimicamente"},
                    {"label": "Sistema Sonoro", "default": "Rattling interno com esferas sonoras vibratórias"},
                    {"label": "Corpo", "default": "Polímero ABS virgem reforçado imune a mordidas severas"},
                    {"label": "Peixes Indicados", "default": "Tucunaré, Robalo, Traíra, Dourado, Black Bass e predadores esportivos"}
                ],
                "care_tips": "Após uso em água salobra ou salgada, lavar em água doce corrente e secar completamente antes de guardar no estojo."
            },

            # 7. Bandanas, Tubenecks, Buffs e Balaclavas
            "neck_gaiters_balaclavas": {
                "id": "neck_gaiters_balaclavas",
                "name": "Bandanas, Tubenecks & Balaclavas",
                "fa_icon": "fa-solid fa-mask-face",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["bandana", "balaclava", "tubeneck", "buff", "mascara de protecao", "máscara de proteção", "gaiter"],
                "default_tagline": "Barreira Solar UV50+, Tecido Seamless Tubular e Conforto Respiratório",
                "act1": {
                    "tag": "Proteção Facial & Nuca",
                    "fa_icon": "fa-solid fa-mask-face",
                    "title": "ESCUDO COMPLETO CONTRA SOL, VENTO, MOSQUITOS E POEIRA",
                    "desc_tmpl": "O(a) {title} envolve o pescoço e a face com barreira física e fator UV permanente, protegendo a pele durante pescarias embarcadas, trilhas e pilotagem."
                },
                "act2": {
                    "tag": "Construção Seamless",
                    "fa_icon": "fa-solid fa-feather",
                    "title": "TECIDO ELÁSTICO TUBULAR SEM COSTURA ANTI-ATRITO",
                    "desc_tmpl": "Estrutura elástica com microfibra respirável de alta elasticidade que se molda confortavelmente ao rosto sem pinicar, apertar ou deixar marcas de pressão."
                },
                "act3": {
                    "tag": "Versatilidade de Uso",
                    "fa_icon": "fa-solid fa-arrows-spin",
                    "title": "MÚLTIPLAS FORMAS DE USO EM QUALQUER AVENTURA",
                    "desc_tmpl": "Pode ser utilizado como máscara facial, protetor de pescoço, faixa de cabeça, capuz ou gorro, secando instantaneamente com o suor ou respingos d'água."
                },
                "base_specs": [
                    {"label": "Proteção Solar", "default": "Fator UV50+ bloqueador permanente de radiação"},
                    {"label": "Construção", "default": "Tubular inteiriço sem costuras (Seamless anti-atrito)"},
                    {"label": "Elasticidade", "default": "Multidirecional 4-Way Stretch com memória de forma"},
                    {"label": "Respirabilidade", "default": "Tecido microperfurado que facilita a respiração e fala"},
                    {"label": "Tamanho", "default": "Único anatômico adaptável a qualquer formato de cabeça"}
                ],
                "care_tips": "Lavar à mão com sabão neutro. Seca em minutos no varal e não necessita de ferro de passar."
            },

            # 8. Manguitos de Proteção Solar
            "sun_sleeves_manguitos": {
                "id": "sun_sleeves_manguitos",
                "name": "Manguitos de Proteção Solar UV50+",
                "fa_icon": "fa-solid fa-hand-holding-hand",
                "theme_color": "#0284c7",
                "theme_bg": "#f0f9ff",
                "category_keywords": ["manguito", "manguitos", "sleeve", "manga avulsa"],
                "default_tagline": "Proteção UV50+ Anatômica com Silicone Antiderrapante no Bíceps",
                "act1": {
                    "tag": "Proteção Solar Anatômica",
                    "fa_icon": "fa-solid fa-hand-holding-hand",
                    "title": "COBERTURA TOTAL DOS BRAÇOS COM PRATICIDADE",
                    "desc_tmpl": "Desenvolvido para oferecer máxima proteção solar UV50+ para os braços, o(a) {title} é essencial para pesca, ciclismo e atividades outdoor, substituindo o protetor solar com conforto."
                },
                "act2": {
                    "tag": "Fixação Antiderrapante",
                    "fa_icon": "fa-solid fa-grip",
                    "title": "ELÁSTICO DE SILICONE NO BÍCEPS QUE NÃO DESLIZA",
                    "desc_tmpl": "Possui faixa interna de silicone na extremidade superior que impede que a manga escorregue pelo braço durante os movimentos de arremesso, pedalada ou corrida."
                },
                "act3": {
                    "tag": "Conforto Térmico & Compressão",
                    "fa_icon": "fa-solid fa-bolt",
                    "title": "COMPRESSÃO SUAVE E DISSIPAÇÃO TÉRMICA CONTÍNUA",
                    "desc_tmpl": "Tecido tecnológico com elastano que reduz a fadiga muscular e dissipa o calor rapidamente, mantendo os braços frescos e protegidos o dia inteiro."
                },
                "base_specs": [
                    {"label": "Proteção Solar", "default": "Fator UV50+ permanente certificado"},
                    {"label": "Composição", "default": "Poliamida com Elastano de toque aveludado e flexível"},
                    {"label": "Fixação Superior", "default": "Borda com fita interna de silicone antiderrapante no bíceps"},
                    {"label": "Secagem", "default": "Tecnologia Dry Fit com evaporação instantânea de suor"},
                    {"label": "Conteúdo da Embalagem", "default": "1 Par de Manguitos (braço direito e esquerdo)"}
                ],
                "care_tips": "Lavar com água fria e sabão neutro. Não usar amaciante nem alvejante. Secar à sombra."
            },

            # 9. Sandálias, Chinelos, Babuches e Clogs Boaonda
            "footwear_sandals_boaonda": {
                "id": "footwear_sandals_boaonda",
                "name": "Sandálias, Chinelos & Babuches Boaonda",
                "fa_icon": "fa-solid fa-shoe-prints",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["sandalia", "sandália", "chinelo", "boaonda", "babuche", "clog", "slide", "pantufa", "crocs", "papete"],
                "default_tagline": "Palmilha Anatômica Anti-Impacto e Solado Antiderrapante para Embarcações",
                "act1": {
                    "tag": "Ergonomia & Conforto",
                    "fa_icon": "fa-solid fa-shoe-prints",
                    "title": "PALMILHA ANATÔMICA COM AMORTECIMENTO ANTI-IMPACTO",
                    "desc_tmpl": "Projetada para garantir descanso prolongado aos pés, a {title} alivia a pressão nos calcanhares e articulações em longos dias de pescaria e caminhada."
                },
                "act2": {
                    "tag": "Aderência & Drenagem",
                    "fa_icon": "fa-solid fa-water",
                    "title": "SOLADO ANTIDERRAPANTE COM CANAIS DE DRENAGEM",
                    "desc_tmpl": "Ranhuras de alta tração que garantem passos firmes e seguros em decks molhados de barcos, pedras e bordas de piscina."
                },
                "act3": {
                    "tag": "Material Impermeável",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TERMOMOLDADO IMPERMEÁVEL QUE NÃO RETÉM ODORES",
                    "desc_tmpl": "Confeccionada em polímero nobre leve, macio e 100% à prova d'água, secando instantaneamente e facilitando a higienização."
                },
                "base_specs": [
                    {"label": "Material do Cabedal", "default": "EVA / Termoplástico nobre Boaonda macio e flexível"},
                    {"label": "Palmilha", "default": "Anatômica anti-impacto (alívio para esporão e fascite)"},
                    {"label": "Solado", "default": "Borracha antiderrapante com canais de escoamento de água"},
                    {"label": "Resistência", "default": "100% impermeável e imune a deformações térmicas"},
                    {"label": "Indicação de Uso", "default": "Embarcações, pesqueiros, praia, piscina e uso casual"}
                ],
                "care_tips": "Lavar com sabão neutro e água corrente. Não expor ao sol direto intenso para preservar o elastômero."
            },

            # 10. Tênis & Calçados Fechados
            "closed_footwear_sneakers": {
                "id": "closed_footwear_sneakers",
                "name": "Tênis & Calçados Fechados",
                "fa_icon": "fa-solid fa-socks",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["tenis", "tênis", "sapato", "botina", "sneaker", "calcado fechado", "calçado fechado"],
                "default_tagline": "Estrutura Firme, Cabedal Respirável e Solado de Alta Tração",
                "act1": {
                    "tag": "Estabilidade & Suporte",
                    "fa_icon": "fa-solid fa-socks",
                    "title": "ESTRUTURA REFORÇADA COM ENCAIXE ANATÔMICO SEGURO",
                    "desc_tmpl": "O {title} entrega estabilidade e firmeza para longas jornadas de trabalho ou aventura, protegendo os pés contra atritos e irregularidades do solo."
                },
                "act2": {
                    "tag": "Amortecimento & Ventilação",
                    "fa_icon": "fa-solid fa-cloud",
                    "title": "ENTRESOLA MACIA E CABEDAL COM CIRCULAÇÃO DE AR",
                    "desc_tmpl": "Sistema de amortecimento que reduz o cansaço nas pernas, aliado a materiais que evitam o aquecimento excessivo e a umidade interna."
                },
                "act3": {
                    "tag": "Tração Segura",
                    "fa_icon": "fa-solid fa-shoe-prints",
                    "title": "SOLADO DE ALTA RESISTÊNCIA À ABRASÃO",
                    "desc_tmpl": "Desenvolvido com compostos resistentes ao desgaste com travas de aderência para diversos tipos de terrenos urbanos e rurais."
                },
                "base_specs": [
                    {"label": "Cabedal", "default": "Material respirável com reforços laterais estruturais"},
                    {"label": "Fechamento", "default": "Cadarço ajustável com passadores reforçados"},
                    {"label": "Palmilha", "default": "Conforto anatômico com espuma de alta densidade"},
                    {"label": "Solado", "default": "Borracha de alta tração antiderrapante"},
                    {"label": "Uso Recomendado", "default": "Caminhada, dia a dia, trabalho rural e atividades ao ar livre"}
                ],
                "care_tips": "Limpar com pano úmido e sabão neutro. Secar à sombra em local ventilado."
            },

            # 11. Copos, Garrafas e Canecas Térmicas
            "drinkware_thermo": {
                "id": "drinkware_thermo",
                "name": "Copos, Garrafas & Térmicos",
                "fa_icon": "fa-solid fa-mug-hot",
                "theme_color": "#0891b2",
                "theme_bg": "#ecfeff",
                "category_keywords": ["copo", "garrafa", "caneca", "cantil", "termico", "térmico", "cooler", "elber", "geladeira"],
                "default_tagline": "Retenção Térmica a Vácuo em Aço Inox 18/8 com Abridor Integrado na Tampa",
                "act1": {
                    "tag": "Retenção Térmica a Vácuo",
                    "fa_icon": "fa-solid fa-snowflake",
                    "title": "PAREDE DUPLA EM AÇO INOXIDÁVEL COM ISOLAMENTO TÉRMICO A VÁCUO",
                    "desc_tmpl": "Projetado com parede dupla em aço inoxidável 18/8 e isolamento térmico a vácuo, o(a) {title} preserva sua bebida gelada por horas sob sol intenso ou quente nas manhãs frias, mantendo o sabor original da primeira à última gota."
                },
                "act2": {
                    "tag": "Tampa com Abridor em Inox",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TAMPA COM VEDAÇÃO EM SILICONE E ABRIDOR DE GARRAFAS BRK INTEGRADO",
                    "desc_tmpl": "Equipado com tampa removível em polímero livre de BPA com anel de vedação em silicone anti-respingos, bocal anatômico e abridor de garrafas em aço inox gravado BRK acoplado diretamente no topo da tampa."
                },
                "act3": {
                    "tag": "Arte Exclusiva & Zero Condensação",
                    "fa_icon": "fa-solid fa-droplet-slash",
                    "title": "REVESTIMENTO TEXTURIZADO EXCLUSIVO BRK E PAREDE QUE NÃO TRANSPIRA",
                    "desc_tmpl": "Revestimento externo texturizado em alta definição com arte exclusiva BRK e base inferior em aço inox escovado. O isolamento a vácuo impede a condensação externa: o copo não sua, mantendo a pegada firme e seca."
                },
                "base_specs": [
                    {"label": "Material", "default": "Aço Inoxidável 18/8 (Grau Alimentício atóxico livre de BPA)"},
                    {"label": "Isolamento Térmico", "default": "Parede dupla com vácuo térmico de alta eficiência (zero condensação)"},
                    {"label": "Tampa & Recurso Extra", "default": "Tampa com vedação em silicone e abridor de garrafas em aço inox integrado"},
                    {"label": "Acabamento Externo", "default": "Revestimento texturizado premium anti-deslizante com arte exclusiva BRK e base em inox"},
                    {"label": "Eficiência Térmica", "default": "Mantém bebidas geladas ou quentes por horas com máxima conservação"}
                ],
                "care_tips": "Lavar com detergente neutro e esponja macia. Não levar ao micro-ondas nem ao congelador."
            },

            # 12. Caixas de Pesca & Organização
            "tackle_boxes_storage": {
                "id": "tackle_boxes_storage",
                "name": "Caixas, Estojos & Organização",
                "fa_icon": "fa-solid fa-box-archive",
                "theme_color": "#1d4ed8",
                "theme_bg": "#eff6ff",
                "category_keywords": ["caixa de pesca", "caixa pesca", "estojo", "maleta", "organizador", "bolsa de pesca", "tubo de vara"],
                "default_tagline": "Estrutura Reforçada e Compartimentação Inteligente para sua Tralha",
                "act1": {
                    "tag": "Organização & Espaço",
                    "fa_icon": "fa-solid fa-box-archive",
                    "title": "DIVISÓRIAS MODULARES E COMPARTIMENTAÇÃO INTELIGENTE",
                    "desc_tmpl": "Projetada para acomodar iscas, anzóis, chumbadas e equipamentos com total organização, a {title} permite ajustar o espaço interno de acordo com a sua necessidade."
                },
                "act2": {
                    "tag": "Segurança & Travamento",
                    "fa_icon": "fa-solid fa-lock",
                    "title": "TRAVAS DUPLAS REFORÇADAS ANTI-ABERTURA",
                    "desc_tmpl": "Equipada com fechos de alta pressão que garantem travamento firme e seguro, impedindo aberturas acidentais mesmo durante impactos e movimentação intensa na embarcação."
                },
                "act3": {
                    "tag": "Proteção & Durabilidade",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "POLÍMERO VIRGEM DE ALTA RESISTÊNCIA COM PROTEÇÃO UV",
                    "desc_tmpl": "Construção robusta resistente a quedas, choques mecânicos e à degradação solar, preservando suas tralhas protegidas da água e do sol por muito mais tempo."
                },
                "base_specs": [
                    {"label": "Material", "default": "Polipropileno virgem de alto impacto com proteção UV"},
                    {"label": "Divisórias", "default": "Removíveis e reposicionáveis sob medida"},
                    {"label": "Travas", "default": "Sistema duplo reforçado de alta pressão"},
                    {"label": "Vedação", "default": "Resistente a respingos d'água e poeira"},
                    {"label": "Aplicação", "default": "Organização de tralhas em barcos, caiaques, pesqueiros e camping"}
                ],
                "care_tips": "Lavar periodicamente com água doce após uso em ambiente salino e secar antes de fechar."
            },

            # 13. Macacões & Jardineiras
            "overalls_workwear": {
                "id": "overalls_workwear",
                "name": "Macacões, Jardineiras & Operacional",
                "fa_icon": "fa-solid fa-vest",
                "theme_color": "#475569",
                "theme_bg": "#f8fafc",
                "category_keywords": ["macacao", "macacão", "jardineira", "jardineiras", "salopete", "wader"],
                "default_tagline": "Proteção Integral, Alças Reguláveis e Bolsos Utilitários de Alta Resistência",
                "act1": {
                    "tag": "Proteção Integral & Robustez",
                    "fa_icon": "fa-solid fa-vest",
                    "title": "COBERTURA COMPLETA CONTRA ABRASÃO E SUJEIRA",
                    "desc_tmpl": "Projetado para trabalhos intensos, trilhas ou operações rurais, o(a) {title} oferece proteção de corpo inteiro com visual imponente e funcional."
                },
                "act2": {
                    "tag": "Mobilidade & Ajuste",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "ALÇAS REGULÁVEIS E ARTICULAÇÃO LIVRE",
                    "desc_tmpl": "Possui fechamentos laterais e alças com fivelas de engate rápido que permitem regulagem milimétrica para conforto em agachamentos e movimentos amplos."
                },
                "act3": {
                    "tag": "Bolsos Utilitários",
                    "fa_icon": "fa-solid fa-box-open",
                    "title": "COMPARTIMENTAÇÃO PRÁTICA PARA FERRAMENTAS E ACESSÓRIOS",
                    "desc_tmpl": "Equipado com múltiplos bolsos reforçados para acomodar ferramentas, celulares e equipamentos com segurança e acesso rápido."
                },
                "base_specs": [
                    {"label": "Material", "default": "Tecido de alta tenacidade com costuras duplas e triplas"},
                    {"label": "Alças", "default": "Reguláveis com engate rápido e elástico de suporte"},
                    {"label": "Bolsos", "default": "Bolsos frontais, laterais e traseiros reforçados"},
                    {"label": "Fechamento", "default": "Zíper resistente ou botões de pressão de alta pressão"},
                    {"label": "Uso Recomendado", "default": "Operacional, campo, oficinas, trilhas e atividades pesadas"}
                ],
                "care_tips": "Lavar com água fria e sabão neutro. Não alvejar. Secar à sombra."
            },

            # 14. Livros & Publicações
            "books_publications": {
                "id": "books_publications",
                "name": "Livros, Guias & Publicações",
                "fa_icon": "fa-solid fa-book-open",
                "theme_color": "#7c3aed",
                "theme_bg": "#f5f3ff",
                "category_keywords": ["livro", "livros", "guia", "cartilha", "revista", "publicacao", "colorir"],
                "default_tagline": "Conteúdo Exclusivo, Educação Ambiental e Valorização da Fauna",
                "act1": {
                    "tag": "Conteúdo & Conhecimento",
                    "fa_icon": "fa-solid fa-book-open",
                    "title": "IMERSÃO NO UNIVERSO DA PESCA E DA NATUREZA",
                    "desc_tmpl": "O {title} traz conteúdo rico e envolvente sobre a fauna, técnicas de pesca e preservação, conectando leitores de todas as idades ao universo do ar livre."
                },
                "act2": {
                    "tag": "Qualidade Editorial",
                    "fa_icon": "fa-solid fa-palette",
                    "title": "IMPRESSÃO EM ALTA DEFINIÇÃO E PAPEL DE ALTA GRAMATURA",
                    "desc_tmpl": "Produzido com acabamento gráfico de alta qualidade, ilustrações detalhadas e páginas resistentes que valorizam a leitura e atividades lúdicas."
                },
                "act3": {
                    "tag": "Coleção & Presente",
                    "fa_icon": "fa-solid fa-gift",
                    "title": "EXCELENTE OPÇÃO PARA PRESENTEAR E COLECIONAR",
                    "desc_tmpl": "Uma obra indispensável para a biblioteca de amantes da pesca esportiva e da vida ao ar livre, estimulando a curiosidade e o aprendizado."
                },
                "base_specs": [
                    {"label": "Formato", "default": "Editorial impresso com encadernação de alta qualidade"},
                    {"label": "Acabamento", "default": "Capa colorida com laminação e papel especial resistente"},
                    {"label": "Tema Principal", "default": "Pesca esportiva, natureza, fauna brasileira e recreação"},
                    {"label": "Idioma", "default": "Português"},
                    {"label": "Público Indicado", "default": "Amantes do ar livre, pescadores, jovens e famílias"}
                ],
                "care_tips": "Armazenar em local seco e arejado, protegido de umidade e luz solar direta."
            },

            # 15. Cutelaria & Facas
            "cutlery_unique": {
                "id": "cutlery_unique",
                "name": "Cutelaria & Peças Artesanais",
                "fa_icon": "fa-solid fa-utensils",
                "theme_color": "#475569",
                "theme_bg": "#f8fafc",
                "category_keywords": ["faca", "cutelaria", "lamina", "bainha", "churrasco", "artesanal", "aco"],
                "default_tagline": "Forja Artesanal, Retenção Excepcional de Fio e Nobreza",
                "act1": {
                    "tag": "Lâmina & Geometria",
                    "fa_icon": "fa-solid fa-utensils",
                    "title": "AÇO TRATADO TERMICAMENTE PARA CORTE PRECISO E DURÁVEL",
                    "desc_tmpl": "Construída com precisão e excelente equilíbrio de peso, a {title} proporciona cortes limpos, firmes e suaves no churrasco, no campo ou na pescaria."
                },
                "act2": {
                    "tag": "Empunhadura & Ergonomia",
                    "fa_icon": "fa-solid fa-gem",
                    "title": "EMPUNHADURA ANATÔMICA DE ALTA FIRMEZA E SEGURANÇA",
                    "desc_tmpl": "Projetada para oferecer pegada firme, ergonômica e confortável durante o manuseio contínuo, unindo acabamento refinado e alta durabilidade."
                },
                "act3": {
                    "tag": "Bainha & Proteção",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "ACOMPANHA BAINHA PROTETORA SOB MEDIDA",
                    "desc_tmpl": "Proteção segura para transporte na cintura ou na tralha e conservação do fio da lâmina, com costura reforçada e travamento firme."
                },
                "base_specs": [
                    {"label": "Material da Lâmina", "default": "Aço Inoxidável / Especial com tratamento térmico de alta dureza"},
                    {"label": "Empunhadura", "default": "Anatômica de alta aderência com fixação reforçada"},
                    {"label": "Acabamento & Fio", "default": "Afiação de precisão com acabamento acetinado de alta retenção de fio"},
                    {"label": "Acompanhamento", "default": "Bainha protetora sob medida com passador para cinto"}
                ],
                "care_tips": "Lavar manualmente com água e lado macio da esponja logo após o uso. Secar imediatamente com pano limpo e seco antes de guardar na bainha."
            },

            # 16. Equipamentos de Pesca & Revenda (Varas, Carretilhas, Molinetes)
            "fishing_tackle_gear": {
                "id": "fishing_tackle_gear",
                "name": "Equipamentos de Pesca & Revenda",
                "fa_icon": "fa-solid fa-gear",
                "theme_color": "#4338ca",
                "theme_bg": "#eef2ff",
                "category_keywords": ["vara", "carretilha", "molinete", "linha", "anzol", "alicate", "passagua", "passaguá"],
                "default_tagline": "Engenharia de Precisão e Alta Performance para Pesca Esportiva",
                "act1": {
                    "tag": "Engenharia & Precisão",
                    "fa_icon": "fa-solid fa-gear",
                    "title": "MECÂNICA BALANCEADA PARA ALTO DESEMPENHO",
                    "desc_tmpl": "Construído com componentes de engenharia refinada, o(a) {title} oferece arremessos precisos, sensibilidade máxima no trabalho da isca e funcionamento suave."
                },
                "act2": {
                    "tag": "Força & Controle",
                    "fa_icon": "fa-solid fa-hand-fist",
                    "title": "RESISTÊNCIA SOB TRAÇÃO E CONTROLE PROGRESSIVO",
                    "desc_tmpl": "Projetado para suportar esforço extremo nas brigas com grandes exemplares, mantendo tração firme e confiabilidade absoluta na linha."
                },
                "act3": {
                    "tag": "Durabilidade & Acabamento",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COMPONENTES TRATADOS CONTRA CORROSÃO",
                    "desc_tmpl": "Materiais selecionados de alta dureza com revestimento resistente à água doce e salinidade, garantindo longa vida útil e preservação dos mecanismos."
                },
                "base_specs": [
                    {"label": "Categoria", "default": "Equipamento de Precisão para Pesca Esportiva"},
                    {"label": "Estrutura", "default": "Liga reforçada de baixo peso e alta rigidez estrutural"},
                    {"label": "Mecânica", "default": "Componentes de precisão com rolamentos selados"},
                    {"label": "Aplicação", "default": "Pesca esportiva em rios, lagos, pesqueiros e mar aberto"},
                    {"label": "Origem / Distribuição", "default": "Produto original com procedência e garantia"}
                ],
                "care_tips": "Após uso em água salgada, lavar levemente com água doce corrente, secar e aplicar óleo lubrificante nos pontos móveis recomendados."
            },

            # 17. Chapéus Country, Feltro, Pralana & Cowboy (Novo Padrão D2C Oficial BRK)
            "hats_country_cowboy": {
                "id": "hats_country_cowboy",
                "name": "Chapéus Country, Feltro, Pralana & Cowboy",
                "layout_format": "d2c_headwear",
                "fa_icon": "fa-solid fa-hat-cowboy",
                "theme_color": "#854d0e",
                "theme_bg": "#fefce8",
                "category_keywords": ["feltro", "pralana", "american hat", "karanda", "karandá", "country", "cowboy", "pantaneiro", "lã", "veludo", "marcatto"],
                "default_tagline": "Elegância Rústica, Copa Estruturada e Acabamento Premium em Couro e Fivela",
                "details_grid": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/eQxQuY7.jpg",
                        "title": "Aba Larga Estruturada",
                        "desc": "Formato clássico com curvatura marcante e acabamento impecável, unindo tradição, imponência e proteção solar no campo."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/k2bupYT.jpg",
                        "title": "Carneira Interna Confortável",
                        "desc": "Faixa interna com toque macio e anatômico, oferecendo fixação firme e confortável na cabeça sem marcar a testa."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/BYAO1Oj.jpg",
                        "title": "Fita & Acabamento Premium",
                        "desc": "Banda decorativa exclusiva com detalhe refinado, reforçando a autenticidade e o visual rústico elegante."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/cjeqbhc.jpg",
                        "title": "Estrutura Nobre & Firme",
                        "desc": "Matéria-prima nobre de alta densidade que preserva a forma da copa e a curvatura da aba mesmo com uso contínuo."
                    }
                ],
                "info_characteristics": [
                    "Copa alta estruturada e moldada no legítimo estilo western / campo.",
                    "Aba larga de presença marcante que proporciona excelente sombra e proteção.",
                    "Carneira interna acolchoada para conforto prolongado em cavalgadas e eventos.",
                    "Fita externa com acabamento nobre e identidade autêntica do homem e da mulher do campo.",
                    "Ideal para rodeios, feiras agropecuárias, lida na fazenda e dia a dia sertanejo."
                ],
                "info_care": [
                    "Limpar delicadamente com escova de cerdas macias sempre no sentido das fibras.",
                    "Evitar contato direto com chuva intensa ou umidade excessiva.",
                    "Armazenar sempre apoiado pela copa ou em suporte adequado para não desformar a aba.",
                    "Nunca dobrar, amassar ou deixar exposto no interior de veículos sob sol forte.",
                    "Em caso de umidade leve, deixe secar naturalmente à sombra em local ventilado."
                ],
                "split_sections": [
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/13-Tags.webp?v=1785788893",
                        "title": "PRODUTO PREMIUM BRK",
                        "highlight": "A tradição e o orgulho do campo em cada detalhe artesanal.",
                        "p1": "Desenvolvido com rigor técnico para quem valoriza a autêntica vida sertaneja.",
                        "p2": "Estrutura nobre, acabamento de precisão e caimento perfeito para cavalgadas e ocasiões especiais."
                    },
                    {
                        "img": "https://cdn.shopify.com/s/files/1/0628/1445/3826/files/CAIXA-BRK.webp?v=1785788895",
                        "title": "ENTREGA SEGURA NA CAIXA",
                        "highlight": "A sua experiência começa antes mesmo de abrir a caixa.",
                        "p1": "O chapéu é embalado com proteção reforçada contra amassados para preservar 100% da sua modelagem original.",
                        "p2": "Receba sua peça pronta para o uso, com aba e copa perfeitamente alinhadas."
                    }
                ],
                "act1": {
                    "tag": "Copa & Estrutura",
                    "fa_icon": "fa-solid fa-hat-cowboy",
                    "title": "COPA CONFORMADA E ABA ESTRUTURADA DE ALTA RETENÇÃO",
                    "desc_tmpl": "Produzido com modelagem clássica que preserva as linhas autênticas do estilo country, o(a) {title} conta com copa firme e aba com retenção de formato para uso prolongado no campo e em eventos."
                },
                "act2": {
                    "tag": "Estilo & Nobreza",
                    "fa_icon": "fa-solid fa-gem",
                    "title": "BANDINHA EM COURO COM DETALHES REFINADOS",
                    "desc_tmpl": "Destaque para o acabamento impecável ao redor da copa com bandinha decorativa e fivela metálica de precisão, conferindo elegância, imponência e robustez à peça."
                },
                "act3": {
                    "tag": "Conforto & Encaixe",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "CARNEIRA INTERNA CONFORTÁVEL COM AJUSTE ANATÔMICO",
                    "desc_tmpl": "Interior equipado com carneira acolchoada anti-suor que garante encaixe macio, estável e confortável na cabeça ao longo de todo o dia, sem apertar."
                },
                "base_specs": [
                    {"label": "Material Principal", "default": "Feltro 100% Lã / Fibra Nobre Especial de Alta Densidade"},
                    {"label": "Formato da Copa", "default": "Tradicional Country Gota / Clássica Conformada"},
                    {"label": "Carneira Interna", "default": "Espuma Acolchoada de Alto Conforto e Toque Macio"},
                    {"label": "Acabamento Externo", "default": "Bandinha exclusiva em couro com fivela/passador metálico"},
                    {"label": "Embalagem de Envio", "default": "Caixa rígida protetora especial (anti-deformação)"}
                ],
                "care_tips": "Limpar delicadamente com escova de cerdas macias no sentido das fibras do feltro. Evitar umidade excessiva e guardar sempre apoiado pela copa."
            },

            # 18. Camisas Work, Botão & Sarja Utilitária
            "shirts_button_work": {
                "id": "shirts_button_work",
                "name": "Camisas Work, Botão & Sarja Utilitária",
                "fa_icon": "fa-solid fa-shirt",
                "theme_color": "#15803d",
                "theme_bg": "#f0fdf4",
                "category_keywords": ["work", "camisa work", "camisa safari", "camisa sarja", "camisa de botao", "camisa botao", "camisa de botão", "camisa militar", "manga curta social", "manga longa sarja", "sarja", "operacional", "camisa lisa"],
                "default_tagline": "Resistência Operacional, Abotoamento Clássico e Bolsos Utilitários de Alta Tenacidade",
                "act1": {
                    "tag": "Visual & Solidez",
                    "fa_icon": "fa-solid fa-shirt",
                    "title": "TECIDO RESISTENTE DE COR SÓLIDA E CAIMENTO PROFISSIONAL",
                    "desc_tmpl": "Desenvolvida para máxima durabilidade no trabalho pesado ou no expediente diário, a {title} apresenta visual clássico e sóbrio em tecido encorpado, sem estampas espalhafatosas."
                },
                "act2": {
                    "tag": "Fechamento & Gola",
                    "fa_icon": "fa-solid fa-square-check",
                    "title": "ABOTOAMENTO FRONTAL CLÁSSICO E COLARINHO ESTRUTURADO",
                    "desc_tmpl": "Com fechamento integral por botões de alta tenacidade reforçados em costura em 'X', oferece ajuste prático, alinhamento alinhado e gola firme que mantém a postura durante toda a jornada."
                },
                "act3": {
                    "tag": "Pala Traseira & Costuras",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "COSTURAS TRIPLAS REFORÇADAS E PALA TRASEIRA ANATÔMICA",
                    "desc_tmpl": "Construída com pesponto reforçado nas áreas de maior tração, pala traseira anatômica com pregas de conforto e modelagem pensada para o trabalho pesado e ampla movimentação dos braços."
                },
                "base_specs": [
                    {"label": "Fechamento Frontal", "default": "Botões reforçados aplicados com costura em 'X'"},
                    {"label": "Colarinho / Gola", "default": "Colarinho tradicional estruturado com entretela de sustentação"},
                    {"label": "Bolsos Frontais", "default": "Dois bolsos utilitários no peito com lapela protetora"},
                    {"label": "Composição do Tecido", "default": "Algodão / Sarja de Alta Densidade resistente ao atrito"},
                    {"label": "Modelagem", "default": "Confortável com folga estratégica para ampla mobilidade nos braços"}
                ],
                "care_tips": "Lavar em água fria com sabão neutro. Não usar alvejantes à base de cloro. Secar à sombra e passar em temperatura média."
            },

            # 19. Calças & Bermudas Táticas / Cargo / Pesca
            "pants_cargo_tactical": {
                "id": "pants_cargo_tactical",
                "name": "Calças & Bermudas Táticas / Cargo / Pesca",
                "fa_icon": "fa-solid fa-vest",
                "theme_color": "#334155",
                "theme_bg": "#f8fafc",
                "category_keywords": ["calca", "calça", "calças", "bermuda", "bermudas", "shorts", "short", "ripstop", "tactical", "cargo"],
                "default_tagline": "Resistência Anti-Rasgo Ripstop, Cós Anatômico e Bolsos Cargo Utilitários",
                "act1": {
                    "tag": "Resistência & Anti-Rasgo",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "TECIDO RIPSTOP REFORÇADO CONTRA ATRITO E VEGETAÇÃO",
                    "desc_tmpl": "Projetada para suportar a lida no campo, trilhas e pescarias, o(a) {title} é confeccionado em tecido com trama ripstop que impede a propagação de rasgos e perfurações."
                },
                "act2": {
                    "tag": "Ajuste & Firmeza",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "CÓS ANATÔMICO COM PASSADORES REFORÇADOS",
                    "desc_tmpl": "Estrutura pensada para o movimento, oferecendo encaixe firme na cintura e passadores largos compatíveis com cintos táticos e coldres utilitários."
                },
                "act3": {
                    "tag": "Capacidade de Carga",
                    "fa_icon": "fa-solid fa-box-open",
                    "title": "BOLSOS CARGO MULTIFUNCIONAIS COM FECHAMENTO SEGURO",
                    "desc_tmpl": "Diversos bolsos com lapela distribuídos estrategicamente para acomodar canivetes, celular, alicate de pesca e ferramentas com rápido acesso."
                },
                "base_specs": [
                    {"label": "Modelagem", "default": "Tática Operacional / Cargo com reforço no cavalo e joelhos"},
                    {"label": "Cós e Fechamento", "default": "Botão de pressão reforçado e zíper com passadores largos para cinto"},
                    {"label": "Compartimentação", "default": "Múltiplos bolsos multifuncionais (cargo laterais, faca e traseiros)"},
                    {"label": "Tecido", "default": "Ripstop de alta tenacidade com acabamento repelente a sujeira"},
                    {"label": "Uso Indicado", "default": "Trabalho operacional, campo, pesca, trilhas e atividades táticas"}
                ],
                "care_tips": "Lavar com sabão neutro em ciclo delicado. Secar à sombra. Não alvejar."
            },

            # 20. Aromatizantes Automotivos & Cuidados
            "accessories_car_care": {
                "id": "accessories_car_care",
                "name": "Aromatizantes Automotivos & Cuidados",
                "fa_icon": "fa-solid fa-spray-can-sparkles",
                "theme_color": "#0d9488",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["aromatizante", "cheirinho", "aroma", "fragrancia", "fragrância", "difusor", "aromatizador", "little trees", "carro", "automotivo"],
                "default_tagline": "Perfume Marcante, Eliminação de Odores e Sensação Prolongada de Frescor",
                "act1": {
                    "tag": "Aroma & Frescor",
                    "fa_icon": "fa-solid fa-spray-can-sparkles",
                    "title": "PERFUME ENVOLVENTE E NEUTRALIZAÇÃO EFICAZ DE ODORES",
                    "desc_tmpl": "O {title} transforma o interior do veículo ou ambiente com essências selecionadas, eliminando odores desagradáveis e promovendo agradável sensação de limpeza."
                },
                "act2": {
                    "tag": "Difusão & Durabilidade",
                    "fa_icon": "fa-solid fa-clock",
                    "title": "TECNOLOGIA DE LIBERAÇÃO CONTÍNUA E PROLONGADA",
                    "desc_tmpl": "Desenvolvido para liberar a fragrância de forma homogênea e estável, garantindo semanas de ação perfumada constante sem perder a intensidade inicial."
                },
                "act3": {
                    "tag": "Praticidade & Estilo",
                    "fa_icon": "fa-solid fa-car",
                    "title": "DESIGN COMPACTO COM SUSPENSÃO PRÁTICA NO RETROVISOR INTERNO",
                    "desc_tmpl": "Formato leve e discreto pensado para fácil suspensão no retrovisor interno ou pequenos ambientes, perfumando a cabine sem ocupar espaço no painel."
                },
                "base_specs": [
                    {"label": "Função Principal", "default": "Aromatizador e neutralizador de odores automotivos e ambientes"},
                    {"label": "Formato de Difusão", "default": "Liberação gradual contínua e homogênea da fragrância"},
                    {"label": "Durabilidade Estimada", "default": "Ação perfumada prolongada de longa duração"},
                    {"label": "Modo de Uso", "default": "Suspensão prática no retrovisor interno ou pequenos espaços"},
                    {"label": "Indicação", "default": "Carros, caminhonetes, escritórios, armários e pequenos ambientes"}
                ],
                "care_tips": "Pendurar livremente evitando contato direto e contínuo com painéis plásticos e revestimentos de couro."
            },

            # 21. Acessórios, Chaveiros & Adesivos
            "accessories_general": {
                "id": "accessories_general",
                "name": "Acessórios, Chaveiros & Adesivos",
                "fa_icon": "fa-solid fa-key",
                "theme_color": "#64748b",
                "theme_bg": "#f8fafc",
                "category_keywords": ["chaveiro", "adesivo", "adesivos", "sticker", "pin", "patch", "emblema"],
                "default_tagline": "Identidade Marcante, Alta Durabilidade e Acabamento de Precisão",
                "act1": {
                    "tag": "Identidade & Estilo",
                    "fa_icon": "fa-solid fa-tag",
                    "title": "DESIGN EXCLUSIVO E IDENTIDADE VISUAL MARCANTE",
                    "desc_tmpl": "O(A) {title} traz detalhes refinados e acabamento de alto nível, perfeito para personalizar suas tralhas, chaves, veículos e equipamentos."
                },
                "act2": {
                    "tag": "Resistência & Durabilidade",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "MATERIAIS DE ALTA RESISTÊNCIA CONTRA DESGASTE",
                    "desc_tmpl": "Confeccionado com matéria-prima resistente a atrito, intempéries e raios UV, preservando o brilho e as cores por muito mais tempo."
                },
                "act3": {
                    "tag": "Praticidade & Fixação",
                    "fa_icon": "fa-solid fa-check",
                    "title": "ACABAMENTO SEGURO E FÁCIL APLICAÇÃO",
                    "desc_tmpl": "Projetado para encaixe seguro ou aderência firme sobre superfícies lisas, resistindo à poeira e umidade sem soltar."
                },
                "base_specs": [
                    {"label": "Categoria", "default": "Acessórios e Itens Colecionáveis Originais"},
                    {"label": "Material", "default": "Liga reforçada / Vinil automotivo de alta resistência"},
                    {"label": "Aplicação", "default": "Chaves, veículos, embarcações, caixas de pesca e cadernos"},
                    {"label": "Durabilidade", "default": "Resistente a água e exposição solar"}
                ],
                "care_tips": "Limpar com pano seco ou levemente umedecido em água. Não utilizar solventes químicos abrasivos."
            },

            # 22. Óculos de Sol & Polarizados UV400
            "eyewear_sunglasses": {
                "id": "eyewear_sunglasses",
                "name": "Óculos de Sol & Polarizados UV400",
                "fa_icon": "fa-solid fa-glasses",
                "theme_color": "#0f766e",
                "theme_bg": "#f0fdfa",
                "category_keywords": ["oculos", "óculos", "polarizado", "polarizada", "aviador", "uv400", "lente polarizada"],
                "default_tagline": "Visão Nítida sem Reflexos, Lentes Polarizadas UV400 e Armação Ultraleve",
                "act1": {
                    "tag": "Lentes & Polarização",
                    "fa_icon": "fa-solid fa-glasses",
                    "title": "LENTES POLARIZADAS DE ALTA DEFINIÇÃO COM PROTEÇÃO UV400",
                    "desc_tmpl": "As lentes do(a) {title} contam com filtro polarizado de alta precisão que elimina reflexos da água, asfalto e superfícies brilhantes, garantindo visão nítida, contraste aprimorado e bloqueio de 100% dos raios UVA e UVB."
                },
                "act2": {
                    "tag": "Estrutura & Conforto",
                    "fa_icon": "fa-solid fa-feather",
                    "title": "ARMAÇÃO ERGONÔMICA LEVE E RESISTENTE A IMPACTOS",
                    "desc_tmpl": "Construída com materiais de alta tenacidade e flexibilidade balanceada, oferece encaixe anatômico confortável que não pressiona as têmporas nem o nariz durante longas horas de uso."
                },
                "act3": {
                    "tag": "Fixação & Durabilidade",
                    "fa_icon": "fa-solid fa-shield-halved",
                    "title": "ACABAMENTO PREMIUM E HASTES ANATÔMICAS CONFORTÁVEIS",
                    "desc_tmpl": "Design esportivo e refinado com dobradiças reforçadas e ponteiras anatômicas que garantem fixação firme no rosto sem pressionar as têmporas, oferecendo máximo conforto mesmo em movimento constante."
                },
                "base_specs": [
                    {"label": "Tecnologia das Lentes", "default": "Polarizadas TAC com filtro anti-reflexo HD"},
                    {"label": "Proteção Solar", "default": "Fator UV400 com 100% de bloqueio contra raios UVA e UVB"},
                    {"label": "Material da Armação", "default": "Polímero ultraleve de alta resistência / Liga metálica nobre"},
                    {"label": "Apoio Nasal", "default": "Plaquetas anatômicas confortáveis que não marcam a pele"},
                    {"label": "Itens Inclusos", "default": "Estojo protetor oficial e flanela especial de microfibra"},
                    {"label": "Uso Recomendado", "default": "Pesca esportiva, náutica, direção, campo e uso diário ao ar livre"}
                ],
                "care_tips": "Lavar periodicamente com água corrente e detergente neutro. Secar com a flanela de microfibra limpa. Guardar sempre no estojo evitando contato com superfícies abrasivas."
            },

            # 23. Luvas de Pesca, Táticas & Esportivas
            "gloves_tactical_fishing": {
                "id": "gloves_tactical_fishing",
                "name": "Luvas de Pesca, Táticas & Esportivas",
                "fa_icon": "fa-solid fa-mitten",
                "theme_color": "#475569",
                "theme_bg": "#f8fafc",
                "category_keywords": ["luva", "luvas", "meio dedo", "dedo inteiro", "grip", "tactical glove"],
                "default_tagline": "Aderência Antiderrapante Firme, Dorso Respirável e Proteção Solar nas Mãos",
                "act1": {
                    "tag": "Aderência & Grip",
                    "fa_icon": "fa-solid fa-hand",
                    "title": "PALMA ANTIDERRAPANTE COM ADERÊNCIA REFORÇADA",
                    "desc_tmpl": "A {title} conta com superfície texturizada de alta aderência na palma, garantindo pegada firme e controle absoluto sobre varas de pesca, guidões, ferramentas e rédeas, mesmo com as mãos molhadas."
                },
                "act2": {
                    "tag": "Respirabilidade & Proteção",
                    "fa_icon": "fa-solid fa-sun",
                    "title": "DORSO RESPIRÁVEL COM PROTEÇÃO SOLAR E SECAGEM RÁPIDA",
                    "desc_tmpl": "Confeccionada com tecido flexível e ventilado que dissipa o calor rapidamente, prevenindo queimaduras solares, bolhas e calosidades durante longas jornadas."
                },
                "act3": {
                    "tag": "Ajuste & Firmeza",
                    "fa_icon": "fa-solid fa-sliders",
                    "title": "AJUSTE ANATÔMICO COM FECHO SEGURO NO PULSO",
                    "desc_tmpl": "Fechamento ajustável no punho que impede a entrada de resíduos, garantindo firmeza sem restringir a circulação ou a mobilidade dos dedos nas atividades de precisão."
                },
                "base_specs": [
                    {"label": "Palma da Mão", "default": "Material sintético texturizado antiderrapante com reforço no polegar"},
                    {"label": "Dorso", "default": "Tecido elástico de alta respirabilidade e secagem ultra rápida (Quick Dry)"},
                    {"label": "Ajuste no Punho", "default": "Fita regulável de fixação rápida para vedação confortável"},
                    {"label": "Modelagem", "default": "Anatômica esportiva (corte meio dedo para sensibilidade tátil)"},
                    {"label": "Indicação de Uso", "default": "Pesca esportiva, ciclismo, motociclismo, tiro e trabalho no campo"}
                ],
                "care_tips": "Lavar à mão com água fria e sabão neutro. Não usar alvejante. Secar à sombra e não torcer."
            }
        }

    def detect_archetype(self, title: str, category: str = "", tags: List[str] = None, vendor: str = "", sku: str = "") -> str:
        """
        Detecta com máxima precisão o arquétipo correto do produto.
        O TÍTULO DO PRODUTO É SOBERANO: previne que coleções multi-categoria
        façam produtos serem classificados incorretamente.
        Normaliza diacríticos para evitar falhas por acentuação incorreta (ex: òculos, óculos, oculos).
        """
        def _clean(s: str) -> str:
            if not s:
                return ""
            return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower().strip()

        t_raw = (title or "").strip()
        t = _clean(t_raw)
        cat = _clean(category)
        tags_str = _clean(" ".join(tags or []))
        vend = _clean(vendor)
        sku_clean = (sku or "").upper().strip()
        text = f"{t} {cat} {vend} {tags_str} {sku_clean}"

        # 1. Aromatizantes Automotivos & Cuidados (Prioridade máxima para evitar que caiam em camisas)
        if any(w in t for w in ["aromatizante", "cheirinho", "difusor", "aromatizador", "odorizador", "little trees", "odor"]):
            return "accessories_car_care"

        # 1.1 Cabos, Fontes Conversoras, Acessórios Elétricos e Peças de Reposição (Para não cair em térmicos ou iscas)
        if any(w in t for w in ["cabo plug", "cabo de alimentacao", "cabo de forca", "adaptador 12v", "fonte conversora", "fonte 110", "conversor 110"]):
            return "accessories_general"

        # 2. Copos Térmicos, Garrafas e Canecas (Prioridade Alta para evitar colisões com boné/isca/camisa)
        is_drinkware = (
            any(w in t for w in ["copo termico", "garrafa termica", "caneca termica", "cuia termica", "cooler"]) or
            ((any(w in t for w in ["copo", "garrafa", "caneca", "cantil", "cuia"]) or "elber" in t) and
             any(w in t for w in ["termic", "termo", "inox", "aco inox", "vacuum", "vazio", "geladeira", "litros"]) and
             not any(w in t for w in ["cabo", "plug", "abridor", "fonte conversora", "fonte 110"])) or
            (t.startswith("copo ") or t.startswith("garrafa ") or t.startswith("caneca ") or t.startswith("cuia "))
        )
        if is_drinkware and not any(w in t for w in ["camisa", "camiseta", "abridor de garrafa"]):
            return "drinkware_thermo"

        # 3. Óculos de Sol & Polarizados UV400 (normalizado para capturar óculos, òculos, oculos)
        if (any(w in t for w in ["oculos", "sunglasses"]) or any(w in t for w in ["polarizado", "polarizada", "aviador", "uv400", "lente polarizada"])) and not any(w in t for w in ["camisa", "camiseta", "adesivo", "chaveiro", "lenco", "bandana"]):
            return "eyewear_sunglasses"

        # 4. Luvas de Pesca, Táticas & Esportivas (se não for camisa)
        if any(w in t for w in ["luva", "luvas"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "gloves_tactical_fishing"

        # 5. Bandanas, Tubenecks, Lenços & Balaclavas (se não for camisa)
        if any(w in t for w in ["bandana", "balaclava", "tubeneck", "buff", "mascara facial", "protetor de pescoco", "lenco", "lencos"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "neck_gaiters_balaclavas"

        # 6. Macacões & Jardineiras (Prioridade antes de calçados para não cair em tênis/bota)
        if any(w in t for w in ["macacao", "jardineira", "jardineiras", "salopete"]):
            return "overalls_workwear"

        # 7. Caixas de Pesca, Estojos & Organização (Prioridade antes de iscas para evitar que caixa de iscas caia em iscas)
        is_tackle_box = (
            any(w in t for w in ["caixa de pesca", "caixa organizadora", "maleta de pesca", "estojo de pesca", "organizador de isca", "porta-iscas", "porta iscas", "porta-vara", "porta vara", "tubo de vara", "multicase", "bolsa tatica deyu kit"]) or
            ((t.startswith("caixa ") or t.startswith("estojo ") or t.startswith("maleta ")) and not any(w in t for w in ["caixa com ", "caixa c/ ", "estojo + ", "anzois", "anzol", "girador"]))
        )
        if is_tackle_box and not any(w in t for w in ["camisa", "camiseta"]) and not any(w in t for w in ["anzois", "anzol", "girador"]):
            return "tackle_boxes_storage"

        # 8. Calças, Bermudas & Shorts (Prioridade antes de camisa para não cair em uv_performance)
        if any(w in t for w in ["calca", "calcas", "bermuda", "bermudas", "shorts", "short", "calcao"]) and not any(w in t for w in ["camisa", "camiseta"]):
            return "pants_cargo_tactical"

        # 8.5 Cutelaria, Facas, Canivetes & Kits Churrasco (Prioridade antes de chapéus/camisas para que Kit Faca Karandá e Kit Churrasco não caiam em chapéu/agro_field)
        if any(w in t for w in ["faca", "facas", "cutelo", "cutelaria", "lamina", "bainha", "canivete", "chaira", "afiador", "kit churrasco"]) and not any(w in t for w in ["camisa", "camiseta", "bone", "chapeu", "copo", "garrafa"]):
            return "cutlery_unique"

        # 9. Chapéus: Distinção estrita entre Country/Feltro/Cowboy vs Safári/Outdoor/Pescador
        if any(w in t for w in ["chapeu", "chapeus"]):
            if any(w in t for w in ["feltro", "pralana", "american hat", "karanda", "country", "cowboy", "pantaneiro", "la", "veludo", "liso", "marcatto", "eldorado", "cury"]):
                return "hats_country_cowboy"
            return "hats_safari_outdoor"
        if any(w in t for w in ["pralana", "american hat", "karanda", "feltro country"]):
            return "hats_country_cowboy"

        # 10. Camisas / Vestuário Superior: Distinção estrita entre Camisas Work/Botão vs Algodão vs Motors vs UV50+
        is_c0_or_uv_sku = any(sku_clean.startswith(prefix) for prefix in ["C0", "CI", "CADV", "ADV", "HYB", "RAGLAN"])
        is_work_sku = any(sku_clean.startswith(prefix) for prefix in ["CMB", "CBT"])
        is_upper_body = any(w in t for w in ["camisa", "camisas", "camiseta", "camisetas", "baby look", "babylook", "regata", "t-shirt", "polo", "jersey", "segunda pele"]) or is_c0_or_uv_sku or is_work_sku

        if is_upper_body:
            # 10.1 Camisas Work / Botão / Sarja / Lisas / Xadrez (Sem zíper, com botões e bolsos utilitários)
            has_uv_or_vest_marker = is_c0_or_uv_sku or any(w in t for w in ["uv", "uv50", "fpu", "fps", "xtech", "solar", "colete", "sublimad"])
            is_button_work = (
                is_work_sku or
                any(w in t for w in ["camisa work", "safari sarja", "camisa sarja", "camisa de botao", "camisa botao", "trabalho botao", "manga longa sarja", "manga curta sarja"]) or
                ("xadrez" in t and not has_uv_or_vest_marker) or
                (("operacional" in t or "sarja" in t or "de botao" in t or "botao" in t) and not any(w in t for w in ["ziper"])) or
                (("lisa" in t or "sem estampa" in t) and any(w in t for w in ["classic", "manga curta", "manga longa"]) and not any(w in t for w in ["uv", "uv50", "dry", "xtech", "segunda pele"]))
            )
            if is_button_work and not any(w in t for w in ["ziper"]):
                return "shirts_button_work"

            # 10.2 Se for camisa com código C0, CI, CADV, ADV, HYB, RAGLAN ou com menção explícita a proteção UV / XTech / Térmica / Kit Camisa
            is_uv_shirt = (
                is_c0_or_uv_sku or
                any(w in t for w in ["uv", "uv50", "fpu", "fps", "xtech", "solar", "segunda pele", "termica", "térmica", "fusionx", "armorx", "hybrid", "kit camisa", "camisa agro"]) or
                any(w in tags_str for w in ["uv50", "uv", "protecao solar", "xtech"])
            )
            if is_uv_shirt and not is_work_sku and not any(w in t for w in ["algodao puro", "100% algodao", "camisa de botao", "camisa work", "botao"]):
                return "uv_performance"

            # 10.3 Camisetas casuais de algodão (Agro / Campo / Lifestyle)
            if (any(w in t for w in ["algodao", "cotton"]) and "algodao sombreado" not in t) or ("camiseta" in t and any(w in t for w in ["campo", "agro", "fazenda", "trator"])):
                return "agro_field"

            # 10.4 Jerseis de motocross sem proteção UV
            if any(w in t for w in ["jersey", "moto", "cross", "off-road", "trilha", "speed", "motors"]):
                return "motors_speed"

            return "uv_performance"

        if "jersey" in t:
            return "motors_speed"

        # 11. Cutelaria & Facas
        if any(w in t for w in ["faca", "facas", "cutelo", "cutelaria", "lamina", "bainha", "canivete", "chaira", "afiador", "kit churrasco"]):
            return "cutlery_unique"

        # 12. Calçados (Sandálias Boaonda vs Tênis/Botinas)
        if any(w in t for w in ["tenis", "botina", "bota", "sneaker", "sapato"]):
            return "closed_footwear_sneakers"
        if any(w in t for w in ["sandalia", "chinelo", "boaonda", "babuche", "clog", "slide", "pantufa"]):
            return "footwear_sandals_boaonda"

        # 13. Chapéus de Pesca / Safári (secundário)
        if any(w in t for w in ["safari", "australiano", "palha", "pescador"]):
            return "hats_safari_outdoor"

        # 14. Bonés Trucker & Snapback (Com trava contra palavra inglesa 'bones')
        is_cap = (
            any(w in t for w in ["trucker", "snapback", "aba curva", "aba reta", "viseira"]) or
            (bool(re.search(r'\b(bone|bones)\b', t)) and not any(w in t for w in ["till the bones", "cross bones", "fish bones", "copo", "garrafa", "camisa"]))
        )
        if is_cap:
            return "caps_trucker_snapback"

        # 15. Manguitos
        if any(w in t for w in ["manguito", "manguitos", "manga avulsa"]):
            return "sun_sleeves_manguitos"

        # 16. Ferragens e Equipamentos de Pesca (Varas, Carretilhas, Molinetes, Giradores, Snaps, Argolas)
        if bool(re.search(r'\bvaras?\b', t)) or any(w in t for w in ["carretilha", "molinete", "linha", "anzol", "anzois", "alicate", "passagua", "girador", "giradores", "snap", "snaps", "argola", "empate", "chumbada", "chumbo", "trava varas", "suporte porta iscas"]):
            return "fishing_tackle_gear"

        # 17. Iscas Artificiais
        if any(w in t for w in ["isca", "iscas", "plug", "jig", "frog", "soft bait", "crankbait", "minnow", "popper", "stick", "twitch", "shad", "criatura"]):
            return "fishing_lures"

        # 18. Acessórios Gerais, Chaveiros, Adesivos, Camping & Caiaque
        if any(w in t for w in ["chaveiro", "adesivo", "adesivos", "sticker", "stickers", "patch", "emblema", "pin ", "capa de caiaque", "caiaque", "barraca", "fogareiro", "mesa dobravel", "cadeira", "coleira", "suporte magnetico", "personalizacao nome", "cabo plug", "fita para protecao", "fonte conversora"]):
            return "accessories_general"

        # 19. Copos e Térmicos (secundário)
        if any(w in t for w in ["copo", "garrafa", "caneca", "cantil", "cooler", "termico"]):
            return "drinkware_thermo"

        # 20. Livros & Publicações
        if any(w in t for w in ["livro", "livros", "cartilha", "guia ilustrado", "colorir"]):
            return "books_publications"

        # Fallback Secundário via Categoria / Tags / Vendor
        if any(w in text for w in ["aromatizante", "cheirinho", "difusor"]):
            return "accessories_car_care"
        if any(w in text for w in ["oculos", "polarizado", "uv400"]):
            return "eyewear_sunglasses"
        if any(w in text for w in ["luva", "luvas"]) and not any(w in text for w in ["camisa", "camiseta"]):
            return "gloves_tactical_fishing"
        if any(w in text for w in ["lenco", "bandana", "balaclava", "tubeneck"]):
            return "neck_gaiters_balaclavas"
        if any(w in text for w in ["chaveiro", "adesivo"]):
            return "accessories_general"
        if any(w in text for w in ["calca", "bermuda", "shorts"]):
            return "pants_cargo_tactical"
        if any(w in text for w in ["faca", "chaira", "cutelaria", "canivete", "churrasco"]):
            return "cutlery_unique"
        if any(w in text for w in ["pralana", "american hat", "karanda", "feltro", "country"]):
            return "hats_country_cowboy"
        if any(w in text for w in ["manguito", "manguitos"]):
            return "sun_sleeves_manguitos"
        if any(w in text for w in ["sandalia", "chinelo", "boaonda"]):
            return "footwear_sandals_boaonda"
        if any(w in text for w in ["tenis", "calcado"]):
            return "closed_footwear_sneakers"
        if any(w in t for w in ["isca", "iscas", "plug"]):
            return "fishing_lures"
        if any(w in text for w in ["copo", "garrafa", "termic"]):
            return "drinkware_thermo"
        if any(w in text for w in ["chapeu"]):
            return "hats_safari_outdoor"
        if bool(re.search(r'\b(bone|bones)\b', text)) and "till the bones" not in text:
            return "caps_trucker_snapback"
        if bool(re.search(r'\bvaras?\b', text)) or any(w in text for w in ["carretilha", "molinete", "girador", "snap", "empate"]):
            return "fishing_tackle_gear"
        if any(w in text for w in ["jersey", "moto", "motors"]):
            return "motors_speed"
        if any(w in text for w in ["agro", "campo"]):
            return "agro_field"

        return "uv_performance"

    def classify_store_category(self, title: str, archetype_id: str, store_key: str = "brk_fishing", tags: List[str] = None, sku: str = "") -> str:
        """
        Classifica o produto em uma Coleção/Categoria oficial da loja com base no arquétipo soberano,
        garantindo zero contaminação entre Camisas, Bonés, Bandanas, Óculos, Botinas e Equipamentos.
        """
        t_low = (title or "").lower()
        sku_low = (sku or "").lower()
        tags_str = " ".join(tags or []).lower() if isinstance(tags, list) else str(tags or "").lower()
        full_info = f"{t_low} {sku_low} {tags_str}"

        if store_key == "brk_agro":
            if archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work"):
                return "Camisas Agro & Campo"
            if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
                return "Bonés & Chapéus Agro"
            if archetype_id in ("closed_footwear_sneakers", "footwear_sandals_boaonda"):
                return "Botinas & Calçados"
            if archetype_id == "cutlery_unique":
                return "Cutelaria & Facas Campo"
            if archetype_id == "drinkware_thermo":
                return "Térmicos & Tereré"
            if archetype_id == "eyewear_sunglasses":
                return "Óculos Polarizados Agro"
            if archetype_id in ("neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"):
                return "Bandanas, Luvas & Manguitos"
            if archetype_id in ("pants_cargo_tactical", "overalls_workwear"):
                return "Calças & Vestuário Campo"
            return "Acessórios Agro & Fazenda"

        if store_key == "brk_motors":
            if archetype_id in ("uv_performance", "motors_speed", "agro_field", "shirts_button_work"):
                if any(w in t_low for w in ["jaqueta", "corta vento", "moletom"]):
                    return "Jaquetas & Corta Vento"
                if "segunda pele" in t_low or sku_low.startswith("raglan"):
                    return "Camisas Segunda Pele"
                return "Jerseys & Camisas Motors"
            if archetype_id in ("neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"):
                return "Proteção & Luvas Motors"
            if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
                return "Bonés & Street Motors"
            if archetype_id == "eyewear_sunglasses":
                return "Óculos & Goggles"
            return "Acessórios & Equipamentos"

        # Default: brk_fishing
        if archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work"):
            if "armorx" in full_info or "armor" in t_low:
                return "Camisas ArmorX"
            return "Camisas de Pesca UV"
        if archetype_id in ("caps_trucker_snapback", "hats_safari_outdoor", "hats_country_cowboy"):
            return "Bonés & Chapéus"
        if archetype_id in ("neck_gaiters_balaclavas", "sun_sleeves_manguitos", "gloves_tactical_fishing"):
            return "Bandanas, Luvas & Manguitos"
        if archetype_id == "eyewear_sunglasses":
            return "Óculos Polarizados"
        if archetype_id in ("fishing_lures", "fishing_tackle_gear", "overalls_workwear"):
            return "Equipamentos & Iscas"
        if archetype_id == "tackle_boxes_storage":
            return "Caixas & Organização"
        if archetype_id in ("footwear_sandals_boaonda", "closed_footwear_sneakers", "pants_cargo_tactical"):
            return "Calçados & Sandálias"
        if archetype_id == "cutlery_unique":
            return "Cutelaria & Facas"
        if archetype_id == "drinkware_thermo":
            return "Térmicos & Camping"
        return "Acessórios Diversos"

    def sanitize_specs_for_archetype(self, specs: List[Dict[str, str]], archetype_id: str) -> List[Dict[str, str]]:
        """
        Sanitiza a ficha técnica para remover estritamente especificações proibidas
        ou alucinações incompatíveis com a categoria do produto (Regra de Ouro da Fidelidade).
        """
        sanitized = []
        for s in specs:
            label = s.get("label", "").lower()
            val = s.get("value", s.get("default", "")).lower()
            full = f"{label} {val}"

            # 1. Chapéus Country / Feltro: ZERO cordão jugular, ZERO trava anti-vento, ZERO ilhoses de respiração
            if archetype_id == "hats_country_cowboy":
                if any(w in full for w in ["jugular", "vento", "ilhós", "ilhoses", "pescoço", "nuca", "protetor de nuca"]):
                    continue

            # 2. Camisas Work / Botão: ZERO zíper, ZERO trava de segurança, ZERO gola padre com zíper, ZERO estampa sublimada
            elif archetype_id == "shirts_button_work":
                if any(w in full for w in ["zíper", "ziper", "cursor", "trava", "sublimad", "gola padre"]):
                    continue

            # 2.1 Camisetas de Algodão (agro_field): ZERO Dry Fit ou Poliéster (evita contradição Algodão vs Dry Fit)
            elif archetype_id == "agro_field":
                if any(w in full for w in ["dry fit", "dryfit", "poliéster", "poliester", "xtech"]):
                    s = {"label": s.get("label", "Composição"), "value": "100% Algodão Premium Penteado com toque macio"}

            # 3. Calças / Bermudas: ZERO mangas, ZERO gola alta, ZERO zíper frontal no peito
            elif archetype_id == "pants_cargo_tactical":
                if any(w in full for w in ["manga", "gola padre", "gola alta", "peito", "punho"]):
                    continue

            # 4. Aromatizantes & Cuidados: ZERO vestuário, ZERO tecido, ZERO lavagem à máquina, ZERO passar a ferro
            elif archetype_id in ["accessories_car_care", "accessories_general"]:
                if any(w in full for w in ["manga", "gola", "tecido", "poliéster", "algodão", "lavar à mão", "lavagem", "ferro", "modelagem"]):
                    continue

            # 5. Óculos de Sol: ZERO vestuário, ZERO mangas, ZERO gola, ZERO zíper, ZERO tecido
            elif archetype_id == "eyewear_sunglasses":
                if any(w in full for w in ["manga", "gola", "zíper", "ziper", "tecido", "poliéster", "algodão", "costura", "punho", "passador", "bolso", "modelagem"]):
                    continue

            # 6. Luvas de Pesca & Táticas: ZERO mangas compridas, ZERO gola, ZERO zíper frontal
            elif archetype_id == "gloves_tactical_fishing":
                if any(w in full for w in ["manga longa", "mangas longas", "gola", "zíper", "ziper", "passador", "bolso"]):
                    continue

            # 7. Lenços e Bandanas: ZERO mangas, ZERO gola padre, ZERO zíper
            elif archetype_id == "neck_gaiters_balaclavas":
                if any(w in full for w in ["manga", "gola padre", "zíper", "ziper", "punho", "passador", "bolso"]):
                    continue

            # 8. Equipamentos e Ferragens de Pesca: ZERO vestuário
            elif archetype_id in ["fishing_tackle_gear", "fishing_lures", "tackle_boxes_storage"]:
                if any(w in full for w in ["manga", "gola", "zíper", "ziper", "tecido", "poliéster", "algodão", "costura"]):
                    continue

            sanitized.append(s)
        return sanitized

    def is_ready_delivery(self, product: Dict[str, Any]) -> bool:
        """
        Identifica se o produto é de pronta entrega / envio imediato.
        Regra Oficial BRK:
        - Códigos/SKUs contendo _FULL ou _OUT (ex: C02496BLP_FULL, C01046BLP_OUT, -FULL, -OUT)
        - Menção expressa de pronta entrega / envio imediato no título ou tags
        """
        if not product:
            return False

        skus_to_check = []
        for k in ["sku", "master_sku"]:
            val = str(product.get(k) or "").strip()
            if val:
                skus_to_check.append(val)

        for vsku in product.get("variants_skus", []):
            if vsku:
                skus_to_check.append(str(vsku).strip())

        for v in product.get("variants", []):
            if isinstance(v, dict):
                v_s = str(v.get("sku") or "").strip()
                if v_s:
                    skus_to_check.append(v_s)

        title = str(product.get("title") or "")
        tags = product.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        tags_str = " ".join(tags)

        full_out_pattern = re.compile(r'(_FULL|_OUT|\bFULL\b|\bOUT\b|-FULL|-OUT)', re.IGNORECASE)
        for s in skus_to_check:
            if full_out_pattern.search(s):
                return True

        if full_out_pattern.search(title) or full_out_pattern.search(tags_str):
            return True
        if any(term in title.lower() for term in ["pronta entrega", "envio imediato"]):
            return True

        return False

    def extract_product_specs(self, product: Dict[str, Any], archetype_id: str, sibling_specs: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Extrai especificações autênticas do produto. Se o sibling_matcher encontrou
        especificações de um irmão homólogo, elas são priorizadas e sanitizadas para garantir fidelidade.
        Para Camisas UV Performance (C0), usa rigorosamente a Ficha Técnica Oficial XTech Pro
        com Prazo de Produção dinâmico (Pronta entrega para _FULL e _OUT, 10 dias úteis para códigos padrão)
        e detalhes anatômicos exclusivos para Fusion (máscara integrada + dedeira) e Hybrid (capuz + dedeira).
        """
        if archetype_id == "uv_performance":
            is_pronta = self.is_ready_delivery(product)
            prazo_val = "Pronta entrega" if is_pronta else "10 dias úteis"
            
            t_low = (product.get("title") or "").lower()
            sku_low = str(product.get("master_sku") or product.get("sku") or "").lower()
            tags_low = " ".join([str(t).lower() for t in (product.get("tags") or [])]) if isinstance(product.get("tags"), list) else str(product.get("tags") or "").lower()
            
            is_fusion = any(w in t_low for w in ["fusion", "fusionx"]) or "fusion" in sku_low or "fusion" in tags_low
            is_hybrid = any(w in t_low for w in ["hybrid"]) or sku_low.startswith("hyb") or "hybrid" in sku_low or "hybrid" in tags_low
            
            specs = [
                {"label": "Prazo de Produção", "value": prazo_val},
                {"label": "Composição", "value": "90% Poliéster 10% Elastano"},
                {"label": "Tecido", "value": "XTech Pro"},
                {"label": "Tecnologia", "value": "Secagem Rápida, Tecido Leve, Proteção Solar"},
                {"label": "Modelagem", "value": "Anatômica e confortável"},
                {"label": "Proteção", "value": "Proteção UV50+ (não sai na lavagem)"},
            ]
            if is_fusion:
                specs.append({"label": "Capuz & Máscara", "value": "Capuz anatômico integrado com máscara facial de proteção UV50+"})
                specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
            elif is_hybrid:
                specs.append({"label": "Capuz", "value": "Capuz anatômico integrado de alta cobertura solar"})
                specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
            return specs

        title = product.get("title", "")
        t_low = title.lower()
        vendor = product.get("vendor", "")

        # Especialização Cirúrgica para Equipamentos de Pesca (Evita 'rolamentos' em Varas, Linhas, Anzóis, Alicates e Suportes)
        if archetype_id == "fishing_tackle_gear":
            origin_res = self.resolve_product_origin_and_title(title=title, vendor=vendor, product=product)
            eff_brand = origin_res["brand_name"] if origin_res.get("brand_name") else (vendor or "BRK")
            origem_val = f"Produto Original {eff_brand} com garantia oficial"

            if "trava vara" in t_low or "trava-vara" in t_low:
                return [
                    {"label": "Categoria", "value": f"Trava-Varas de Convés para Embarcações e Caiaques {eff_brand}".strip()},
                    {"label": "Capacidade", "value": "Acomoda e trava até 3 varas de pesca simultaneamente"},
                    {"label": "Fixação Inclusa", "value": "Suportes de engate rápido + Parafusos em Aço Inoxidável inclusos"},
                    {"label": "Material", "value": "Cinta elástica de alta memória, bases em polímero naval e inox"},
                    {"label": "Aplicação", "value": "Barcos de alumínio, bass boats, lanchas e caiaques de pesca"},
                ]
            if ("alça" in t_low or "alca" in t_low) and "vara" in t_low:
                return [
                    {"label": "Categoria", "value": f"Alça de Transporte de Ombro para Varas de Pesca {eff_brand}".strip()},
                    {"label": "Sistema de Fixação", "value": "2 cintas agrupadoras de fixação firme com fivelas de engate rápido"},
                    {"label": "Ergonomia", "value": "Ombreira acolchoada antiderrapante com tira ajustável (até 120 cm)"},
                    {"label": "Aplicação", "value": "Transporte seguro de múltiplos conjuntos de varas com mãos livres"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if "capa protetora" in t_low and "carretilha" in t_low:
                return [
                    {"label": "Categoria", "value": f"Capa Protetora para Carretilha de Perfil Baixo {eff_brand}".strip()},
                    {"label": "Material", "value": "Neoprene flexível de alta densidade com absorção de impacto"},
                    {"label": "Compatibilidade", "value": "Carretilhas de Perfil Baixo (direitas e esquerdas), avulsas ou montadas na vara"},
                    {"label": "Fechamento", "value": "Abas anatômicas de fixação rápida e ajuste firme"},
                    {"label": "Acabamento", "value": "Estampa exclusiva BRK Fishing em alta definição"},
                ]
            if "cinto" in t_low and "apoiador" in t_low:
                return [
                    {"label": "Categoria", "value": f"Cinto Colete Apoiador Dorsal para Pesca Pesada {eff_brand}".strip()},
                    {"label": "Estrutura", "value": "Painel dorsal anatômico acolchoado com alças reguláveis em X"},
                    {"label": "Conexão da Carretilha", "value": "Ganchos metálicos reforçados com tiras de alta tração e fivelas de engate rápido"},
                    {"label": "Função Principal", "value": "Distribuição ergonômica da tração entre costas e ombros em brigas pesadas"},
                    {"label": "Indicação de Uso", "value": "Pesca pesada de grandes peixes de couro (Piraíba, Jaú, Pirarara) e oceânica"},
                ]
            if "passaguá" in t_low or "passagua" in t_low or "puçá" in t_low or "puca" in t_low:
                return [
                    {"label": "Categoria", "value": f"Passaguá / Puçá de Pesca Dobrável {eff_brand}".strip()},
                    {"label": "Dimensões", "value": "Arco de 40 x 40 cm | Comprimento total montado: 180 cm (1,80 m)"},
                    {"label": "Estrutura do Cabo", "value": "Alumínio leve dividido em 2 partes com trava de encaixe rápido e punho antiderrapante"},
                    {"label": "Rede", "value": "Malha resistente de secagem rápida amiga do Pesque e Solte"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if "alicate" in t_low and ("contenção" in t_low or "contencao" in t_low or "balança" in t_low or "balanca" in t_low):
                return [
                    {"label": "Categoria", "value": f"Alicate de Contenção (Lip Grip) com Balança Integrada {eff_brand}".strip()},
                    {"label": "Estrutura & Pinça", "value": "Tubo metálico anticorrosivo com garras de travamento em aço inox"},
                    {"label": "Balança Integrada", "value": "Escala mecânica de pesagem embutida no corpo do alicate"},
                    {"label": "Segurança & Ergonomia", "value": "Cabo emborrachado antiderrapante com gatilho duplo e cordão fiel de pulso"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if "alicate" in t_low:
                return [
                    {"label": "Categoria", "value": f"Alicate de Pesca e Corte de Precisão {eff_brand}".strip()},
                    {"label": "Material", "value": "Aço carbono / inox forjado com tratamento superficial anticorrosivo"},
                    {"label": "Funções", "value": "Corte de linhas, remoção de anzóis/garatéias e manutenção de terminais"},
                    {"label": "Empunhadura", "value": "Cabo anatômico emborrachado antiderrapante com mola de retorno"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]

            is_rod_kit = "kit vara" in t_low and ("molinete" in t_low or "carretilha" in t_low)
            is_rod = bool(re.search(r'\bvaras?\b', t_low)) and not is_rod_kit
            is_line = bool(re.search(r'\blinhas?\b', t_low))
            is_hook_terminal = any(w in t_low for w in ["anzol", "anzóis", "anzois", "snap", "girador", "argola", "empate", "chumbada", "chumbo", "garateia", "garatéia"])

            if is_rod_kit:
                return [
                    {"label": "Categoria", "value": f"Kit Conjunto Vara e Molinete {eff_brand}".strip()},
                    {"label": "Vara (Blank & Passadores)", "value": "Blank em compósito resistente de 2 partes com passadores anti-atrito"},
                    {"label": "Molinete (Recolhimento)", "value": "Carretel balanceado com sistema de fricção progressiva e recolhimento macio"},
                    {"label": "Empunhadura", "value": "Cabo anatômico em EVA de alta densidade com Reel Seat firme"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if is_rod:
                return [
                    {"label": "Categoria", "value": f"Vara de Pesca Esportiva {eff_brand}".strip()},
                    {"label": "Blank (Corpo)", "value": "Compósito de alta sensibilidade e resistência à tração"},
                    {"label": "Passadores", "value": "Passadores reforçados anti-atrito de alto desempenho"},
                    {"label": "Cabo & Fixador", "value": "Cabo anatômico de alta aderência com Reel Seat de travamento firme"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if is_line:
                is_multi = any(w in t_low for w in ["multi", "x4", "x8", "4x", "8x", "j-braid", "vexter", "siglon", "rapinova"])
                if is_multi:
                    tipo_linha = "Multifilamento trançado em fibras PE de alta tenacidade e elasticidade próxima de zero"
                elif "fluor" in t_low:
                    tipo_linha = "Nylon especial com revestimento de Fluorcarbono (baixa visibilidade na água)"
                else:
                    tipo_linha = "Monofilamento de Nylon (Poliamida) copolímero calibrado de alta resistência"
                return [
                    {"label": "Categoria", "value": f"Linha de Pesca {eff_brand}".strip()},
                    {"label": "Construção", "value": tipo_linha},
                    {"label": "Resistência", "value": "Alta resistência linear à tração, ao nó e à abrasão"},
                    {"label": "Desempenho", "value": "Baixíssima memória mecânica para arremessos longos e precisos"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if "argola" in t_low:
                return [
                    {"label": "Categoria", "value": f"Argola (Split Ring) para Iscas Artificiais {eff_brand}".strip()},
                    {"label": "Material", "value": "Aço Inoxidável forjado de alta memória elástica"},
                    {"label": "Modelo", "value": "Split Ring tradicional sem trava de alta resistência à tração"},
                    {"label": "Aplicação", "value": "Fixação segura de garatéias, anzóis inline e snaps em iscas artificiais"},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]
            if is_hook_terminal:
                if "anz" in t_low and "sabiki" in t_low:
                    prec_val = "Sistema multi-anzol Sabiki com filetes atrativos para captura rápida"
                elif "anz" in t_low and "encastoado" in t_low:
                    prec_val = "Anzol afiado quimicamente encastoado em cabo de aço flexível anti-corte"
                elif "anz" in t_low:
                    prec_val = "Afiamento químico de penetração rápida e farpa de retenção firme"
                elif "girador" in t_low and "snap" in t_low:
                    prec_val = "Giro livre 360° anti-torção de linha com snap de engate rápido"
                elif "girador" in t_low:
                    prec_val = "Rotação livre 360° de alta velocidade que elimina a torção da linha"
                elif "empate" in t_low:
                    prec_val = "Cabo de aço flexível revestido com girador e snap contra dentes cortantes"
                else:
                    prec_val = "Trava segura de alta pressão para troca rápida de iscas"
                return [
                    {"label": "Categoria", "value": f"Terminal de Pesca de Alta Resistência {eff_brand}".strip()},
                    {"label": "Material", "value": "Aço carbono / inox forjado de alta resistência à tração"},
                    {"label": "Acabamento", "value": "Tratamento anticorrosivo para água doce e salgada"},
                    {"label": "Especificação Técnica", "value": prec_val},
                    {"label": "Origem / Distribuição", "value": origem_val},
                ]

        if sibling_specs and len(sibling_specs) >= 2:
            raw_specs = [{"label": s["label"], "value": s["default"]} for s in sibling_specs]
            return self.sanitize_specs_for_archetype(raw_specs, archetype_id)

        template = self.templates.get(archetype_id, self.templates["uv_performance"])
        base_specs = template["base_specs"]
        
        body = product.get("body_html", "") or ""
        tags = product.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        
        full_text = f"{title} {vendor} {body} {' '.join(tags)}".lower()

        extracted = []
        for spec in base_specs:
            label = spec["label"]
            val = spec["default"]
            
            # Se for equipamento de revenda, injetar Vendor real
            if label == "Origem / Distribuição" and vendor:
                val = f"Produto Original {vendor} com garantia oficial"
            elif label == "Categoria" and vendor:
                val = f"Equipamento de Precisão {vendor}"
            elif "boaonda" in full_text and label == "Material do Cabedal":
                val = "Termoplástico nobre Boaonda flexível e lavável"

            # 1. Proteção Solar (uv_performance usa padrão oficial XTech Pro)
            if archetype_id != "uv_performance" and ("proteção" in label.lower() or "solar" in label.lower()):
                if any(x in full_text for x in ["50+", "uv 50", "fps 50", "fpu 50"]):
                    val = "Fator FPU 50+ permanente certificado"
                elif "uv" in full_text:
                    val = "Proteção UV integrada ao tecido"
            
            # 2. Composição / Tecido (agro_field / camisetas de algodão usam estritamente 100% Algodão Premium)
            elif archetype_id != "uv_performance" and ("composição" in label.lower() or "tecido" in label.lower()):
                if archetype_id == "agro_field" or "algodão" in t_low or "algodao" in t_low:
                    val = "100% Algodão Premium Penteado com toque macio"
                elif any(x in full_text for x in ["dry fit", "dryfit", "dry"]):
                    val = "100% Poliéster Tecnológico Dry Fit respirável"
                elif "algodão" in full_text or "algodao" in full_text:
                    val = "100% Algodão Premium Penteado com toque macio"

            # 3. Zíper
            elif "zíper" in label.lower() or "ziper" in label.lower():
                if "ykk" in full_text:
                    val = "Zíper reforçado YKK com trava emborrachada"
                elif "sem zíper" in full_text or "careca" in full_text:
                    val = "Gola careca com acabamento reforçado"

            extracted.append({"label": label, "value": val})

        return extracted

    def resolve_product_origin_and_title(self, title: str, vendor: str = "", sku: str = "", tags = None, product: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Determina com precisão a origem do produto (produção própria BRK vs revenda)
        e formata o título da descrição:
        - Produção própria: garante 'BRK' no título.
        - Revenda: garante o nome da marca correspondente no título.
        - Camisas de produção própria com código iniciado em C0: ativa show_copyright.
        """
        tags_str = " ".join(tags or []) if isinstance(tags, list) else str(tags or "")
        full_info = f"{title} {vendor} {tags_str}"
        
        detected_brand = None
        for brand in self.known_brands:
            if re.search(r'\b' + re.escape(brand) + r'\b', full_info, re.IGNORECASE):
                detected_brand = "Cutelaria D'Avila" if brand.lower() in ("d'avila", "cutelaria d'avila") else ("Karandá" if brand.lower() == "karanda" else brand)
                break
        if not detected_brand:
            if re.search(r'faca\s+artesanal\s+ga[úu]cha', full_info, re.IGNORECASE):
                detected_brand = "Cutelaria D'Avila"
            elif re.search(r'\bisca\s+artificial\s+inna\b', full_info, re.IGNORECASE):
                detected_brand = "Marine Sports"
                
        is_revenda = detected_brand is not None and detected_brand.lower() != "brk"
        
        t_clean = title.strip()
        t_clean = re.sub(r'\bÒculos\b', 'Óculos', t_clean)
        t_clean = re.sub(r'\bòculos\b', 'óculos', t_clean)
        t_clean = re.sub(r'\bProtecão\b', 'Proteção', t_clean)
        t_clean = re.sub(r'\bprotecão\b', 'proteção', t_clean)
        t_clean = re.sub(r'\bBalaclava\s+Balaclava\b', 'Balaclava', t_clean, flags=re.IGNORECASE)
        t_clean = re.sub(r'\b(com|de|para|em)\s+\1\b', r'\1', t_clean, flags=re.IGNORECASE)
        t_clean = re.sub(r'\s{2,}', ' ', t_clean).strip()
        if is_revenda:
            origin_type = "revenda"
            brand_name = detected_brand
            if not re.search(r'\b' + re.escape(brand_name) + r'\b', t_clean, re.IGNORECASE):
                formatted_title = f"{t_clean} - {brand_name}"
            else:
                formatted_title = t_clean
        else:
            origin_type = "producao_propria"
            brand_name = "BRK"
            if not re.search(r'\b(BRK|ArmorX)\b', t_clean, re.IGNORECASE):
                formatted_title = f"BRK {t_clean}"
            else:
                formatted_title = t_clean
                
        # Regra de Direitos Autorais em Camisas C0 (Verificação exaustiva de SKU mestre, variantes e handle)
        sku_upper = str(sku or "").upper().strip()
        var_skus = []
        handle_str = ""
        if isinstance(product, dict):
            var_skus = [str(v).upper() for v in product.get("variants_skus", [])]
            handle_str = str(product.get("handle", "")).upper()
        
        is_c0 = sku_upper.startswith("C0") or any(v.startswith("C0") for v in var_skus) or handle_str.startswith("C0") or "C0" in str(tags or "").upper()
        is_shirt = any(w in t_clean.lower() for w in ["camisa", "camiseta", "jersey", "baby look", "regata", "polo"])
        show_copyright = (origin_type == "producao_propria") and is_shirt and is_c0
        
        return {
            "formatted_title": formatted_title,
            "brand_name": brand_name,
            "origin_type": origin_type,
            "show_copyright": show_copyright
        }

    _EXPLICIT_BACK_POC_HASHES = (
        "7b19cafab14e", "e2f62ee973da", "387e870f3379", "7bdc66337bfe",
        "b4b1be48b687", "028bb8fdcfd5", "fff9408f57fe", "b01708bd7eea",
        "0855ecb1a641", "61d791ea91ca", "ee825cc65556", "e8f232579489",
        "c4773979284d", "3b4aba35b3d2", "0c83e30f278a", "22311f856466",
        "2320ad7a784d", "8da0d64f829c", "9656ca14524e", "33beb817c568",
        "7b1e90ac1efc", "71b9cbecac2a", "c06bcd092644", "6f84821f7619",
        "236b64bb841b", "0721a4c8ce17", "82bf06e5656d", "086u9hh",
        "4ad9fc8f16bc", "94a3b81f5954", "73591bff33b1", "32165d82a90b",
        "fcb50f9e02ac", "b3e2c7dc24a2", "c8a91438bfdd", "e5092aceccc3",
        "2339b90698f3", "84a9e29f3d47", "0a5de4344adb", "5f5276d2", "d19242f6", "094fb596", "e65b23e7",
        "voului", "hkjbjth", "91d0224d198b", "d639ff6b1c5a", "d1caa407ee4c", "4a16f38fbd2e", "41cdcae64190",
        "b43394572417", "f8fd81f01331",
        # brk_motors (C02893..C02897BL, C02893I..2897I, BP105BL)
        "c548407e", "ec5b9024", "1a8929e3", "1524a040", "2f96f543", "d000cf7e", "fa33bfa6",
        "bc24ae71", "dca252fa", "f8fbe84e", "0a8feee6", "59c6e4c0", "9170d7b1", "878c454f",
        "59a38649", "4b867467", "a8302ae8", "3ceae18c", "ce5d92d7", "58953552", "061eb7bc",
        "b0e916f8", "d43c5a58", "61812f9a", "a5c13f78", "1ca3d397", "a4c26e1c",
        # brk_fishing (FUSION264..267BL, CI139I..146I, C02874..2888BL, FUSION156BL/160, C02406, C02907/2906, C02800I..2819, C02795I..2799I, C02503BL, C01828BL, C01316BL)
        "45264908", "13105c88", "fd83706b", "8c080972", "f216f901", "4d2d6d08", "c252c71d",
        "46527a54", "690bc78c", "04573785", "e38b5b7a", "36f55c3f", "8ab61efc", "a5d85d3f",
        "99eac446", "9441361f", "467d8be4", "f6ac2d2f", "0613bce8", "0f246755", "b572fc99",
        "918533a9", "7207f2f3", "6c7ea73a", "a0deafd1", "79bc00df", "9ea038aa",
        "0171fd65", "9d69cd2a", "6cf52d17", "74ff3b1b", "84c0fd2a", "50927e47", "d53188b6",
        "f9272d9d", "b4e6b115", "6ae27aba", "da70f47a", "26162728", "3695e90e", "2aba8948",
        "28b07dbe", "477731fa", "d1fa0698", "b3c85297", "c11b6e73", "50cfe677", "ff755646",
        "e2e61d79", "3d94f24c", "1f3124fe", "9c9aec2c", "b32ac4aa", "bde30803", "e97cd38b",
        "9866b4af", "474379d9", "aee9a4d7", "a0268929", "80e0722b", "ba4b97f3", "311b1a48",
        "387611db",
        # brk_agro (C02901..2906, CI111..124, BP103..105, C0796, C01203, C01966BL, C01828BL/I, C02806..2869, C02783I..2794I, C02648..2684, C02585, C02047I, CBTML024, CBTMC042)
        "1e528db3", "1ae31ae8", "eeb483da", "641138aa", "7af8bee7", "96a33263", "bd421e10",
        "72a45e5a", "171544dd", "0e2f0090", "0efb8232", "e5731d9f", "54bfe1d4", "9f9bda93",
        "bb5b18c7", "e88ba3e1", "0010ded4", "21f474ee", "c79bce79", "3adfeb2d", "e566edc6",
        "6e7e1221", "787a7d0b", "a5025406", "891beb7a", "57649b54", "09af3788", "173299e0",
        "d7f2bfe2", "876b52fe", "9ef1be5e", "ce77f8a9", "a8fc9f34", "f926f2f9", "f5047d84",
        "b56a2aed", "521f0869", "388fa6af", "6d9cbfb8", "b8d9699c", "c17c1302", "2bf64b3f",
        "61500b8b", "e530b68e", "c5b54f10", "2b6c194f", "02781a5e", "9ba59d31", "603df378",
        "eb6064ae", "1a8c7ea9", "93250732", "d3cacd5c", "4f445b35", "bce437e5", "f4a005bc",
        "77850713", "91b565a3", "c39e65b5", "da63c015", "b277f79c", "0e6cf2c0",
        "ba878fcc", "71a54be9", "abc2a560", "1aac96a2", "d6035923", "03dbed6f", "11fcc517",
        "81ccd5ac", "4f96b46d", "d670dece", "bc78e78c", "e2774c44", "6a833563", "f1e47bff",
        "d2d1d19a", "32a3d776", "dc2a5969", "53dca2d0", "8212ed55", "13ba8a69", "bc98ee7b",
        "583328cc", "063a40dd", "8db723a7", "9e0d1a83", "14a98c08", "8070ee59", "c2b30a94",
        "33d33a45", "fb4ca266", "573b0e79", "3a78a6a2", "bdcc212d", "33f3559a", "cabfb843",
        "9b2d4240", "d0518590", "611b4e36", "97181e9f", "a2b260ba", "8b129343", "0ae4a4ba",
        "12836d62", "5deb18b2", "4fae46ea", "a95867bc", "a359da0e", "a3fe2a08", "3f1079ca",
        "350ac9a4", "42ed5a54", "e12745ed", "784b0d09", "07a248f9", "7ceab477", "e6ae4c22",
        "fd8814b0", "f18b4e92", "f23c1aae", "e8ab12ed", "d1911749", "05978a94", "55ff42d9",
        "38b9f32b", "ec809742", "c2db5498", "dd5b5986", "03_6c7c8bc", "cbtmc042.webp",
    )

    def _is_back_view_url(self, url: str, include_03: bool = False) -> bool:
        if not url or not isinstance(url, str):
            return False
        u_low = url.lower()
        fname = u_low.split("/")[-1].split("?")[0]
        if fname.startswith("02_1918aa2d") or "zoom" in fname or "2-capa" in fname or "capa-2" in fname:
            return False
        if "productonchannel" in fname:
            return any(h in fname for h in self._EXPLICIT_BACK_POC_HASHES)
        if any(h in fname for h in self._EXPLICIT_BACK_POC_HASHES):
            return True
        fname_no_ts = re.sub(r'(?:^|[_.\-\s])\d{2}_\d{2}_\d{2}(?=[_.\-\s]|$)', '', fname)
        if "frente" in fname_no_ts or "mkpmaopunho" in fname_no_ts:
            return False
        keywords = [
            "costas", "costa", "back", "traseira", "verso", "tras",
            "02fem", "02masc", "02inf", "02_fem", "02_masc", "02_inf",
            "2fem", "2masc", "2inf", "2-fem", "2-masc", "2-inf", "2_fem", "2_masc", "2_inf"
        ]
        if any(w in fname_no_ts for w in keywords):
            return True
        if any(k in fname_no_ts for k in ("-brk-agro-", "-brk-fishing-", "-brk-motors-", "camisa-agro-", "camisa-de-pesca-", "camisa-pesca-")):
            return False
        return bool(re.search(r'(?:^|[-_.\s])(2|02|b)(?:[-_.\s]|masc|fem|inf|kids|bl|$)', fname_no_ts))

    def _is_explicit_back_name(self, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        fname = url.lower().split("/")[-1].split("?")[0]
        if fname.startswith("02_1918aa2d") or "zoom" in fname or "2-capa" in fname or "capa-2" in fname:
            return False
        if "productonchannel" in fname:
            return any(h in fname for h in self._EXPLICIT_BACK_POC_HASHES)
        if any(h in fname for h in self._EXPLICIT_BACK_POC_HASHES):
            return True
        if "frente" in fname or "mkpmaopunho" in fname:
            return False
        if any(
            w in fname for w in [
                "costas", "costa", "back", "traseira", "verso", "tras",
                "02fem", "02masc", "02inf", "02_fem", "02_masc", "02_inf",
                "02_", "-02."
            ]
        ):
            return True
        return bool(re.search(r'(?:^|[-_.\s])0?2[-_]?(?:fem|masc|inf)', fname))

    _HAND_GLOVE_POC_TOKENS = (
        "44c44e9612c4",  # CAX039BL[1]
        "f2e090fe8ba1",  # CAX028BL[1]
        "62aaf6b25986",  # CAX005[3]
        "d7f4f49cf301",  # CAX003BL[1]
        "8059f931198b",  # CAX005BL[3]
        "dc7c509bffe8",  # CAX039[1]
        "aa4b90bdb553",  # CAX034[1]
        "48aec41d5e02",  # CAX029[1]
    )

    _HUMANIZED_MODEL_TOKENS = (
        "aayvxta", "tb1io0b", "5m5m0yc", "iyewcrl", "dw7n5ow", "yx5ql6y", "nc5vehx", "vbu8izl",
        "gemini_generat", "psdemusoambiente", "emusoambiente", "psd_20em_20uso",
    )

    @classmethod
    def _is_hand_glove_photo(cls, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        fname = url.lower().split("/")[-1].split("?")[0]
        if "mkpmaopunho" in fname:
            return True
        if any(tok in fname for tok in cls._HAND_GLOVE_POC_TOKENS):
            return True
        if (
            re.match(r'^cax\d+(?:[._-]|$)', fname)
            and not any(k in fname for k in ("01fem", "02fem", "03fem", "01masc", "02masc", "03masc", "frente", "costas"))
            and not re.match(r'^cax\d+(?:bl|i)?[_-]?[1234]\.', fname)
        ):
            return True
        return False

    @classmethod
    def _is_humanized_model_photo(cls, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        fname = url.lower().split("/")[-1].split("?")[0]
        if any(tok in fname for tok in cls._HUMANIZED_MODEL_TOKENS):
            return True
        if re.match(r'^c028\d+(?:bl|i)?(?:_[0-9a-f-]+)?\.webp$', fname):
            return True
        return False

    def _select_apparel_act_images(self, cdn_images: List[str], is_female: bool = False, is_kids: bool = False, sku: str = "", title: str = ""):
        if not cdn_images:
            return "", "", ""
        if len(cdn_images) == 1:
            return cdn_images[0], "", ""

        # Caso especial CI075 / CI083 em brk_agro onde [0] foi nomeado 01_MASC mas é a Frente Infantil e [1]=10INF (Costas), [2]=11INF (Infográfico Frontal)
        if len(cdn_images) >= 3 and "01_masc" in cdn_images[0].lower() and "10inf" in cdn_images[1].lower():
            return cdn_images[0], cdn_images[1], cdn_images[2]

        # Filtragem inteligente de galerias mistas de família (MASC / FEM / INF no mesmo produto)
        def _classify_img_audience(u: str):
            fname = u.lower().split("?")[0].split("/")[-1]
            has_masc = (
                any(k in fname for k in ["masc", "man2", "homem"])
                or bool(re.search(r'^(?:casual|c0|cm)\d+(?:pp|p|m|g|gg|xg|xgg|g1|g2|g3)(?:[-_.\d]|$)', fname))
            )
            has_fem = (
                any(k in fname for k in ["fem", "mulher"])
                or bool(re.search(r'(?:^|[-_.\d])bl(?:[-_.\d]|$)', fname))
                or bool(re.search(r'^(?:casual|c0|cf|cm)\d+bl', fname))
            )
            has_inf = (
                any(k in fname for k in ["inf", "kids", "crianca", "juvenil"])
                or bool(re.search(r'^(?:casual|c0|cm)\d+i(?:pp|p|m|g|gg|g1|g2|\d+)?(?:[-_.\d]|$)', fname))
            )
            only_masc = has_masc and not has_fem and not has_inf
            only_fem = has_fem and not has_masc and not has_inf
            only_inf = has_inf and not has_masc and not has_fem
            return has_masc, has_fem, has_inf, only_masc, only_fem, only_inf

        working_images = list(cdn_images)
        if is_kids or is_female or any(_classify_img_audience(u)[3:] != (False, False, False) for u in cdn_images):
            preferred = []
            compatible = []
            for u in cdn_images:
                has_masc, has_fem, has_inf, only_masc, only_fem, only_inf = _classify_img_audience(u)
                if is_kids:
                    if has_inf:
                        preferred.append(u)
                    if not only_masc and not only_fem:
                        compatible.append(u)
                elif is_female:
                    if has_fem:
                        preferred.append(u)
                    if not only_masc and not only_inf:
                        compatible.append(u)
                else:
                    if has_masc:
                        preferred.append(u)
                    if not only_fem and not only_inf:
                        compatible.append(u)

            if len(compatible) < len(cdn_images):
                # Se a galeria é mista (ex: CASUAL288BL ['1masc', '2masc', '5fem', '6fem'] ou CASUAL003BL ['capa', '5-fem', '6-fem', '7-inf'])
                # e só existem 1 ou 2 fotos específicas do público-alvo (preferred), preferred[0] é 100% Frontal daquele público!
                if 1 <= len(preferred) <= 2 and len(cdn_images) >= 3:
                    p0 = preferred[0]
                    neutral_cands = [u for u in compatible if u not in preferred]
                    if not neutral_cands:
                        return (p0, (preferred[1] if len(preferred) == 2 else ""), "")
                    act1_img = neutral_cands[0]
                    act2_img = preferred[1] if len(preferred) == 2 else (neutral_cands[1] if len(neutral_cands) > 1 else act1_img)
                    return act1_img, act2_img, p0

                ordered_compatible = (
                    compatible
                    if (compatible and compatible[0] == cdn_images[0])
                    else (preferred + [u for u in compatible if u not in preferred] if preferred else compatible)
                )
                if len(ordered_compatible) >= 3:
                    working_images = ordered_compatible
                elif len(ordered_compatible) >= 1:
                    working_images = ordered_compatible

        if len(working_images) == 1:
            return working_images[0], "", ""
        if len(working_images) == 2:
            return working_images[0], working_images[1], ""

        fnames = [u.lower().split("?")[0].split("/")[-1] for u in working_images]
        sku_up = (sku or "").strip().upper()
        sku_t_low = f"{sku or ''} {title or ''}".lower()

        def _match_explicit_studio_num(fname_str: str):
            m_st = re.search(
                r'(?:^|\d{10,14}[-_]|[-_])(0?[1-9]|1[0-3])(?:[-_](?:20)?(?:masc|fem|inf|ffem)|masc|fem|inf|ffem)?(?:_\d)?(?:_(?:frente_costas|zoom_fem|zoom_masc|zoom))?(?:_[a-z0-9]{6})?(?:_[0-9a-f]{8}-[0-9a-f-]{27})?\.[a-z0-9]+$',
                fname_str
            )
            return int(m_st.group(1)) if m_st else None

        def _extract_ts4(fname_str: str) -> str:
            m_ts = re.match(r'^(\d{4})\d{6,10}[-_]', fname_str)
            return m_ts.group(1) if m_ts else ""

        ts0 = _extract_ts4(fnames[0])

        # =====================================================================
        # PILAR 1: GALERIAS COM 4 OU MAIS FOTOS
        # =====================================================================
        if len(working_images) >= 4:
            # Caso especial 0A: Camisas ArmorX (CAX*) com foto humanizada de mãos/dedeira em [1] ou [3]
            if self._is_hand_glove_photo(working_images[1]):
                # [0]=0° Frente, [1]=Humanized Hands/Glove, [2]=180° Costas Reta, [3]=Costas 3/4
                # Retorna (base1=[0], base2=[2] p/ Giro 180° Costas, base3=[1] p/ Ato 3 Mãos; unused4=[3] vai p/ Ato 2)
                return working_images[0], working_images[2], working_images[1]
            if self._is_hand_glove_photo(working_images[3]):
                # [0]=0° Frente, [1]=180° Costas Reta, [2]=Costas 3/4, [3]=Humanized Hands/Glove (CAX005, CAX005BL, CAX020, CAX022, CAX023)
                return working_images[0], working_images[1], working_images[3]

            # Caso especial 0B: Coleção Apache BRK Agro (C02833BL, C02834, C02833) onde [0]=180° Costas Estúdio, [1]=Humanizada Costas, [2]=3/4 Frente, [3]=0° Frente
            if sku_up in ("C02833BL", "C02834", "C02833"):
                return working_images[3], working_images[0], working_images[2]

            # Caso especial 0C: Coleção Apache BRK Agro (C02832BL..C02854BL) com foto humanizada frontal .webp em [1]
            if self._is_humanized_model_photo(working_images[1]) and fnames[1].startswith("c028"):
                if self._is_explicit_back_name(working_images[3]):
                    # [0]=3/4 Frente, [1]=Humanizada Frente .webp, [2]=0° Frente, [3]=180° Costas
                    return working_images[0], working_images[3], working_images[1]
                if self._is_explicit_back_name(working_images[2]):
                    # [0]=3/4 Frente, [1]=Humanizada Frente .webp, [2]=180° Costas, [3]=0° Frente
                    return working_images[0], working_images[2], working_images[1]

            # Caso especial RAGLAN230BL (1780685222215) onde [0] é a única foto Frontal e [1..3] são Costas
            if fnames[0].startswith("1780685222215"):
                return working_images[2], working_images[1], working_images[0]

            # Caso especial ADV131BL ([0]=02_fem Frente, [1]=01_fem_frente_costas Combo, [2]=03_fem Costas, [3]=04_zoom_fem Infográfico Frontal)
            if "01_fem_frente_costas" in fnames[1] and "02_fem" in fnames[0]:
                return working_images[0], working_images[2], working_images[3]

            # Caso especial 1-capa / 2-capa (ex: CI073, CI077, CI016I onde [0]=1-capa Humanizada Frente, [1]=2-capa Humanizada Frente, [2]=Estúdio 100% Frente, [3]=Estúdio Costas)
            if "2-capa" in fnames[1] or "capa-2" in fnames[1]:
                return working_images[0], working_images[3], working_images[2]

            # Caso especial C01824 / C01824BL com imagens geradas (gemini_generated_image / chatgpt_image) onde [1] é Costas e [3] é Frontal
            if sku_up.startswith("C01824") or any("gemini_generated_image" in f for f in fnames[1:3]):
                return working_images[0], working_images[1], working_images[3]

            # Se existe foto de zoom/infográfico frontal em [2] ou [3] (ex: C02350P_FULL, C02291, C02496BLP_FULL, C01971BL, FUSION39, FUSION83)
            if "03_zoom" in fnames[3] or "04_zoom" in fnames[3] or "11_zoom" in fnames[3]:
                return working_images[0], working_images[1], working_images[3]
            if "zoom" in fnames[2]:
                return working_images[0], working_images[1], working_images[2]
            if "zoom" in fnames[3]:
                return working_images[0], working_images[2], working_images[3]

            # Subcaso 1A: Série de 4 renders numerados 1..4
            seq_map = {}
            for idx_u, f in enumerate(fnames[:4]):
                st_num = _match_explicit_studio_num(f)
                if st_num in (1, 2, 3, 4) and "frente_costas" not in f and "zoom" not in f:
                    seq_map[st_num] = working_images[idx_u]
            if set(seq_map.keys()) != {1, 2, 3, 4}:
                glued_prefixes = []
                glued_map = {}
                for idx_u, f in enumerate(fnames[:4]):
                    m_gl = re.match(r'^((?:c0|casual|adv|cadv|fusion|hyb|cax|raglan)\d+(?:bl|i)?)([1234])\.[a-z0-9]+$', f)
                    if m_gl:
                        glued_prefixes.append(m_gl.group(1))
                        glued_map[int(m_gl.group(2))] = working_images[idx_u]
                if len(set(glued_prefixes)) == 1 and set(glued_map.keys()) == {1, 2, 3, 4}:
                    seq_map = glued_map
            if set(seq_map.keys()) == {1, 2, 3, 4}:
                # Sistema B (Capa Combo Frente+Costas em 1, Frente em 2, Costas em 3, 3/4 Frontal/Infográfico/Humanizada em 4):
                is_combo_1234 = (
                    sku_up.startswith("CCPBR")
                    or "ccpbr" in fnames[0]
                    or (ts0 == "1761" and (sku_up.startswith("HYB") or "hyb" in sku_t_low))
                    or (
                        not sku_up.startswith("ADV")
                        and ("01fem" in fnames[0] or ("1fem" in fnames[0] and "1_fem" not in fnames[0]))
                        and ts0 in {"1744", "1746", "1750", "1755", "1757", "1758", "1760", "1762", "1764", "1768", "1770", "1772"}
                    )
                    or fnames[0].startswith(("1790364852293", "1790354628351"))
                )
                if is_combo_1234:
                    return seq_map[1], seq_map[3], seq_map[4]
                # Sistema A padrão: 1 = Frente, 2 = Costas, 3 = 3/4 Frontal/Detalhe (Pula 4 = 3/4 Costas!)
                return seq_map[1], seq_map[2], seq_map[3]

            # Subcaso 1A-bis: Séries de estúdio {1, 4, 5, 6}, {1, 2, 5, 6}, {1, 2, 4, 5}
            nums_first4 = [_match_explicit_studio_num(f) for f in fnames[:4]]
            if set(nums_first4) == {1, 4, 5, 6}:
                s_map = {nums_first4[i]: working_images[i] for i in range(4)}
                if nums_first4[0] in (5, 6):
                    # RAGLAN270 ([5, 6, 1, 4]): [0]=5 Capa, 4=Costas, 1=Estúdio Frente
                    return working_images[0], s_map[4], s_map[1]
                return s_map[1], s_map[4], s_map[5]
            if set(nums_first4) == {1, 2, 5, 6}:
                s_map = {nums_first4[i]: working_images[i] for i in range(4)}
                if nums_first4[0] in (5, 6):
                    # RAGLAN235BL ([6,1,5,2]) / RAGLAN261 ([6,5,1,2]): [0]=6 Capa, 2=Costas, 1=Estúdio Frente
                    return working_images[0], s_map[2], s_map[1]
                return s_map[1], s_map[2], s_map[5]
            if set(nums_first4) == {1, 2, 4, 5}:
                s_map = {nums_first4[i]: working_images[i] for i in range(4)}
                if is_female:
                    return s_map[4], s_map[2], s_map[1]
                return s_map[1], s_map[2], s_map[4]

            # Se [0..2] são [1, 2, 3] ou [2, 1, 3] e [3] é uma foto extra não-numerada (ex: APC0259, PM098, C02522BL, C01973BL)
            if nums_first4[:3] in ([1, 2, 3], [2, 1, 3]) and nums_first4[3] is None and not self._is_explicit_back_name(working_images[3]):
                return working_images[0], working_images[2], working_images[3]

            # Se [0] é 1, [1] é uma foto extra não-numerada e [2..3] são [2, 3] (ex: RAGLAN157, CMB06, CAX032BL)
            if nums_first4 == [1, None, 2, 3]:
                if "03fem" in fnames[3] or "fishing" in fnames[1]:
                    return working_images[0], working_images[3], working_images[1]
                return working_images[0], working_images[2], working_images[3]

            # Se a 4ª foto ([3]) é explicitamente nomeada 'frenteperspectiva' / 'frente' (ex: ADV47BL, C02622BL, C02569BL, HYB087, CCPBR0783)
            if "frente" in fnames[3] and "costas" not in fnames[3]:
                if self._is_explicit_back_name(working_images[0]) and "frente" in fnames[2]:
                    # C02569BL: [0]=costas, [2]=frente, [3]=frenteperspectiva
                    return working_images[2], working_images[0], working_images[3]
                return working_images[0], working_images[2], working_images[3]

            # Subcaso 1B: Capa Externa/Humanizada/Combo em [0] + Renders de Estúdio em [1:]
            f0_num = nums_first4[0]
            rest_seq = {}
            for idx_u in range(1, len(working_images)):
                st_num = _match_explicit_studio_num(fnames[idx_u])
                if st_num is not None and st_num not in rest_seq:
                    rest_seq[st_num] = working_images[idx_u]

            if f0_num != 1 and 1 in rest_seq:
                if "frente" in fnames[0] and "costas" not in fnames[0] and not is_kids:
                    if 3 in rest_seq:
                        return working_images[0], (rest_seq.get(2) or working_images[2]), rest_seq[3]
                    if 5 in rest_seq:
                        return working_images[0], (rest_seq.get(2) or working_images[2]), rest_seq[5]
                back_cand = rest_seq.get(2) or rest_seq.get(3) or rest_seq.get(4) or rest_seq.get(9) or working_images[2]
                if back_cand == rest_seq[1]:
                    back_cand = working_images[1] if working_images[1] != rest_seq[1] else working_images[2]
                return working_images[0], back_cand, rest_seq[1]

            if f0_num is None:
                # Capa Externa em [0] + {5, 6, 7} ou {6, 7, 8} ou {7, 8, 9} em [1:4]
                if {5, 6, 7}.issubset(rest_seq.keys()):
                    if "frente_costas" in rest_seq[5].lower():
                        # C02041BLP_FULL / C01860BL: 5=Combo, 6=Estúdio Frente, 7=Estúdio Costas
                        return working_images[0], rest_seq[7], rest_seq[6]
                    # FUSION147BL / C01826BL / C01963BL: 5=Frente, 6=Costas, 7=Frontal
                    return working_images[0], rest_seq[6], rest_seq[7]
                if {6, 7, 8}.issubset(rest_seq.keys()):
                    # HYB021BL: 6=Combo, 7=Costas, 8=Frente
                    return working_images[0], rest_seq[7], rest_seq[8]
                if {7, 8, 9}.issubset(rest_seq.keys()):
                    if fnames[0].startswith(("c0492bl", "c02418bl")):
                        # C0492BL / C02418BL: 7=Combo, 8=Estúdio Frente, 9=Estúdio Costas
                        return working_images[0], rest_seq[9], rest_seq[8]
                    # C02362BL / C02371BL / C02410BL: 7=Combo/Frente, 8=Costas, 9=Humanizada Frontal
                    return working_images[0], rest_seq[8], rest_seq[9]

            # Subcaso 1C: Séries de estúdio numeradas de 4..13 sem capa externa em [0]
            if all(n is not None for n in nums_first4) and min(nums_first4) >= 4:
                if nums_first4[0] == 9 and set(nums_first4) == {7, 8, 9, 10}:
                    # ADV243BL ([9, 8, 7, 10]): 9=Costas, 8=Frente, 7=Combo, 10=Humanizada Frontal
                    return working_images[1], working_images[0], working_images[3]
                if nums_first4 in ([6, 7, 10, 11], [5, 6, 7, 9]) or (nums_first4 == [6, 7, 8, 9] and not is_female and not is_kids):
                    # C0883BL ([6,7,10,11]), C02040BL ([5,6,7,9]) e C02431 ([6,7,8,9] Masc): [2] é Frontal
                    return working_images[0], working_images[1], working_images[2]
                if nums_first4 in ([4, 5, 6, 7], [6, 5, 7, 10]) or fnames[0].startswith("174897"):
                    # C02492I ([4,5,6,7]), C01049BL ([6,5,7,10]) e C0554BL (174897): [3] é Humanizada Frontal
                    return working_images[0], working_images[2], working_images[3]
                if is_female or is_kids:
                    # Nas demais séries Femininas e Infantis >= 4 ([5,6,7,8], [5,6,7,10], [5,6,9,10], [6,7,8,9], [7,8,9,10], [7,8,9,12], [9,10,11,12], [9,12,13,10], [10,11,12,13]):
                    # [0]=Combo, [1]=Estúdio Frente (100% Frontal), [2]=Costas, [3]=Costas
                    return working_images[0], working_images[2], working_images[1]
                return working_images[0], working_images[2], working_images[3]

            # C01972BL / C02371BL com 3 números de estúdio >= 5
            if nums_first4[:3] in ([7, 6, 8], [6, 7, 8], [5, 6, 7], [6, 5, 7]) or set(n for n in nums_first4 if n is not None) == {7, 8, 9}:
                return working_images[0], working_images[2], working_images[3]

            # Caso especial C01828BL em brk_agro ([0]=Humanizada Frente, [1]=POC 180° Costas 171544dd, [2]=5_fem Combo, [3]=POC 0° Frente 6d0faf03)
            if "171544dd" in fnames[1] and "6d0faf03" in fnames[3]:
                return working_images[0], working_images[1], working_images[3]

            # Subcaso 1D-POC: Galerias productOnChannel (com ou sem capa humanizada em [0])
            poc_flags = ["productonchannel" in f for f in fnames[:4]]
            if (not poc_flags[0] and all(poc_flags[1:4])) or ("c1bd5af8" in fnames[0] and all(poc_flags[1:4])):
                backs_poc = [u for u in working_images[1:4] if self._is_explicit_back_name(u)]
                fronts_poc = [u for u in working_images[1:4] if not self._is_explicit_back_name(u)]
                if backs_poc and fronts_poc:
                    return working_images[0], backs_poc[0], fronts_poc[0]
                return working_images[0], working_images[2], working_images[1]

            if all(poc_flags[:4]) and self._is_explicit_back_name(working_images[0]) and not self._is_explicit_back_name(working_images[1]):
                front0 = working_images[1]
                back0 = working_images[0]
                act3_cand = working_images[2] if not self._is_explicit_back_name(working_images[2]) else working_images[3]
                return front0, back0, act3_cand

            # Subcaso 1D: 4 fotos de estúdio explicitamente nomeadas ([0]=FRENTE, [1]=COSTAS, ...)
            if "frente" in fnames[0] and self._is_explicit_back_name(working_images[1]):
                img1 = working_images[0]
                non_back_rest = [u for u in working_images[1:] if not self._is_explicit_back_name(u)]
                if non_back_rest:
                    return img1, working_images[1], non_back_rest[0]
                return working_images[2], working_images[1], working_images[0]

            # Subcaso 1E: Se AMBAS [2] e [3] forem explicitamente Costas (ex: C0889I ['01inf', '10_frente', '02inf', '11_costas'], RAGLAN174, HYB092BL)
            if self._is_explicit_back_name(working_images[2]) and self._is_explicit_back_name(working_images[3]):
                return working_images[0], working_images[2], working_images[1]

            # Se a 4ª foto ([3]) for explicitamente Costas e a 3ª ([2]) NÃO for Costas (ex: CMB01, CM024BL, CI061, CI062, C01196)
            if self._is_explicit_back_name(working_images[3]) and not self._is_explicit_back_name(working_images[2]):
                return working_images[0], working_images[3], working_images[2]

            # Se a 3ª foto ([2]) for explicitamente Costas e a 4ª ([3]) NÃO for Costas
            if self._is_explicit_back_name(working_images[2]) and not self._is_explicit_back_name(working_images[3]):
                return working_images[0], working_images[2], working_images[3]

            # Se a 2ª foto ([1]) for explicitamente Costas e a 3ª ([2]) NÃO for Costas (ex: C01828 OTH:237, CM024BL OTH:151, CAX005 OTH:357, CF033I OTH:083)
            if self._is_explicit_back_name(working_images[1]) and not self._is_explicit_back_name(working_images[2]):
                return working_images[0], working_images[1], working_images[2]

            # Subcaso 1F: Galerias productOnChannel de 4+ fotos
            if poc_flags[:4] == [False, False, True, True]:
                # C01828 / C01828BL: [0]=Humanizada, [1]=Frente, [2]=POC Costas, [3]=POC 3/4 Frontal
                return working_images[0], working_images[2], working_images[3]

            if all(poc_flags[:4]):
                if any(k in sku_t_low for k in ("raglan", "segunda pele", "hyb")) or is_kids:
                    return working_images[0], working_images[1], working_images[3]
                return working_images[0], working_images[1], working_images[2]

            # Subcaso 1G: Fallback para demais galerias de 4+ fotos
            if sku_up.startswith("ADV"):
                return working_images[0], working_images[2], working_images[3]
            if any(k in fnames[0] for k in ("-brk-agro-", "-brk-fishing-", "-brk-motors-", "camisa-agro-", "camisa-de-pesca-", "camisa-pesca-", "camisa-uv")):
                # Galeria de 4 fotos com nomes SEO-slug de estúdio sem capa externa em [0] ([0]=Frente, [1]=Costas, [2]=3/4 Frente, [3]=3/4 Costas)
                return working_images[0], working_images[1], working_images[2]
            return working_images[0], working_images[2], working_images[1]

        # =====================================================================
        # PILAR 2: GALERIAS COM EXATAMENTE 3 FOTOS (len == 3)
        # =====================================================================
        if self._is_hand_glove_photo(working_images[1]):
            # CAX003BL: [0]=0° Frente, [1]=Humanized Hands/Glove, [2]=180° Costas Reta
            return working_images[0], working_images[2], working_images[1]
        if self._is_hand_glove_photo(working_images[2]):
            return working_images[0], working_images[1], working_images[2]

        non_back_all = [u for u in working_images if not self._is_explicit_back_name(u)]
        if len(non_back_all) == 1:
            # Se só existe 1 única foto Frontal e 2 fotos explicitamente Costas (ex: C02826, C02837BL),
            # garante que a única foto Frontal vá para o Ato 3!
            only_front = non_back_all[0]
            backs = [u for u in working_images if u != only_front]
            return backs[0], backs[1], only_front

        # C01367I: ['1755030263590-01inf.jpg', '1752600866747-1_frente_...', '1755030264276-02inf.jpg'] onde [0] (01inf) é a única foto Frontal pura
        if fnames[0].startswith("1755030263590"):
            return working_images[1], working_images[2], working_images[0]

        nums3 = [_match_explicit_studio_num(f) for f in fnames[:3]]

        if nums3 in ([2, 3, 4], [1, 2, 5], [1, 5, 6]):
            # C02871I ([2,3,4]), C01590M_FULL ([1,2,5]), CI076 ([1,5,6]): [0] é a única foto Frontal e [1]/[2] são Costas
            return working_images[1], working_images[2], working_images[0]

        if nums3 == [2, 1, 3]:
            # C02796: [0]=02masc Costas, [1]=01masc Frente, [2]=03masc Costas
            return working_images[0], working_images[2], working_images[1]

        if nums3 == [6, 5, 7]:
            # ADV288BL / C01978BL: [0]=6_fem Frente pura, [1]=5_fem Combo, [2]=7_fem Costas
            return working_images[1], working_images[2], working_images[0]

        if nums3 == [8, 9, 7]:
            # C01044BLP_FULL: [0]=8_fem Frente, [1]=9_fem Costas, [2]=7_fem Combo
            return working_images[2], working_images[1], working_images[0]

        img1 = working_images[0]
        if self._is_explicit_back_name(img1):
            if non_back_all:
                img1 = non_back_all[0]

        rem = [u for u in working_images if u != img1]
        if len(rem) < 2:
            return img1, (rem[0] if rem else ""), ""

        # 2-Combo: Galerias de 3 fotos onde [0] é Combo (Frente+Costas), [1] é Frente e [2] é Costas:
        if nums3 == [1, 2, 3]:
            is_combo_123 = (
                sku_up.startswith("CCPBR")
                or "ccpbr" in fnames[0]
                or ("01fem" in fnames[0] and bool(ts0) and int(ts0) < 1775)
            )
            if is_combo_123:
                return working_images[0], working_images[2], working_images[1]
            return working_images[0], working_images[1], working_images[2]

        if (
            nums3 in ([6, 7, 8], [7, 8, 9], [7, 8, 11], [9, 12, 13])
            or (nums3 == [5, 6, 7] and ("frente_costas" in fnames[0] or (ts0 in {"1760", "1761", "1768"} and not sku_up.startswith("FUSION"))))
            or (nums3[0] is None and "frente" not in fnames[0] and nums3[1] == 1 and nums3[2] in (2, 3))
        ):
            # [2] é Costas e [1] é Frente/Combo -> Ato 2 recebe [2] (Costas) e Ato 3 recebe [1] (Frente)
            return working_images[0], working_images[2], working_images[1]

        # 2A: Se rem[0] é explicitamente Costas e rem[1] NÃO é Costas,
        # Ato 2 fica com Costas (rem[0]) e Ato 3 fica com Frontal (rem[1])
        if self._is_explicit_back_name(rem[0]) and not self._is_explicit_back_name(rem[1]):
            return img1, rem[0], rem[1]

        # 2B: Se rem[1] é explicitamente Costas e rem[0] é Frente (ex: ['Capa.jpg', '-01.jpg', '-02.jpg']),
        # Ato 2 fica com Costas (rem[1]) e Ato 3 fica com Frente (rem[0])
        if self._is_back_view_url(rem[1]) and not self._is_back_view_url(rem[0]):
            return img1, rem[1], rem[0]

        # 2C: Lotes productOnChannel em galerias de 3 fotos:
        # SOMENTE quando [0] é uma Capa Externa (g0 is None) e [1], [2] são do mesmo grupo productOnChannel (g1 == g2)
        poc_re = re.compile(r'productonchannel(?:_2f|/)images(?:_2f|/)(\d+)', re.IGNORECASE)
        g0 = poc_re.search(img1).group(1) if poc_re.search(img1) else None
        g1 = poc_re.search(rem[0]).group(1) if poc_re.search(rem[0]) else None
        g2 = poc_re.search(rem[1]).group(1) if poc_re.search(rem[1]) else None
        if g0 is None and g1 and g2 and g1 == g2:
            return img1, rem[1], rem[0]

        # 2D: Padrão 3 fotos de estúdio na mesma sequência ([0]=Frente, [1]=Costas, [2]=3/4 Frontal)
        return img1, rem[0], rem[1]

    _HUMANIZED_BACK_COVER_SKU_PREFIXES = (
        "BP10", "C02893", "C02894", "C02895", "C02896", "C02897",
        "C02864", "C02865", "C02863", "C02861", "C02860",
        "C02830", "C02829", "C02827", "C02826", "C02824", "C02822",
        "C02884", "C02879", "C02875",
    )

    def _resolve_apparel_act_and_360_images(self, cdn_images: List[str], is_female: bool = False, is_kids: bool = False, sku: str = "", title: str = ""):
        """
        Alocação inteligente de 4 slots (Ato 1 Face 1, Ato 1 Face 2 Giro 360°, Ato 2 Lupa, Ato 3 Lupa)
        sem JAMAIS duplicar nenhuma foto na descrição e mapeando capas humanizadas de Costas (180° Costas -> 0° Frente)
        vs. capas humanizadas/estúdio de Frente (0° Frente -> 180° Costas).
        """
        base1, base2, base3 = self._select_apparel_act_images(
            cdn_images, is_female=is_female, is_kids=is_kids, sku=sku, title=title
        )
        if not cdn_images or len(cdn_images) < 4:
            return base1, base2, base3, "", False

        # Reaplica filtro de público-alvo sobre cdn_images para extrair a 4ª foto compatível (unused4)
        def _classify_aud(u: str):
            fname = u.lower().split("?")[0].split("/")[-1]
            has_masc = any(k in fname for k in ["masc", "man2", "homem"]) or bool(re.search(r'^(?:casual|c0|cm)\d+(?:pp|p|m|g|gg|xg|xgg|g1|g2|g3)(?:[-_.\d]|$)', fname))
            has_fem = any(k in fname for k in ["fem", "mulher"]) or bool(re.search(r'(?:^|[-_.\d])bl(?:[-_.\d]|$)', fname)) or bool(re.search(r'^(?:casual|c0|cf|cm)\d+bl', fname))
            has_inf = any(k in fname for k in ["inf", "kids", "crianca", "juvenil"]) or bool(re.search(r'^(?:casual|c0|cm)\d+i(?:pp|p|m|g|gg|g1|g2|\d+)?(?:[-_.\d]|$)', fname))
            return has_masc and not has_fem and not has_inf, has_fem and not has_masc and not has_inf, has_inf and not has_masc and not has_fem

        working_pool = list(cdn_images)
        if is_kids or is_female or any(_classify_aud(u) != (False, False, False) for u in cdn_images):
            compat = []
            for u in cdn_images:
                om, of, oi = _classify_aud(u)
                if is_kids and not om and not of:
                    compat.append(u)
                elif is_female and not om and not oi:
                    compat.append(u)
                elif not is_kids and not is_female and not of and not oi:
                    compat.append(u)
            if compat:
                working_pool = compat

        used_base = {u for u in (base1, base2, base3) if u}
        unused4 = [u for u in working_pool if u and u not in used_base]
        if not unused4:
            return base1, base2, base3, "", False

        f0 = (base1 or working_pool[0]).lower().split("?")[0].split("/")[-1]
        sku_up = (sku or "").strip().upper()
        is_humanized_cover = ("productonchannel" not in f0) or ("c1bd5af8" in f0)
        studio_backs_in_rest = sum(1 for u in working_pool[1:4] if self._is_explicit_back_name(u))
        is_humanized_back_cover = is_humanized_cover and (
            "c1bd5af8" in f0
            or any(sku_up.startswith(p) for p in self._HUMANIZED_BACK_COVER_SKU_PREFIXES)
            or (
                studio_backs_in_rest >= 2
                and not any(k in f0 for k in ("frente", "01_", "1_", "01fem", "01masc", "01inf", "1fem", "1masc", "1inf"))
                and "productonchannel" in working_pool[1].lower()
            )
        )

        if is_humanized_back_cover:
            # Capa Humanizada de Costas (180° Costas):
            # - Ato 1 Face 1 (180° Costas): base1 (Humanizada de Costas)
            # - Ato 1 Face 2 (0° Frente): base3 (Estúdio 0° Frente)
            # - Ato 2 (Lupa): base2 (Estúdio 180° Costas)
            # - Ato 3 (Lupa): unused4[0] (Estúdio 3/4)
            return base1, base2, unused4[0], base3, True

        # Capa de Frente (Humanizada Frontal ou Estúdio 0° Frente):
        # - Ato 1 Face 1 (0° Frente): base1 (Capa Frontal)
        # - Ato 1 Face 2 (180° Costas): base2 (Estúdio 180° Costas)
        # - Ato 2 (Lupa): unused4[0] (4ª foto distinta de estúdio)
        # - Ato 3 (Lupa): base3 (Estúdio Frontal / 3/4 Frente / Detalhe)
        return base1, unused4[0], base3, base2, False

    def _select_cutlery_act_images(self, cdn_images: List[str], title: str = ""):
        """
        Seleciona cirurgicamente as fotos de cada Ato para a linha de Cutelaria (cutlery_unique),
        garantindo alinhamento visual-textual absoluto:
        - Ato 1: Conjunto Completo / Lâmina Principal
        - Ato 2: Close-up da Empunhadura / Cabo (Madeira, Resina, Isca Encapsulada, Torneado)
        - Ato 3: Bainha de Couro / Estojo / Uso Prático (nunca escolhe fotos gráficas .png de cota quando há fotos reais de estúdio)
        """
        if not cdn_images:
            return "", "", ""
        if len(cdn_images) == 1:
            return cdn_images[0], "", ""
        if len(cdn_images) == 2:
            return cdn_images[0], cdn_images[1], ""
        if len(cdn_images) == 3:
            return cdn_images[0], cdn_images[1], cdn_images[2]

        t_low = (title or "").lower()

        # 1. Cutelo 6" em Inox (5 fotos: [0]=lâmina, [1]=cortando costela, [2]=cabo madeira, [3]=corpo inteiro, [4]=cota .png)
        if "cutelo" in t_low:
            return cdn_images[0], cdn_images[2], cdn_images[1]

        # 2. Kit Faca e Chaira Karandá (8 fotos: [0]=conjunto, [1]=cota .png, [2]=afiando, [3]=bainha close-up, [4]=faca+chaira cabos)
        if ("kit faca" in t_low or "chaira" in t_low) and ("karand" in t_low):
            img2 = cdn_images[4] if len(cdn_images) > 4 else cdn_images[2]
            img3 = cdn_images[3] if len(cdn_images) > 3 else cdn_images[2]
            return cdn_images[0], img2, img3

        # 3. Kit Faca e Chaira BRK 9" Floral / Trançada (8 fotos: [0]=conjunto, [1]=afiando, [2]=cota .png, [3]=detalhe cabos, [5]=bainha couro)
        if "kit faca" in t_low or "chaira" in t_low:
            img2 = cdn_images[3] if len(cdn_images) > 3 else cdn_images[1]
            img3 = cdn_images[5] if len(cdn_images) > 5 else (cdn_images[4] if len(cdn_images) > 4 else cdn_images[1])
            return cdn_images[0], img2, img3

        # 4. Facas Compactas de Cintura: Faca Rodeio 5" & Faca Curva 3" (8 fotos)
        # Evita fotos .png de cota gráfica (ex: -2.png, -3.png, -4.png, -5.png) e prioriza close-up do cabo (Ato 2) e faca na bainha (Ato 3)
        if "rodeio" in t_low or "curva" in t_low:
            img1 = cdn_images[0]
            non_png_rest = [u for u in cdn_images[1:] if not u.lower().split("?")[0].endswith(".png")]
            if len(non_png_rest) >= 2:
                # Em galerias de 8 fotos BRK Rodeio/Curva, non_png_rest[0] é close-up do cabo/conjunto e non_png_rest[1] é faca na bainha
                return img1, non_png_rest[0], non_png_rest[1]
            img2 = cdn_images[3] if len(cdn_images) > 3 else cdn_images[1]
            img3 = cdn_images[4] if len(cdn_images) > 4 else (cdn_images[2] if len(cdn_images) > 2 else img2)
            return img1, img2, img3

        # 5. Facas 10" Cabo em Madeira e Resina (Pescaria com Isca / Resina com Abridor - 6 a 8 fotos)
        # [0]=conjunto faca+bainha, [1]=ambientada, [2]=close-up do cabo em resina/isca, [3]=close-up lâmina, [4]=faca na bainha de couro
        if "resina" in t_low:
            img1 = cdn_images[0]
            img2 = cdn_images[2] if len(cdn_images) > 2 else cdn_images[1]
            img3 = cdn_images[4] if len(cdn_images) > 4 else cdn_images[3]
            return img1, img2, img3

        # 6. Facas 10" em Inox Personalizadas / Abridor de Garrafa (6 a 7 fotos)
        # [0]=conjunto faca+bainha, [1]=ambientada, [2]=close-up cabo madeira e gravação, [3]=bainha de couro costurada
        if "inox" in t_low and ('10"' in t_low or "10 " in t_low or "abridor" in t_low):
            img2 = cdn_images[2] if len(cdn_images) > 2 else cdn_images[1]
            img3 = cdn_images[3] if len(cdn_images) > 3 else (cdn_images[2] if len(cdn_images) > 2 else img2)
            return cdn_images[0], img2, img3

        # 7. Facas Artesanais Gaúchas Forjadas (4 a 7 fotos: [0]=faca+bainha, [3]=detalhe lâmina/cabo, [1]=certificado/especificações)
        if "artesanal" in t_low and len(cdn_images) >= 4:
            return cdn_images[0], cdn_images[3], cdn_images[1]

        # 8. Canivetes Táticos e demais itens de cutelaria
        return cdn_images[0], cdn_images[1], cdn_images[2]

    # Tokens de fotos de catálogo de fornecedor onde a isca está SEM garatéias (apenas o corpo/pitões sem anzol).
    # NUNCA devem ser exibidas nos Atos (especialmente no Ato 3 "Garatéias de Alta Resistência").
    HOOKLESS_LURE_IMAGE_TOKENS = (
        "1755631990951",  # Kisu 01 tem garatéia, então filtramos apenas 17556320* abaixo!
    )
    HOOKLESS_LURE_SUBSTRINGS = (
        "17556320",   # Marine Sports Kisu (02, 24, 31, 38-G sem garatéia)
        "175563244",  # Marine Sports Invader MR 110F (14 sem garatéia)
        "175563245",  # Marine Sports Invader MR 110F (24 sem garatéia)
        "175563246",  # Marine Sports Invader MR 110F (BCT66, BOT61 sem garatéia)
        "175563247",  # Marine Sports Invader MR 110F (CTT70 sem garatéia)
        "175563248",  # Marine Sports Invader MR 110F (N4 sem garatéia)
        "175563249",  # Marine Sports Invader MR 110F (WOS74 sem garatéia)
        "175563255",  # Marine Sports Invader MR 110F (PYOT73 sem garatéia)
        "17556365",   # Marine Sports Predator SR 115S (14, 24, 24MG sem garatéia)
        "17556366",   # Marine Sports Predator SR 115S (BCT66..WOS74 sem garatéia)
        "17556370",   # Marine Sports Predator SR 115S (N4, SHT63 sem garatéia)
        "17556390",   # Marine Sports Savage 95 (BGO sem garatéia)
        "17556913",   # Marine Sports Inna 90 (38G, 104, 108, WOT sem garatéia)
        "17556915",   # Marine Sports Savage 85 (BGO sem garatéia)
        "175630609",  # Rapala XRAP XRD (HS sem garatéia)
        "175630611",  # Rapala XRAP XRD (OG, S sem garatéia)
        "17563904",   # Marine Sports Brava 90 (110 sem garatéia) e Savage 95 (BGO sem garatéia)
        "17563913",   # Rapala Precision Xtreme Pencil 107 (FHC sem garatéia)
        "175640425",  # CCM Stick Letal 90 (16 sem garatéia)
        "htaipoi",    # Marine Sports Inna 90 (sem garatéia)
        "trrcouw",    # CCM Stick Letal 90 (sem garatéia)
        "ngmpqqt",    # CCM Stick Letal 90 (sem garatéia)
        "4p1iqiy",    # Yara Encrenca 9cm (sem garatéia)
        "8yy2b7x",    # Yara Encrenca 9cm (sem garatéia)
        "qngeftb",    # Yara Encrenca 9cm (sem garatéia)
        "wlc1umo",    # Yara Encrenca 9cm (sem garatéia)
        "buuvmhx",    # Yara Encrenca 9cm (sem garatéia)
        "lesihbz",    # Yara Encrenca 9cm (sem garatéia)
    )

    # Mapa homologado por distância cromática RGB (maximin) + deduplicação de prefixo de cor + 100% COM GARATÉIAS
    # Garante que cada isca exiba variações de cores 100% distintas e armadas com garatéias nos 3 Atos
    LURE_DIVERSE_IMAGE_PICKS = {
        "7539624771650": ["1-capa-80.jpg", "vxlBXlr_c8a16eea-cb0e-4526-adee-a2317eb1e117.jpg", "VXDSa7Z_a9bd0781-d15c-4d7a-924a-9b3a0197a2d6.jpg", "1755031950521-N11_3fabac3f-2bb9-481e-97ec-dae0805a4533.jpg"],
        "7872731906114": ["mwfv6pS.jpg", "dG8SXB6.jpg", "suMM8DG.jpg", "QIqUILH.jpg"],
        "7539606519874": [
            "1-capa_7697faeb-b125-49cd-8176-bacf201d1344.jpg",
            "isca_artificial_nelson_nakamura_lucky_sogra_9cm_12g_36080_3_c04c6990d472e653deceb89fed5abd35_ff8619d3-8495-40b4-9070-8d11b619c998.jpg",
            "isca_artificial_nelson_nakamura_lucky_sogra_9cm_12g_36080_1_ffc3977d12d9145d7039abb891b09a6f_2c982f95-462b-4036-9963-819b97391586.jpg",
            "isca_artificial_nelson_nakamura_lucky_sogra_9cm_12g_36080_4_37cc76b697ede7e7580d134f201fe7e3.jpg",
        ],
        "7539625263170": ["1-capa-8-5.jpg", "rlReMCy.jpg", "FVZ1UA0.jpg", "zw7ZLwH.jpg"],
        "7539965132866": ["1-capa_2b8c1727-287e-42a9-b434-3d50b1fe632c.jpg", "6I36Gw4.jpg", "IZntQpk.jpg", "aJtuCBg.jpg"],
        "7539965100098": ["1-capa_fc37e5ae-98ed-44b0-a4e5-57fd0ff74953.jpg", "4pZfPPC.jpg", "U6f9YYe.jpg", "aJd3xbK.jpg"],
        "7539965198402": ["capa-1_b4ed0f33-008b-4088-afb6-64fdb687e4f8.jpg", "pUHgJWp.jpg", "BUz9MHU.jpg", "VmlZnNK.jpg"],
        "8369524047938": ["EMfYTYA_b512e97b-9cd7-4395-bb16-1d8ffa962f2e.jpg", "9NlUFZD_e852724e-1f31-4566-95c0-b1b9db733bc4.jpg", "ca0p2HE_c9ca1351-b460-486f-9fce-de7a14a0796d.jpg", "M0Z6489_1acbf535-62a7-4693-93df-69d2f7fc97fe.jpg"],
        "7539964870722": ["1-capa_c2c26de5-529f-4c14-9015-34f436243578.jpg", "HEvkpc6.jpg", "x2hw3PW.jpg", "ZMsJaAi.jpg"],
        "7860235501634": ["xKo0czs.jpg", "ZEouqcE.jpg", "AEfeyMo.jpg", "ncQZTUY.jpg"],
        "7860235796546": ["aa3b94d3-a88c-41f6-b823-dd35972d1b06.png", "29.png", "H87g4Qi.png", "30.png"],
        "7874266136642": ["UXR6ec0.jpg", "j6AxVhs.jpg", "CWd0bMX.jpg", "MMdtVQE.jpg"],
        "7874413068354": ["24.png", "3182bddb-7ede-46e2-9596-0bc66144cd58.png", "26.png", "45.png"],
        "7872610828354": ["FSvorM8.jpg", "tsYV59E.jpg", "uX8YWv2.jpg", "DEneCgk.jpg"],
        "7539328122946": ["1-capa_96cf9845-5c1b-43db-846d-a08af81136b9.jpg", "uKcMELH.jpg", "87EmjtE.jpg", "1756404140708-LIGHT-BLUE-BACK.jpg"],
        "7539328090178": ["1-capa_ec07ad6a-ae1b-4467-bbcc-3dcc37d8d9b9.jpg", "GXNFeNc.jpg", "JuvocWR.jpg", "1756307030216-CHARTREUSE-WH.jpg"],
        "7874566258754": ["2XRQjuy.jpg", "Q8FXdbJ.jpg", "gy9mxN9.jpg", "X1Kgj1m.jpg"],
        "7540011925570": ["1-capa_805f1121-8f55-4512-ac93-112893f39c88.jpg", "1756306148800-80.jpg", "1756306155383-81.jpg", "1756306173116-83.jpg"],
        "7873835860034": ["B0t7VtY.jpg", "UoZboWr.jpg", "acy5nZE.jpg", "eZ8GqTz.jpg"],
        "7873697644610": ["VPHilhk.jpg", "aVlidQH.jpg", "iZHTnuL.jpg", "3RKuo3h.jpg"],
        "7539626082370": ["1-xapa_1095c658-11d1-4a99-b392-b9417a7ea070.jpg", "hyvLRpp.jpg", "1LPYD60.jpg", "j3JkYWO.jpg"],
        "7539626180674": ["1-capa_2b3baf7c-c41e-4328-b05a-9cb3713c5c50.jpg", "hgAIqd7.jpg", "qHXuT2L.jpg", "IscadePescaBrancacomOlhoHolografico.png"],
        "7539625132098": ["1-capa_a3c3541b-81eb-44af-91c9-5377f38aa4bb.jpg", "ISnymzY.jpg", "OmKmFDe.jpg", "6Wj4t0B.jpg"],
        "7872703594562": ["vlm0OkE.jpg", "Vkn893r.jpg", "kaHKdxL.jpg", "kC3kjAn.jpg"],
        "7872313327682": ["re1.png", "re3.png", "re2.png", "Iscametalicalistradacomanzoltriplo_ed76db07-368a-48d4-a0bc-09db7f6b9524.png"],
        "7872155385922": ["AnunciodeIscasBRKFishing.png", "jl1.png", "jl2.png", "jl3.png"],
        "7539624837186": ["IscaPredatorMarineFlutuante.png", "50.png", "54.png", "hj1.png"],
        "7540011466818": ["1-capa_0d5834e8-4b3a-4a88-b3ed-1edc4f7f00b9.jpg", "df1.png", "Iscadepescaneoncomganchostriplos.png"],
        "7539625918530": ["1-capa_5b81291d-f33e-4bde-89f6-f5af920d463a.jpg", "YQVNSch.jpg", "fe1S4a6.jpg", "xW4FItG.jpg"],
        "7539607142466": ["1-capa-ipon-80.jpg", "N3z4plS.jpg", "Svke56p.jpg", "82VEssQ.jpg"],
        "7539607175234": ["1-capa_afa556c1-9857-40cc-93a4-6aab388853c4.jpg", "1756214711581-108.jpg", "1756214720696-201.jpg", "1756214735165-202.jpg"],
        "7539606749250": ["1-capa_e1bced8c-c452-4471-ba47-cd87239738c8.jpg", "EaB1Gec.jpg", "bfmgjKJ.jpg", "9xiH8tS.jpg"],
        "7539606716482": ["1-capa-8-5cm.jpg", "bTBY4hE.jpg", "mvWRNFj.jpg", "wbmDDaR.jpg"],
        "7539625001026": ["1-capa-85.jpg", "5FKfm4Q.jpg", "cnznqYX.jpg", "YFm4XlE.jpg"],
        "7539316817986": ["capa-90-1.jpg", "ZO8uYGY.jpg", "PMqZokI.jpg", "S7hZsPI.jpg"],
        "7538279055426": ["1-capa_b63d1445-1eea-4e9d-aedf-ba0c90aed018.jpg", "RR4UqEg.jpg", "4UW2vJf.jpg", "sKpK01i_6b7a3445-415f-4b15-a5d4-818d50e7bd24.jpg"],
        "7539316883522": ["1-capa_742aa0c7-dc1b-4573-9bb3-247507d0639f.jpg", "qSY7Knx.jpg", "Atony3C.jpg", "YyjN4Xo.jpg"],
        "7538360778818": ["1-capa_ea35434c-f231-4ce0-86e4-6f2130e63c35.jpg", "nVb8YQm.jpg", "69Z32EA.jpg", "cbA2bif.jpg"],
        "7539949600834": ["1-capa_e508f7a7-d97a-4e7a-b7b8-d7ef5897bc07.jpg", "bonIJm5.jpg", "BGGiHKy.jpg", "ezPCPVu.jpg"],
        "7873393885250": ["Soml0zX.jpg", "ac2cb4ef-d970-4417-806c-dc1e7a7a6bc9.png", "p2BBsGV.jpg", "SDuySHA.jpg"],
    }

    def _is_hookless_lure_image(self, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        fn = url.lower().split("?")[0].split("/")[-1]
        return any(tok in fn for tok in self.HOOKLESS_LURE_SUBSTRINGS)

    def _select_lure_act_images(self, cdn_images: List[str], variants: List[Any] = None, product_id: str = "", title: str = "") -> Tuple[Optional[List[str]], str, str, str]:
        """
        Seleciona imagens de variações de iscas 100% distintas e COM GARATÉIAS para os 3 Atos:
        - NUNCA seleciona `2-capa` (cdn_images[1], que repete a mesma isca da capa sem texto).
        - NUNCA seleciona fotos de catálogo sem garatéia (`HOOKLESS_LURE_SUBSTRINGS`).
        - Evita a foto de fundo branco da mesma cor da capa (geralmente em cdn_images[2]) e códigos de mesma família cromática (ex: 24 e 24MG).
        - Para iscas de apenas 3 cores no total (5 fotos sendo 3 da cor da capa), aloca 1 cor distinta por Ato sem Split Media.
        """
        if not cdn_images:
            return None, "", "", ""
        pid_str = str(product_id or "").strip()
        if pid_str in self.LURE_DIVERSE_IMAGE_PICKS:
            target_fnames = self.LURE_DIVERSE_IMAGE_PICKS[pid_str]
            fname_to_url = {u.split("?")[0].split("/")[-1].lower(): u for u in cdn_images if u}
            matched = [fname_to_url.get(fn.lower()) for fn in target_fnames]
            if all(matched):
                if len(matched) == 4:
                    return [matched[0], matched[1]], matched[0], matched[2], matched[3]
                elif len(matched) == 3:
                    return None, matched[0], matched[1], matched[2]

        img1 = cdn_images[0]
        banner_toks = ("catalogobrkfishing", "chatgpt", "capacategoria", "prancheta")
        clean_rest = [
            u for u in cdn_images[1:]
            if not any(t in u.lower() for t in banner_toks)
            and not self._is_hookless_lure_image(u)
        ]
        has_any_hookless = any(self._is_hookless_lure_image(u) for u in cdn_images[1:])
        if has_any_hookless:
            # Se a galeria tinha fotos sem garatéia que foram filtradas, remove também 2-capa para usar apenas fotos válidas com garatéia
            valid_hooked_rest = [
                u for u in clean_rest
                if not any(
                    k in u.split("?")[0].split("/")[-1].lower()
                    for k in ("2-capa", "2_capa", "capa-2", "capa_2", "capa-90-2")
                )
            ]
            pool_all = [img1] + valid_hooked_rest
        else:
            pool_all = [img1] + (clean_rest if len(clean_rest) >= 3 else cdn_images[1:])
        n = len(pool_all)
        var_len = len(variants) if variants else 0

        if n >= 6:
            raw_cands = pool_all[1:] if has_any_hookless else pool_all[3:]
            dedup_cands = []
            seen_roots = set()
            for u in raw_cands:
                fn = u.split("?")[0].split("/")[-1].rsplit(".", 1)[0]
                m = re.search(r"^\d{10,14}[-_]([A-Za-z]*\d+)", fn)
                root = m.group(1).upper() if m else None
                if root and root in seen_roots:
                    continue
                if root:
                    seen_roots.add(root)
                dedup_cands.append(u)
            cands = dedup_cands if len(dedup_cands) >= 3 else raw_cands
            v1 = cands[0]
            v2 = cands[len(cands) // 2]
            v3 = cands[-1]
            return [img1, v1], img1, v2, v3
        elif n == 5:
            if var_len and var_len <= 3:
                return None, img1, pool_all[3], pool_all[4]
            if has_any_hookless:
                return [img1, pool_all[1]], img1, pool_all[2], pool_all[4]
            return [img1, pool_all[3]], img1, pool_all[2], pool_all[4]
        elif n == 4:
            fn1 = pool_all[1].split("?")[0].split("/")[-1].lower()
            if "capa" in fn1 or fn1.startswith("2_") or fn1.startswith("2-"):
                return None, img1, pool_all[2], pool_all[3]
            return [img1, pool_all[1]], img1, pool_all[2], pool_all[3]
        elif n == 3:
            fn1 = pool_all[1].split("?")[0].split("/")[-1].lower()
            if "capa" in fn1 or fn1.startswith("2_") or fn1.startswith("2-"):
                return None, img1, pool_all[2], ""
            return None, img1, pool_all[1], pool_all[2]
        elif n == 2:
            fn1 = pool_all[1].split("?")[0].split("/")[-1].lower()
            if "capa" in fn1 or fn1.startswith("2_") or fn1.startswith("2-"):
                return None, img1, "", ""
            return None, img1, pool_all[1], ""
        return None, img1, "", ""

    def _sanitize_and_dedup_images(self, cdn_images: List[Any], archetype_id: str = "", title: str = "") -> List[str]:
        """
        Contingência Oficial Anti-Duplicação de Fotos na Galeria da Shopify (4 Camadas):
        1. Filtra capas repetidas vinculadas a variantes de tamanho (variant_ids) em objetos de imagem Shopify.
        2. Elimina tokens de arquivos comprovadamente duplicados bit-a-bit pelo conector ERP/productOnChannel
           (ex: FUSION197, FUSION197BL, C02906BL, RAGLAN306BL, CAX049) quando já há foto primária na fila.
        3. Normaliza sufixos UUID da Shopify, sufixos de exportação (_-_jpg, -reduzido, _copy), extensão
           e prefixos de timestamp de 10 a 14 dígitos, além de colapsar múltiplos mockups frontais puros.
        4. Aplica contingência estrutural em galerias productOnChannel multi-grupo (A + B com UUID re-upado
           ou múltiplos grupos unitários consecutivos de variantes no início da galeria).
        """
        if not cdn_images:
            return []

        is_multi_color_arch = archetype_id in ("fishing_lures", "eyewear_sunglasses", "footwear_sandals_boaonda")

        # Camada 1: Se receber objetos de imagem da API Shopify ({src, variant_ids, width, height}),
        # colapsar fotos de capa repetidas por variante de tamanho (PP, P, M, G, GG, G1, G2).
        raw_urls: List[str] = []
        seen_variant_cover = False
        first_var_dims = None
        for item in cdn_images:
            if isinstance(item, dict):
                src = (item.get("src") or "").strip()
                if not src:
                    continue
                v_ids = item.get("variant_ids") or []
                dims = (item.get("width"), item.get("height"))
                if v_ids and not is_multi_color_arch:
                    if not seen_variant_cover:
                        seen_variant_cover = True
                        first_var_dims = dims
                        raw_urls.append(src)
                    else:
                        if "productonchannel" in src.lower() or (first_var_dims and dims == first_var_dims):
                            continue
                        raw_urls.append(src)
                else:
                    raw_urls.append(src)
            elif isinstance(item, str) and item.strip():
                raw_urls.append(item.strip())

        if not raw_urls:
            return []

        uuid_re = re.compile(r'_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?=\.[a-z0-9]+$)', re.IGNORECASE)
        copy_re = re.compile(r'(?:_-_jpg|_-_png|-reduzido|_reduzido|_copy|-copy|\s*\(\d+\))(?=\.[a-z0-9]+$)', re.IGNORECASE)
        ext_re = re.compile(r'\.[a-z0-9]+$', re.IGNORECASE)
        ts_re = re.compile(r'^\d{10,14}[-_]')
        poc_group_re = re.compile(r'productOnChannel_2Fimages_2F(\d+)', re.IGNORECASE)
        poc_hash_re = re.compile(r'_2f([0-9a-f]{32})', re.IGNORECASE)

        deduped: List[str] = []
        seen_keys = set()
        seen_pure_front = False

        for clean_u in raw_urls:
            fname = clean_u.split("?")[0].split("/")[-1].lower()
            m_hash = poc_hash_re.search(fname)
            poc_tok = m_hash.group(1).lower() if m_hash else fname

            # Camada 2: Descarte de duplicata binária conhecida do ERP/Shopify quando já há foto primária
            if deduped and (poc_tok in KNOWN_SHOPIFY_DUP_IMAGE_TOKENS or fname in KNOWN_SHOPIFY_DUP_IMAGE_TOKENS):
                continue

            # Camada 3: Normalização de UUID, sufixos de cópia, extensão e timestamp de upload
            norm_key = uuid_re.sub("", fname)
            norm_key = copy_re.sub("", norm_key)
            stem_no_ext = ext_re.sub("", norm_key)
            if "productonchannel" not in stem_no_ext and not is_multi_color_arch:
                ts_stripped = ts_re.sub("", stem_no_ext)
                if len(ts_stripped) > 2:
                    stem_no_ext = ts_stripped

            is_pure_front = (
                "frente" in stem_no_ext
                and not any(k in stem_no_ext for k in ("costa", "verso", "tras", "detalhe", "persp", "zoom", "2", "02", "3", "03", "4", "04", "5", "05"))
            )
            if is_pure_front:
                if seen_pure_front:
                    continue
                seen_pure_front = True

            if stem_no_ext not in seen_keys:
                seen_keys.add(stem_no_ext)
                deduped.append(clean_u)

        # Camada 4: Contingência estrutural para lotes productOnChannel multi-grupo
        if len(deduped) >= 3 and archetype_id != "fishing_lures":
            groups = [poc_group_re.search(u).group(1) if poc_group_re.search(u) else None for u in deduped]
            g_counts = {}
            for g in groups:
                if g:
                    g_counts[g] = g_counts.get(g, 0) + 1
            if groups[0] and g_counts.get(groups[0]) == 1:
                # Caso 4A: Grupo A unitário (capa da variante 1) + Grupo B multi-foto cuja 1ª imagem tem sufixo UUID de re-upload (ex: FUSION197)
                if (
                    groups[1]
                    and g_counts.get(groups[1], 0) >= 2
                    and uuid_re.search(deduped[1].split("?")[0])
                    and not uuid_re.search(deduped[2].split("?")[0])
                ):
                    deduped.pop(1)
                # Caso 4B: Múltiplos grupos unitários consecutivos no início (capas repetidas por variante P, M, G, GG)
                elif groups[1] and g_counts.get(groups[1]) == 1:
                    filtered = [deduped[0]]
                    idx = 1
                    while idx < len(deduped) and groups[idx] and g_counts.get(groups[idx]) == 1:
                        idx += 1
                    filtered.extend(deduped[idx:])
                    deduped = filtered

        non_banner = [u for u in deduped if "catalogobrkfishing_iscapremiumemdetalhes" not in u.lower() and "imagemdochatgpt" not in u.lower()]
        if len(non_banner) >= 3:
            deduped = non_banner

        # Move cards informativos / banners de categoria para o final da galeria para que fotos reais ocupem os Atos 1, 2 e 3
        banner_tokens = (
            "capacategoria", "prancheta_1_copiar", "versao3", "diferencialuv",
            "diferencialtela", "guia-de-tamanhos", "star-feminino", "dfubcro", "mqlxrlf", "chatgpt"
        )
        real_photos = [u for u in deduped if not any(tok in u.lower() for tok in banner_tokens)]
        info_banners = [u for u in deduped if any(tok in u.lower() for tok in banner_tokens)]
        if real_photos and info_banners:
            deduped = real_photos + info_banners

        return deduped

    def generate_narrative_from_template(self, product: Dict[str, Any], archetype_id: str, cdn_images: List[str], store_key: str = None, sibling_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gera os 3 blocos narrativos e especificações prontos para o HTMLBuilder.
        Se sibling_info for fornecido, anota o produto como originário de irmão homólogo do site.
        """
        template = dict(self.templates.get(archetype_id, self.templates["uv_performance"]))
        title = product.get("title", "Produto BRK")
        sku = product.get("master_sku") or product.get("sku") or ""
        vendor = product.get("vendor", "")
        tags = product.get("tags") or []
        cdn_images = self._sanitize_and_dedup_images(cdn_images, archetype_id=archetype_id, title=title)

        # Resolução de Origem, Título Formatado e Direitos Autorais C0
        origin_info = self.resolve_product_origin_and_title(title=title, vendor=vendor, sku=sku, tags=tags, product=product)
        formatted_title = origin_info["formatted_title"]
        brand_name = origin_info["brand_name"]
        origin_type = origin_info["origin_type"]
        show_copyright = origin_info["show_copyright"]
        
        # Paleta Cromática Suave por Loja
        store_palettes = {
            "brk_fishing": {"color": "#0284c7", "bg": "#f0f9ff"}, # Azul Leve
            "brk_agro":    {"color": "#16a34a", "bg": "#f0fdf4"}, # Verde Leve
            "brk_motors":  {"color": "#f97316", "bg": "#fff7ed"}, # Laranja Leve
        }
        
        if not store_key:
            url = (product.get("url") or "").lower()
            vendor_str = (product.get("vendor") or "").lower()
            category = (product.get("category") or "").lower()
            t_low_store = title.lower()
            imgs_str_store = " ".join(str(u) for u in cdn_images).lower()
            if (
                "agro" in url or "agro" in vendor_str or "agro" in category
                or archetype_id == "agro_field"
                or "0887/2083/4857" in imgs_str_store
                or "0798/6462/7495" in imgs_str_store
                or any(w in t_low_store for w in ["agro", "botina", "fazenda", "pecuaria", "pecuária", "nelore"])
            ):
                store_key = "brk_agro"
            elif (
                "motors" in url or "motors" in vendor_str or "motors" in category
                or archetype_id == "motors_speed"
                or "0714/9853/1081" in imgs_str_store
            ):
                store_key = "brk_motors"
            else:
                store_key = "brk_fishing"

        theme_color = store_palettes.get(store_key, {}).get("color", template.get("theme_color", "#0284c7"))
        theme_bg = store_palettes.get(store_key, {}).get("bg", template.get("theme_bg", "#f0f9ff"))

        # Determinar ícone de cuidados apropriado ao arquétipo
        care_icons = {
            "hats_country_cowboy": "fa-solid fa-hat-cowboy",
            "hats_safari_outdoor": "fa-solid fa-hat-cowboy-side",
            "caps_trucker_snapback": "fa-solid fa-hat-baseball",
            "shirts_button_work": "fa-solid fa-shirt",
            "pants_cargo_tactical": "fa-solid fa-vest",
            "accessories_car_care": "fa-solid fa-spray-can-sparkles",
            "accessories_general": "fa-solid fa-key",
            "fishing_lures": "fa-solid fa-fish-fins",
            "neck_gaiters_balaclavas": "fa-solid fa-mask-face",
            "sun_sleeves_manguitos": "fa-solid fa-hand-holding-hand",
            "footwear_sandals_boaonda": "fa-solid fa-shoe-prints",
            "closed_footwear_sneakers": "fa-solid fa-socks",
            "drinkware_thermo": "fa-solid fa-mug-hot",
            "tackle_boxes_storage": "fa-solid fa-box-archive",
            "overalls_workwear": "fa-solid fa-vest",
            "books_publications": "fa-solid fa-book-open",
            "cutlery_unique": "fa-solid fa-utensils",
            "fishing_tackle_gear": "fa-solid fa-screwdriver-wrench",
            "motors_speed": "fa-solid fa-shield-halved",
            "agro_field": "fa-solid fa-seedling",
            "uv_performance": "fa-solid fa-shirt",
            "eyewear_sunglasses": "fa-solid fa-glasses",
            "gloves_tactical_fishing": "fa-solid fa-mitten"
        }
        care_icon = care_icons.get(archetype_id, template.get("fa_icon", "fa-solid fa-hand-sparkles"))

        is_apparel = archetype_id in ("uv_performance", "agro_field", "motors_speed", "shirts_button_work", "pants_cargo_tactical")

        # Contextual Intelligence Flags para Adaptação Narrativa e Seleção Semântica de Fotos
        t_low = title.lower()
        tags_list = tags if isinstance(tags, list) else [str(tags)]
        tags_low = " ".join([str(t).lower() for t in tags_list])
        body_low = (product.get("body_html") or "").lower()
        all_info = f"{t_low} {tags_low} {body_low}"

        sku_clean_for_flags = str(product.get("master_sku") or product.get("sku") or "").lower().strip()
        is_fusion = is_apparel and (
            any(w in t_low for w in ["fusion", "fusionx"]) or
            "fusion" in sku_clean_for_flags or
            "fusion" in tags_low
        )
        is_hybrid = is_apparel and (
            any(w in t_low for w in ["hybrid"]) or
            sku_clean_for_flags.startswith("hyb") or
            "hybrid" in sku_clean_for_flags or
            "hybrid" in tags_low
        )
        is_hooded = (is_apparel and any(w in t_low for w in ["capuz", "hood", "hoodie"])) or is_fusion or is_hybrid
        is_kids_sku = is_apparel and (
            sku_clean_for_flags.startswith("ci")
            or bool(re.search(r'^(?:c0|ci|cf|cm|casual|adv|cadv|ccpbr|bp|hyb|fusion|cax|raglan)\d+i(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$', sku_clean_for_flags))
        ) and not any(w in t_low for w in ["feminina", "feminino", "baby look", "babylook", "masculina", "masculino", "adulto"])
        is_kids = is_apparel and (
            any(w in t_low for w in ["infantil", "kids", "juvenil"])
            or bool(re.search(r'\bmini\b', t_low))
            or is_kids_sku
        )
        if any(w in t_low for w in ["adulto", "unissex adulto"]):
            is_kids = False
        is_segunda_pele = is_apparel and (
            any(w in t_low for w in ["segunda pele", "camisa térmica", "camisa termica", "blusa térmica", "blusa termica"])
            or sku_clean_for_flags.startswith("raglan")
        )
        is_kit_shirt_boot = is_apparel and any(w in t_low for w in ["camisa", "camiseta", "blusa", "segunda pele"]) and bool(re.search(r'\b(botina|bota|coturno)\b', t_low))
        is_short_sleeve = is_apparel and (
            any(w in t_low for w in ["manga curta", "manga-curta", "camiseta"])
            or ("curta" in t_low and "manga" in t_low)
            or sku_clean_for_flags.startswith("cbtmc")
            or (sku_clean_for_flags.startswith(("casual", "bp", "cm", "cadv", "cf")) and not sku_clean_for_flags.startswith(("cmb", "cbt")))
        ) and not any(w in t_low for w in ["manga longa", "manga-longa"]) and not is_segunda_pele
        is_has_glove = is_apparel and (any(w in t_low for w in ["com luva", "e luva", "luva integrada", "armorx"]) or sku_clean_for_flags.startswith("cax"))
        is_casal = is_apparel and "casal" in t_low and ("kit" in t_low or "combo" in t_low)
        is_female = (
            any(w in t_low for w in ["feminina", "feminino", "baby look", "babylook", "mulher"]) or
            "femin" in tags_low or
            (is_apparel and bool(re.search(r'bl(?:pp|p|m|g|gg|xg|g1|g2)?(?:_full|_out)?$', sku_clean_for_flags)))
        ) and not is_kids and not is_casal
        is_round_neck = (
            is_apparel
            and archetype_id != "shirts_button_work"
            and not sku_clean_for_flags.startswith(("cmb", "cbt"))
            and not any(w in t_low for w in ["botão", "botao", "colarinho", "camisa work"])
            and (
                is_segunda_pele
                or is_short_sleeve
                or bool(re.match(r'^ci0(?:54|7[2-9]|8[0-4])(?:i|pp|p|m|g|gg|g1|g2)?(?:_full|_out)?$', sku_clean_for_flags))
                or any(w in t_low for w in ["gola careca", "gola redonda", "sem zíper", "sem ziper", "t-shirt", "camisa casual", "casual"])
            )
            and not any(w in t_low for w in ["com zíper", "com ziper"])
        )
        is_windbreaker = is_apparel and any(w in t_low for w in ["corta vento", "corta-vento", "windbreaker", "jaqueta", "anorak"]) and "rosa dos ventos" not in t_low

        # Tratamento Especial para Iscas e Produtos com Várias Variações (Split Media estrito para fishing_lures)
        is_lure = (archetype_id == "fishing_lures")
        variants = product.get("variants") or []
        has_multiple_variations = is_lure and (len(variants) > 1 or len(cdn_images) >= 2)
        split_images = None
        variations_summary = ""

        back_360_img = ""
        is_back_cover_360 = False

        # Alocação estrita de imagens exclusivas por ato - ZERO DUPLICAÇÃO DE MESMA COR / 2-CAPA / GIRO 360°
        if has_multiple_variations and (len(cdn_images) >= 4 or len(cdn_images) == 2):
            split_images, img1, img2, img3 = self._select_lure_act_images(
                cdn_images, variants=variants, product_id=str(product.get("id", "")), title=title
            )
            variant_titles = [v.get("title") for v in variants if isinstance(v, dict) and v.get("title") and v.get("title") != "Default Title"]
            if not variant_titles and product.get("variants_skus"):
                variant_titles = [s.split("_")[-1] if "_" in s else s for s in product.get("variants_skus") if s]
            if variant_titles:
                variations_summary = f"Disponível em {len(variant_titles)} opções de cores e modelos no anúncio ({', '.join(variant_titles[:4])}{'...' if len(variant_titles) > 4 else ''})."
            else:
                variations_summary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio."
        elif is_kit_shirt_boot:
            img1 = cdn_images[0] if len(cdn_images) > 0 else ""
            img2 = cdn_images[1] if len(cdn_images) > 1 else ""
            img3 = cdn_images[2] if len(cdn_images) > 2 else ""
            back_360_img = ""
            is_back_cover_360 = False
        elif is_apparel:
            img1, img2, img3, back_360_img, is_back_cover_360 = self._resolve_apparel_act_and_360_images(
                cdn_images, is_female=is_female, is_kids=is_kids, sku=sku_clean_for_flags, title=title
            )
        elif archetype_id == "cutlery_unique":
            img1, img2, img3 = self._select_cutlery_act_images(cdn_images, title)
        elif archetype_id == "neck_gaiters_balaclavas" and len(cdn_images) >= 3:
            sku_up_gaiter = sku_clean_for_flags.upper()
            if sku_up_gaiter in ("T659", "T660", "T662", "T663", "T664", "T665", "T666", "T667", "T668", "T669", "T670", "T671"):
                # Bandanas Amazon onde [1] é foto humanizada em uso no rosto/pescoço e [2] é render 3D tubular lateral
                img1, img2, img3 = cdn_images[0], cdn_images[2], cdn_images[1]
            elif sku_up_gaiter == "T563" and len(cdn_images) >= 4:
                img1, img2, img3 = cdn_images[0], cdn_images[2], cdn_images[3]
            else:
                img1, img2, img3 = cdn_images[0], cdn_images[1], cdn_images[2]
        elif archetype_id == "fishing_tackle_gear" and "trava vara" in title.lower() and len(cdn_images) >= 3:
            img1, img2, img3 = cdn_images[0], cdn_images[2], cdn_images[1]
        elif (
            len(cdn_images) >= 4
            and (
                "2-capa" in cdn_images[1].lower()
                or ("capa" in cdn_images[0].lower() and "capa" in cdn_images[1].lower())
                or str(product.get("id", "")) == "7553072103490"
            )
        ):
            # Varas de Pesca / Caixas Organizadoras onde cdn_images[1] é 2-capa (mesma foto da capa sem selo)
            img1, img2, img3 = cdn_images[0], cdn_images[2], cdn_images[3]
        elif len(cdn_images) == 3 and "2-capa" in cdn_images[1].lower():
            img1, img2, img3 = cdn_images[0], cdn_images[2], ""
        else:
            img1 = cdn_images[0] if len(cdn_images) > 0 else ""
            img2 = cdn_images[1] if len(cdn_images) > 1 else ""
            img3 = cdn_images[2] if len(cdn_images) > 2 else ""
            if has_multiple_variations:
                variant_titles = [v.get("title") for v in variants if isinstance(v, dict) and v.get("title") and v.get("title") != "Default Title"]
                if not variant_titles and product.get("variants_skus"):
                    variant_titles = [s.split("_")[-1] if "_" in s else s for s in product.get("variants_skus") if s]
                if variant_titles:
                    variations_summary = f"Disponível em {len(variant_titles)} opções de cores e modelos no anúncio ({', '.join(variant_titles[:4])}{'...' if len(variant_titles) > 4 else ''})."
                else:
                    variations_summary = "Múltiplas variações e opções de cores disponíveis para escolha no anúncio."

        act1 = dict(template["act1"])
        act2 = dict(template["act2"])
        act3 = dict(template["act3"])

        # 0. Adaptação Corta-Vento / Jaqueta (Proteção aerodinâmica contra vento e respingos)
        if is_windbreaker:
            act1["tag"] = "Barreira Corta-Vento & Leveza"
            act1["fa_icon"] = "fa-solid fa-wind"
            act1["title"] = "PROTEÇÃO AERODINÂMICA CONTRA VENTO, FRIO LEVE E RESPINGOS"
            act1["desc_tmpl"] = "Desenvolvido para bloquear rajadas de vento na navegação, na pilotagem ou nas manhãs frias no campo sem adicionar peso, o(a) {title} atua como um escudo térmico leve, compacto e resistente a respingos."
            act2["tag"] = "Isolamento & Portabilidade"
            act2["title"] = "TECIDO TÉCNICO REPELENTE À UMIDADE E DOBRA ULTRACOMPACTA"
            act2["desc_tmpl"] = "Confeccionado em tecido plano técnico de alta densidade que corta o vento frio e preserva o equilíbrio térmico corporal, dobrando de forma compacta para transporte fácil na mochila, barco ou alforge."
            act3["tag"] = "Fechamento & Vedação"
            act3["title"] = "ZÍPER FRONTAL INTEGRAL, CAPUZ ANATÔMICO E PUNHOS ELÁSTICOS"
            act3["desc_tmpl"] = "Equipado com fechamento frontal prático, punhos e barra com acabamento elástico que impedem a entrada de ar frio e costuras reforçadas de alta durabilidade."

        # 1. Adaptação Kids / Infantil (Seleção por Idade mantendo a referência de Tamanho PP ao G2)
        elif is_kids:
            act1["tag"] = "Proteção Infantil & Conforto"
            act1["fa_icon"] = "fa-solid fa-child"
            act1["title"] = "CONFORTO E PROTEÇÃO SOLAR TOTAL PARA OS PEQUENOS AVENTUREIROS"
            act1["desc_tmpl"] = "Desenvolvida especialmente para crianças e jovens exploradores com grade inteligente por faixa de idade (1 a 13 anos, mantendo a referência dos tamanhos PP ao G2), o(a) {title} oferece proteção solar máxima FPU 50+ com toque extra suave na pele, garantindo segurança, leveza e liberdade total para brincar ao ar livre."

            act2["tag"] = "Respirabilidade & Frescor"
            act2["fa_icon"] = "fa-solid fa-sun"
            act2["title"] = "TECNOLOGIA DRY FIT QUE MANTÉM AS CRIANÇAS FRESCAS E SECAS"
            kids_context = (
                "passeios na fazenda, cavalgadas e brincadeiras ao ar livre"
                if store_key == "brk_agro" else (
                    "passeios, viagens em família e brincadeiras ao ar livre"
                    if store_key == "brk_motors" else
                    "todas as brincadeiras e pescarias em família"
                )
            )
            act2["desc_tmpl"] = f"Tecido tecnológico respirável que absorve e dissipa o suor rapidamente, evitando o superaquecimento e mantendo o corpo seco e confortável durante {kids_context}."

            if not is_hooded:
                act3["tag"] = "Durabilidade & Liberdade"
                act3["fa_icon"] = "fa-solid fa-shield-heart"
                act3["title"] = "COSTURAS PLANAS ANTI-ATRITO E MÁXIMA DURABILIDADE"
                act3["desc_tmpl"] = "Construída com acabamento elástico de alta resistência que não pinica nem irrita a pele sensível das crianças, oferecendo caimento confortável que aguenta todas as aventuras infantis."

        # 1.1 Adaptação Segunda Pele Térmica / UV (RAGLAN)
        elif is_segunda_pele:
            act1["tag"] = "Segunda Pele Térmica & UV50+"
            if is_female:
                act1["title"] = "MODELAGEM FEMININA ANATÔMICA, CONFORTO TÉRMICO E PROTEÇÃO UV50+"
                act1["desc_tmpl"] = "Projetada sob medida para a anatomia feminina para atuar como uma verdadeira segunda pele sob jaquetas, macacões ou no uso direto ao ar livre, a {title} mantém o equilíbrio térmico corporal, reduz o atrito e garante proteção solar FPU 50+ com caimento acinturado impecável."
            else:
                act1["title"] = "CONFORTO TÉRMICO, AJUSTE ANATÔMICO E PROTEÇÃO SOLAR UV50+"
                act1["desc_tmpl"] = "Projetada para atuar como uma verdadeira segunda pele sob jaquetas, macacões ou no uso direto ao ar livre, a {title} mantém o equilíbrio térmico corporal, reduz o atrito com equipamentos e garante proteção solar FPU 50+ com liberdade total de movimentos."

        # 1.9 Adaptação Kit Casal (1 Camisa Masculina + 1 Camisa Feminina Baby Look)
        elif is_casal and archetype_id == "uv_performance":
            act1["tag"] = "Kit Casal Oficial (Masculino + Feminino)"
            act1["title"] = "KIT CASAL COM MODELAGEM MASCULINA E FEMININA (BABY LOOK)"
            act1["desc_tmpl"] = "Desenvolvido para casais que compartilham a paixão por estrada, aventura e atividades ao ar livre, o {title} combina a modelagem tradicional Masculina e o corte acinturado Feminino (Baby Look), oferecendo proteção solar FPU 50+, leveza e liberdade total de movimentos."

        # 2. Adaptação Feminina (Corte anatômico Baby Look em todas as linhas UV50+, incluindo FusionX, Hybrid e Capuz)
        elif is_female and archetype_id == "uv_performance":
            act1["title"] = "MODELAGEM FEMININA ANATÔMICA COM CAIMENTO IMPECÁVEL"
            act1["desc_tmpl"] = "Projetada sob medida para a anatomia feminina, a {title} combina corte acinturado esportivo (Baby Look), máxima liberdade de movimentos e proteção solar FPU 50+ com toque suave e elegante."

        # 3. Adaptação Fusion (Capuz com Máscara Facial Integrada e Punhos com Dedeira - SEM ZÍPER)
        if is_fusion:
            act3["tag"] = "Capuz com Máscara Integrada & Proteção 360°"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ COM MÁSCARA FACIAL INTEGRADA E PUNHO COM DEDEIRA"
            act3["desc_tmpl"] = "Desenvolvida com modelagem anatômica contínua para máximo conforto e zero atrito, a camisa FusionX conta com capuz anatômico acoplado com máscara facial protetora (balaclava integrada) que protege cabeça, nuca e rosto contra o sol forte e o vento, além de punhos anatômicos com abertura para o polegar (dedeira) que mantêm o dorso da mão sempre protegido."

        # 3.1 Adaptação Hybrid (Capuz Anatômico e Punhos com Dedeira - SEM ZÍPER)
        elif is_hybrid:
            act3["tag"] = "Capuz Anatômico & Punho com Dedeira"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ ANATÔMICO INTEGRADO E PUNHO COM ABERTURA PARA POLEGAR"
            hybrid_context = (
                "jornada no campo ou atividade ao ar livre"
                if store_key == "brk_agro" else (
                    "pilotagem, trilha ou atividade ao ar livre"
                    if store_key == "brk_motors" else
                    "pescaria ou atividade ao ar livre"
                )
            )
            act3["desc_tmpl"] = f"Projetada com caimento leve, contínuo e livre de atrito, a camisa Hybrid integra capuz anatômico de proteção solar 360° para nuca e cabeça, mangas com costuras planas reforçadas e punhos com abertura para o polegar (dedeira) que protegem o dorso das mãos durante toda a {hybrid_context}."

        # 3.2 Adaptação Capuz Geral (Elimina 'gola padre', injeta cobertura 360° no rosto/nuca)
        elif is_hooded:
            act3["tag"] = "Capuz Anatômico & Proteção 360°"
            act3["fa_icon"] = "fa-solid fa-head-side-mask"
            act3["title"] = "CAPUZ ANATÔMICO INTEGRADO E COSTURA REFORÇADA"
            act3["desc_tmpl"] = "Equipada com capuz anatômico integrado que oferece proteção solar 360° para nuca, orelhas e laterais do rosto contra a radiação forte e o vento, dispensando acessórios extras, com costuras planas reforçadas anti-atrito."

        # 3.3 Adaptação Segunda Pele no Ato 3 (Gola redonda e mangas raglan sem zíper)
        elif is_segunda_pele:
            act3["tag"] = "Costuras Planas & Gola Anatômica"
            act3["title"] = "MANGAS RAGLAN E COSTURAS PLANAS ANTI-ATRITO"
            act3["desc_tmpl"] = "Construída com mangas de corte raglan esportivo, gola redonda anatômica e costuras planas reforçadas que eliminam pontos de pressão sob jaquetas, coletes ou mochilas."

        # 4. Adaptação Manga Curta (Elimina 'punhos anatômicos', injeta ventilação e barra pespontada)
        elif is_short_sleeve:
            if "punhos anatômicos" in act3.get("desc_tmpl", "").lower():
                if is_round_neck:
                    act3["title"] = "COSTURA REFORÇADA E GOLA REDONDA ANATÔMICA"
                    act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola redonda anatômica reforçada ombro a ombro e mangas curtas com barra em costura dupla reforçada que proporcionam ventilação ideal e liberdade total de movimentos."
                else:
                    act3["desc_tmpl"] = act3["desc_tmpl"].replace(
                        "punhos anatômicos que mantêm o ajuste firme e não laceiam",
                        "mangas curtas com barra em costura dupla reforçada que proporcionam ventilação ideal e liberdade nos braços"
                    ).replace(
                        "punhos anatômicos que não laceiam com o uso frequente",
                        "mangas curtas com barra em costura dupla reforçada que proporcionam ventilação ideal e liberdade nos braços"
                    )
            if "manga longa" in act3.get("desc_tmpl", "").lower():
                act3["desc_tmpl"] = act3["desc_tmpl"].replace("manga longa", "manga curta")

        # 5. Adaptação Gola Redonda / Sem Zíper (Elimina 'zíper com trava', injeta gola careca canelada)
        elif is_round_neck:
            act3["title"] = "COSTURA REFORÇADA E GOLA REDONDA ANATÔMICA"
            act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola careca anatômica reforçada ombro a ombro e caimento confortável para uso prolongado."

        # 6. Adaptação Camisa com Luva Integrada (Linha ArmorX / CAX)
        elif is_has_glove:
            if self._is_hand_glove_photo(img3):
                act3["tag"] = "Punho Luva com Encaixe de Polegar"
                act3["title"] = "PUNHOS ALONGADOS COM ABERTURA ANATÔMICA PARA O POLEGAR (LUVA INTEGRADA)"
                act3["desc_tmpl"] = (
                    "Projetada para proteger uma das regiões mais expostas ao sol durante a pescaria, a linha ArmorX conta com punhos alongados em tecido elástico e abertura anatômica para passar o polegar (luva integrada). Esse sistema mantém a manga firme sobre o dorso da mão sem subir nos arremessos, deixando os dedos totalmente livres para sensibilidade tátil no manuseio de carretilha, molinete e iscas."
                )
            else:
                act3["tag"] = "Punho com Luva Integrada & Acabamento"
                act3["title"] = "PUNHOS ESTENDIDOS COM LUVA INTEGRADA E COSTURAS REFORÇADAS"
                act3["desc_tmpl"] = "Acabamento de alto padrão com costuras planas anti-atrito, gola padre anatômica e punhos estendidos com luva integrada (abertura para o polegar) que garantem proteção solar contínua no dorso das mãos com total liberdade nos dedos."

        sibling_specs = sibling_info.get("extracted_specs") if sibling_info else None
        specs = self.extract_product_specs(product, archetype_id, sibling_specs=sibling_specs)
        specs = self.sanitize_specs_for_archetype(specs, archetype_id)

        # Adaptação Contextual de Ficha Técnica
        new_specs = []
        for s in specs:
            lbl = s.get("label", "")
            val = s.get("value", s.get("default", ""))

            # Fusion e Hybrid: Capuz e Dedeira sem zíper
            if is_fusion:
                if any(w in lbl.lower() for w in ["gola", "capuz", "zíper", "ziper"]):
                    lbl = "Capuz & Máscara"
                    val = "Capuz anatômico integrado com máscara facial de proteção UV50+"
                val = re.sub(r'gola padre[^,;.]*', 'capuz com máscara facial integrada', val, flags=re.IGNORECASE)
                val = re.sub(r'punhos anatômicos[^,;.]*', 'punhos anatômicos com abertura para o polegar (dedeira)', val, flags=re.IGNORECASE)
            elif is_hybrid:
                if any(w in lbl.lower() for w in ["gola", "capuz", "zíper", "ziper"]):
                    lbl = "Capuz"
                    val = "Capuz anatômico integrado de alta cobertura solar"
                val = re.sub(r'gola padre[^,;.]*', 'capuz anatômico integrado', val, flags=re.IGNORECASE)
                val = re.sub(r'punhos anatômicos[^,;.]*', 'punhos anatômicos com abertura para o polegar (dedeira)', val, flags=re.IGNORECASE)
            elif is_hooded:
                if any(w in lbl.lower() for w in ["gola", "zíper", "ziper"]):
                    lbl = "Capuz / Gola"
                    val = "Capuz anatômico integrado de alta cobertura solar com acabamento elástico"
                val = re.sub(r'gola padre[^,;.]*', 'capuz anatômico integrado', val, flags=re.IGNORECASE)

            # Manga Curta: elimina punhos / manga longa
            if is_short_sleeve:
                if any(w in lbl.lower() for w in ["punho", "manga"]):
                    lbl = "Mangas"
                    val = "Mangas curtas com acabamento reforçado em pesponto duplo"
                val = re.sub(r'punhos anatômicos[^,;.]*', 'mangas curtas reforçadas', val, flags=re.IGNORECASE)
                val = re.sub(r'mangas raglan esportivas', 'mangas curtas com barra reforçada', val, flags=re.IGNORECASE)

            # Kids: elimina jargão adulto e explicita grade por idade + tamanho
            if is_kids:
                val = re.sub(r'homem e da mulher do campo', 'pequenos aventureiros', val, flags=re.IGNORECASE)
                val = re.sub(r'lida no campo|lida diária', 'atividades ao ar livre', val, flags=re.IGNORECASE)
                if "modelagem" in lbl.lower():
                    val = "Infantil / Juvenil anatômica confortável (1 a 13 Anos | PP ao G2)"

            # Gola Redonda: elimina zíper
            if is_round_neck and not is_hooded:
                if any(w in lbl.lower() for w in ["zíper", "ziper", "gola", "fechamento"]):
                    lbl = "Gola"
                    val = "Gola redonda anatômica com acabamento reforçado anti-atrito"
                val = re.sub(r'com zíper[^,;.]*', '', val, flags=re.IGNORECASE)
                val = re.sub(r'gola padre[^,;.]*', 'gola redonda anatômica', val, flags=re.IGNORECASE)

            # Luva integrada em camisa
            if is_has_glove and not is_short_sleeve:
                if "punho" in lbl.lower():
                    lbl = "Punhos / Luva"
                    val = "Punhos estendidos anatômicos com luva integrada para o dorso da mão"

            new_specs.append({"label": lbl, "value": val})

        if is_windbreaker:
            new_specs = [
                {"label": "Construção", "value": "Tecido plano técnico Corta-Vento de alta densidade repelente a respingos"},
                {"label": "Proteção", "value": "Barreira contra vento frio, sereno e radiação solar UV50+"},
                {"label": "Fechamento & Capuz", "value": "Zíper frontal integral reforçado e capuz anatômico de proteção"},
                {"label": "Punhos & Barra", "value": "Acabamento elástico anatômico para vedação contra entrada de vento"},
                {"label": "Portabilidade", "value": "Ultraleve e dobrável (compacto para mochila, barco ou alforge)"}
            ]

        if is_has_glove and not is_short_sleeve and not any("luva" in s["label"].lower() for s in new_specs):
            new_specs.append({"label": "Punhos / Luva", "value": "Punhos estendidos anatômicos com luva integrada para o dorso da mão"})

        if archetype_id == "uv_performance" and not is_fusion and not is_hybrid and not is_hooded:
            if is_round_neck:
                if not any(w in s["label"].lower() for s in new_specs for w in ["gola", "fechamento"]):
                    new_specs.append({"label": "Gola", "value": "Gola redonda anatômica com acabamento reforçado anti-atrito"})
            else:
                if not any(w in s["label"].lower() for s in new_specs for w in ["gola", "fechamento"]):
                    new_specs.append({"label": "Gola / Fechamento", "value": "Gola padre anatômica com zíper e trava de segurança"})

        if is_fusion:
            if not any("capuz" in s["label"].lower() or "máscara" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Capuz & Máscara", "value": "Capuz anatômico integrado com máscara facial de proteção UV50+"})
            if not any("punho" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
        elif is_hybrid:
            if not any("capuz" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Capuz", "value": "Capuz anatômico integrado de alta cobertura solar"})
            if not any("punho" in s["label"].lower() for s in new_specs):
                new_specs.append({"label": "Punhos", "value": "Punhos anatômicos com abertura para o polegar (dedeira)"})
        elif is_hooded and not any("capuz" in s["label"].lower() for s in new_specs):
            new_specs.append({"label": "Capuz", "value": "Capuz anatômico integrado para proteção solar estendida"})

        if is_fusion or is_hybrid or is_hooded or is_round_neck:
            act3["title"] = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', act3["title"], flags=re.IGNORECASE).strip()
            replacement_collar = "capuz anatômico contínuo" if (is_fusion or is_hybrid or is_hooded) else "gola redonda anatômica"
            act3["desc_tmpl"] = re.sub(r'gola padre com cobertura no cursor do z[íi]per', replacement_collar, act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\bcursor do z[íi]per\b', 'acabamento anatômico', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\bz[íi]per com trava de seguran[çc]a\b', 'conforto anatômico contínuo', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', act3["desc_tmpl"], flags=re.IGNORECASE)
            act3["desc_tmpl"] = re.sub(r'\(\s*\)', '', act3["desc_tmpl"]).strip()
            new_clean_specs = []
            for sp in new_specs:
                lbl_c = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', sp["label"], flags=re.IGNORECASE).strip()
                replacement_hood = "capuz com máscara facial integrada" if is_fusion else ("capuz anatômico integrado" if (is_hybrid or is_hooded) else "gola redonda anatômica")
                val_c = re.sub(r'gola padre[^,;.]*', replacement_hood, sp["value"], flags=re.IGNORECASE)
                val_c = re.sub(r'\bcursor do z[íi]per\b', 'acabamento contínuo', val_c, flags=re.IGNORECASE)
                val_c = re.sub(r'\b(com zíper|com ziper|sem zíper|sem ziper|zíper|ziper)\b', '', val_c, flags=re.IGNORECASE)
                val_c = re.sub(r'\(\s*\)', '', val_c).strip()
                new_clean_specs.append({"label": lbl_c or "Acabamento", "value": val_c})
            new_specs = new_clean_specs

        # Adaptação Temática de Público por Loja (Agro, Motors e Fishing) para Camisas UV
        if archetype_id == "uv_performance" and not is_kids:
            if store_key == "brk_agro" or any(w in t_low for w in ["agro", "campo", "rural", "trator", "fazenda", "pecuaria", "pecuária"]):
                if "pescadores" in act1.get("desc_tmpl", ""):
                    act1["desc_tmpl"] = (
                        act1["desc_tmpl"]
                        .replace("pescadores e entusiastas do ar livre", "o homem e a mulher do campo e entusiastas do ar livre")
                        .replace("os arremessos e manobras", "a rotina intensa no campo e manobras")
                        .replace("arremessos e manobras", "a rotina intensa no campo e manobras")
                    )
            elif store_key == "brk_motors" or any(w in t_low for w in ["moto", "trail", "cross", "velocidade", "motors", "pista"]):
                if "pescadores" in act1.get("desc_tmpl", ""):
                    act1["desc_tmpl"] = (
                        act1["desc_tmpl"]
                        .replace("pescadores e entusiastas do ar livre", "pilotos, motociclistas e aventureiros")
                        .replace("os arremessos e manobras", "a pilotagem e manobras")
                        .replace("arremessos e manobras", "a pilotagem e manobras")
                    )

        # 7.9 Adaptação Especializada para Kit Multi-Produtos: Camisa + Botina em Couro Legítimo
        if is_kit_shirt_boot:
            if is_segunda_pele:
                act1["tag"] = "Item 01 do Kit: Segunda Pele Térmica UV50+"
                act1["fa_icon"] = "fa-solid fa-shirt"
                act1["title"] = "CAMISA TÉRMICA DE TOQUE FRIO, MODELAGEM RAGLAN E PROTEÇÃO SOLAR FPU 50+"
                act1["desc_tmpl"] = "O primeiro item do {title} é a Camisa Térmica BRK com fator FPU 50+ homologado, mangas de corte raglan esportivo e costuras planas anti-atrito que mantêm o equilíbrio térmico corporal e dissipam o suor rapidamente sob o sol ou sob outras peças."
            else:
                act1["tag"] = "Item 01 do Kit: Camisa Técnica BRK UV50+"
                act1["fa_icon"] = "fa-solid fa-shirt"
                act1["title"] = "TECNOLOGIA XTECH PRO COM PROTEÇÃO SOLAR FPU 50+ E SECAGEM ULTRA RÁPIDA"
                act1["desc_tmpl"] = "O primeiro item do {title} é a Camisa Técnica BRK confeccionada em malha tecnológica leve e respirável com bloqueio permanente de até 98% dos raios UVA e UVB (FPU 50+), garantindo frescor, proteção solar e liberdade de movimentos na lida do campo."
            act2["tag"] = "Item 02 do Kit: Botina em Couro Legítimo"
            act2["fa_icon"] = "fa-solid fa-shoe-prints"
            act2["title"] = "BOTINA EM COURO BOVINO LEGÍTIMO COM SOLADO ANTIDERRAPANTE E CALCE FÁCIL"
            act2["desc_tmpl"] = "Complementando o conjunto na segunda imagem, a Botina Country em Couro Bovino Legítimo Chocolate conta com elásticos laterais cobertos para calce rápido, puxador reforçado, palmilha anatômica macia de absorção de impacto e solado de borracha tratorado antiderrapante com acabamento blaqueado lateral para máxima firmeza e durabilidade."
            act3["tag"] = "Conjunto Completo Campo & Dia a Dia"
            act3["fa_icon"] = "fa-solid fa-shield-halved"
            act3["title"] = "PROTEÇÃO DA CABEÇA AOS PÉS: A COMBINAÇÃO DEFINITIVA PARA A LIDA E O LAZER"
            act3["desc_tmpl"] = "Pensado para quem exige desempenho, resistência e apresentação impecável na fazenda, manejo rural, cavalgadas ou rotina diária, este kit reúne proteção solar superior no tronco e segurança robusta nos pés em uma única compra."
            new_specs = [
                {"label": "Itens Inclusos no Kit", "value": "1 Camisa Técnica BRK UV50+ + 1 Par de Botinas em Couro Legítimo Chocolate"},
                {"label": "Item 01 — Tecido da Camisa", "value": "Malha tecnológica XTech Pro® com proteção solar FPU 50+ permanente e secagem rápida (Dry)"},
                {"label": "Item 01 — Modelagem da Camisa", "value": "Segunda pele térmica com mangas raglan e gola redonda anatômica" if is_segunda_pele else "Manga longa anatômica com gola padre e zíper frontal com trava"},
                {"label": "Item 02 — Cabedal da Botina", "value": "Couro Bovino Legítimo selecionado na cor Chocolate com elásticos laterais de calce fácil"},
                {"label": "Item 02 — Solado & Palmilha", "value": "Borracha antiderrapante de alta tração blaqueada + Palmilha anatômica anti-impacto"},
                {"label": "Indicação de Uso", "value": "Lida no campo, agronegócio, fazenda, cavalgadas, rodeios e uso diário"}
            ]
            template["care_tips"] = "Camisa: lavar à mão ou em ciclo suave com sabão neutro e secar à sombra. Botina em Couro: limpar com pano levemente úmido, secar à sombra longe de fontes de calor e hidratar periodicamente com pasta ou condicionador para couro legítimo."

        # 8. Adaptação 360° para Camisetas de Algodão em BRK Motors (Lifestyle Duas Rodas vs Agro)
        if archetype_id == "agro_field":
            is_motors_cotton = (
                store_key == "brk_motors"
                or any(w in t_low for w in ["moto", "motocicl", "trail", "big trail", "adventure", "gs ", "r1250", "r1200", "grau", "244", "rossi", "ninja", "hornet", "xj6", "tiger", "africa twin", "harley", "custom", "pista", "velocidade", "piloto"])
            )
            if is_motors_cotton:
                act1["tag"] = "Lifestyle Duas Rodas & Algodão Nobre"
                act1["title"] = "ESTILO AUTÊNTICO DUAS RODAS COM CONFORTO PREMIUM"
                act1["desc_tmpl"] = "Desenvolvida para apaixonados por motociclismo, estrada e liberdade, a {title} une estampa exclusiva de alta definição ao toque macio do algodão premium, garantindo presença marcante em encontros, viagens e no dia a dia urbano."
                for sp in new_specs:
                    if "uso recomendado" in sp["label"].lower():
                        sp["value"] = "Encontros de motociclismo, viagens, passeios e uso casual no dia a dia"

        # 8.5 Adaptação 360° para Camisas de Botão: Work Safari UV50+ (CMB) vs Country Xadrez / Lisa Classic (CBTML / CBTMC)
        elif archetype_id == "shirts_button_work":
            is_cmb_work_uv = sku_clean_for_flags.startswith("cmb") or ("work" in t_low and "uv" in t_low)
            if is_cmb_work_uv:
                act1["tag"] = "Proteção Solar UV50+ & Linha Work"
                act1["title"] = "TECIDO TÉCNICO LEVE COM PROTEÇÃO SOLAR FPU 50+ E CAIMENTO OPERACIONAL"
                act1["desc_tmpl"] = "Desenvolvida para unir apresentação profissional, máxima funcionalidade e proteção solar certificada FPU 50+ no campo, na pescaria ou na rotina operacional, a {title} mantém o corpo fresco, protegido e confortável durante todo o dia."
                act2["tag"] = "Bolsos Utilitários & Abotoamento"
                act2["title"] = "DOIS BOLSOS FRONTAIS COM LAPELA ABOTOADA E COLARINHO ESTRUTURADO"
                act2["desc_tmpl"] = "Equipada com fechamento frontal integral por botões reforçados, colarinho estruturado de excelente postura e dois bolsos utilitários frontais no peito com lapela e botão para guardar objetos com total segurança."
                act3["tag"] = "Versatilidade & Acabamento"
                act3["title"] = "MANGAS COM PRESILHA DE AJUSTE E COSTURAS REFORÇADAS"
                act3["desc_tmpl"] = "Construída com costuras reforçadas nos pontos de maior exigência, punhos abotoados e sistema funcional de presilha (martingale) que permite dobrar e fixar as mangas com praticidade nos momentos de maior calor."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ homologado contra raios UVA e UVB"},
                    {"label": "Fechamento & Gola", "value": "Abotoamento frontal reforçado e colarinho estruturado"},
                    {"label": "Bolsos Utilitários", "value": "2 bolsos frontais no peito com lapela e fechamento por botão"},
                    {"label": "Mangas & Ajuste", "value": "Manga longa com punho abotoado e presilha para uso dobrado"},
                    {"label": "Modelagem", "value": "Operacional / Safari Work confortável de alta mobilidade"}
                ]
            else:
                estilo_padrao = "Xadrez Country" if "xadrez" in t_low else "Lisa Classic"
                manga_txt = "Manga Curta" if is_short_sleeve else "Manga Longa"
                publico_txt = "Feminina acinturada" if is_female else "Masculina confortável"
                act1["tag"] = f"Estilo {estilo_padrao} & Tradição"
                act1["title"] = f"TECIDO ENCORPADO DE TOQUE MACIO E VISUAL {estilo_padrao.upper()} AUTÊNTICO"
                act1["desc_tmpl"] = f"Desenvolvida para quem valoriza elegância, tradição e durabilidade no campo, no trabalho ou em eventos sertanejos, a {{title}} entrega caimento impecável ({publico_txt}) e conforto térmico o dia inteiro."
                act2["tag"] = "Abotoamento & Colarinho"
                act2["title"] = "FECHAMENTO FRONTAL POR BOTÕES REFORÇADOS E COLARINHO ESTRUTURADO"
                act2["desc_tmpl"] = "Conta com abotoamento frontal de alta resistência, colarinho firme que preserva o alinhamento da peça e bolso frontal funcional com acabamento de alto padrão."
                act3["tag"] = f"Acabamento {manga_txt}"
                act3["title"] = (
                    "MANGAS CURTAS COM BARRA REFORÇADA E COSTURAS DE ALTA PRECISÃO"
                    if is_short_sleeve else
                    "PUNHOS ABOTOADOS, PALA TRASEIRA ANATÔMICA E COSTURAS REFORÇADAS"
                )
                act3["desc_tmpl"] = (
                    "Construída com mangas curtas de caimento leve e ventilado, pala traseira anatômica e pespontos reforçados que garantem liberdade total de movimentos nos dias quentes."
                    if is_short_sleeve else
                    "Construída com punhos estruturados com abotoamento firme, pala traseira anatômica e costuras reforçadas que garantem durabilidade superior e ampla mobilidade dos braços."
                )
                new_specs = [
                    {"label": "Estilo / Padrão", "value": f"Camisa {estilo_padrao} de Botão ({manga_txt})"},
                    {"label": "Fechamento & Gola", "value": "Botões frontais reforçados e colarinho tradicional estruturado"},
                    {"label": "Mangas", "value": "Mangas curtas com barra pespontada" if is_short_sleeve else "Mangas longas com punhos abotoados"},
                    {"label": "Tecido", "value": "Algodão / Sarja leve de alta resistência e toque macio"},
                    {"label": "Modelagem", "value": f"{publico_txt} com ótimo caimento e liberdade de movimentos"}
                ]

        # 9. Adaptação 360° por Subtipo de Equipamentos de Pesca (fishing_tackle_gear)
        elif archetype_id == "fishing_tackle_gear":
            if "trava vara" in t_low or "trava-vara" in t_low:
                act1["tag"] = "Fixação Segura no Convés"
                act1["title"] = "TRAVA-VARAS ELÁSTICO DE CONVÉS PARA BARCOS, LANCHAS E CAIAQUES"
                act1["desc_tmpl"] = "Desenvolvido para manter suas varas de pesca perfeitamente alinhadas e imóveis no convés da embarcação mesmo sob ondas e navegação rápida, o {title} evita quedas, batidas de blanks e enroscos de linha."
                act2["tag"] = "Capacidade para 3 Varas & Inox"
                act2["title"] = "ACOMODA ATÉ 3 VARAS COM ENGATE RÁPIDO E PARAFUSOS EM AÇO INOX"
                act2["desc_tmpl"] = "Cinta elástica de alta memória com divisórias protetoras que estabilizam até 3 varas simultaneamente, equipada com fivela de engate rápido lateral e acompanhada de parafusos em aço inoxidável para instalação imediata."
                act3["tag"] = "Durabilidade Náutica"
                act3["title"] = "RESISTÊNCIA SUPERIOR AO SOL, UMIDADE E AMBIENTE MARINHO"
                act3["desc_tmpl"] = "Construído com polímero técnico de alta tenacidade, cordão elástico reforçado e fixadores em aço inox, suportando exposição solar contínua e respingos em água doce ou salgada."
            elif ("alça" in t_low or "alca" in t_low) and "vara" in t_low:
                act1["tag"] = "Transporte Prático de Varas"
                act1["title"] = "ALÇA DE OMBRO COM CINTAS AGRUPADORAS PARA TRANSPORTE SEGURO"
                act1["desc_tmpl"] = "Projetada para facilitar a caminhada até o pesqueiro, barranco ou embarcação com as mãos livres, a {title} agrupa múltiplas varas de pesca com segurança e evita o entrelaçamento de linhas e ponteiras."
                act2["tag"] = "Conforto & Ajuste Rápido"
                act2["title"] = "OMBREIRA ACOLCHOADA ANTIDERRAPANTE E FIVELAS DE ENGATE RÁPIDO"
                act2["desc_tmpl"] = "Conta com apoio de ombro macio e texturizado que distribui o peso sem escorregar, além de cintas reguláveis com fechos de engate rápido que abraçam os cabos e blanks sem danificar os passadores."
                act3["tag"] = "Qualidade Marine Sports"
                act3["title"] = "MATERIAL RESISTENTE À UMIDADE E REGULAGEM DE COMPRIMENTO"
                act3["desc_tmpl"] = "Confeccionada em fita sintética de alta tenacidade com ajuste de altura (até 1,20 m), garantindo durabilidade e praticidade em todas as suas jornadas de pesca."
            elif "capa protetora" in t_low and "carretilha" in t_low:
                act1["tag"] = "Proteção em Neoprene"
                act1["title"] = "CAPA PROTETORA EM NEOPRENE PARA CARRETILHAS DE PERFIL BAIXO"
                act1["desc_tmpl"] = "Desenvolvida sob medida para proteger sua carretilha de perfil baixo contra riscos, impactos, poeira e maresia durante o transporte ou armazenamento, a {title} preserva a pintura e a mecânica do seu equipamento."
                act2["tag"] = "Encaixe Anatômico na Vara"
                act2["title"] = "MODELAGEM INTELIGENTE QUE PERMITE USO MESMO MONTADA NA VARA"
                act2["desc_tmpl"] = "Sua estrutura flexível com abas de fixação rápida envolve a carretilha com firmeza tanto avulsa na maleta quanto já fixada no reel seat da vara de pesca, agilizando a proteção no barco ou no carro."
                act3["tag"] = "Identidade Exclusiva BRK"
                act3["title"] = "ACABAMENTO EM ALTA DEFINIÇÃO E AMORTECIMENTO ANTI-IMPACTO"
                act3["desc_tmpl"] = "Confeccionada em neoprene espesso de alta elasticidade que absorve pequenos choques mecânicos, estampada com grafismo exclusivo BRK Fishing de cores vivas e duráveis."
            elif "cinto" in t_low and "apoiador" in t_low:
                act1["tag"] = "Suporte Dorsal para Pesca Pesada"
                act1["title"] = "ARNÊS LOMBAR E DORSAL PARA BRIGAS COM GRANDES TROFÉUS"
                act1["desc_tmpl"] = "Projetado para distribuir o esforço físico nas costas e nos ombros durante longas batalhas com grandes peixes de couro e oceânicos, o {title} reduz drasticamente a fadiga lombar e nos braços do pescador."
                act2["tag"] = "Ganchos Metálicos & Alças em X"
                act2["title"] = "GANCHOS DE APOIO EM METAL REFORÇADO E FIVELAS DE ENGATE RÁPIDO"
                act2["desc_tmpl"] = "Equipado com tiras de regulagem de alta tenacidade, fivelas frontais de travamento seguro e ganchos metálicos inferiores para conexão firme aos olhais de carretilhas de pesca pesada."
                act3["tag"] = "Conforto & Ventilação"
                act3["title"] = "ESTRUTURA ACOLCHOADA RESPIRÁVEL COM ESTAMPA EXCLUSIVA BRK"
                act3["desc_tmpl"] = "Painel dorsal ergonômico com revestimento interno respirável que amortece a pressão nas costas, finalizado com arte exclusiva BRK em alta resolução."
            elif "passaguá" in t_low or "passagua" in t_low or "puçá" in t_low or "puca" in t_low:
                act1["tag"] = "Embarque Seguro do Troféu"
                act1["title"] = "PASSAGUÁ RETRÁTIL DE AMPLA ABERTURA (40X40 CM) E 1,80 M DE ALCANCE"
                act1["desc_tmpl"] = "Essencial para garantir o embarque seguro do peixe na hora decisiva sem forçar a ponta da vara ou estourar a linha, o {title} oferece alcance total de 1,80 m e arco amplo de 40x40 cm."
                act2["tag"] = "Cabo em 2 Partes & Dobrável"
                act2["title"] = "HASTE METÁLICA EM 2 SEÇÕES COM TRAVA RÁPIDA E EMPUNHADURA FIRME"
                act2["desc_tmpl"] = "Construído com cabo tubular leve e resistente desmontável em 2 partes e arco dobrável com trava central, ocupando mínimo espaço no barco, caiaque ou porta-malas do veículo."
                act3["tag"] = "Rede Protetora & Pesque e Solte"
                act3["title"] = "MALHA MACIA DE SECAGEM RÁPIDA QUE PRESERVA O MUCO DO PEIXE"
                act3["desc_tmpl"] = "Rede confeccionada em malha resistente e macia que reduz o enrosco de garatéias e protege as escamas e o muco protetor do peixe para uma soltura saudável no Pesque e Solte."
            elif "alicate" in t_low and ("contenção" in t_low or "contencao" in t_low or "balança" in t_low or "balanca" in t_low):
                act1["tag"] = "Contenção Firme & Pesagem"
                act1["title"] = "ALICATE DE CONTENÇÃO (LIP GRIP) COM BALANÇA INTEGRADA"
                act1["desc_tmpl"] = "Desenvolvido para imobilizar o peixe pela mandíbula com total segurança e realizar a pesagem imediata do seu troféu, o {title} protege as mãos do pescador contra dentes afiados e garatéias."
                act2["tag"] = "Pinça de Travamento & Gatilho"
                act2["title"] = "GARRA DE AÇO INOX COM FECHAMENTO AUTOMÁTICO E GATILHO ANATÔMICO"
                act2["desc_tmpl"] = "Mecanismo de pinça de alta precisão acionado por gatilho suave de dois dedos, mantendo a boca do peixe travada com firmeza sem machucar a estrutura óssea do exemplar."
                act3["tag"] = "Empunhadura & Cordão Fiel"
                act3["title"] = "CABO EMBORRACHADO ANTIDERRAPANTE E FIEL DE PULSO DE SEGURANÇA"
                act3["desc_tmpl"] = "Conta com empunhadura anatômica antiderrapante para uso com as mãos molhadas, visor de escala de peso integrado no tubo e cordão fiel ajustável para evitar perda na água."
            elif "alicate" in t_low:
                act1["tag"] = "Precisão & Manutenção de Tralha"
                act1["title"] = "ALICATE DE PESCA EM AÇO PARA CORTE DE LINHAS E REMOÇÃO DE ANZÓIS"
                act1["desc_tmpl"] = "Ferramenta indispensável no colete ou na caixa de pesca, o {title} proporciona agilidade e segurança para retirar anzóis e garatéias, cortar linhas, apertar chumbadas e preparar encastoados."
                act2["tag"] = "Bico Funcional & Lâmina de Corte"
                act2["title"] = "LÂMINA DE CORTE PRECISA E ABERTURA DE ARGOLAS (SPLIT RING)"
                act2["desc_tmpl"] = "Projetado com mandíbula serrilhada de alta firmeza, área de corte afiada para linhas monofilamento e multifilamento e retorno por mola que permite operação prática com apenas uma mão."
                act3["tag"] = "Empunhadura Antiderrapante"
                act3["title"] = "CABO ERGONÔMICO REVESTIDO E TRATAMENTO ANTICORROSIVO"
                act3["desc_tmpl"] = "Acabamento metálico resistente à oxidação aliado a cabos anatômicos emborrachados que garantem pegada firme e confortável mesmo com as mãos molhadas."
            elif "kit vara" in t_low and ("molinete" in t_low or "carretilha" in t_low):
                act1["tag"] = "Conjunto Pronto para Pescar"
                act1["title"] = "KIT EQUILIBRADO VARA EM 2 PARTES E MOLINETE DE RECOLHIMENTO MACIO"
                act1["desc_tmpl"] = "Praticidade imediata para suas pescarias em rios, lagos e pesqueiros: o {title} combina uma vara de 1,50 m desmontável em 2 partes com um molinete tamanho 200 perfeitamente balanceado."
                act2["tag"] = "Transporte Compacto & Conforto"
                act2["title"] = "VARA DE 2 SEÇÕES COM PASSADORES REFORÇADOS E CABO EM EVA"
                act2["desc_tmpl"] = "A vara dividida em duas partes facilita o transporte na mochila ou no porta-malas, contando com cabo anatômico em EVA antiderrapante, reel seat firme e passadores resistentes ao atrito."
                act3["tag"] = "Molinete 200 & Fricção Ajustável"
                act3["title"] = "SISTEMA DE FRICÇÃO PROGRESSIVA E MANIVELA REVERSÍVEL"
                act3["desc_tmpl"] = "O molinete 200 oferece recolhimento suave, freio ajustável ponto a ponto e manivela intercambiável (direito/esquerdo), sendo excelente para pescadores iniciantes, jovens e lazer em família."
            elif any(w in t_low for w in ["vara ", "vara de", "varas"]):
                act1["tag"] = "Ação & Sensibilidade de Arremesso"
                act1["title"] = "BLANK DE ALTA SENSIBILIDADE E ARREMESSOS DE PRECISÃO"
                act1["desc_tmpl"] = "Projetada para pescadores que exigem leitura imediata da isca e fisgadas rápidas, a {title} combina leveza, equilíbrio de blank e reserva de potência para dominar predadores esportivos com total controle."
                act2["tag"] = "Passadores & Cabo Ergonômico"
                act2["title"] = "PASSADORES RESISTENTES À ABRASÃO E EMPUNHADURA FIRME"
                act2["desc_tmpl"] = "Equipada com passadores dimensionados para reduzir o atrito de linhas multifilamento e monofilamento, além de reel seat anatômico e cabo ergonômico de alta aderência para horas de arremessos sem fadiga."
                act3["tag"] = "Resistência & Envergadura"
                act3["title"] = "RESERVA DE POTÊNCIA PARA BRIGAS INTENSAS"
                act3["desc_tmpl"] = "Construção robusta que distribui a tensão de forma progressiva ao longo do blank, garantindo segurança nas fisgadas e durabilidade superior em água doce ou salgada."
            elif any(w in t_low for w in ["linha ", "multifilamento", "monofilamento", "fluorocarbon", "leader"]):
                act1["tag"] = "Resistência Linear & Sensibilidade"
                act1["title"] = "ALTA RESISTÊNCIA À TRAÇÃO E SENSIBILIDADE IMEDIATA"
                act1["desc_tmpl"] = "Desenvolvida para oferecer máxima confiabilidade entre o pescador e o troféu, a {title} entrega diâmetro uniforme, baixíssima memória mecânica e resposta instantânea na fisgada."
                act2["tag"] = "Arremesso Suave & Abrasão"
                act2["title"] = "DESLIZAMENTO MACIO NOS PASSADORES E PROTEÇÃO ANTI-ABRASÃO"
                act2["desc_tmpl"] = "Superfície tratada para reduzir o atrito nos passadores, permitindo arremessos mais longos e silenciosos, além de elevada resistência contra estruturas submersas, galhadas e pedras."
                act3["tag"] = "Força de Nó & Durabilidade"
                act3["title"] = "SEGURANÇA SUPERIOR EM NÓS E TENSÃO CONTÍNUA"
                act3["desc_tmpl"] = "Fibras selecionadas com tratamento impermeabilizante que evita absorção de água e preserva a resistência original mesmo após longas jornadas de pesca."
            elif "argola" in t_low:
                act1["tag"] = "Conexão de Alta Tração"
                act1["title"] = "ARGOLAS (SPLIT RINGS) EM AÇO INOX DE ALTA MEMÓRIA ELÁSTICA"
                act1["desc_tmpl"] = "Desenvolvida para conectar garatéias, anzóis inline e snaps às iscas artificiais com máxima segurança, a {title} possui construção espiral sem trava de altíssima resistência à tração."
                act2["tag"] = "Memória Mecânica Calibrada"
                act2["title"] = "RESISTÊNCIA EXTREMA SEM DEFORMAÇÃO APÓS A TROCA DE GARATÉIAS"
                act2["desc_tmpl"] = "Fabricada em aço inoxidável forjado com memória mecânica calibrada: abre para a passagem do olhal com alicate de split ring e retorna imediatamente ao fechamento original sem perder pressão."
                act3["tag"] = "Durabilidade Anticorrosiva"
                act3["title"] = "PROTEÇÃO INTEGRAL CONTRA FERRUGEM EM ÁGUA DOCE E SALGADA"
                act3["desc_tmpl"] = "Acabamento polido anticorrosivo que mantém a integridade estrutural e não altera o equilíbrio nem a flutuação das suas iscas artificiais."
            elif any(w in t_low for w in ["anzol", "anzois", "anzóis", "garateia", "garatéia", "snap", "girador", "encastoado", "empate", "chumbada", "boia", "bóia", "jig head"]):
                act1["tag"] = "Fisgada Rápida & Segurança"
                act1["title"] = "AÇO DE ALTA RESISTÊNCIA E CONFIABILIDADE EXTREMA"
                act1["desc_tmpl"] = "Componente essencial para não perder o troféu na hora decisiva, o(a) {title} é fabricado(a) em liga metálica de alta tenacidade para suportar forte tração sem abrir ou deformar."
                act2["tag"] = "Precisão & Acabamento"
                act2["title"] = "GEOMETRIA PRECISA E PROTEÇÃO ANTI-CORROSÃO"
                act2["desc_tmpl"] = "Acabamento técnico com tratamento superficial anticorrosivo que preserva a integridade e a eficiência mecânica em pescarias de água doce ou salgada."
                act3["tag"] = "Performance Profissional"
                act3["title"] = "PADRONIZAÇÃO RIGOROSA PARA MONTAGENS SEGURAS"
                act3["desc_tmpl"] = "Dimensionamento exato que garante equilíbrio na apresentação da isca e máxima segurança durante o trabalho e a briga com grandes peixes."

        # 9.5 Adaptação 360° por Subtipo de Iscas Artificiais (fishing_lures)
        elif archetype_id == "fishing_lures":
            if any(w in t_low for w in ["soft", "criatura", "crayfish"]):
                act1["tag"] = "Elastômero Flexível & Vibração"
                act1["title"] = "CORPO MACIO DE ALTA ELASTICIDADE E NADO NATURAL REALISTA"
                act1["desc_tmpl"] = "Desenvolvida em elastômero macio de alta flexibilidade e resistência, a {title} possui apêndices e garras vibrantes que movimentam a água ao menor toque de ponta de vara, simulando com perfeição uma presa natural no fundo ou meia-água."
                act2["tag"] = "Montagem Versátil Anti-Enrosco"
                act2["title"] = "IDEAL PARA MONTAGENS COM ANZOL OFFSET, JIG HEAD OU TEXAS RIG"
                act2["desc_tmpl"] = "Sua anatomia equilibrada permite montagens anti-enrosco com anzol Offset (Texas Rig, Carolina Rig, Florida Rig) ou com Jig Head, trabalhando com eficiência dentro de galhadas, estruturas submersas, pedras e vegetação."
                act3["tag"] = "Durabilidade & Poder Atrativo"
                act3["title"] = "ALTA RESISTÊNCIA A MORDIDAS E APRESENTAÇÃO IRRESISTÍVEL"
                act3["desc_tmpl"] = "Composto polimérico flexível projetado para suportar múltiplos ataques de predadores sem rasgar facilmente, mantendo a maciez necessária para que o peixe retenha a isca por mais tempo na boca e garanta fisgadas certeiras."
                new_specs = [
                    {"label": "Tipo / Construção", "value": "Isca Artificial Soft em elastômero flexível de alta resistência"},
                    {"label": "Ação do Trabalho", "value": "Fundo e Meia-Água com garras/apêndices de vibração contínua"},
                    {"label": "Montagem Recomendada", "value": "Anzol Offset (anti-enrosco), Jig Head, Texas Rig ou Jig Trailer"},
                    {"label": "Diferencial", "value": "Textura macia realista que prolonga a retenção na boca do predador"},
                    {"label": "Peixes Indicados", "value": "Traíra, Black Bass, Tucunaré, Robalo, Dourado e predadores de estrutura"}
                ]
            elif any(w in t_low for w in ["frog", "sapinho", "sapo"]):
                act1["tag"] = "Superfície Anti-Enrosco"
                act1["title"] = "CORPO OCO MACIO PARA PESCA SOBRE VEGETAÇÃO E GALHADAS"
                act1["desc_tmpl"] = "Projetada especialmente para desafiar estruturas fechadas, aguapés, capinzais e galhadas onde os grandes predadores se escondem, a {title} desliza sobre a superfície sem enroscar e provoca ataques explosivos."
                act2["tag"] = "Anzol Duplo Colado ao Corpo"
                act2["title"] = "SISTEMA DE COMPRESSÃO RÁPIDA E FISGADA EFICIENTE"
                act2["desc_tmpl"] = "Equipada com anzol duplo reforçado posicionado rente ao dorso macio: no momento do bote, o corpo flexível se comprime instantaneamente e expõe as pontas afiadas para uma fisgada limpa e segura."
                act3["tag"] = "Cerdas Atrativas & Equilíbrio"
                act3["title"] = "CERDAS TRASEIRAS VIBRATÓRIAS E PESO TRASEIRO BALANCEADO"
                act3["desc_tmpl"] = "Conta com cerdas de borracha nas extremidades que simulam o movimento das patas na água e lastro traseiro calibrado para arremessos precisos e trabalho em Zara curta ou toques contínuos."
                new_specs = [
                    {"label": "Tipo / Construção", "value": "Isca Artificial Frog (Sapo) de corpo oco macio anti-enrosco"},
                    {"label": "Ação do Trabalho", "value": "Superfície (Anti-Enrosco sobre vegetação, aguapés e estruturas)"},
                    {"label": "Armação", "value": "Anzol duplo em aço carbono de alta penetração integrado ao corpo"},
                    {"label": "Atrativo Extra", "value": "Cerdas traseiras flexíveis que simulam patas em movimento"},
                    {"label": "Peixes Indicados", "value": "Traíra, Trairão, Tucunaré, Black Bass e predadores de superfície"}
                ]
            elif "jig" in t_low:
                act1["tag"] = "Metal Jig de Alta Densidade"
                act1["title"] = "PERFIL HIDRODINÂMICO EM LIGA METÁLICA PARA ARREMESSOS EXTREMOS"
                act1["desc_tmpl"] = "Construída em liga metálica compacta de alta densidade, a {title} corta o vento com facilidade para alcançar longas distâncias de arremesso e afunda rapidamente até a zona de ação dos predadores."
                act2["tag"] = "Queda Errática & Brilho 3D"
                act2["title"] = "AÇÃO FLUTTERING VIBRATÓRIA NA DESCIDA E NO RECOLHIMENTO"
                act2["desc_tmpl"] = "Seu centro de gravidade balanceado produz um nado errático e deslizante durante a queda livre e nos toques de ponta de vara (Jigging vertical ou arremesso), emitindo reflexos intensos que despertam o ataque por reflexo."
                act3["tag"] = "Pintura Holográfica & Olhos 3D"
                act3["title"] = "ACABAMENTO METALIZADO MULTICAMADAS DE ALTA VISIBILIDADE"
                act3["desc_tmpl"] = "Revestimento holográfico espelhado com olhos 3D realistas que refletem a luminosidade mesmo em águas profundas ou turvas, resistindo ao desgaste severo da pesca em água doce ou salgada."
                new_specs = [
                    {"label": "Tipo / Construção", "value": "Metal Jig / Jumping Jig em liga metálica de alta densidade"},
                    {"label": "Ação do Trabalho", "value": "Meia-Água e Fundo (Jigging vertical ou recolhimento com toques)"},
                    {"label": "Acabamento", "value": "Pintura holográfica espelhada multicamadas com olhos 3D"},
                    {"label": "Diferencial", "value": "Perfil compacto aerodinâmico para arremessos longos e descida rápida"},
                    {"label": "Peixes Indicados", "value": "Tucunaré, Robalo, Dourado, Xaréu, Olhete, Anchova e predadores esportivos"}
                ]
            else:
                if "silent" in t_low:
                    act2["tag"] = "Apresentação Furtiva (Silent)"
                    act2["title"] = "SISTEMA SILENT COM PESOS FIXOS DE TUNGSTÊNIO PARA PEIXES MANHOSOS"
                    act2["desc_tmpl"] = "Projetada sem esferas de chocalho (Silent) e com lastros internos fixos perfeitamente equilibrados, entrega nado deslizante natural e silencioso, sendo letal em dias de alta pressão de pesca ou águas cristalinas com predadores ariscos."
                if "popper" in t_low:
                    acao_exata = "Superfície (Popper — estalos e bolhas na flor d'água)"
                elif any(w in t_low for w in ["superficie", "superfície", "bonnie", "zara", "stick"]):
                    acao_exata = "Superfície (Zara / Stick — nado em Z na flor d'água)"
                elif any(w in t_low for w in ["fundo", "deep"]):
                    acao_exata = "Fundo / Meia-Água Profunda (Barbela de imersão rápida)"
                else:
                    acao_exata = "Meia-Água (Floating / Suspending com nado errático provocante)"
                for sp in new_specs:
                    if "ação" in sp["label"].lower():
                        sp["value"] = acao_exata
                    elif "sistema sonoro" in sp["label"].lower() and "silent" in t_low:
                        sp["value"] = "Silent (Silenciosa — sem chocalho, ideal para peixes manhosos e águas claras)"

        # 9.8 Adaptação 360° por Subtipo de Caixas, Bolsas e Organização (tackle_boxes_storage)
        elif archetype_id == "tackle_boxes_storage":
            if "primeiros socorros" in t_low or "bolsa tática" in t_low or "bolsa tatica" in t_low:
                act1["tag"] = "Organização Tática & Emergência"
                act1["title"] = "BOLSA TÁTICA MODULAR PARA KIT DE PRIMEIROS SOCORROS E UTILIDADES"
                act1["desc_tmpl"] = "Desenvolvida para manter itens de primeiros socorros, medicamentos e equipamentos de emergência sempre organizados e acessíveis em pescarias, acampamentos e expedições, a {title} oferece estrutura compacta de pronta resposta."
                act2["tag"] = "Sistema Modular & Engate Rápido"
                act2["title"] = "TIRAS DE FIXAÇÃO MODULAR (MOLLE), FIVELA DE TRAVA E DIVISÓRIAS ELÁSTICAS"
                act2["desc_tmpl"] = "Equipada com cinta externa de segurança com fivela de engate rápido, tiras traseiras com botões de pressão para acoplamento em mochilas, coletes ou cintos, e compartimento interno com fitas elásticas organizadoras."
                act3["tag"] = "Nylon Oxford de Alta Densidade"
                act3["title"] = "CONSTRUÇÃO ROBUSTA RESISTENTE À ABRASÃO E INTEMPÉRIES"
                act3["desc_tmpl"] = "Confeccionada em nylon Oxford 600D de alta tenacidade resistente a respingos e atrito severo, contando com emblema frontal de identificação de emergência e abertura ampla de 180° para visualização imediata."
                new_specs = [
                    {"label": "Categoria", "value": "Bolsa Tática Modular de Primeiros Socorros e Emergência Deyu"},
                    {"label": "Material Externo", "value": "Nylon Oxford 600D de alta densidade resistente à abrasão e respingos"},
                    {"label": "Fixação & Fechamento", "value": "Sistema modular traseiro com botões de pressão + Cinta frontal com fivela de engate rápido"},
                    {"label": "Organização Interna", "value": "Abertura ampla com divisórias e fitas elásticas de fixação firme"},
                    {"label": "Aplicação", "value": "Pesca esportiva, camping, trilhas, veículos 4x4, barcos e primeiros socorros"}
                ]
            elif "suporte porta iscas" in t_low or ("porta iscas" in t_low and "inox" in t_low):
                act1["tag"] = "Organização Rápida na Embarcação"
                act1["title"] = "SUPORTE ORGANIZADOR EM AÇO INOXIDÁVEL PARA ISCAS, ALICATES E TESOURA"
                act1["desc_tmpl"] = "Projetado para manter suas iscas artificiais mais utilizadas e ferramentas de contenção/corte sempre à mão na borda do barco ou lancha, o {title} elimina a bagunça no convés e agiliza a troca de iscas durante a pescaria."
                act2["tag"] = "Fendas de Encaixe & Elástico"
                act2["title"] = "5 RANHURAS FRONTAIS PARA GARATÉIAS E COMPARTIMENTO COM TRAVA ELÁSTICA"
                act2["desc_tmpl"] = "Conta com 5 fendas frontais usinadas para pendurar iscas artificiais pelas garatéias sem enroscar e aberturas superiores dimensionadas para acomodar alicates e tesoura de pesca, com cordão elástico de retenção lateral."
                act3["tag"] = "Aço Inox Escovado Naval"
                act3["title"] = "CHAPA DE AÇO INOXIDÁVEL DOBRADA IMUNE À FERRUGEM E À MARESIA"
                act3["desc_tmpl"] = "Fabricado integralmente em aço inoxidável escovado de alta espessura com furos de fixação, suportando sol, chuva e ambiente marinho por muitos anos com zero manutenção."
                new_specs = [
                    {"label": "Categoria", "value": "Suporte Organizador de Embarcação em Aço Inox Pesca Plus"},
                    {"label": "Material", "value": "Aço Inoxidável escovado de alta resistência à corrosão (água doce e salgada)"},
                    {"label": "Capacidade", "value": "5 fendas frontais para iscas artificiais + Alojamentos superiores para alicates e tesoura"},
                    {"label": "Segurança", "value": "Elástico retentor integrado para manter os alicates firmes durante a navegação"},
                    {"label": "Instalação", "value": "Fixação prática na borda ou console de barcos, lanchas e caiaques"}
                ]

        # 10. Adaptação 360° para Geladeiras Portáteis e Bolsas Térmicas (drinkware_thermo)
        elif archetype_id == "drinkware_thermo":
            if "geladeira" in t_low:
                act1["tag"] = "Refrigeração Portátil 12V/24V"
                act1["title"] = "COMPRESSOR DE ALTA EFICIÊNCIA PARA EXPEDIÇÕES E ESTRADA"
                act1["desc_tmpl"] = "Desenvolvida para garantir conservação térmica profissional em viagens, pescarias, caminhões, motorhomes e acampamentos, a {title} entrega refrigeração rápida e estável mesmo sob altas temperaturas externas."
                act2["tag"] = "Economia de Bateria & Controle"
                act2["title"] = "PAINEL DIGITAL INTELIGENTE COM PROTEÇÃO DE BATERIA"
                act2["desc_tmpl"] = "Conta com controle preciso de temperatura e módulo inteligente de proteção contra descarga da bateria veicular, operando com baixo consumo energético e mínima emissão de ruído."
                act3["tag"] = "Gabinete Robusto & Isolamento"
                act3["title"] = "ESTRUTURA REFORÇADA PARA TERRENOS SEVEROS"
                act3["desc_tmpl"] = "Isolamento térmico de alta densidade, trava de tampa segura e construção resistente a vibrações e inclinações em trilhas, barcos e estradas."
                new_specs = [
                    {"label": "Alimentação", "value": "12V / 24V DC (bateria veicular/náutica)"},
                    {"label": "Tecnologia de Refrigeração", "value": "Compressor hermético de alta performance"},
                    {"label": "Controle de Temperatura", "value": "Painel digital com ajuste preciso e módulo protetor de bateria"},
                    {"label": "Isolamento", "value": "Poliuretano expandido de alta densidade livre de CFC"},
                    {"label": "Aplicação", "value": "Pesca, camping, overland, caminhões, barcos e viagens"}
                ]
            elif any(w in t_low for w in ["bolsa termica", "bolsa térmica", "caixa termica", "caixa térmica", "cooler"]):
                act1["tag"] = "Conservação Térmica Portátil"
                act1["title"] = "ISOLAMENTO TÉRMICO DE ALTA DENSIDADE PARA SUAS AVENTURAS"
                act1["desc_tmpl"] = "Perfeita para manter bebidas e alimentos na temperatura ideal durante pescarias, viagens e lazer ao ar livre, a {title} alia excelente capacidade interna e praticidade de transporte."
                act2["tag"] = "Impermeabilidade & Higiene"
                act2["title"] = "REVESTIMENTO INTERNO SELADO E FÁCIL DE LIMPAR"
                act2["desc_tmpl"] = "Camada interna impermeável que evita vazamentos, não retém odores e facilita a higienização rápida após o uso."
                act3["tag"] = "Transporte Confortável"
                act3["title"] = "ESTRUTURA EXTERNA RESISTENTE E ALÇAS REFORÇADAS"
                act3["desc_tmpl"] = "Construída com materiais externos resistentes à abrasão, fechamento superior reforçado de alta vedação e alças ergonômicas para transporte seguro em qualquer ambiente."
                new_specs = [
                    {"label": "Construção Externa", "value": "Material sintético de alta resistência à abrasão e respingos"},
                    {"label": "Isolamento Térmico", "value": "Espuma térmica de célula fechada com manta aluminizada interna"},
                    {"label": "Revestimento Interno", "value": "Impermeável, atóxico e de fácil higienização"},
                    {"label": "Transporte", "value": "Alças reforçadas com ajuste ergonômico"},
                    {"label": "Uso Recomendado", "value": "Pescarias, praia, camping, viagens e dia a dia"}
                ]

        # 11. Adaptação 360° para Calça Jeans / Denim (pants_cargo_tactical)
        elif archetype_id == "pants_cargo_tactical" and any(w in t_low for w in ["jeans", "denim"]):
            is_fem_jeans = "feminina" in t_low or "feminino" in t_low
            act1["tag"] = "Denim Encorpado & Tradição"
            act1["title"] = "JEANS COUNTRY FEMININO DE ALTA GRAMATURA E CAIMENTO ANATÔMICO" if is_fem_jeans else "JEANS DE ALTA GRAMATURA PARA A LIDA E O DIA A DIA"
            act1["desc_tmpl"] = (
                "Desenvolvida para unir a resistência do legítimo Jeans Country a uma modelagem anatômica que valoriza a silhueta feminina, a {title} garante conforto superior na sela, em rodeios ou no dia a dia."
                if is_fem_jeans else
                "Desenvolvida para suportar a rotina intensa no campo, viagens e uso casual com elegância rústica, a {title} une tecido Denim resistente a um corte anatômico que garante conforto na sela, na caminhonete ou na cidade."
            )
            act2["tag"] = "Conforto & Mobilidade"
            act2["title"] = "CAIMENTO ESTRUTURADO COM LIBERDADE DE MOVIMENTOS"
            act2["desc_tmpl"] = "Modelagem tradicional pensada para não prender os movimentos ao agachar ou montar, com toque macio interno e excelente estabilidade dimensional após a lavagem."
            act3["tag"] = "Costuras Reforçadas & Rebites"
            act3["title"] = "ACABAMENTO REFORÇADO COM 5 BOLSOS FUNCIONAIS"
            act3["desc_tmpl"] = "Equipada com 5 bolsos funcionais profundos, passantes largos para cinto country, zíper metálico de alta trava e costuras reforçadas nos pontos de maior tensão."
            new_specs = [
                {"label": "Tecido Principal", "value": "Denim / Jeans de alta gramatura e resistência"},
                {"label": "Modelagem", "value": "Country Feminina anatômica com cintura estruturada" if is_fem_jeans else "Tradicional / Country Masculina anatômica com ótimo caimento"},
                {"label": "Bolsos", "value": "5 bolsos funcionais profundos com rebites de reforço"},
                {"label": "Costuras & Cós", "value": "Pesponto reforçado e passantes largos para cinto"},
                {"label": "Fechamento", "value": "Braguilha com zíper metálico reforçado e botão personalizado"},
                {"label": "Indicação de Uso", "value": "Lida no campo, rodeios, viagens e uso diário"}
            ]

        # 12. Adaptação 360° para Botinas Country / Agro e Tênis de Pesca RaptorX (closed_footwear_sneakers)
        elif archetype_id == "closed_footwear_sneakers":
            if "raptorx" in t_low or "tênis" in t_low or "tenis" in t_low:
                act1["tag"] = "Performance Anfíbia & Estabilidade"
                act1["title"] = "CANO MÉDIO COM SUPORTE DE TORNOZELO E CABEDAL RESPIRÁVEL DE DRENAGEM RÁPIDA"
                act1["desc_tmpl"] = "Desenvolvido especialmente para pescadores esportivos e aventureiros que enfrentam pedras molhadas, barrancos, caiaques e convés de embarcações, o {title} combina estrutura firme de cano médio com cabedal em trama respirável que não retém água e acelera a secagem."
                act2["tag"] = "Amarração Rápida & Proteção"
                act2["title"] = "GANCHOS METÁLICOS SUPERIORES, BIQUEIRA REFORÇADA E PALMILHA DE ABSORÇÃO"
                act2["desc_tmpl"] = "Equipado com passadores reforçados e ganchos metálicos superiores para ajuste firme no tornozelo, biqueira frontal estruturada contra impactos em pedras e galhos, puxador traseiro de calce ágil e palmilha macia de alta densidade."
                act3["tag"] = "Tração Extrema Multi-Terreno"
                act3["title"] = "SOLADO TRATORADO DE BORRACHA ANTIDERRAPANTE PARA SUPERFÍCIES MOLHADAS"
                act3["desc_tmpl"] = "Solado robusto com garras multidirecionais profundas que expulsam a lama e a água, garantindo aderência superior em pisos lisos de barcos, margens de rios, trilhas úmidas e terrenos acidentados."
                new_specs = [
                    {"label": "Cabedal", "value": "Trama técnica respirável de secagem rápida com reforços estruturais em PU"},
                    {"label": "Cano & Fechamento", "value": "Cano médio com acolchoamento no tornozelo e cadarço com ganchos metálicos superiores"},
                    {"label": "Proteção Frontal", "value": "Biqueira e calcanhar estruturados contra impactos em pedras e estruturas"},
                    {"label": "Solado", "value": "Borracha tratorada antiderrapante com sulcos de escoamento de água e lama"},
                    {"label": "Indicação de Uso", "value": "Pesca esportiva (embarcada, caiaque ou barranco), trilhas, camping e aventura"}
                ]
            elif any(w in t_low for w in ["botina", "bota "]):
                is_fem_boot = "feminina" in t_low or "feminino" in t_low
                estilo_publico = "design country feminino elegante e anatômico" if is_fem_boot else "design country tradicional robusto"
                act1["tag"] = "Tradição & Robustez no Campo"
                act1["title"] = "COURO LEGÍTIMO E ESTRUTURA REFORÇADA PARA A LIDA E O ESTILO COUNTRY"
                act1["desc_tmpl"] = f"Projetada com {estilo_publico} para enfrentar a rotina na fazenda, eventos sertanejos e uso prolongado com máximo conforto, a {{title}} entrega proteção superior aos pés e durabilidade comprovada."
                act2["tag"] = "Solado Blaqueado de Alta Tração"
                act2["title"] = "SOLADO DE BORRACHA ANTIDERRAPANTE COM ACABAMENTO BLAQUEADO LATERAL"
                act2["desc_tmpl"] = "Solado tratorado antiderrapante com borda blaqueada de alta tenacidade e brasão western no salto, garantindo estabilidade na terra, estribo ou piso molhado, aliado a palmilha macia que reduz a fadiga plantar."
                act3["tag"] = "Calce Fácil & Ajuste Firme"
                act3["title"] = "ELÁSTICOS LATERAIS COBERTOS E PUXADOR TRASEIRO ANATÔMICO"
                act3["desc_tmpl"] = "Cabedal estruturado em couro nobre com elásticos laterais de alta memória e puxadores superiores que facilitam o calce rápido e mantêm o ajuste firme no tornozelo ao longo do dia."
                new_specs = [
                    {"label": "Cabedal", "value": "Couro legítimo selecionado de alta resistência e toque macio"},
                    {"label": "Solado", "value": "Borracha antiderrapante de alta tração com acabamento blaqueado lateral"},
                    {"label": "Palmilha", "value": "Anatômica em espuma de alta densidade com absorção de impacto"},
                    {"label": "Sistema de Calce", "value": "Calce fácil Chelsea com elásticos laterais reforçados e puxador"},
                    {"label": "Uso Recomendado", "value": "Lida no campo, agronegócio, rodeios, cavalgadas e uso diário"}
                ]

        # 12.1 Adaptação 360° para Sandálias/Babuches vs Chinelos Boaonda (footwear_sandals_boaonda)
        elif archetype_id == "footwear_sandals_boaonda":
            if "chinelo" in t_low:
                act1["tag"] = "Conforto Ortopédico Extremo"
                act1["title"] = "CHINELO ANATÔMICO DE ABSORÇÃO DE IMPACTO PARA PÉS SENSÍVEIS"
                act1["desc_tmpl"] = "Desenvolvido com engenharia ergonômica para proporcionar alívio imediato à planta dos pés, calcanhares e articulações, o {title} absorve até 80% do impacto da pisada no uso diário, pós-pescaria ou lazer."
                act2["tag"] = "Tiras Largas & Base Texturizada"
                act2["title"] = "TIRAS ANATÔMICAS VENTILADAS E PALMILHA TEXTURIZADA ANTIESTRESSE"
                act2["desc_tmpl"] = "Conta com tiras largas flexíveis com aberturas laterais de ventilação que não machucam o peito do pé e base interna levemente texturizada que estimula a circulação plantar e evita que o pé escorregue."
                act3["tag"] = "Termoplástico 100% Impermeável"
                act3["title"] = "SOLADO ANTIDERRAPANTE, ANTIBACTERIANO E LIVRE DE ODORES"
                act3["desc_tmpl"] = "Produzido integralmente em elastômero termoplástico nobre Boaonda 100% impermeável, fácil de lavar, imune a deformações e seguro para pisos molhados de barcos, piscinas e áreas externas."
                new_specs = [
                    {"label": "Modelo", "value": "Chinelo de dedo anatômico ortopédico com tiras largas ventiladas"},
                    {"label": "Material", "value": "Termoplástico nobre Boaonda (TR/EVA) flexível, antiodor e lavável"},
                    {"label": "Biomecânica", "value": "Absorção superior de impacto (ideal para esporão de calcâneo e fascite plantar)"},
                    {"label": "Solado", "value": "Antiderrapante com ranhuras de segurança para pisos úmidos"},
                    {"label": "Origem / Distribuição", "value": "Produto 100% Original Boaonda com garantia oficial"}
                ]
            else:
                act1["tag"] = "Palmilha Maxisense Anti-Impacto"
                act1["title"] = "SANDÁLIA BABUCHE ORTOPÉDICA COM AMORTECIMENTO PROLONGADO"
                act1["desc_tmpl"] = "Projetada para oferecer descanso ativo e proteção integral aos pés durante longas horas em pé no barco, no pesqueiro ou na rotina diária, a {title} conta com palmilha anatômica removível de altíssima absorção de impacto."
                act2["tag"] = "Alça Reversível & Ventilação"
                act2["title"] = "USO 2 EM 1 COM TIRA TRASEIRA MÓVEL E ABERTURAS DE DRENAGEM"
                act2["desc_tmpl"] = "Sua alça traseira articulada permite usar como sandália presa ao calcanhar para caminhadas e navegação segura ou rebatida à frente como babuche/clog de calce rápido, com janelas laterais que ventilam os pés e escoam a água."
                act3["tag"] = "Solado Naval Antiderrapante"
                act3["title"] = "POLÍMERO NOBRE IMPERMEÁVEL, ANTIBACTERIANO E DE FÁCIL LIMPEZA"
                act3["desc_tmpl"] = "Injetada em termoplástico flexível Boaonda que não retém odores, seca em instantes e oferece aderência confiável em convés molhado de embarcações, pedras, rampas e pisos lisos."
                new_specs = [
                    {"label": "Modelo", "value": "Sandália Babuche / Clog fechada na frente com alça traseira reversível 2 em 1"},
                    {"label": "Material do Cabedal", "value": "Termoplástico nobre Boaonda flexível, impermeável e fácil de lavar"},
                    {"label": "Palmilha", "value": "Anatômica anti-impacto removível (alívio para esporão e fascite plantar)"},
                    {"label": "Ventilação & Solado", "value": "Aberturas laterais de respiração/drenagem e solado antiderrapante"},
                    {"label": "Origem / Distribuição", "value": "Produto 100% Original Boaonda com garantia oficial"}
                ]

        # 12.2 Adaptação 360° para Óculos de Sol Polarizados UV400 (eyewear_sunglasses)
        elif archetype_id == "eyewear_sunglasses":
            if "infantil" in t_low or "kids" in t_low:
                act1["tag"] = "Proteção Ocular Infantil UV400"
                act1["title"] = "LENTES POLARIZADAS COM BLOQUEIO 100% UVA E UVB PARA OS PEQUENOS"
                act1["desc_tmpl"] = "Desenvolvido especialmente para proteger a visão sensível das crianças sob o sol forte, o {title} conta com lentes polarizadas UV400 que eliminam o ofuscamento da água e da areia com conforto visual imediato."
                act2["tag"] = "Armação Infantil Flexível & Leve"
                act2["title"] = "DIMENSIONAMENTO ANATÔMICO INFANTIL RESISTENTE A QUEDAS E BRINCADEIRAS"
                act2["desc_tmpl"] = "Construído em polímero leve, flexível e seguro com encaixe sob medida para o rosto infantil, oferecendo firmeza sem apertar as têmporas ou escorregar pelo nariz durante as brincadeiras."
                act3["tag"] = "Aventura em Família"
                act3["title"] = "DESIGN COLORIDO EXCLUSIVO COM ESTOJO E FLANELA INCLUSOS"
                act3["desc_tmpl"] = "Perfeito para acompanhar os pequenos aventureiros em pescarias em família, praia, piscina, passeios no campo e atividades ao ar livre com muito estilo e proteção."
                new_specs = [
                    {"label": "Tecnologia das Lentes", "value": "Polarizadas TAC com filtro antirreflexo e proteção UV400"},
                    {"label": "Proteção Solar", "value": "100% de bloqueio contra raios nocivos UVA e UVB"},
                    {"label": "Material da Armação", "value": "Polímero infantil flexível ultraleve e resistente a impactos"},
                    {"label": "Dimensionamento", "value": "Anatômico Infantil / Juvenil de encaixe seguro e confortável"},
                    {"label": "Itens Inclusos", "value": "Estojo protetor oficial BRK e flanela especial de microfibra"},
                    {"label": "Uso Recomendado", "value": "Praia, piscina, pescarias em família, passeios ao ar livre e lazer infantil"}
                ]
            elif any(w in t_low for w in ["bambu", "bamboo", "wood", "madeira", "timber"]):
                act2["tag"] = "Design Nobre & Leveza"
                act2["title"] = "FRONTAL DE ALTA RESISTÊNCIA COMBINADO A HASTES EM MADEIRA / BAMBU NATURAL"
                act2["desc_tmpl"] = "Sua estrutura une frontal ergonômico de alta tenacidade a hastes trabalhadas em madeira/bambu natural legítimo, resultando em um óculos extremamente leve, equilibrado e com acabamento artesanal exclusivo."
                act3["tag"] = "Dobradiças Flexíveis & Conforto"
                act3["title"] = "DOBRADIÇAS METÁLICAS COM MOLA FLEXÍVEL PARA ENCAIXE SOB MEDIDA"
                act3["desc_tmpl"] = "Equipado com dobradiças metálicas com sistema de mola (Spring Hinge) que se adaptam suavemente a diferentes larguras de rosto sem pressionar as têmporas, acompanhando estojo protetor e flanela."
                new_specs = [
                    {"label": "Tecnologia das Lentes", "value": "Polarizadas TAC de alta definição com filtro antirreflexo"},
                    {"label": "Proteção Solar", "value": "Fator UV400 com 100% de bloqueio contra raios UVA e UVB"},
                    {"label": "Material da Armação", "value": "Frontal em polímero nobre com hastes artesanais em Bambu / Madeira natural"},
                    {"label": "Articulação", "value": "Dobradiças metálicas reforçadas com mola flexível autoajustável"},
                    {"label": "Itens Inclusos", "value": "Estojo protetor oficial BRK e flanela especial de microfibra"},
                    {"label": "Uso Recomendado", "value": "Pesca esportiva, náutica, direção, campo e estilo casual ao ar livre"}
                ]
            elif any(w in t_low for w in ["aviador", "aviator", "metal", "steel", "octagon", "rose gold", "maverick", "dubai", "Ibiza".lower()]):
                act2["tag"] = "Armação Metálica Nobre"
                act2["title"] = "ESTRUTURA EM LIGA METÁLICA ANTICORROSIVA E PLAQUETAS NASAIS AJUSTÁVEIS"
                act2["desc_tmpl"] = "Construído com perfil metálico fino de alta rigidez e baixíssimo peso, equipado com plaquetas nasais anatômicas ajustáveis que garantem apoio suave e personalizado sem marcar o rosto."
                new_specs = [
                    {"label": "Tecnologia das Lentes", "value": "Polarizadas TAC de alta definição com filtro antirreflexo HD"},
                    {"label": "Proteção Solar", "value": "Fator UV400 com 100% de bloqueio contra raios UVA e UVB"},
                    {"label": "Material da Armação", "value": "Liga metálica nobre anticorrosiva de baixo peso e alta durabilidade"},
                    {"label": "Apoio Nasal", "value": "Plaquetas anatômicas macias e ajustáveis para encaixe preciso"},
                    {"label": "Itens Inclusos", "value": "Estojo protetor oficial BRK e flanela especial de microfibra"},
                    {"label": "Uso Recomendado", "value": "Pesca esportiva, direção, viagens, campo e uso diário ao ar livre"}
                ]
            else:
                new_specs = [
                    {"label": "Tecnologia das Lentes", "value": "Polarizadas TAC de alta definição com filtro antirreflexo HD"},
                    {"label": "Proteção Solar", "value": "Fator UV400 com 100% de bloqueio contra raios UVA e UVB"},
                    {"label": "Material da Armação", "value": "Policarbonato / Acetato ultraleve de alta resistência a impactos"},
                    {"label": "Apoio Nasal", "value": "Ponte anatômica integrada que distribui o peso sem marcar a pele"},
                    {"label": "Itens Inclusos", "value": "Estojo protetor oficial BRK e flanela especial de microfibra"},
                    {"label": "Uso Recomendado", "value": "Pesca esportiva, náutica, direção, ciclismo, campo e uso diário"}
                ]

        # 12.3 Adaptação 360° para Luvas Táticas, Esportivas e de Pesca (gloves_tactical_fishing)
        elif archetype_id == "gloves_tactical_fishing":
            if "dedo inteiro" in t_low or "yl020" in t_low:
                act1["tag"] = "Proteção Dorsal Rígida & Grip"
                act1["title"] = "CASQUILHO PROTETOR NAS ARTICULAÇÕES E PALMA ANTIDERRAPANTE REFORÇADA"
                act1["desc_tmpl"] = "Projetada para operações táticas, motociclismo, trilha e pesca pesada em estruturas fechadas, a {title} integra escudo dorsal rígido absorvedor de impactos sobre os nós dos dedos e palma texturizada de alta aderência."
                act2["tag"] = "Cobertura Integral Dedo Inteiro"
                act2["title"] = "PROTEÇÃO COMPLETA DOS 5 DEDOS COM ENTRADAS DE VENTILAÇÃO NAS FALANGES"
                act2["desc_tmpl"] = "Sua modelagem de dedo inteiro protege integralmente as mãos contra galhos, espinhos, abrasão, sol e vento, contando com dutos de ventilação sobre as falanges que dissipam o calor interno."
                act3["tag"] = "Fixação Firme no Pulso"
                act3["title"] = "FECHAMENTO REGULÁVEL NO PUNHO PARA MÁXIMA ESTABILIDADE"
                act3["desc_tmpl"] = "Equipada com cinta de pulso ajustável de alta fixação que mantém a luva perfeitamente firme na mão durante a pilotagem, manuseio de equipamentos ou trabalho pesado."
                new_specs = [
                    {"label": "Modelagem", "value": "Dedo Inteiro (cobertura integral dos 5 dedos com proteção tática)"},
                    {"label": "Proteção Dorsal", "value": "Casquilho rígido termoplástico nas articulações + respiros nas falanges"},
                    {"label": "Palma da Mão", "value": "Reforço sintético texturizado antiderrapante de alta resistência à abrasão"},
                    {"label": "Ajuste no Punho", "value": "Cinta regulável no pulso com fecho de contato firme"},
                    {"label": "Indicação de Uso", "value": "Motociclismo, trilha, airsoft, operações táticas, pesca e trabalho no campo"}
                ]
            elif "dorsal" in t_low or "yl025" in t_low or "yl018" in t_low:
                act1["tag"] = "Escudo Dorsal & Pegada Firme"
                act1["title"] = "PROTETOR DORSAL NAS ARTICULAÇÕES E PALMA ANTIDERRAPANTE REFORÇADA"
                act1["desc_tmpl"] = "Desenvolvida para unir proteção robusta no dorso da mão e controle absoluto de empunhadura, a {title} conta com proteção estruturada sobre as articulações e palma revestida com textura antiderrapante."
                act2["tag"] = "Corte Meio Dedo de Precisão"
                act2["title"] = "PONTAS DOS DEDOS LIVRES PARA SENSIBILIDADE TÁTIL IMEDIATA"
                act2["desc_tmpl"] = "O corte meio dedo mantém as pontas dos dedos livres para atar nós de pesca, controlar o carretel da carretilha, acionar comandos da moto ou manusear ferramentas com precisão milimétrica."
                act3["tag"] = "Punho Regulável & Respirabilidade"
                act3["title"] = "AJUSTE FIRME NO PULSO E TECIDO VENTILADO DE SECAGEM RÁPIDA"
                act3["desc_tmpl"] = "Construída com dorso respirável que evita o acúmulo de suor e fecho regulável no punho para encaixe anatômico sem folgas."
                new_specs = [
                    {"label": "Modelagem", "value": "Meio Dedo Tática / Esportiva (pontas livres para sensibilidade tátil)"},
                    {"label": "Proteção Dorsal", "value": "Reforço protetor estruturado sobre as articulações do dorso"},
                    {"label": "Palma da Mão", "value": "Material sintético antiderrapante resistente ao atrito contínuo"},
                    {"label": "Ajuste no Punho", "value": "Cinta regulável no pulso de fixação rápida e segura"},
                    {"label": "Indicação de Uso", "value": "Pesca esportiva, motociclismo, ciclismo, tiro esportivo e aventura"}
                ]
            elif "2 dedos" in t_low or "yl013" in t_low:
                act1["tag"] = "Design Especial de Pesca (3 Dedos Livres)"
                act1["title"] = "SENSIBILIDADE MÁXIMA NO POLEGAR, INDICADOR E MÉDIO COM PROTEÇÃO LATERAL"
                act1["desc_tmpl"] = "Projetada especificamente para a mecânica do arremesso com carretilha e molinete, a {title} mantém o polegar, o indicador e o dedo médio expostos para controle fino da linha, enquanto protege integralmente os dedos anelar e mínimo."
                act2["tag"] = "Grip em Silicone na Palma"
                act2["title"] = "PALMA COM TRILHAS ANTIDERRAPANTES PARA CONTROLE DA VARA MOLHADA"
                act2["desc_tmpl"] = "Superfície palmar com aplicação de trilhas de silicone de alta aderência que travam o cabo da vara na mão mesmo sob chuva ou respingos constantes."
                act3["tag"] = "Conforto Térmico & Ajuste"
                act3["title"] = "DORSO CAMUFLADO RESPIRÁVEL E FECHAMENTO REGULÁVEL NO PUNHO"
                act3["desc_tmpl"] = "Tecido elástico leve de secagem ultra rápida com estampa camuflada Florest e ajuste de pulso firme para centenas de arremessos sem fadiga."
                new_specs = [
                    {"label": "Modelagem", "value": "Especial de Pesca (2 dedos cobertos + 3 dedos com pontas livres para arremesso)"},
                    {"label": "Palma da Mão", "value": "Revestimento com trilhas de silicone antiderrapante de alto grip"},
                    {"label": "Dorso", "value": "Malha elástica respirável camuflada Florest de secagem rápida"},
                    {"label": "Ajuste no Punho", "value": "Fechamento regulável anatômico no pulso"},
                    {"label": "Origem / Distribuição", "value": "Produto Original Albatroz Fishing com garantia oficial"}
                ]
            elif "deyu" in t_low:
                act1["tag"] = "Palma Ventilada com Silicone"
                act1["title"] = "MICROPERFURAÇÕES DE RESPIRAÇÃO E PONTOS DE SILICONE ANTIDERRAPANTE"
                act1["desc_tmpl"] = "Ultraleve e anatômica para longas jornadas de pesca sob sol forte, a {title} combina palma microperfurada com matriz de silicone antiderrapante que garante pegada firme e fresca na vara de pesca."
                act2["tag"] = "Proteção Solar UV & Toque Frio"
                act2["title"] = "DORSO EM LYCRA ELÁSTICA RESPIRÁVEL E CORTE MEIO DEDO"
                act2["desc_tmpl"] = "Confeccionada em tecido elástico de toque gelado que protege o dorso das mãos contra a radiação solar enquanto deixa os dedos livres para trocar iscas e fazer nós com agilidade."
                act3["tag"] = "Punho Alongado & Puxador Rápido"
                act3["title"] = "PUNHO ELÁSTICO ANATÔMICO COM ALÇA INTEGRADA PARA CALCE FÁCIL"
                act3["desc_tmpl"] = "Modelagem slip-on sem velcro que não enrosca na linha multifilamento, contando com punho elástico alongado e puxador integrado na base da palma para vestir com rapidez."
                new_specs = [
                    {"label": "Modelagem", "value": "Meio Dedo de Pesca Slip-On (sem velcro para não enroscar na linha)"},
                    {"label": "Palma da Mão", "value": "Microperfurada respirável com pontos de silicone antiderrapante"},
                    {"label": "Dorso & Punho", "value": "Tecido elástico UV de secagem rápida com puxador de calce rápido Deyu"},
                    {"label": "Origem / Distribuição", "value": "Produto Original Deyu com garantia oficial"}
                ]
            elif "yl015" in t_low:
                act1["tag"] = "Palma Antiderrapante Ventilada"
                act1["title"] = "REFORÇO PALMAR DE ALTA ADERÊNCIA COM ABERTURA CENTRAL DE RESPIRAÇÃO"
                act1["desc_tmpl"] = "Desenvolvida para garantir pegada firme e ventilação contínua na palma da mão durante pescarias, ciclismo e remo, a {title} possui reforço anatômico antiderrapante com respiro central estratégico."
                act2["tag"] = "Agilidade Meio Dedo"
                act2["title"] = "DEDOS LIVRES PARA SENSIBILIDADE TÁTIL E DORSO ELÁSTICO"
                act2["desc_tmpl"] = "Corte meio dedo esportivo que preserva a sensibilidade no toque da linha e carretilha, combinado a dorso flexível de secagem rápida."
                act3["tag"] = "Estabilidade no Pulso"
                act3["title"] = "FECHAMENTO REGULÁVEL NO PUNHO PARA ENCAIXE PERSONALIZADO"
                act3["desc_tmpl"] = "Cinta de pulso com regulagem rápida que mantém a luva estável e previne calosidades e bolhas em movimentos repetitivos."
                new_specs = [
                    {"label": "Modelagem", "value": "Meio Dedo Esportiva com abertura central de ventilação na palma"},
                    {"label": "Palma da Mão", "value": "Reforço sintético antiderrapante contra calosidades e atrito"},
                    {"label": "Dorso", "value": "Tecido elástico respirável de secagem rápida"},
                    {"label": "Ajuste no Punho", "value": "Fita regulável de fixação firme no pulso"},
                    {"label": "Origem / Distribuição", "value": "Produto Original Albatroz Fishing com garantia oficial"}
                ]

        # 12.4 Adaptação 360° para Manguitos de Proteção Solar (sun_sleeves_manguitos)
        elif archetype_id == "sun_sleeves_manguitos":
            if "tattoo" in t_low:
                act1["tag"] = "Arte Full-Print 360° & Proteção UV50+"
                act1["title"] = "ESTAMPA TATTOO EM ALTA DEFINIÇÃO COM BLOQUEIO SOLAR CERTIFICADO"
                act1["desc_tmpl"] = "Desenvolvido para motociclistas, ciclistas e aventureiros que buscam visual autêntico aliado à proteção térmica e solar, o {title} traz arte sublimada em 360° de altíssima definição com fator FPU 50+."
                act2["tag"] = "Ajuste Anatômico Segunda Pele"
                act2["title"] = "MALHA ELÁSTICA DE TOQUE FRIO QUE ABRAÇA O BRAÇO SEM ESCORREGAR"
                act2["desc_tmpl"] = "Confeccionado em poliamida/poliéster tecnológico com elastano de memória elástica que se molda perfeitamente ao contorno do bíceps ao punho, mantendo fixação firme durante a pilotagem."
                act3["tag"] = "Conforto Térmico & Secagem Rápida"
                act3["title"] = "PUNHO TRADICIONAL CONFORTÁVEL E DISSIPAÇÃO IMEDIATA DO SUOR"
                act3["desc_tmpl"] = "Acabamento de punho reto anatômico que encaixa perfeitamente com luvas e relógios, acelerando a evaporação do suor e mantendo os braços frescos sob o sol."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ permanente integrado ao tecido"},
                    {"label": "Estamparia", "value": "Sublimação digital Full-Print 360° de alta definição (Estilo Tattoo)"},
                    {"label": "Modelagem", "value": "Anatômica segunda pele com punho reto tradicional e borda elástica no bíceps"},
                    {"label": "Tecnologia", "value": "Toque frio, alta respirabilidade e secagem ultra rápida (Dry Fit)"},
                    {"label": "Conteúdo da Embalagem", "value": "1 Par de Manguitos (braço direito e esquerdo)"}
                ]
            elif "com proteção" in t_low or "com protecao" in t_low:
                act1["tag"] = "Proteção UV50+ Braço & Dorso da Mão"
                act1["title"] = "COBERTURA SOLAR INTEGRAL DO BÍCEPS AO DORSO DA MÃO COM DEDEIRA"
                act1["desc_tmpl"] = "Projetado para quem exige proteção solar sem brechas na pescaria, no ciclismo ou no trabalho ao ar livre, o {title} bloqueia até 98% dos raios UVA e UVB com tecido de toque gelado."
                act2["tag"] = "Punho com Encaixe de Polegar"
                act2["title"] = "ABERTURA ANATÔMICA PARA O POLEGAR QUE PROTEGE O DORSO DA MÃO"
                act2["desc_tmpl"] = "Conta com encaixe anatômico para o polegar na extremidade inferior, mantendo o manguito esticado sobre o dorso da mão durante arremessos, pedaladas ou condução de veículos."
                act3["tag"] = "Fixação Firme & Frescor"
                act3["title"] = "ELÁSTICO SUPERIOR NO BÍCEPS E EVAPORAÇÃO INSTANTÂNEA DE SUOR"
                act3["desc_tmpl"] = "Borda superior estruturada que impede que a peça escorregue pelo braço, combinada à tecnologia Dry Fit de secagem rápida que mantém a pele fresca o dia inteiro."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ permanente certificado"},
                    {"label": "Diferencial no Punho", "value": "Punho estendido com abertura anatômica para o polegar (protege o dorso da mão)"},
                    {"label": "Fixação Superior", "value": "Borda elástica anatômica de fixação firme no bíceps"},
                    {"label": "Composição & Toque", "value": "Malha tecnológica flexível de toque frio e secagem rápida"},
                    {"label": "Conteúdo da Embalagem", "value": "1 Par de Manguitos (braço direito e esquerdo)"}
                ]

        # 12.5 Adaptação 360° para Bandanas Tubeneck, ArmorX, Black Mask, Balaclavas e Lenços (neck_gaiters_balaclavas)
        elif archetype_id == "neck_gaiters_balaclavas":
            prod_id_str = str(product.get("id") or "")
            if "lenço" in t_low or "lenco" in t_low:
                act1["tag"] = "Proteção Solar & Estilo Versátil"
                act1["title"] = "LENÇO QUADRADO DE AMARRAÇÃO COM PROTEÇÃO SOLAR UV50+"
                act1["desc_tmpl"] = "Desenvolvido em tecido tecnológico leve de toque sedoso e proteção solar FPU 50+ permanente, o {title} protege a cabeça, os cabelos, a nuca ou o pescoço contra o sol e o vento com máxima elegância e frescor."
                act2["tag"] = "Toque Macio & Acabamento"
                act2["title"] = "MODELAGEM QUADRADA PLANA DE FÁCIL AMARRAÇÃO E SECAGEM RÁPIDA"
                act2["desc_tmpl"] = "Sua construção plana com bordas de acabamento refinado permite dobrar e amarrar com firmeza sem escorregar, sem pesar e sem abafar, destacando-se pela estampa exclusiva em alta definição."
                act3["tag"] = "Múltiplas Formas de Uso"
                act3["title"] = "USE NA CABEÇA, NO PESCOÇO, NOS CABELOS OU COMO ACESSÓRIO"
                lenco_ctx = (
                    "para pescarias, passeios de barco, praia, lazer e dia a dia"
                    if store_key == "brk_fishing" else
                    "para pescarias, cavalgadas, praia, campo e dia a dia"
                )
                act3["desc_tmpl"] = f"Extremamente versátil {lenco_ctx}: pode ser usado amarrado na cabeça estilo bandana/camponesa, no pescoço estilo outdoor, como faixa de cabelo ou preso a bolsas e chapéus."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ permanente integrado ao tecido"},
                    {"label": "Modelagem / Formato", "value": "Lenço quadrado plano de amarração versátil"},
                    {"label": "Tecido", "value": "Microfibra tecnológica leve de toque macio e secagem rápida"},
                    {"label": "Estamparia", "value": "Sublimação digital HD de cores vivas resistente ao desbotamento"},
                    {"label": "Tamanho", "value": "Único amplo para múltiplas formas de dobra e amarração"}
                ]
            elif "black mask" in t_low or "blackmask" in t_low:
                act1["tag"] = "Design Anatômico Black Mask"
                act1["title"] = "RECORTE ERGONÔMICO NASAL E COBERTURA INTEGRAL DE ROSTO E PESCOÇO"
                act1["desc_tmpl"] = "Projetada com engenharia facial 3D para pescadores, pilotos e aventureiros, a {title} possui recorte superior anatômico que contorna o nariz e as maçãs do rosto com perfeição, além de aba inferior alongada que protege todo o pescoço."
                act2["tag"] = "Painel Frontal Respirável"
                act2["title"] = "TELA MICROPERFURADA PARA RESPIRAÇÃO LIVRE SEM EMBAÇAR OS ÓCULOS"
                act2["desc_tmpl"] = "Conta com painel central em tela Mesh microperfurada estrategicamente posicionado sobre o nariz e a boca, garantindo fluxo de ar contínuo, fala clara e evitando que seus óculos polarizados ou viseira embacem."
                act3["tag"] = "Conforto Térmico & Fixação"
                act3["title"] = "TECIDO GELADO UV50+ COM VIÉS SUPERIOR MACIO QUE NÃO ESCORREGA"
                act3["desc_tmpl"] = "Confeccionada em malha elástica de toque frio com proteção FPU 50+ permanente e acabamento superior em viés elástico macio que mantém a máscara firme no rosto mesmo em alta velocidade no barco ou na moto."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ permanente certificado"},
                    {"label": "Construção", "value": "Modelagem anatômica Black Mask com recorte nasal e viés elástico superior"},
                    {"label": "Respirabilidade", "value": "Painel frontal em tela Mesh microperfurada (anti-embaçamento de óculos)"},
                    {"label": "Tecido & Conforto", "value": "Malha elástica de toque frio, leve e de secagem ultra rápida"},
                    {"label": "Tamanho", "value": "Único anatômico de encaixe firme no rosto e pescoço"}
                ]
            elif ("balaclava" in t_low and "tubeneck" not in t_low) or prod_id_str == "9880439324967":
                act1["tag"] = "Cobertura Integral 360°"
                act1["title"] = "CAPUZ BALACLAVA COMPLETO PARA CABEÇA, ROSTO, ORELHAS E PESCOÇO"
                act1["desc_tmpl"] = "Desenvolvida para oferecer blindagem completa contra sol intenso, vento, poeira e insetos, a {title} envolve integralmente a cabeça, a nuca, as orelhas, o rosto e o pescoço com ajuste anatômico de segunda pele."
                act2["tag"] = "Visor Ocular Anatômico"
                act2["title"] = "ABERTURA FRONTAL COM VIÉS ELÁSTICO PERFEITA PARA USO SOB CAPACETE OU BONÉ"
                act2["desc_tmpl"] = "Possui abertura ocular contornada por viés macio de alta elasticidade e costuras planas que não marcam a pele, proporcionando visão ampla e encaixe perfeito por baixo de capacetes de motociclismo ou com chapéus e bonés de pesca."
                act3["tag"] = "Proteção UV50+ & Toque Frio"
                act3["title"] = "TECIDO TECNOLÓGICO RESPIRÁVEL DE SECAGEM ULTRA RÁPIDA"
                act3["desc_tmpl"] = "Confeccionada em malha tecnológica leve com elastano e fator FPU 50+ permanente, facilita a respiração, absorve o suor instantaneamente e mantém o conforto térmico em qualquer estação."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ permanente certificado"},
                    {"label": "Construção", "value": "Capuz Balaclava integral com abertura ocular anatômica e costura plana"},
                    {"label": "Tecido", "value": "Malha tecnológica Poliéster com Elastano de toque frio e secagem rápida"},
                    {"label": "Versatilidade", "value": "Ideal para uso sob capacetes (moto/trilha/kart) ou ao ar livre (pesca/campo)"},
                    {"label": "Tamanho", "value": "Único elástico adaptável a qualquer formato de cabeça"}
                ]
            elif "armorx" in t_low:
                act1["tag"] = "Linha Premium ArmorX UV50+"
                act1["title"] = "ESCUDO SOLAR E TÉRMICO DE ALTA PERFORMANCE PARA ROSTO E PESCOÇO"
                act1["desc_tmpl"] = "Integrante da linha de elite ArmorX da BRK, a {title} protege o rosto, a nuca e o pescoço contra a radiação solar intensa, vento forte, poeira e insetos durante pescarias e expedições extremas."
                act2["tag"] = "Borda Superior Antiderrapante"
                act2["title"] = "BAINHA ESTRUTURADA COM FITA ELÁSTICA INTERNA QUE NÃO ENROLA E NÃO CAI"
                act2["desc_tmpl"] = "Diferente das bandanas comuns, o modelo ArmorX conta com borda superior estruturada com fita elástica interna antiderrapante e acabamento reforçado, garantindo que a peça permaneça firme sobre o nariz mesmo em movimento intenso."
                act3["tag"] = "Toque Gelado & Respirabilidade"
                act3["title"] = "MALHA ELÁSTICA 4-WAY STRETCH DE SECAGEM RÁPIDA"
                act3["desc_tmpl"] = "Tecido tecnológico de toque frio que dissipa o calor rapidamente, facilita a respiração e seca em poucos minutos após contato com suor ou respingos d'água."
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ permanente certificado (Linha Premium ArmorX)"},
                    {"label": "Diferencial ArmorX", "value": "Borda superior estruturada com fita elástica interna antiderrapante que não enrola"},
                    {"label": "Construção", "value": "Tubular anatômica com bainhas reforçadas e elasticidade 4-Way Stretch"},
                    {"label": "Respirabilidade", "value": "Malha tecnológica de toque frio e secagem ultra rápida"},
                    {"label": "Tamanho", "value": "Único anatômico de alta estabilidade no rosto"}
                ]
            else:
                new_specs = [
                    {"label": "Proteção Solar", "value": "Fator FPU 50+ bloqueador permanente de radiação UVA e UVB"},
                    {"label": "Construção", "value": "Tubular multifuncional em microfibra elástica anti-atrito"},
                    {"label": "Elasticidade", "value": "Multidirecional 4-Way Stretch com memória de forma"},
                    {"label": "Respirabilidade", "value": "Tecido leve de toque frio que facilita a respiração e seca rápido"},
                    {"label": "Tamanho", "value": "Único anatômico adaptável a qualquer formato de rosto e cabeça"}
                ]

        # 13. Adaptação 360° para Camisas de Botão Xadrez Country/Farm e Camisas Work UV50+ (shirts_button_work)
        elif archetype_id == "shirts_button_work":
            if "xadrez" in t_low and is_short_sleeve:
                act1["tag"] = "Tradição Country & Frescor"
                act1["title"] = "PADRONAGEM XADREZ CLÁSSICA E MANGAS CURTAS VENTILADAS"
                act1["desc_tmpl"] = "Desenvolvida para unir a autêntica tradição do estilo Country e Farm ao frescor ideal para os dias quentes no campo, rodeios ou cidade, a {title} apresenta padronagem xadrez de fios tintos com caimento alinhado e confortável."
                act2["tag"] = "Colarinho & Abotoamento"
                act2["title"] = "COLARINHO ESTRUTURADO, BOTÕES PERSONALIZADOS E BOLSO FRONTAL"
                act2["desc_tmpl"] = "Conta com fechamento frontal por botões de alta resistência, colarinho estruturado que mantém o alinhamento impecável e bolso frontal funcional no peito com acabamento de alfaiataria country."
                act3["tag"] = "Mobilidade & Acabamento"
                act3["title"] = "PALA TRASEIRA ANATÔMICA E COSTURAS REFORÇADAS"
                act3["desc_tmpl"] = "Construída com mangas curtas de barra pespontada, pala traseira anatômica que favorece a movimentação dos ombros e tecido macio de alta durabilidade."
                new_specs = [
                    {"label": "Fechamento Frontal", "value": "Botões reforçados aplicados com costura em 'X'"},
                    {"label": "Colarinho / Gola", "value": "Colarinho tradicional estruturado com entretela de sustentação"},
                    {"label": "Mangas", "value": "Mangas curtas confortáveis com acabamento em pesponto duplo"},
                    {"label": "Bolso Frontal", "value": "Bolso funcional no peito com acabamento country"},
                    {"label": "Composição do Tecido", "value": "Algodão / Tricoline fio tinto respirável de alta durabilidade"},
                    {"label": "Modelagem", "value": "Country / Farm confortável com ampla mobilidade nos braços"}
                ]
            elif "xadrez" in t_low:
                if is_female:
                    act1["tag"] = "Elegância Country Feminina"
                    act1["title"] = "PADRONAGEM XADREZ CLÁSSICA E MODELAGEM FEMININA ACINTURADA"
                    act1["desc_tmpl"] = "Projetada especialmente para valorizar a silhueta feminina com a autenticidade do estilo Country e Farm, a {title} combina padronagem xadrez clássica em tecido macio a um caimento acinturado elegante para o campo, rodeios e dia a dia."
                else:
                    act1["tag"] = "Estilo Country & Durabilidade"
                    act1["title"] = "PADRONAGEM XADREZ CLÁSSICA E ESTRUTURA DE ALTA DURABILIDADE"
                    act1["desc_tmpl"] = "Desenvolvida para quem vive a cultura do campo, rodeios e rotina agropecuária com elegância, a {title} traz padronagem xadrez clássica em tecido encorpado e macio, garantindo presença marcante e resistência superior."
                act2["tag"] = "Abotoamento & Punhos"
                act2["title"] = "ABOTOAMENTO FRONTAL CLÁSSICO, COLARINHO FIRME E PUNHOS ABOTOADOS"
                act2["desc_tmpl"] = "Equipada com fechamento frontal integral por botões reforçados, colarinho estruturado de ótimo caimento e mangas longas com punhos abotoados ajustáveis."
                new_specs = [
                    {"label": "Fechamento Frontal", "value": "Botões reforçados aplicados com costura em 'X'"},
                    {"label": "Colarinho & Punhos", "value": "Colarinho tradicional estruturado e punhos com abotoamento ajustável"},
                    {"label": "Bolso Frontal", "value": "Bolso funcional no peito com acabamento country"},
                    {"label": "Composição do Tecido", "value": "Algodão / Tricoline fio tinto macio e resistente"},
                    {"label": "Modelagem", "value": "Country Feminina acinturada anatômica" if is_female else "Country / Farm confortável com folga estratégica nos braços"}
                ]
            else:
                if any(w in t_low for w in ["uv", "uv50", "solar", "fpu"]) and not any("proteção" in s["label"].lower() for s in new_specs):
                    new_specs.append({"label": "Proteção Solar", "value": "Fator UV50+ integrado ao tecido"})

        # 14. Adaptação 360° para Equipamentos de Camping, Náutica e Acessórios Específicos (accessories_general)
        elif archetype_id == "accessories_general":
            if "barraca" in t_low:
                act1["tag"] = "Abrigo & Impermeabilidade"
                act1["title"] = "PROTEÇÃO CONFIÁVEL CONTRA CHUVA, VENTO E INSETOS"
                act1["desc_tmpl"] = "Projetada para proporcionar noites seguras e confortáveis em acampamentos e expedições de pesca, a {title} combina montagem prática, ventilação eficiente e cobertura impermeável."
                act2["tag"] = "Estrutura & Ventilação"
                act2["title"] = "VARETAS FLEXÍVEIS DE FIBRA E TELA MOSQUITEIRO DE ALTA DENSIDADE"
                act2["desc_tmpl"] = "Varetas interligadas que garantem estabilidade estrutural contra rajadas de vento e janelas com tela mosquiteiro ultrafina que mantêm a circulação de ar bloqueando insetos."
                act3["tag"] = "Piso Reforçado & Portabilidade"
                act3["title"] = "PISO ANTI-UMIDADE E BOLSA COMPACTA DE TRANSPORTE"
                act3["desc_tmpl"] = "Fundo confeccionado em polietileno de alta resistência que isola a umidade do solo, acompanhando estacas metálicas, cordas de tensão e bolsa para transporte fácil."
                new_specs = [
                    {"label": "Sobreteto / Cobertura", "value": "Poliéster impermeabilizado com proteção contra chuva e sol"},
                    {"label": "Estrutura", "value": "Varetas em fibra de vidro flexível de alta resistência"},
                    {"label": "Piso", "value": "Polietileno de alta densidade anti-umidade (antifungo)"},
                    {"label": "Ventilação", "value": "Tela mosquiteiro de poliéster superfino"},
                    {"label": "Acessórios Inclusos", "value": "Estacas metálicas, cordas de fixação e bolsa de transporte"}
                ]
            elif any(w in t_low for w in ["mesa dobravel", "mesa dobrável", "mesa de camping"]):
                act1["tag"] = "Bancada Portátil (95x56x60 cm)"
                act1["title"] = "AMPLA MESA DOBRÁVEL PARA CAMPING, PESCA E CHURRASCO"
                act1["desc_tmpl"] = "Desenvolvida para oferecer uma superfície firme, espaçosa (95 x 56 cm) e na altura ideal (60 cm) para refeições e preparo de tralhas no acampamento ou na beira do rio, a {title} monta e desmonta em poucos segundos."
                act2["tag"] = "Tampo Articulado & Base em X"
                act2["title"] = "ESTRUTURA TUBULAR REFORÇADA E TAMPO DE FÁCIL HIGIENIZAÇÃO"
                act2["desc_tmpl"] = "Construída com cavalete tubular metálico em X com ponteiras antiderrapantes e tampo superior articulado com acabamento anticorrosivo, garantindo estabilidade mesmo em terrenos de grama, terra ou areia."
                act3["tag"] = "Transporte Compacto"
                act3["title"] = "DESMONTAGEM RÁPIDA COM BOLSA DE TRANSPORTE INCLUSA"
                act3["desc_tmpl"] = "Quando fechada, recolhe-se em um volume compacto e leve dentro da bolsa de transporte, ocupando mínimo espaço no porta-malas ou na embarcação."
                new_specs = [
                    {"label": "Dimensões Montada", "value": "95 cm (comprimento) x 56 cm (largura) x 60 cm (altura)"},
                    {"label": "Estrutura", "value": "Tubular metálica em X com pintura eletrostática preta anticorrosiva"},
                    {"label": "Tampo", "value": "Ripas articuladas resistentes à umidade e de fácil limpeza"},
                    {"label": "Portabilidade", "value": "Totalmente dobrável/desmontável com bolsa de transporte inclusa"}
                ]
            elif any(w in t_low for w in ["cadeira", "banqueta"]):
                act1["tag"] = "Conforto & Estabilidade (Até 100 kg)"
                act1["title"] = "CADEIRA DOBRÁVEL REFORÇADA PARA PESCA, CAMPING E LAZER"
                act1["desc_tmpl"] = "Desenvolvida para garantir máximo conforto e estabilidade na beira do rio, no acampamento ou na praia, a {title} suporta até 100 kg com 73 cm de altura e abre em segundos."
                act2["tag"] = "Porta-Copo & Tecido Camuflado"
                act2["title"] = "APOIO DE BRAÇOS COM PORTA-COPO EM TELA E TECIDO DE ALTA TENACIDADE"
                act2["desc_tmpl"] = "Equipada com apoios de braço ergonômicos, porta-copo integrado em malha no braço direito e assento/encosto em tecido Oxford camuflado resistente ao peso e à umidade."
                act3["tag"] = "Transporte Descomplicado"
                act3["title"] = "FECHAMENTO COMPACTO E SAPATAS ESTABILIZADORAS"
                act3["desc_tmpl"] = "Conta com sapatas articuladas para terrenos de terra ou grama e acompanha bolsa com alça para transporte prático no ombro ou no porta-malas."
                new_specs = [
                    {"label": "Capacidade & Altura", "value": "Suporta até 100 kg | Altura total: 73 cm"},
                    {"label": "Estrutura", "value": "Tubos de aço com pintura anticorrosiva e sapatas estabilizadoras"},
                    {"label": "Assento & Encosto", "value": "Tecido Oxford camuflado de alta tenacidade com porta-copo integrado"},
                    {"label": "Origem / Distribuição", "value": "Produto Original Marine Sports com garantia oficial"}
                ]
            elif "fogareiro" in t_low:
                act1["tag"] = "Chama Potente & Portabilidade"
                act1["title"] = "COZIMENTO RÁPIDO E SEGURO EM QUALQUER ACAMPAMENTO OU PESCARIA"
                act1["desc_tmpl"] = "Projetado para preparar refeições e café fresco na beira do rio ou no camping com total praticidade, o {title} oferece chama estável, controle preciso de fogo e transporte compacto."
                act2["tag"] = "Ignição & Segurança"
                act2["title"] = "ACENDIMENTO PRÁTICO E CONTROLE GRADUAL DE CHAMA"
                act2["desc_tmpl"] = "Sistema de ignição ágil que dispensa fósforos, válvula com trava de segurança para o cartucho de gás e queimador eficiente que otimiza o consumo."
                act3["tag"] = "Estrutura & Limpeza"
                act3["title"] = "APOIO FIRME PARA PANELAS E ALTA DURABILIDADE"
                act3["desc_tmpl"] = "Suporte estável para panelas e chaleiras com proteção lateral contra vento, construído em liga metálica resistente ao calor intenso."
                new_specs = [
                    {"label": "Tipo", "value": "Fogareiro portátil para camping e pesca"},
                    {"label": "Ignição", "value": "Acendimento automático piezoelétrico com ajuste de chama"},
                    {"label": "Segurança", "value": "Trava de engate seguro com dispositivo de corte de pressão"},
                    {"label": "Uso Recomendado", "value": "Camping, pescarias, expedições e viagens"}
                ]
            elif any(w in t_low for w in ["capa de caiaque", "saco estanque", "bolsa estanque"]):
                act1["tag"] = "Proteção Impermeável & UV"
                act1["title"] = "BLINDAGEM COMPLETA CONTRA SOL, CHUVA, POEIRA E UMIDADE"
                act1["desc_tmpl"] = "Desenvolvida para proteger seu caiaque durante o armazenamento na garagem, quintal ou marina, a {title} preserva o casco e os acessórios contra raios solares, chuva, poeira e folhas."
                act2["tag"] = "Ajuste Elástico Perimetral"
                act2["title"] = "MATERIAL IMPERMEÁVEL DE ALTA TENACIDADE COM BORDA ELÁSTICA"
                act2["desc_tmpl"] = "Confeccionada em material impermeável de alta gramatura com elástico embutido em toda a borda, abraçando o formato do caiaque com firmeza e rapidez."
                act3["tag"] = "Vida Útil Prolongada"
                act3["title"] = "PREVENÇÃO CONTRA DESBOTAMENTO E RESSECAMENTO DO CASCO"
                act3["desc_tmpl"] = "Fácil de vestir, dobrar e higienizar, evitando o ressecamento do polietileno e mantendo seu caiaque sempre limpo e pronto para a próxima pescaria."
                new_specs = [
                    {"label": "Categoria", "value": "Capa Protetora Impermeável para Caiaque BRK"},
                    {"label": "Material", "value": "Tecido técnico impermeável de alta gramatura com proteção UV"},
                    {"label": "Sistema de Ajuste", "value": "Borda perimetral com elástico reforçado de ajuste rápido ao casco"},
                    {"label": "Proteção", "value": "Barreira completa contra sol, chuva, poeira, folhas e maresia"},
                    {"label": "Aplicação", "value": "Armazenamento e conservação de caiaques de pesca e lazer"}
                ]
            elif any(w in t_low for w in ["cabo plug", "cabo de força", "cabo de alimentacao", "cabo de alimentação"]):
                act1["tag"] = "Alimentação Veicular 12V/24V"
                act1["title"] = "CABO DE ALIMENTAÇÃO VEICULAR 12V/24V ORIGINAL ELBER"
                act1["desc_tmpl"] = "Peça de reposição original desenvolvida para garantir alimentação contínua e segura da sua geladeira portátil Elber no veículo ou na embarcação, o {title} assegura encaixe preciso e máxima condutividade."
                act2["tag"] = "Plugue com Fusível Integrado"
                act2["title"] = "CONECTOR PADRÃO AUTOMOTIVO/NÁUTICO COM PROTEÇÃO ELÉTRICA"
                act2["desc_tmpl"] = "Equipado com plugue 12V/24V de contato firme que não solta com a trepidação da estrada ou das ondas, contando com fusível interno de proteção contra surtos de corrente."
                act3["tag"] = "Qualidade Original Elber"
                act3["title"] = "BITOLA DIMENSIONADA E ISOLAMENTO RESISTENTE SEM SUPERAQUECIMENTO"
                act3["desc_tmpl"] = "Construído com cabos de cobre de bitola homologada pela engenharia Elber e revestimento flexível resistente a dobras e calor."
                new_specs = [
                    {"label": "Compatibilidade", "value": "Geladeiras portáteis Elber 12V/24V (Linha TB / CAB)"},
                    {"label": "Tensão de Operação", "value": "12V / 24V DC (Tomada veicular ou embarcação)"},
                    {"label": "Segurança", "value": "Plugue com fusível interno de proteção contra surtos e curto-circuito"},
                    {"label": "Procedência", "value": "Peça de reposição 100% Original Elber"}
                ]
            elif "fonte conversora" in t_low:
                act1["tag"] = "Conversão 110V/220V para 12V/24V"
                act1["title"] = "LIGUE SUA GELADEIRA PORTÁTIL ELBER NA TOMADA RESIDENCIAL"
                act1["desc_tmpl"] = "Acessório original desenvolvido para converter a energia da tomada comum (110V/220V) para 12V/24V contínuos, a {title} permite pré-resfriar ou utilizar sua geladeira portátil Elber em casa, no rancho, no hotel ou na marina."
                act2["tag"] = "Bivolt Automático Estabilizado"
                act2["title"] = "EFICIÊNCIA ENERGÉTICA COM PROTEÇÃO CONTRA OSCILAÇÕES"
                act2["desc_tmpl"] = "Opera em faixa Bivolt automática (110V/220V AC) entregando tensão contínua estabilizada para o compressor da geladeira, sem risco de sobrecarga."
                act3["tag"] = "Qualidade Original Elber"
                act3["title"] = "GABINETE ISOLADO E CONECTOR PADRÃO DE ENCAIXE DIRETO"
                act3["desc_tmpl"] = "Construída com componentes homologados, saída fêmea padrão 12V para acoplamento direto do cabo da geladeira e proteção térmica integrada."
                new_specs = [
                    {"label": "Compatibilidade", "value": "Geladeiras portáteis Elber 12V/24V"},
                    {"label": "Tensão", "value": "Entrada Bivolt automática 110V/220V AC -> Saída 12V/24V DC"},
                    {"label": "Segurança", "value": "Proteção contra sobrecarga, curto-circuito e superaquecimento"},
                    {"label": "Procedência", "value": "Acessório 100% Original Elber"}
                ]
            elif "suporte magnético" in t_low or "suporte magnetico" in t_low:
                act1["tag"] = "Acesso Rápido com Uma Mão"
                act1["title"] = "SUPORTE MAGNÉTICO DE ALTA FORÇA COM ENGATE E SAQUE INSTANTÂNEO"
                act1["desc_tmpl"] = "Projetado para prender passaguás, alicates, cortadores de linha e ferramentas diretamente no colete, mochila ou cinto, o {title} permite liberar o equipamento com um simples puxão e reconectá-lo automaticamente pela força do ímã."
                act2["tag"] = "Mosquetão & Fiel Espiral"
                act2["title"] = "MOSQUETÃO DE ALUMÍNIO E CORDÃO ESPIRAL ELÁSTICO ANTI-PERDA"
                act2["desc_tmpl"] = "Equipado com mosquetão de engate rápido e cabo espiral retrátil de segurança que acompanha o movimento das mãos, impedindo que seu alicate ou passaguá caia na água durante a pescaria."
                act3["tag"] = "Resistência à Corrosão"
                act3["title"] = "ESTRUTURA METÁLICA ANODIZADA PARA ÁGUA DOCE E SALGADA"
                act3["desc_tmpl"] = "Construído com cápsula magnética blindada, argolas em aço inox e acabamento anodizado resistente à umidade, garantindo fixação confiável em pescarias de vadeio, caiaque ou barco."
                new_specs = [
                    {"label": "Categoria", "value": "Suporte Magnético Salva-Tralha com Mosquetão Deyu"},
                    {"label": "Sistema de Engate", "value": "Ímã de neodímio de alta tração para conexão e liberação rápida"},
                    {"label": "Componentes", "value": "Cápsula magnética dupla + Mosquetão de engate + Cabo espiral elástico (fiel)"},
                    {"label": "Aplicação", "value": "Fixação de passaguás, alicates de contenção, tesouras e ferramentas no colete ou cinto"},
                    {"label": "Origem / Distribuição", "value": "Produto Original Deyu com garantia oficial"}
                ]
            elif "fita para proteção" in t_low or "fita para protecao" in t_low:
                act1["tag"] = "Proteção nos Arremessos"
                act1["title"] = "FITA PROTETORA DE DEDOS CONTRA CORTES DE LINHA E ATRITO"
                act1["desc_tmpl"] = "Desenvolvida para proteger os dedos do pescador contra cortes provocados por linhas multifilamento e pelo atrito repetitivo em centenas de arremessos e recolhimentos, a {title} garante conforto e firmeza na pegada."
                act2["tag"] = "Tecnologia Autoaderente"
                act2["title"] = "ADERÊNCIA COESIVA SEM COLA QUE NÃO DEIXA RESÍDUOS NA PELE"
                act2["desc_tmpl"] = "Sua tecnologia autoaderente (coesiva) faz com que a fita grude apenas sobre si mesma, moldando-se perfeitamente às articulações dos dedos ou ao cabo da vara sem colar na pele ou nos pelos."
                act3["tag"] = "Respirável & Camuflada"
                act3["title"] = "LARGURA DE 2,5 CM FLEXÍVEL, RESPIRÁVEL E RESISTENTE À ÁGUA"
                act3["desc_tmpl"] = "Com 2,5 cm de largura e acabamento Camo Preto, mantém a sensibilidade tátil no controle do carretel e resiste a respingos d'água e suor durante toda a jornada de pesca."
                new_specs = [
                    {"label": "Categoria", "value": "Fita Coesiva Protetora de Dedos para Pesca Albatroz Fishing"},
                    {"label": "Largura", "value": "2,5 cm (ideal para falanges dos dedos e empunhaduras)"},
                    {"label": "Tecnologia de Fixação", "value": "Autoaderente (gruda sobre si mesma sem deixar resíduo de cola na pele)"},
                    {"label": "Função Principal", "value": "Prevenção de cortes por linha multifilamento, calos e bolhas nos arremessos"},
                    {"label": "Origem / Distribuição", "value": "Produto Original Albatroz Fishing com garantia oficial"}
                ]
            elif "coleira" in t_low or "peitoral" in t_low:
                act1["tag"] = "Conforto & Segurança Pet"
                act1["title"] = "PEITORAL ANATÔMICO RESPIRÁVEL COM GUIA PARA CÃES E GATOS"
                act1["desc_tmpl"] = "Projetado para distribuir a pressão de forma suave pelo tórax sem forçar o pescoço do animal, o {title} proporciona passeios seguros, confortáveis e cheios de liberdade para o seu pet."
                act2["tag"] = "Visibilidade Noturna & Trava"
                act2["title"] = "FAIXAS REFLETIVAS DE ALTA VISIBILIDADE E FIVELA DE ENGATE RÁPIDO"
                act2["desc_tmpl"] = "Conta com detalhes refletivos que aumentam a visualização em caminhadas noturnas ou ao entardecer, além de fecho traseiro de engate rápido e argola metálica dupla para conexão da guia."
                act3["tag"] = "Malha Aerada & Ajuste"
                act3["title"] = "TECIDO MESH VENTILADO QUE NÃO AQUECE E REGULAGEM ANATÔMICA"
                act3["desc_tmpl"] = "Confeccionado em malha aerada macia (Air Mesh) que permite ventilação contínua na pelagem e tiras reguláveis para um ajuste sob medida ao corpo do seu cão ou gato."
                new_specs = [
                    {"label": "Categoria", "value": "Conjunto Peitoral Anatômico com Guia para Pets (Cães e Gatos)"},
                    {"label": "Material", "value": "Malha respirável Air Mesh acolchoada com fitas de nylon de alta resistência"},
                    {"label": "Segurança", "value": "Faixas refletivas 360° + Fivela de engate rápido + Meia-argola metálica para guia"},
                    {"label": "Itens Inclusos", "value": "1 Coleira Peitoral Anatômica + 1 Guia de Passeio"}
                ]
            elif "personalização" in t_low or "personalizacao" in t_low:
                act1["tag"] = "Exclusividade Oficial BRK"
                act1["title"] = "PERSONALIZE SUA CAMISA BRK COM SEU NOME OU EQUIPE"
                act1["desc_tmpl"] = "Torne seu uniforme de pesca, campo ou aventura único: o serviço de {title} aplica seu nome ou apelido diretamente na sua camisa BRK com padrão gráfico profissional de fábrica."
                act2["tag"] = "Alta Definição & Durabilidade"
                act2["title"] = "APLICAÇÃO DE ALTA FIXAÇÃO QUE NÃO DESBOTA E NÃO DESCASCA"
                act2["desc_tmpl"] = "Executada pela equipe de produção oficial da BRK com tecnologia de termotransferência/sublimação de alta aderência, preservando a elasticidade, a leveza e a respirabilidade do tecido."
                act3["tag"] = "Identidade Profissional"
                act3["title"] = "TIPOGRAFIA ESPORTIVA ALINHADA AO DESIGN DA SUA CAMISA"
                act3["desc_tmpl"] = "Posicionamento e dimensionamento harmonizados com a arte do modelo escolhido, ideal para pescadores esportivos, torneios, comitivas, equipes e presentes personalizados."
                new_specs = [
                    {"label": "Categoria", "value": "Serviço Oficial de Personalização de Nome BRK"},
                    {"label": "Método de Aplicação", "value": "Termotransferência / Sublimação profissional de alta fixação"},
                    {"label": "Durabilidade", "value": "Não racha, não desbota e acompanha a elasticidade do tecido"},
                    {"label": "Compatibilidade", "value": "Camisas e vestuário oficial BRK adquiridos no mesmo pedido"}
                ]
            elif "chaveiro" in t_low:
                new_specs = [
                    {"label": "Categoria", "value": "Chaveiro Colecionável Oficial BRK"},
                    {"label": "Material", "value": "Emborrachado em relevo de alta densidade com argola e corrente metálica"},
                    {"label": "Aplicação", "value": "Chaves de veículos, caminhonetes, tratores, barcos, mochilas e bolsas"},
                    {"label": "Durabilidade", "value": "Resistente à água, atrito e exposição solar"}
                ]
            elif "adesivo" in t_low or "sticker" in t_low:
                new_specs = [
                    {"label": "Categoria", "value": "Cartela de Adesivos Colecionáveis Oficiais BRK"},
                    {"label": "Material", "value": "Vinil adesivo automotivo de alta aderência com recorte preciso"},
                    {"label": "Aplicação", "value": "Caixas de pesca, barcos, caiaques, caminhonetes, coolers e copos térmicos"},
                    {"label": "Durabilidade", "value": "Resistente à água e exposição solar"}
                ]

        # 14.5 Adaptação 360° para Livros de Colorir BRK Agro vs BRK Fishing (books_publications)
        elif archetype_id == "books_publications":
            if store_key == "brk_agro" or "agro" in t_low:
                act1["tag"] = "Universo do Campo & Diversão"
                act1["title"] = "IMERSÃO LÚDICA NA VIDA DA FAZENDA, ANIMAIS E NATUREZA"
                act1["desc_tmpl"] = "O {title} traz ilustrações exclusivas e envolventes sobre o universo do campo, cavalos, pecuária, tratores e vida na fazenda, estimulando a criatividade e conectando crianças e famílias às raízes do agronegócio."
                act2["tag"] = "Qualidade Editorial BRK"
                act2["title"] = "TRAÇOS EM ALTA DEFINIÇÃO E PAPEL DE ALTA GRAMATURA"
                act2["desc_tmpl"] = "Produzido com acabamento gráfico de alta qualidade, desenhos ricos em detalhes e páginas resistentes ideais para lápis de cor e giz de cera."
                act3["tag"] = "Presente & Aprendizado"
                act3["title"] = "EXCELENTE OPÇÃO PARA PRESENTEAR OS PEQUENOS APAIXONADOS PELO AGRO"
                act3["desc_tmpl"] = "Uma atividade educativa e criativa longe das telas, perfeita para incentivar a coordenação motora e o amor pela vida no campo desde a infância."
                new_specs = [
                    {"label": "Formato", "value": "Livro de colorir impresso com encadernação de alta qualidade"},
                    {"label": "Acabamento", "value": "Capa colorida laminada e páginas em papel especial de alta gramatura"},
                    {"label": "Tema Principal", "value": "Vida no campo, fazenda, cavalos, animais rurais e máquinas agrícolas"},
                    {"label": "Idioma", "value": "Português"},
                    {"label": "Público Indicado", "value": "Crianças, jovens e famílias apaixonadas pelo universo Agro"}
                ]
            else:
                act1["tag"] = "Aventura na Pesca & Criatividade"
                act1["title"] = "ILUSTRAÇÕES EXCLUSIVAS DO UNIVERSO DA PESCA ESPORTIVA E NATUREZA"
                act1["desc_tmpl"] = "O {title} reúne desenhos exclusivos de peixes esportivos brasileiros, barcos, pescarias em família e cenários aquáticos, despertando a imaginação e o contato das crianças com a pesca esportiva."
                act2["tag"] = "Qualidade Editorial BRK"
                act2["title"] = "TRAÇOS NÍTIDOS EM ALTA DEFINIÇÃO E PAPEL ENCORPADO"
                act2["desc_tmpl"] = "Impresso em papel de alta gramatura com contornos bem definidos, oferecendo excelente superfície para colorir com lápis de cor e giz de cera sem transferir facilmente para o verso."
                act3["tag"] = "Presente & Momentos em Família"
                act3["title"] = "DIVERSÃO EDUCATIVA LONGE DAS TELAS PARA PEQUENOS PESCADORES"
                act3["desc_tmpl"] = "Ideal para estimular a coordenação motora fina, a concentração e a paixão pela natureza e pela preservação dos rios desde cedo."
                new_specs = [
                    {"label": "Formato", "value": "Livro de colorir impresso com encadernação reforçada"},
                    {"label": "Acabamento", "value": "Capa colorida laminada e miolo em papel especial de alta gramatura"},
                    {"label": "Tema Principal", "value": "Pesca esportiva, espécies de peixes, natureza e aventuras nos rios"},
                    {"label": "Idioma", "value": "Português"},
                    {"label": "Público Indicado", "value": "Crianças, jovens e famílias apaixonadas pela pesca esportiva"}
                ]

        # 14.6 Adaptação 360° para Calças Jeans Country Masculinas BRK Agro (pants_cargo_tactical)
        elif archetype_id == "pants_cargo_tactical":
            if any(w in t_low for w in ["jeans", "denim", "country", "western", "rancher", "dusty", "badlands", "stout", "hardland", "tennesse"]):
                act1["tag"] = "Denim Encorpado & Corte Country"
                act1["title"] = "JEANS DE ALTA GRAMATURA COM CAIMENTO TRADICIONAL WESTERN"
                act1["desc_tmpl"] = "Desenvolvida para unir a resistência exigida na rotina do campo à elegância do estilo sertanejo, a {title} é confeccionada em tecido Denim encorpado de alta durabilidade, com corte tradicional country que acomoda perfeitamente o cano de botas e botinas."
                act2["tag"] = "Conforto na Lida & Cós Estruturado"
                act2["title"] = "LIBERDADE DE MOVIMENTOS NO CAMPO E PASSADORES REFORÇADOS PARA CINTO"
                act2["desc_tmpl"] = "Projetada para acompanhar longas jornadas na fazenda, cavalgadas, rodeios e uso diário, conta com cós anatômico firme e passadores reforçados dimensionados para cintos country e fivelas tradicionais."
                act3["tag"] = "Acabamento & Costuras Duplas"
                act3["title"] = "5 BOLSOS FUNCIONAIS COM REBITES METÁLICOS E PESPONTOS DE ALTA TENACIDADE"
                act3["desc_tmpl"] = "Construída com 5 bolsos clássicos profundos (frontais com bolso relógio e traseiros estruturados com pesponto western), travetes e rebites metálicos nos pontos de maior tensão que garantem longa vida útil mesmo sob uso intenso."
                new_specs = [
                    {"label": "Tecido Principal", "value": "Denim (Jeans) encorpado de alta gramatura e resistência ao atrito"},
                    {"label": "Modelagem / Corte", "value": "Tradicional Country / Western Masculina (caimento ideal sobre botas e botinas)"},
                    {"label": "Cós & Fechamento", "value": "Botão metálico personalizado, zíper reforçado e passadores largos para cinto"},
                    {"label": "Bolsos & Reforços", "value": "5 bolsos tradicionais com rebites metálicos e costuras duplas de alta tenacidade"},
                    {"label": "Uso Recomendado", "value": "Lida no campo, agronegócio, cavalgadas, rodeios, eventos sertanejos e dia a dia"}
                ]
                template["care_tips"] = "Lavar do avesso com sabão neutro para preservar a tonalidade original do jeans. Secar à sombra e não utilizar alvejantes."

        # 14.7 Adaptação 360° para Macacão Jardineira de Pesca com Bota Impermeável Wader (overalls_workwear)
        elif archetype_id == "overalls_workwear":
            if any(w in t_low for w in ["pesca", "impermeavel", "impermeável", "bota", "silicone", "wader"]):
                act1["tag"] = "Impermeabilidade Total (Wader)"
                act1["title"] = "JARDINEIRA DE PESCA 100% IMPERMEÁVEL COM BOTAS ACOPLADAS"
                act1["desc_tmpl"] = "Projetado para pescarias dentro d'água, manejo em açudes e ambientes alagados, o {title} forma uma barreira estanque integral que mantém o corpo e os pés completamente secos da cintura até a sola."
                act2["tag"] = "Botas Integradas & Tração"
                act2["title"] = "BOTAS DE PVC/SILICONE TERMOSSOLDADAS COM SOLADO TRATORADO ANTIDERRAPANTE"
                act2["desc_tmpl"] = "Conta com botas impermeáveis fundidas diretamente à jardineira por termossoldagem de alta frequência (sem frestas ou costuras aparentes) e solado tratorado robusto para tração firme em lama, pedras e margens escorregadias."
                act3["tag"] = "Suspensórios & Mobilidade"
                act3["title"] = "ALÇAS ELÁSTICAS REGULÁVEIS COM FIVELAS DE ENGATE RÁPIDO"
                act3["desc_tmpl"] = "Equipado com suspensórios de alta elasticidade, fivelas plásticas de trava rápida e ajuste de cintura que permitem vestir ou retirar a jardineira com facilidade sobre a roupa."
                new_specs = [
                    {"label": "Construção & Vedação", "value": "Composto impermeável de PVC/Nylon flexível com emendas termossoldadas estanques"},
                    {"label": "Botas Acopladas", "value": "Botas de PVC/Silicone impermeáveis integradas diretamente à estrutura da jardineira"},
                    {"label": "Solado", "value": "Tratorado antiderrapante de alta aderência para terrenos lamacentos e aquáticos"},
                    {"label": "Sistema de Ajuste", "value": "Alças elásticas reguláveis com fivelas de engate rápido e ajuste na cintura"},
                    {"label": "Indicação de Uso", "value": "Pesca embarcada ou vadeio, piscicultura, limpeza de tanques, lavoura irrigada e áreas alagadas"}
                ]
                template["care_tips"] = "Enxaguar com água doce limpa após o uso para remover lama ou sal. Secar completamente à sombra em local ventilado antes de guardar, mantendo as botas desdobradas."

        # 14.8 Adaptação 360° para Chapéu BRK Agro Juta Palha de Bambu Premium (hats_safari_outdoor)
        elif archetype_id == "hats_safari_outdoor":
            if any(w in t_low for w in ["juta", "bambu", "palha"]):
                act1["tag"] = "Trama Natural em Juta & Bambu"
                act1["title"] = "VENTILAÇÃO NATURAL SUPERIOR E ESTILO AUTÊNTICO NO CAMPO"
                act1["desc_tmpl"] = "Confeccionado com fibras selecionadas de juta e palha de bambu, o {title} combina leveza extrema, circulação constante de ar pela trama trançada e sombra generosa para dias ensolarados na fazenda, eventos agro ou lazer."
                act2["tag"] = "Acabamento Exclusivo BRK Agro"
                act2["title"] = "COPA E ABA ESTRUTURADAS COM BANDINHA PERSONALIZADA E FIVELA METÁLICA"
                act2["desc_tmpl"] = "Possui copa moldada de caimento impecável, aba estruturada com viés protetor nas bordas e bandinha personalizada BRK Agro com fivela metálica lateral."
                act3["tag"] = "Conforto Anatômico"
                act3["title"] = "CARNEIRA INTERNA MACIA PARA USO PROLONGADO SEM APERTAR"
                act3["desc_tmpl"] = "Equipado com faixa interna confortável que proporciona encaixe firme, macio e estável na cabeça durante todo o dia."
                new_specs = [
                    {"label": "Material Principal", "value": "Trama selecionada em fibra de Juta e Palha de Bambu respirável"},
                    {"label": "Copa & Aba", "value": "Copa estruturada ventilada e aba ampla com acabamento em viés"},
                    {"label": "Acabamento Externo", "value": "Bandinha exclusiva BRK Agro em tom caramelo com fivela metálica"},
                    {"label": "Carneira Interna", "value": "Faixa anatômica macia de toque suave na testa"},
                    {"label": "Embalagem de Envio", "value": "Caixa protetora reforçada BRK (anti-deformação)"}
                ]
                template["care_tips"] = "Limpar delicadamente com pano seco ou escova de cerdas macias. Não lavar em água, não submergir e armazenar em local seco e arejado apoiado pela copa."

        # 14.9 Adaptação 360° para Chapéus Country American Hat — Palha Ventilada vs Feltro (hats_country_cowboy)
        elif archetype_id == "hats_country_cowboy":
            if any(w in t_low for w in ["bozeman", " cal", "palha"]):
                act1["tag"] = "Tradição Western & Ventilação"
                act1["title"] = "TRAMA NOBRE ESTRUTURADA COM COPA VENTILADA E ABA IMPONENTE"
                act1["desc_tmpl"] = "O {title} une a imponência clássica dos chapéus American Hat à leveza de uma copa com trama ventilada, garantindo presença marcante e excelente conforto térmico sob o sol."
                act2["tag"] = "Acabamento Autêntico"
                act2["title"] = "BANDINHA FINA COM FIVELA METÁLICA E MODELAGEM CATTLEMAN"
                act2["desc_tmpl"] = "Modelagem tradicional com vincos precisos na copa, aba larga curvada de alta sustentação e bandinha externa clássica com fivela e passador metálicos."
                act3["tag"] = "Ajuste & Conforto"
                act3["title"] = "CARNEIRA INTERNA MACIA COM ENCAIXE FIRME E CONFORTÁVEL"
                act3["desc_tmpl"] = "Interior equipado com carneira anatômica que oferece ajuste seguro e toque suave na testa durante cavalgadas, rodeios, feiras agropecuárias e lida no campo."
                new_specs = [
                    {"label": "Material Principal", "value": "Palha / Fibra Nobre trançada de alta firmeza com copa ventilada"},
                    {"label": "Formato da Copa", "value": "Tradicional Western / Cattleman com microperfurações de ventilação"},
                    {"label": "Carneira Interna", "value": "Faixa anatômica macia de alto conforto e estabilidade"},
                    {"label": "Acabamento Externo", "value": "Bandinha clássica com fivela, passador e ponteira metálica"},
                    {"label": "Embalagem de Envio", "value": "Caixa rígida protetora especial (anti-deformação)"}
                ]

        # 14.10 Adaptação 360° para Boné 6 Gomos Fechado vs Trucker (caps_trucker_snapback)
        elif archetype_id == "caps_trucker_snapback":
            if "6 gomos" in t_low or "seis gomos" in t_low:
                act1["tag"] = "Copa Fechada 6 Gomos"
                act1["title"] = "ESTRUTURA INTEGRAL EM TECIDO CAMUFLADO COM ILHOSES DE VENTILAÇÃO"
                act1["desc_tmpl"] = "O {title} apresenta construção clássica de 6 gomos fechados em tecido encorpado com ilhoses bordados para respiro, entregando visual tático autêntico e proteção integral contra o sol na pescaria ou no campo."
                new_specs = [
                    {"label": "Modelagem da Copa", "value": "6 Gomos fechada estruturada com ilhoses bordados de ventilação"},
                    {"label": "Aba Frontal", "value": "Curva estruturada com 6 costuras de reforço"},
                    {"label": "Sistema de Ajuste", "value": "Regulagem traseira anatômica (Tamanho Único Ajustável)"},
                    {"label": "Acabamento Frontal", "value": "Bordado / Patch exclusivo BRK de alta definição"},
                    {"label": "Carneira Interna", "value": "Faixa absorvente de suor de toque macio"}
                ]

        # 15. Adaptação 360° para Cutelaria, Facas, Kits Faca & Chaira, Cutelo e Canivetes (cutlery_unique)
        elif archetype_id == "cutlery_unique":
            prod_id_str = str(product.get("id") or "")
            # 15.1 Kit Churrasco Deyu com 3 Peças (Faca + Garfo + Pegador em Inox + Estojo Organizador)
            if "kit churrasco" in t_low and ("3 pe" in t_low or "deyu" in t_low):
                act1["tag"] = "Conjunto Completo 3 em 1"
                act1["title"] = "FACA, GARFO TRINCHANTE E PEGADOR EM AÇO INOXIDÁVEL"
                act1["desc_tmpl"] = "Praticidade completa para o seu churrasco no camping, na pescaria ou em casa: o {title} reúne 1 faca de corte afiada, 1 garfo trinchante estruturado e 1 pegador multiuso construídos integralmente em aço inoxidável."
                act2["tag"] = "Maleta Organizadora Portátil"
                act2["title"] = "ESTOJO ORGANIZADOR COM FECHAMENTO PERIMETRAL, ALÇA E ELÁSTICOS INTERNOS"
                act2["desc_tmpl"] = "Acompanha estojo organizador compacto com fechamento perimetral completo, alças externas de transporte e fitas elásticas internas que mantêm cada utensílio fixo, protegido e organizado."
                act3["tag"] = "Higiene & Durabilidade"
                act3["title"] = "CABOS MONOBLOCO EM INOX RESISTENTES À CORROSÃO E FÁCIL LIMPEZA"
                act3["desc_tmpl"] = "Utensílios com cabos tubulares em aço inoxidável e alças de suspensão nas extremidades, oferecendo alta resistência à umidade, zero absorção de odores e higienização rápida."
                new_specs = [
                    {"label": "Itens Inclusos", "value": "1 Faca de Churrasco, 1 Garfo Trinchante, 1 Pegador em Inox e 1 Estojo Organizador"},
                    {"label": "Material dos Utensílios", "value": "Aço Inoxidável integral (lâminas e cabos) com alças de suspensão"},
                    {"label": "Armazenamento", "value": "Estojo organizador em nylon estruturado com elásticos internos e alça de mão"},
                    {"label": "Indicação de Uso", "value": "Churrascos, camping, pescarias, viagens e área gourmet"}
                ]
                template["care_tips"] = "Lavar manualmente com água e lado macio da esponja com sabão neutro logo após o uso. Secar imediatamente com pano limpo e macio antes de guardar no estojo organizador."
            # 15.2 Canivetes Táticos Dobráveis Deyu (Cabo Madeira 018355 vs Metálico ZD W84)
            elif "canivete" in t_low:
                template["care_tips"] = "Limpar a lâmina com pano úmido e sabão neutro após o uso e secar completamente antes de recolher o fio no cabo."
                if "madeira" in t_low or "018355" in t_low:
                    act1["tag"] = "Lâmina Dobrável Tática"
                    act1["title"] = "AÇO INOXIDÁVEL COM ACABAMENTO ESCURECIDO E CORTE PRECISO"
                    act1["desc_tmpl"] = "Compacto, versátil e sempre pronto para ação no campo ou na pescaria, o {title} possui lâmina principal em aço inoxidável com acabamento escurecido antirreflexo e sulco de abertura rápida."
                    act2["tag"] = "Empunhadura em Madeira"
                    act2["title"] = "TALAS ANATÔMICAS EM MADEIRA COM FIXAÇÃO METÁLICA E FURO PARA FIEL"
                    act2["desc_tmpl"] = "Cabo ergonômico revestido em madeira selecionada, fixado por parafusos Torx de alta resistência e equipado com olhal traseiro para passagem de cordão fiel."
                    act3["tag"] = "Lâmina Auxiliar & Segurança"
                    act3["title"] = "CORTADOR DE LINHA E CINTO INTEGRADO COM PONTA DE PROTEÇÃO"
                    act3["desc_tmpl"] = "Conta com lâmina secundária dobrável em formato de gancho cortador com ponta arredondada de segurança, ideal para cortar linhas, cordas e cintos com rapidez."
                    new_specs = [
                        {"label": "Tipo", "value": "Canivete Tático Dobrável de Bolso com Dupla Função"},
                        {"label": "Material da Lâmina", "value": "Aço Inoxidável com revestimento escurecido protetor"},
                        {"label": "Empunhadura", "value": "Talas anatômicas em madeira com parafusos reforçados e olhal para fiel"},
                        {"label": "Recurso Adicional", "value": "Lâmina auxiliar cortadora de linha/corda com ponta de segurança"},
                        {"label": "Aplicação", "value": "Pesca esportiva, camping, trilhas e uso diário (EDC)" if store_key == "brk_fishing" else "Pesca esportiva, camping, lida no campo e uso diário (EDC)"}
                    ]
                else:
                    act1["tag"] = "Lâmina Tática em Aço Inox"
                    act1["title"] = "CORTE ÁGIL COM ACABAMENTO ESCURECIDO E DORSO SERRILHADO"
                    act1["desc_tmpl"] = "Projetado para máxima praticidade no bolso ou na caixa de pesca, o {title} combina lâmina em aço inoxidável com revestimento preto antirreflexo e apoio serrilhado para o polegar."
                    act2["tag"] = "Empunhadura Metálica"
                    act2["title"] = "CABO EM METAL TEXTURIZADO EM ALTO-RELEVO DE ALTA ADERÊNCIA"
                    act2["desc_tmpl"] = "Estrutura integral metálica com textura artística em relevo que garante pegada firme, resistência a impactos e olhal integrado na extremidade para fiel ou mosquetão."
                    act3["tag"] = "Portabilidade & Fechamento"
                    act3["title"] = "DESIGN DOBRÁVEL COMPACTO COM TRAVA DE SEGURANÇA"
                    act3["desc_tmpl"] = "Sistema dobrável seguro que recolhe totalmente o fio dentro do cabo metálico, permitindo transporte compacto e protegido no bolso, mochila ou colete de pesca."
                    new_specs = [
                        {"label": "Tipo", "value": "Canivete Tático Dobrável Compacto de Bolso"},
                        {"label": "Material da Lâmina", "value": "Aço Inoxidável com acabamento escurecido e abertura rápida"},
                        {"label": "Empunhadura", "value": "Corpo metálico texturizado em relevo com olhal traseiro para fiel"},
                        {"label": "Mecanismo", "value": "Dobrável com trava de segurança firme"},
                        {"label": "Aplicação", "value": "Pesca, camping, trilhas e uso diário (EDC)"}
                    ]
            # 15.3 Faca de Filetar Marine Sports Fillet Knife 19cm (MFK75T - Sem Bainha; Lâmina com Teflon e Cabo com Olhal)
            elif "fillet" in t_low or "mfk75t" in t_low:
                act1["tag"] = "Lâmina Flexível com Teflon (19 cm)"
                act1["title"] = "PRECISÃO CIRÚRGICA PARA FILETAR PEIXES COM ZERO DESPERDÍCIO"
                act1["desc_tmpl"] = "Desenvolvida especialmente para pescadores esportivos e preparo culinário de pescado, a {title} possui lâmina estreita e flexível de 19 cm (7,5\") em aço inoxidável com revestimento antiaderente que contorna a espinha com suavidade."
                act2["tag"] = "Empunhadura Antiderrapante"
                act2["title"] = "CABO EMBORRACHADO TEXTURIZADO COM GUARDA DE SEGURANÇA"
                act2["desc_tmpl"] = "Empunhadura ergonômica antiderrapante projetada para manter controle total mesmo com as mãos molhadas ou escorregadias, contando com guarda frontal de proteção para os dedos."
                act3["tag"] = "Revestimento Teflon & Olhal para Fiel"
                act3["title"] = "PROTEÇÃO ANTICORROSÃO E PASSADOR TRASEIRO PARA CORDÃO DE PULSO"
                act3["desc_tmpl"] = "O revestimento escuro em Teflon protege o aço contra a oxidação em ambientes de água doce ou salgada e evita que o filé grude na lâmina, enquanto o olhal integrado na extremidade do cabo permite acoplar cordão fiel ou pendurar a faca com praticidade."
                new_specs = [
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável flexível de 19 cm (7,5 polegadas) com revestimento em Teflon antiaderente"},
                    {"label": "Empunhadura", "value": "Polímero emborrachado antiderrapante texturizado com guarda de proteção e olhal traseiro"},
                    {"label": "Acabamento da Lâmina", "value": "Teflon preto anticorrosão de fácil limpeza (desliza sem grudar no filé)"},
                    {"label": "Indicação de Uso", "value": "Filetagem de peixes, limpeza de pescado e culinária náutica"}
                ]
                template["care_tips"] = "Lavar manualmente com água doce e lado macio da esponja com sabão neutro logo após o uso para preservar o revestimento em Teflon. Secar imediatamente com pano limpo e macio antes de guardar em local seco e protegido."
            # 15.4 Cutelo 6" em Inox BRK (Sem bainha nas fotos; foco em lâmina larga, cabo madeira e corte de carnes/costelas)
            elif "cutelo" in t_low:
                act1["tag"] = "Lâmina Larga Full Tang de 6\""
                act1["title"] = "ESTRUTURA ROBUSTA EM AÇO INOX ESCOVADO COM DORSO MOSQUEADO"
                act1["desc_tmpl"] = "Projetado para entregar força de impacto e estabilidade superior na tábua, o {title} conta com lâmina larga de 6 polegadas (aprox. 16 cm) em aço inoxidável escovado, dorso trabalhado (mosqueado), gravação BRK a laser e furo frontal de suspensão."
                act2["tag"] = "Empunhadura Full Tang em Madeira"
                act2["title"] = "CABO ANATÔMICO EM MADEIRA NOBRE FIXADO POR 3 REBITES METÁLICOS"
                act2["desc_tmpl"] = "Construção integral Full Tang (espiga inteiriça) revestida por talas anatômicas de madeira nobre envernizada e fixada por 3 rebites metálicos em aço inox, assegurando equilíbrio perfeito e pegada firme."
                act3["tag"] = "Performance no Churrasco & Cozinha"
                act3["title"] = "IMPACTO PRECISO PARA CORTES DE CARNES, COSTELAS E TRINCHAMENTO"
                act3["desc_tmpl"] = "O peso balanceado na parte frontal da lâmina facilita o corte limpo de peças altas de churrasco, costelas, aves e alimentos densos com mínimo esforço e máxima precisão."
                new_specs = [
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável Full Tang de 6 polegadas (aprox. 16 cm) com dorso mosqueado"},
                    {"label": "Empunhadura", "value": "Madeira nobre anatômica fixada por 3 rebites metálicos em inox"},
                    {"label": "Acabamento da Lâmina", "value": "Inox escovado acetinado com furo de suspensão e gravação BRK a laser"},
                    {"label": "Indicação de Uso", "value": "Cortes pesados de churrasco, costelas, trinchamento de carnes e cozinha gourmet"}
                ]
                template["care_tips"] = "Lavar manualmente com água e lado macio da esponja logo após o uso. Secar imediatamente com pano limpo e macio antes de guardar em local seco e arejado."
            # 15.5 Kit Faca e Chaira Karandá (Bainha com Pelo / Bainha Preta)
            elif ("kit faca" in t_low or "chaira" in t_low) and ("karand" in t_low):
                bainha_desc = "revestimento frontal em pelo bovino natural legítimo" if "pelo" in t_low else "couro legítimo preto de alta espessura"
                bainha_title = "BAINHA DUPLA EM COURO COM PELO BOVINO NATURAL E TRAVAS DE PRESSÃO" if "pelo" in t_low else "BAINHA DUPLA EM COURO LEGÍTIMO PRETO COM TRAVAS DE PRESSÃO"
                act1["tag"] = "Conjunto Completo Faca & Chaira Karandá"
                act1["title"] = "LÂMINA EM AÇO INOXIDÁVEL POLIDO E CHAIRA ESTRIADA DE AFIAÇÃO"
                act1["desc_tmpl"] = "Conjunto tradicional de cutelaria assinado pela Karandá: o {title} combina faca de churrasco em aço inoxidável de aproximadamente 21 cm de lâmina com chaira estriada de 19 cm para manter o fio sempre alinhado."
                act2["tag"] = "Empunhadura Clássica & Guarda Polida"
                act2["title"] = "CABOS TORNEADOS ERGONÔMICOS COM GUARDA E POMO EM METAL POLIDO"
                act2["desc_tmpl"] = "Tanto a faca quanto a chaira apresentam cabos torneados de toque liso e anatômico em tom marfim clássico, finalizados com virola, guarda de proteção e pomo traseiro em metal polido."
                act3["tag"] = "Bainha Dupla de Cintura"
                act3["title"] = bainha_title
                act3["desc_tmpl"] = f"Acompanha bainha dupla confeccionada em {bainha_desc}, equipada com compartimentos independentes, passador para cinto e tiras com botões de pressão que travam a faca e a chaira com segurança."
                new_specs = [
                    {"label": "Itens Inclusos", "value": "1 Faca em Aço Inox (lâmina aprox. 21 cm), 1 Chaira Estriada (19 cm) e 1 Bainha Dupla"},
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável Karandá de alta retenção de fio e fácil manutenção"},
                    {"label": "Empunhadura", "value": "Cabos torneados ergonômicos com guarda e pomo em metal polido"},
                    {"label": "Bainha Inclusa", "value": f"Bainha dupla em {bainha_desc} com passador de cinto e travas de pressão"}
                ]
            # 15.6 Kit Faca e Chaira 9" BRK (Bainha Caramelo/Marrom Floral ou Trançada)
            elif "kit faca" in t_low or "chaira" in t_low:
                cor_bainha = "caramelo" if "caramelo" in t_low else "marrom"
                estilo_bainha = "relevo floral estampado" if "floral" in t_low else "textura trançada (balaiada) artesanal"
                act1["tag"] = "Conjunto Completo Faca 9\" & Chaira"
                act1["title"] = "FACA 9\" EM AÇO INOX COM DORSO MOSQUEADO E CHAIRA ESTRIADA"
                act1["desc_tmpl"] = "Pronto para o mestre churrasqueiro e para a lida no campo, o {title} une uma faca de 9 polegadas em aço inox escovado com vazado Bull Head e dorso mosqueado a uma chaira estriada de afiação rápida."
                act2["tag"] = "Empunhadura em Madeira Nobre"
                act2["title"] = "CABOS EM MADEIRA SELECIONADA COM 3 REBITES E ARGOLA DE SUSPENSÃO"
                act2["desc_tmpl"] = "A faca conta com construção Full Tang e cabo anatômico em madeira nobre fixado por 3 rebites metálicos, enquanto a chaira possui cabo em madeira torneada com guarda de proteção e argola metálica na extremidade."
                act3["tag"] = "Bainha Dupla em Couro Trabalhado"
                act3["title"] = f"BAINHA DUPLA EM COURO {cor_bainha.upper()} COM {estilo_bainha.upper()}"
                act3["desc_tmpl"] = f"Acompanha bainha dupla confeccionada em couro legítimo {cor_bainha} com {estilo_bainha}, costuras de alta tenacidade, passador de cinto e 2 travas individuais de botão de pressão para transporte seguro."
                new_specs = [
                    {"label": "Itens Inclusos", "value": "1 Faca 9\" em Aço Inox, 1 Chaira Estriada com cabo em madeira e 1 Bainha Dupla em Couro"},
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável Full Tang de 9 polegadas com dorso mosqueado e vazado Bull Head"},
                    {"label": "Empunhadura", "value": "Madeira nobre anatômica (3 rebites na faca + cabo torneado com argola na chaira)"},
                    {"label": "Bainha Inclusa", "value": f"Bainha dupla em couro {cor_bainha} com {estilo_bainha}, passador de cinto e 2 travas de pressão"}
                ]
            # 15.7 Facas Compactas de Cintura: Faca Rodeio 5" & Faca Curva 3" / Curva Nelore 3"
            elif "rodeio" in t_low or "curva" in t_low:
                cor_bainha = "caramelo" if "caramelo" in t_low else "marrom"
                pol = '3"' if '3"' in t_low or ' 3 ' in t_low else '5"'
                perfil_lamina = "perfil curvo Skinner de 3 polegadas com gancho superior" if "curva" in t_low else "perfil utilitário de 5 polegadas com dorso trabalhado"
                gravacao_extra = " e gravação Nelore na lâmina" if "nelore" in t_low else ""
                act1["tag"] = f"Lâmina Compacta Full Tang ({pol})"
                act1["title"] = f"AÇO INOXIDÁVEL ESCOVADO COM VAZADO BULL HEAD E CORTE ÁGIL"
                act1["desc_tmpl"] = f"Desenvolvida para o porte diário na cintura durante a lida no campo, rodeios, cavalgadas e churrascos, a {{title}} apresenta lâmina Full Tang em aço inoxidável escovado com {perfil_lamina}, vazado Bull Head{gravacao_extra} e excelente retenção de fio."
                act2["tag"] = "Empunhadura em Madeira Nobre"
                act2["title"] = "CABO ANATÔMICO EM MADEIRA FIXADO POR REBITES METÁLICOS"
                act2["desc_tmpl"] = "Empunhadura anatômica em madeira nobre que preenche a palma da mão com firmeza e segurança, fixada à espiga integral de aço por rebites metálicos e furo traseiro para fiel."
                act3["tag"] = "Bainha de Cintura em Couro"
                act3["title"] = f"BAINHA EM COURO {cor_bainha.upper()} TRABALHADO COM PASSADOR DUPLO DE CINTO"
                act3["desc_tmpl"] = f"Acompanha bainha sob medida em couro legítimo {cor_bainha} com textura balaiada/trançada em relevo, costura perimetral em linha encerada grossa, trava de botão de pressão e fendas laterais para passagem horizontal ou inclinada no cinto."
                new_specs = [
                    {"label": "Material da Lâmina", "value": f"Aço Inoxidável Full Tang de {pol} com acabamento escovado e vazado Bull Head{gravacao_extra}"},
                    {"label": "Empunhadura", "value": "Madeira nobre anatômica fixada por rebites metálicos com furo para fiel"},
                    {"label": "Bainha Inclusa", "value": f"Bainha de cintura em couro legítimo {cor_bainha} trabalhado com trava de pressão e passador duplo de cinto"},
                    {"label": "Indicação de Uso", "value": "Porte na cintura, lida no campo, rodeios, cavalgadas, pesca e churrasco"}
                ]
            # 15.8 Facas 10" Cabo em Madeira e Resina com Isca Artificial Encapsulada (Pescaria)
            elif "resina" in t_low and "isca" in t_low:
                tom_resina = "resina azul translúcida" if "resina azul" in t_low else "resina cristalina transparente"
                act1["tag"] = "Lâmina 10\" Multifuncional em Inox"
                act1["title"] = "AÇO INOX ESCOVADO COM DORSO MOSQUEADO, ABRIDOR E GRAVAÇÃO PESCARIA"
                act1["desc_tmpl"] = "Uma peça de destaque absoluto para pescadores e churrasqueiros: a {title} possui lâmina robusta de 10 polegadas em aço inoxidável escovado com dorso mosqueado, abridor de garrafas integrado, gancho frontal e gravação temática 'PESCARIA'."
                act2["tag"] = "Cabo Exclusivo com Isca Encapsulada"
                act2["title"] = "EMPUNHADURA ARTÍSTICA EM MADEIRA NOBRE E RESINA COM ISCA ARTIFICIAL"
                act2["desc_tmpl"] = f"O grande diferencial está no cabo anatômico híbrido confeccionado em madeira nobre e {tom_resina} de alto brilho, trazendo uma autêntica isca artificial encapsulada em 3D no interior do cabo."
                act3["tag"] = "Bainha Protetora em Couro"
                act3["title"] = "ACOMPANHA BAINHA EM COURO COSTURADO COM TRAVA DE BOTÃO DE PRESSÃO"
                act3["desc_tmpl"] = "Acompanha bainha protetora sob medida em couro legítimo com costura perimetral em linha encerada, passador de cinto e presilha com botão de pressão que mantém a faca segura no transporte."
                new_specs = [
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável de 10 polegadas (aprox. 26 cm) com dorso mosqueado e abridor de garrafas"},
                    {"label": "Empunhadura Exclusiva", "value": f"Híbrida anatômica em madeira nobre e {tom_resina} com isca artificial encapsulada"},
                    {"label": "Personalização na Lâmina", "value": "Gravação e vazado temático 'PESCARIA' + logo BRK Bull Head"},
                    {"label": "Bainha Inclusa", "value": "Bainha em couro costurado com trava de botão de pressão e passador de cinto"}
                ]
            # 15.9 Facas 10" Cabo em Madeira e Resina com Abridor (São Bento, Nossa Senhora, Nelore, Brasil, Azul, Colorida, Tática)
            elif "resina" in t_low:
                detalhe_tema = "personalização exclusiva"
                if "são bento" in t_low or "sao bento" in t_low:
                    detalhe_tema = "Medalha de São Bento gravada na lâmina e inserto São Bento com medalha no pomo em resina"
                elif "nossa senhora" in t_low:
                    detalhe_tema = "homenagem a Nossa Senhora gravada na lâmina e acabamento artístico no cabo em resina"
                elif "nelore" in t_low:
                    detalhe_tema = "tema Nelore gravado na lâmina e cabo artístico em madeira e resina"
                elif "brasil" in t_low:
                    detalhe_tema = "identidade Brasil na lâmina e cabo exclusivo em madeira e resina"
                elif prod_id_str == "10197363196201":
                    detalhe_tema = "vazado de revólver na lâmina e miniatura de revólver encapsulada na resina translúcida"
                elif prod_id_str == "10197363130665":
                    detalhe_tema = "vazado de escopeta na lâmina e cartucho encapsulado no cabo em resina"
                elif prod_id_str == "10197362737449":
                    detalhe_tema = "vazado de rifle na lâmina e projétil dourado encapsulado no cabo em resina"
                act1["tag"] = "Lâmina 10\" em Inox com Abridor"
                act1["title"] = "AÇO INOXIDÁVEL ESCOVADO COM DORSO MOSQUEADO E ABRIDOR INTEGRADO"
                act1["desc_tmpl"] = f"Projetada para unir alta performance de corte e design colecionável no churrasco, a {{title}} conta com lâmina de 10 polegadas (aprox. 26 cm) em aço inox escovado, dorso mosqueado, abridor de garrafas integrado e {detalhe_tema}."
                act2["tag"] = "Cabo Híbrido em Madeira & Resina"
                act2["title"] = "EMPUNHADURA ANATÔMICA EM MADEIRA NOBRE E RESINA DE ALTO BRILHO"
                act2["desc_tmpl"] = "Cabo anatômico esculpido na fusão entre madeira nobre selecionada e resina artística polida de alta densidade, garantindo pegada firme, equilíbrio de peso e visual único em cada peça."
                act3["tag"] = "Bainha Protetora em Couro"
                act3["title"] = "ACOMPANHA BAINHA EM COURO COSTURADO COM TRAVA DE PRESSÃO"
                act3["desc_tmpl"] = "Acompanha bainha sob medida em couro legítimo com costura perimetral em linha encerada, passador traseiro para cinto e presilha com botão de pressão para proteção total da lâmina."
                new_specs = [
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável de 10 polegadas (aprox. 26 cm) com dorso mosqueado e abridor integrado"},
                    {"label": "Empunhadura", "value": "Híbrida anatômica em madeira nobre e resina de alto brilho"},
                    {"label": "Destaque Exclusivo", "value": detalhe_tema[:1].upper() + detalhe_tema[1:]},
                    {"label": "Bainha Inclusa", "value": "Bainha protetora em couro costurado com trava de botão de pressão"}
                ]
            # 15.10 Facas 10" em Inox com Cabo em Madeira (São Bento, Nossa Senhora, Heróis da Estrada, Agro É Top, A Roça Venceu, Abridor)
            elif "inox" in t_low and ('10"' in t_low or "10 " in t_low or "abridor" in t_low):
                has_abridor = "abridor" in t_low
                act1["tag"] = "Lâmina 10\" Full Tang em Aço Inox"
                act1["title"] = "AÇO INOXIDÁVEL ESCOVADO DE 10 POLEGADAS COM GRAVAÇÃO EXCLUSIVA" if not has_abridor else "AÇO INOXIDÁVEL ESCOVADO DE 10 POLEGADAS COM ABRIDOR DE GARRAFA INTEGRADO"
                act1["desc_tmpl"] = "Construída para dominar o churrasco com precisão e presença marcante, a {title} apresenta lâmina Full Tang de 10 polegadas (aprox. 26,5 cm) em aço inoxidável escovado de alta retenção de fio."
                act2["tag"] = "Empunhadura Full Tang em Madeira"
                act2["title"] = "CABO ANATÔMICO EM MADEIRA NOBRE FIXADO POR 3 REBITES METÁLICOS"
                act2["desc_tmpl"] = "Espiga integral (Full Tang) revestida por talas anatômicas em madeira nobre selecionada e travada por 3 rebites metálicos em aço inox, proporcionando firmeza absoluta e equilíbrio no corte."
                act3["tag"] = "Bainha de Couro Sob Medida"
                act3["title"] = "ACOMPANHA BAINHA EM COURO COSTURADO COM TRAVA DE BOTÃO DE PRESSÃO"
                act3["desc_tmpl"] = "Acompanha bainha protetora confeccionada em couro legítimo com costura lateral em linha encerada, passador de cinto e presilha com botão de pressão para transporte e armazenamento seguros."
                new_specs = [
                    {"label": "Material da Lâmina", "value": "Aço Inoxidável Full Tang de 10 polegadas (aprox. 26,5 cm) com acabamento escovado"},
                    {"label": "Empunhadura", "value": "Madeira nobre anatômica fixada por 3 rebites metálicos em aço inox"},
                    {"label": "Diferencial da Lâmina", "value": "Abridor de garrafas integrado à lâmina e gravação BRK" if has_abridor else "Gravação temática exclusiva de alta definição na lâmina"},
                    {"label": "Bainha Inclusa", "value": "Bainha em couro legítimo costurado com trava de botão de pressão"}
                ]
            # 15.11 Facas Artesanais Gaúchas Forjadas (Aço Damasco / Aço Carbono - Cutelaria D'Avila)
            elif "artesanal" in t_low:
                is_damasco = "damasco" in t_low
                pol_ga = '12"' if '12"' in t_low or "12'" in t_low else '8"'
                aco_nome = "Aço Damasco forjado artesanalmente com padrão único de camadas" if is_damasco else "Aço Carbono forjado artesanalmente com acabamento brut de forge e dorso mosqueado"
                if "chifre de cervo" in t_low:
                    cabo_title = "CABO NOBRE EM CHIFRE DE CERVO E DETALHES EM ALPACA TRABALHADA"
                    cabo_val = "Chifre de Cervo legítimo com guarda/pomo em Alpaca finamente trabalhada"
                elif "hibrido" in t_low or "híbrido" in t_low:
                    cabo_title = "CABO HÍBRIDO ANATÔMICO EM MADEIRA NOBRE ESTABILIZADA COM PINOS METÁLICOS"
                    cabo_val = "Cabo híbrido anatômico em madeira nobre selecionada com pinos de fixação"
                else:
                    cabo_title = "CABO ARTESANAL EM MADEIRA NOBRE DE ALTA DENSIDADE E EQUILÍBRIO"
                    cabo_val = "Madeira nobre gaúcha selecionada de alta densidade e ergonomia"
                act1["tag"] = f"Forja Artesanal Gaúcha ({pol_ga})"
                act1["title"] = "LÂMINA FORJADA EM AÇO DAMASCO COM FIO NAVALHA EXCEPCIONAL" if is_damasco else "LÂMINA FORJADA EM AÇO CARBONO COM TÊMPERA INTEGRAL E DORSO MOSQUEADO"
                act1["desc_tmpl"] = f"Obra legítima da cutelaria artesanal gaúcha (Cutelaria D'Avila), a {{title}} é forjada individualmente em {aco_nome}, entregando poder de corte cirúrgico para churrascos, carneadas e uso no campo."
                act2["tag"] = "Empunhadura Exclusiva"
                act2["title"] = cabo_title
                act2["desc_tmpl"] = "Cada empunhadura possui veios e texturas naturais únicos, moldada artesanalmente para proporcionar encaixe firme na mão, equilíbrio impecável e nobreza estética."
                act3["tag"] = "Bainha de Couro & Garantia Vitalícia"
                act3["title"] = "ACOMPANHA BAINHA EM COURO LEGÍTIMO E CERTIFICADO DE PROPRIEDADE"
                act3["desc_tmpl"] = "Acompanha bainha artesanal sob medida em couro legítimo e Certificado de Propriedade com Garantia Vitalícia, consagrando uma peça exclusiva para colecionar ou usar por gerações."
                new_specs = [
                    {"label": "Material da Lâmina", "value": f"{aco_nome} ({pol_ga})"},
                    {"label": "Empunhadura", "value": cabo_val},
                    {"label": "Acompanhamento", "value": "Bainha artesanal em couro legítimo sob medida"},
                    {"label": "Certificação", "value": "Peça exclusiva numerada/assinada com Certificado de Garantia Vitalícia"}
                ]

        # 16. Isolamento Semântico de Vocabulário entre Lojas (brk_agro e brk_motors sem jargão de pesca indevido)
        has_explicit_fish_title = any(
            w in t_low for w in [
                "pesca", "pescaria", "fishing", "peixe", "tucunar", "robalo",
                "dourado", "pirarara", "tambaqui", "traira", "traíra", "isca", "carretilha", "molinete"
            ]
        )
        if store_key in ("brk_agro", "brk_motors") and not has_explicit_fish_title:
            def _adapt_store_vocab(txt: str) -> str:
                if not txt:
                    return txt
                if store_key == "brk_agro":
                    replacements = [
                        ("durante pescarias embarcadas, trilhas e pilotagem", "durante a lida no campo, cavalgadas e atividades ao ar livre"),
                        ("durante pescarias e expedições extremas", "durante a lida no campo, cavalgadas e expedições rurais"),
                        ("para pescarias, cavalgadas, praia, campo e dia a dia", "para a lida no campo, cavalgadas, rodeios, fazenda e dia a dia"),
                        ("para pescadores, pilotos e aventureiros", "para o homem e a mulher do campo, cavaleiros e aventureiros"),
                        ("no barco ou na moto", "no campo, a cavalo ou na caminhonete"),
                        ("com chapéus e bonés de pesca", "com chapéus country e bonés no campo"),
                        ("(pesca/campo)", "(campo/fazenda)"),
                        ("essencial para pesca, ciclismo e atividades outdoor", "essencial para o trabalho no campo, cavalgadas e atividades outdoor"),
                        ("movimentos de arremesso, pedalada ou corrida", "movimentos intensos na lida do campo, cavalgada ou lazer"),
                        ("na pescaria, no ciclismo ou no trabalho ao ar livre", "na lida do campo, nas cavalgadas ou no trabalho ao ar livre"),
                        ("durante arremessos, pedaladas ou condução de veículos", "durante a lida no campo, cavalgadas ou condução de veículos e máquinas"),
                        ("durante pescarias, viagens e lazer", "durante viagens, rotina na fazenda e lazer"),
                        ("Pescarias, praia, camping, viagens e dia a dia", "Fazenda, viagens, camping, rodeios e dia a dia"),
                        ("pós-pescaria ou lazer", "lazer, descanso e rotina diária"),
                        ("em longos dias de pescaria e caminhada", "em longos dias na fazenda, viagens e caminhada"),
                        ("no barco, no pesqueiro ou na rotina diária", "na fazenda, nas viagens ou na rotina diária"),
                        ("Embarcações, pesqueiros, praia, piscina e uso casual", "Fazenda, lazer, praia, piscina e uso casual"),
                        ("pescarias em família, praia, piscina, passeios no campo", "passeios na fazenda, cavalgadas em família, praia, piscina"),
                        ("Praia, piscina, pescarias em família, passeios ao ar livre e lazer infantil", "Fazenda, passeios em família, praia, piscina e lazer infantil ao ar livre"),
                        ("Pesca esportiva, náutica, direção, campo e estilo casual ao ar livre", "Lida no campo, direção, cavalgadas, eventos agro e estilo casual ao ar livre"),
                        ("Pesca esportiva, direção, viagens, campo e uso diário ao ar livre", "Lida no campo, direção, viagens, rodeios e uso diário ao ar livre"),
                        ("Pesca esportiva, náutica, direção, ciclismo, campo e uso diário", "Lida no campo, direção, cavalgadas, viagens e uso diário"),
                        ("pesca pesada em estruturas fechadas", "trabalho pesado no campo e atividades intensas"),
                        ("durante pescarias, ciclismo e remo", "durante o trabalho no campo, manejo rural e atividades ao ar livre"),
                        ("no toque da linha e carretilha", "no manuseio de ferramentas, rédeas e equipamentos"),
                        ("atar nós de pesca, controlar o carretel da carretilha,", "manusear ferramentas, rédeas,"),
                        ("Pesca esportiva, motociclismo, ciclismo, tiro esportivo e aventura", "Lida no campo, manejo rural, cavalgadas, ciclismo e aventura"),
                        ("Motociclismo, trilha, airsoft, operações táticas, pesca e trabalho no campo", "Trabalho no campo, manejo rural, trilha, operações táticas e aventura"),
                        ("uniforme de pesca, campo ou aventura", "uniforme de campo, comitiva ou aventura"),
                        ("ideal para pescadores esportivos, torneios, comitivas, equipes", "ideal para comitivas, fazendas, eventos agropecuários, equipes"),
                        ("Caixas de pesca, barcos, caiaques, caminhonetes, coolers e copos térmicos", "Caminhonetes, tratores, caixas térmicas, coolers e copos térmicos"),
                        ("no campo, na pescaria ou na rotina operacional", "no campo, na fazenda ou na rotina operacional"),
                        ("em viagens, pescarias, caminhões, motorhomes e acampamentos", "em viagens, na fazenda, caminhonetes, caminhões e acampamentos"),
                        ("Pesca, camping, overland, caminhões, barcos e viagens", "Fazenda, agronegócio, viagens, caminhonetes, caminhões e camping"),
                        ("na pescaria ou no campo", "na fazenda, na lida ou no lazer"),
                        ("no churrasco, no campo ou na pescaria", "no churrasco, na fazenda ou na lida campeira"),
                        ("no camping, na pescaria ou em casa", "na fazenda, no camping ou em casa"),
                        ("Churrascos, camping, pescarias, viagens e área gourmet", "Churrascos, fazenda, camping, viagens e área gourmet"),
                        ("no campo ou na pescaria", "na lida do campo, na fazenda ou no camping"),
                        ("Pesca esportiva, camping, lida no campo e uso diário (EDC)", "Lida no campo, fazenda, camping e uso diário (EDC)"),
                        ("Porte na cintura, lida no campo, rodeios, cavalgadas, pesca e churrasco", "Porte na cintura, lida no campo, rodeios, cavalgadas e churrasco"),
                        ("Pesca, camping, trilhas e uso diário (EDC)", "Lida no campo, camping, trilhas e uso diário (EDC)"),
                        ("durante a pescaria, a linha ArmorX", "na lida do campo e nas cavalgadas, a linha ArmorX"),
                        ("sem subir nos arremessos, deixando os dedos totalmente livres para sensibilidade tátil no manuseio de carretilha, molinete e iscas", "sem subir durante os movimentos, deixando os dedos totalmente livres para o manuseio de rédeas, ferramentas e equipamentos"),
                    ]
                else:  # brk_motors
                    replacements = [
                        ("durante pescarias embarcadas, trilhas e pilotagem", "durante a pilotagem, trilhas off-road e viagens de moto"),
                        ("durante pescarias e expedições extremas", "durante trilhas off-road, pilotagem e expedições extremas"),
                        ("para pescarias, cavalgadas, praia, campo e dia a dia", "para pilotagem, encontros de motos, viagens e dia a dia"),
                        ("para pescadores, pilotos e aventureiros", "para pilotos, motociclistas e aventureiros"),
                        ("no barco ou na moto", "na moto, no quadriciclo ou na trilha"),
                        ("com chapéus e bonés de pesca", "com capacetes, óculos de proteção e bonés"),
                        ("(pesca/campo)", "(estrada/trilha)"),
                        ("essencial para pesca, ciclismo e atividades outdoor", "essencial para motociclismo, ciclismo, trilhas e atividades outdoor"),
                        ("movimentos de arremesso, pedalada ou corrida", "movimentos de pilotagem, trilha, pedalada ou corrida"),
                        ("na pescaria, no ciclismo ou no trabalho ao ar livre", "na pilotagem, nas trilhas, no ciclismo ou ao ar livre"),
                        ("durante arremessos, pedaladas ou condução de veículos", "durante a pilotagem na estrada, trilhas ou condução de veículos"),
                        ("durante pescarias, viagens e lazer", "durante viagens, trilhas, track days e lazer"),
                        ("Pescarias, praia, camping, viagens e dia a dia", "Viagens, trilhas, camping, encontros automotivos e dia a dia"),
                        ("Pesca esportiva, náutica, direção, campo e estilo casual ao ar livre", "Pilotagem, direção, viagens, encontros automotivos e estilo casual"),
                        ("Pesca esportiva, direção, viagens, campo e uso diário ao ar livre", "Pilotagem, direção, viagens, estrada e uso diário ao ar livre"),
                        ("Pesca esportiva, náutica, direção, ciclismo, campo e uso diário", "Pilotagem, direção, ciclismo, viagens e uso diário"),
                        ("pesca pesada em estruturas fechadas", "pilotagem off-road, motocross e enduro"),
                        ("durante pescarias, ciclismo e remo", "durante a pilotagem, ciclismo e trilhas"),
                        ("no toque da linha e carretilha", "no acionamento de manetes e comandos"),
                        ("atar nós de pesca, controlar o carretel da carretilha,", "acionar comandos com rapidez,"),
                        ("Pesca esportiva, motociclismo, ciclismo, tiro esportivo e aventura", "Motociclismo, trilha, ciclismo, operações táticas e aventura"),
                        ("Motociclismo, trilha, airsoft, operações táticas, pesca e trabalho no campo", "Motociclismo, trilha, enduro, airsoft e operações táticas"),
                        ("uniforme de pesca, campo ou aventura", "uniforme de equipe, trilha ou motociclismo"),
                        ("ideal para pescadores esportivos, torneios, comitivas, equipes", "ideal para pilotos, equipes de trilha e motocross, motoclubes"),
                        ("Caixas de pesca, barcos, caiaques, caminhonetes, coolers e copos térmicos", "Capacetes, motos, carros, caixas de ferramentas, coolers e copos térmicos"),
                        ("no campo, na pescaria ou na rotina operacional", "nas oficinas, nos boxes, em viagens ou na rotina operacional"),
                        ("em viagens, pescarias, caminhões, motorhomes e acampamentos", "em expedições overland, viagens de caminhonete, caminhões, motorhomes e acampamentos"),
                        ("trilhas, barcos e estradas", "trilhas off-road, caminhonetes e estradas"),
                        ("Pesca, camping, overland, caminhões, barcos e viagens", "Overland, expedições 4x4, caminhonetes, caminhões, motorhomes e camping"),
                        ("na pescaria ou no campo", "nas pistas, nas trilhas ou no dia a dia"),
                        ("durante a pescaria, a linha ArmorX", "durante a pilotagem e as trilhas, a linha ArmorX"),
                        ("sem subir nos arremessos, deixando os dedos totalmente livres para sensibilidade tátil no manuseio de carretilha, molinete e iscas", "sem subir durante a pilotagem, deixando os dedos totalmente livres para sensibilidade tátil nos manetes e comandos"),
                    ]
                out = txt
                for old_s, new_s in replacements:
                    out = out.replace(old_s, new_s)
                return out

            for act_obj in (act1, act2, act3):
                act_obj["desc_tmpl"] = _adapt_store_vocab(act_obj.get("desc_tmpl", ""))
            for sp in new_specs:
                sp["value"] = _adapt_store_vocab(sp.get("value", ""))

        specs = new_specs

        source_type = "sibling_template" if sibling_info else "archetype_specialized"
        source_label = f"Molde Homólogo do Site ({sibling_info['sibling_title']})" if sibling_info else f"Arquétipo Especializado ({template['name']})"

        is_hand_glove_act3 = bool(is_apparel and img3 and self._is_hand_glove_photo(img3))
        is_humanized_model_act3 = bool(is_apparel and img3 and self._is_humanized_model_photo(img3))
        crop_sleeve_detail = bool(is_apparel and not is_kit_shirt_boot and img3 and not is_hand_glove_act3 and self._is_explicit_back_name(img3))
        if crop_sleeve_detail:
            act3["tag"] = "Detalhe Lateral: Mangas Curtas & Costura" if is_short_sleeve else "Detalhe Lateral: Mangas, Punhos & Costura"
            if not is_fusion and not is_hybrid and not is_hooded:
                act3["title"] = (
                    "MANGAS CURTAS COM BARRA REFORÇADA E COSTURAS PLANAS ANTI-ATRITO"
                    if is_short_sleeve else
                    "MANGAS ANATÔMICAS, PUNHOS FIRMES E COSTURAS PLANAS ANTI-ATRITO"
                )

        act1_dict = {
            "tag": act1["tag"],
            "fa_icon": act1.get("fa_icon", template.get("fa_icon", "fa-solid fa-check")),
            "title": act1["title"],
            "description": act1["desc_tmpl"].format(title=formatted_title),
            "image": img1,
            "back_360_image": back_360_img,
            "is_back_cover_360": is_back_cover_360,
            "split_images": split_images,
            "variations_summary": variations_summary
        }
        act2_dict = {
            "tag": act2["tag"],
            "fa_icon": act2.get("fa_icon", "fa-solid fa-sun"),
            "title": act2["title"],
            "description": act2["desc_tmpl"].format(title=formatted_title),
            "image": img2
        }
        act3_dict = {
            "tag": act3["tag"],
            "fa_icon": act3.get("fa_icon", "fa-solid fa-shield-halved"),
            "title": act3["title"],
            "description": act3["desc_tmpl"].format(title=formatted_title),
            "image": img3,
            "crop_sleeve_detail": crop_sleeve_detail,
            "is_hand_glove_act3": is_hand_glove_act3,
            "is_humanized_model_act3": is_humanized_model_act3
        }

        sku = str(product.get("sku") or product.get("master_sku") or product.get("id") or "")
        handle = str(product.get("handle") or "")
        vendor = str(product.get("vendor") or brand_name or "BRK")
        price = str(product.get("price") or (product.get("variants") and product.get("variants")[0].get("price")) or "0.00")

        details_grid = [dict(d) for d in template["details_grid"]] if template.get("details_grid") else None
        if details_grid and cdn_images:
            non_png = [u for u in cdn_images if not u.lower().split("?")[0].endswith(".png")]
            hw_pool = non_png if len(non_png) >= 4 else (non_png + [u for u in cdn_images if u not in non_png] if non_png else list(cdn_images))
            hw_imgs = [
                hw_pool[0],
                hw_pool[1] if len(hw_pool) > 1 else hw_pool[0],
                hw_pool[2] if len(hw_pool) > 2 else hw_pool[0],
                hw_pool[3] if len(hw_pool) > 3 else (hw_pool[1] if len(hw_pool) > 1 else hw_pool[0]),
            ]
            for idx, item in enumerate(details_grid[:4]):
                item["img"] = hw_imgs[idx]

        return {
            "title": formatted_title,
            "formatted_title": formatted_title,
            "brand_name": brand_name,
            "origin_type": origin_type,
            "show_copyright": show_copyright,
            "has_multiple_variations": has_multiple_variations,
            "split_images": split_images,
            "variations_summary": variations_summary,
            "store_key": store_key,
            "theme_color": theme_color,
            "theme_bg": theme_bg,
            "care_icon": care_icon,
            "source_type": source_type,
            "source_label": source_label,
            "sibling_info": sibling_info,
            "archetype_id": archetype_id,
            "layout_format": template.get("layout_format", "standard_3act"),
            "details_grid": details_grid,
            "info_characteristics": template.get("info_characteristics"),
            "info_care": template.get("info_care"),
            "split_sections": template.get("split_sections"),
            "is_kids": is_kids,
            "is_female": is_female,
            "is_short_sleeve": is_short_sleeve,
            "is_hooded": is_hooded,
            "sku": sku,
            "handle": handle,
            "vendor": vendor,
            "price": price,
            "images": cdn_images,
            "act1": act1_dict,
            "act2": act2_dict,
            "act3": act3_dict,
            "narrative_blocks": [act1_dict, act2_dict, act3_dict],
            "specs": specs,
            "care_tips": template.get("care_tips", "Lavar com sabão neutro e secar à sombra.")
        }
