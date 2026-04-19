import streamlit as st
import os
import time
import sqlite3
import json
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nailpro_users.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        profile TEXT DEFAULT '{}',
        orders TEXT DEFAULT '[]'
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        nume TEXT NOT NULL,
        curs TEXT NOT NULL,
        rating INTEGER NOT NULL,
        text TEXT NOT NULL,
        data TEXT NOT NULL
    )""")
    conn.commit()
    return conn

def db_add_review(email, nume, curs, rating, text):
    conn = get_db()
    conn.execute("INSERT INTO reviews (email,nume,curs,rating,text,data) VALUES (?,?,?,?,?,?)",
                 (email, nume, curs, rating, text, datetime.now().strftime("%d.%m.%Y")))
    conn.commit()
    conn.close()

def db_get_reviews():
    conn = get_db()
    rows = conn.execute("SELECT email,nume,curs,rating,text,data FROM reviews ORDER BY id DESC").fetchall()
    conn.close()
    return [{"email":r[0],"nume":r[1],"curs":r[2],"rating":r[3],"text":r[4],"data":r[5]} for r in rows]

def db_user_has_review(email):
    conn = get_db()
    row = conn.execute("SELECT 1 FROM reviews WHERE email=?", (email,)).fetchone()
    conn.close()
    return row is not None

# Seed demo reviews if none exist
def seed_reviews():
    conn = get_db()
    cnt = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    conn.close()
    if cnt == 0:
        demo = [
            ("ana.pop@gmail.com","Ana Pop","Nivel 1",5,"Am terminat Nivel 1 și sunt uimită de rezultate! Melisa explică totul pas cu pas, cu răbdare. Acum lucrez deja primele mele cliente. Recomand din toată inima!","12.03.2025"),
            ("maria.ion@yahoo.ro","Maria Ionescu","Nivel 2",5,"Tehnica French Glass m-a fascinat. Tutorialele sunt clare, de calitate, și pot reveni oricând la ele. Cel mai bun curs online pe care l-am urmat.","28.02.2025"),
            ("elena.d@gmail.com","Elena Dumitrescu","Nivel 1",5,"Eram total la început, fără nicio experiență. Acum după 3 săptămâni fac lucrări pe care le postez cu mândrie pe Instagram. Mersi NailPro!","15.01.2025"),
            ("cristina.m@gmail.com","Cristina M.","Nivel 2",4,"Materialele video sunt de înaltă calitate și feedback-ul personalizat m-a ajutat enorm să îmi corectez tehnica. Foarte profesionistă!","05.04.2025"),
            ("ioana.b@hotmail.com","Ioana Bălan","Nivel 1",5,"Am urmat cursul din diaspora (Spania) și totul a mers perfect. Accesul la materiale e rapid și instructorul răspunde mereu la întrebări.","18.03.2025"),
        ]
        conn = get_db()
        for r in demo:
            conn.execute("INSERT INTO reviews (email,nume,curs,rating,text,data) VALUES (?,?,?,?,?,?)", r)
        conn.commit()
        conn.close()

seed_reviews()

def db_get_user(email):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if row:
        return {"password": row[1], "profile": json.loads(row[2]), "orders": json.loads(row[3])}
    return None

def db_create_user(email, password):
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (email, password, profile, orders) VALUES (?,?,?,?)",
                     (email, password, '{}', '[]'))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def db_save_user(email, user_data):
    conn = get_db()
    conn.execute("UPDATE users SET password=?, profile=?, orders=? WHERE email=?",
                 (user_data["password"], json.dumps(user_data["profile"]),
                  json.dumps(user_data["orders"]), email))
    conn.commit()
    conn.close()

def db_user_exists(email):
    conn = get_db()
    row = conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return row is not None


def load_user_to_session(email):
    user = db_get_user(email)
    if user:
        st.session_state.users[email] = user

def save_current_user():
    if st.session_state.current_user:
        email = st.session_state.current_user
        db_save_user(email, st.session_state.users[email])

st.set_page_config(
    page_title="NailPro Academy",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>

/* ascunde complet butonul collapse sidebar */
button[data-testid="collapsedControl"] {
    display: none !important;
}

/* fallback vechi */
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* fallback nou streamlit */
button[kind="header"] {
    display: none !important;
}

/* fallback universal */
header button {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,700;1,400;1,500&family=Jost:wght@200;300;400;500&display=swap');

:root {
    --black:   #F5EDE0;
    --ink:     #FAF4EC;
    --surface: #EDE3D5;
    --border:  #D6C8B4;
    --gold:    #8B5E1A;
    --gold-lt: #A67C2E;
    --rose:    #9B4D6A;
    --rose-lt: #B8607E;
    --white:   #1A1208;
    --muted:   #5a4e3a;
    --serif:   'Playfair Display', serif;
    --sans:    'Jost', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container,
section[data-testid="stSidebar"],
[class*="css"] {
    background-color: var(--black) !important;
    color: var(--white);
    font-family: var(--sans);
}

#MainMenu, footer, header { visibility: hidden; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--black); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 2px; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #EDE3D5 0%, #E8DCC8 100%) !important;
    border-right: 1px solid #C8B89A !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 0.8rem 2rem 0.8rem; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid transparent !important;
    color: var(--muted) !important;
    width: 100% !important;
    text-align: left !important;
    font-family: var(--sans) !important;
    font-size: 0.7rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 0 !important;
    transition: all 0.25s ease !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-left: 2px solid var(--gold) !important;
    color: var(--gold) !important;
    background: rgba(139,94,26,0.08) !important;
}

/* ── MAIN ── */
.block-container {
    padding: 2.5rem 3rem 5rem 3rem !important;
    max-width: 1180px !important;
}

/* ── TYPOGRAPHY ── */
.eyebrow {
    font-family: var(--sans); font-size: 0.66rem; font-weight: 300;
    letter-spacing: 0.35em; text-transform: uppercase; color: var(--rose);
    text-align: center; display: block; margin-bottom: 0.5rem;
}
.pg-title {
    font-family: var(--serif); font-size: clamp(2rem,4vw,3.2rem);
    font-weight: 400; font-style: italic; color: var(--white);
    text-align: center; line-height: 1.15; display: block;
}
.pg-title .g { color: var(--gold); }
.pg-lead {
    font-family: var(--sans); font-size: 0.8rem; font-weight: 300;
    color: var(--muted); text-align: center; letter-spacing: 0.14em;
    margin-top: 0.4rem; display: block;
}
.sec-title {
    font-family: var(--serif); font-size: 1.65rem; font-weight: 400;
    color: var(--white); letter-spacing: 0.01em; margin-bottom: 0.2rem;
}
.sec-title em { color: var(--gold); font-style: italic; }
.sec-title-rose em { color: var(--rose); }

/* ── RULE ── */
.rule { display:flex; align-items:center; gap:1rem; margin:2rem 0; }
.rule::before,.rule::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg,transparent,var(--border),transparent);
}
.rdiamond {
    width:6px; height:6px; background:var(--gold);
    transform:rotate(45deg); flex-shrink:0;
}

/* ── CARDS ── */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 2px; padding: 1.8rem; position: relative; overflow: hidden;
}
.card::before {
    content:''; position:absolute; top:0;left:0;right:0; height:1px;
    background:linear-gradient(90deg,transparent,var(--gold),transparent);
}
.card-rose::before { background:linear-gradient(90deg,transparent,var(--rose),transparent); }

/* ── FEATURES ── */
.feat { display:flex; align-items:flex-start; gap:0.7rem; padding:0.65rem 0;
        border-bottom:1px solid var(--border); font-size:0.83rem; font-weight:300;
        color:var(--white); line-height:1.5; }
.feat:last-child { border-bottom:none; }
.fdot { width:4px; height:4px; background:var(--gold); border-radius:50%;
        flex-shrink:0; margin-top:0.55rem; }
.fdot-r { background:var(--rose); }

/* ── PRICE ── */
.price { font-family:var(--serif); font-size:2.5rem; font-weight:400; color:var(--gold); line-height:1; }
.price small { font-family:var(--sans); font-size:0.68rem; color:var(--muted);
               letter-spacing:0.15em; text-transform:uppercase; vertical-align:middle; margin-left:0.4rem; }
.price-rose { color:var(--rose); }

/* ── BUTTONS ── */
.stButton > button {
    background: transparent !important; border: 1px solid var(--gold) !important;
    color: var(--gold) !important; font-family: var(--sans) !important;
    font-size: 0.68rem !important; font-weight: 400 !important;
    letter-spacing: 0.22em !important; text-transform: uppercase !important;
    padding: 0.7rem 2rem !important; border-radius: 1px !important;
    transition: all 0.28s ease !important; box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--gold) !important; color: var(--black) !important;
    box-shadow: 0 0 20px rgba(139,94,26,0.15) !important;
}
.btn-rose .stButton > button { border-color:var(--rose)!important; color:var(--rose)!important; }
.btn-rose .stButton > button:hover { background:var(--rose)!important; color:var(--black)!important; }
.btn-fill .stButton > button { background:var(--gold)!important; color:#FAF4EC!important; font-weight:500!important; }
.btn-fill .stButton > button:hover { background:var(--gold-lt)!important; box-shadow:0 0 28px rgba(139,94,26,0.2)!important; }

/* ── INPUTS ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div {
    background:var(--ink)!important; border:1px solid var(--border)!important;
    border-radius:1px!important; color:var(--white)!important;
    font-family:var(--sans)!important; font-size:0.86rem!important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus {
    border-color:var(--gold)!important;
    box-shadow:0 0 0 1px rgba(139,94,26,0.15)!important;
}
.stTextInput label,.stTextArea label,.stSelectbox label,.stNumberInput label {
    font-family:var(--sans)!important; font-size:0.65rem!important;
    font-weight:400!important; letter-spacing:0.22em!important;
    text-transform:uppercase!important; color:var(--muted)!important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { background:transparent!important; border-bottom:1px solid var(--border)!important; }
.stTabs [data-baseweb="tab"] { background:transparent!important; color:var(--muted)!important;
    font-family:var(--sans)!important; font-size:0.68rem!important;
    letter-spacing:0.22em!important; text-transform:uppercase!important;
    padding:0.75rem 2rem!important; border:none!important; }
.stTabs [aria-selected="true"] { color:var(--gold)!important; border-bottom:1px solid var(--gold)!important; }

/* ── STAT BOX ── */
.stat { border:1px solid var(--border); border-top:1px solid var(--gold);
        padding:1.3rem 1rem; text-align:center; background:var(--surface); }
.stat .n { font-family:var(--serif); font-size:1.9rem; display:block; line-height:1; }
.stat .l { font-size:0.62rem; letter-spacing:0.2em; text-transform:uppercase;
           color:var(--muted); margin-top:0.35rem; display:block; }

/* ── BADGE ── */
.badge { display:inline-block; font-size:0.6rem; letter-spacing:0.18em;
         text-transform:uppercase; padding:0.2rem 0.8rem; border-radius:20px; }
.bg { border:1px solid var(--gold); color:var(--gold); background:rgba(201,151,58,0.08); }
.br { border:1px solid var(--rose); color:var(--rose); background:rgba(212,134,154,0.08); }
.bgrn { border:1px solid #4caf7d; color:#4caf7d; background:rgba(76,175,125,0.08); }

/* ── CONTACT ROW ── */
.crow { display:flex; gap:1rem; padding:0.85rem 0; border-bottom:1px solid var(--border); align-items:flex-start; }
.crow .ico { color:var(--gold); font-size:0.88rem; flex-shrink:0; margin-top:0.1rem; }
.crow .dt { font-size:0.82rem; font-weight:300; color:var(--white); line-height:1.6; }
.crow .lb { font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; color:var(--muted); display:block; margin-bottom:0.1rem; }

/* ── ORDER CARD ── */
.oc { background:var(--surface); border:1px solid var(--border);
      border-left:2.5px solid var(--gold); padding:1.3rem 1.6rem; margin-bottom:0.8rem; border-radius:1px; }
.oc-r { border-left-color:var(--rose); }

/* ── GALLERY uniform height ── */
.gallery-grid { display:grid; gap:6px; }
.gallery-grid .gimg {
    width:100%; aspect-ratio:1/1; object-fit:cover;
    border-radius:16px; display:block;
}
.gallery-grid-5 { grid-template-columns: repeat(5,1fr); }
.gallery-grid-2 { grid-template-columns: repeat(2,1fr); }
.gallery-grid-4 { grid-template-columns: repeat(4,1fr); }

/* ── READABILITY improvements ── */
.pg-title {
    font-size: clamp(2.4rem, 5vw, 3.8rem) !important;
    margin-bottom: 0.3rem !important;
    line-height: 1.1 !important;
}
.pg-lead {
    font-size: 0.88rem !important;
    letter-spacing: 0.08em !important;
    color: #6a5c44 !important;
}
.eyebrow {
    font-size: 0.7rem !important;
    letter-spacing: 0.28em !important;
}
.sec-title { font-size: 1.85rem !important; }
.feat { font-size: 0.88rem !important; padding: 0.75rem 0 !important; }
.stat .n { font-size: 2.2rem !important; }
.stat .l { font-size: 0.68rem !important; color: #6a5c44 !important; }
.price { font-size: 2.8rem !important; }


/* ── SIDEBAR LOGO ── */
.sl { padding:2.2rem 1rem 1.4rem; border-bottom:1px solid var(--border); margin-bottom:1rem; text-align:center; }
.sl .ico { font-size:1.7rem; display:block; }
.sl .brand { font-family:var(--serif); font-size:1.1rem; color:var(--gold); letter-spacing:0.12em; display:block; margin-top:0.4rem; }
.sl .tag { font-size:0.56rem; letter-spacing:0.3em; text-transform:uppercase; color:var(--muted); display:block; margin-top:0.25rem; }
.slbl { font-size:0.56rem; letter-spacing:0.3em; text-transform:uppercase; color:var(--muted); padding:0.9rem 1.2rem 0.35rem; display:block; }

/* ── CAROUSEL ARROW BUTTONS ── */
button[kind="secondary"][data-testid*="_p"],
button[kind="secondary"][data-testid*="_n"] {
    padding: 0.25rem 0.6rem !important;
    font-size: 1.1rem !important;
    letter-spacing: 0 !important;
    border-radius: 50% !important;
    min-height: unset !important;
    width: 2rem !important;
    height: 2rem !important;
}

/* Carousel arrows — compact round style */
div[data-testid="column"] .stButton > button:has(+ *) {
    padding: 0.2rem 0.5rem !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown('<div id="top"></div>', unsafe_allow_html=True)


for k, v in {
    "page": "Prezentare", "logged_in": False,
    "users": {}, "current_user": None,
    "cart": [], "ci1": 0, "ci2": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


BASE1 = r"C:\Users\Melisa\Desktop\Pagina web\Nivel 1"
BASE2 = r"C:\Users\Melisa\Desktop\Pagina web\Nivel 2"
N1 = [os.path.join(BASE1, f"{i}.jpeg") for i in range(1, 11)]
N2 = [os.path.join(BASE2, f"{i}.jpeg") for i in range(29, 20, -1)]

def valid(paths): return [p for p in paths if os.path.exists(p)]


def carousel(images, key, idx_key):
    imgs = valid(images)
    if not imgs:
        st.markdown("""
        <div style="background:var(--ink);border:1px dashed #C8B89A;height:240px;
                    display:flex;align-items:center;justify-content:center;border-radius:12px;">
            <span style="color:var(--muted);font-size:0.7rem;letter-spacing:0.15em;">
                Adaugă pozele în folderul indicat
            </span>
        </div>""", unsafe_allow_html=True)
        return
    idx = st.session_state[idx_key] % len(imgs)


    auto_key = f"{key}_auto_tick"
    if auto_key not in st.session_state:
        st.session_state[auto_key] = 0

    # Show image with rounded corners
    st.markdown(f'<div style="border-radius:16px;overflow:hidden;">', unsafe_allow_html=True)
    st.image(imgs[idx], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Dot indicators
    dots_html = "<div style='text-align:center;margin:0.5rem 0 0.3rem 0;display:flex;justify-content:center;gap:5px;'>"
    for i in range(len(imgs)):
        color = "var(--gold)" if i == idx else "var(--border)"
        size  = "8px" if i == idx else "6px"
        dots_html += f"<span style='width:{size};height:{size};border-radius:50%;background:{color};display:inline-block;transition:all 0.3s;'></span>"
    dots_html += "</div>"
    st.markdown(dots_html, unsafe_allow_html=True)

    # Navigation — compact arrow buttons
    nav_l, nav_c, nav_r = st.columns([1, 4, 1])
    with nav_l:
        st.markdown('<div style="display:flex;justify-content:center;">', unsafe_allow_html=True)
        if st.button("‹", key=f"{key}_p", help="Anterior"):
            st.session_state[idx_key] = (idx-1) % len(imgs); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with nav_c:
        st.markdown(f"<p style='text-align:center;font-size:0.6rem;letter-spacing:0.2em;color:var(--muted);text-transform:uppercase;margin:0.4rem 0;'>{idx+1} / {len(imgs)}</p>", unsafe_allow_html=True)
    with nav_r:
        st.markdown('<div style="display:flex;justify-content:center;">', unsafe_allow_html=True)
        if st.button("›", key=f"{key}_n", help="Următor"):
            st.session_state[idx_key] = (idx+1) % len(imgs); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── JS: after 10s post-load, simulate click on "next" button ─────────────
    st.markdown(f"""
    <script>
    (function() {{
        if (window._carouselTimer_{key}) clearTimeout(window._carouselTimer_{key});
        window._carouselTimer_{key} = setTimeout(function() {{
            // find the › button for this carousel and click it
            const btns = window.parent.document.querySelectorAll('button');
            for (let b of btns) {{
                if (b.innerText.trim() === '›') {{
                    b.click();
                    break;
                }}
            }}
        }}, 10000);
    }})();
    </script>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] svg {
    display: none !important;
}
    </style>
    """, unsafe_allow_html=True)

def gallery(images, n=4):
    imgs = valid(images)[:n]
    if not imgs: return
    # Build uniform-height gallery via HTML img tags with object-fit
    grid_class = f"gallery-grid-{n}" if n in [2,4,5] else "gallery-grid-4"
    imgs_html = "".join(
        f'<img class="gimg" src="data:image/jpeg;base64,{_img_to_b64(img)}" alt="lucrare"/>'
        for img in imgs
    )
    st.markdown(f'<div class="gallery-grid {grid_class}">{imgs_html}</div>', unsafe_allow_html=True)

import base64
def _img_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def scroll_top():
    """Inject JS to scroll window back to top."""
    st.markdown("""
    <script>
        window.scrollTo({top: 0, behavior: 'smooth'});
        const frames = window.parent.document.querySelectorAll('iframe');
        frames.forEach(f => { try { f.contentWindow.scrollTo(0,0); } catch(e){} });
        window.parent.scrollTo({top: 0, behavior: 'smooth'});
    </script>
    """, unsafe_allow_html=True)

def rule():
    st.markdown('<div class="rule"><div class="rdiamond"></div></div>', unsafe_allow_html=True)

def sp(n=1):
    st.markdown(f"<div style='margin:{n*0.5}rem 0;'></div>", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div class="sl">
        <span class="ico">💅</span>
        <span class="brand">NailPro Academy</span>
        <span class="tag">Cursuri Online · Constanța</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<span class="slbl">Meniu principal</span>', unsafe_allow_html=True)
    for p in ["Prezentare", "Pachete", "Recenzii", "Blog", "Contact"]:
        if st.button(p, key=f"nav_{p}"):
            st.session_state.page = p
            scroll_top()
            st.rerun()

    if st.session_state.logged_in:
        st.markdown('<span class="slbl">Contul meu</span>', unsafe_allow_html=True)
        cart_lbl = f"Coș ({len(st.session_state.cart)})" if st.session_state.cart else "Coș"
        for p in ["Profilul Meu", "Cursurile Mele", cart_lbl]:
            k = p.split(" (")[0]
            if st.button(p, key=f"nav_{k}"):
                st.session_state.page = k
                scroll_top()
                st.rerun()

    sp(2)
    # ── Social links ──
    st.markdown("""
    <div style="display:flex;justify-content:center;gap:1rem;padding:0.5rem 0;">
        <a href="https://www.facebook.com/share/18e1ZfkwW1/?mibextid=wwXIfr" target="_blank"
           style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;
                  border-radius:50%;border:1px solid #C8B89A;color:#8B5E1A;text-decoration:none;
                  font-size:1rem;transition:all 0.2s;" title="Facebook">f</a>
        <a href="https://www.instagram.com/nailproacademy.online" target="_blank"
           style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;
                  border-radius:50%;border:1px solid #C8B89A;color:#9B4D6A;text-decoration:none;
                  font-size:1rem;transition:all 0.2s;" title="Instagram">📸</a>
    </div>
    <p style="text-align:center;font-size:0.56rem;letter-spacing:0.2em;text-transform:uppercase;color:#7a6040;margin-top:0.3rem;">Urmărește-ne</p>
    """, unsafe_allow_html=True)

    sp(2)
    rule()

    if not st.session_state.logged_in:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login", key="sl_l"):
                st.session_state.page = "Auth"; st.rerun()
        with c2:
            if st.button("Cont nou", key="sl_r"):
                st.session_state.page = "Auth"; st.rerun()
    else:
        prof = st.session_state.users[st.session_state.current_user].get("profile", {})
        name = prof.get("prenume", st.session_state.current_user.split("@")[0])
        st.markdown(f"<p style='font-size:0.72rem;color:var(--gold);text-align:center;letter-spacing:0.1em;padding:0.3rem 0;'>👤 {name}</p>", unsafe_allow_html=True)
        if st.button("Deconectare", key="logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.cart = []
            st.session_state.page = "Prezentare"; st.rerun()


if st.session_state.page == "Prezentare":

    # Hero
    sp(2)
    st.markdown('<span class="eyebrow">Cursuri online de manichiură</span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-title"><em>NailPro</em> <span class="g">Academy</span></span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-lead">Formează-te profesional · Online · Din orice colț din lume</span>', unsafe_allow_html=True)
    sp(2)

    # Stats
    sc = st.columns(4)
    for col, (num, lbl, clr) in zip(sc, [
        ("2",   "niveluri de pregătire", "var(--gold)"),
        ("~2",  "săptămâni per nivel",   "var(--rose)"),
        ("100%","online & flexibil",     "var(--gold)"),
        ("∞",   "reluări materiale video","var(--rose)"),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat">
                <span class="n" style="color:{clr};">{num}</span>
                <span class="l">{lbl}</span>
            </div>""", unsafe_allow_html=True)

    rule()


    sp()
    st.markdown('<span class="eyebrow">Lucrări din cursurile noastre</span>', unsafe_allow_html=True)
    sp()
    gallery(N2, n=5)
    sp(2)

    rule()


    a_left, a_gap, a_right = st.columns([5, 1, 4])

    with a_left:
        st.markdown('<div class="sec-title">Despre <em>noi</em></div>', unsafe_allow_html=True)
        sp()
        st.markdown("""
        <p style="font-size:0.93rem;font-weight:300;color:#3a2e1e;line-height:2.1;max-width:460px;">
            NailPro Academy este o platformă de formare profesională în domeniul nail art, 
            fondată de un instructor cu experiență bogată atât în cursuri fizice cât și online, 
            cu sediul în Constanța.
        </p>
        <p style="font-size:0.93rem;font-weight:300;color:#3a2e1e;line-height:2.1;max-width:460px;margin-top:0.9rem;">
            Misiunea noastră: să oferim fiecărei cursante un parcurs elegant, 
            structurat și personalizat — indiferent că ești la început sau dorești 
            să-ți perfecționezi tehnica.
        </p>""", unsafe_allow_html=True)
        sp()
        for f in [
            "Materiale video demonstrative cu acces nelimitat",
            "Feedback personalizat pe fotografii transmise",
            "Sesiuni live individuale sau de grup pe Zoom",
            "Diplomă de absolvire după finalizarea modulelor",
            "Accesibil din orice localitate sau din diaspora",
            "Flexibil — înveți în ritmul propriu",
        ]:
            st.markdown(f'<div class="feat"><span class="fdot"></span><span>{f}</span></div>', unsafe_allow_html=True)

    with a_right:
        sp(2)
        gallery(N2[4:6], n=2)
        sp()
        gallery(N1[7:9], n=2)

    rule()


    st.markdown('<span class="eyebrow">Procesul nostru</span>', unsafe_allow_html=True)
    sp()
    st.markdown('<div class="sec-title" style="text-align:center;">Cum <em>funcționează</em></div>', unsafe_allow_html=True)
    sp(2)

    hc = st.columns(4)
    for col, (n, t, d, clr) in zip(hc, [
        ("01","Alegi nivelul","Selectezi pachetul potrivit și îl adaugi în coș.","var(--gold)"),
        ("02","Efectuezi plata","Transfer bancar la IBAN-ul indicat + confirmare.","var(--rose)"),
        ("03","Primești accesul","Link Google Drive în maxim 24h de la confirmare.","var(--gold)"),
        ("04","Înveți & crești","Parcurgi materialele și primești feedback personalizat.","var(--rose)"),
    ]):
        with col:
            st.markdown(f"""
            <div style="padding:1.5rem 1.1rem;background:var(--surface);
                        border:1px solid var(--border);border-top:1px solid {clr};border-radius:1px;height:100%;">
                <span style="font-family:var(--serif);font-size:1.9rem;color:{clr};display:block;line-height:1;margin-bottom:0.7rem;">{n}</span>
                <span style="font-family:var(--serif);font-size:0.95rem;color:var(--white);display:block;margin-bottom:0.5rem;">{t}</span>
                <span style="font-size:0.77rem;font-weight:300;color:var(--muted);line-height:1.7;display:block;">{d}</span>
            </div>""", unsafe_allow_html=True)

    rule()


    _, mc, _ = st.columns([3,2,3])
    with mc:
        st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
        if st.button("Explorează Pachetele", key="cta"):
            st.session_state.page = "Pachete"
            scroll_top()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    rule()


    st.markdown('<span class="eyebrow">Urmărește-ne</span>', unsafe_allow_html=True)
    sp()
    soc_l, soc_r = st.columns(2)
    with soc_l:
        st.markdown("""
        <a href="https://www.facebook.com/share/18e1ZfkwW1/?mibextid=wwXIfr" target="_blank"
           style="display:flex;align-items:center;gap:1rem;background:var(--surface);
                  border:1px solid var(--border);border-left:3px solid #1877F2;
                  padding:1.2rem 1.5rem;border-radius:8px;text-decoration:none;
                  transition:all 0.25s;margin-bottom:0.5rem;">
            <span style="font-size:1.8rem;">📘</span>
            <span>
                <span style="display:block;font-family:'Playfair Display',serif;font-size:1rem;color:#1A1208;margin-bottom:0.2rem;">Facebook</span>
                <span style="font-size:0.72rem;color:#5a4e3a;letter-spacing:0.08em;">NailPro Academy · Urmărește pagina noastră</span>
            </span>
        </a>""", unsafe_allow_html=True)
    with soc_r:
        st.markdown("""
        <a href="https://www.instagram.com/nailproacademy.online" target="_blank"
           style="display:flex;align-items:center;gap:1rem;background:var(--surface);
                  border:1px solid var(--border);border-left:3px solid #E1306C;
                  padding:1.2rem 1.5rem;border-radius:8px;text-decoration:none;
                  transition:all 0.25s;margin-bottom:0.5rem;">
            <span style="font-size:1.8rem;">📸</span>
            <span>
                <span style="display:block;font-family:'Playfair Display',serif;font-size:1rem;color:#1A1208;margin-bottom:0.2rem;">Instagram</span>
                <span style="font-size:0.72rem;color:#5a4e3a;letter-spacing:0.08em;">@nailproacademy.online · Inspirație zilnică</span>
            </span>
        </a>""", unsafe_allow_html=True)

    rule()


    reviews = db_get_reviews()
    if reviews:
        st.markdown('<span class="eyebrow">Ce spun cursantele noastre</span>', unsafe_allow_html=True)
        sp()
        st.markdown('<div class="sec-title" style="text-align:center;">Recenzii <em>verificate</em></div>', unsafe_allow_html=True)
        sp(2)
        rev_cols = st.columns(3)
        for i, rev in enumerate(reviews[:3]):
            with rev_cols[i]:
                stars = "★" * rev["rating"] + "☆" * (5 - rev["rating"])
                badge_clr = "var(--gold)" if "1" in rev["curs"] else "var(--rose)"
                st.markdown(f"""
                <div class="card" style="height:100%;min-height:200px;">
                    <p style="color:{badge_clr};font-size:1rem;letter-spacing:0.05em;margin-bottom:0.6rem;">{stars}</p>
                    <p style="font-family:'Playfair Display',serif;font-style:italic;font-size:0.93rem;
                               color:#1A1208;line-height:1.8;margin-bottom:0.8rem;">"{rev['text']}"</p>
                    <p style="font-size:0.72rem;font-weight:500;color:#3a2e1e;">{rev['nume']}</p>
                    <p style="font-size:0.62rem;color:var(--muted);letter-spacing:0.1em;">{rev['curs']} · {rev['data']}</p>
                </div>""", unsafe_allow_html=True)
        sp()
        _, btn_c, _ = st.columns([3,2,3])
        with btn_c:
            if st.button("Vezi toate recenziile", key="all_rev"):
                st.session_state.page = "Recenzii"; scroll_top(); st.rerun()

    rule()


elif st.session_state.page == "Pachete":
    scroll_top()
    sp(2)
    st.markdown('<span class="eyebrow">Oferta noastră</span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-title">Alege-ți <span class="g">nivelul</span></span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-lead">Două pachete complete · Feedback personalizat · Diplomă inclusă</span>', unsafe_allow_html=True)
    rule()

    # ── NIVEL 1 ──
    st.markdown("""
    <div style="display:flex;align-items:baseline;gap:1.4rem;margin-bottom:2rem;padding-bottom:1rem;border-bottom:1px solid var(--border);">
        <span style="font-family:var(--serif);font-size:0.7rem;letter-spacing:0.4em;
                     text-transform:uppercase;color:var(--muted);">Nivelul</span>
        <span style="font-family:var(--serif);font-size:2.4rem;font-style:italic;color:var(--gold);">
            01 — Tehnici de bază
        </span>
    </div>""", unsafe_allow_html=True)

    n1l, n1r = st.columns([5, 4])
    with n1l:
        st.markdown('<div class="price">1.000 lei<small>/ curs complet</small></div>', unsafe_allow_html=True)
        sp()
        st.markdown("""
        <p style="font-size:0.93rem;font-weight:300;color:#3a2e1e;line-height:2.1;max-width:440px;">
            Destinat persoanelor fără experiență anterioară. Vei dobândi toate competențele 
            necesare pentru a realiza lucrări corecte și rezistente, cu sprijin constant 
            din partea instructorului.
        </p>""", unsafe_allow_html=True)
        sp()
        for t, d in [
            ("Unghii scurte","Pregătire, aplicare corectă, finisare profesională"),
            ("Construcție pe tips","Alegerea tipsului potrivit, aplicare și modelare"),
            ("Construcție pe șablon","Extensie fără tips folosind șablonul de construcție"),
            ("Întreținerea lucrărilor","Tehnici de corecție după creștere și refacere"),
        ]:
            st.markdown(f"""
            <div class="feat"><span class="fdot"></span>
            <span><strong style="color:var(--white);font-weight:500;font-size:0.92rem;">{t}</strong>
            &nbsp;—&nbsp;<span style="color:#5a4e3a;font-size:0.85rem;">{d}</span></span></div>""", unsafe_allow_html=True)
        sp(2)
        st.markdown("""
        <div style="background:var(--surface);border:1px solid var(--border);
                    border-left:2px solid var(--gold);padding:1.1rem 1.4rem;border-radius:1px;">
            <p style="font-size:0.78rem;letter-spacing:0.06em;color:#5a4e3a;line-height:2.1;">
                ✦ Acces video nelimitat &nbsp;·&nbsp; ✦ Evaluare fotografii
                &nbsp;·&nbsp; ✦ Sesiuni Zoom &nbsp;·&nbsp; ✦ Diplomă de absolvire
            </p>
        </div>""", unsafe_allow_html=True)
        sp()
        if st.button("Adaugă Nivel 1 în Coș", key="cn1"):
            if not st.session_state.logged_in:
                st.warning("Autentifică-te pentru a achiziționa cursul.")
            elif "Nivel 1" in [x["name"] for x in st.session_state.cart]:
                st.info("Nivel 1 se află deja în coș.")
            else:
                st.session_state.cart.append({"name":"Nivel 1","price":1000})
                st.success("Nivel 1 adăugat în coș!")

    with n1r:
        st.markdown("<p style='font-size:0.65rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--muted);margin-bottom:0.8rem;'>Galerie lucrări · Nivel 1</p>", unsafe_allow_html=True)
        carousel(N1, "c1", "ci1")

    rule()

    # Galerie decorativa Nivel 2 intre sectiuni
    imgs2v = valid(N2)
    if imgs2v:
        st.markdown("<p style='font-size:0.65rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--muted);margin-bottom:0.9rem;'>Previzualizare lucrări · Nivel 2</p>", unsafe_allow_html=True)
        # Use HTML gallery for uniform heights
        n_preview = min(4, len(imgs2v))
        imgs_html = "".join(
            f'<img class="gimg" src="data:image/jpeg;base64,{_img_to_b64(img)}" alt="lucrare"/>'
            for img in imgs2v[:n_preview]
        )
        st.markdown(f'<div class="gallery-grid gallery-grid-4">{imgs_html}</div>', unsafe_allow_html=True)
        sp(2)

    # ── NIVEL 2 ──
    st.markdown("""
    <div style="display:flex;align-items:baseline;gap:1.4rem;margin-bottom:2rem;padding-bottom:1rem;border-bottom:1px solid var(--border);">
        <span style="font-family:var(--serif);font-size:0.7rem;letter-spacing:0.4em;
                     text-transform:uppercase;color:var(--muted);">Nivelul</span>
        <span style="font-family:var(--serif);font-size:2.4rem;font-style:italic;color:var(--rose);">
            02 — Tehnici avansate
        </span>
    </div>""", unsafe_allow_html=True)

    n2l, n2r = st.columns([4, 5])
    with n2l:
        st.markdown("<p style='font-size:0.65rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--muted);margin-bottom:0.8rem;'>Galerie lucrări · Nivel 2</p>", unsafe_allow_html=True)
        carousel(N2, "c2", "ci2")

    with n2r:
        st.markdown('<div class="price price-rose">1.500 lei<small>/ curs complet</small></div>', unsafe_allow_html=True)
        sp()
        st.markdown("""
        <p style="font-size:0.93rem;font-weight:300;color:#3a2e1e;line-height:2.1;max-width:440px;">
            Pentru persoanele cu cunoștințe de bază care doresc un nivel de execuție 
            profesional, specific saloanelor de specialitate. Tehnici de vârf, 
            rezultate de concurs.
        </p>""", unsafe_allow_html=True)
        sp()
        for t, d in [
            ("Forma pătrat arcuit","Structură corectă și simetrie laterală perfectă"),
            ("Forma balerină","Construcție pe șablon, modelare specifică"),
            ("Tehnica French Glass","Efect translucid modern, lucrări profesionale"),
            ("French de interior","Aspect natural și elegant, tehnică de vârf"),
            ("Pătrat dublu side","Structură precisă pentru lucrări avansate"),
        ]:
            st.markdown(f"""
            <div class="feat"><span class="fdot fdot-r"></span>
            <span><strong style="color:var(--white);font-weight:500;font-size:0.92rem;">{t}</strong>
            &nbsp;—&nbsp;<span style="color:#5a4e3a;font-size:0.85rem;">{d}</span></span></div>""", unsafe_allow_html=True)
        sp(2)
        st.markdown("""
        <div style="background:var(--surface);border:1px solid var(--border);
                    border-left:2px solid var(--rose);padding:1.1rem 1.4rem;border-radius:1px;">
            <p style="font-size:0.78rem;letter-spacing:0.06em;color:#5a4e3a;line-height:2.1;">
                ✦ Acces video nelimitat &nbsp;·&nbsp; ✦ Evaluare fotografii
                &nbsp;·&nbsp; ✦ Sesiuni Zoom &nbsp;·&nbsp; ✦ Diplomă de absolvire
            </p>
        </div>""", unsafe_allow_html=True)
        sp()
        st.markdown('<div class="btn-rose">', unsafe_allow_html=True)
        if st.button("Adaugă Nivel 2 în Coș", key="cn2"):
            if not st.session_state.logged_in:
                st.warning("Autentifică-te pentru a achiziționa cursul.")
            elif "Nivel 2" in [x["name"] for x in st.session_state.cart]:
                st.info("Nivel 2 se află deja în coș.")
            else:
                st.session_state.cart.append({"name":"Nivel 2","price":1500})
                st.success("Nivel 2 adăugat în coș!")
        st.markdown('</div>', unsafe_allow_html=True)

    rule()


    st.markdown('<span class="eyebrow">Previzualizare conținut</span>', unsafe_allow_html=True)
    sp()
    st.markdown('<div class="sec-title" style="text-align:center;">Demo <em>video</em> — Tehnici din cursuri</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;font-size:0.8rem;color:var(--muted);margin-top:0.4rem;letter-spacing:0.08em;">Descoperă stilul nostru de predare înainte să te înscrii</p>', unsafe_allow_html=True)
    sp(2)

    vd1, vd2, vd3 = st.columns(3)
    videos = [
        ("https://www.youtube.com/shorts/rXKiPWxtof4", "Tehnici de bază", "Nivel 1 · Construcție unghii"),
        ("https://www.youtube.com/shorts/L43uKZgP9QI", "Modelare avansată", "Nivel 2 · Forme speciale"),
        ("https://www.youtube.com/shorts/Do8woKfEuv0", "Finisare profesională", "Nivel 1 & 2 · Detalii"),
    ]
    for col, (url, title, sub) in zip([vd1, vd2, vd3], videos):
        vid_id = url.split("/")[-1]
        embed  = f"https://www.youtube.com/embed/{vid_id}"
        with col:
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:12px;overflow:hidden;border-top:2px solid var(--gold);">
                <div style="position:relative;padding-bottom:177%;height:0;overflow:hidden;">
                    <iframe src="{embed}"
                        style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
                        allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture"
                        allowfullscreen loading="lazy">
                    </iframe>
                </div>
                <div style="padding:1rem;">
                    <p style="font-family:'Playfair Display',serif;font-size:0.95rem;color:#1A1208;margin-bottom:0.2rem;">{title}</p>
                    <p style="font-size:0.68rem;color:var(--muted);letter-spacing:0.1em;">{sub}</p>
                </div>
            </div>""", unsafe_allow_html=True)
    sp(2)


elif st.session_state.page == "Contact":
    sp(2)
    st.markdown('<span class="eyebrow">Suntem aici pentru tine</span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-title">Ne <span class="g">contactezi</span></span>', unsafe_allow_html=True)
    rule()

    cl, cg, cr = st.columns([4, 1, 5])
    with cl:
        st.markdown('<div class="sec-title">Date de <em>contact</em></div>', unsafe_allow_html=True)
        sp()
        for ico, lbl, val in [
            ("📍","Adresă","Bd. Mamaia 123, Bloc A<br>Constanța, 900001"),
            ("📞","Telefon","+40 723 456 789"),
            ("📧","Email","contact@nailproacademy.ro"),
            ("📸","Instagram",'<a href="https://www.instagram.com/nailproacademy.online" style="color:var(--rose);text-decoration:none;font-weight:500;" target="_blank">@nailproacademy.online</a>'),
            ("📘","Facebook",'<a href="https://www.facebook.com/share/18e1ZfkwW1/?mibextid=wwXIfr" style="color:#1877F2;text-decoration:none;font-weight:500;" target="_blank">NailPro Academy pe Facebook</a>'),
            ("⏰","Program","Luni – Vineri 10:00 – 20:00<br>Sâmbătă 10:00 – 15:00"),
        ]:
            st.markdown(f"""
            <div class="crow" style="padding:1rem 0;">
                <span class="ico" style="font-size:1.3rem;">{ico}</span>
                <span class="dt" style="font-size:0.98rem;">
                    <span class="lb" style="font-size:0.68rem;">{lbl}</span>
                    {val}
                </span>
            </div>""", unsafe_allow_html=True)

        sp(2)
        st.markdown('<div class="sec-title">Trimite-ne un <em>mesaj</em></div>', unsafe_allow_html=True)
        sp()
        with st.form("cf"):
            st.text_input("Nume complet")
            st.text_input("Email")
            st.text_area("Mesaj", height=100)
            st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
            if st.form_submit_button("Trimite"):
                st.success("Mesajul tău a fost trimis. Te vom contacta în curând.")
            st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="sec-title">Localizare <em>Constanța</em></div>', unsafe_allow_html=True)
        sp()
        st.components.v1.html("""
        <iframe
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d46217.0!2d28.5943!3d44.1598!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40bad04e89424b97%3A0xb16c26f6be0de27c!2sConstanta%2C%20Romania!5e0!3m2!1sro!2sro"
          width="100%" height="500"
          style="border:1px solid #C8B89A;border-radius:2px;display:block;
                 filter:grayscale(55%) invert(92%) sepia(15%) hue-rotate(185deg) brightness(0.88);"
          allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade">
        </iframe>""", height=510)

elif st.session_state.page == "Auth":
    sp(2)
    st.markdown('<span class="eyebrow">Accesează platforma</span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-title">Contul <span class="g">tău</span></span>', unsafe_allow_html=True)
    rule()
    _, mid, _ = st.columns([2,4,2])
    with mid:
        tl, tr = st.tabs(["  Autentificare  ","  Cont nou  "])
        with tl:
            sp()
            with st.form("lf"):
                em = st.text_input("Email")
                pw = st.text_input("Parolă", type="password")
                sp()
                st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
                b = st.form_submit_button("Intră în cont")
                st.markdown('</div>', unsafe_allow_html=True)
                if b:
                    user_data = db_get_user(em)
                    if user_data and user_data["password"] == pw:
                        st.session_state.users[em] = user_data
                        st.session_state.logged_in = True
                        st.session_state.current_user = em
                        st.session_state.page = "Profilul Meu"; st.rerun()
                    else:
                        st.error("Email sau parolă incorectă.")
        with tr:
            sp()
            with st.form("rf"):
                re_ = st.text_input("Email")
                rp  = st.text_input("Parolă", type="password")
                rp2 = st.text_input("Confirmă parola", type="password")
                sp()
                st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
                b2 = st.form_submit_button("Creează cont")
                st.markdown('</div>', unsafe_allow_html=True)
                if b2:
                    if not re_ or not rp:
                        st.error("Completează toate câmpurile.")
                    elif rp != rp2:
                        st.error("Parolele nu coincid.")
                    elif db_user_exists(re_):
                        st.error("Contul există deja.")
                    else:
                        ok = db_create_user(re_, rp)
                        if ok:
                            st.session_state.users[re_] = {"password":rp,"profile":{},"orders":[]}
                            st.session_state.logged_in = True
                            st.session_state.current_user = re_
                            st.session_state.page = "Profilul Meu"; st.rerun()
                        else:
                            st.error("Eroare la crearea contului.")


elif st.session_state.page == "Profilul Meu":
    if not st.session_state.logged_in:
        st.warning("Autentifică-te mai întâi.")
    else:
        user = st.session_state.users[st.session_state.current_user]
        profile = user.get("profile", {})
        sp(2)
        st.markdown('<span class="eyebrow">Informații personale</span>', unsafe_allow_html=True)
        st.markdown('<span class="pg-title">Profilul <span class="g">meu</span></span>', unsafe_allow_html=True)
        rule()


        st.markdown('<div class="sec-title" style="margin-bottom:0.5rem;">Video <em>demo</em> — Previzualizare cursuri</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.78rem;color:var(--muted);margin-bottom:1.2rem;">Trei tehnici din cursurile NailPro Academy</p>', unsafe_allow_html=True)
        pv1, pv2, pv3 = st.columns(3)
        prof_videos = [
            ("https://www.youtube.com/shorts/rXKiPWxtof4","Tehnici de bază","Unghii scurte · Construcție"),
            ("https://www.youtube.com/shorts/ixEotix6bg0","Forme avansate","Balerină · French Glass"),
            ("https://www.youtube.com/shorts/Do8woKfEuv0","Finisare","Detalii & perfecțiune"),
        ]
        for col, (url, title, sub) in zip([pv1, pv2, pv3], prof_videos):
            vid_id = url.split("/")[-1]
            embed  = f"https://www.youtube.com/embed/{vid_id}"
            with col:
                st.markdown(f"""
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;
                            overflow:hidden;border-top:2px solid var(--rose);">
                    <div style="position:relative;padding-bottom:177%;height:0;overflow:hidden;">
                        <iframe src="{embed}"
                            style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
                            allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture"
                            allowfullscreen loading="lazy">
                        </iframe>
                    </div>
                    <div style="padding:0.8rem;">
                        <p style="font-family:'Playfair Display',serif;font-size:0.88rem;color:#1A1208;margin-bottom:0.15rem;">{title}</p>
                        <p style="font-size:0.63rem;color:var(--muted);">{sub}</p>
                    </div>
                </div>""", unsafe_allow_html=True)
        rule()
        pl, pr = st.columns([5,3])
        with pl:
            with st.form("pf"):
                ca, cb = st.columns(2)
                with ca: nume    = st.text_input("Nume",    value=profile.get("nume",""))
                with cb: prenume = st.text_input("Prenume", value=profile.get("prenume",""))
                telefon = st.text_input("Telefon",  value=profile.get("telefon",""))
                adresa  = st.text_input("Adresă",   value=profile.get("adresa",""))
                cc, cd  = st.columns(2)
                with cc: oras = st.text_input("Oraș",  value=profile.get("oras",""))
                with cd: jud  = st.text_input("Județ", value=profile.get("judet",""))
                cp  = st.text_input("Cod poștal", value=profile.get("cod_postal",""))
                exp = st.selectbox("Nivel experiență",
                    ["Fără experiență","Începător","Intermediar","Avansat"],
                    index=["Fără experiență","Începător","Intermediar","Avansat"].index(
                        profile.get("nivel_experienta","Fără experiență")))
                sp()
                st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
                save = st.form_submit_button("Salvează profilul")
                st.markdown('</div>', unsafe_allow_html=True)
                if save:
                    st.session_state.users[st.session_state.current_user]["profile"] = {
                        "nume":nume,"prenume":prenume,"telefon":telefon,"adresa":adresa,
                        "oras":oras,"judet":jud,"cod_postal":cp,"nivel_experienta":exp}
                    save_current_user()
                    st.success("Profilul actualizat."); st.rerun()
        with pr:
            sp()
            orders = user.get("orders",[])
            st.markdown(f"""
            <div class="card" style="margin-bottom:1rem;">
                <p style="font-size:0.6rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--muted);margin-bottom:1rem;">Cont</p>
                <p style="font-size:0.72rem;color:var(--muted);">Email</p>
                <p style="font-size:0.88rem;color:var(--white);margin-bottom:0.8rem;">{st.session_state.current_user}</p>
                <p style="font-size:0.72rem;color:var(--muted);">Nivel experiență</p>
                <p style="font-size:0.9rem;color:var(--gold);">{profile.get("nivel_experienta","—")}</p>
            </div>""", unsafe_allow_html=True)
            st.markdown('<div class="card card-rose">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.6rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--muted);margin-bottom:0.8rem;">Cursuri</p>', unsafe_allow_html=True)
            if orders:
                for o in orders:
                    bc = "bgrn" if o.get("activated") else "bg"
                    bl = "Activ" if o.get("activated") else "În procesare"
                    st.markdown(f"<p style='font-size:0.87rem;color:var(--white);margin-bottom:0.3rem;'>{o['name']}</p><span class='badge {bc}'>{bl}</span><br><br>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size:0.78rem;color:var(--muted);'>Niciun curs încă.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


elif st.session_state.page == "Cursurile Mele":
    if not st.session_state.logged_in:
        st.warning("Autentifică-te mai întâi.")
    else:
        user   = st.session_state.users[st.session_state.current_user]
        orders = user.get("orders",[])
        sp(2)
        st.markdown('<span class="eyebrow">Parcursul meu</span>', unsafe_allow_html=True)
        st.markdown('<span class="pg-title">Cursurile <span class="g">mele</span></span>', unsafe_allow_html=True)
        rule()
        if not orders:
            st.markdown('<div class="card" style="text-align:center;padding:2.5rem;"><p style="font-family:var(--serif);font-size:1.3rem;font-style:italic;color:var(--muted);">Nu ai achiziționat niciun curs încă.</p></div>', unsafe_allow_html=True)
            sp()
            if st.button("Explorează pachetele"): st.session_state.page="Pachete"; st.rerun()
        else:
            for o in orders:
                act  = o.get("activated",False)
                bclr = "var(--gold)" if "1" in o["name"] else "var(--rose)"
                sclr = "#4caf7d" if act else "var(--gold-lt)"
                stxt = "✅ Curs activ — accesul a fost activat" if act else "⏳ În procesare — vei primi accesul în 24h de la confirmare"
                ci, cb = st.columns([7,2])
                with ci:
                    st.markdown(f"""
                    <div class="oc" style="border-left-color:{bclr};">
                        <p style="font-family:var(--serif);font-size:1.05rem;color:var(--white);margin-bottom:0.35rem;">{o['name']} — Cursuri Online de Manichiură</p>
                        <p style="font-size:0.73rem;color:{sclr};margin-bottom:0.5rem;">{stxt}</p>
                        <p style="font-size:0.68rem;color:var(--muted);">Data comenzii: {o.get('date','—')}</p>
                        {"<p style='font-size:0.8rem;color:var(--gold);margin-top:0.5rem;'>🔗 <a href='https://drive.google.com' style='color:var(--gold);' target='_blank'>Accesează materialele Google Drive</a></p>" if act else ""}
                    </div>""", unsafe_allow_html=True)
                with cb:
                    if not act:
                        sp()
                        act_key = f"show_act_{o['name']}"
                        if act_key not in st.session_state:
                            st.session_state[act_key] = False
                        if not st.session_state[act_key]:
                            if st.button("🔓 Activează", key=f"a_{o['name']}"):
                                st.session_state[act_key] = True
                                st.rerun()
                        else:
                            act_pw = st.text_input("Parolă de activare", type="password", key=f"pw_{o['name']}", placeholder="Introdu parola")
                            col_ok, col_x = st.columns(2)
                            with col_ok:
                                if st.button("✓ Confirmă", key=f"conf_{o['name']}"):
                                    if act_pw == "nailacademy":
                                        for x in st.session_state.users[st.session_state.current_user]["orders"]:
                                            if x["name"] == o["name"]:
                                                x["activated"] = True
                                        st.session_state[act_key] = False
                                        save_current_user()
                                        st.success("Curs activat!")
                                        st.rerun()
                                    else:
                                        st.error("Parolă incorectă.")
                            with col_x:
                                if st.button("✕ Anulează", key=f"cancel_{o['name']}"):
                                    st.session_state[act_key] = False
                                    st.rerun()


elif st.session_state.page == "Coș":
    if not st.session_state.logged_in:
        st.warning("Autentifică-te mai întâi.")
    else:
        sp(2)
        st.markdown('<span class="eyebrow">Finalizare achiziție</span>', unsafe_allow_html=True)
        st.markdown('<span class="pg-title">Coșul <span class="g">tău</span></span>', unsafe_allow_html=True)
        rule()

        # ── Mini pachete summary ──
        st.markdown('<div class="sec-title" style="margin-bottom:1.2rem;">Pachetele <em>noastre</em></div>', unsafe_allow_html=True)
        pk1, pk2 = st.columns(2)
        with pk1:
            st.markdown("""
            <div class="card" style="border-top:2px solid var(--gold);border-radius:12px;">
                <p style="font-family:var(--serif);font-size:1.1rem;font-style:italic;color:var(--gold);margin-bottom:0.3rem;">Nivel 01 — Tehnici de bază</p>
                <p style="font-size:0.78rem;color:var(--muted);margin-bottom:0.8rem;">Ideal pentru începătoare · ~2 săptămâni</p>
                <p style="font-family:var(--serif);font-size:1.8rem;color:var(--gold);margin-bottom:0.6rem;">1.000 lei</p>
                <p style="font-size:0.75rem;color:var(--muted);line-height:1.9;">
                    ✦ Unghii scurte &nbsp;·&nbsp; ✦ Construcție pe tips<br>
                    ✦ Construcție pe șablon &nbsp;·&nbsp; ✦ Întreținere<br>
                    ✦ Acces video nelimitat &nbsp;·&nbsp; ✦ Diplomă
                </p>
            </div>""", unsafe_allow_html=True)
            sp()
            if st.button("Adaugă Nivel 1 în Coș", key="cart_add_n1"):
                if "Nivel 1" in [x["name"] for x in st.session_state.cart]:
                    st.info("Nivel 1 se află deja în coș.")
                else:
                    st.session_state.cart.append({"name":"Nivel 1","price":1000})
                    st.success("Nivel 1 adăugat!"); st.rerun()
        with pk2:
            st.markdown("""
            <div class="card card-rose" style="border-top:2px solid var(--rose);border-radius:12px;">
                <p style="font-family:var(--serif);font-size:1.1rem;font-style:italic;color:var(--rose);margin-bottom:0.3rem;">Nivel 02 — Tehnici avansate</p>
                <p style="font-size:0.78rem;color:var(--muted);margin-bottom:0.8rem;">Pentru cursante cu bază · ~2 săptămâni</p>
                <p style="font-family:var(--serif);font-size:1.8rem;color:var(--rose);margin-bottom:0.6rem;">1.500 lei</p>
                <p style="font-size:0.75rem;color:var(--muted);line-height:1.9;">
                    ✦ Formă pătrat arcuit &nbsp;·&nbsp; ✦ Formă balerină<br>
                    ✦ Tehnica French Glass &nbsp;·&nbsp; ✦ French de interior<br>
                    ✦ Acces video nelimitat &nbsp;·&nbsp; ✦ Diplomă
                </p>
            </div>""", unsafe_allow_html=True)
            sp()
            st.markdown('<div class="btn-rose">', unsafe_allow_html=True)
            if st.button("Adaugă Nivel 2 în Coș", key="cart_add_n2"):
                if "Nivel 2" in [x["name"] for x in st.session_state.cart]:
                    st.info("Nivel 2 se află deja în coș.")
                else:
                    st.session_state.cart.append({"name":"Nivel 2","price":1500})
                    st.success("Nivel 2 adăugat!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        rule()

        if not st.session_state.cart:
            st.markdown('<div class="card" style="text-align:center;padding:2.5rem;border-radius:12px;"><p style="font-family:var(--serif);font-size:1.3rem;font-style:italic;color:var(--muted);">Coșul tău este gol — adaugă un pachet de mai sus.</p></div>', unsafe_allow_html=True)
        else:
            bll, blr = st.columns([5,3])
            with bll:
                st.markdown('<div class="sec-title" style="margin-bottom:1rem;">Produse <em>selectate</em></div>', unsafe_allow_html=True)
                total = 0
                for i, item in enumerate(st.session_state.cart):
                    total += item["price"]
                    clr = "var(--gold)" if "1" in item["name"] else "var(--rose)"
                    ci2, crm = st.columns([8,1])
                    with ci2:
                        st.markdown(f"""
                        <div style="background:var(--surface);border:1px solid var(--border);
                                    border-left:2px solid {clr};padding:1.1rem 1.3rem;
                                    margin-bottom:0.7rem;border-radius:8px;">
                            <p style="font-family:var(--serif);font-size:1rem;color:var(--white);margin-bottom:0.25rem;">{item['name']}</p>
                            <p style="font-size:0.7rem;color:var(--muted);">~2 săptămâni · Video nelimitat · Diplomă inclusă</p>
                            <p style="font-family:var(--serif);font-size:1.25rem;color:{clr};margin-top:0.4rem;">{item['price']:,} lei</p>
                        </div>""", unsafe_allow_html=True)
                    with crm:
                        sp()
                        if st.button("✕", key=f"rm_{i}"):
                            st.session_state.cart.pop(i); st.rerun()
                rule()
                st.markdown(f"<div style='text-align:right;'><span style='font-size:0.68rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted);'>Total &nbsp;</span><span style='font-family:var(--serif);font-size:2rem;color:var(--gold);'>{total:,} lei</span></div>", unsafe_allow_html=True)

            with blr:
                sp()
                st.markdown("""
                <div class="card" style="border-radius:12px;">
                    <p style="font-size:0.6rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--muted);margin-bottom:1.2rem;">Instrucțiuni de plată</p>
                    <p style="font-size:0.7rem;color:var(--muted);margin-bottom:0.15rem;">Modalitate</p>
                    <p style="font-size:0.86rem;color:var(--white);margin-bottom:0.9rem;">Transfer bancar</p>
                    <p style="font-size:0.7rem;color:var(--muted);margin-bottom:0.15rem;">IBAN</p>
                    <p style="font-family:var(--serif);font-size:0.9rem;color:var(--gold);margin-bottom:0.9rem;letter-spacing:0.04em;">RO49 AAAA 1B31 0075 9384 0000</p>
                    <p style="font-size:0.7rem;color:var(--muted);margin-bottom:0.15rem;">Beneficiar</p>
                    <p style="font-size:0.86rem;color:var(--white);margin-bottom:0.9rem;">NailPro Academy SRL</p>
                    <p style="font-size:0.7rem;color:var(--muted);margin-bottom:0.15rem;">Detalii transfer</p>
                    <p style="font-size:0.84rem;color:var(--white);">Numele complet + cursul ales</p>
                </div>""", unsafe_allow_html=True)
                sp()
                uprofile = st.session_state.users[st.session_state.current_user].get("profile",{})
                with st.form("chf"):
                    cem = st.text_input("Email confirmare", value=st.session_state.current_user)
                    cph = st.text_input("Telefon", value=uprofile.get("telefon",""))
                    sp()
                    st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
                    go  = st.form_submit_button("Finalizează comanda")
                    st.markdown('</div>', unsafe_allow_html=True)
                    if go:
                        for item in st.session_state.cart:
                            st.session_state.users[st.session_state.current_user]["orders"].append({
                                "name":item["name"],"price":item["price"],
                                "date":datetime.now().strftime("%d.%m.%Y"),"activated":False})
                        st.session_state.cart = []
                        save_current_user()
                        st.success("Comanda a fost înregistrată cu succes!")
                        st.info(f"Detaliile de plată și link-ul de acces la cursuri vor fi trimise la **{cem}** în termen de 24 ore de la confirmarea plății.")


elif st.session_state.page == "Recenzii":
    sp(2)
    st.markdown('<span class="eyebrow">Experiențele cursantelor noastre</span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-title">Recenzii <span class="g">verificate</span></span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-lead">Opinii reale de la cursante care au parcurs programele NailPro Academy</span>', unsafe_allow_html=True)
    rule()

    reviews = db_get_reviews()


    if reviews:
        avg = sum(r["rating"] for r in reviews) / len(reviews)
        rc1, rc2, rc3 = st.columns([2,1,2])
        with rc2:
            st.markdown(f"""
            <div style="text-align:center;background:var(--surface);border:1px solid var(--border);
                        border-top:2px solid var(--gold);padding:1.5rem;border-radius:8px;">
                <p style="font-family:'Playfair Display',serif;font-size:3rem;color:var(--gold);
                           line-height:1;margin-bottom:0.3rem;">{avg:.1f}</p>
                <p style="font-size:1.2rem;color:var(--gold);margin-bottom:0.3rem;">{"★" * round(avg)}</p>
                <p style="font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted);">
                    {len(reviews)} recenzii
                </p>
            </div>""", unsafe_allow_html=True)

    sp(2)


    for i in range(0, len(reviews), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(reviews):
                rev = reviews[i+j]
                stars = "★" * rev["rating"] + "☆" * (5-rev["rating"])
                badge_clr = "var(--gold)" if "1" in rev["curs"] else "var(--rose)"
                with col:
                    st.markdown(f"""
                    <div class="card" style="margin-bottom:1rem;border-radius:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem;">
                            <span style="color:{badge_clr};font-size:1.05rem;">{stars}</span>
                            <span style="font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;
                                         color:{badge_clr};border:1px solid {badge_clr};
                                         padding:0.15rem 0.6rem;border-radius:20px;">{rev['curs']}</span>
                        </div>
                        <p style="font-family:'Playfair Display',serif;font-style:italic;font-size:0.95rem;
                                   color:#1A1208;line-height:1.9;margin-bottom:0.9rem;">"{rev['text']}"</p>
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <p style="font-size:0.78rem;font-weight:500;color:#3a2e1e;">{rev['nume']}</p>
                            <p style="font-size:0.62rem;color:var(--muted);">{rev['data']}</p>
                        </div>
                    </div>""", unsafe_allow_html=True)

    rule()


    if not st.session_state.logged_in:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem;border-radius:10px;">
            <p style="font-family:'Playfair Display',serif;font-style:italic;font-size:1.1rem;color:var(--muted);margin-bottom:0.5rem;">
                Autentifică-te pentru a lăsa o recenzie
            </p>
            <p style="font-size:0.75rem;color:var(--muted);">Recenziile pot fi scrise doar de cursante cu un curs achiziționat.</p>
        </div>""", unsafe_allow_html=True)
        sp()
        _, bl, _ = st.columns([2,2,2])
        with bl:
            st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
            if st.button("Intră în cont", key="rev_login"):
                st.session_state.page = "Auth"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        user_orders = st.session_state.users[st.session_state.current_user].get("orders", [])
        has_order   = len(user_orders) > 0
        has_review  = db_user_has_review(st.session_state.current_user)

        if not has_order:
            st.markdown("""
            <div class="card" style="text-align:center;padding:1.8rem;border-radius:10px;">
                <p style="font-family:'Playfair Display',serif;font-style:italic;font-size:1rem;color:var(--muted);">
                    Recenziile pot fi scrise doar după achiziționarea unui curs.
                </p>
            </div>""", unsafe_allow_html=True)
        elif has_review:
            st.markdown("""
            <div class="card" style="text-align:center;padding:1.8rem;border-radius:10px;">
                <p style="color:#4caf7d;font-size:1rem;">✅ Ai lăsat deja o recenzie. Mulțumim!</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="sec-title">Lasă o <em>recenzie</em></div>', unsafe_allow_html=True)
            sp()
            _, rev_mid, _ = st.columns([1,4,1])
            with rev_mid:
                with st.form("rev_form"):
                    prof = st.session_state.users[st.session_state.current_user].get("profile",{})
                    default_name = f"{prof.get('prenume','')} {prof.get('nume','')}".strip() or st.session_state.current_user.split("@")[0]
                    rev_name  = st.text_input("Numele tău", value=default_name)
                    rev_curs  = st.selectbox("Cursul urmat", [o["name"] for o in user_orders])
                    rev_rat   = st.select_slider("Rating", options=[1,2,3,4,5], value=5,
                                                  format_func=lambda x: "★"*x + "☆"*(5-x))
                    rev_text  = st.text_area("Experiența ta", height=120, placeholder="Povestește-ne despre experiența ta cu NailPro Academy...")
                    sp()
                    st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
                    submit_rev = st.form_submit_button("Publică recenzia")
                    st.markdown('</div>', unsafe_allow_html=True)
                    if submit_rev:
                        if not rev_text.strip():
                            st.error("Scrie un text pentru recenzie.")
                        else:
                            db_add_review(st.session_state.current_user, rev_name, rev_curs, rev_rat, rev_text)
                            st.success("Recenzia ta a fost publicată! Mulțumim 💛")
                            st.rerun()


elif st.session_state.page == "Blog":
    sp(2)
    st.markdown('<span class="eyebrow">Sfaturi & inspirație</span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-title">Blog <span class="g">NailPro</span></span>', unsafe_allow_html=True)
    st.markdown('<span class="pg-lead">Articole despre tehnici, tendințe și îngrijirea unghiilor</span>', unsafe_allow_html=True)
    rule()

    blog_posts = [
        {
            "titlu": "Top 5 greșeli ale începătoarelor în nail art",
            "data": "10 Aprilie 2025",
            "categorie": "Tehnici",
            "clr": "var(--gold)",
            "text": """Când ești la început, e normal să faci greșeli. Dar câteva dintre ele pot compromite întreaga lucrare. Prima și cea mai frecventă greșeală este aplicarea unui strat prea gros de produs — acesta nu se polimerizeazã corect și duce la crăpare. A doua greșeală este neglijarea pregătirii unghiei naturale: cuticulele neîndepărtate și suprafața neprelucrată duc la o aderență slabă.

A treia greșeală este graba — fiecare strat trebuie polimerizat complet înainte de aplicarea urmãtorului. Urmează lipsa de simetrie în forma unghiei, care face ca lucrarea să arate neprofesionistă chiar dacă tehnica este corectã. Și nu în ultimul rând, folosirea produselor de calitate scăzutã care nu sunt compatibile între ele.

La NailPro Academy, toate aceste aspecte sunt acoperite pas cu pas în modulele noastre.""",
            "emoji": "💅"
        },
        {
            "titlu": "Tendințe nail art în 2025: ce e la modă",
            "data": "28 Martie 2025",
            "categorie": "Tendințe",
            "clr": "var(--rose)",
            "text": """2025 aduce o estetică rafinatã în lumea nail art-ului. Nuanțele nude cu accente aurii sau argintii continuă să domine, alături de tehnica French Glass — un efect translucid, modern, care mimează unghia naturală dar cu un plus de eleganță.

Forma balerină (coffin) rămâne preferata profesioniștilor, în timp ce unghiile scurte și pătrate câștigã teren printre cele care preferă un look îngrijit și practic. Nail art-ul minimal — o linie subțire, un punct discret, un detaliu geometric — înlocuiește treptat decorurile elaborate.

Toate aceste tehnici sunt predate în cadrul cursurilor Nivel 2 NailPro Academy.""",
            "emoji": "✨"
        },
        {
            "titlu": "Cum îți construiești un portofoliu ca nail artist",
            "data": "14 Martie 2025",
            "categorie": "Carieră",
            "clr": "var(--gold)",
            "text": """Un portofoliu bun este cartea ta de vizitã ca nail artist. Primul pas este să fotografiezi fiecare lucrare finalizatã, cu lumină naturală și fundal neutru. Calitatea imaginilor contează — un telefon bun e suficient, dar unghi și lumina fac diferența.

Organizează-ți lucrările pe categorii: unghii scurte, construcție pe șablon, French, nail art etc. Instagram rămâne platforma principalã pentru nail artists — postează constant, folosește hashtag-uri relevante și interacționează cu comunitatea.

După absolvirea cursurilor NailPro Academy primești o diplomã recunoscutã, pe care o poți adăuga în bio-ul de Instagram sau pe un viitor site personal.""",
            "emoji": "📸"
        },
    ]

    for i, post in enumerate(blog_posts):
        bl1, bl2 = st.columns([1, 2]) if i % 2 == 0 else [None, None]
        st.markdown(f"""
        <div class="card" style="border-radius:12px;margin-bottom:1.5rem;border-left:3px solid {post['clr']};">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                <span style="font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;
                             color:{post['clr']};border:1px solid {post['clr']};
                             padding:0.2rem 0.7rem;border-radius:20px;">{post['categorie']}</span>
                <span style="font-size:0.65rem;color:var(--muted);">{post['data']}</span>
            </div>
            <p style="font-family:'Playfair Display',serif;font-size:1.3rem;font-style:italic;
                       color:#1A1208;margin-bottom:0.8rem;">{post['emoji']} {post['titlu']}</p>
            <div style="font-size:0.88rem;font-weight:300;color:#3a2e1e;line-height:2.0;">
                {''.join(f"<p style='margin-bottom:0.7rem;'>{p.strip()}</p>" for p in post['text'].strip().split(chr(10)+chr(10)) if p.strip())}
            </div>
        </div>""", unsafe_allow_html=True)

    rule()


    st.markdown('<span class="eyebrow">Rămâi la curent</span>', unsafe_allow_html=True)
    sp()
    st.markdown('<div class="sec-title" style="text-align:center;">Abonează-te la <em>newsletter</em></div>', unsafe_allow_html=True)
    sp()
    _, nl_mid, _ = st.columns([2,3,2])
    with nl_mid:
        with st.form("nl_form"):
            nl_email = st.text_input("Adresa ta de email", placeholder="exemplu@email.ro")
            st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
            nl_sub = st.form_submit_button("Abonează-mă")
            st.markdown('</div>', unsafe_allow_html=True)
            if nl_sub:
                if nl_email and "@" in nl_email:
                    st.success("Te-ai abonat cu succes! Vei primi cele mai noi articole și oferte.")
                else:
                    st.error("Introdu o adresă de email validă.")


sp(3)


if "sat_done" not in st.session_state:
    st.session_state.sat_done = False

if not st.session_state.sat_done:
    with st.expander("💬 Cum ți s-a părut site-ul? Ajută-ne cu un feedback rapid (30 sec)"):
        with st.form("sat_form"):
            sat1 = st.select_slider("Cât de utilă ți s-a părut informația de pe site?",
                                     options=["1 – Deloc","2","3","4","5 – Foarte utilă"], value="4")
            sat2 = st.radio("Ai găsit ce căutai?", ["Da, ușor", "Parțial", "Nu"], horizontal=True)
            sat3 = st.text_area("Orice sugestie sau comentariu (opțional)", height=70)
            st.markdown('<div class="btn-fill">', unsafe_allow_html=True)
            sat_go = st.form_submit_button("Trimite feedback")
            st.markdown('</div>', unsafe_allow_html=True)
            if sat_go:
                st.session_state.sat_done = True
                st.success("Mulțumim pentru feedback! 💛")
                st.rerun()

sp(2)
st.markdown("""
<div style="border-top:1px solid #C8B89A;padding-top:1.8rem;text-align:center;">
    <p style="font-family:'Playfair Display',serif;font-style:italic;
              font-size:0.95rem;color:#8B5E1A;margin-bottom:0.6rem;">NailPro Academy</p>
    <div style="display:flex;justify-content:center;gap:1.5rem;margin-bottom:0.8rem;">
        <a href="https://www.facebook.com/share/18e1ZfkwW1/?mibextid=wwXIfr" target="_blank"
           style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;
                  color:#1877F2;text-decoration:none;">📘 Facebook</a>
        <a href="https://www.instagram.com/nailproacademy.online" target="_blank"
           style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;
                  color:#E1306C;text-decoration:none;">📸 Instagram</a>
    </div>
    <p style="font-size:0.58rem;letter-spacing:0.28em;text-transform:uppercase;color:#7a6040;">
        © 2025 · Constanța, România · contact@nailproacademy.ro
    </p>
</div>""", unsafe_allow_html=True)
