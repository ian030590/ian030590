<<<<<<< HEAD
import sys
import re
import json
import argparse
import shutil
from html import escape
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote
import urllib.parse
import xml.etree.ElementTree as ET

from article_editorial_copy import HUMANIZED_ARTICLE_COPY

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / 'content'
SITEMAP_FILE = BASE_DIR / 'sitemap.xml'
ARTICLES_DATA_FILE = BASE_DIR / 'js' / 'articles-data.js'
BLOG_HTML_FILE = BASE_DIR / 'blog.html'

SITE_BASE_URL = 'https://ian030590.trainerhub.cc'

ADDITIONAL_CONTENT_FOLDERS = {
    'CognitRehab': ('認知復健', '中風認知、溝通與社會參與', 'cognitive'),
    'DigitLearn': ('數位學習', '臨床數位能力與 AI 應用', 'digital'),
    'MotorRehab': ('動作復健', '中風動作功能與併發症管理', 'motor'),
    'VisualRehab': ('視覺復健', '視覺復健評估與介入', 'visual'),
}

DL_IMAGES = [
    'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80',
]

def generate_publish_schedule():
    """
    產生全站 53 篇文章的穿插發布排程：
    1. 同主題文章時間絕不相鄰，相鄰文章必定來自不同主題（中間至少穿插一篇其他主題）
    2. 最新文章必須是視覺復健的最後一篇 (VisualTherapy 020)
    3. 同主題文章之間的時間順序嚴格遞增 (第二篇絕不早於第一篇)
    """
    # 總篇數：OT 20 篇, VT 20 篇, DL 13 篇，合計 53 篇
    # 建立 20 個 blocks，每個 block 由 OT 開始、VT 結束：
    # 13 個 X 型 block: [OT, DL, VT]
    # 7 個 Y 型 block: [OT, VT]
    # 使用 Bresenham 演算法均勻分配 X 與 Y
    blocks = []
    acc = 0
    for i in range(20):
        acc += 13
        if acc >= 20:
            blocks.append('X')
            acc -= 20
        else:
            blocks.append('Y')

    seq = []
    ot_idx = 1
    vt_idx = 1
    dl_idx = 1

    for b in blocks:
        if b == 'X':
            seq.append(('OccupationalTherapy', ot_idx))
            ot_idx += 1
            seq.append(('DigitalLearning', dl_idx))
            dl_idx += 1
            seq.append(('VisualTherapy', vt_idx))
            vt_idx += 1
        else:
            seq.append(('OccupationalTherapy', ot_idx))
            ot_idx += 1
            seq.append(('VisualTherapy', vt_idx))
            vt_idx += 1

    # 發布時程：起始於 2026-01-05 08:00:00+08:00，每 3 天一篇，最後一篇為 2026-06-10 08:00:00+08:00 (VisualTherapy 020)
    start_date = datetime(2026, 1, 5, 8, 0, 0)
    schedule = {}
    for i, (folder, order) in enumerate(seq):
        pub_date = start_date + timedelta(days=i * 3)
        schedule[f"{folder}_{order:03d}"] = pub_date.strftime('%Y-%m-%dT%H:%M:%S+08:00')

    return schedule

ARTICLE_PUBLISH_SCHEDULE = generate_publish_schedule()

# DigitalLearning file mapping: (old_filename, new_filename, short_topic, cluster, order)
DL_MAPPING = {
    '00_Blogger_Series_Introduction.html': (
        '001_AI產品架構思維系列總覽_非工程師的12講導讀總綱.html',
        '系列總覽',
        '非工程師的「AI 產品架構思維」12 講專題',
        1,
        '導讀總綱'
    ),
    'Post_01_AI_Mental_Model.html': (
        '002_心智模型_破除全能迷思用聘請頂尖實習生的心態理解大型語言模型.html',
        '心智模型',
        '非工程師的「AI 產品架構思維」12 講專題',
        2,
        '基礎認知與軟體架構'
    ),
    'Post_02_Software_Architecture_Lego.html': (
        '003_軟體骨架_非工程師的軟體樂高課前端後端API與資料庫到底在幹嘛.html',
        '軟體骨架',
        '非工程師的「AI 產品架構思維」12 講專題',
        3,
        '基礎認知與軟體架構'
    ),
    'Post_03_Prompt_Engineering_Secret.html': (
        '004_提示工程_別再盲目摸索提示詞寫出工業級Prompt的標準作業程序.html',
        '提示工程',
        '非工程師的「AI 產品架構思維」12 講專題',
        4,
        '提示工程與知識檢索'
    ),
    'Post_04_RAG_External_Brain.html': (
        '005_知識外掛_終結AI瞎掰RAG檢索增強生成如何打造專屬外掛大腦.html',
        '知識外掛',
        '非工程師的「AI 產品架構思維」12 講專題',
        5,
        '提示工程與知識檢索'
    ),
    'Post_05_AI_Agents_Action.html': (
        '006_智慧體行動_會思考還會動手自主AI智慧體是得力助手還是碎鈔機.html',
        '智慧體行動',
        '非工程師的「AI 產品架構思維」12 講專題',
        6,
        '自主智慧體與多Agent協同'
    ),
    'Post_06_Multi_Agent_and_MCP.html': (
        '007_協同協定_一人開一間虛擬公司多智慧體協同與AI界TypeC接口MCP.html',
        '協同協定',
        '非工程師的「AI 產品架構思維」12 講專題',
        7,
        '自主智慧體與多Agent協同'
    ),
    'Post_07_Vibe_Coding_Trap.html': (
        '008_防翻車指南_隨興編程是效率革命還是維運災難不懂代碼如何用AI開發工具不翻車.html',
        '防翻車指南',
        '非工程師的「AI 產品架構思維」12 講專題',
        8,
        '工程防護與資訊安全'
    ),
    'Post_08_LLM_Cybersecurity.html': (
        '009_資訊安全_AI時代的駭客江湖一句話就能套出公司機密的提示詞注入攻擊.html',
        '資訊安全',
        '非工程師的「AI 產品架構思維」12 講專題',
        9,
        '工程防護與資訊安全'
    ),
    'Post_09_Guardrails_and_Safety.html': (
        '010_安全護欄_給AI戴上安全韁繩如何打造不說髒話不洩漏個資的防護欄.html',
        '安全護欄',
        '非工程師的「AI 產品架構思維」12 講專題',
        10,
        '工程防護與資訊安全'
    ),
    'Post_10_Evaluating_AI.html': (
        '011_量化評測_你的AI到底有多聰明別再看感覺讓AI當裁判的科學評測法.html',
        '量化評測',
        '非工程師的「AI 產品架構思維」12 講專題',
        11,
        '評測成本與長期維運'
    ),
    'Post_11_Cost_and_Latency.html': (
        '012_成本與延遲_每聊一句都在燒錢破解AI產品的負毛利陷阱與延遲控制.html',
        '成本與延遲',
        '非工程師的「AI 產品架構思維」12 講專題',
        12,
        '評測成本與長期維運'
    ),
    'Post_12_AI_Lifecycle_and_Operations.html': (
        '013_生命週期運維_發布不是結束AI產品上線後如何不生病不擺爛的長照指南.html',
        '生命週期運維',
        '非工程師的「AI 產品架構思維」12 講專題',
        13,
        '評測成本與長期維運'
    ),
}

OT_IMAGES = {
    1: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80',
    2: 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=1200&q=80',
    3: 'https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=1200&q=80',
    4: 'https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&w=1200&q=80',
    5: 'https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&w=1200&q=80',
    6: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=1200&q=80',
    7: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1200&q=80',
    8: 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80',
    9: 'https://images.unsplash.com/photo-1516585427167-9f4af9627e6c?auto=format&fit=crop&w=1200&q=80',
    10: 'https://images.unsplash.com/photo-1581579438747-1dc8d17bbce4?auto=format&fit=crop&w=1200&q=80',
    11: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1200&q=80',
    12: 'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=1200&q=80',
    13: 'https://images.unsplash.com/photo-1576671081837-49000212a370?auto=format&fit=crop&w=1200&q=80',
    14: 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=1200&q=80',
    15: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=1200&q=80',
    16: 'https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&w=1200&q=80',
    17: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80',
    18: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=1200&q=80',
    19: 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80',
    20: 'https://images.unsplash.com/photo-1592478411213-6153e4ebc07d?auto=format&fit=crop&w=1200&q=80',
}

VT_IMAGES = {
    1: 'https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&w=1200&q=80',
    2: 'https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=1200&q=80',
    3: 'https://images.unsplash.com/photo-1574258495973-f010dfbb5371?auto=format&fit=crop&w=1200&q=80',
    4: 'https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&w=1200&q=80',
    5: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=1200&q=80',
    6: 'https://images.unsplash.com/photo-1563178406-4cdc2923acbc?auto=format&fit=crop&w=1200&q=80',
    7: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80',
    8: 'https://images.unsplash.com/photo-1758656321519-02fb5f48dc7e?auto=format&fit=crop&w=1200&q=80',
    9: 'https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1200&q=80',
    10: 'https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?auto=format&fit=crop&w=1200&q=80',
    11: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=1200&q=80',
    12: 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80',
    13: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80',
    14: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=1200&q=80',
    15: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=1200&q=80',
    16: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=1200&q=80',
    17: 'https://images.unsplash.com/photo-1527137342181-19aab11a8ee8?auto=format&fit=crop&w=1200&q=80',
    18: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=1200&q=80',
    19: 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=1200&q=80',
    20: 'https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=1200&q=80',
}

BROKEN_DOI_FIXES = {
    'https://research.google/pubs/everyone-wants-to-do-the-model-work-not-the-data-work-data-cascades-in-high-stakes-ai/': (
        'https://doi.org/10.1145/3411764.3445518',
        'Sambasivan N, Kapania S, Highfill H, et al. "Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI. Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems. 2021. https://doi.org/10.1145/3411764.3445518'
    ),
    '10.1609/hcomp.v11i1.27541': (
        'https://doi.org/10.48550/arXiv.2208.03274',
        'Markov, T., Zhang, C., Agarwal, S., et al. (2023). A Holistic Approach to Undesired Content Detection in the Real World. arXiv preprint arXiv:2208.03274.'
    ),
    '10.1016/S0140-6736(17)31447-3': (
        'https://doi.org/10.1016/S0140-6736(17)31447-2',
        'Lindley, R. I., et al. (2017). Family-led rehabilitation after stroke in India (ATTEND): a randomised, blind-endpoint trial. The Lancet, 390(10094), 588-599. https://doi.org/10.1016/S0140-6736(17)31447-2'
    ),
    '10.1016/S0140-6736(05)70992-3': (
        'https://doi.org/10.1016/S0140-6736(05)17983-5',
        'Dennis, M., et al. (2005). Effect of timing and method of enteral tube feeding for dysphagic stroke patients (FOOD): a multicentre randomised controlled trial. The Lancet, 365(9461), 764-772. https://doi.org/10.1016/S0140-6736(05)17983-5'
    ),
    '10.1136/bmjopen-2018-024170': (
        'https://doi.org/10.1371/journal.pone.0213035',
        'Rowe, F. J., et al. (2019). High incidence and prevalence of visual problems after acute stroke: An epidemiology study with implications for service delivery. PLOS ONE, 14(3), e0213035. https://doi.org/10.1371/journal.pone.0213035'
    ),
    '10.1002/14651858.CD008388.pub4': (
        'https://doi.org/10.1002/14651858.CD008388.pub3',
        'Pollock, A., et al. (2019). Interventions for visual field defects in people with stroke. Cochrane Database of Systematic Reviews, 5(5), CD008388. https://doi.org/10.1002/14651858.CD008388.pub3'
    ),
    '10.1016/S0140-6736(12)61852-7': (
        'https://doi.org/10.1136/bmj.328.7448.1099',
        'Kalra, L., et al. (2004). Training carers of stroke patients: randomised controlled trial. BMJ, 328(7448), 1099. https://doi.org/10.1136/bmj.328.7448.1099'
    ),
    '10.1016/S1474-4422(12)70163-6': (
        'https://doi.org/10.1016/j.neuropsychologia.2012.01.024',
        'Kerkhoff, G., & Schenk, T. (2012). Rehabilitation of neglect: An update. Neuropsychologia, 50(6), 1072–1079. https://doi.org/10.1016/j.neuropsychologia.2012.01.024'
    ),
    '10.1044/2019_AJSLP-18-0242': (
        'https://doi.org/10.1044/1058-0360(2009/09-0006)',
        'McCauley, R. J., Strand, E., Lof, G. L., Schooling, T., & Frymark, T. (2009). Evidence-based systematic review: Effects of nonspeech oral motor exercises on speech. American Journal of Speech-Language Pathology, 18(4), 343–360. https://doi.org/10.1044/1058-0360(2009/09-0006)'
    ),
    '10.1186/s13063-017-2066-x': (
        'https://doi.org/10.1186/1745-6215-13-218',
        'Rowe, F. J., et al. (2012). A randomised controlled trial of treatment for post-stroke homonymous hemianopia: screening and recruitment. Trials, 13, 218. https://doi.org/10.1186/1745-6215-13-218'
    ),
    '10.1177/15459683211011234': (
        'https://doi.org/10.1177/1545968310372774',
        'Keller, I., & Lefin-Rank, G. (2010). Improvement of visual search after audiovisual exploration training in hemianopic patients. Neurorehabilitation and Neural Repair, 24(7), 666–673. https://doi.org/10.1177/1545968310372774'
    ),
    '10.1001/jamaophthalmol.2014.2292': (
        'https://doi.org/10.1001/jamaophthalmol.2013.5636',
        'Bowers, A. R., Keeney, K., & Peli, E. (2014). Randomized Crossover Clinical Trial of Real and Sham Peripheral Prism Glasses for Hemianopia. JAMA Ophthalmology, 132(9), 1144–1152. https://doi.org/10.1001/jamaophthalmol.2013.5636'
    ),
    '10.1016/B978-0-444-53855-0.00013-X': (
        'https://doi.org/10.1016/B978-0-444-53355-5.00013-0',
        'Sabel, B. A., Henrich-Noack, P., Fedorov, A., & Gall, C. (2011). Vision restoration after brain and retina damage: The "residual vision activation theory". Progress in Brain Research, 192, 199–262. https://doi.org/10.1016/B978-0-444-53355-5.00013-0'
    ),
    '10.3389/fneur.2022.843100': (
        'https://doi.org/10.1177/1545968311425927',
        'Mödden, C., et al. (2012). A randomized controlled trial comparing 2 interventions for visual field loss with standard occupational therapy during inpatient stroke rehabilitation. Neurorehabilitation and Neural Repair, 26(5), 463–469. https://doi.org/10.1177/1545968311425927'
    ),
    '10.3233/RNN-201111': (
        'https://doi.org/10.3233/RNN-211198',
        'Räty, S., Borrmann, C., et al. (2021). Non-invasive electrical brain stimulation for vision restoration after stroke: An exploratory randomized trial (REVIS). Restorative Neurology and Neuroscience, 39(3), 221–235. https://doi.org/10.3233/RNN-211198'
    ),
    '10.5014/ajot.2021.755001': (
        'https://doi.org/10.5014/ajot.2023.077501',
        'Hildebrand, M. W., Geller, D., & Proffitt, R. (2023). Occupational Therapy Practice Guidelines for Adults With Stroke. American Journal of Occupational Therapy, 77(5), 7705397010. https://doi.org/10.5014/ajot.2023.077501'
    ),
}

VT_DOI_CACHE = {
  "Jackson ML, Virgili G, Shepherd JD, et al. Vision Rehabilitation Preferred Practice Pattern®. Ophthalmology. 2023;130(3):P271-P342.": "10.1016/j.ophtha.2022.10.024",
  "World Health Organization. World report on vision. Geneva: World Health Organization; 2019.": "https://www.who.int/publications/i/item/9789241516570",
  "Stelmack JA, Tang XC, Reda DJ, et al. Outcomes of the Veterans Affairs Low Vision Intervention Trial (LOVIT). Arch Ophthalmol. 2008;126(5):608-617.": "10.1001/archopht.126.5.608",
  "van Nispen RMA, Virgili G, Hoeben M, et al. Low vision rehabilitation for better quality of life in visually impaired adults. Cochrane Database Syst Rev. 2020;1(1):CD006543.": "10.1002/14651858.cd006543.pub2",
  "Ivers RQ, Norton R, Cumming RG, et al. Visual impairment and risk of hip fracture. Am J Epidemiol. 2000;152(7):633-639.": "10.1016/s0002-9394(01)00990-4",
  "Bailey IL, Lovie JE. New design principles for visual acuity letter charts. Am J Optom Physiol Opt. 1976;53(11):740-745.": "10.1097/00006324-197611000-00006",
  "Ferris FL 3rd, Kassoff A, Bresnick GH, Bailey I. New visual acuity charts for clinical research. Am J Ophthalmol. 1982;94(1):91-96.": "10.1016/0002-9394(82)90197-0",
  "Rosser DA, Cousens SN, Murdoch IE, et al. How sensitive to clinical change are common visual acuity charts? Invest Ophthalmol Vis Sci. 2003;44(7):3277-3281.": "10.1167/iovs.02-1100",
  "Sunness JS, El Annan J. Improvement of visual acuity in patients with dry age-related macular degeneration using a trial frame refraction. Retina. 2010;30(9):1472-1478.": "10.1097/00006982-200002000-00009",
  "Pelli DG, Robson JG, Wilkins AJ. The design of a new letter chart for measuring contrast sensitivity. Clin Vis Sci. 1988;2(3):187-199.": "10.32388/mcwwss",
  "Arditi A. Improving the design of the letter contrast sensitivity test. Invest Ophthalmol Vis Sci. 2005;46(6):2225-2229.": "10.1167/iovs.04-1198",
  "Rubin GS, Bandeen-Roche K, Prasada-Rao P, Fried LP. Visual impairment and disability in older adults: the SEE Project. Invest Ophthalmol Vis Sci. 1997;38(1):92-101.": "10.1002/j.1538-9235.1994.tb03438.x",
  "West SK, Rubin GS, Broman AT, et al. How does visual impairment affect performance on tasks of everyday life? The SEE Project. Arch Ophthalmol. 2002;120(6):774-780.": "10.1001/archopht.120.6.774",
  "Fletcher DC, Schuchard RA. Preferred retinal loci relationship to macular scotomas in a low-vision population. Ophthalmology. 1997;104(4):632-638.": "10.1016/s0161-6420(97)30260-7",
  "Crossland MD, Engel SA, Legge GE. The Preferred Retinal Locus in macular disease: characteristics and clinical implications. Ophthalmic Physiol Opt. 2011;31(3):210-214.": "10.1097/iae.0b013e31820d3fba",
  "Timberlake GT, Mainster MA, Peli E, et al. Reading with a macular scotoma. I. Retinal location of scotoma and fixation area. Invest Ophthalmol Vis Sci. 1986;27(7):1137-1147.": "10.1167/iovs.12-9908",
  "Midena E, Vujosevic S. Microperimetry in age-related macular degeneration. Eye (Lond). 2017;31(8):1108-1113.": "10.1038/eye.2017.34",
  "Nilsson UL, Frennesson C, Nilsson SE. Patients with AMD and a large foveal scotoma can learn to use an eccentric trained retinal locus (TRL): associated changes in reading speed and visual acuity. Optom Vis Sci. 2003;80(8):608-618.": "10.1016/s0042-6989(03)00219-0",
  "Deruaz A, Whatham AR, Mermoud C, Safran AB. Reading with an eccentric fixation point: is it possible to train eye movement patterns? Vision Res. 2002;42(22):2519-2532.": "10.1016/s0042-6989(02)00354-1",
  "Coco-Martin MB, Cuadrado-Asensio R, Lopez-Miguel A, et al. Design and evaluation of a customized visual training program in patients with age-related macular degeneration. Transl Vis Sci Technol. 2020;9(4):18.": "10.1016/j.ophtha.2012.07.035",
  "Virgili G, Acosta R, Bentley SA, et al. Reading aids for adults with low vision. Cochrane Database Syst Rev. 2018;4(4):CD003303.": "10.1002/14651858.cd003303.pub4",
  "Faye EE. Clinical Low Vision. 2nd ed. Boston: Little, Brown; 1984.": "10.1177/026461968500300310",
  "Bailey IL. Magnification for the low vision patient. Optom Monthly. 1981;72:14-17.": "10.1007/978-1-4612-4780-7_21",
  "Lovie-Kitchin J, Bowers A. High-addition and bifocal spectacles for low vision: predicting success. Optom Vis Sci. 2002;79(8):525-534.": "10.1111/j.1444-0938.2002.tb03042.x",
  "Peterson CB, Giles HC, Hall EC, et al. Reading performance in patients using closed circuit television vs. optical magnifiers. Optom Vis Sci. 2003;80(3):209-216.": "10.1167/iovs.11-8407",
  "Lovie-Kitchin J, Whittaker SG. Prescribing reading aids: developing a systematic procedure. Clin Exp Optom. 1999;82(3-4):115-124.": "10.1111/j.1444-0938.1999.tb06651.x",
  "Markowitz SN, Reyes SV, Flanagan JG. The role of smart phones in low vision rehabilitation. Can J Ophthalmol. 2013;48(5):e111-e113.": "10.1007/978-3-642-40300-2_19",
  "Crossland MD, Silva RZ, Macedo AF. Smartphone, tablet computer and e-reader use by people with vision impairment. Ophthalmic Physiol Opt. 2014;34(5):552-557.": "10.1111/opo.12136",
  "Joshi R, Huisingh C, McGwin G Jr, et al. Comparing smartphone and handheld optical magnification in persons with macular degeneration. Optom Vis Sci. 2017;94(8):831-837.": "10.1167/iovs.15-18962",
  "Budenz DL, Sunness JS, Di Nome MA, et al. Accessibility and mobile health applications in low vision: an American Academy of Ophthalmology clinical perspective. Ophthalmology. 2022;129(8):e75-e84.": "10.1016/j.ophtha.2022.04.015",
  "Mansfield JS, Ahn SJ, Legge GE, Luebker A. A new reading-acuity chart for normal and low vision: the MNREAD Acuity Chart. Invest Ophthalmol Vis Sci. 1993;34:1418.": "10.1364/navs.1993.nsud.3",
  "Legge GE. Psychophysics of Reading in Normal and Low Vision. Mahwah, NJ: Lawrence Erlbaum Associates; 2007.": "10.1201/9781482269482",
  "Calabrèse A, Cheong AM, Cheung SH, et al. Baseline MNREAD measures for normally sighted subjects from childhood to old age. Invest Ophthalmol Vis Sci. 2016;57(8):3866-3875.": "10.1167/iovs.16-19580",
  "Subramanian A, Dickinson C. What is the difference between reading acuity and critical print size in low vision patients? Optom Vis Sci. 2006;83(6):369-376.": "10.1093/9780198946960.003.0003",
  "Bowers AR, Meek C, Barker NH. Illumination characteristics of task lights preferred by people with low vision. Ophthalmic Physiol Opt. 2001;21(4):287-295.": "10.1007/s44402-026-00143-y",
  "Eperjesi F, Fowler CW, Evans BJ. Do tinted lenses or filters improve visual performance in low vision? A review of the literature. Ophthalmic Physiol Opt. 2002;22(1):68-77.": "10.1046/j.1475-1313.2002.00004.x",
  "Cullinane B, Evans BJ, Hughes D. The effect of lighting on reading speed and performance in patients with age-related macular degeneration. Br J Ophthalmol. 2004;88(6):830-834.": "10.1007/s10384-020-00769-6",
  "Brunnström G, Sörensen S, Alsterstad K, Sjöstrand J. Quality of light and quality of life in home care: elderly people with visual impairment. J Occup Sci. 2004;11(1):27-35.": "10.1111/j.1475-1313.2004.00192.x",
  "Leat SJ, North RV, Bryson H. Do long wavelength pass filters improve low vision performance? Ophthalmic Physiol Opt. 1990;10(3):219-224.": "10.1111/j.1475-1313.1990.tb00855.x",
  "Faye EE. Absorptive lenses in low vision: an overview. Optom Clin. 1993;3(4):75-84.": "10.54352/dozv.jvwy6099",
  "Mainster MA, Turner PL. Glare's causes, consequences, and clinical challenges after a century of cyclopean dissatisfaction. Prog Retin Eye Res. 2012;31(2):123-142.": "10.1016/j.ajo.2012.01.008",
  "American Occupational Therapy Association. Occupational therapy practice framework: Domain and process (4th ed.). Am J Occup Ther. 2020;74(Suppl. 2):7412410010.": "10.5014/ajot.2020.74s2001",
  "Berger S, Kaldenberg J. Occupational therapy interventions for older adults with low vision: a systematic review. Am J Occup Ther. 2013;67(3):e75-e84.": "10.5014/ajot.2019.038380",
  "Smallfield S, Clem K, Myers A. Occupational therapy interventions to improve reading performance of older adults with low vision: a systematic review. Am J Occup Ther. 2013;67(3):e61-e74.": "10.5014/ajot.2019.038380",
  "Warren M. Evaluation and Intervention for Low Vision. In: Pendleton HM, Schultz-Krohn W, eds. Pedretti's Occupational Therapy: Practice Skills for Physical Dysfunction. 8th ed. St. Louis: Elsevier; 2018:615-645.": "10.5014/ajot.45.6.573c",
  "Lord SR, Dayhew J. Visual risk factors for falls in older people. J Am Geriatr Soc. 2001;49(5):508-515.": "10.1046/j.1532-5415.2001.49107.x",
  "Wiener WR, Welsh RL, Blasch BB. Foundations of Orientation and Mobility. 3rd ed. New York: AFB Press; 2010.": "10.5070/t412011819",
  "Gillespie LD, Robertson MC, Gillespie WJ, et al. Interventions for preventing falls in older people living in the community. Cochrane Database Syst Rev. 2012;9:CD007146.": "10.1002/14651858.cd007146.pub2",
  "Sloan FA, Wang F. Disparities among older adults in medication adherence: the role of cognitive and visual impairments. Cogn Behav Neurol. 2005;18(4):217-226.": "10.1093/geroni/igab046.1852",
  "Brown CM, Jackson ML. Medication management in low vision: an occupational therapy and low vision clinician collaborative approach. J Vis Impair Blind. 2017;111(5):455-468.": "10.1177/0308022619858940",
  "American Society of Health-System Pharmacists. ASHP statement on the pharmacist's role in the care of patients with disabilities. Am J Health Syst Pharm. 2002;59(12):1201-1205.": "10.1093/ajhp/59.3.282",
  "Sleath B, Blalock SJ, Covert D, et al. The relationship between glaucoma medication adherence, eye drop technique, and visual field defect severity. Ophthalmology. 2011;118(12):2398-2402.": "10.1016/j.ophtha.2011.05.013",
  "American Medical Association. Physician's Guide to Assessing and Counseling Older Drivers. 4th ed. Washington, DC: National Highway Traffic Safety Administration; 2019.": "https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/14358a_olderdriversguidelines_082019_v1a_tag.pdf",
  "Bowers AR, Peli E, Elgin J, et al. On-road driving with bioptic telescopes: does the telescope help? Optom Vis Sci. 2005;82(8):743-753.": "10.1167/iovs.04-0271",
  "Owsley C, McGwin G Jr. Vision and driving. Vision Res. 2010;50(23):2348-2361.": "10.1016/j.visres.2010.05.021",
  "Freeman EE, Muñoz B, Turano KA, West SK. Measures of visual function and time to driving cessation in older adults: the Salisbury Eye Evaluation. Invest Ophthalmol Vis Sci. 2005;46(8):2756-2763.": "10.1167/iovs.05-0934",
  "Teunisse RJ, Cruysberg JR, Hoefnagels WH, et al. Visual hallucinations in psychologically normal people: Charles Bonnet's syndrome. Lancet. 1996;347(9004):794-797.": "10.1016/s0140-6736(96)90869-7",
  "Menon GJ, Rahman I, Menon SJ, Dutton GN. Complex visual hallucinations in the visually impaired: the Charles Bonnet Syndrome. Surv Ophthalmol. 2003;48(1):58-72.": "10.1016/s0039-6257(02)00414-9",
  "ffytche DH. Visual hallucinations and the Charles Bonnet syndrome. Curr Psychiatry Rep. 2005;7(3):168-179.": "10.1007/s11920-005-0050-3",
  "daSilva Morgan K, Webster KE, Shepherd JD, et al. Inhibitory transcranial direct current stimulation (tDCS) for the treatment of Charles Bonnet Syndrome: a randomized controlled trial. Ophthalmic Physiol Opt. 2021;41(4):780-791.": "10.26226/morressier.59a3e8b7d462b8028d89591d",
  "Rovner BW, Casten RJ, Hegel MT, et al. Preventing depression in age-related macular degeneration: a randomized controlled trial. Arch Gen Psychiatry. 2007;64(8):886-892.": "10.1001/archpsyc.64.8.886",
  "Rovner BW, Casten RJ, Hegel MT, et al. Low vision rehabilitation and depression in age-related macular degeneration: a randomized clinical trial. Ophthalmology. 2014;121(11):2204-2211.": "10.1016/j.ophtha.2014.05.002",
  "Brody BL, Roch-Levecq AC, Gamst AC, et al. Self-management of age-related macular degeneration and quality of life: a randomized controlled trial. Arch Ophthalmol. 2002;120(11):1477-1483.": "10.1001/archopht.120.11.1477",
  "van der Aa HP, van Rens GH, Comijs HC, et al. Stepped care for depression and anxiety in visually impaired older adults: a randomized controlled trial. BMJ Open. 2013;3(11):e003723.": "10.1136/bmj.h6127",
  "Baile WF, Buckman R, Lenzi R, et al. SPIKES—A six-step protocol for delivering bad news: application to the patient with cancer. Oncologist. 2000;5(4):302-311.": "10.1634/theoncologist.5-4-302",
  "Liénard A, Merckaert I, Libert Y, et al. Is it possible to improve residents breaking bad news skills? A randomised study assessing the efficacy of a 38-h communication skills training program. Br J Cancer. 2010;103(2):171-177.": "10.1038/sj.bjc.6605749",
  "Fletcher DC. Low vision rehabilitation: the art of compassionate communication and functional restoration. Ophthalmol Clin North Am. 2003;16(2):147-157.": "10.1001/archopht.1994.01090240026018",
  "Mogk LG. Vision rehabilitation: the critical next step in patient care. JAMA Ophthalmol. 2013;131(11):1481-1482.": "10.1001/jamaophthalmol.2013.4686",
  "Warren M. Occupational therapy's role in low vision rehabilitation: a historical perspective and future trends. Am J Occup Ther. 1995;49(9):857-865.": "10.5014/ajot.49.9.857",
  "Center for Medicare and Medicaid Services (CMS). Medicare Benefit Policy Manual: Chapter 15 - Covered Medical and Other Health Services (Section 220 - Physical Therapy, Occupational Therapy, and Speech-Language Pathology Services).": "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/bp102c15.pdf",
  "Markowitz SN. Principles of modern low vision rehabilitation. Can J Ophthalmol. 2006;41(3):289-312.": "10.1139/i06-027",
  "Stelmack JA, Tang XC, Wei Y, et al. Outcomes of the Veterans Affairs Low Vision Intervention Trial II (LOVIT II): a randomized clinical trial. JAMA Ophthalmol. 2017;135(2):96-104.": "10.1001/jamaophthalmol.2016.4742"
}



def get_cluster_articles(art, all_articles):
    return sorted(
        [candidate for candidate in all_articles
         if candidate['folder'] == art['folder'] and candidate['cluster'] == art['cluster']],
        key=lambda candidate: candidate['order'],
    )


def render_prev_next_navigation(art, all_articles):
    cluster_articles = get_cluster_articles(art, all_articles)
    current_index = next(
        index for index, candidate in enumerate(cluster_articles)
        if candidate['new_filename'] == art['new_filename']
    )
    neighbors = (
        ('prev', '上一篇', 'arrow_back', cluster_articles[current_index - 1] if current_index > 0 else None,
         '已是本系列首篇'),
        ('next', '下一篇', 'arrow_forward',
         cluster_articles[current_index + 1] if current_index + 1 < len(cluster_articles) else None,
         '已是本系列末篇'),
    )
    cards = []
    for direction, label, icon, article, boundary in neighbors:
        card_class = f'prev-next-card prev-next-card--{direction}'
        if article:
            href = f"/content/{article['folder']}/{quote(article['new_filename'])}"
            opening = f'<a class="{card_class}" href="{href}" rel="{direction}">'
            title = article['title']
            closing = '</a>'
        else:
            opening = f'<div class="{card_class} is-disabled" aria-disabled="true">'
            title = boundary
            closing = '</div>'
        cards.append(
            f'{opening}<span class="prev-next-label">'
            f'<span class="material-symbols-outlined" aria-hidden="true">{icon}</span>{label}</span>'
            f'<span class="prev-next-title">{escape(title)}</span>{closing}'
        )
    return '<nav class="prev-next-nav" aria-label="系列文章導覽">' + ''.join(cards) + '</nav>'


def sync_article_source(soup, art, all_articles=None):
    """Keep the published article, metadata, and navigation in sync."""
    if not art:
        return

    title = normalize_terminology(art.get('title', ''))
    summary = normalize_terminology(art.get('summary', ''))
    canonical_url = f"{SITE_BASE_URL}/content/{art['folder']}/{quote(art['new_filename'])}"
    image_url = art.get('img_src') or f"{SITE_BASE_URL}/icons/icon.svg"

    h1 = soup.find('h1', class_='article-title') or soup.find('h1')
    if h1 and title:
        h1.clear()
        h1.append(title)

    lead_box = soup.find('div', class_='article-lead-box')
    lead_p = lead_box.find('p') if lead_box else None
    if lead_p and summary:
        lead_p.clear()
        lead_p.append(summary)

    body = soup.find('div', class_='article-body-content')
    raw_body = art.get('raw_body', '')
    if body and raw_body:
        fragment = BeautifulSoup(raw_body, 'html.parser')
        body.clear()
        for child in list(fragment.contents):
            body.append(child)

    references = soup.select('.article-references ol > li')
    for index, citation in enumerate(art.get('citations', [])):
        if index >= len(references):
            break
        references[index]['id'] = f"ref-{index + 1}"
        link = references[index].find('a')
        if link is None or not citation.get('url'):
            continue
        link['href'] = citation['url']
        link['target'] = '_blank'
        link['rel'] = ['noopener', 'noreferrer']
        link.clear()
        link.append(citation['text'])

    title_tag = soup.find('title')
    if title_tag and title:
        title_tag.string = f"{title}｜蔡泓恩 職能治療師"

    curr_bc = soup.find('span', class_='breadcrumb-current')
    if curr_bc and title:
        curr_bc.clear()
        curr_bc.append(title)

    tag_badges = soup.find('div', class_='article-tag-badges')
    if tag_badges and art.get('tags'):
        tag_badges.clear()
        for t in art['tags']:
            badge = soup.new_tag('a', attrs={
                'class': 'article-badge',
                'href': f"{SITE_BASE_URL}/blog?tag={quote(t)}"
            })
            badge.string = t
            tag_badges.append(badge)

    lead_box_title = soup.find('div', class_='article-lead-box-title')
    if lead_box_title:
        lead_box_title.clear()
        lead_box_title.append("本篇要回答的決策")

    meta_row = soup.find('div', class_='article-meta-row')
    if meta_row:
        time_tag = meta_row.find('time')
        if not time_tag:
            date_str = (art.get('date_modified') or art.get('date_published', '2026-09-13'))[:10]
            meta_row.clear()
            author_span = soup.new_tag('span', attrs={'class': 'article-meta-item'})
            author_span.string = "蔡泓恩 職能治療師"
            time_elem = soup.new_tag('time', attrs={'datetime': art.get('date_modified') or art.get('date_published', '2026-09-13T08:00:00+08:00')})
            time_elem.string = f"更新：{date_str}"
            read_span = soup.new_tag('span', attrs={'class': 'article-meta-item'})
            read_span.string = art.get('read_time', '約 8 分鐘閱讀')
            meta_row.append(author_span)
            meta_row.append(time_elem)
            meta_row.append(read_span)

    author_note = soup.find('footer', class_='article-author-note')
    if author_note:
        p = author_note.find('p')
        if p:
            p.string = "作者：蔡泓恩 職能治療師。本文為專業教育與證據整理；個別處置仍需完整評估、當事人參與及適當跨專業合作。"

    keywords = ','.join(art.get('tags', []))
    meta_values = [
        ({'name': 'description'}, summary),
        ({'name': 'keywords'}, keywords),
        ({'property': 'og:title'}, title),
        ({'property': 'og:description'}, summary),
        ({'property': 'og:url'}, canonical_url),
        ({'property': 'og:image'}, image_url),
        ({'property': 'og:section'}, art.get('cat_name', '專業文章')),
        ({'property': 'article:published_time'}, art.get('date_published', '')),
        ({'property': 'article:modified_time'}, art.get('date_modified', '')),
        ({'property': 'article:section'}, art.get('cat_name', '專業文章')),
        ({'name': 'twitter:title'}, title),
        ({'name': 'twitter:description'}, summary),
        ({'name': 'twitter:image'}, image_url),
    ]
    for attrs, value in meta_values:
        if not value:
            continue
        tag = soup.find('meta', attrs=attrs)
        if tag is None and soup.head:
            tag = soup.new_tag('meta')
            for key, attr_value in attrs.items():
                tag[key] = attr_value
            soup.head.append(tag)
        if tag is not None:
            tag['content'] = value

    canonical = soup.find('link', rel='canonical')
    if canonical is not None:
        canonical['href'] = canonical_url

    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        nodes = data.get('@graph', []) if isinstance(data, dict) else []
        nodes = nodes or [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            types = node.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if 'Article' in types:
                node['@id'] = f"{canonical_url}#article"
                node['url'] = canonical_url
                node['mainEntityOfPage'] = canonical_url
                node['headline'] = title
                node['description'] = summary
                node['image'] = [image_url]
                node['datePublished'] = art.get('date_published', node.get('datePublished'))
                node['dateModified'] = art.get('date_modified', node.get('dateModified'))
                node['articleSection'] = art.get('cat_name', '專業文章')
                node['keywords'] = art.get('tags', [])
                node['citation'] = [
                    {
                        '@type': 'CreativeWork',
                        'name': citation['text'],
                        'url': citation['url'],
                    }
                    for citation in art.get('citations', [])
                    if citation.get('text') and citation.get('url')
                ]
            elif 'BreadcrumbList' in types:
                for item in node.get('itemListElement', []):
                    if item.get('position') == 3:
                        item['name'] = title
                        item['item'] = canonical_url
        script.string = json.dumps(data, ensure_ascii=False)

    if all_articles:
        navigation = BeautifulSoup(render_prev_next_navigation(art, all_articles), 'html.parser').nav
        existing = soup.select('.prev-next-nav')
        if existing:
            existing[0].replace_with(navigation)
            for duplicate in existing[1:]:
                duplicate.decompose()
        else:
            container = soup.find(class_='article-container')
            if container:
                bottom_actions = container.select_one('.article-trainerhub-cta, .article-bottom-actions')
                if bottom_actions:
                    bottom_actions.insert_before(navigation)
                else:
                    container.append(navigation)


def normalize_terminology(text):
    """Normalize clinical and assistive technology terminology according to content/README.md."""
    if not text:
        return text
    text = text.replace('電子助視器', '電子擴視機')
    text = text.replace('智慧頭顯', '頭戴式顯示器')
    text = text.replace('頭顯', '頭戴式顯示器')
    text = text.replace('低視力', '低視能')
    text = text.replace('黃斑旁預覽視窗', '中央凹旁預視視窗')
    return text

def extract_article_schema(soup):
    """Return the Article node from either a flat or @graph JSON-LD block."""
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        nodes = data.get('@graph', []) if isinstance(data, dict) else []
        nodes = nodes or [data]
        for node in nodes:
            types = node.get('@type', []) if isinstance(node, dict) else []
            if isinstance(types, str):
                types = [types]
            if 'Article' in types:
                return node
    return {}

def clean_inner_body(soup_body):
    """Clean up inline styles from body elements to make them adapt to light/dark themes."""
    for table in soup_body.find_all('table'):
        table['class'] = ['article-table']
        table.attrs.pop('style', None)
        if not table.parent or 'table-wrapper' not in table.parent.get('class', []):
            wrapper = soup_body.new_tag('div', **{'class': 'table-wrapper'})
            table.wrap(wrapper)
            
    for th in soup_body.find_all('th'):
        th.attrs.pop('style', None)
    for td in soup_body.find_all('td'):
        td.attrs.pop('style', None)
    for tr in soup_body.find_all('tr'):
        tr.attrs.pop('style', None)
        
    for h in soup_body.find_all(['h1', 'h2', 'h3', 'h4']):
        h.attrs.pop('style', None)
        
    for p in soup_body.find_all('p'):
        p.attrs.pop('style', None)
    for ul in soup_body.find_all(['ul', 'ol', 'li']):
        ul.attrs.pop('style', None)
        
    for div in soup_body.find_all('div'):
        style = div.get('style', '').lower()
        if 'fff5f5' in style or 'e53e3e' in style: # warning
            div['class'] = ['callout-box', 'warning']
            div.attrs.pop('style', None)
        elif 'fffaf0' in style or 'dd6b20' in style: # amber warning
            div['class'] = ['callout-box', 'amber']
            div.attrs.pop('style', None)
        elif 'e6f4ea' in style or '137333' in style or 'ebf8ff' in style: # success / info
            div['class'] = ['callout-box', 'success']
            div.attrs.pop('style', None)
        elif 'eff6ff' in style or 'f8fafc' in style or 'f7fafc' in style:
            div['class'] = ['callout-box']
            div.attrs.pop('style', None)
        elif 'ui-monospace' in style or 'monospace' in style or '#0f172a' in style:
            div['class'] = ['code-terminal-block']
            div.attrs.pop('style', None)
            
    for span in soup_body.find_all('span'):
        style = span.get('style', '').lower()
        if 'background' in style:
            text = span.get_text().strip()
            if 'cor 1' in text.lower():
                span['class'] = ['article-badge']
            elif 'cor 3' in text.lower():
                span['class'] = ['article-badge', 'badge-danger']
            span.attrs.pop('style', None)
        elif 'color' in style and ('#2d3748' in style or '#1a202c' in style or '#0f172a' in style):
            span.attrs.pop('style', None)
            
    return str(soup_body)

ARTICLE_TAG_MAP = {
    # DigitalLearning (13 articles)
    "DigitalLearning_001": ["數位學習", "AI應用"],
    "DigitalLearning_002": ["數位學習", "AI應用"],
    "DigitalLearning_003": ["數位學習", "AI應用"],
    "DigitalLearning_004": ["數位學習", "AI應用"],
    "DigitalLearning_005": ["數位學習", "AI應用"],
    "DigitalLearning_006": ["數位學習", "AI應用"],
    "DigitalLearning_007": ["數位學習", "AI應用"],
    "DigitalLearning_008": ["數位學習", "AI應用"],
    "DigitalLearning_009": ["數位學習", "AI應用"],
    "DigitalLearning_010": ["數位學習", "AI應用"],
    "DigitalLearning_011": ["數位學習", "AI應用"],
    "DigitalLearning_012": ["數位學習", "AI應用"],
    "DigitalLearning_013": ["數位學習", "AI應用"],

    # OccupationalTherapy (20 articles)
    "OccupationalTherapy_001": ["中風復健", "動作復健"],
    "OccupationalTherapy_002": ["中風復健", "動作復健"],
    "OccupationalTherapy_003": ["中風復健", "動作復健"],
    "OccupationalTherapy_004": ["中風復健", "動作復健"],
    "OccupationalTherapy_005": ["中風復健", "動作復健"],
    "OccupationalTherapy_006": ["中風復健", "認知復健", "視覺復健"],
    "OccupationalTherapy_007": ["中風復健", "認知復健", "動作復健"],
    "OccupationalTherapy_008": ["中風復健", "動作復健"],
    "OccupationalTherapy_009": ["中風復健", "認知復健"],
    "OccupationalTherapy_010": ["中風復健", "動作復健", "認知復健"],
    "OccupationalTherapy_011": ["中風復健", "視覺復健"],
    "OccupationalTherapy_012": ["中風復健", "視覺復健", "動作復健"],
    "OccupationalTherapy_013": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_014": ["中風復健", "視覺復健"],
    "OccupationalTherapy_015": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_016": ["中風復健", "視覺復健"],
    "OccupationalTherapy_017": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_018": ["中風復健", "視覺復健"],
    "OccupationalTherapy_019": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_020": ["中風復健", "動作復健", "視覺復健", "認知復健"],

    # VisualTherapy (20 articles)
    "VisualTherapy_001": ["視覺復健"],
    "VisualTherapy_002": ["視覺復健"],
    "VisualTherapy_003": ["視覺復健", "動作復健"],
    "VisualTherapy_004": ["視覺復健"],
    "VisualTherapy_005": ["視覺復健", "認知復健"],
    "VisualTherapy_006": ["視覺復健"],
    "VisualTherapy_007": ["視覺復健"],
    "VisualTherapy_008": ["視覺復健", "AI應用"],
    "VisualTherapy_009": ["視覺復健", "認知復健"],
    "VisualTherapy_010": ["視覺復健"],
    "VisualTherapy_011": ["視覺復健"],
    "VisualTherapy_012": ["視覺復健", "動作復健"],
    "VisualTherapy_013": ["視覺復健", "動作復健"],
    "VisualTherapy_014": ["視覺復健", "認知復健"],
    "VisualTherapy_015": ["視覺復健", "認知復健"],
    "VisualTherapy_016": ["視覺復健", "認知復健"],
    "VisualTherapy_017": ["視覺復健", "認知復健"],
    "VisualTherapy_018": ["視覺復健"],
    "VisualTherapy_019": ["視覺復健", "中風復健"],
    "VisualTherapy_020": ["視覺復健"]
}

# Additional evidence-note collections. Keep every generated article inside the six approved tags.
ARTICLE_TAG_MAP.update({f"CognitRehab_{i:03d}": ["中風復健", "認知復健"] for i in range(1, 11)})
ARTICLE_TAG_MAP["CognitRehab_006"] = ["中風復健", "認知復健", "視覺復健"]

ARTICLE_TAG_MAP.update({f"DigitLearn_{i:03d}": ["數位學習"] for i in range(1, 29)})
for i in [3, 5, 8, 9, 17]:
    if f"DigitLearn_{i:03d}" in ARTICLE_TAG_MAP:
        ARTICLE_TAG_MAP[f"DigitLearn_{i:03d}"] = ["數位學習", "AI應用"]
for i in range(16, 29):
    if f"DigitLearn_{i:03d}" in ARTICLE_TAG_MAP:
        ARTICLE_TAG_MAP[f"DigitLearn_{i:03d}"] = ["數位學習", "AI應用"]

ARTICLE_TAG_MAP.update({f"MotorRehab_{i:03d}": ["中風復健", "動作復健"] for i in range(1, 17)})
ARTICLE_TAG_MAP["MotorRehab_016"] = ["動作復健", "認知復健"]
ARTICLE_TAG_MAP["MotorRehab_017"] = ["動作復健"]

ARTICLE_TAG_MAP.update({f"VisualRehab_{i:03d}": ["視覺復健"] for i in range(1, 30)})
for i in range(20, 23):
    ARTICLE_TAG_MAP[f"VisualRehab_{i:03d}"].insert(0, "中風復健")
ARTICLE_TAG_MAP["VisualRehab_013"] = ["視覺復健", "動作復健"]
ARTICLE_TAG_MAP["VisualRehab_025"] = ["視覺復健", "AI應用"]
ARTICLE_TAG_MAP["VisualRehab_028"] = ["視覺復健", "動作復健"]
ARTICLE_TAG_MAP["VisualRehab_030"] = ["視覺復健", "動作復健"]

def collect_article_metadata():
    folders = [
        (folder, values[0], values[1], values[2])
        for folder, values in ADDITIONAL_CONTENT_FOLDERS.items()
    ]

    all_articles = []

    for folder, cat_name, cat_badge, cat_slug in folders:
        folder_path = CONTENT_DIR / folder
        conflicted = list(folder_path.glob('*conflicted*'))
        if conflicted:
            raise RuntimeError(f'Cloud sync conflict files require manual resolution: {conflicted}')

        files = sorted([f for f in folder_path.glob('*.html') if '[conflicted' not in f.name])
        for f in files:
            content = f.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            source_schema = extract_article_schema(soup)
            
            if folder == 'DigitalLearning':
                if f.name in DL_MAPPING:
                    new_filename, short_topic, cluster, order, sub_cluster = DL_MAPPING[f.name]
                elif f.name.startswith(('001_', '002_', '003_', '004_', '005_', '006_', '007_', '008_', '009_', '010_', '011_', '012_', '013_')):
                    order = int(f.name[:3])
                    new_filename = f.name
                    short_topic = f.name[4:].replace('.html', '').split('_')[0]
                    cluster = '非工程師的「AI 產品架構思維」12 講專題'
                    sub_cluster = '導讀總綱' if order == 1 else ('基礎認知與軟體架構' if order <= 3 else ('提示工程與知識檢索' if order <= 5 else ('自主智慧體與多Agent協同' if order <= 7 else ('工程防護與資訊安全' if order <= 10 else '評測成本與長期維運'))))
                else:
                    continue
            elif folder in ADDITIONAL_CONTENT_FOLDERS:
                clean_name = re.sub(r'\s*\[conflicted.*?\]', '', f.name)
                if not clean_name[:3].isdigit():
                    continue
                order = int(clean_name[:3])
                new_filename = clean_name
                short_topic = clean_name[4:].removesuffix('.html').split('_')[0]

                if folder == 'DigitLearn':
                    if order <= 7:
                        cluster, sub_cluster = '臨床人員的資工學習路徑', '資訊科學基礎'
                    elif order <= 15:
                        cluster, sub_cluster = 'Excel 與 Python 資料自動化', '資料處理與辦公自動化'
                    else:
                        cluster, sub_cluster = 'AI 產品開發與治理', 'AI 系統實務'
                else:
                    cluster = ADDITIONAL_CONTENT_FOLDERS[folder][1]
                    if folder == 'CognitRehab':
                        sub_cluster = '認知與溝通' if order <= 6 else '心理、轉銜與社會參與'
                    elif folder == 'VisualRehab':
                        if order >= 30:
                            cluster = '周邊前庭低功能與凝視穩定訓練'
                            sub_cluster = '2022 ANPT 前庭復健臨床實務指引'
                        elif order >= 23:
                            cluster = '低視能復健指引與實踐專題'
                            sub_cluster = 'Whittaker 臨床指引與實踐'
                        else:
                            sub_cluster = '低視能評估與介入' if order <= 19 else '腦傷與中風後視覺復健'
                    else:
                        if order >= 17:
                            cluster = '圍手術期與術後加速康復專題'
                            sub_cluster = '術後加速康復 ERAS 實證指引'
                        else:
                            sub_cluster = '工作復能與失能預防' if order == 16 else '動作、移動與日常活動'
            else:
                if f.name[:3].isdigit():
                    order = int(f.name[:3])
                    new_filename = f.name
                    short_topic = f.name[4:].replace('.html', '').split('_')[0]
                else:
                    order = int(f.name[:2])
                    new_filename = f'{order:03d}_{f.name[3:]}'
                    short_topic = f.name[3:].replace('.html', '').split('_')[0]
                    
                if folder == 'OccupationalTherapy':
                    if order <= 10:
                        cluster = '中風神經復健與全人照護'
                        sub_cluster = '急性期與動作功能重建'
                    else:
                        cluster = '中風後神經視覺復健'
                        sub_cluster = '神經視覺功能重建與代償'
                else: # VisualTherapy
                    if order <= 9:
                        cluster = '低視能臨床評估與光學處方科學'
                        sub_cluster = '功能評估與輔具處方'
                    elif order <= 14:
                        cluster = '環境人因工程、安全自理與防跌防護'
                        sub_cluster = '環境改造與居家自理'
                    else:
                        cluster = '特殊病徵、心理調適與跨專業協同'
                        sub_cluster = '跨專業全人照護'

            # Normalize terminology across filename, topic, cluster
            new_filename = normalize_terminology(new_filename)
            short_topic = normalize_terminology(short_topic)
            cluster = normalize_terminology(cluster)
            sub_cluster = normalize_terminology(sub_cluster)

            art_key = f"{folder}_{order:03d}"
            editorial_copy = HUMANIZED_ARTICLE_COPY.get(art_key)

            h1 = soup.find('h1')
            title = h1.get_text().strip() if h1 else ''
            if not title and soup.title:
                title = soup.title.get_text().strip()
            title = normalize_terminology(title)
            if editorial_copy:
                title = normalize_terminology(editorial_copy['title'])
                
            # Publish dates interleave the series; VT_020 stays the latest.
            header = soup.find('header')
            spans = [s.get_text().strip() for s in header.find_all('span')] if header else []
            
            html_tags = [a.get_text().strip() for a in header.select('.article-tag-badges a')] if header else []
            tags = html_tags or ARTICLE_TAG_MAP.get(art_key, [cat_name])
            if folder in ADDITIONAL_CONTENT_FOLDERS:
                date_published = source_schema.get('datePublished') or source_schema.get('dateModified') or '2026-09-12'
            else:
                date_published = ARTICLE_PUBLISH_SCHEDULE.get(art_key, '2026-01-01T08:00:00+08:00')
            date_modified = source_schema.get('dateModified') or date_published
            if len(date_published) == 10:
                date_published += 'T08:00:00+08:00'
            if len(date_modified) == 10:
                date_modified += 'T08:00:00+08:00'
                
            read_time = '約 5 分鐘閱讀'
            for s in spans:
                m = re.search(r'([0-9]+)\s*分鐘', s)
                if m:
                    read_time = f'約 {m.group(1)} 分鐘閱讀'
                    break
                    
            fig = soup.find('figure')
            img = fig.find('img') if fig else soup.find('img')
            caption = fig.find('figcaption').get_text().strip() if fig and fig.find('figcaption') else ''
            if not caption and img and img.get('alt'):
                caption = img.get('alt')
            caption = normalize_terminology(caption)
                
            if folder == 'OccupationalTherapy' and order in OT_IMAGES:
                img_src = OT_IMAGES[order]
            elif folder == 'VisualTherapy' and order in VT_IMAGES:
                img_src = VT_IMAGES[order]
            else:
                img_src = img['src'] if img and img.has_attr('src') else ''
                if 'files.catbox.moe' in img_src:
                    img_src = 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80'
            if folder in ADDITIONAL_CONTENT_FOLDERS and not (img_src.startswith('https://images.unsplash.com/') or img_src.startswith('https://plus.unsplash.com/')):
                if folder == 'DigitLearn':
                    img_src = DL_IMAGES[(order - 1) % len(DL_IMAGES)]
                elif folder == 'VisualRehab':
                    img_src = VT_IMAGES[(order - 1) % len(VT_IMAGES) + 1]
                else:
                    img_src = OT_IMAGES[(order - 1) % len(OT_IMAGES) + 1]

            summary = ''
            lead_box = soup.find('div', class_='article-lead-box')
            if lead_box and lead_box.find('p'):
                summary = lead_box.find('p').get_text().strip()
            else:
                header_p = header.find('p') if header else None
                if header_p and len(header_p.get_text().strip()) > 20:
                    summary = header_p.get_text().strip()
                else:
                    for div in soup.find_all('div'):
                        style = div.get('style', '')
                        if 'border-left' in style and ('f7fafc' in style or 'f8fafc' in style or 'eff6ff' in style):
                            p_in_div = div.find('p')
                            if p_in_div:
                                summary = p_in_div.get_text().strip()
                            else:
                                summary = div.get_text().strip()
                            break
            if not summary:
                first_p = soup.find('p')
                summary = first_p.get_text().strip() if first_p else title
            summary = normalize_terminology(summary)
            summary = re.sub(r'\s*\[\d+\]', '', summary)
            if editorial_copy:
                summary = normalize_terminology(editorial_copy['summary'])
                
            ref_sec = soup.find(['section', 'footer'], class_=lambda c: c and 'reference' in c) or soup.find('footer') or soup.find('section', {'aria-label': lambda x: x and '參考' in x})
            citations = []
            if ref_sec:
                for li in ref_sec.find_all('li'):
                    a = li.find('a')
                    cit_text = li.get_text().strip()
                    cit_url = a['href'].strip() if a and a.has_attr('href') else ''

                    if cit_url.startswith('../OriginalSources/DigitalLearning/'):
                        cit_url = cit_url.replace('../OriginalSources/DigitalLearning/', '../DigitalLearning/', 1)
                    elif cit_url.startswith('../OriginalSources/'):
                        cit_url = ''
                        cit_text = cit_text.removeprefix('本資料夾收錄之 ')
                    
                    for old_doi, (new_doi, new_text) in BROKEN_DOI_FIXES.items():
                        if old_doi in cit_url or old_doi in cit_text:
                            cit_url = new_doi
                            if new_text:
                                cit_text = new_text
                                
                    # If cit_url is empty (e.g. VisualTherapy), check VT_DOI_CACHE
                    if not cit_url and cit_text in VT_DOI_CACHE:
                        val = VT_DOI_CACHE[cit_text]
                        if val:
                            cit_url = val if val.startswith('http') else f'https://doi.org/{val}'
                            
                    citation = {'text': normalize_terminology(cit_text), 'url': cit_url}
                    if citation not in citations:
                        citations.append(citation)
                    
            if folder == 'DigitalLearning':
                news_article = soup.find('div', class_='news-article')
                if news_article:
                    na_copy = BeautifulSoup(str(news_article), 'html.parser')
                    if na_copy.find('header'):
                        na_copy.find('header').decompose()
                    if na_copy.find('figure'):
                        na_copy.find('figure').decompose()
                    if na_copy.find('footer'):
                        na_copy.find('footer').decompose()
                    if na_copy.find('style'):
                        na_copy.find('style').decompose()
                    body_html = str(na_copy)
                else:
                    body_soup = BeautifulSoup(content, 'html.parser')
                    if body_soup.find('header'):
                        body_soup.find('header').decompose()
                    if body_soup.find('figure'):
                        body_soup.find('figure').decompose()
                    if body_soup.find('footer'):
                        body_soup.find('footer').decompose()
                    if body_soup.find('style'):
                        body_soup.find('style').decompose()
                    body_html = str(body_soup)
            elif folder in ADDITIONAL_CONTENT_FOLDERS:
                body_div = soup.find('div', class_='article-body-content')
                if body_div:
                    body_copy = BeautifulSoup(str(body_div), 'html.parser')
                    for references in body_copy.find_all(class_='article-references'):
                        references.decompose()
                    body_html = body_copy.find('div', class_='article-body-content').decode_contents()
                else:
                    body_html = ''
            else: # OccupationalTherapy / VisualTherapy
                post_content_div = soup.find('div', class_='post-content')
                summary_box = soup.find('div', style=lambda s: s and 'ebf8ff' in s)
                body_parts = []
                if post_content_div:
                    body_parts.append(str(post_content_div))
                if summary_box:
                    body_parts.append(str(summary_box))
                body_html = '\n'.join(body_parts)
                
            if editorial_copy:
                body_html = editorial_copy['body']

            # Replace broken DOIs in body_html
            for old_doi, (new_doi, _) in BROKEN_DOI_FIXES.items():
                if old_doi in body_html:
                    body_html = body_html.replace(old_doi, new_doi)
            body_html = body_html.replace('https://doi.org/https://doi.org/', 'https://doi.org/')
            body_html = normalize_terminology(body_html)
                    
            all_articles.append({
                'folder': folder,
                'cat_name': cat_name,
                'cat_badge': cat_badge,
                'cat_slug': cat_slug,
                'cluster': cluster,
                'sub_cluster': sub_cluster,
                'order': order,
                'old_filename': f.name,
                'new_filename': new_filename,
                'title': title,
                'short_topic': short_topic,
                'tags': tags,
                'read_time': read_time,
                'img_src': img_src,
                'caption': caption,
                'summary': summary,
                'citations': citations,
                'date_published': date_published,
                'date_modified': date_modified,
                'raw_body': body_html
            })
            
    return all_articles

def build_article_html(art, all_articles):
    folder = art['folder']
    cat_name = art['cat_name']
    cluster_name = art['cluster']
    new_filename = art['new_filename']
    title = art['title']
    summary = art['summary']
    clean_desc = re.sub(r'\s+', ' ', summary).strip().replace('"', '&quot;')[:200]
    keywords_str = ', '.join(art['tags'])
    canonical_url = f"{SITE_BASE_URL}/content/{folder}/{quote(new_filename)}"
    web_page_path = f"/content/{folder}/{new_filename}"
    
    cluster_articles = get_cluster_articles(art, all_articles)
    
    schema_type = "TechArticle" if folder in ("DigitalLearning", "DigitLearn") else "MedicalScholarlyArticle"
    citations_json = [c['text'] for c in art['citations'] if c['text']]
    
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": [schema_type, "Article"],
                "@id": f"{canonical_url}#article",
                "isPartOf": {
                    "@type": "WebPage",
                    "@id": canonical_url
                },
                "headline": title,
                "description": clean_desc,
                "image": art['img_src'] if art['img_src'] else f"{SITE_BASE_URL}/icons/icon.svg",
                "datePublished": art['date_published'],
                "dateModified": art['date_modified'],
                "inLanguage": "zh-TW",
                "mainEntityOfPage": canonical_url,
                "author": {
                    "@type": "Person",
                    "name": "蔡泓恩",
                    "alternateName": "Hung-En (Ian) Tsai",
                    "jobTitle": "職能治療師",
                    "url": f"{SITE_BASE_URL}/",
                    "sameAs": [
                        "https://github.com/ian030590",
                        "https://trainerhub.cc"
                    ],
                    "knowsAbout": ["職能治療", "神經復健", "視覺復健", "低視能評估", "數位醫療", "AI系統架構"],
                    "alumniOf": "國立臺灣大學"
                },
                "publisher": {
                    "@type": "Person",
                    "name": "蔡泓恩",
                    "url": f"{SITE_BASE_URL}/"
                },
                "articleSection": cat_name,
                "keywords": art['tags'],
                "citation": citations_json
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首頁",
                        "item": f"{SITE_BASE_URL}/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "專業文章",
                        "item": f"{SITE_BASE_URL}/blog"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": cat_name,
                        "item": f"{SITE_BASE_URL}/blog?tag={quote(cat_name)}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": title,
                        "item": canonical_url
                    }
                ]
            }
        ]
    }
    
    cluster_items_html = []
    for ca in cluster_articles:
        is_active = (ca['new_filename'] == new_filename)
        active_class = " active" if is_active else ""
        link_target = f"./{ca['new_filename']}"
        current_badge = '<span class="topic-cluster-item-current">目前閱讀中</span>' if is_active else ""
        cluster_items_html.append(f"""
        <li>
          <a href="{link_target}" class="topic-cluster-item{active_class}">
            <span class="topic-cluster-item-num">{ca['order']:03d}</span>
            <span class="topic-cluster-item-title">{ca['title']}</span>
            {current_badge}
          </a>
        </li>""")
        
    cluster_list_rendered = '\n'.join(cluster_items_html)
    
    prev_next_html = render_prev_next_navigation(art, all_articles)

    refs_html = ""
    if art['citations']:
        ref_items = []
        for c in art['citations']:
            if c['url']:
                ref_items.append(f'<li><a href="{c["url"]}" target="_blank" rel="noopener noreferrer">{c["text"]}</a></li>')
            else:
                ref_items.append(f'<li>{c["text"]}</li>')
        refs_html = f"""
        <section class="article-references" aria-label="參考文獻與實證指引">
          <h2>參考文獻與實證指引 (References)</h2>
          <ol>
            {chr(10).join(ref_items)}
          </ol>
        </section>
        """

    cleaned_body = clean_inner_body(BeautifulSoup(art['raw_body'], 'html.parser'))
    
    figure_html = ""
    if art['img_src']:
        figure_html = f"""
        <figure class="article-featured-figure">
          <img src="{art['img_src']}" alt="{title}" class="article-featured-img" loading="lazy" />
          <figcaption class="article-figcaption">{art['caption'] or title}</figcaption>
        </figure>
        """

    date_str = art['date_published'][:10]
    date_html = f'<time datetime="{art["date_published"]}">{date_str}</time>' if folder in ADDITIONAL_CONTENT_FOLDERS else date_str
    
    if folder == 'OccupationalTherapy':
        evidence_note = '2026 AHA/ASA 臨床指引實證'
    elif folder == 'VisualRehab' and art['order'] >= 30:
        evidence_note = '2022 ANPT 前庭復健臨床實務指引'
    elif folder == 'VisualTherapy' or (folder == 'VisualRehab' and art['order'] <= 19):
        evidence_note = '2023 AAO PPP 臨床指引實證'
    elif folder in ('DigitalLearning', 'DigitLearn'):
        evidence_note = 'AI 系統架構與工程實踐'
    elif folder == 'MotorRehab' and art['order'] == 16:
        evidence_note = '2026 ACOEM 臨床實證指引'
    elif folder == 'MotorRehab' and art['order'] >= 17:
        evidence_note = '2019 ERAS 國際實證指引'
    else:
        evidence_note = '2026 AHA/ASA 臨床指引實證'

    tag_badges_html = '\n'.join([
        f'              <a href="/blog?tag={quote(t)}" class="article-badge" title="查看「{t}」相關文章">{t}</a>'
        for t in art['tags']
    ])

    full_html = f"""<!doctype html>
<html lang="zh-TW">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{title} | 蔡泓恩 職能治療師</title>
    <meta name="description" content="{clean_desc}" />
    <meta name="keywords" content="{keywords_str}" />
    <meta name="author" content="蔡泓恩 職能治療師" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{canonical_url}" />

    <!-- Open Graph / Social Media -->
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="zh_TW" />
    <meta property="og:site_name" content="蔡泓恩 | 職能治療師" />
    <meta property="og:title" content="{title} ｜ 蔡泓恩 職能治療師" />
    <meta property="og:description" content="{clean_desc}" />
    <meta property="og:url" content="{canonical_url}" />
    <meta property="og:image" content="{art['img_src'] or f'{SITE_BASE_URL}/icons/icon.svg'}" />
    <meta property="article:published_time" content="{art['date_published']}" />
    <meta property="article:modified_time" content="{art['date_modified']}" />
    <meta property="article:author" content="{SITE_BASE_URL}/" />
    <meta property="article:section" content="{cat_name}" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title} ｜ 蔡泓恩 職能治療師" />
    <meta name="twitter:description" content="{clean_desc}" />
    <meta name="twitter:image" content="{art['img_src'] or f'{SITE_BASE_URL}/icons/icon.svg'}" />

    <!-- Favicon & Stylesheet -->
    <link rel="icon" type="image/svg+xml" href="../../icons/icon.svg" />
    <link rel="icon" type="image/png" sizes="32x32" href="../../icons/favicon-32x32.png" />
    <link rel="icon" type="image/png" sizes="16x16" href="../../icons/favicon-16x16.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="../../icons/apple-touch-icon.png" />
    <link rel="stylesheet" href="../../css/style.css" />

    <!-- Schema.org Article JSON-LD (E-E-A-T) -->
    <script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
    </script>
  </head>
  <body>
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="/">
          <img src="../../icons/logo.png" alt="蔡泓恩 職能治療師 Logo" class="brand-logo" width="36" height="36" />
          <span>蔡泓恩 | 職能治療師</span>
        </a>
        <nav class="nav-links" aria-label="主要導覽">
          <a class="nav-link" href="/">首頁</a>
          <a class="nav-link" href="/projects">開源專案</a>
          <a class="nav-link active" href="/blog" aria-current="page">專業文章</a>
          <a class="nav-link" href="/contact">聯絡我</a>
          <a class="nav-link" href="/sponsor">贊助我</a>
        </nav>
        <button
          class="theme-toggle"
          aria-label="切換深色模式"
          title="切換深色模式"
        >
          <span class="material-symbols-outlined icon-dark" aria-hidden="true">dark_mode</span>
          <span class="material-symbols-outlined icon-light" aria-hidden="true" style="display: none;">light_mode</span>
        </button>
        <a class="nav-cta" href="mailto:rainbowh9490@gmail.com">聯絡我</a>
        <button
          class="menu-button"
          aria-label="開啟選單"
          aria-expanded="false"
        >
          <span
            class="animate-icon animate-icon--menu"
            data-animate-icon="menu"
            aria-hidden="true"
          ></span>
        </button>
      </div>
      <div class="mobile-panel">
        <a href="/">首頁</a>
        <a href="/projects">開源專案</a>
        <a href="/blog" aria-current="page">專業文章</a>
        <a href="/contact">聯絡我</a>
        <a href="/sponsor">贊助我</a>
      </div>
    </header>

    <main class="page-main article-page-layout">
      <div class="container">
        <!-- Breadcrumb Navigation -->
        <nav class="breadcrumb-trail" aria-label="文章路徑導覽">
          <a href="/">首頁</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <a href="/blog">專業文章</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <a href="/blog?tag={quote(cat_name)}">{cat_name}</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <span class="breadcrumb-current" aria-current="page">{title}</span>
        </nav>

        <article class="article-container">
          <!-- Article Header -->
          <header class="article-detail-header">
            <div class="article-tag-badges">
{tag_badges_html}
            </div>
            <h1 class="article-title">{title}</h1>
            <div class="article-meta-row">
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">person</span>
                蔡泓恩 職能治療師
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">calendar_today</span>
                {date_html}
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">schedule</span>
                {art['read_time']}
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">verified</span>
                {evidence_note}
              </span>
            </div>
          </header>

          <!-- Featured Banner Image -->
          {figure_html}

          <!-- Executive Summary Callout Box -->
          <div class="article-lead-box">
            <div class="article-lead-box-title">
              <span class="material-symbols-outlined" aria-hidden="true">lightbulb</span>
              專題重點摘要與核心洞察
            </div>
            <p>{summary}</p>
          </div>

          <!-- Main Body Content -->
          <div class="article-body-content">
            {cleaned_body}
          </div>

          <!-- Scientific References Section -->
          {refs_html}


          <!-- Topic Cluster Series Navigation -->
          <nav class="topic-cluster-nav" aria-label="同系列主題專題叢集">
            <div class="topic-cluster-header">
              <div class="topic-cluster-title">
                <span class="material-symbols-outlined" aria-hidden="true">auto_stories</span>
                【主題叢集】{cluster_name}
              </div>
              <div class="topic-cluster-progress">
                第 {art['order']:03d} 篇 / 全 {len(cluster_articles)} 篇
              </div>
            </div>
            <ul class="topic-cluster-list">
              {cluster_list_rendered}
            </ul>
          </nav>

          <!-- Prev & Next Article Navigation -->
          {prev_next_html}

          <!-- TrainerHub CTA & Back to Blog Navigation -->
          <div class="article-trainerhub-cta">
            <div class="trainerhub-cta-card">
              <div class="trainerhub-cta-badge">
                <span class="material-symbols-outlined" aria-hidden="true">neurology</span>
                <span>居家自主復健實踐</span>
              </div>
              <h3 class="trainerhub-cta-title">將臨床復健實證融入日常生活：TrainerHub 居家訓練網</h3>
              <p class="trainerhub-cta-desc">
                專為神經動作、視覺注意力與認知功能設計的互動式數位復能工具。免安裝、隨開隨練，讓中風復健、視野訓練與日常認知練習在家也能持續進行。
              </p>
              <div class="trainerhub-cta-actions">
                <a href="https://trainerhub.cc" class="button-primary trainerhub-cta-btn" target="_blank" rel="noopener" title="前往 TrainerHub 居家復健訓練網">
                  前往 TrainerHub 居家訓練網
                  <span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>
                </a>
              </div>
            </div>
          </div>

          <div class="article-bottom-actions">
            <a href="/blog" class="button-secondary">
              <span class="material-symbols-outlined" aria-hidden="true">arrow_back</span>
              返回所有專業專題列表
            </a>
          </div>
        </article>
      </div>
    </main>

    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <div class="footer-brand">
            <img src="../../icons/logo.png" alt="蔡泓恩 職能治療師 Logo" class="brand-logo footer-logo" width="26" height="26" />
            <span>蔡泓恩 | 職能治療師</span>
          </div>
          <div class="footer-copy">
            © <span data-year></span> Ian Tsai. 保留所有權利。
          </div>
        </div>
        <div class="footer-links">
          <a href="/">首頁</a>
          <a href="/projects">專案</a>
          <a href="/blog">專業文章</a>
          <a href="https://trainerhub.cc" target="_blank" rel="noopener" title="TrainerHub 居家復健訓練網">居家訓練網</a>
          <a href="/contact">聯絡</a>
          <a href="/sponsor">贊助我</a>
        </div>
      </div>
    </footer>

    <script src="../../js/animate-icons.js"></script>
    <script src="../../js/main.js"></script>
  </body>
</html>"""
    return full_html

def article_public_url(art):
    """Return the URL Cloudflare Workers static assets serve with 200.

    Workers answer `/x.html` with a redirect to `/x`, and search engines skip
    redirecting URLs in sitemaps and feeds, so these list the final URL.
    """
    stem = art['new_filename'].removesuffix('.html')
    return f"{SITE_BASE_URL}/content/{art['folder']}/{quote(stem)}"


def generate_sitemap(all_articles, output_dir=None):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{SITE_BASE_URL}/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/projects</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/blog</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/contact</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/sponsor</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>',
    ]
    
    for art in all_articles:
        encoded_url = article_public_url(art)
        lastmod = art['date_modified'][:10]
        lines.append(f'  <url><loc>{encoded_url}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')
        
    lines.append('</urlset>\n')
    sitemap_content = '\n'.join(lines)
    target = Path(output_dir) / 'sitemap.xml' if output_dir else SITEMAP_FILE
    target.write_text(sitemap_content, encoding='utf-8')
    print(f'Sitemap written to {target} ({len(all_articles) + 5} URLs)')

def generate_rss(all_articles, output_dir=None):
    sorted_articles = sorted(all_articles, key=lambda art: art['date_published'], reverse=True)
    rss_items = []
    for art in sorted_articles:
        encoded_url = article_public_url(art)
        try:
            dt = datetime.fromisoformat(art['date_published'])
            pub_date_str = dt.strftime('%a, %d %b %Y %H:%M:%S +0800')
        except Exception:
            pub_date_str = art['date_published']
        title_esc = escape(art['title'])
        summary_esc = escape(art['summary'])
        categories = '\n'.join([f'        <category>{escape(t)}</category>' for t in art['tags']])
        rss_items.append(f"""    <item>
      <title>{title_esc}</title>
      <link>{encoded_url}</link>
      <guid isPermaLink="true">{encoded_url}</guid>
      <pubDate>{pub_date_str}</pubDate>
      <description>{summary_esc}</description>
      <author>rainbowh9490@gmail.com (蔡泓恩 職能治療師)</author>
{categories}
    </item>""")

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>蔡泓恩 | 職能治療師 - 專業文章與專題</title>
    <link>{SITE_BASE_URL}/blog</link>
    <description>蔡泓恩職能治療師的個人專業知識庫與專題文章，專注於中風神經復健、視覺復健、認知與動作復健、AI與數位醫療應用。</description>
    <language>zh-TW</language>
    <atom:link href="{SITE_BASE_URL}/rss.xml" rel="self" type="application/rss+xml" />
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
    rss_file = Path(output_dir or BASE_DIR) / 'rss.xml'
    rss_file.write_text(rss_content, encoding='utf-8')
    print(f'RSS feed written to {rss_file} ({len(sorted_articles)} items)')

def generate_articles_data(all_articles, output_dir=None):
    catalog = []
    for art in all_articles:
        catalog.append({
            'id': f"{art['folder']}_{art['order']:03d}",
            'title': art['title'],
            'lead': art['summary'][:160] + ('...' if len(art['summary']) > 160 else ''),
            'imageUrl': art['img_src'],
            'tags': art['tags'],
            'dateString': art['date_published'][:10],
            'readTime': art['read_time'],
            'link': f"/content/{art['folder']}/{art['new_filename']}",
            'sourceName': art['cat_name'],
            'category': art['cat_name'],
            'cluster': art['cluster'],
            'subCluster': art['sub_cluster'],
            'order': art['order'],
            'folder': art['folder'],
            'filename': art['new_filename']
        })
        
    js_code = f"""// Generated static articles catalog (No Blogger dependencies)
window.__STATIC_ARTICLES__ = {json.dumps(catalog, ensure_ascii=False, indent=2)};
"""
    target = Path(output_dir) / 'js' / 'articles-data.js' if output_dir else ARTICLES_DATA_FILE
    target.write_text(js_code, encoding='utf-8')
    print(f'Articles data written to {target} ({len(catalog)} articles)')
    return catalog

def validate_article_navigation(soup, art, all_articles):
    navigation = soup.select('.prev-next-nav')
    expected = BeautifulSoup(render_prev_next_navigation(art, all_articles), 'html.parser').nav
    if len(navigation) != 1 or navigation[0] != expected:
        raise RuntimeError(f"Inconsistent series navigation: {art['folder']}/{art['new_filename']}")


def validate_internal_link(source_file, href, page_soups):
    source_url = f"{SITE_BASE_URL}/{source_file.relative_to(BASE_DIR).as_posix()}"
    url = urllib.parse.urlsplit(urllib.parse.urljoin(source_url, href))
    if url.scheme not in ('http', 'https') or url.netloc != urllib.parse.urlsplit(SITE_BASE_URL).netloc:
        return None

    target = BASE_DIR / unquote(url.path).lstrip('/')
    if target.is_dir():
        target /= 'index.html'
    elif not target.suffix:
        target = target.with_suffix('.html')
    if not target.is_file():
        raise RuntimeError(f'Broken internal link in {source_file.relative_to(BASE_DIR)}: {href}')

    if url.fragment and target.suffix == '.html':
        if target not in page_soups:
            page_soups[target] = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
        target_soup = page_soups[target]
        fragment = unquote(url.fragment)
        if not (target_soup.find(id=fragment) or target_soup.find('a', attrs={'name': fragment})):
            raise RuntimeError(f'Broken internal fragment in {source_file.relative_to(BASE_DIR)}: {href}')
    return target


def validate_generated_site(all_articles):
    """Fail the build when generated navigation, metadata, or approved tags drift."""
    not_found = BASE_DIR / '404.html'
    if not not_found.is_file():
        raise RuntimeError('Cloudflare Workers needs 404.html to avoid serving the home page for missing URLs')
    not_found_soup = BeautifulSoup(not_found.read_text(encoding='utf-8'), 'html.parser')
    robots = not_found_soup.find('meta', attrs={'name': 'robots'})
    if not robots or 'noindex' not in {value.strip().lower() for value in robots.get('content', '').split(',')}:
        raise RuntimeError('The 404 page must be excluded from search indexing')
    approved_tags = {'中風復健', '視覺復健', '動作復健', '認知復健', '數位學習', 'AI應用'}
    additional_articles = [art for art in all_articles if art['folder'] in ADDITIONAL_CONTENT_FOLDERS]
    if len(additional_articles) < 30:
        raise RuntimeError(f'Expected at least 30 additional articles, found {len(additional_articles)}')

    for art in all_articles:
        article_key = f"{art['folder']}_{art['order']:03d}"
        if article_key not in ARTICLE_TAG_MAP or not set(art['tags']).issubset(approved_tags):
            raise RuntimeError(f'Unregistered or invalid tags: {article_key}')
        if art['folder'] not in ADDITIONAL_CONTENT_FOLDERS:
            continue

        article_file = CONTENT_DIR / art['folder'] / art['new_filename']
        soup = BeautifulSoup(article_file.read_text(encoding='utf-8'), 'html.parser')
        validate_article_navigation(soup, art, all_articles)
        stylesheet = soup.find('link', rel=lambda value: value and 'stylesheet' in value)
        schema = extract_article_schema(soup)
        if not stylesheet or stylesheet.get('href') != '../../css/style.css':
            raise RuntimeError(f'Wrong stylesheet path: {article_file}')
        if not schema.get('datePublished') or not schema.get('author'):
            raise RuntimeError(f'Incomplete Article JSON-LD: {article_file}')
        if '"@type": "BreadcrumbList"' not in article_file.read_text(encoding='utf-8'):
            raise RuntimeError(f'Missing BreadcrumbList JSON-LD: {article_file}')
        if not soup.find('header', class_='site-header'):
            raise RuntimeError(f'Missing site-header navbar: {article_file}')
        if not soup.find('a', class_='article-back-link'):
            raise RuntimeError(f'Missing article-back-link: {article_file}')
        if not soup.find('footer', class_='site-footer'):
            raise RuntimeError(f'Missing site-footer: {article_file}')
        if 'main.js' not in article_file.read_text(encoding='utf-8'):
            raise RuntimeError(f'Missing main.js script: {article_file}')
        if '.breadcrumb-trail, .ot-blog-article .prev-next-nav { display: none;' in article_file.read_text(encoding='utf-8'):
            raise RuntimeError(f'Hidden breadcrumb-trail or prev-next-nav in style: {article_file}')
        cluster_size = sum(
            1
            for candidate in additional_articles
            if candidate['folder'] == art['folder']
            and candidate['cluster'] == art['cluster']
        )
        if (
            cluster_size > 1
            and len(soup.select('.prev-next-nav a[href]')) < 1
            and len(soup.select('.topic-cluster-nav a[href]')) < 1
        ):
            raise RuntimeError(f'Missing topic-cluster internal links: {article_file}')
        if soup.find('a', href=lambda href: href and '../OriginalSources/' in href):
            raise RuntimeError(f'Dead OriginalSources link remains: {article_file}')

    # Cloud-sync conflict copies must never reach the build.
    conflicted_files = list(CONTENT_DIR.rglob('*conflicted*'))
    if conflicted_files:
        raise RuntimeError(f"Cloud sync conflict files detected in content/: {[f.name for f in conflicted_files]}")

    for art in additional_articles:
        fname = art['new_filename']
        if ' ' in fname or '[' in fname or ']' in fname:
            raise RuntimeError(f"Article filename contains invalid characters: {fname}")
        article_file = CONTENT_DIR / art['folder'] / fname
        if not article_file.is_file():
            raise RuntimeError(f"Article file does not exist on disk: {article_file}")

    # Covers relative paths, clean routes and fragment targets.
    page_soups = {}
    internal_link_count = 0
    for page in sorted(BASE_DIR.glob('*.html')) + sorted(CONTENT_DIR.rglob('*.html')):
        if page not in page_soups:
            page_soups[page] = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        for link in page_soups[page].select('a[href], link[href], script[src], img[src]'):
            href = link.get('href') if link.has_attr('href') else link['src']
            if validate_internal_link(page, href, page_soups) is not None:
                internal_link_count += 1

    data_content = ARTICLES_DATA_FILE.read_text(encoding='utf-8')
    json_match = re.search(r"window\.__STATIC_ARTICLES__\s*=\s*(\[.*?\]);", data_content, re.DOTALL)
    if not json_match:
        raise RuntimeError("Failed to parse window.__STATIC_ARTICLES__ in articles-data.js")
    articles_data = json.loads(json_match.group(1))
    expected_links = {f"/content/{art['folder']}/{art['new_filename']}" for art in all_articles}
    catalog_links = [item.get('link', '') for item in articles_data]
    if len(catalog_links) != len(expected_links) or set(catalog_links) != expected_links:
        raise RuntimeError('Article catalog has missing, duplicate or unexpected links')
    for item in articles_data:
        validate_internal_link(ARTICLES_DATA_FILE, item['link'], page_soups)
    blog_links = [link['href'] for link in page_soups[BLOG_HTML_FILE].select('.card-link[href]')]
    first_page_links = [
        item['link']
        for item in sorted(articles_data, key=lambda item: item['dateString'], reverse=True)[:15]
    ]
    if blog_links != first_page_links:
        raise RuntimeError('Blog must render the latest 15 articles in catalog order')

    # Sitemap URLs must resolve to real files and include every article.
    sitemap_links = [node.text for node in ET.parse(SITEMAP_FILE).iterfind('.//{*}loc')]
    for link in sitemap_links:
        if validate_internal_link(SITEMAP_FILE, link, page_soups) is None:
            raise RuntimeError(f'Unexpected external URL in sitemap.xml: {link}')
    sitemap_paths = {unquote(urllib.parse.urlsplit(link).path) for link in sitemap_links}
    if any(path.endswith('.html') for path in sitemap_paths):
        raise RuntimeError('Sitemap lists .html URLs that Cloudflare Workers redirect')
    if not {link.removesuffix('.html') for link in expected_links}.issubset(sitemap_paths):
        raise RuntimeError('Sitemap is missing article URLs')
    # No two articles may share an Unsplash photo.
    photo_ids = {}
    for art in additional_articles:
        img_url = art.get('img_src', '')
        m = re.search(r'photo-([a-zA-Z0-9_-]+)', img_url)
        pid = m.group(1) if m else img_url
        if pid in photo_ids:
            raise RuntimeError(
                f"Duplicate article image detected! Photo ID '{pid}' is used in both "
                f"'{photo_ids[pid]}' and '{art['folder']}/{art['new_filename']}'. "
                f"All articles must have unique, verified images."
            )
        photo_ids[pid] = f"{art['folder']}/{art['new_filename']}"

    print(f'Validation passed: {len(additional_articles)} articles have consistent series navigation, CSS, JSON-LD, navbar, back-link, unique images and zero conflict files. Checked {internal_link_count} internal HTML links, {len(catalog_links)} catalog links and {len(sitemap_links)} sitemap URLs, including fragment targets.')

def prepare_astro_assets(all_articles):
    """Stage only public assets; published article source files are immutable."""
    generated = BASE_DIR / '.generated'
    public = generated / 'public'
    if generated.resolve() != BASE_DIR.resolve() / '.generated' or public.is_symlink():
        raise RuntimeError('Generated asset directories must not redirect outside the project')
    if public.exists():
        if public.resolve() != BASE_DIR.resolve() / '.generated' / 'public':
            raise RuntimeError('Refusing to clean assets outside the generated directory')
        shutil.rmtree(public)
    public.mkdir(parents=True)

    for directory in ('assets', 'css', 'icons', 'js'):
        shutil.copytree(BASE_DIR / directory, public / directory,
                        ignore=shutil.ignore_patterns('articles-data.js', '__pycache__', '*.pyc'))
    for filename in ('favicon.ico', 'robots.txt', 'llms.txt', '_headers', '_redirects'):
        shutil.copy2(BASE_DIR / filename, public / filename)

    for art in all_articles:
        if art['old_filename'] != art['new_filename']:
            raise RuntimeError(f"Article filename requires manual correction: {art['old_filename']}")
        relative = Path('content') / art['folder'] / art['new_filename']
        target = public / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BASE_DIR / relative, target)

    catalog = generate_articles_data(all_articles, public)
    (generated / 'articles.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
    generate_sitemap(all_articles, public)
    generate_rss(all_articles, public)
    print(f'Astro assets prepared: {len(all_articles)} articles copied without modification.')


def main():
    parser = argparse.ArgumentParser(description='Prepare immutable article assets for Astro, or validate its output.')
    parser.add_argument('--validate', type=Path, metavar='SITE_DIR', help='Validate the completed Astro build')
    args = parser.parse_args()
    all_articles = collect_article_metadata()
    if args.validate:
        global BASE_DIR, CONTENT_DIR, ARTICLES_DATA_FILE, BLOG_HTML_FILE, SITEMAP_FILE
        source_root = BASE_DIR
        BASE_DIR = args.validate.resolve()
        CONTENT_DIR = BASE_DIR / 'content'
        ARTICLES_DATA_FILE = BASE_DIR / 'js' / 'articles-data.js'
        BLOG_HTML_FILE = BASE_DIR / 'blog.html'
        SITEMAP_FILE = BASE_DIR / 'sitemap.xml'
        for art in all_articles:
            relative = Path('content') / art['folder'] / art['new_filename']
            if (source_root / relative).read_bytes() != (BASE_DIR / relative).read_bytes():
                raise RuntimeError(f'Published article was modified during the build: {relative}')
        validate_generated_site(all_articles)
    else:
        prepare_astro_assets(all_articles)

if __name__ == '__main__':
    main()
=======
import sys
import re
import json
import argparse
import shutil
from html import escape
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote
import urllib.parse
import xml.etree.ElementTree as ET

from article_editorial_copy import HUMANIZED_ARTICLE_COPY

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / 'content'
SITEMAP_FILE = BASE_DIR / 'sitemap.xml'
ARTICLES_DATA_FILE = BASE_DIR / 'js' / 'articles-data.js'
BLOG_HTML_FILE = BASE_DIR / 'blog.html'

SITE_BASE_URL = 'https://ian030590.trainerhub.cc'

ADDITIONAL_CONTENT_FOLDERS = {
    'CognitRehab': ('認知復健', '中風認知、溝通與社會參與', 'cognitive'),
    'DigitLearn': ('數位學習', '臨床數位能力與 AI 應用', 'digital'),
    'MotorRehab': ('動作復健', '中風動作功能與併發症管理', 'motor'),
    'VisualRehab': ('視覺復健', '視覺復健評估與介入', 'visual'),
}

DL_IMAGES = [
    'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80',
]

def generate_publish_schedule():
    """
    產生全站 53 篇文章的穿插發布排程：
    1. 同主題文章時間絕不相鄰，相鄰文章必定來自不同主題（中間至少穿插一篇其他主題）
    2. 最新文章必須是視覺復健的最後一篇 (VisualTherapy 020)
    3. 同主題文章之間的時間順序嚴格遞增 (第二篇絕不早於第一篇)
    """
    # 總篇數：OT 20 篇, VT 20 篇, DL 13 篇，合計 53 篇
    # 建立 20 個 blocks，每個 block 由 OT 開始、VT 結束：
    # 13 個 X 型 block: [OT, DL, VT]
    # 7 個 Y 型 block: [OT, VT]
    # 使用 Bresenham 演算法均勻分配 X 與 Y
    blocks = []
    acc = 0
    for i in range(20):
        acc += 13
        if acc >= 20:
            blocks.append('X')
            acc -= 20
        else:
            blocks.append('Y')

    seq = []
    ot_idx = 1
    vt_idx = 1
    dl_idx = 1

    for b in blocks:
        if b == 'X':
            seq.append(('OccupationalTherapy', ot_idx))
            ot_idx += 1
            seq.append(('DigitalLearning', dl_idx))
            dl_idx += 1
            seq.append(('VisualTherapy', vt_idx))
            vt_idx += 1
        else:
            seq.append(('OccupationalTherapy', ot_idx))
            ot_idx += 1
            seq.append(('VisualTherapy', vt_idx))
            vt_idx += 1

    # 發布時程：起始於 2026-01-05 08:00:00+08:00，每 3 天一篇，最後一篇為 2026-06-10 08:00:00+08:00 (VisualTherapy 020)
    start_date = datetime(2026, 1, 5, 8, 0, 0)
    schedule = {}
    for i, (folder, order) in enumerate(seq):
        pub_date = start_date + timedelta(days=i * 3)
        schedule[f"{folder}_{order:03d}"] = pub_date.strftime('%Y-%m-%dT%H:%M:%S+08:00')

    return schedule

ARTICLE_PUBLISH_SCHEDULE = generate_publish_schedule()

# DigitalLearning file mapping: (old_filename, new_filename, short_topic, cluster, order)
DL_MAPPING = {
    '00_Blogger_Series_Introduction.html': (
        '001_AI產品架構思維系列總覽_非工程師的12講導讀總綱.html',
        '系列總覽',
        '非工程師的「AI 產品架構思維」12 講專題',
        1,
        '導讀總綱'
    ),
    'Post_01_AI_Mental_Model.html': (
        '002_心智模型_破除全能迷思用聘請頂尖實習生的心態理解大型語言模型.html',
        '心智模型',
        '非工程師的「AI 產品架構思維」12 講專題',
        2,
        '基礎認知與軟體架構'
    ),
    'Post_02_Software_Architecture_Lego.html': (
        '003_軟體骨架_非工程師的軟體樂高課前端後端API與資料庫到底在幹嘛.html',
        '軟體骨架',
        '非工程師的「AI 產品架構思維」12 講專題',
        3,
        '基礎認知與軟體架構'
    ),
    'Post_03_Prompt_Engineering_Secret.html': (
        '004_提示工程_別再盲目摸索提示詞寫出工業級Prompt的標準作業程序.html',
        '提示工程',
        '非工程師的「AI 產品架構思維」12 講專題',
        4,
        '提示工程與知識檢索'
    ),
    'Post_04_RAG_External_Brain.html': (
        '005_知識外掛_終結AI瞎掰RAG檢索增強生成如何打造專屬外掛大腦.html',
        '知識外掛',
        '非工程師的「AI 產品架構思維」12 講專題',
        5,
        '提示工程與知識檢索'
    ),
    'Post_05_AI_Agents_Action.html': (
        '006_智慧體行動_會思考還會動手自主AI智慧體是得力助手還是碎鈔機.html',
        '智慧體行動',
        '非工程師的「AI 產品架構思維」12 講專題',
        6,
        '自主智慧體與多Agent協同'
    ),
    'Post_06_Multi_Agent_and_MCP.html': (
        '007_協同協定_一人開一間虛擬公司多智慧體協同與AI界TypeC接口MCP.html',
        '協同協定',
        '非工程師的「AI 產品架構思維」12 講專題',
        7,
        '自主智慧體與多Agent協同'
    ),
    'Post_07_Vibe_Coding_Trap.html': (
        '008_防翻車指南_隨興編程是效率革命還是維運災難不懂代碼如何用AI開發工具不翻車.html',
        '防翻車指南',
        '非工程師的「AI 產品架構思維」12 講專題',
        8,
        '工程防護與資訊安全'
    ),
    'Post_08_LLM_Cybersecurity.html': (
        '009_資訊安全_AI時代的駭客江湖一句話就能套出公司機密的提示詞注入攻擊.html',
        '資訊安全',
        '非工程師的「AI 產品架構思維」12 講專題',
        9,
        '工程防護與資訊安全'
    ),
    'Post_09_Guardrails_and_Safety.html': (
        '010_安全護欄_給AI戴上安全韁繩如何打造不說髒話不洩漏個資的防護欄.html',
        '安全護欄',
        '非工程師的「AI 產品架構思維」12 講專題',
        10,
        '工程防護與資訊安全'
    ),
    'Post_10_Evaluating_AI.html': (
        '011_量化評測_你的AI到底有多聰明別再看感覺讓AI當裁判的科學評測法.html',
        '量化評測',
        '非工程師的「AI 產品架構思維」12 講專題',
        11,
        '評測成本與長期維運'
    ),
    'Post_11_Cost_and_Latency.html': (
        '012_成本與延遲_每聊一句都在燒錢破解AI產品的負毛利陷阱與延遲控制.html',
        '成本與延遲',
        '非工程師的「AI 產品架構思維」12 講專題',
        12,
        '評測成本與長期維運'
    ),
    'Post_12_AI_Lifecycle_and_Operations.html': (
        '013_生命週期運維_發布不是結束AI產品上線後如何不生病不擺爛的長照指南.html',
        '生命週期運維',
        '非工程師的「AI 產品架構思維」12 講專題',
        13,
        '評測成本與長期維運'
    ),
}

OT_IMAGES = {
    1: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80',
    2: 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=1200&q=80',
    3: 'https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=1200&q=80',
    4: 'https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&w=1200&q=80',
    5: 'https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&w=1200&q=80',
    6: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=1200&q=80',
    7: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1200&q=80',
    8: 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80',
    9: 'https://images.unsplash.com/photo-1516585427167-9f4af9627e6c?auto=format&fit=crop&w=1200&q=80',
    10: 'https://images.unsplash.com/photo-1581579438747-1dc8d17bbce4?auto=format&fit=crop&w=1200&q=80',
    11: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1200&q=80',
    12: 'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=1200&q=80',
    13: 'https://images.unsplash.com/photo-1576671081837-49000212a370?auto=format&fit=crop&w=1200&q=80',
    14: 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=1200&q=80',
    15: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=1200&q=80',
    16: 'https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&w=1200&q=80',
    17: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80',
    18: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=1200&q=80',
    19: 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80',
    20: 'https://images.unsplash.com/photo-1592478411213-6153e4ebc07d?auto=format&fit=crop&w=1200&q=80',
}

VT_IMAGES = {
    1: 'https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&w=1200&q=80',
    2: 'https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=1200&q=80',
    3: 'https://images.unsplash.com/photo-1574258495973-f010dfbb5371?auto=format&fit=crop&w=1200&q=80',
    4: 'https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&w=1200&q=80',
    5: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=1200&q=80',
    6: 'https://images.unsplash.com/photo-1563178406-4cdc2923acbc?auto=format&fit=crop&w=1200&q=80',
    7: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80',
    8: 'https://images.unsplash.com/photo-1758656321519-02fb5f48dc7e?auto=format&fit=crop&w=1200&q=80',
    9: 'https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1200&q=80',
    10: 'https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?auto=format&fit=crop&w=1200&q=80',
    11: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=1200&q=80',
    12: 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80',
    13: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80',
    14: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=1200&q=80',
    15: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=1200&q=80',
    16: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=1200&q=80',
    17: 'https://images.unsplash.com/photo-1527137342181-19aab11a8ee8?auto=format&fit=crop&w=1200&q=80',
    18: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=1200&q=80',
    19: 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=1200&q=80',
    20: 'https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=1200&q=80',
}

BROKEN_DOI_FIXES = {
    'https://research.google/pubs/everyone-wants-to-do-the-model-work-not-the-data-work-data-cascades-in-high-stakes-ai/': (
        'https://doi.org/10.1145/3411764.3445518',
        'Sambasivan N, Kapania S, Highfill H, et al. "Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI. Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems. 2021. https://doi.org/10.1145/3411764.3445518'
    ),
    '10.1609/hcomp.v11i1.27541': (
        'https://doi.org/10.48550/arXiv.2208.03274',
        'Markov, T., Zhang, C., Agarwal, S., et al. (2023). A Holistic Approach to Undesired Content Detection in the Real World. arXiv preprint arXiv:2208.03274.'
    ),
    '10.1016/S0140-6736(17)31447-3': (
        'https://doi.org/10.1016/S0140-6736(17)31447-2',
        'Lindley, R. I., et al. (2017). Family-led rehabilitation after stroke in India (ATTEND): a randomised, blind-endpoint trial. The Lancet, 390(10094), 588-599. https://doi.org/10.1016/S0140-6736(17)31447-2'
    ),
    '10.1016/S0140-6736(05)70992-3': (
        'https://doi.org/10.1016/S0140-6736(05)17983-5',
        'Dennis, M., et al. (2005). Effect of timing and method of enteral tube feeding for dysphagic stroke patients (FOOD): a multicentre randomised controlled trial. The Lancet, 365(9461), 764-772. https://doi.org/10.1016/S0140-6736(05)17983-5'
    ),
    '10.1136/bmjopen-2018-024170': (
        'https://doi.org/10.1371/journal.pone.0213035',
        'Rowe, F. J., et al. (2019). High incidence and prevalence of visual problems after acute stroke: An epidemiology study with implications for service delivery. PLOS ONE, 14(3), e0213035. https://doi.org/10.1371/journal.pone.0213035'
    ),
    '10.1002/14651858.CD008388.pub4': (
        'https://doi.org/10.1002/14651858.CD008388.pub3',
        'Pollock, A., et al. (2019). Interventions for visual field defects in people with stroke. Cochrane Database of Systematic Reviews, 5(5), CD008388. https://doi.org/10.1002/14651858.CD008388.pub3'
    ),
    '10.1016/S0140-6736(12)61852-7': (
        'https://doi.org/10.1136/bmj.328.7448.1099',
        'Kalra, L., et al. (2004). Training carers of stroke patients: randomised controlled trial. BMJ, 328(7448), 1099. https://doi.org/10.1136/bmj.328.7448.1099'
    ),
    '10.1016/S1474-4422(12)70163-6': (
        'https://doi.org/10.1016/j.neuropsychologia.2012.01.024',
        'Kerkhoff, G., & Schenk, T. (2012). Rehabilitation of neglect: An update. Neuropsychologia, 50(6), 1072–1079. https://doi.org/10.1016/j.neuropsychologia.2012.01.024'
    ),
    '10.1044/2019_AJSLP-18-0242': (
        'https://doi.org/10.1044/1058-0360(2009/09-0006)',
        'McCauley, R. J., Strand, E., Lof, G. L., Schooling, T., & Frymark, T. (2009). Evidence-based systematic review: Effects of nonspeech oral motor exercises on speech. American Journal of Speech-Language Pathology, 18(4), 343–360. https://doi.org/10.1044/1058-0360(2009/09-0006)'
    ),
    '10.1186/s13063-017-2066-x': (
        'https://doi.org/10.1186/1745-6215-13-218',
        'Rowe, F. J., et al. (2012). A randomised controlled trial of treatment for post-stroke homonymous hemianopia: screening and recruitment. Trials, 13, 218. https://doi.org/10.1186/1745-6215-13-218'
    ),
    '10.1177/15459683211011234': (
        'https://doi.org/10.1177/1545968310372774',
        'Keller, I., & Lefin-Rank, G. (2010). Improvement of visual search after audiovisual exploration training in hemianopic patients. Neurorehabilitation and Neural Repair, 24(7), 666–673. https://doi.org/10.1177/1545968310372774'
    ),
    '10.1001/jamaophthalmol.2014.2292': (
        'https://doi.org/10.1001/jamaophthalmol.2013.5636',
        'Bowers, A. R., Keeney, K., & Peli, E. (2014). Randomized Crossover Clinical Trial of Real and Sham Peripheral Prism Glasses for Hemianopia. JAMA Ophthalmology, 132(9), 1144–1152. https://doi.org/10.1001/jamaophthalmol.2013.5636'
    ),
    '10.1016/B978-0-444-53855-0.00013-X': (
        'https://doi.org/10.1016/B978-0-444-53355-5.00013-0',
        'Sabel, B. A., Henrich-Noack, P., Fedorov, A., & Gall, C. (2011). Vision restoration after brain and retina damage: The "residual vision activation theory". Progress in Brain Research, 192, 199–262. https://doi.org/10.1016/B978-0-444-53355-5.00013-0'
    ),
    '10.3389/fneur.2022.843100': (
        'https://doi.org/10.1177/1545968311425927',
        'Mödden, C., et al. (2012). A randomized controlled trial comparing 2 interventions for visual field loss with standard occupational therapy during inpatient stroke rehabilitation. Neurorehabilitation and Neural Repair, 26(5), 463–469. https://doi.org/10.1177/1545968311425927'
    ),
    '10.3233/RNN-201111': (
        'https://doi.org/10.3233/RNN-211198',
        'Räty, S., Borrmann, C., et al. (2021). Non-invasive electrical brain stimulation for vision restoration after stroke: An exploratory randomized trial (REVIS). Restorative Neurology and Neuroscience, 39(3), 221–235. https://doi.org/10.3233/RNN-211198'
    ),
    '10.5014/ajot.2021.755001': (
        'https://doi.org/10.5014/ajot.2023.077501',
        'Hildebrand, M. W., Geller, D., & Proffitt, R. (2023). Occupational Therapy Practice Guidelines for Adults With Stroke. American Journal of Occupational Therapy, 77(5), 7705397010. https://doi.org/10.5014/ajot.2023.077501'
    ),
}

VT_DOI_CACHE = {
  "Jackson ML, Virgili G, Shepherd JD, et al. Vision Rehabilitation Preferred Practice Pattern®. Ophthalmology. 2023;130(3):P271-P342.": "10.1016/j.ophtha.2022.10.024",
  "World Health Organization. World report on vision. Geneva: World Health Organization; 2019.": "https://www.who.int/publications/i/item/9789241516570",
  "Stelmack JA, Tang XC, Reda DJ, et al. Outcomes of the Veterans Affairs Low Vision Intervention Trial (LOVIT). Arch Ophthalmol. 2008;126(5):608-617.": "10.1001/archopht.126.5.608",
  "van Nispen RMA, Virgili G, Hoeben M, et al. Low vision rehabilitation for better quality of life in visually impaired adults. Cochrane Database Syst Rev. 2020;1(1):CD006543.": "10.1002/14651858.cd006543.pub2",
  "Ivers RQ, Norton R, Cumming RG, et al. Visual impairment and risk of hip fracture. Am J Epidemiol. 2000;152(7):633-639.": "10.1016/s0002-9394(01)00990-4",
  "Bailey IL, Lovie JE. New design principles for visual acuity letter charts. Am J Optom Physiol Opt. 1976;53(11):740-745.": "10.1097/00006324-197611000-00006",
  "Ferris FL 3rd, Kassoff A, Bresnick GH, Bailey I. New visual acuity charts for clinical research. Am J Ophthalmol. 1982;94(1):91-96.": "10.1016/0002-9394(82)90197-0",
  "Rosser DA, Cousens SN, Murdoch IE, et al. How sensitive to clinical change are common visual acuity charts? Invest Ophthalmol Vis Sci. 2003;44(7):3277-3281.": "10.1167/iovs.02-1100",
  "Sunness JS, El Annan J. Improvement of visual acuity in patients with dry age-related macular degeneration using a trial frame refraction. Retina. 2010;30(9):1472-1478.": "10.1097/00006982-200002000-00009",
  "Pelli DG, Robson JG, Wilkins AJ. The design of a new letter chart for measuring contrast sensitivity. Clin Vis Sci. 1988;2(3):187-199.": "10.32388/mcwwss",
  "Arditi A. Improving the design of the letter contrast sensitivity test. Invest Ophthalmol Vis Sci. 2005;46(6):2225-2229.": "10.1167/iovs.04-1198",
  "Rubin GS, Bandeen-Roche K, Prasada-Rao P, Fried LP. Visual impairment and disability in older adults: the SEE Project. Invest Ophthalmol Vis Sci. 1997;38(1):92-101.": "10.1002/j.1538-9235.1994.tb03438.x",
  "West SK, Rubin GS, Broman AT, et al. How does visual impairment affect performance on tasks of everyday life? The SEE Project. Arch Ophthalmol. 2002;120(6):774-780.": "10.1001/archopht.120.6.774",
  "Fletcher DC, Schuchard RA. Preferred retinal loci relationship to macular scotomas in a low-vision population. Ophthalmology. 1997;104(4):632-638.": "10.1016/s0161-6420(97)30260-7",
  "Crossland MD, Engel SA, Legge GE. The Preferred Retinal Locus in macular disease: characteristics and clinical implications. Ophthalmic Physiol Opt. 2011;31(3):210-214.": "10.1097/iae.0b013e31820d3fba",
  "Timberlake GT, Mainster MA, Peli E, et al. Reading with a macular scotoma. I. Retinal location of scotoma and fixation area. Invest Ophthalmol Vis Sci. 1986;27(7):1137-1147.": "10.1167/iovs.12-9908",
  "Midena E, Vujosevic S. Microperimetry in age-related macular degeneration. Eye (Lond). 2017;31(8):1108-1113.": "10.1038/eye.2017.34",
  "Nilsson UL, Frennesson C, Nilsson SE. Patients with AMD and a large foveal scotoma can learn to use an eccentric trained retinal locus (TRL): associated changes in reading speed and visual acuity. Optom Vis Sci. 2003;80(8):608-618.": "10.1016/s0042-6989(03)00219-0",
  "Deruaz A, Whatham AR, Mermoud C, Safran AB. Reading with an eccentric fixation point: is it possible to train eye movement patterns? Vision Res. 2002;42(22):2519-2532.": "10.1016/s0042-6989(02)00354-1",
  "Coco-Martin MB, Cuadrado-Asensio R, Lopez-Miguel A, et al. Design and evaluation of a customized visual training program in patients with age-related macular degeneration. Transl Vis Sci Technol. 2020;9(4):18.": "10.1016/j.ophtha.2012.07.035",
  "Virgili G, Acosta R, Bentley SA, et al. Reading aids for adults with low vision. Cochrane Database Syst Rev. 2018;4(4):CD003303.": "10.1002/14651858.cd003303.pub4",
  "Faye EE. Clinical Low Vision. 2nd ed. Boston: Little, Brown; 1984.": "10.1177/026461968500300310",
  "Bailey IL. Magnification for the low vision patient. Optom Monthly. 1981;72:14-17.": "10.1007/978-1-4612-4780-7_21",
  "Lovie-Kitchin J, Bowers A. High-addition and bifocal spectacles for low vision: predicting success. Optom Vis Sci. 2002;79(8):525-534.": "10.1111/j.1444-0938.2002.tb03042.x",
  "Peterson CB, Giles HC, Hall EC, et al. Reading performance in patients using closed circuit television vs. optical magnifiers. Optom Vis Sci. 2003;80(3):209-216.": "10.1167/iovs.11-8407",
  "Lovie-Kitchin J, Whittaker SG. Prescribing reading aids: developing a systematic procedure. Clin Exp Optom. 1999;82(3-4):115-124.": "10.1111/j.1444-0938.1999.tb06651.x",
  "Markowitz SN, Reyes SV, Flanagan JG. The role of smart phones in low vision rehabilitation. Can J Ophthalmol. 2013;48(5):e111-e113.": "10.1007/978-3-642-40300-2_19",
  "Crossland MD, Silva RZ, Macedo AF. Smartphone, tablet computer and e-reader use by people with vision impairment. Ophthalmic Physiol Opt. 2014;34(5):552-557.": "10.1111/opo.12136",
  "Joshi R, Huisingh C, McGwin G Jr, et al. Comparing smartphone and handheld optical magnification in persons with macular degeneration. Optom Vis Sci. 2017;94(8):831-837.": "10.1167/iovs.15-18962",
  "Budenz DL, Sunness JS, Di Nome MA, et al. Accessibility and mobile health applications in low vision: an American Academy of Ophthalmology clinical perspective. Ophthalmology. 2022;129(8):e75-e84.": "10.1016/j.ophtha.2022.04.015",
  "Mansfield JS, Ahn SJ, Legge GE, Luebker A. A new reading-acuity chart for normal and low vision: the MNREAD Acuity Chart. Invest Ophthalmol Vis Sci. 1993;34:1418.": "10.1364/navs.1993.nsud.3",
  "Legge GE. Psychophysics of Reading in Normal and Low Vision. Mahwah, NJ: Lawrence Erlbaum Associates; 2007.": "10.1201/9781482269482",
  "Calabrèse A, Cheong AM, Cheung SH, et al. Baseline MNREAD measures for normally sighted subjects from childhood to old age. Invest Ophthalmol Vis Sci. 2016;57(8):3866-3875.": "10.1167/iovs.16-19580",
  "Subramanian A, Dickinson C. What is the difference between reading acuity and critical print size in low vision patients? Optom Vis Sci. 2006;83(6):369-376.": "10.1093/9780198946960.003.0003",
  "Bowers AR, Meek C, Barker NH. Illumination characteristics of task lights preferred by people with low vision. Ophthalmic Physiol Opt. 2001;21(4):287-295.": "10.1007/s44402-026-00143-y",
  "Eperjesi F, Fowler CW, Evans BJ. Do tinted lenses or filters improve visual performance in low vision? A review of the literature. Ophthalmic Physiol Opt. 2002;22(1):68-77.": "10.1046/j.1475-1313.2002.00004.x",
  "Cullinane B, Evans BJ, Hughes D. The effect of lighting on reading speed and performance in patients with age-related macular degeneration. Br J Ophthalmol. 2004;88(6):830-834.": "10.1007/s10384-020-00769-6",
  "Brunnström G, Sörensen S, Alsterstad K, Sjöstrand J. Quality of light and quality of life in home care: elderly people with visual impairment. J Occup Sci. 2004;11(1):27-35.": "10.1111/j.1475-1313.2004.00192.x",
  "Leat SJ, North RV, Bryson H. Do long wavelength pass filters improve low vision performance? Ophthalmic Physiol Opt. 1990;10(3):219-224.": "10.1111/j.1475-1313.1990.tb00855.x",
  "Faye EE. Absorptive lenses in low vision: an overview. Optom Clin. 1993;3(4):75-84.": "10.54352/dozv.jvwy6099",
  "Mainster MA, Turner PL. Glare's causes, consequences, and clinical challenges after a century of cyclopean dissatisfaction. Prog Retin Eye Res. 2012;31(2):123-142.": "10.1016/j.ajo.2012.01.008",
  "American Occupational Therapy Association. Occupational therapy practice framework: Domain and process (4th ed.). Am J Occup Ther. 2020;74(Suppl. 2):7412410010.": "10.5014/ajot.2020.74s2001",
  "Berger S, Kaldenberg J. Occupational therapy interventions for older adults with low vision: a systematic review. Am J Occup Ther. 2013;67(3):e75-e84.": "10.5014/ajot.2019.038380",
  "Smallfield S, Clem K, Myers A. Occupational therapy interventions to improve reading performance of older adults with low vision: a systematic review. Am J Occup Ther. 2013;67(3):e61-e74.": "10.5014/ajot.2019.038380",
  "Warren M. Evaluation and Intervention for Low Vision. In: Pendleton HM, Schultz-Krohn W, eds. Pedretti's Occupational Therapy: Practice Skills for Physical Dysfunction. 8th ed. St. Louis: Elsevier; 2018:615-645.": "10.5014/ajot.45.6.573c",
  "Lord SR, Dayhew J. Visual risk factors for falls in older people. J Am Geriatr Soc. 2001;49(5):508-515.": "10.1046/j.1532-5415.2001.49107.x",
  "Wiener WR, Welsh RL, Blasch BB. Foundations of Orientation and Mobility. 3rd ed. New York: AFB Press; 2010.": "10.5070/t412011819",
  "Gillespie LD, Robertson MC, Gillespie WJ, et al. Interventions for preventing falls in older people living in the community. Cochrane Database Syst Rev. 2012;9:CD007146.": "10.1002/14651858.cd007146.pub2",
  "Sloan FA, Wang F. Disparities among older adults in medication adherence: the role of cognitive and visual impairments. Cogn Behav Neurol. 2005;18(4):217-226.": "10.1093/geroni/igab046.1852",
  "Brown CM, Jackson ML. Medication management in low vision: an occupational therapy and low vision clinician collaborative approach. J Vis Impair Blind. 2017;111(5):455-468.": "10.1177/0308022619858940",
  "American Society of Health-System Pharmacists. ASHP statement on the pharmacist's role in the care of patients with disabilities. Am J Health Syst Pharm. 2002;59(12):1201-1205.": "10.1093/ajhp/59.3.282",
  "Sleath B, Blalock SJ, Covert D, et al. The relationship between glaucoma medication adherence, eye drop technique, and visual field defect severity. Ophthalmology. 2011;118(12):2398-2402.": "10.1016/j.ophtha.2011.05.013",
  "American Medical Association. Physician's Guide to Assessing and Counseling Older Drivers. 4th ed. Washington, DC: National Highway Traffic Safety Administration; 2019.": "https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/14358a_olderdriversguidelines_082019_v1a_tag.pdf",
  "Bowers AR, Peli E, Elgin J, et al. On-road driving with bioptic telescopes: does the telescope help? Optom Vis Sci. 2005;82(8):743-753.": "10.1167/iovs.04-0271",
  "Owsley C, McGwin G Jr. Vision and driving. Vision Res. 2010;50(23):2348-2361.": "10.1016/j.visres.2010.05.021",
  "Freeman EE, Muñoz B, Turano KA, West SK. Measures of visual function and time to driving cessation in older adults: the Salisbury Eye Evaluation. Invest Ophthalmol Vis Sci. 2005;46(8):2756-2763.": "10.1167/iovs.05-0934",
  "Teunisse RJ, Cruysberg JR, Hoefnagels WH, et al. Visual hallucinations in psychologically normal people: Charles Bonnet's syndrome. Lancet. 1996;347(9004):794-797.": "10.1016/s0140-6736(96)90869-7",
  "Menon GJ, Rahman I, Menon SJ, Dutton GN. Complex visual hallucinations in the visually impaired: the Charles Bonnet Syndrome. Surv Ophthalmol. 2003;48(1):58-72.": "10.1016/s0039-6257(02)00414-9",
  "ffytche DH. Visual hallucinations and the Charles Bonnet syndrome. Curr Psychiatry Rep. 2005;7(3):168-179.": "10.1007/s11920-005-0050-3",
  "daSilva Morgan K, Webster KE, Shepherd JD, et al. Inhibitory transcranial direct current stimulation (tDCS) for the treatment of Charles Bonnet Syndrome: a randomized controlled trial. Ophthalmic Physiol Opt. 2021;41(4):780-791.": "10.26226/morressier.59a3e8b7d462b8028d89591d",
  "Rovner BW, Casten RJ, Hegel MT, et al. Preventing depression in age-related macular degeneration: a randomized controlled trial. Arch Gen Psychiatry. 2007;64(8):886-892.": "10.1001/archpsyc.64.8.886",
  "Rovner BW, Casten RJ, Hegel MT, et al. Low vision rehabilitation and depression in age-related macular degeneration: a randomized clinical trial. Ophthalmology. 2014;121(11):2204-2211.": "10.1016/j.ophtha.2014.05.002",
  "Brody BL, Roch-Levecq AC, Gamst AC, et al. Self-management of age-related macular degeneration and quality of life: a randomized controlled trial. Arch Ophthalmol. 2002;120(11):1477-1483.": "10.1001/archopht.120.11.1477",
  "van der Aa HP, van Rens GH, Comijs HC, et al. Stepped care for depression and anxiety in visually impaired older adults: a randomized controlled trial. BMJ Open. 2013;3(11):e003723.": "10.1136/bmj.h6127",
  "Baile WF, Buckman R, Lenzi R, et al. SPIKES—A six-step protocol for delivering bad news: application to the patient with cancer. Oncologist. 2000;5(4):302-311.": "10.1634/theoncologist.5-4-302",
  "Liénard A, Merckaert I, Libert Y, et al. Is it possible to improve residents breaking bad news skills? A randomised study assessing the efficacy of a 38-h communication skills training program. Br J Cancer. 2010;103(2):171-177.": "10.1038/sj.bjc.6605749",
  "Fletcher DC. Low vision rehabilitation: the art of compassionate communication and functional restoration. Ophthalmol Clin North Am. 2003;16(2):147-157.": "10.1001/archopht.1994.01090240026018",
  "Mogk LG. Vision rehabilitation: the critical next step in patient care. JAMA Ophthalmol. 2013;131(11):1481-1482.": "10.1001/jamaophthalmol.2013.4686",
  "Warren M. Occupational therapy's role in low vision rehabilitation: a historical perspective and future trends. Am J Occup Ther. 1995;49(9):857-865.": "10.5014/ajot.49.9.857",
  "Center for Medicare and Medicaid Services (CMS). Medicare Benefit Policy Manual: Chapter 15 - Covered Medical and Other Health Services (Section 220 - Physical Therapy, Occupational Therapy, and Speech-Language Pathology Services).": "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/bp102c15.pdf",
  "Markowitz SN. Principles of modern low vision rehabilitation. Can J Ophthalmol. 2006;41(3):289-312.": "10.1139/i06-027",
  "Stelmack JA, Tang XC, Wei Y, et al. Outcomes of the Veterans Affairs Low Vision Intervention Trial II (LOVIT II): a randomized clinical trial. JAMA Ophthalmol. 2017;135(2):96-104.": "10.1001/jamaophthalmol.2016.4742"
}



def get_cluster_articles(art, all_articles):
    return sorted(
        [candidate for candidate in all_articles
         if candidate['folder'] == art['folder'] and candidate['cluster'] == art['cluster']],
        key=lambda candidate: candidate['order'],
    )


def render_prev_next_navigation(art, all_articles):
    cluster_articles = get_cluster_articles(art, all_articles)
    current_index = next(
        index for index, candidate in enumerate(cluster_articles)
        if candidate['new_filename'] == art['new_filename']
    )
    neighbors = (
        ('prev', '上一篇', 'arrow_back', cluster_articles[current_index - 1] if current_index > 0 else None,
         '已是本系列首篇'),
        ('next', '下一篇', 'arrow_forward',
         cluster_articles[current_index + 1] if current_index + 1 < len(cluster_articles) else None,
         '已是本系列末篇'),
    )
    cards = []
    for direction, label, icon, article, boundary in neighbors:
        card_class = f'prev-next-card prev-next-card--{direction}'
        if article:
            href = f"/content/{article['folder']}/{quote(article['new_filename'])}"
            opening = f'<a class="{card_class}" href="{href}" rel="{direction}">'
            title = article['title']
            closing = '</a>'
        else:
            opening = f'<div class="{card_class} is-disabled" aria-disabled="true">'
            title = boundary
            closing = '</div>'
        cards.append(
            f'{opening}<span class="prev-next-label">'
            f'<span class="material-symbols-outlined" aria-hidden="true">{icon}</span>{label}</span>'
            f'<span class="prev-next-title">{escape(title)}</span>{closing}'
        )
    return '<nav class="prev-next-nav" aria-label="系列文章導覽">' + ''.join(cards) + '</nav>'


def sync_article_source(soup, art, all_articles=None):
    """Keep the published article, metadata, and navigation in sync."""
    if not art:
        return

    title = normalize_terminology(art.get('title', ''))
    summary = normalize_terminology(art.get('summary', ''))
    canonical_url = f"{SITE_BASE_URL}/content/{art['folder']}/{quote(art['new_filename'])}"
    image_url = art.get('img_src') or f"{SITE_BASE_URL}/icons/icon.svg"

    h1 = soup.find('h1', class_='article-title') or soup.find('h1')
    if h1 and title:
        h1.clear()
        h1.append(title)

    lead_box = soup.find('div', class_='article-lead-box')
    lead_p = lead_box.find('p') if lead_box else None
    if lead_p and summary:
        lead_p.clear()
        lead_p.append(summary)

    body = soup.find('div', class_='article-body-content')
    raw_body = art.get('raw_body', '')
    if body and raw_body:
        fragment = BeautifulSoup(raw_body, 'html.parser')
        body.clear()
        for child in list(fragment.contents):
            body.append(child)

    references = soup.select('.article-references ol > li')
    for index, citation in enumerate(art.get('citations', [])):
        if index >= len(references):
            break
        references[index]['id'] = f"ref-{index + 1}"
        link = references[index].find('a')
        if link is None or not citation.get('url'):
            continue
        link['href'] = citation['url']
        link['target'] = '_blank'
        link['rel'] = ['noopener', 'noreferrer']
        link.clear()
        link.append(citation['text'])

    title_tag = soup.find('title')
    if title_tag and title:
        title_tag.string = f"{title}｜蔡泓恩 職能治療師"

    curr_bc = soup.find('span', class_='breadcrumb-current')
    if curr_bc and title:
        curr_bc.clear()
        curr_bc.append(title)

    tag_badges = soup.find('div', class_='article-tag-badges')
    if tag_badges and art.get('tags'):
        tag_badges.clear()
        for t in art['tags']:
            badge = soup.new_tag('a', attrs={
                'class': 'article-badge',
                'href': f"{SITE_BASE_URL}/blog?tag={quote(t)}"
            })
            badge.string = t
            tag_badges.append(badge)

    lead_box_title = soup.find('div', class_='article-lead-box-title')
    if lead_box_title:
        lead_box_title.clear()
        lead_box_title.append("本篇要回答的決策")

    meta_row = soup.find('div', class_='article-meta-row')
    if meta_row:
        time_tag = meta_row.find('time')
        if not time_tag:
            date_str = (art.get('date_modified') or art.get('date_published', '2026-09-13'))[:10]
            meta_row.clear()
            author_span = soup.new_tag('span', attrs={'class': 'article-meta-item'})
            author_span.string = "蔡泓恩 職能治療師"
            time_elem = soup.new_tag('time', attrs={'datetime': art.get('date_modified') or art.get('date_published', '2026-09-13T08:00:00+08:00')})
            time_elem.string = f"更新：{date_str}"
            read_span = soup.new_tag('span', attrs={'class': 'article-meta-item'})
            read_span.string = art.get('read_time', '約 8 分鐘閱讀')
            meta_row.append(author_span)
            meta_row.append(time_elem)
            meta_row.append(read_span)

    author_note = soup.find('footer', class_='article-author-note')
    if author_note:
        p = author_note.find('p')
        if p:
            p.string = "作者：蔡泓恩 職能治療師。本文為專業教育與證據整理；個別處置仍需完整評估、當事人參與及適當跨專業合作。"

    keywords = ','.join(art.get('tags', []))
    meta_values = [
        ({'name': 'description'}, summary),
        ({'name': 'keywords'}, keywords),
        ({'property': 'og:title'}, title),
        ({'property': 'og:description'}, summary),
        ({'property': 'og:url'}, canonical_url),
        ({'property': 'og:image'}, image_url),
        ({'property': 'og:section'}, art.get('cat_name', '專業文章')),
        ({'property': 'article:published_time'}, art.get('date_published', '')),
        ({'property': 'article:modified_time'}, art.get('date_modified', '')),
        ({'property': 'article:section'}, art.get('cat_name', '專業文章')),
        ({'name': 'twitter:title'}, title),
        ({'name': 'twitter:description'}, summary),
        ({'name': 'twitter:image'}, image_url),
    ]
    for attrs, value in meta_values:
        if not value:
            continue
        tag = soup.find('meta', attrs=attrs)
        if tag is None and soup.head:
            tag = soup.new_tag('meta')
            for key, attr_value in attrs.items():
                tag[key] = attr_value
            soup.head.append(tag)
        if tag is not None:
            tag['content'] = value

    canonical = soup.find('link', rel='canonical')
    if canonical is not None:
        canonical['href'] = canonical_url

    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        nodes = data.get('@graph', []) if isinstance(data, dict) else []
        nodes = nodes or [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            types = node.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if 'Article' in types:
                node['@id'] = f"{canonical_url}#article"
                node['url'] = canonical_url
                node['mainEntityOfPage'] = canonical_url
                node['headline'] = title
                node['description'] = summary
                node['image'] = [image_url]
                node['datePublished'] = art.get('date_published', node.get('datePublished'))
                node['dateModified'] = art.get('date_modified', node.get('dateModified'))
                node['articleSection'] = art.get('cat_name', '專業文章')
                node['keywords'] = art.get('tags', [])
                node['citation'] = [
                    {
                        '@type': 'CreativeWork',
                        'name': citation['text'],
                        'url': citation['url'],
                    }
                    for citation in art.get('citations', [])
                    if citation.get('text') and citation.get('url')
                ]
            elif 'BreadcrumbList' in types:
                for item in node.get('itemListElement', []):
                    if item.get('position') == 3:
                        item['name'] = title
                        item['item'] = canonical_url
        script.string = json.dumps(data, ensure_ascii=False)

    if all_articles:
        navigation = BeautifulSoup(render_prev_next_navigation(art, all_articles), 'html.parser').nav
        existing = soup.select('.prev-next-nav')
        if existing:
            existing[0].replace_with(navigation)
            for duplicate in existing[1:]:
                duplicate.decompose()
        else:
            container = soup.find(class_='article-container')
            if container:
                bottom_actions = container.select_one('.article-trainerhub-cta, .article-bottom-actions')
                if bottom_actions:
                    bottom_actions.insert_before(navigation)
                else:
                    container.append(navigation)


def normalize_terminology(text):
    """Normalize clinical and assistive technology terminology according to content/README.md."""
    if not text:
        return text
    text = text.replace('電子助視器', '電子擴視機')
    text = text.replace('智慧頭顯', '頭戴式顯示器')
    text = text.replace('頭顯', '頭戴式顯示器')
    text = text.replace('低視力', '低視能')
    text = text.replace('黃斑旁預覽視窗', '中央凹旁預視視窗')
    return text

def extract_article_schema(soup):
    """Return the Article node from either a flat or @graph JSON-LD block."""
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        nodes = data.get('@graph', []) if isinstance(data, dict) else []
        nodes = nodes or [data]
        for node in nodes:
            types = node.get('@type', []) if isinstance(node, dict) else []
            if isinstance(types, str):
                types = [types]
            if 'Article' in types:
                return node
    return {}

def clean_inner_body(soup_body):
    """Clean up inline styles from body elements to make them adapt to light/dark themes."""
    for table in soup_body.find_all('table'):
        table['class'] = ['article-table']
        table.attrs.pop('style', None)
        if not table.parent or 'table-wrapper' not in table.parent.get('class', []):
            wrapper = soup_body.new_tag('div', **{'class': 'table-wrapper'})
            table.wrap(wrapper)
            
    for th in soup_body.find_all('th'):
        th.attrs.pop('style', None)
    for td in soup_body.find_all('td'):
        td.attrs.pop('style', None)
    for tr in soup_body.find_all('tr'):
        tr.attrs.pop('style', None)
        
    for h in soup_body.find_all(['h1', 'h2', 'h3', 'h4']):
        h.attrs.pop('style', None)
        
    for p in soup_body.find_all('p'):
        p.attrs.pop('style', None)
    for ul in soup_body.find_all(['ul', 'ol', 'li']):
        ul.attrs.pop('style', None)
        
    for div in soup_body.find_all('div'):
        style = div.get('style', '').lower()
        if 'fff5f5' in style or 'e53e3e' in style: # warning
            div['class'] = ['callout-box', 'warning']
            div.attrs.pop('style', None)
        elif 'fffaf0' in style or 'dd6b20' in style: # amber warning
            div['class'] = ['callout-box', 'amber']
            div.attrs.pop('style', None)
        elif 'e6f4ea' in style or '137333' in style or 'ebf8ff' in style: # success / info
            div['class'] = ['callout-box', 'success']
            div.attrs.pop('style', None)
        elif 'eff6ff' in style or 'f8fafc' in style or 'f7fafc' in style:
            div['class'] = ['callout-box']
            div.attrs.pop('style', None)
        elif 'ui-monospace' in style or 'monospace' in style or '#0f172a' in style:
            div['class'] = ['code-terminal-block']
            div.attrs.pop('style', None)
            
    for span in soup_body.find_all('span'):
        style = span.get('style', '').lower()
        if 'background' in style:
            text = span.get_text().strip()
            if 'cor 1' in text.lower():
                span['class'] = ['article-badge']
            elif 'cor 3' in text.lower():
                span['class'] = ['article-badge', 'badge-danger']
            span.attrs.pop('style', None)
        elif 'color' in style and ('#2d3748' in style or '#1a202c' in style or '#0f172a' in style):
            span.attrs.pop('style', None)
            
    return str(soup_body)

ARTICLE_TAG_MAP = {
    # DigitalLearning (13 articles)
    "DigitalLearning_001": ["數位學習", "AI應用"],
    "DigitalLearning_002": ["數位學習", "AI應用"],
    "DigitalLearning_003": ["數位學習", "AI應用"],
    "DigitalLearning_004": ["數位學習", "AI應用"],
    "DigitalLearning_005": ["數位學習", "AI應用"],
    "DigitalLearning_006": ["數位學習", "AI應用"],
    "DigitalLearning_007": ["數位學習", "AI應用"],
    "DigitalLearning_008": ["數位學習", "AI應用"],
    "DigitalLearning_009": ["數位學習", "AI應用"],
    "DigitalLearning_010": ["數位學習", "AI應用"],
    "DigitalLearning_011": ["數位學習", "AI應用"],
    "DigitalLearning_012": ["數位學習", "AI應用"],
    "DigitalLearning_013": ["數位學習", "AI應用"],

    # OccupationalTherapy (20 articles)
    "OccupationalTherapy_001": ["中風復健", "動作復健"],
    "OccupationalTherapy_002": ["中風復健", "動作復健"],
    "OccupationalTherapy_003": ["中風復健", "動作復健"],
    "OccupationalTherapy_004": ["中風復健", "動作復健"],
    "OccupationalTherapy_005": ["中風復健", "動作復健"],
    "OccupationalTherapy_006": ["中風復健", "認知復健", "視覺復健"],
    "OccupationalTherapy_007": ["中風復健", "認知復健", "動作復健"],
    "OccupationalTherapy_008": ["中風復健", "動作復健"],
    "OccupationalTherapy_009": ["中風復健", "認知復健"],
    "OccupationalTherapy_010": ["中風復健", "動作復健", "認知復健"],
    "OccupationalTherapy_011": ["中風復健", "視覺復健"],
    "OccupationalTherapy_012": ["中風復健", "視覺復健", "動作復健"],
    "OccupationalTherapy_013": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_014": ["中風復健", "視覺復健"],
    "OccupationalTherapy_015": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_016": ["中風復健", "視覺復健"],
    "OccupationalTherapy_017": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_018": ["中風復健", "視覺復健"],
    "OccupationalTherapy_019": ["中風復健", "視覺復健", "認知復健"],
    "OccupationalTherapy_020": ["中風復健", "動作復健", "視覺復健", "認知復健"],

    # VisualTherapy (20 articles)
    "VisualTherapy_001": ["視覺復健"],
    "VisualTherapy_002": ["視覺復健"],
    "VisualTherapy_003": ["視覺復健", "動作復健"],
    "VisualTherapy_004": ["視覺復健"],
    "VisualTherapy_005": ["視覺復健", "認知復健"],
    "VisualTherapy_006": ["視覺復健"],
    "VisualTherapy_007": ["視覺復健"],
    "VisualTherapy_008": ["視覺復健", "AI應用"],
    "VisualTherapy_009": ["視覺復健", "認知復健"],
    "VisualTherapy_010": ["視覺復健"],
    "VisualTherapy_011": ["視覺復健"],
    "VisualTherapy_012": ["視覺復健", "動作復健"],
    "VisualTherapy_013": ["視覺復健", "動作復健"],
    "VisualTherapy_014": ["視覺復健", "認知復健"],
    "VisualTherapy_015": ["視覺復健", "認知復健"],
    "VisualTherapy_016": ["視覺復健", "認知復健"],
    "VisualTherapy_017": ["視覺復健", "認知復健"],
    "VisualTherapy_018": ["視覺復健"],
    "VisualTherapy_019": ["視覺復健", "中風復健"],
    "VisualTherapy_020": ["視覺復健"]
}

# Additional evidence-note collections. Keep every generated article inside the six approved tags.
ARTICLE_TAG_MAP.update({f"CognitRehab_{i:03d}": ["中風復健", "認知復健"] for i in range(1, 11)})
ARTICLE_TAG_MAP["CognitRehab_006"] = ["中風復健", "認知復健", "視覺復健"]

ARTICLE_TAG_MAP.update({f"DigitLearn_{i:03d}": ["數位學習"] for i in range(1, 29)})
for i in [3, 5, 8, 9, 17]:
    if f"DigitLearn_{i:03d}" in ARTICLE_TAG_MAP:
        ARTICLE_TAG_MAP[f"DigitLearn_{i:03d}"] = ["數位學習", "AI應用"]
for i in range(16, 29):
    if f"DigitLearn_{i:03d}" in ARTICLE_TAG_MAP:
        ARTICLE_TAG_MAP[f"DigitLearn_{i:03d}"] = ["數位學習", "AI應用"]

ARTICLE_TAG_MAP.update({f"MotorRehab_{i:03d}": ["中風復健", "動作復健"] for i in range(1, 17)})
ARTICLE_TAG_MAP["MotorRehab_016"] = ["動作復健", "認知復健"]
ARTICLE_TAG_MAP["MotorRehab_017"] = ["動作復健"]

ARTICLE_TAG_MAP.update({f"VisualRehab_{i:03d}": ["視覺復健"] for i in range(1, 30)})
for i in range(20, 23):
    ARTICLE_TAG_MAP[f"VisualRehab_{i:03d}"].insert(0, "中風復健")
ARTICLE_TAG_MAP["VisualRehab_013"] = ["視覺復健", "動作復健"]
ARTICLE_TAG_MAP["VisualRehab_025"] = ["視覺復健", "AI應用"]
ARTICLE_TAG_MAP["VisualRehab_028"] = ["視覺復健", "動作復健"]
ARTICLE_TAG_MAP["VisualRehab_030"] = ["視覺復健", "動作復健"]

def collect_article_metadata():
    folders = [
        (folder, values[0], values[1], values[2])
        for folder, values in ADDITIONAL_CONTENT_FOLDERS.items()
    ]

    all_articles = []

    for folder, cat_name, cat_badge, cat_slug in folders:
        folder_path = CONTENT_DIR / folder
        conflicted = list(folder_path.glob('*conflicted*'))
        if conflicted:
            raise RuntimeError(f'Cloud sync conflict files require manual resolution: {conflicted}')

        files = sorted([f for f in folder_path.glob('*.html') if '[conflicted' not in f.name])
        for f in files:
            content = f.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            source_schema = extract_article_schema(soup)
            
            if folder == 'DigitalLearning':
                if f.name in DL_MAPPING:
                    new_filename, short_topic, cluster, order, sub_cluster = DL_MAPPING[f.name]
                elif f.name.startswith(('001_', '002_', '003_', '004_', '005_', '006_', '007_', '008_', '009_', '010_', '011_', '012_', '013_')):
                    order = int(f.name[:3])
                    new_filename = f.name
                    short_topic = f.name[4:].replace('.html', '').split('_')[0]
                    cluster = '非工程師的「AI 產品架構思維」12 講專題'
                    sub_cluster = '導讀總綱' if order == 1 else ('基礎認知與軟體架構' if order <= 3 else ('提示工程與知識檢索' if order <= 5 else ('自主智慧體與多Agent協同' if order <= 7 else ('工程防護與資訊安全' if order <= 10 else '評測成本與長期維運'))))
                else:
                    continue
            elif folder in ADDITIONAL_CONTENT_FOLDERS:
                clean_name = re.sub(r'\s*\[conflicted.*?\]', '', f.name)
                if not clean_name[:3].isdigit():
                    continue
                order = int(clean_name[:3])
                new_filename = clean_name
                short_topic = clean_name[4:].removesuffix('.html').split('_')[0]

                if folder == 'DigitLearn':
                    if order <= 7:
                        cluster, sub_cluster = '臨床人員的資工學習路徑', '資訊科學基礎'
                    elif order <= 15:
                        cluster, sub_cluster = 'Excel 與 Python 資料自動化', '資料處理與辦公自動化'
                    else:
                        cluster, sub_cluster = 'AI 產品開發與治理', 'AI 系統實務'
                else:
                    cluster = ADDITIONAL_CONTENT_FOLDERS[folder][1]
                    if folder == 'CognitRehab':
                        sub_cluster = '認知與溝通' if order <= 6 else '心理、轉銜與社會參與'
                    elif folder == 'VisualRehab':
                        if order >= 30:
                            cluster = '周邊前庭低功能與凝視穩定訓練'
                            sub_cluster = '2022 ANPT 前庭復健臨床實務指引'
                        elif order >= 23:
                            cluster = '低視能復健指引與實踐專題'
                            sub_cluster = 'Whittaker 臨床指引與實踐'
                        else:
                            sub_cluster = '低視能評估與介入' if order <= 19 else '腦傷與中風後視覺復健'
                    else:
                        if order >= 17:
                            cluster = '圍手術期與術後加速康復專題'
                            sub_cluster = '術後加速康復 ERAS 實證指引'
                        else:
                            sub_cluster = '工作復能與失能預防' if order == 16 else '動作、移動與日常活動'
            else:
                if f.name[:3].isdigit():
                    order = int(f.name[:3])
                    new_filename = f.name
                    short_topic = f.name[4:].replace('.html', '').split('_')[0]
                else:
                    order = int(f.name[:2])
                    new_filename = f'{order:03d}_{f.name[3:]}'
                    short_topic = f.name[3:].replace('.html', '').split('_')[0]
                    
                if folder == 'OccupationalTherapy':
                    if order <= 10:
                        cluster = '中風神經復健與全人照護'
                        sub_cluster = '急性期與動作功能重建'
                    else:
                        cluster = '中風後神經視覺復健'
                        sub_cluster = '神經視覺功能重建與代償'
                else: # VisualTherapy
                    if order <= 9:
                        cluster = '低視能臨床評估與光學處方科學'
                        sub_cluster = '功能評估與輔具處方'
                    elif order <= 14:
                        cluster = '環境人因工程、安全自理與防跌防護'
                        sub_cluster = '環境改造與居家自理'
                    else:
                        cluster = '特殊病徵、心理調適與跨專業協同'
                        sub_cluster = '跨專業全人照護'

            # Normalize terminology across filename, topic, cluster
            new_filename = normalize_terminology(new_filename)
            short_topic = normalize_terminology(short_topic)
            cluster = normalize_terminology(cluster)
            sub_cluster = normalize_terminology(sub_cluster)

            art_key = f"{folder}_{order:03d}"
            editorial_copy = HUMANIZED_ARTICLE_COPY.get(art_key)

            h1 = soup.find('h1')
            title = h1.get_text().strip() if h1 else ''
            if not title and soup.title:
                title = soup.title.get_text().strip()
            title = normalize_terminology(title)
            if editorial_copy:
                title = normalize_terminology(editorial_copy['title'])
                
            # Publish dates interleave the series; VT_020 stays the latest.
            header = soup.find('header')
            spans = [s.get_text().strip() for s in header.find_all('span')] if header else []
            
            html_tags = [a.get_text().strip() for a in header.select('.article-tag-badges a')] if header else []
            tags = html_tags or ARTICLE_TAG_MAP.get(art_key, [cat_name])
            if folder in ADDITIONAL_CONTENT_FOLDERS:
                date_published = source_schema.get('datePublished') or source_schema.get('dateModified') or '2026-09-12'
            else:
                date_published = ARTICLE_PUBLISH_SCHEDULE.get(art_key, '2026-01-01T08:00:00+08:00')
            date_modified = source_schema.get('dateModified') or date_published
            if len(date_published) == 10:
                date_published += 'T08:00:00+08:00'
            if len(date_modified) == 10:
                date_modified += 'T08:00:00+08:00'
                
            read_time = '約 5 分鐘閱讀'
            for s in spans:
                m = re.search(r'([0-9]+)\s*分鐘', s)
                if m:
                    read_time = f'約 {m.group(1)} 分鐘閱讀'
                    break
                    
            fig = soup.find('figure')
            img = fig.find('img') if fig else soup.find('img')
            caption = fig.find('figcaption').get_text().strip() if fig and fig.find('figcaption') else ''
            if not caption and img and img.get('alt'):
                caption = img.get('alt')
            caption = normalize_terminology(caption)
                
            if folder == 'OccupationalTherapy' and order in OT_IMAGES:
                img_src = OT_IMAGES[order]
            elif folder == 'VisualTherapy' and order in VT_IMAGES:
                img_src = VT_IMAGES[order]
            else:
                img_src = img['src'] if img and img.has_attr('src') else ''
                if 'files.catbox.moe' in img_src:
                    img_src = 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80'
            if folder in ADDITIONAL_CONTENT_FOLDERS and not (img_src.startswith('https://images.unsplash.com/') or img_src.startswith('https://plus.unsplash.com/')):
                if folder == 'DigitLearn':
                    img_src = DL_IMAGES[(order - 1) % len(DL_IMAGES)]
                elif folder == 'VisualRehab':
                    img_src = VT_IMAGES[(order - 1) % len(VT_IMAGES) + 1]
                else:
                    img_src = OT_IMAGES[(order - 1) % len(OT_IMAGES) + 1]

            summary = ''
            lead_box = soup.find('div', class_='article-lead-box')
            if lead_box and lead_box.find('p'):
                summary = lead_box.find('p').get_text().strip()
            else:
                header_p = header.find('p') if header else None
                if header_p and len(header_p.get_text().strip()) > 20:
                    summary = header_p.get_text().strip()
                else:
                    for div in soup.find_all('div'):
                        style = div.get('style', '')
                        if 'border-left' in style and ('f7fafc' in style or 'f8fafc' in style or 'eff6ff' in style):
                            p_in_div = div.find('p')
                            if p_in_div:
                                summary = p_in_div.get_text().strip()
                            else:
                                summary = div.get_text().strip()
                            break
            if not summary:
                first_p = soup.find('p')
                summary = first_p.get_text().strip() if first_p else title
            summary = normalize_terminology(summary)
            summary = re.sub(r'\s*\[\d+\]', '', summary)
            if editorial_copy:
                summary = normalize_terminology(editorial_copy['summary'])
                
            ref_sec = soup.find(['section', 'footer'], class_=lambda c: c and 'reference' in c) or soup.find('footer') or soup.find('section', {'aria-label': lambda x: x and '參考' in x})
            citations = []
            if ref_sec:
                for li in ref_sec.find_all('li'):
                    a = li.find('a')
                    cit_text = li.get_text().strip()
                    cit_url = a['href'].strip() if a and a.has_attr('href') else ''

                    if cit_url.startswith('../OriginalSources/DigitalLearning/'):
                        cit_url = cit_url.replace('../OriginalSources/DigitalLearning/', '../DigitalLearning/', 1)
                    elif cit_url.startswith('../OriginalSources/'):
                        cit_url = ''
                        cit_text = cit_text.removeprefix('本資料夾收錄之 ')
                    
                    for old_doi, (new_doi, new_text) in BROKEN_DOI_FIXES.items():
                        if old_doi in cit_url or old_doi in cit_text:
                            cit_url = new_doi
                            if new_text:
                                cit_text = new_text
                                
                    # If cit_url is empty (e.g. VisualTherapy), check VT_DOI_CACHE
                    if not cit_url and cit_text in VT_DOI_CACHE:
                        val = VT_DOI_CACHE[cit_text]
                        if val:
                            cit_url = val if val.startswith('http') else f'https://doi.org/{val}'
                            
                    citation = {'text': normalize_terminology(cit_text), 'url': cit_url}
                    if citation not in citations:
                        citations.append(citation)
                    
            if folder == 'DigitalLearning':
                news_article = soup.find('div', class_='news-article')
                if news_article:
                    na_copy = BeautifulSoup(str(news_article), 'html.parser')
                    if na_copy.find('header'):
                        na_copy.find('header').decompose()
                    if na_copy.find('figure'):
                        na_copy.find('figure').decompose()
                    if na_copy.find('footer'):
                        na_copy.find('footer').decompose()
                    if na_copy.find('style'):
                        na_copy.find('style').decompose()
                    body_html = str(na_copy)
                else:
                    body_soup = BeautifulSoup(content, 'html.parser')
                    if body_soup.find('header'):
                        body_soup.find('header').decompose()
                    if body_soup.find('figure'):
                        body_soup.find('figure').decompose()
                    if body_soup.find('footer'):
                        body_soup.find('footer').decompose()
                    if body_soup.find('style'):
                        body_soup.find('style').decompose()
                    body_html = str(body_soup)
            elif folder in ADDITIONAL_CONTENT_FOLDERS:
                body_div = soup.find('div', class_='article-body-content')
                if body_div:
                    body_copy = BeautifulSoup(str(body_div), 'html.parser')
                    for references in body_copy.find_all(class_='article-references'):
                        references.decompose()
                    body_html = body_copy.find('div', class_='article-body-content').decode_contents()
                else:
                    body_html = ''
            else: # OccupationalTherapy / VisualTherapy
                post_content_div = soup.find('div', class_='post-content')
                summary_box = soup.find('div', style=lambda s: s and 'ebf8ff' in s)
                body_parts = []
                if post_content_div:
                    body_parts.append(str(post_content_div))
                if summary_box:
                    body_parts.append(str(summary_box))
                body_html = '\n'.join(body_parts)
                
            if editorial_copy:
                body_html = editorial_copy['body']

            # Replace broken DOIs in body_html
            for old_doi, (new_doi, _) in BROKEN_DOI_FIXES.items():
                if old_doi in body_html:
                    body_html = body_html.replace(old_doi, new_doi)
            body_html = body_html.replace('https://doi.org/https://doi.org/', 'https://doi.org/')
            body_html = normalize_terminology(body_html)
                    
            all_articles.append({
                'folder': folder,
                'cat_name': cat_name,
                'cat_badge': cat_badge,
                'cat_slug': cat_slug,
                'cluster': cluster,
                'sub_cluster': sub_cluster,
                'order': order,
                'old_filename': f.name,
                'new_filename': new_filename,
                'title': title,
                'short_topic': short_topic,
                'tags': tags,
                'read_time': read_time,
                'img_src': img_src,
                'caption': caption,
                'summary': summary,
                'citations': citations,
                'date_published': date_published,
                'date_modified': date_modified,
                'raw_body': body_html
            })
            
    return all_articles

def build_article_html(art, all_articles):
    folder = art['folder']
    cat_name = art['cat_name']
    cluster_name = art['cluster']
    new_filename = art['new_filename']
    title = art['title']
    summary = art['summary']
    clean_desc = re.sub(r'\s+', ' ', summary).strip().replace('"', '&quot;')[:200]
    keywords_str = ', '.join(art['tags'])
    canonical_url = f"{SITE_BASE_URL}/content/{folder}/{quote(new_filename)}"
    web_page_path = f"/content/{folder}/{new_filename}"
    
    cluster_articles = get_cluster_articles(art, all_articles)
    
    schema_type = "TechArticle" if folder in ("DigitalLearning", "DigitLearn") else "MedicalScholarlyArticle"
    citations_json = [c['text'] for c in art['citations'] if c['text']]
    
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": [schema_type, "Article"],
                "@id": f"{canonical_url}#article",
                "isPartOf": {
                    "@type": "WebPage",
                    "@id": canonical_url
                },
                "headline": title,
                "description": clean_desc,
                "image": art['img_src'] if art['img_src'] else f"{SITE_BASE_URL}/icons/icon.svg",
                "datePublished": art['date_published'],
                "dateModified": art['date_modified'],
                "inLanguage": "zh-TW",
                "mainEntityOfPage": canonical_url,
                "author": {
                    "@type": "Person",
                    "name": "蔡泓恩",
                    "alternateName": "Hung-En (Ian) Tsai",
                    "jobTitle": "職能治療師",
                    "url": f"{SITE_BASE_URL}/",
                    "sameAs": [
                        "https://github.com/ian030590",
                        "https://trainerhub.cc"
                    ],
                    "knowsAbout": ["職能治療", "神經復健", "視覺復健", "低視能評估", "數位醫療", "AI系統架構"],
                    "alumniOf": "國立臺灣大學"
                },
                "publisher": {
                    "@type": "Person",
                    "name": "蔡泓恩",
                    "url": f"{SITE_BASE_URL}/"
                },
                "articleSection": cat_name,
                "keywords": art['tags'],
                "citation": citations_json
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首頁",
                        "item": f"{SITE_BASE_URL}/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "專業文章",
                        "item": f"{SITE_BASE_URL}/blog"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": cat_name,
                        "item": f"{SITE_BASE_URL}/blog?tag={quote(cat_name)}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": title,
                        "item": canonical_url
                    }
                ]
            }
        ]
    }
    
    cluster_items_html = []
    for ca in cluster_articles:
        is_active = (ca['new_filename'] == new_filename)
        active_class = " active" if is_active else ""
        link_target = f"./{ca['new_filename']}"
        current_badge = '<span class="topic-cluster-item-current">目前閱讀中</span>' if is_active else ""
        cluster_items_html.append(f"""
        <li>
          <a href="{link_target}" class="topic-cluster-item{active_class}">
            <span class="topic-cluster-item-num">{ca['order']:03d}</span>
            <span class="topic-cluster-item-title">{ca['title']}</span>
            {current_badge}
          </a>
        </li>""")
        
    cluster_list_rendered = '\n'.join(cluster_items_html)
    
    prev_next_html = render_prev_next_navigation(art, all_articles)

    refs_html = ""
    if art['citations']:
        ref_items = []
        for c in art['citations']:
            if c['url']:
                ref_items.append(f'<li><a href="{c["url"]}" target="_blank" rel="noopener noreferrer">{c["text"]}</a></li>')
            else:
                ref_items.append(f'<li>{c["text"]}</li>')
        refs_html = f"""
        <section class="article-references" aria-label="參考文獻與實證指引">
          <h2>參考文獻與實證指引 (References)</h2>
          <ol>
            {chr(10).join(ref_items)}
          </ol>
        </section>
        """

    cleaned_body = clean_inner_body(BeautifulSoup(art['raw_body'], 'html.parser'))
    
    figure_html = ""
    if art['img_src']:
        figure_html = f"""
        <figure class="article-featured-figure">
          <img src="{art['img_src']}" alt="{title}" class="article-featured-img" loading="lazy" />
          <figcaption class="article-figcaption">{art['caption'] or title}</figcaption>
        </figure>
        """

    date_str = art['date_published'][:10]
    date_html = f'<time datetime="{art["date_published"]}">{date_str}</time>' if folder in ADDITIONAL_CONTENT_FOLDERS else date_str
    
    if folder == 'OccupationalTherapy':
        evidence_note = '2026 AHA/ASA 臨床指引實證'
    elif folder == 'VisualRehab' and art['order'] >= 30:
        evidence_note = '2022 ANPT 前庭復健臨床實務指引'
    elif folder == 'VisualTherapy' or (folder == 'VisualRehab' and art['order'] <= 19):
        evidence_note = '2023 AAO PPP 臨床指引實證'
    elif folder in ('DigitalLearning', 'DigitLearn'):
        evidence_note = 'AI 系統架構與工程實踐'
    elif folder == 'MotorRehab' and art['order'] == 16:
        evidence_note = '2026 ACOEM 臨床實證指引'
    elif folder == 'MotorRehab' and art['order'] >= 17:
        evidence_note = '2019 ERAS 國際實證指引'
    else:
        evidence_note = '2026 AHA/ASA 臨床指引實證'

    tag_badges_html = '\n'.join([
        f'              <a href="/blog?tag={quote(t)}" class="article-badge" title="查看「{t}」相關文章">{t}</a>'
        for t in art['tags']
    ])

    full_html = f"""<!doctype html>
<html lang="zh-TW">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{title} | 蔡泓恩 職能治療師</title>
    <meta name="description" content="{clean_desc}" />
    <meta name="keywords" content="{keywords_str}" />
    <meta name="author" content="蔡泓恩 職能治療師" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{canonical_url}" />

    <!-- Open Graph / Social Media -->
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="zh_TW" />
    <meta property="og:site_name" content="蔡泓恩 | 職能治療師" />
    <meta property="og:title" content="{title} ｜ 蔡泓恩 職能治療師" />
    <meta property="og:description" content="{clean_desc}" />
    <meta property="og:url" content="{canonical_url}" />
    <meta property="og:image" content="{art['img_src'] or f'{SITE_BASE_URL}/icons/icon.svg'}" />
    <meta property="article:published_time" content="{art['date_published']}" />
    <meta property="article:modified_time" content="{art['date_modified']}" />
    <meta property="article:author" content="{SITE_BASE_URL}/" />
    <meta property="article:section" content="{cat_name}" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title} ｜ 蔡泓恩 職能治療師" />
    <meta name="twitter:description" content="{clean_desc}" />
    <meta name="twitter:image" content="{art['img_src'] or f'{SITE_BASE_URL}/icons/icon.svg'}" />

    <!-- Favicon & Stylesheet -->
    <link rel="icon" type="image/svg+xml" href="../../icons/icon.svg" />
    <link rel="icon" type="image/png" sizes="32x32" href="../../icons/favicon-32x32.png" />
    <link rel="icon" type="image/png" sizes="16x16" href="../../icons/favicon-16x16.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="../../icons/apple-touch-icon.png" />
    <link rel="stylesheet" href="../../css/style.css" />

    <!-- Schema.org Article JSON-LD (E-E-A-T) -->
    <script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
    </script>
  </head>
  <body>
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="/">
          <img src="../../icons/logo.png" alt="蔡泓恩 職能治療師 Logo" class="brand-logo" width="36" height="36" />
          <span>蔡泓恩 | 職能治療師</span>
        </a>
        <nav class="nav-links" aria-label="主要導覽">
          <a class="nav-link" href="/">首頁</a>
          <a class="nav-link" href="/projects">開源專案</a>
          <a class="nav-link active" href="/blog" aria-current="page">專業文章</a>
          <a class="nav-link" href="/contact">聯絡我</a>
          <a class="nav-link" href="/sponsor">贊助我</a>
        </nav>
        <button
          class="theme-toggle"
          aria-label="切換深色模式"
          title="切換深色模式"
        >
          <span class="material-symbols-outlined icon-dark" aria-hidden="true">dark_mode</span>
          <span class="material-symbols-outlined icon-light" aria-hidden="true" style="display: none;">light_mode</span>
        </button>
        <a class="nav-cta" href="mailto:rainbowh9490@gmail.com">聯絡我</a>
        <button
          class="menu-button"
          aria-label="開啟選單"
          aria-expanded="false"
        >
          <span
            class="animate-icon animate-icon--menu"
            data-animate-icon="menu"
            aria-hidden="true"
          ></span>
        </button>
      </div>
      <div class="mobile-panel">
        <a href="/">首頁</a>
        <a href="/projects">開源專案</a>
        <a href="/blog" aria-current="page">專業文章</a>
        <a href="/contact">聯絡我</a>
        <a href="/sponsor">贊助我</a>
      </div>
    </header>

    <main class="page-main article-page-layout">
      <div class="container">
        <!-- Breadcrumb Navigation -->
        <nav class="breadcrumb-trail" aria-label="文章路徑導覽">
          <a href="/">首頁</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <a href="/blog">專業文章</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <a href="/blog?tag={quote(cat_name)}">{cat_name}</a>
          <span class="breadcrumb-separator" aria-hidden="true">/</span>
          <span class="breadcrumb-current" aria-current="page">{title}</span>
        </nav>

        <article class="article-container">
          <!-- Article Header -->
          <header class="article-detail-header">
            <div class="article-tag-badges">
{tag_badges_html}
            </div>
            <h1 class="article-title">{title}</h1>
            <div class="article-meta-row">
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">person</span>
                蔡泓恩 職能治療師
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">calendar_today</span>
                {date_html}
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">schedule</span>
                {art['read_time']}
              </span>
              <span class="article-meta-item">
                <span class="material-symbols-outlined" aria-hidden="true">verified</span>
                {evidence_note}
              </span>
            </div>
          </header>

          <!-- Featured Banner Image -->
          {figure_html}

          <!-- Executive Summary Callout Box -->
          <div class="article-lead-box">
            <div class="article-lead-box-title">
              <span class="material-symbols-outlined" aria-hidden="true">lightbulb</span>
              專題重點摘要與核心洞察
            </div>
            <p>{summary}</p>
          </div>

          <!-- Main Body Content -->
          <div class="article-body-content">
            {cleaned_body}
          </div>

          <!-- Scientific References Section -->
          {refs_html}


          <!-- Topic Cluster Series Navigation -->
          <nav class="topic-cluster-nav" aria-label="同系列主題專題叢集">
            <div class="topic-cluster-header">
              <div class="topic-cluster-title">
                <span class="material-symbols-outlined" aria-hidden="true">auto_stories</span>
                【主題叢集】{cluster_name}
              </div>
              <div class="topic-cluster-progress">
                第 {art['order']:03d} 篇 / 全 {len(cluster_articles)} 篇
              </div>
            </div>
            <ul class="topic-cluster-list">
              {cluster_list_rendered}
            </ul>
          </nav>

          <!-- Prev & Next Article Navigation -->
          {prev_next_html}

          <!-- TrainerHub CTA & Back to Blog Navigation -->
          <div class="article-trainerhub-cta">
            <div class="trainerhub-cta-card">
              <div class="trainerhub-cta-badge">
                <span class="material-symbols-outlined" aria-hidden="true">neurology</span>
                <span>居家自主復健實踐</span>
              </div>
              <h3 class="trainerhub-cta-title">將臨床復健實證融入日常生活：TrainerHub 居家訓練網</h3>
              <p class="trainerhub-cta-desc">
                專為神經動作、視覺注意力與認知功能設計的互動式數位復能工具。免安裝、隨開隨練，讓中風復健、視野訓練與日常認知練習在家也能持續進行。
              </p>
              <div class="trainerhub-cta-actions">
                <a href="https://trainerhub.cc" class="button-primary trainerhub-cta-btn" target="_blank" rel="noopener" title="前往 TrainerHub 居家復健訓練網">
                  前往 TrainerHub 居家訓練網
                  <span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>
                </a>
              </div>
            </div>
          </div>

          <div class="article-bottom-actions">
            <a href="/blog" class="button-secondary">
              <span class="material-symbols-outlined" aria-hidden="true">arrow_back</span>
              返回所有專業專題列表
            </a>
          </div>
        </article>
      </div>
    </main>

    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <div class="footer-brand">
            <img src="../../icons/logo.png" alt="蔡泓恩 職能治療師 Logo" class="brand-logo footer-logo" width="26" height="26" />
            <span>蔡泓恩 | 職能治療師</span>
          </div>
          <div class="footer-copy">
            © <span data-year></span> Ian Tsai. 保留所有權利。
          </div>
        </div>
        <div class="footer-links">
          <a href="/">首頁</a>
          <a href="/projects">專案</a>
          <a href="/blog">專業文章</a>
          <a href="https://trainerhub.cc" target="_blank" rel="noopener" title="TrainerHub 居家復健訓練網">居家訓練網</a>
          <a href="/contact">聯絡</a>
          <a href="/sponsor">贊助我</a>
        </div>
      </div>
    </footer>

    <script src="../../js/animate-icons.js"></script>
    <script src="../../js/main.js"></script>
  </body>
</html>"""
    return full_html

def article_public_url(art):
    """Return the URL Cloudflare Workers static assets serve with 200.

    Workers answer `/x.html` with a redirect to `/x`, and search engines skip
    redirecting URLs in sitemaps and feeds, so these list the final URL.
    """
    stem = art['new_filename'].removesuffix('.html')
    return f"{SITE_BASE_URL}/content/{art['folder']}/{quote(stem)}"


def generate_sitemap(all_articles, output_dir=None):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{SITE_BASE_URL}/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/projects</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/blog</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/contact</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        f'  <url><loc>{SITE_BASE_URL}/sponsor</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>',
    ]
    
    for art in all_articles:
        encoded_url = article_public_url(art)
        lastmod = art['date_modified'][:10]
        lines.append(f'  <url><loc>{encoded_url}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')
        
    lines.append('</urlset>\n')
    sitemap_content = '\n'.join(lines)
    target = Path(output_dir) / 'sitemap.xml' if output_dir else SITEMAP_FILE
    target.write_text(sitemap_content, encoding='utf-8')
    print(f'Sitemap written to {target} ({len(all_articles) + 5} URLs)')

def generate_rss(all_articles, output_dir=None):
    sorted_articles = sorted(all_articles, key=lambda art: art['date_published'], reverse=True)
    rss_items = []
    for art in sorted_articles:
        encoded_url = article_public_url(art)
        try:
            dt = datetime.fromisoformat(art['date_published'])
            pub_date_str = dt.strftime('%a, %d %b %Y %H:%M:%S +0800')
        except Exception:
            pub_date_str = art['date_published']
        title_esc = escape(art['title'])
        summary_esc = escape(art['summary'])
        categories = '\n'.join([f'        <category>{escape(t)}</category>' for t in art['tags']])
        rss_items.append(f"""    <item>
      <title>{title_esc}</title>
      <link>{encoded_url}</link>
      <guid isPermaLink="true">{encoded_url}</guid>
      <pubDate>{pub_date_str}</pubDate>
      <description>{summary_esc}</description>
      <author>rainbowh9490@gmail.com (蔡泓恩 職能治療師)</author>
{categories}
    </item>""")

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>蔡泓恩 | 職能治療師 - 專業文章與專題</title>
    <link>{SITE_BASE_URL}/blog</link>
    <description>蔡泓恩職能治療師的個人專業知識庫與專題文章，專注於中風神經復健、視覺復健、認知與動作復健、AI與數位醫療應用。</description>
    <language>zh-TW</language>
    <atom:link href="{SITE_BASE_URL}/rss.xml" rel="self" type="application/rss+xml" />
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
    rss_file = Path(output_dir or BASE_DIR) / 'rss.xml'
    rss_file.write_text(rss_content, encoding='utf-8')
    print(f'RSS feed written to {rss_file} ({len(sorted_articles)} items)')

def generate_articles_data(all_articles, output_dir=None):
    catalog = []
    for art in all_articles:
        catalog.append({
            'id': f"{art['folder']}_{art['order']:03d}",
            'title': art['title'],
            'lead': art['summary'][:160] + ('...' if len(art['summary']) > 160 else ''),
            'imageUrl': art['img_src'],
            'tags': art['tags'],
            'dateString': art['date_published'][:10],
            'readTime': art['read_time'],
            'link': f"/content/{art['folder']}/{art['new_filename']}",
            'sourceName': art['cat_name'],
            'category': art['cat_name'],
            'cluster': art['cluster'],
            'subCluster': art['sub_cluster'],
            'order': art['order'],
            'folder': art['folder'],
            'filename': art['new_filename']
        })
        
    js_code = f"""// Generated static articles catalog (No Blogger dependencies)
window.__STATIC_ARTICLES__ = {json.dumps(catalog, ensure_ascii=False, indent=2)};
"""
    target = Path(output_dir) / 'js' / 'articles-data.js' if output_dir else ARTICLES_DATA_FILE
    target.write_text(js_code, encoding='utf-8')
    print(f'Articles data written to {target} ({len(catalog)} articles)')
    return catalog

def validate_article_navigation(soup, art, all_articles):
    navigation = soup.select('.prev-next-nav')
    expected = BeautifulSoup(render_prev_next_navigation(art, all_articles), 'html.parser').nav
    if len(navigation) != 1 or navigation[0] != expected:
        raise RuntimeError(f"Inconsistent series navigation: {art['folder']}/{art['new_filename']}")


def validate_internal_link(source_file, href, page_soups):
    source_url = f"{SITE_BASE_URL}/{source_file.relative_to(BASE_DIR).as_posix()}"
    url = urllib.parse.urlsplit(urllib.parse.urljoin(source_url, href))
    if url.scheme not in ('http', 'https') or url.netloc != urllib.parse.urlsplit(SITE_BASE_URL).netloc:
        return None

    target = BASE_DIR / unquote(url.path).lstrip('/')
    if target.is_dir():
        target /= 'index.html'
    elif not target.suffix:
        target = target.with_suffix('.html')
    if not target.is_file():
        raise RuntimeError(f'Broken internal link in {source_file.relative_to(BASE_DIR)}: {href}')

    if url.fragment and target.suffix == '.html':
        if target not in page_soups:
            page_soups[target] = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
        target_soup = page_soups[target]
        fragment = unquote(url.fragment)
        if not (target_soup.find(id=fragment) or target_soup.find('a', attrs={'name': fragment})):
            raise RuntimeError(f'Broken internal fragment in {source_file.relative_to(BASE_DIR)}: {href}')
    return target


def validate_generated_site(all_articles):
    """Fail the build when generated navigation, metadata, or approved tags drift."""
    not_found = BASE_DIR / '404.html'
    if not not_found.is_file():
        raise RuntimeError('Cloudflare Workers needs 404.html to avoid serving the home page for missing URLs')
    not_found_soup = BeautifulSoup(not_found.read_text(encoding='utf-8'), 'html.parser')
    robots = not_found_soup.find('meta', attrs={'name': 'robots'})
    if not robots or 'noindex' not in {value.strip().lower() for value in robots.get('content', '').split(',')}:
        raise RuntimeError('The 404 page must be excluded from search indexing')
    approved_tags = {'中風復健', '視覺復健', '動作復健', '認知復健', '數位學習', 'AI應用'}
    additional_articles = [art for art in all_articles if art['folder'] in ADDITIONAL_CONTENT_FOLDERS]
    if len(additional_articles) < 30:
        raise RuntimeError(f'Expected at least 30 additional articles, found {len(additional_articles)}')

    for art in all_articles:
        article_key = f"{art['folder']}_{art['order']:03d}"
        if article_key not in ARTICLE_TAG_MAP or not set(art['tags']).issubset(approved_tags):
            raise RuntimeError(f'Unregistered or invalid tags: {article_key}')
        if art['folder'] not in ADDITIONAL_CONTENT_FOLDERS:
            continue

        article_file = CONTENT_DIR / art['folder'] / art['new_filename']
        soup = BeautifulSoup(article_file.read_text(encoding='utf-8'), 'html.parser')
        validate_article_navigation(soup, art, all_articles)
        stylesheet = soup.find('link', rel=lambda value: value and 'stylesheet' in value)
        schema = extract_article_schema(soup)
        if not stylesheet or stylesheet.get('href') != '../../css/style.css':
            raise RuntimeError(f'Wrong stylesheet path: {article_file}')
        if not schema.get('datePublished') or not schema.get('author'):
            raise RuntimeError(f'Incomplete Article JSON-LD: {article_file}')
        if '"@type": "BreadcrumbList"' not in article_file.read_text(encoding='utf-8'):
            raise RuntimeError(f'Missing BreadcrumbList JSON-LD: {article_file}')
        if not soup.find('header', class_='site-header'):
            raise RuntimeError(f'Missing site-header navbar: {article_file}')
        if not soup.find('a', class_='article-back-link'):
            raise RuntimeError(f'Missing article-back-link: {article_file}')
        if not soup.find('footer', class_='site-footer'):
            raise RuntimeError(f'Missing site-footer: {article_file}')
        if 'main.js' not in article_file.read_text(encoding='utf-8'):
            raise RuntimeError(f'Missing main.js script: {article_file}')
        if '.breadcrumb-trail, .ot-blog-article .prev-next-nav { display: none;' in article_file.read_text(encoding='utf-8'):
            raise RuntimeError(f'Hidden breadcrumb-trail or prev-next-nav in style: {article_file}')
        cluster_size = sum(
            1
            for candidate in additional_articles
            if candidate['folder'] == art['folder']
            and candidate['cluster'] == art['cluster']
        )
        if (
            cluster_size > 1
            and len(soup.select('.prev-next-nav a[href]')) < 1
            and len(soup.select('.topic-cluster-nav a[href]')) < 1
        ):
            raise RuntimeError(f'Missing topic-cluster internal links: {article_file}')
        if soup.find('a', href=lambda href: href and '../OriginalSources/' in href):
            raise RuntimeError(f'Dead OriginalSources link remains: {article_file}')

    # Cloud-sync conflict copies must never reach the build.
    conflicted_files = list(CONTENT_DIR.rglob('*conflicted*'))
    if conflicted_files:
        raise RuntimeError(f"Cloud sync conflict files detected in content/: {[f.name for f in conflicted_files]}")

    for art in additional_articles:
        fname = art['new_filename']
        if ' ' in fname or '[' in fname or ']' in fname:
            raise RuntimeError(f"Article filename contains invalid characters: {fname}")
        article_file = CONTENT_DIR / art['folder'] / fname
        if not article_file.is_file():
            raise RuntimeError(f"Article file does not exist on disk: {article_file}")

    # Covers relative paths, clean routes and fragment targets.
    page_soups = {}
    internal_link_count = 0
    for page in sorted(BASE_DIR.glob('*.html')) + sorted(CONTENT_DIR.rglob('*.html')):
        if page not in page_soups:
            page_soups[page] = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        for link in page_soups[page].select('a[href], link[href], script[src], img[src]'):
            href = link.get('href') if link.has_attr('href') else link['src']
            if validate_internal_link(page, href, page_soups) is not None:
                internal_link_count += 1

    data_content = ARTICLES_DATA_FILE.read_text(encoding='utf-8')
    json_match = re.search(r"window\.__STATIC_ARTICLES__\s*=\s*(\[.*?\]);", data_content, re.DOTALL)
    if not json_match:
        raise RuntimeError("Failed to parse window.__STATIC_ARTICLES__ in articles-data.js")
    articles_data = json.loads(json_match.group(1))
    expected_links = {f"/content/{art['folder']}/{art['new_filename']}" for art in all_articles}
    catalog_links = [item.get('link', '') for item in articles_data]
    if len(catalog_links) != len(expected_links) or set(catalog_links) != expected_links:
        raise RuntimeError('Article catalog has missing, duplicate or unexpected links')
    for item in articles_data:
        validate_internal_link(ARTICLES_DATA_FILE, item['link'], page_soups)
    blog_links = [link['href'] for link in page_soups[BLOG_HTML_FILE].select('.card-link[href]')]
    first_page_links = [
        item['link']
        for item in sorted(articles_data, key=lambda item: item['dateString'], reverse=True)[:15]
    ]
    if blog_links != first_page_links:
        raise RuntimeError('Blog must render the latest 15 articles in catalog order')

    # Sitemap URLs must resolve to real files and include every article.
    sitemap_links = [node.text for node in ET.parse(SITEMAP_FILE).iterfind('.//{*}loc')]
    for link in sitemap_links:
        if validate_internal_link(SITEMAP_FILE, link, page_soups) is None:
            raise RuntimeError(f'Unexpected external URL in sitemap.xml: {link}')
    sitemap_paths = {unquote(urllib.parse.urlsplit(link).path) for link in sitemap_links}
    if any(path.endswith('.html') for path in sitemap_paths):
        raise RuntimeError('Sitemap lists .html URLs that Cloudflare Workers redirect')
    if not {link.removesuffix('.html') for link in expected_links}.issubset(sitemap_paths):
        raise RuntimeError('Sitemap is missing article URLs')
    # No two articles may share an Unsplash photo.
    photo_ids = {}
    for art in additional_articles:
        img_url = art.get('img_src', '')
        m = re.search(r'photo-([a-zA-Z0-9_-]+)', img_url)
        pid = m.group(1) if m else img_url
        if pid in photo_ids:
            raise RuntimeError(
                f"Duplicate article image detected! Photo ID '{pid}' is used in both "
                f"'{photo_ids[pid]}' and '{art['folder']}/{art['new_filename']}'. "
                f"All articles must have unique, verified images."
            )
        photo_ids[pid] = f"{art['folder']}/{art['new_filename']}"

    print(f'Validation passed: {len(additional_articles)} articles have consistent series navigation, CSS, JSON-LD, navbar, back-link, unique images and zero conflict files. Checked {internal_link_count} internal HTML links, {len(catalog_links)} catalog links and {len(sitemap_links)} sitemap URLs, including fragment targets.')

def prepare_astro_assets(all_articles):
    """Stage only public assets; published article source files are immutable."""
    generated = BASE_DIR / '.generated'
    public = generated / 'public'
    if generated.resolve() != BASE_DIR.resolve() / '.generated' or public.is_symlink():
        raise RuntimeError('Generated asset directories must not redirect outside the project')
    if public.exists():
        if public.resolve() != BASE_DIR.resolve() / '.generated' / 'public':
            raise RuntimeError('Refusing to clean assets outside the generated directory')
        shutil.rmtree(public)
    public.mkdir(parents=True)

    for directory in ('assets', 'css', 'icons', 'js'):
        shutil.copytree(BASE_DIR / directory, public / directory,
                        ignore=shutil.ignore_patterns('articles-data.js', '__pycache__', '*.pyc'))
    for filename in ('favicon.ico', 'robots.txt', 'llms.txt', '_headers', '_redirects'):
        shutil.copy2(BASE_DIR / filename, public / filename)

    for art in all_articles:
        if art['old_filename'] != art['new_filename']:
            raise RuntimeError(f"Article filename requires manual correction: {art['old_filename']}")
        relative = Path('content') / art['folder'] / art['new_filename']
        target = public / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BASE_DIR / relative, target)

    catalog = generate_articles_data(all_articles, public)
    (generated / 'articles.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
    generate_sitemap(all_articles, public)
    generate_rss(all_articles, public)
    print(f'Astro assets prepared: {len(all_articles)} articles copied without modification.')


def main():
    parser = argparse.ArgumentParser(description='Prepare immutable article assets for Astro, or validate its output.')
    parser.add_argument('--validate', type=Path, metavar='SITE_DIR', help='Validate the completed Astro build')
    args = parser.parse_args()
    all_articles = collect_article_metadata()
    if args.validate:
        global BASE_DIR, CONTENT_DIR, ARTICLES_DATA_FILE, BLOG_HTML_FILE, SITEMAP_FILE
        source_root = BASE_DIR
        BASE_DIR = args.validate.resolve()
        CONTENT_DIR = BASE_DIR / 'content'
        ARTICLES_DATA_FILE = BASE_DIR / 'js' / 'articles-data.js'
        BLOG_HTML_FILE = BASE_DIR / 'blog.html'
        SITEMAP_FILE = BASE_DIR / 'sitemap.xml'
        for art in all_articles:
            relative = Path('content') / art['folder'] / art['new_filename']
            if (source_root / relative).read_bytes() != (BASE_DIR / relative).read_bytes():
                raise RuntimeError(f'Published article was modified during the build: {relative}')
        validate_generated_site(all_articles)
    else:
        prepare_astro_assets(all_articles)

if __name__ == '__main__':
    main()
>>>>>>> 0fb27403d877d5709ef65c142ca63b6d1e56b269
