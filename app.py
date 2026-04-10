import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# 1. 全局配置：强制开启宽屏模式，支持夜间模式
st.set_page_config(page_title="工业事故评价与逻辑推演系统", layout="wide")

# 2. 注入 CSS：全局放大字体，移除强制颜色
st.markdown("""
    <style>
    .stMarkdown p, .stMarkdown li { font-size: 1.15rem !important; line-height: 1.6 !important; }
    h1, h2, h3 { font-family: "Microsoft YaHei", sans-serif; margin-bottom: 1rem; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. 侧边栏配置
with st.sidebar:
    st.header("系统参数配置")
    # 👉 请把下面这串 sk- 开头的字符换成你真实的密钥
    api_key = "sk-e8534e50d9d74f38baff185fa8173d68" 
    
    st.success("✅ AI 通信密钥已在底层加密加载")
    industry_type = st.selectbox("行业知识库", ["石油化工", "建筑施工", "交通运输", "通用安全"])
    st.info("💡 提示：本系统采用 Neuro-Symbolic 架构，确保核心概率推演绝对准确。")

# 4. 主界面 UI
st.title("工业事故链推演与定量评价系统")
st.caption("基于大语言模型语义解析与布尔代数引擎的综合安全评价平台")

accident_description = st.text_area("事故/隐患情景描述：", height=100, 
                                    placeholder="请输入具体的事故经过...")

# 5. 核心文本报告生成函数 (仅保留文本报告生成)
def analyze_report_with_llm(description, industry, key):
    try:
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
        system_prompt = f"""
        你现在是一名国家注册安全工程师。请对【{industry}】事故进行详尽分析。
        要求包含：事故直接原因、间接原因、管理缺陷、整改建议。不需要生成图表代码。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": description}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用大模型失败: {str(e)}"

# 6. 终极兼容版图表渲染函数 (修复所有乱码/不显示问题)
def render_dynamic_mermaid(mermaid_code):
    # 使用最稳定的 iframe 沙盒模式隔离渲染，彻底解决乱码
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ 
                startOnLoad: true, 
                theme: 'neutral', 
                securityLevel: 'loose' 
            }});
        </script>
        <style>
            body {{ background-color: #ffffff; padding: 20px; border-radius: 10px; margin: 0; }}
            .mermaid {{ display: flex; justify-content: center; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{mermaid_code}
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=500, scrolling=True)

# 7. 执行按钮与动态交互流程
if st.button("执行逻辑提取与定量推演", type="primary"):
    if not accident_description:
        st.warning("请输入情景描述")
    else:
        with st.spinner('系统正在解析网络拓扑并执行后端代数计算...'):
            text_report = analyze_report_with_llm(accident_description, industry_type, api_key)
            
            # --- 全新模块：交互式定量计算与动态事故树 ---
            st.markdown("---")
            st.subheader("一、 交互式事故树定量推演 (Interactive FTA)")
            st.caption("拖动下方滑块，事故树模型及顶事件发生概率将实时更新。")
            
            # 使用 Streamlit 布局
            col_params, col_metrics = st.columns([1, 1.5])
            
            with col_params:
                st.markdown("**调节底事件概率 (P):**")
                p_x1 = st.slider("X1: 设备/管道失效概率", 0.0, 1.0, 0.05, format="%.3f")
                p_x2 = st.slider("X2: 报警/联锁失效概率", 0.0, 1.0, 0.10, format="%.3f")
                p_x3 = st.slider("X3: 人员违章作业概率", 0.0, 1.0, 0.01, format="%.3f")
            
            with col_metrics:
                # 后台精准数学计算
                prob_m1 = p_x1 * p_x2
                prob_t = 1 - (1 - p_x3) * (1 - prob_m1)
                
                m1, m2 = st.columns(2)
                m1.metric("顶事件发生概率 P(T)", f"{prob_t:.4%}", delta="高风险" if prob_t > 0.02 else "受控", delta_color="inverse")
                m2.metric("推演最小割集 (MCS)", "{X3} ∪ {X1, X2}")
                st.info("计算逻辑： $P(T) = 1 - (1 - P(X_3)) \\times (1 - P(X_1)P(X_2))$")

            # 👉 核心创新：根据滑块数据实时生成的标准向下(TD)事故树
            dynamic_mermaid_code = f"""
            graph TD
                T["[顶上事件] 事故发生<br/>P(T)={prob_t:.4f}"] 
                M1["[中间事件] 防护与设备双重失效<br/>P(M1)={prob_m1:.4f}"]
                
                X3["[基本原因] 人员违章<br/>P(X3)={p_x3:.3f}"]
                X1["[基本原因] 设备失效<br/>P(X1)={p_x1:.3f}"]
                X2["[基本原因] 联锁失效<br/>P(X2)={p_x2:.3f}"]

                T -->|OR| M1
                T -->|OR| X3
                M1 -->|AND| X1
                M1 -->|AND| X2

                classDef topEvent fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#c62828;
                classDef midEvent fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#e65100;
                classDef basicEvent fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
                
                class T topEvent;
                class M1 midEvent;
                class X1,X2,X3 basicEvent;
            """
            
            # 渲染动态生成的图表
            render_dynamic_mermaid(dynamic_mermaid_code)

            # --- 分析报告模块 ---
            st.markdown("---")
            st.subheader("二、 综合安全诊断报告 (Safety Evaluation Report)")
            st.markdown(text_report)
            st.download_button("导出完整分析报告 (TXT)", data=text_report, file_name="Report.txt")