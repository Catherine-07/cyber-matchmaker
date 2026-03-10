import streamlit as st
import pandas as pd
import os
import datetime
import requests

# ==========================================
# 🔧 飞书核心配置区 (密码已全部集齐并填入)
# ==========================================
APP_ID = "cli_a9253e6a3be6dbd1"
APP_SECRET = "zLnbqkfzFKsRTjuH25JOdzqMbGQGZUO"
APP_TOKEN = "FS7YbPxt8auvIHseslZcVN03nUh" 
TABLE_ID = "tbls07Rnv0sHsQoV"
BOT_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3fa6624a-7839-4539-9569-98e17f009f42"

# --- 1. 页面UI与基础配置（移动端极致优化） ---
st.set_page_config(page_title="赛博小红娘 | 助力城镇青年择偶", page_icon="💖", layout="centered")

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

# --- 2. 构建交互式表单（单列瀑布流） ---
with st.form("matchmaker_form"):
    st.subheader("🛠️ 一、 你的基础情况")
    name = st.text_input("怎么称呼你？（真实姓名/小名均可）*")
    birth_year = st.number_input("出生年份*", min_value=1980, max_value=2006, value=1998)
    gender = st.selectbox("性别*", ["女生 🚺", "男生 🚹"])
    height = st.number_input("身高 (厘米)", min_value=140, max_value=210, value=170)
    weight = st.number_input("体重 (公斤)", min_value=30, max_value=150, value=60) # 已加入体重

    st.subheader("🌍 二、 居住地与工作状态")
    location = st.selectbox("目前常驻地*", ["太原市（细化到区请在下方补充）", "吕梁市（兴县周边）", "其他（请补充）"])
    job = st.text_input("行业/职业（如：体制内/国企/个体户/自由职业等）")
    work_style = st.radio("工作节奏", ["早九晚五，周末双休", "偶尔加班，单休或大小周", "经常出差 / 工作很忙", "时间自由灵活"])

    st.subheader("🧩 三、 个人性格与生活爱好")
    personality = st.text_input("性格类型（选填，如：开朗外向 / 稳重内向）")
    hobbies = st.text_input("平时喜欢干什么？（如：爬山、看书、看剧、宅家打游戏）")
    self_desc = st.text_input("用3个词客观评价一下自己的性格")

    st.subheader("🎯 四、 核心匹配逻辑 (你的择偶标准)")
    crush_points = st.text_area("什么特质最容易让你『心动』？（加分项）*", help="例如：情绪稳定、声音好听、做事讲道理...")
    deal_breakers = st.text_area("绝对不能接受的『红线』？（一票否决项）*", help="例如：抽烟、冷暴力、异地恋...")

    st.subheader("🧱 五、 现实基础 (硬性条件与信任基石)")
    st.markdown("*💡 爱情需要浪漫，婚姻需要落地。真实的现实底牌，是建立信任的第一步。*")

    family_bg = st.selectbox("原生家庭情况*", ["独生子女，家庭和睦", "非独生，有兄弟姐妹", "单亲/重组家庭", "其他"])
    parents_pension = st.selectbox("父母养老状态（选填，帮助评估未来压力）", ["父母均有退休金/医保", "部分有保障", "体制外/无退休金，需要较多支持", "暂不方便透露"])
    assets = st.selectbox("房车资产情况*", ["已有独立住房和车", "有房无车 / 有车无房", "暂无，但有明确购房/购车计划", "暂无，随缘打拼", "保密（后续与红娘私聊）"])
    income = st.selectbox("目前年收入水平 (仅红娘可见)*", ["5万以下", "5万 - 10万", "10万 - 20万", "20万以上", "自由职业/收入浮动较大"])

    st.subheader("🔒 六、 建立连接 (隐私保护)")
    wechat = st.text_input("微信号 (必填，匹配成功前绝不公开)*")

    submitted = st.form_submit_button("🚀 生成我的单身档案")

# --- 3. 数据处理与双重推送逻辑 ---
if submitted:
    if not name or not wechat or not crush_points or not deal_breakers:
        st.error("⚠️ 请填写完整的必填项（带*的空格）哦！")
    else:
        try:
            # ==========================================
            # 步骤 A：获取飞书 API 访问令牌
            # ==========================================
            auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            auth_res = requests.post(auth_url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
            token = auth_res.json().get("tenant_access_token")

            # ==========================================
            # 步骤 B：向多维表格写入结构化数据
            # ==========================================
            write_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            payload = {
                "fields": {
                    "昵称": name,
                    "性别": gender,
                    "出生年份": birth_year,
                    "身高": height,
                    "体重": weight,
                    "常驻地": location,
                    "职业": job,
                    "工作节奏": work_style,
                    "性格类型": personality,
                    "爱好": hobbies,
                    "自我评价": self_desc,
                    "心动加分项": crush_points,
                    "底线红线": deal_breakers,
                    "家庭情况": family_bg,
                    "父母养老": parents_pension,
                    "房车情况": assets,
                    "年收入": income,
                    "微信号": wechat,
                    "提交时间": int(datetime.datetime.now().timestamp() * 1000) # 飞书日期列使用毫秒时间戳
                }
            }
            res_table = requests.post(write_url, headers=headers, json=payload)

            # ==========================================
            # 步骤 C：发送机器人即时提醒
            # ==========================================
            msg_content = f"""🔔 收到新档案！
👤 {name} ({gender})
🎂 {birth_year}年 | 身高：{height}cm | 体重：{weight}kg
📍 {location} | 💼 {job}
📞 微信：{wechat}
📊 完整数据已自动同步至多维表格。"""
            requests.post(BOT_URL, json={"msg_type": "text", "content": {"text": msg_content}})

            # ==========================================
            # 步骤 D：兜底方案 (本地 CSV 备份)
            # ==========================================
            new_data = payload["fields"].copy()
            new_data["提交时间"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_file = "cyber_matchmaker_database.csv"
            df_new = pd.DataFrame([new_data])
            if os.path.exists(csv_file):
                df_new.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            else:
                df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')

            # --- 前端反馈 ---
            if res_table.status_code == 200:
                st.success("🎉 档案录入成功！红娘已接收到你的信息与现实底牌，请耐心等待匹配~")
                st.balloons()
            else:
                st.error(f"⚠️ 飞书表格写入失败。请检查表格里的列名是否完全对应。飞书报错：{res_table.text}")

        except Exception as e:
            st.error(f"⚠️ 网络波动，请联系红娘。错误信息: {e}")
