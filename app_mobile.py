import streamlit as st
import pandas as pd
import os
import datetime
import requests
import threading
import re

# ==========================================
# 🔧 飞书核心配置区 
# ==========================================
APP_ID = "cli_a9253e6a3be6dbd1"
APP_SECRET = "zLnbqkfszFKsRTjuH25JOdzqMbGQGZUO"
APP_TOKEN = "FS7YbPxt8auvIHsesIZcVN03nUh" 
TABLE_ID = "tbls07Rnv0sHsQoV"
BOT_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3fa6624a-7839-4539-9569-98e17f009f42"

# --- 1. 页面UI与基础配置（移动端极致优化） ---
st.set_page_config(page_title="赛博小红娘 | 助力城镇青年择偶", page_icon="💖", layout="centered")

if 'has_submitted_successfully' not in st.session_state:
    st.session_state['has_submitted_successfully'] = False

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="InputInstructions"] { display: none !important; }
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif !important; }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[role="radiogroup"] { gap: 0.8rem; }
    [data-testid="baseButton-formSubmit"] {
        width: 100% !important; background-color: #ff4b4b !important; color: white !important;
        border-radius: 8px !important; height: 3.5rem !important; font-size: 1.2rem !important;
        font-weight: bold !important; border: none !important; margin-top: 1rem !important;
        box-shadow: 0 4px 6px rgba(255, 75, 75, 0.2) !important;
    }
    [data-testid="baseButton-formSubmit"]:active, [data-testid="baseButton-formSubmit"]:hover { background-color: #ff3333 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💖 赛博小红娘：城镇青年单身档案")
st.markdown("""
**你好，欢迎来到这场真实的社交实验。** 在这个大家都很忙的时代，我们希望助力太原/吕梁的单身青年打破圈子，主动争取属于自己的幸福。  
我是一个懂数据和算法的理工科女生。我希望用真实的客观数据结合主观的性格画像，帮你找到那个同频的另一半。  
🔒 *承诺：你的所有隐私数据仅用于平台内部匹配，绝不泄露。越真实，匹配越精准。*
""")

# --- 2. 构建交互式表单 ---
with st.form("matchmaker_form"):
    st.subheader("🛠️ 一、 你的基础情况")
    name = st.text_input("怎么称呼你？（真实姓名/小名均可）*")
    birth_year = st.number_input("出生年份*", min_value=1980, max_value=2006, value=1998)
    gender = st.selectbox("性别*", ["女生 🚺", "男生 🚹"])
    height = st.number_input("身高 (厘米)", min_value=140, max_value=210, value=170)
    weight = st.number_input("体重 (公斤)", min_value=30, max_value=150, value=60)

    st.subheader("🌍 二、 居住地与工作状态")
    location_options = [
        "太原市",
        "吕梁市-兴县", "吕梁市-离石区", "吕梁市-孝义市", "吕梁市-汾阳市", "吕梁市-文水县",
        "吕梁市-交城县", "吕梁市-临县", "吕梁市-柳林县", "吕梁市-石楼县", "吕梁市-岚县",
        "吕梁市-方山县", "吕梁市-中阳县", "吕梁市-交口县",
        "其他（请手动键入）"
    ]
    location_base = st.selectbox("目前常驻地*", location_options)
    location_other = st.text_input("如果您选择了「其他」，请在此手动输入所在地区：", placeholder="例如：晋中市-榆次区")
    
    job = st.text_input("行业/职业（如：体制内/国企/个体户/自由职业等）")
    work_style = st.radio("工作节奏", ["早九晚五，周末双休", "偶尔加班，单休或大小周", "经常出差 / 工作很忙", "时间自由灵活"])

    st.subheader("🧩 三、 个人性格与生活爱好")
    # ✅ 修改点 1：缩短 placeholder 适应手机屏幕，并将长段文字移入 help (小问号) 中
    personality = st.text_input(
        "性格类型（选填，推荐写MBTI）", 
        placeholder="如：INTJ / 开朗外向", 
        help="建议填写您的 MBTI（如：INTJ、ENFP），或者使用传统词汇（如：开朗外向、沉稳内向）"
    )
    hobbies = st.text_input("平时喜欢干什么？（如：爬山、看书、宅家打游戏）")
    self_desc = st.text_input("用3个词客观评价一下自己的性格")

    st.subheader("🎯 四、 核心匹配逻辑 (你的择偶标准)")
    crush_points = st.text_area("什么特质最容易让你『心动』？（加分项）*", help="例如：情绪稳定、声音好听、做事讲道理...")
    deal_breakers = st.text_area("绝对不能接受的『红线』？（一票否决项）*", help="例如：抽烟、冷暴力、异地恋...")

    st.subheader("🧱 五、 现实基础 (硬性条件与信任基石)")
    st.markdown("*💡 爱情需要浪漫，婚姻需要落地。真实的现实底牌，是建立信任的第一步。*")

    family_bg = st.selectbox("原生家庭情况*", ["独生子女，家庭和睦", "非独生，有兄弟姐妹", "单亲/重组家庭", "其他"])
    parents_pension = st.selectbox("父母养老状态（选填）", ["父母均有退休金/医保", "部分有保障", "体制外/无保障，需较多支持", "暂不方便透露"])
    assets = st.selectbox("房车资产情况*", ["已有独立住房和车", "有房无车 / 有车无房", "暂无，但有明确购房/购车计划", "暂无，随缘打拼", "保密（后续与红娘私聊）"])
    income = st.selectbox("目前年收入水平 (仅红娘可见)*", ["5万以下", "5万 - 10万", "10万 - 20万", "20万以上", "自由职业/收入浮动较大"])

    st.subheader("🔒 六、 建立连接 (隐私保护)")
    wechat = st.text_input("联系方式 (微信同号的手机号)*")

    submitted = st.form_submit_button("🚀 生成我的单身档案")

# --- 飞书云端校验 ---
def check_if_submitted_today(wx_id):
    try:
        auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token = requests.post(auth_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json().get("tenant_access_token")
        if not token: return False

        search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"filter": {"conjunction": "and", "conditions": [{"field_name": "微信号", "operator": "is", "value": [str(wx_id)]}]}}
        res = requests.post(search_url, headers=headers, json=payload).json()
        
        items = res.get("data", {}).get("items", [])
        if items:
            today_start_ts = int(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
            for item in items:
                if item.get("fields", {}).get("提交时间", 0) >= today_start_ts:
                    return True 
    except Exception as e:
        pass
    return False

# --- 后台异步提交 ---
def background_full_submit(name, gender, birth_year, height, weight, location, job, work_style, personality, hobbies, self_desc, crush_points, deal_breakers, family_bg, parents_pension, assets, income, wechat):
    try:
        auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token = requests.post(auth_url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json().get("tenant_access_token")

        write_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
        payload = {
            "fields": {
                "昵称": name, "性别": gender, "出生年份": birth_year, "身高": height, "体重": weight,
                "常驻地": location, "职业": job, "工作节奏": work_style, "性格类型": personality,
                "爱好": hobbies, "自我评价": self_desc, "心动加分项": crush_points, "底线红线": deal_breakers,
                "家庭情况": family_bg, "父母养老": parents_pension, "房车情况": assets, "年收入": income,
                "微信号": wechat, "提交时间": int(datetime.datetime.now().timestamp() * 1000)
            }
        }
        requests.post(write_url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=payload)

        msg_content = f"🔔 收到新档案！\n👤 {name} ({gender})\n🎂 {birth_year}年 | {height}cm | {weight}kg\n📍 {location} | 💼 {job}\n📞 联系方式: {wechat}"
        requests.post(BOT_URL, json={"msg_type": "text", "content": {"text": msg_content}})
    except Exception as e:
        print(f"后台同步失败: {e}") 

# --- 3. 提交逻辑 ---
if submitted:
    if st.session_state['has_submitted_successfully']:
        st.warning("⚠️ 您刚刚已经成功提交过啦，无需重复点击哦！
