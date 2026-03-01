import streamlit as st
import streamlit.components.v1 as components

# --- 1. 页面配置与样式优化 ---
st.set_page_config(page_title="Sleek Snake Pro", layout="wide", initial_sidebar_state="collapsed")

# 注入 CSS 提升 Streamlit 本身的白净感
st.markdown("""
    <style>
    .main { background: #f8f9fa; }
    .stButton>button { border-radius: 20px; border: 1px solid #ddd; transition: all 0.3s; }
    .stButton>button:hover { border-color: #4CAF50; color: #4CAF50; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { font-size: 28px; color: #2E7D32; }
    </style>
""", unsafe_allow_html=True)

# 初始化最高分
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

# --- 2. 欢迎与设置界面 ---
if not st.session_state.game_started:
    st.markdown("<h1 style='text-align: center; color: #333;'>🎨 Sleek Snake Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>极简艺术风格，极致丝滑体验</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        with st.expander("🛠️ 游戏实验室 (设置)", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                snake_theme = st.selectbox("蛇身风格", ["翠绿渐变", "天空幻影", "落日余晖", "极地冰蓝"])
                canvas_size = st.radio("画布比例", ["精致方块 (600x600)", "沉浸宽屏 (900x600)"], horizontal=True)
            with c2:
                difficulty = st.select_slider("初始流速", options=["慢享", "平衡", "竞技", "极限"], value="平衡")
                logic_mode = st.checkbox("量子穿梭 (穿墙模式)", value=True)
        
        # 颜色映射
        color_map = {
            "翠绿渐变": ["#43a047", "#a1ffce"],
            "天空幻影": ["#1e88e5", "#80d0ff"],
            "落日余晖": ["#fb8c00", "#ffcc80"],
            "极地冰蓝": ["#00acc1", "#80deea"]
        }
        speed_val = {"慢享": 130, "平衡": 90, "竞技": 65, "极限": 45}[difficulty]
        width_val = 900 if "宽屏" in canvas_size else 600

        if st.button("✨ 开启新征程", use_container_width=True):
            st.session_state.config = {
                "colors": color_map[snake_theme],
                "speed": speed_val,
                "can_wrap": logic_mode,
                "width": width_val,
                "height": 600
            }
            st.session_state.game_started = True
            st.rerun()

# --- 3. 游戏运行界面 ---
else:
    conf = st.session_state.config
    
    # 顶部状态栏
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("最高纪录", f"🏆 {st.session_state.high_score}")
    with c2: st.markdown(f"<div style='text-align:center; padding:10px; font-weight:bold;'>模式: {'穿梭' if conf['can_wrap'] else '经典'}</div>", unsafe_allow_html=True)
    with c3: 
        if st.button("🔙 退出游戏"):
            st.session_state.game_started = False
            st.rerun()

    # 核心游戏 JS
    game_js = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background: transparent; margin: 0; display: flex; flex-direction: column; align-items: center; font-family: sans-serif; overflow: hidden; }}
            canvas {{ background: #ffffff; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }}
            #hud {{ color: #444; font-size: 20px; margin-bottom: 10px; display: flex; gap: 20px; }}
            .fever {{ color: #ff4081; font-weight: bold; animation: blink 0.5s infinite; }}
            @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
        </style>
    </head>
    <body>
        <div id="hud">
            <span>得分: <span id="cur_score">0</span></span>
            <span id="fever_msg" style="display:none;" class="fever">FEVER MODE! x2</span>
        </div>
        <canvas id="game"></canvas>

        <script>
            const canvas = document.getElementById('game');
            const ctx = canvas.getContext('2d');
            canvas.width = {conf['width']};
            canvas.height = {conf['height']};

            const grid = 25;
            let score = 0, tail = 5, particles = [];
            let px=10, py=10, xv=0, yv=0;
            let trail = [];
            let ax=5, ay=5, atype=0;
            let gameActive = false;
            let feverTimer = 0;

            const foodList = [
                {{c: '#ff5252', p: 10, s: 1}}, // 普通
                {{c: '#ffd700', p: 50, s: 1.2}}, // 黄金
                {{c: '#b388ff', p: 100, s: 0.8}} // 减速蓝莓
            ];

            // 粒子特效类
            class Particle {{
                constructor(x, y, color) {{
                    this.x = x; this.y = y;
                    this.color = color;
                    this.vx = (Math.random()-0.5) * 10;
                    this.vy = (Math.random()-0.5) * 10;
                    this.alpha = 1;
                }}
                draw() {{
                    ctx.globalAlpha = this.alpha;
                    ctx.fillStyle = this.color;
                    ctx.beginPath(); ctx.arc(this.x, this.y, 3, 0, Math.PI*2); ctx.fill();
                    this.alpha -= 0.02;
                }}
            }}

            function spawnFood() {{
                ax = Math.floor(Math.random() * (canvas.width/grid));
                ay = Math.floor(Math.random() * (canvas.height/grid));
                let r = Math.random();
                atype = r > 0.9 ? 2 : (r > 0.7 ? 1 : 0);
            }}

            function draw() {{
                if(!gameActive) {{
                    ctx.fillStyle = "rgba(255,255,255,0.8)";
                    ctx.fillRect(0,0,canvas.width, canvas.height);
                    ctx.fillStyle = "#333";
                    ctx.font = "bold 30px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("READY?", canvas.width/2, canvas.height/2);
                    ctx.font = "16px sans-serif";
                    ctx.fillText("按方向键或 WASD 开启灵动之旅", canvas.width/2, canvas.height/2+40);
                    return;
                }}

                px += xv; py += yv;

                // 穿墙逻辑
                if({str(conf['can_wrap']).lower()}) {{
                    if(px<0) px=canvas.width/grid-1; if(px>=canvas.width/grid) px=0;
                    if(py<0) py=canvas.height/grid-1; if(py>=canvas.height/grid) py=0;
                }} else if(px<0 || px>=canvas.width/grid || py<0 || py>=canvas.height/grid) {{
                    endGame();
                }}

                ctx.fillStyle = "white";
                ctx.fillRect(0,0,canvas.width, canvas.height);

                // 画粒子
                particles = particles.filter(p => p.alpha > 0);
                particles.forEach(p => {{ p.x += p.vx; p.y += p.vy; p.draw(); }});
                ctx.globalAlpha = 1.0;

                // 画蛇 (渐变)
                let grad = ctx.createLinearGradient(0,0,canvas.width,0);
                grad.addColorStop(0, "{conf['colors'][0]}");
                grad.addColorStop(1, "{conf['colors'][1]}");
                ctx.fillStyle = grad;
                ctx.shadowBlur = 10; ctx.shadowColor = "rgba(0,0,0,0.1)";

                for(let i=0; i<trail.length; i++) {{
                    let r = 4; // 圆角
                    ctx.beginPath();
                    ctx.roundRect(trail[i].x*grid+1, trail[i].y*grid+1, grid-2, grid-2, 6);
                    ctx.fill();
                    if(trail[i].x==px && trail[i].y==py) endGame();
                }}
                trail.push({{x:px, y:py}});
                while(trail.length>tail) trail.shift();

                // 画豆子
                ctx.fillStyle = foodList[atype].c;
                ctx.shadowBlur = 15; ctx.shadowColor = foodList[atype].c;
                ctx.beginPath();
                ctx.arc(ax*grid+grid/2, ay*grid+grid/2, grid/2-4, 0, Math.PI*2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // 吃到食物
                if(ax==px && ay==py) {{
                    // 生成粒子
                    for(let i=0; i<15; i++) particles.push(new Particle(ax*grid+grid/2, ay*grid+grid/2, foodList[atype].c));
                    
                    tail++;
                    let p = foodList[atype].p;
                    if(feverTimer > 0) p *= 2; 
                    score += p;
                    document.getElementById('cur_score').innerText = score;
                    
                    // Fever 触发逻辑
                    if(atype === 1) {{ 
                        feverTimer = 100; 
                        document.getElementById('fever_msg').style.display = 'inline';
                    }}
                    
                    spawnFood();
                }}

                if(feverTimer > 0) {{
                    feverTimer--;
                    if(feverTimer === 0) document.getElementById('fever_msg').style.display = 'none';
                }}
            }}

            function endGame() {{
                alert("Game Over! Score: " + score);
                // 简单的最高分反馈给 Streamlit (通过标题动态传达并非最优，但JS Alert最直接)
                location.reload(); 
            }}

            document.addEventListener("keydown", e => {{
                gameActive = true;
                switch(e.keyCode) {{
                    case 37: case 65: if(xv==0){{xv=-1; yv=0;}} break;
                    case 38: case 87: if(yv==0){{xv=0; yv=-1;}} break;
                    case 39: case 68: if(xv==0){{xv=1; yv=0;}} break;
                    case 40: case 83: if(yv==0){{xv=0; yv=1;}} break;
                }}
            }});

            setInterval(draw, {conf['speed']});
        </script>
    </body>
    </html>
    """
    
    components.html(game_js, height=700)
