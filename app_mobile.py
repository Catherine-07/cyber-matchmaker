import streamlit as st
import pandas as pd
import os
import datetime

# --- 1. 页面UI与基础配置（包含移动端极致优化） ---
st.set_page_config(page_title="赛博小红娘 | 助力城镇青年择偶", page_icon="💖", layout="centered")

# 注入 CSS 魔法：隐藏英文提示，压榨留白，美化移动端按钮
st.markdown("""
    <style>
    /* 彻底隐藏输入框右下角的英文提示 */
    [data-testid="InputInstructions"] {
        display: none !important;
    }
    /* 📱 移动端优化：压榨左右留白，让输入框尽量占满手机屏幕 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    /* 📱 移动端优化：稍微放大单选框的上下间距，防止手指误触 */
    div[role="radiogroup"] {
        gap: 0.8rem;
    }
    /* 美化提交按钮，变成全宽心动红大按钮，极具点击欲 */
    div.stButton > button:first-child {
        width: 100%; 
        background-color: #ff4b4b; 
        color: white;
        border-radius: 8px;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff3333;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 页头文案 ---
st.title("💖 赛博小红娘：城镇青年单身档案")
st.markdown("""
**你好，欢迎来到这场真实的社交实验。** 在这个大家都很忙的时代，我们希望助力太原/吕梁的单身青年打破圈子，主动争取属于自己的幸福。  
我是一个懂数据和算法的理工科女生。我希望用真实的客观数据结合主观的性格画像，帮你找到那个同频的另一半。  
🔒 *承诺：你的所有隐私数据仅用于平台内部匹配，绝不泄露。越真实，匹配越精准。*
""")

# --- 2. 构建交互式表单（全面取消并排，改为手机最舒服的单列瀑布流） ---
with st.form("matchmaker_form"):
    st.subheader("🛠️ 一、 你的基础情况")
    name = st.text_input("怎么称呼你？（真实姓名/小名均可）*")
    birth_year = st.number_input("出生年份*", min_value=1980, max_value=2006, value=1998)
    gender = st.selectbox("性别*", ["女生 🚺", "男生 🚹"])
    height = st.number_input("身高 (厘米)", min_value=140, max_value=210, value=170)

    st.subheader("🌍 二、 居住地与工作状态")
    location = st.selectbox("目前常驻地*", ["太原市（细化到区请在下方补充）", "吕梁市（兴县周边）", "其他（请补充）"])
    job = st.text_input("行业/职业（如：体制内/国企/个体户/自由职业等）")
    work_style = st.radio("工作节奏",
                          ["早九晚五，周末双休", "偶尔加班，单休或大小周", "经常出差 / 工作很忙", "时间自由灵活"])

    st.subheader("🧩 三、 个人性格与生活爱好")
    personality = st.text_input("性格类型（选填，如：开朗外向 / 稳重内向）")
    hobbies = st.text_input("平时喜欢干什么？（如：爬山、看书、看剧、宅家打游戏）")
    self_desc = st.text_input("用3个词客观评价一下自己的性格")

    st.subheader("🎯 四、 核心匹配逻辑 (你的择偶标准)")
    crush_points = st.text_area("什么特质最容易让你『心动』？（加分项）*", help="例如：情绪稳定、声音好听、做事讲道理...")
    deal_breakers = st.text_area("绝对不能接受的『红线』？（一票否决项）*", help="例如：抽烟、冷暴力、异地恋...")

    st.subheader("🧱 五、 现实基础 (硬性条件与信任基石)")
    st.markdown("*💡 爱情需要浪漫，婚姻需要落地。真实的现实底牌，是建立信任的第一步。*")

    family_bg = st.selectbox("原生家庭情况*", [
        "独生子女，家庭和睦",
        "非独生，有兄弟姐妹",
        "单亲/重组家庭",
        "其他"
    ])
    parents_pension = st.selectbox("父母养老状态（选填，帮助评估未来压力）", [
        "父母均有退休金/医保",
        "部分有保障",
        "体制外/无退休金，需要较多支持",
        "暂不方便透露"
    ])
    assets = st.selectbox("房车资产情况*", [
        "已有独立住房和车",
        "有房无车 / 有车无房",
        "暂无，但有明确购房/购车计划",
        "暂无，随缘打拼",
        "保密（后续与红娘私聊）"
    ])
    income = st.selectbox("目前年收入水平 (仅红娘可见)*", [
        "5万以下",
        "5万 - 10万",
        "10万 - 20万",
        "20万以上",
        "自由职业/收入浮动较大"
    ])

    st.subheader("🔒 六、 建立连接 (隐私保护)")
    wechat = st.text_input("微信号 (必填，匹配成功前绝不公开)*")

    # 提交按钮
    submitted = st.form_submit_button("🚀 生成我的单身档案")

# --- 3. 数据处理与保存逻辑 ---
if submitted:
    if not name or not wechat or not crush_points or not deal_breakers:
        st.error("⚠️ 请填写完整的必填项（带*的空格）哦！")
    else:
        # 组装数据字典
        new_data = {
            "提交时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "昵称": name,
            "性别": gender,
            "出生年份": birth_year,
            "身高": height,
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
            "微信号": wechat
        }

        # 保存为 CSV
        csv_file = "cyber_matchmaker_database.csv"
        df_new = pd.DataFrame([new_data])

        if os.path.exists(csv_file):
            df_new.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')

        st.success("🎉 档案录入成功！红娘已接收到你的信息与现实底牌，请耐心等待匹配~")
        st.balloons()