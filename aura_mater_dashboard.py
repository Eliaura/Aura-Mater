import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="AURA Energy — MATER 2T2026",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0F1923; }
[data-testid="stSidebar"] * { color: #E8F0FE !important; }
[data-testid="stSidebar"] .stSlider > div > div > div { background: #2E75B6; }
h1 { color: #1F3864; font-size: 1.6rem; }
h2 { color: #1F3864; font-size: 1.2rem; }
h3 { color: #2E75B6; font-size: 1rem; }
.metric-card {
    background: white; border-radius: 10px; padding: 16px 20px;
    border-left: 4px solid #2E75B6; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    margin-bottom: 8px;
}
.metric-val { font-size: 2rem; font-weight: 600; color: #1F3864; line-height: 1.1; }
.metric-lbl { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: .06em; }
.seg-aura  { background:#EAF3DE; color:#3B6D11; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
.seg-terc  { background:#E1F5EE; color:#0F6E56; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
.seg-mon   { background:#F5F5F5; color:#888;    padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ─── DATOS ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    raw = [{"id":"1142","nombre":"OLAVARRIA 500KV","corredor":"PBA CENTRO-SUR","cap":200,"ghi":1550,"lat":-36.9,"lon":-60.3},{"id":"1052","nombre":"BRANDSEN","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1510,"lat":None,"lon":None},{"id":"1054","nombre":"CHASCOMUS","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1510,"lat":None,"lon":None},{"id":"1199","nombre":"MONTE","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1520,"lat":None,"lon":None},{"id":"9464","nombre":"BRANDSEN","corredor":"PBA CENTRO-SUR","cap":15,"ghi":1510,"lat":None,"lon":None},{"id":"1195","nombre":"NEWTON","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1530,"lat":None,"lon":None},{"id":"1191","nombre":"LAS FLORES","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1530,"lat":None,"lon":None},{"id":"1193","nombre":"SALADILLO","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1530,"lat":-35.6,"lon":-59.8},{"id":"1197","nombre":"ROSAS","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1530,"lat":None,"lon":None},{"id":"1187","nombre":"RAUCH","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1570,"lat":-36.8,"lon":-59.3},{"id":"1184","nombre":"AZUL","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1570,"lat":-36.8,"lon":-59.8},{"id":"1189","nombre":"CACHARI","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1580,"lat":-37.6,"lon":-59.5},{"id":"1136","nombre":"OLAVARRIA 132KV","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1550,"lat":None,"lon":None},{"id":"1156","nombre":"BARKER II","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1550,"lat":None,"lon":None},{"id":"1166","nombre":"ET LOS TEROS","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1550,"lat":None,"lon":None},{"id":"1173","nombre":"BOLIVAR","corredor":"PBA CENTRO-SUR","cap":10,"ghi":1560,"lat":None,"lon":None},{"id":"1135","nombre":"OLAVARRIA VIEJA","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1550,"lat":None,"lon":None},{"id":"1153","nombre":"LOMA NEGRA","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1550,"lat":None,"lon":None},{"id":"1154","nombre":"CALERA AVELLANEDA","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1550,"lat":None,"lon":None},{"id":"1158","nombre":"BARKER","corredor":"PBA CENTRO-SUR","cap":30,"ghi":1570,"lat":None,"lon":None},{"id":"1169","nombre":"TANDIL INDUSTRIAL","corredor":"PBA CENTRO-SUR","cap":30,"ghi":1570,"lat":None,"lon":None},{"id":"1178","nombre":"TANDIL","corredor":"PBA CENTRO-SUR","cap":30,"ghi":1570,"lat":None,"lon":None},{"id":"2047","nombre":"TANDIL","corredor":"PBA CENTRO-SUR","cap":12,"ghi":1570,"lat":None,"lon":None},{"id":"1141","nombre":"GONZALEZ CHAVES","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1620,"lat":-38.0,"lon":-60.1},{"id":"1137","nombre":"CHILLAR","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1590,"lat":-37.6,"lon":-60.1},{"id":"1260","nombre":"BAHÍA BLANCA 500 kV","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1600,"lat":-38.7,"lon":-62.3},{"id":"1270","nombre":"GUILLERMO BROWN","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1600,"lat":None,"lon":None},{"id":"1250","nombre":"BAHÍA BLANCA 132 kV","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1600,"lat":-38.7,"lon":-62.3},{"id":"1161","nombre":"CORONEL DORREGO","corredor":"PBA CENTRO-SUR","cap":5,"ghi":1590,"lat":None,"lon":None},{"id":"1174","nombre":"BAJO HONDO","corredor":"PBA CENTRO-SUR","cap":5,"ghi":1590,"lat":None,"lon":None},{"id":"1176","nombre":"MONTE HERMOSO","corredor":"PBA CENTRO-SUR","cap":5,"ghi":1610,"lat":None,"lon":None},{"id":"1013","nombre":"ET BAHÍA BLANCA SUR","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1600,"lat":None,"lon":None},{"id":"1240","nombre":"CHAÑARES","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1600,"lat":-38.5,"lon":-62.3},{"id":"1243","nombre":"ET LA CASTELLANA","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1600,"lat":-38.5,"lon":-62.2},{"id":"1147","nombre":"CNEL SUAREZ","corredor":"PBA CENTRO-SUR","cap":15,"ghi":1580,"lat":None,"lon":None},{"id":"1148","nombre":"CNEL SUAREZ","corredor":"PBA CENTRO-SUR","cap":24,"ghi":1580,"lat":None,"lon":None},{"id":"1150","nombre":"CORTI","corredor":"PBA CENTRO-SUR","cap":40,"ghi":1580,"lat":None,"lon":None},{"id":"1212","nombre":"VILLALONGA","corredor":"PBA CENTRO-SUR","cap":20,"ghi":1590,"lat":None,"lon":None},{"id":"1220","nombre":"CARMEN DE PATAGONES","corredor":"PBA CENTRO-SUR","cap":20,"ghi":1600,"lat":None,"lon":None},{"id":"1230","nombre":"PUNTA ALTA","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1610,"lat":-38.9,"lon":-62.1},{"id":"1233","nombre":"PUNTA ALTA","corredor":"PBA CENTRO-SUR","cap":15,"ghi":1610,"lat":None,"lon":None},{"id":"1145","nombre":"PIGUE","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1570,"lat":-37.9,"lon":-63.0},{"id":"1146","nombre":"CNEL SUAREZ","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1570,"lat":None,"lon":None},{"id":"1159","nombre":"TRES PICOS","corredor":"PBA CENTRO-SUR","cap":30,"ghi":1560,"lat":None,"lon":None},{"id":"1163","nombre":"TORNQUIST","corredor":"PBA CENTRO-SUR","cap":35,"ghi":1560,"lat":-38.1,"lon":-62.2},{"id":"1165","nombre":"PUAN","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1570,"lat":-37.8,"lon":-63.0},{"id":"1171","nombre":"TORNQUIST","corredor":"PBA CENTRO-SUR","cap":50,"ghi":1570,"lat":-38.1,"lon":-62.2},{"id":"1047","nombre":"INDIO RICO","corredor":"PBA CENTRO-SUR","cap":20,"ghi":1580,"lat":None,"lon":None},{"id":"1055","nombre":"LA GENOVEVA","corredor":"PBA CENTRO-SUR","cap":25,"ghi":1580,"lat":None,"lon":None},{"id":"1130","nombre":"CNEL PRINGLES","corredor":"PBA CENTRO-SUR","cap":20,"ghi":1580,"lat":None,"lon":None},{"id":"1132","nombre":"LAPRIDA","corredor":"PBA CENTRO-SUR","cap":25,"ghi":1570,"lat":None,"lon":None},{"id":"2030","nombre":"VIVORATÁ","corredor":"COSTA ATLÁNTICA","cap":100,"ghi":1590,"lat":-37.5,"lon":-57.1},{"id":"2032","nombre":"BALCARCE 132","corredor":"COSTA ATLÁNTICA","cap":78,"ghi":1600,"lat":-37.9,"lon":-58.2},{"id":"2033","nombre":"BALCARCE 33","corredor":"COSTA ATLÁNTICA","cap":25,"ghi":1600,"lat":None,"lon":None},{"id":"2036","nombre":"NUMANCIA","corredor":"COSTA ATLÁNTICA","cap":18,"ghi":1600,"lat":None,"lon":None},{"id":"2044","nombre":"VILLA GESELL","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1560,"lat":-37.3,"lon":-56.9},{"id":"2010","nombre":"MIRAMAR","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1520,"lat":-38.3,"lon":-57.8},{"id":"2014","nombre":"MIRAMAR DOS","corredor":"COSTA ATLÁNTICA","cap":30,"ghi":1520,"lat":None,"lon":None},{"id":"2017","nombre":"MAR DEL PLATA INDUSTRIAL","corredor":"COSTA ATLÁNTICA","cap":30,"ghi":1520,"lat":None,"lon":None},{"id":"2020","nombre":"NECOCHEA","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1590,"lat":-38.6,"lon":-58.7},{"id":"2040","nombre":"VIVORATÁ","corredor":"COSTA ATLÁNTICA","cap":100,"ghi":1530,"lat":None,"lon":None},{"id":"2041","nombre":"MAR DEL PLATA","corredor":"COSTA ATLÁNTICA","cap":100,"ghi":1530,"lat":-38.0,"lon":-57.5},{"id":"2001","nombre":"PINAMAR","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1510,"lat":-37.1,"lon":-56.9},{"id":"2002","nombre":"MAR DEL TUYÚ","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1510,"lat":None,"lon":None},{"id":"2003","nombre":"SAN CLEMENTE DEL TUYÚ","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1510,"lat":None,"lon":None},{"id":"2009","nombre":"MAR DE AJO","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1510,"lat":None,"lon":None},{"id":"2012","nombre":"LAS TONINAS","corredor":"COSTA ATLÁNTICA","cap":50,"ghi":1510,"lat":None,"lon":None},{"id":"2013","nombre":"LAS TONINAS","corredor":"COSTA ATLÁNTICA","cap":20,"ghi":1510,"lat":None,"lon":None},{"id":"7070","nombre":"SAN LORENZO","corredor":"LITORAL","cap":88,"ghi":1480,"lat":None,"lon":None},{"id":"7077","nombre":"CALCHAQUI","corredor":"LITORAL","cap":100,"ghi":1500,"lat":-29.9,"lon":-60.1},{"id":"7078","nombre":"GOBERNADOR CRESPO","corredor":"LITORAL","cap":75,"ghi":1500,"lat":None,"lon":None},{"id":"7079","nombre":"SAN JAVIER","corredor":"LITORAL","cap":50,"ghi":1500,"lat":None,"lon":None},{"id":"7081","nombre":"SALTO GRANDE","corredor":"LITORAL","cap":300,"ghi":1490,"lat":-31.4,"lon":-58.0},{"id":"7082","nombre":"CONCORDIA","corredor":"LITORAL","cap":300,"ghi":1490,"lat":-31.4,"lon":-58.0},{"id":"7083","nombre":"CONCORDIA","corredor":"LITORAL","cap":50,"ghi":1490,"lat":None,"lon":None},{"id":"7084","nombre":"MASISA","corredor":"LITORAL","cap":180,"ghi":1490,"lat":None,"lon":None},{"id":"7085","nombre":"RIO URUGUAY","corredor":"LITORAL","cap":120,"ghi":1490,"lat":None,"lon":None},{"id":"7020","nombre":"CAÑADA DE GOMEZ","corredor":"LITORAL","cap":100,"ghi":1500,"lat":None,"lon":None},{"id":"7034","nombre":"CHABAS","corredor":"LITORAL","cap":150,"ghi":1500,"lat":-33.2,"lon":-61.3},{"id":"7010","nombre":"VENADO TUERTO","corredor":"LITORAL","cap":92,"ghi":1510,"lat":-33.8,"lon":-61.9},{"id":"7019","nombre":"FIRMAT","corredor":"LITORAL","cap":110,"ghi":1510,"lat":-33.5,"lon":-61.5},{"id":"7000","nombre":"RUFINO","corredor":"LITORAL","cap":70,"ghi":1520,"lat":-34.5,"lon":-62.7},{"id":"7076","nombre":"RECONQUISTA","corredor":"LITORAL","cap":70,"ghi":1520,"lat":-29.1,"lon":-59.6},{"id":"7074","nombre":"AVELLANEDA","corredor":"LITORAL","cap":70,"ghi":1510,"lat":None,"lon":None},{"id":"7075","nombre":"CHAPERO","corredor":"LITORAL","cap":70,"ghi":1510,"lat":None,"lon":None},{"id":"7060","nombre":"VILLA OCAMPO","corredor":"LITORAL","cap":100,"ghi":1520,"lat":-28.5,"lon":-59.7},{"id":"7057","nombre":"ESPERANZA","corredor":"LITORAL","cap":100,"ghi":1490,"lat":-31.4,"lon":-60.9},{"id":"7059","nombre":"SANTO TOME","corredor":"LITORAL","cap":100,"ghi":1490,"lat":-31.4,"lon":-60.9},{"id":"7029","nombre":"SAN CARLOS","corredor":"LITORAL","cap":76,"ghi":1490,"lat":None,"lon":None},{"id":"7031","nombre":"MARIA JUANA","corredor":"LITORAL","cap":76,"ghi":1490,"lat":None,"lon":None},{"id":"7032","nombre":"SAN JORGE","corredor":"LITORAL","cap":76,"ghi":1490,"lat":None,"lon":None},{"id":"7058","nombre":"SANTA FE OESTE","corredor":"LITORAL","cap":150,"ghi":1480,"lat":-31.6,"lon":-60.7},{"id":"7004","nombre":"SAN JERÓNIMO NORTE","corredor":"LITORAL","cap":90,"ghi":1490,"lat":None,"lon":None},{"id":"7053","nombre":"RAFAELA OESTE","corredor":"LITORAL","cap":90,"ghi":1490,"lat":None,"lon":None},{"id":"7054","nombre":"RAFAELA SUR","corredor":"LITORAL","cap":90,"ghi":1490,"lat":None,"lon":None},{"id":"7021","nombre":"TOSTADO","corredor":"LITORAL","cap":30,"ghi":1520,"lat":None,"lon":None},{"id":"7023","nombre":"CERES","corredor":"LITORAL","cap":40,"ghi":1520,"lat":None,"lon":None},{"id":"7025","nombre":"SAN GUILLERMO","corredor":"LITORAL","cap":50,"ghi":1520,"lat":None,"lon":None},{"id":"7027","nombre":"ARRUFO","corredor":"LITORAL","cap":60,"ghi":1520,"lat":None,"lon":None},{"id":"7050","nombre":"SUNCHALES","corredor":"LITORAL","cap":90,"ghi":1520,"lat":None,"lon":None},{"id":"7001","nombre":"RAFAELA NORTE","corredor":"LITORAL","cap":90,"ghi":1520,"lat":None,"lon":None},{"id":"8001","nombre":"EL DORADO","corredor":"MISIONES","cap":94,"ghi":1380,"lat":None,"lon":None},{"id":"8002","nombre":"EL DORADO","corredor":"MISIONES","cap":44,"ghi":1380,"lat":None,"lon":None},{"id":"8006","nombre":"IGUAZU","corredor":"MISIONES","cap":44,"ghi":1380,"lat":None,"lon":None},{"id":"8007","nombre":"IGUAZU","corredor":"MISIONES","cap":40,"ghi":1380,"lat":None,"lon":None},{"id":"8027","nombre":"PTO MINERAL - B1","corredor":"MISIONES","cap":40,"ghi":1380,"lat":None,"lon":None},{"id":"8028","nombre":"PTO MINERAL - B1","corredor":"MISIONES","cap":40,"ghi":1380,"lat":None,"lon":None},{"id":"8004","nombre":"WANDA","corredor":"MISIONES","cap":40,"ghi":1380,"lat":None,"lon":None},{"id":"8050","nombre":"WANDA","corredor":"MISIONES","cap":25,"ghi":1380,"lat":None,"lon":None},{"id":"8046","nombre":"OBERA","corredor":"MISIONES","cap":25,"ghi":1400,"lat":None,"lon":None},{"id":"8049","nombre":"OBERA","corredor":"MISIONES","cap":60,"ghi":1400,"lat":None,"lon":None},{"id":"8024","nombre":"OBERA II","corredor":"MISIONES","cap":60,"ghi":1400,"lat":None,"lon":None},{"id":"8025","nombre":"OBERA II","corredor":"MISIONES","cap":20,"ghi":1400,"lat":None,"lon":None},{"id":"8014","nombre":"ARISTOBULO DEL VALLE","corredor":"MISIONES","cap":20,"ghi":1390,"lat":None,"lon":None},{"id":"8015","nombre":"ARISTOBULO DEL VALLE","corredor":"MISIONES","cap":27,"ghi":1390,"lat":None,"lon":None},{"id":"8011","nombre":"PTO MINERAL - B2","corredor":"MISIONES","cap":27,"ghi":1390,"lat":None,"lon":None},{"id":"8012","nombre":"PTO MINERAL - B2","corredor":"MISIONES","cap":40,"ghi":1390,"lat":None,"lon":None},{"id":"8017","nombre":"SAN VICENTE","corredor":"MISIONES","cap":40,"ghi":1390,"lat":None,"lon":None},{"id":"8030","nombre":"CORRIENTES ESTE","corredor":"NEA","cap":265,"ghi":1600,"lat":-27.5,"lon":-58.8},{"id":"8089","nombre":"FORMOSA","corredor":"NEA","cap":265,"ghi":1650,"lat":-26.2,"lon":-58.2},{"id":"8047","nombre":"BELLA VISTA","corredor":"NEA","cap":83,"ghi":1610,"lat":-28.5,"lon":-59.1},{"id":"8060","nombre":"SANTA ROSA","corredor":"NEA","cap":15,"ghi":1610,"lat":None,"lon":None},{"id":"8125","nombre":"BELLA VISTA","corredor":"NEA","cap":28,"ghi":1610,"lat":None,"lon":None},{"id":"8126","nombre":"BELLA VISTA","corredor":"NEA","cap":40,"ghi":1610,"lat":None,"lon":None},{"id":"8116","nombre":"COLONIA BRUGNE","corredor":"NEA","cap":110,"ghi":1620,"lat":-30.2,"lon":-59.3},{"id":"8117","nombre":"COLONIA BRUGNE","corredor":"NEA","cap":30,"ghi":1620,"lat":None,"lon":None},{"id":"8113","nombre":"SANTA CATALINA","corredor":"NEA","cap":265,"ghi":1620,"lat":-29.2,"lon":-58.8},{"id":"8114","nombre":"SANTA CATALINA","corredor":"NEA","cap":70,"ghi":1620,"lat":None,"lon":None},{"id":"8115","nombre":"SANTA CATALINA","corredor":"NEA","cap":80,"ghi":1620,"lat":None,"lon":None},{"id":"8085","nombre":"CLORINDA","corredor":"NEA","cap":20,"ghi":1650,"lat":None,"lon":None},{"id":"8086","nombre":"CLORINDA","corredor":"NEA","cap":10,"ghi":1650,"lat":None,"lon":None},{"id":"8087","nombre":"CLORINDA","corredor":"NEA","cap":10,"ghi":1650,"lat":None,"lon":None},{"id":"8077","nombre":"VG GUEMES","corredor":"NEA","cap":10,"ghi":1640,"lat":None,"lon":None},{"id":"8078","nombre":"VG GUEMES","corredor":"NEA","cap":20,"ghi":1640,"lat":None,"lon":None},{"id":"8079","nombre":"VG GUEMES","corredor":"NEA","cap":20,"ghi":1640,"lat":None,"lon":None},{"id":"8081","nombre":"LAGUNA BLANCA","corredor":"NEA","cap":20,"ghi":1640,"lat":None,"lon":None},{"id":"8110","nombre":"CASTELLI","corredor":"NEA","cap":10,"ghi":1680,"lat":None,"lon":None},{"id":"8111","nombre":"CASTELLI","corredor":"NEA","cap":10,"ghi":1680,"lat":None,"lon":None},{"id":"8140","nombre":"ESQUINA","corredor":"NEA","cap":5,"ghi":1620,"lat":None,"lon":None},{"id":"8133","nombre":"GOYA","corredor":"NEA","cap":5,"ghi":1620,"lat":None,"lon":None},{"id":"8131","nombre":"GOYA OESTE","corredor":"NEA","cap":15,"ghi":1620,"lat":None,"lon":None},{"id":"8127","nombre":"PASO TALA","corredor":"NEA","cap":15,"ghi":1620,"lat":None,"lon":None},{"id":"8128","nombre":"PASO TALA","corredor":"NEA","cap":10,"ghi":1620,"lat":None,"lon":None},{"id":"8136","nombre":"STELLA MARIS","corredor":"NEA","cap":10,"ghi":1620,"lat":None,"lon":None},{"id":"8137","nombre":"STELLA MARIS","corredor":"NEA","cap":5,"ghi":1620,"lat":None,"lon":None},{"id":"8142","nombre":"RINCON","corredor":"NEA","cap":7,"ghi":1620,"lat":None,"lon":None},{"id":"8152","nombre":"SAN ALONSO","corredor":"NEA","cap":7,"ghi":1620,"lat":None,"lon":None},{"id":"8155","nombre":"SANTO TOMÉ (CORRIENTES)","corredor":"NEA","cap":7,"ghi":1620,"lat":None,"lon":None},{"id":"8042","nombre":"SANTO TOMÉ (CORRIENTES)","corredor":"NEA","cap":15,"ghi":1620,"lat":None,"lon":None},{"id":"8153","nombre":"VIRASORO","corredor":"NEA","cap":15,"ghi":1620,"lat":None,"lon":None},{"id":"8045","nombre":"VIRASORO","corredor":"NEA","cap":30,"ghi":1620,"lat":-28.1,"lon":-56.1},{"id":"8154","nombre":"VIRASORO","corredor":"NEA","cap":30,"ghi":1620,"lat":None,"lon":None},{"id":"8143","nombre":"IITUZAINGO NORTE","corredor":"NEA","cap":30,"ghi":1610,"lat":None,"lon":None},{"id":"8144","nombre":"IITUZAINGO NORTE","corredor":"NEA","cap":25,"ghi":1610,"lat":None,"lon":None},{"id":"8149","nombre":"ITA-IBATE","corredor":"NEA","cap":25,"ghi":1610,"lat":None,"lon":None},{"id":"8150","nombre":"ITA-IBATE","corredor":"NEA","cap":30,"ghi":1610,"lat":None,"lon":None},{"id":"8146","nombre":"PI ITUZAINGO","corredor":"NEA","cap":30,"ghi":1610,"lat":None,"lon":None},{"id":"8147","nombre":"PI ITUZAINGO","corredor":"NEA","cap":15,"ghi":1610,"lat":None,"lon":None},{"id":"8063","nombre":"IBARRETA","corredor":"NEA","cap":5,"ghi":1660,"lat":None,"lon":None},{"id":"8056","nombre":"ING. JUAREZ","corredor":"NEA","cap":15,"ghi":1660,"lat":-23.9,"lon":-61.8},{"id":"8057","nombre":"ING. JUAREZ","corredor":"NEA","cap":10,"ghi":1660,"lat":None,"lon":None},{"id":"8059","nombre":"LAS LOMITAS","corredor":"NEA","cap":15,"ghi":1660,"lat":-24.1,"lon":-60.6},{"id":"8052","nombre":"LAS LOMITAS","corredor":"NEA","cap":8,"ghi":1660,"lat":None,"lon":None},{"id":"8061","nombre":"LAS LOMITAS","corredor":"NEA","cap":8,"ghi":1660,"lat":None,"lon":None},{"id":"8073","nombre":"COLORADO","corredor":"NEA","cap":8,"ghi":1670,"lat":-26.0,"lon":-58.6},{"id":"8074","nombre":"COLORADO","corredor":"NEA","cap":30,"ghi":1670,"lat":-26.0,"lon":-58.6},{"id":"8067","nombre":"PIRANE","corredor":"NEA","cap":25,"ghi":1670,"lat":None,"lon":None},{"id":"8072","nombre":"COLORADO","corredor":"NEA","cap":25,"ghi":1670,"lat":None,"lon":None},{"id":"8068","nombre":"PIRANE","corredor":"NEA","cap":5,"ghi":1670,"lat":None,"lon":None},{"id":"8069","nombre":"PIRANE","corredor":"NEA","cap":5,"ghi":1670,"lat":None,"lon":None},{"id":"8167","nombre":"RESISTENCIA","corredor":"NEA","cap":5,"ghi":1640,"lat":-27.5,"lon":-59.0},{"id":"8168","nombre":"LEONESA","corredor":"NEA","cap":25,"ghi":1640,"lat":None,"lon":None},{"id":"8169","nombre":"LEONESA","corredor":"NEA","cap":25,"ghi":1640,"lat":None,"lon":None},{"id":"8000","nombre":"T LA ESCONDIDA","corredor":"NEA","cap":25,"ghi":1680,"lat":-27.3,"lon":-60.5},{"id":"8164","nombre":"LA ESCONDIDA SOLAR","corredor":"NEA","cap":25,"ghi":1680,"lat":None,"lon":None},{"id":"8119","nombre":"PRES. ROCA","corredor":"NEA","cap":60,"ghi":1680,"lat":-26.9,"lon":-60.2},{"id":"8122","nombre":"SAN MARTIN","corredor":"NEA","cap":65,"ghi":1680,"lat":-26.9,"lon":-60.3},{"id":"8160","nombre":"MACHAGAI","corredor":"NEA","cap":80,"ghi":1680,"lat":-27.3,"lon":-60.4},{"id":"8161","nombre":"PRES DE LA PLAZA","corredor":"NEA","cap":99,"ghi":1680,"lat":-27.3,"lon":-60.4},{"id":"9010","nombre":"PANTANOSA","corredor":"GBA","cap":240,"ghi":1390,"lat":-34.8,"lon":-58.6},{"id":"9016","nombre":"ABASTO","corredor":"GBA","cap":500,"ghi":1390,"lat":-35.0,"lon":-58.5},{"id":"9020","nombre":"TOLOSA","corredor":"GBA","cap":240,"ghi":1390,"lat":-34.9,"lon":-57.9},{"id":"9030","nombre":"VILLA DOMINICO","corredor":"GBA","cap":100,"ghi":1390,"lat":-34.7,"lon":-58.3},{"id":"9017","nombre":"LA PLATA (BARRA 2)","corredor":"GBA","cap":100,"ghi":1390,"lat":-35.0,"lon":-57.9},{"id":"9018","nombre":"KAISER 2","corredor":"GBA","cap":86,"ghi":1390,"lat":None,"lon":None},{"id":"9022","nombre":"KAISER 1","corredor":"GBA","cap":110,"ghi":1390,"lat":None,"lon":None},{"id":"9451","nombre":"VERÓNICA","corredor":"BS. AS.","cap":80,"ghi":1420,"lat":None,"lon":None},{"id":"9462","nombre":"CAMPANA III","corredor":"BS. AS.","cap":150,"ghi":1430,"lat":-34.2,"lon":-58.9},{"id":"9000","nombre":"LUJÁN I","corredor":"BS. AS.","cap":120,"ghi":1450,"lat":-34.6,"lon":-59.1},{"id":"9454","nombre":"LUJÁN II","corredor":"BS. AS.","cap":90,"ghi":1450,"lat":-34.6,"lon":-59.1},{"id":"9456","nombre":"MERCEDES","corredor":"BS. AS.","cap":120,"ghi":1470,"lat":-34.7,"lon":-59.4},{"id":"9458","nombre":"CHIVILCOY","corredor":"BS. AS.","cap":120,"ghi":1480,"lat":-34.9,"lon":-60.0},{"id":"9460","nombre":"25 DE MAYO","corredor":"BS. AS.","cap":120,"ghi":1490,"lat":-35.4,"lon":-60.2},{"id":"9520","nombre":"CHIVILCOY","corredor":"BS. AS.","cap":40,"ghi":1480,"lat":None,"lon":None},{"id":"9006","nombre":"RAMALLO","corredor":"BS. AS.","cap":366,"ghi":1460,"lat":-33.5,"lon":-60.0},{"id":"9007","nombre":"RAMALLO","corredor":"BS. AS.","cap":366,"ghi":1460,"lat":-33.5,"lon":-60.0},{"id":"9008","nombre":"VILLA LÍA","corredor":"BS. AS.","cap":200,"ghi":1460,"lat":-34.0,"lon":-59.1},{"id":"9009","nombre":"VILLA LÍA","corredor":"BS. AS.","cap":200,"ghi":1460,"lat":-34.0,"lon":-59.1},{"id":"7030","nombre":"ROJAS","corredor":"BS. AS.","cap":138,"ghi":1480,"lat":-34.1,"lon":-61.0},{"id":"9005","nombre":"COLON","corredor":"BS. AS.","cap":110,"ghi":1480,"lat":-34.0,"lon":-61.1},{"id":"9012","nombre":"JUNÍN","corredor":"BS. AS.","cap":138,"ghi":1490,"lat":-34.6,"lon":-60.9},{"id":"9013","nombre":"IMSA","corredor":"BS. AS.","cap":138,"ghi":1490,"lat":-34.6,"lon":-60.9},{"id":"9014","nombre":"LINCOLN","corredor":"BS. AS.","cap":138,"ghi":1510,"lat":-34.8,"lon":-61.5},{"id":"9015","nombre":"BRAGADO","corredor":"BS. AS.","cap":138,"ghi":1490,"lat":-35.1,"lon":-60.5},{"id":"9500","nombre":"PERGAMINO","corredor":"BS. AS.","cap":98,"ghi":1480,"lat":-33.9,"lon":-60.6},{"id":"9003","nombre":"ARRECIFES","corredor":"BS. AS.","cap":10,"ghi":1470,"lat":None,"lon":None},{"id":"9004","nombre":"CAPITAN SARMIENTO","corredor":"BS. AS.","cap":10,"ghi":1470,"lat":None,"lon":None},{"id":"9510","nombre":"PERGAMINO","corredor":"BS. AS.","cap":10,"ghi":1480,"lat":None,"lon":None}]
    return pd.DataFrame(raw)

df_base = load_data()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ AURA Energy")
    st.markdown("**MATER 2T2026 — Oportunidades**")
    st.markdown("---")

    st.markdown("### Pesos del ranking")
    w_ghi = st.slider("Peso GHI (recurso solar)", 0, 100, 80, 5,
                      help="Mayor peso → prioriza zonas con mejor irradiación solar")
    w_mw  = 100 - w_ghi
    st.markdown(f"Peso MW disponibles: **{w_mw}%**")
    st.markdown(f"*Suma total: {w_ghi + w_mw}%*")

    st.markdown("---")
    st.markdown("### Filtros")
    corredores = ["Todos"] + sorted(df_base["corredor"].unique().tolist())
    sel_corredor = st.selectbox("Corredor", corredores)

    cap_min, cap_max = int(df_base.cap.min()), int(df_base.cap.max())
    rng_cap = st.slider("Capacidad disponible (MW)", cap_min, cap_max, (cap_min, cap_max))

    ghi_min_all, ghi_max_all = int(df_base.ghi.min()), int(df_base.ghi.max())
    rng_ghi = st.slider("GHI (kWh/m²/año)", ghi_min_all, ghi_max_all, (ghi_min_all, ghi_max_all))

    st.markdown("---")
    st.markdown("### Segmentación AURA")
    umbral_aura = st.slider("Umbral MW para 'Desarrollar'", 10, 100, 50, 5,
                            help="Proyectos con cap ≤ este valor son candidatos para que AURA desarrolle directamente")
    st.caption("Proyectos más grandes → ofrecer a terceros como consultores")

# ─── CÁLCULO DINÁMICO ─────────────────────────────────────────────────────────
@st.cache_data
def compute(data, w_ghi, w_mw, umbral):
    df = data.copy()
    ghi_n = (df.ghi - df.ghi.min()) / (df.ghi.max() - df.ghi.min())
    mw_n  = (df.cap - df.cap.min()) / (df.cap.max() - df.cap.min())
    df["score"] = (w_ghi/100)*ghi_n + (w_mw/100)*mw_n
    df["rank"]  = df["score"].rank(ascending=False, method="min").astype(int)
    df["rank_ghi"] = df["ghi"].rank(ascending=False, method="min").astype(int)
    def seg(row):
        if row["rank"] <= 50 and row["cap"] <= umbral:
            return "⭐ Desarrollar (AURA)"
        elif row["rank"] <= 80 and row["cap"] > umbral:
            return "🤝 Ofrecer a terceros"
        return "Monitorear"
    df["segmento"] = df.apply(seg, axis=1)
    return df

df = compute(df_base, w_ghi, w_mw, umbral_aura)

# ─── FILTRAR ──────────────────────────────────────────────────────────────────
mask = (
    (df.cap >= rng_cap[0]) & (df.cap <= rng_cap[1]) &
    (df.ghi >= rng_ghi[0]) & (df.ghi <= rng_ghi[1])
)
if sel_corredor != "Todos":
    mask &= (df.corredor == sel_corredor)
df_f = df[mask].copy()

# ─── COLORES ──────────────────────────────────────────────────────────────────
COLOR_MAP = {
    "PBA CENTRO-SUR":  "#2E75B6",
    "COSTA ATLÁNTICA": "#1D9E75",
    "LITORAL":         "#3B6D11",
    "MISIONES":        "#BA7517",
    "NEA":             "#D85A30",
    "GBA":             "#534AB7",
    "BS. AS.":         "#993556",
}

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("# ⚡ AURA Energy — Oportunidades MATER 2T2026")
st.markdown(f"**{len(df_f)} nodos** · Pesos activos: GHI {w_ghi}% / MW {w_mw}%")

# ─── MÉTRICAS ─────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
total_mw = df_f.cap.sum()
top_nodo = df_f.loc[df_f.rank.idxmin()] if not df_f.empty else None
n_aura   = (df_f.segmento == "⭐ Desarrollar (AURA)").sum()
n_terc   = (df_f.segmento == "🤝 Ofrecer a terceros").sum()

with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total MW disponibles</div><div class="metric-val">{total_mw:,.0f}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Nodo top ranked</div><div class="metric-val" style="font-size:1.1rem">{top_nodo["nombre"] if top_nodo is not None else "—"}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">⭐ Para desarrollar (AURA)</div><div class="metric-val">{n_aura}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">🤝 Para ofrecer a terceros</div><div class="metric-val">{n_terc}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Scatter GHI vs MW", "🗺️ Mapa", "🏆 Ranking", "📋 Tabla completa"])

# ── TAB 1: SCATTER ────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### GHI vs Capacidad disponible")
    st.caption("Tamaño de burbuja = MW disponibles · Color = corredor · Forma = segmento AURA")

    fig = px.scatter(
        df_f,
        x="ghi", y="cap",
        color="corredor",
        size="cap",
        size_max=50,
        symbol="segmento",
        symbol_map={
            "⭐ Desarrollar (AURA)":  "star",
            "🤝 Ofrecer a terceros":  "circle",
            "Monitorear":             "x",
        },
        color_discrete_map=COLOR_MAP,
        hover_name="nombre",
        hover_data={"id": True, "corredor": True, "ghi": True, "cap": True,
                    "score": ":.3f", "rank": True, "segmento": True},
        labels={"ghi": "GHI estimado (kWh/m²/año)", "cap": "Capacidad disponible (MW)",
                "corredor": "Corredor", "score": "Score ponderado", "rank": "Ranking"},
    )
    fig.update_layout(
        height=520,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="v", x=1.01, y=1),
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0", title_font_size=13),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title_font_size=13),
        font=dict(family="Arial"),
    )
    # Líneas de referencia
    fig.add_hline(y=umbral_aura, line_dash="dot", line_color="#BA7517",
                  annotation_text=f"Umbral AURA ({umbral_aura} MW)", annotation_position="right")
    fig.add_vline(x=1550, line_dash="dot", line_color="#2E75B6",
                  annotation_text="GHI 1550", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

    # Mini barras por corredor
    st.markdown("### MW disponibles por corredor")
    by_corr = df_f.groupby("corredor")["cap"].sum().reset_index().sort_values("cap", ascending=True)
    fig_bar = px.bar(by_corr, x="cap", y="corredor", orientation="h",
                     color="corredor", color_discrete_map=COLOR_MAP,
                     labels={"cap": "MW totales", "corredor": ""},
                     text="cap")
    fig_bar.update_traces(texttemplate="%{text} MW", textposition="outside")
    fig_bar.update_layout(height=300, showlegend=False, plot_bgcolor="white",
                          paper_bgcolor="white", xaxis=dict(showgrid=True, gridcolor="#F0F0F0"))
    st.plotly_chart(fig_bar, use_container_width=True)

# ── TAB 2: MAPA ───────────────────────────────────────────────────────────────
with tab2:
    df_map = df_f.dropna(subset=["lat","lon"]).copy()
    st.markdown(f"### Mapa de oportunidades ({len(df_map)} nodos con coordenadas)")
    st.caption("Tamaño = MW disponibles · Color = corredor")

    if df_map.empty:
        st.info("No hay nodos con coordenadas para el filtro seleccionado.")
    else:
        fig_map = px.scatter_mapbox(
            df_map,
            lat="lat", lon="lon",
            color="corredor",
            size="cap",
            size_max=30,
            color_discrete_map=COLOR_MAP,
            hover_name="nombre",
            hover_data={"id": True, "corredor": True, "ghi": True,
                        "cap": True, "rank": True, "segmento": True,
                        "lat": False, "lon": False},
            zoom=4,
            center={"lat": -34, "lon": -61},
            mapbox_style="carto-positron",
            labels={"cap": "MW", "corredor": "Corredor"},
        )
        fig_map.update_layout(height=560, margin={"r":0,"t":0,"l":0,"b":0},
                               legend=dict(orientation="v", x=0.01, y=0.99,
                                           bgcolor="rgba(255,255,255,0.85)"))
        st.plotly_chart(fig_map, use_container_width=True)

# ── TAB 3: RANKING ────────────────────────────────────────────────────────────
with tab3:
    c_izq, c_der = st.columns(2)

    with c_izq:
        st.markdown("### ⭐ Para desarrollar directamente (AURA)")
        df_aura = df_f[df_f.segmento == "⭐ Desarrollar (AURA)"].sort_values("rank").head(25)
        if df_aura.empty:
            st.info("Sin nodos en este segmento con los filtros activos.")
        else:
            for _, r in df_aura.iterrows():
                corr_color = COLOR_MAP.get(r.corredor, "#888")
                st.markdown(f"""
                <div style="border-left:3px solid {corr_color};padding:6px 10px;margin:4px 0;background:#FAFAFA;border-radius:0 6px 6px 0">
                  <span style="font-weight:600;color:#1F3864">#{int(r['rank'])} {r['nombre']}</span>
                  <span style="font-size:.8rem;color:#666;margin-left:8px">{r.corredor}</span><br>
                  <span style="font-size:.85rem">GHI <b>{r.ghi}</b> · <b>{r.cap} MW</b> · score {r.score:.3f}</span>
                </div>""", unsafe_allow_html=True)

    with c_der:
        st.markdown("### 🤝 Para ofrecer a terceros como consultores")
        df_terc = df_f[df_f.segmento == "🤝 Ofrecer a terceros"].sort_values("rank").head(25)
        if df_terc.empty:
            st.info("Sin nodos en este segmento con los filtros activos.")
        else:
            for _, r in df_terc.iterrows():
                corr_color = COLOR_MAP.get(r.corredor, "#888")
                st.markdown(f"""
                <div style="border-left:3px solid {corr_color};padding:6px 10px;margin:4px 0;background:#F0FAF5;border-radius:0 6px 6px 0">
                  <span style="font-weight:600;color:#0F6E56">#{int(r['rank'])} {r['nombre']}</span>
                  <span style="font-size:.8rem;color:#666;margin-left:8px">{r.corredor}</span><br>
                  <span style="font-size:.85rem">GHI <b>{r.ghi}</b> · <b>{r.cap} MW</b> · score {r.score:.3f}</span>
                </div>""", unsafe_allow_html=True)

# ── TAB 4: TABLA ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### Tabla completa — todos los nodos filtrados")
    cols_show = ["rank", "nombre", "corredor", "ghi", "cap", "score", "segmento", "id"]
    df_show = df_f[cols_show].sort_values("rank").copy()
    df_show.columns = ["Ranking", "Nombre", "Corredor", "GHI", "Cap. (MW)", "Score", "Segmento", "ID"]
    st.dataframe(
        df_show,
        use_container_width=True,
        height=500,
        column_config={
            "Ranking":   st.column_config.NumberColumn(format="%d"),
            "GHI":       st.column_config.NumberColumn(format="%d kWh/m²"),
            "Cap. (MW)": st.column_config.NumberColumn(format="%d MW"),
            "Score":     st.column_config.NumberColumn(format="%.3f"),
        },
        hide_index=True,
    )
    st.caption(f"{len(df_f)} nodos · Exportá con clic derecho → Copiar, o usá el botón ↓ de la tabla.")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("AURA Energy · Datos: Cammesa Anexo 3 Ref A 1T2026 · GHI: Global Solar Atlas · Desarrollado con Streamlit")
