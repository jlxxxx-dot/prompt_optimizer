import streamlit as st

def init_session_state():
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def main():
    init_session_state()
    
    # 顶部功能栏
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button('🌙 日间模式' if st.session_state.dark_mode else '☀️ 夜间模式'):
            st.session_state.dark_mode = not st.session_state.dark_mode
    with col2:
        st.button('📝 功能提示词')
    with col3:
        st.button('📜 历史记录')
    with col4:
        st.button('⚙️ 模型管理')
    
    st.divider()
    
    # 主要内容区域
    st.subheader('测试内容')
    user_input = st.text_area('请输入要测试的内容...', height=200)
    
    # 模型选择
    st.subheader('模型')
    model = st.selectbox('请配置模型', ['请配置模型...'])
    
    # 开始测试按钮
    if st.button('开始测试 →', type='primary'):
        if user_input and model != '请配置模型...':
            st.info('正在处理...')
        else:
            st.warning('请输入测试内容并选择模型')
    
    # 测试结果区域
    st.subheader('测试结果')
    st.text_area('测试结果将显示在这里...', height=300, disabled=True)

if __name__ == '__main__':
    st.set_page_config(
        page_title='Prompt Optimizer',
        page_icon='🚀',
        layout='wide'
    )
    main()