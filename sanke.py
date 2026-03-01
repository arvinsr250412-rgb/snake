import streamlit as st
import streamlit.components.v1 as components
import random

# --- 页面配置 ---
st.set_page_config(page_title="高级霓虹贪吃蛇", layout="wide")

# 初始化游戏状态
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

# --- 1. 游戏配置界面 ---
if not st.session_state.game_started:
    st.title("🐍 霓虹贪吃蛇")
    st.markdown("在开始前，请配置你的专属游戏环境。")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎨 视觉设计")
        theme_style = st.selectbox("页面风格", ["赛博朋克 (深色)", "极简白 (浅色)", "翡翠森林 (深绿)"])
        snake_color = st.color_picker("贪吃蛇颜色", "#00FFD1")
        bg_color = "#000000" if "赛博" in theme_style else ("#ffffff" if "极简" in theme_style else "#0a2e0a")
        
    with col2:
        st.subheader("⚙️ 游戏规则")
        difficulty = st.select_slider("游戏难度 (速度)", options=["休闲", "标准", "疯狂", "噩梦"], value="标准")
        can_wrap = st.toggle("允许穿墙 (从另一侧出现)", value=True)
        grid_size_opt = st.radio("游戏区域大小", ["标准 (600x600)", "大 (800x600)"], horizontal=True)

    # 映射难度到速度（毫秒）
    speed_map = {"休闲": 150, "标准": 100, "疯狂": 60, "噩梦": 40}
    canvas_w = 800 if "大" in grid_size_opt else 600
    canvas_h = 600

    if st.button("🚀 开始游戏", use_container_width=True):
        st.session_state.config = {
            "speed": speed_map[difficulty],
            "snake_color": snake_color,
            "bg_color": bg_color,
            "can_wrap": can_wrap,
            "width": canvas_w,
            "height": canvas_h
        }
        st.session_state.game_started = True
        st.rerun()

# --- 2. 游戏运行界面 ---
else:
    conf = st.session_state.config
    
    col_main, col_side = st.columns([3, 1])
    
    with col_side:
        st.title("🎮 正在游戏")
        st.metric("当前难度", "🔥" if conf['speed'] < 70 else "⚖️ 正常")
        st.write(f"穿墙模式: {'✅ 开启' if conf['can_wrap'] else '❌ 关闭'}")
        
        if st.button("🏠 返回主菜单"):
            st.session_state.game_started = False
            st.rerun()
            
        st.info("提示：\n- 🔴 红色豆: 10分\n- 🟡 黄金豆: 50分\n- 🟣 幻彩豆: 100分")

    # 构建 JavaScript 游戏逻辑
    game_js = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: {conf['bg_color']}; margin: 0; display: flex; justify-content: center; }}
            canvas {{ 
                border: 5px solid {conf['snake_color']}; 
                box-shadow: 0 0 30px {conf['snake_color']};
                margin-top: 20px;
            }}
            #ui {{ position: absolute; color: white; font-family: sans-serif; top: 30px; left: 50px; pointer-events: none; }}
        </style>
    </head>
    <body>
        <div id="ui">分数: <span id="score">0</span></div>
        <canvas id="gameCanvas" width="{conf['width']}" height="{conf['height']}"></canvas>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");
            const scoreDisplay = document.getElementById("score");

            const grid = 20;
            let count = 0;
            let score = 0;
            
            let snake = {{
                x: 160, y: 160,
                dx: grid, dy: 0,
                cells: [{{x: 160, y: 160}}, {{x: 140, y: 160}}],
                maxCells: 4
            }};

            // 豆子类型配置
            const foodTypes = [
                {{ color: '#FF3131', score: 10, weight: 0.7 }}, // 普通
                {{ color: '#FFD700', score: 50, weight: 0.2 }}, // 黄金
                {{ color: '#BC13FE', score: 100, weight: 0.1 }} // 稀有
            ];

            let food = getRandomFood();

            function getRandomFood() {{
                const r = Math.random();
                let type = foodTypes[0];
                if (r > 0.7 && r <= 0.9) type = foodTypes[1];
                else if (r > 0.9) type = foodTypes[2];

                return {{
                    x: Math.floor(Math.random() * (canvas.width / grid)) * grid,
                    y: Math.floor(Math.random() * (canvas.height / grid)) * grid,
                    ...type
                }};
            }}

            function loop() {{
                requestAnimationFrame(loop);
                if (++count < {conf['speed'] / 16}) return; // 控制速度
                count = 0;

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // 移动蛇
                snake.x += snake.dx;
                snake.y += snake.dy;

                // 边界处理
                if ({'true' if conf['can_wrap'] else 'false'}) {{
                    if (snake.x < 0) snake.x = canvas.width - grid;
                    else if (snake.x >= canvas.width) snake.x = 0;
                    if (snake.y < 0) snake.y = canvas.height - grid;
                    else if (snake.y >= canvas.height) snake.y = 0;
                }} else {{
                    if (snake.x < 0 || snake.x >= canvas.width || snake.y < 0 || snake.y >= canvas.height) {{
                        gameOver();
                    }}
                }}

                snake.cells.unshift({{x: snake.x, y: snake.y}});
                if (snake.cells.length > snake.maxCells) snake.cells.pop();

                // 画豆子
                ctx.shadowBlur = 15;
                ctx.shadowColor = food.color;
                ctx.fillStyle = food.color;
                ctx.beginPath();
                ctx.arc(food.x + grid/2, food.y + grid/2, grid/2 - 2, 0, 2 * Math.PI);
                ctx.fill();

                // 画蛇
                ctx.shadowBlur = 10;
                ctx.shadowColor = "{conf['snake_color']}";
                ctx.fillStyle = "{conf['snake_color']}";
                snake.cells.forEach(function(cell, index) {{
                    ctx.fillRect(cell.x, cell.y, grid-1, grid-1);

                    // 吃到豆子
                    if (cell.x === food.x && cell.y === food.y) {{
                        snake.maxCells++;
                        score += food.score;
                        scoreDisplay.innerHTML = score;
                        food = getRandomFood();
                    }}

                    // 检查碰撞自身
                    for (let i = index + 1; i < snake.cells.length; i++) {{
                        if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {{
                            gameOver();
                        }}
                    }}
                }});
            }}

            function gameOver() {{
                alert("游戏结束！最终分数: " + score);
                snake.x = 160; snake.y = 160;
                snake.cells = [{{x: 160, y: 160}}, {{x: 140, y: 160}}];
                snake.maxCells = 4;
                snake.dx = grid; snake.dy = 0;
                score = 0;
                scoreDisplay.innerHTML = score;
            }}

            document.addEventListener('keydown', function(e) {{
                if (e.which === 37 && snake.dx === 0) {{ snake.dx = -grid; snake.dy = 0; }}
                else if (e.which === 38 && snake.dy === 0) {{ snake.dy = -grid; snake.dx = 0; }}
                else if (e.which === 39 && snake.dx === 0) {{ snake.dx = grid; snake.dy = 0; }}
                else if (e.which === 40 && snake.dy === 0) {{ snake.dy = grid; snake.dx = 0; }}
            }});

            requestAnimationFrame(loop);
        </script>
    </body>
    </html>
    """
    
    with col_main:
        components.html(game_js, height=conf['height'] + 50)
