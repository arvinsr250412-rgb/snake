import streamlit as st
import streamlit.components.v1 as components

# 设置页面基本配置
st.set_page_config(page_title="霓虹贪吃蛇", layout="centered")

st.title("🐍 霓虹贪吃蛇游戏")
st.markdown("使用 **方向键** 或 **WASD** 控制蛇的移动。")

# 游戏参数设置（侧边栏）
with st.sidebar:
    st.header("游戏设置")
    difficulty = st.select_slider("选择难度", options=["新手", "普通", "高手", "传说"], value="普通")
    speed_map = {"新手": 150, "普通": 100, "高手": 70, "传说": 45}
    speed = speed_map[difficulty]
    
    st.info("提示：点击游戏区域后即可开始控制。")

# 嵌入 HTML/JavaScript 游戏逻辑
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #0e1117;
            margin: 0;
            overflow: hidden;
            font-family: 'Courier New', Courier, monospace;
        }}
        canvas {{
            border: 4px solid #00d4ff;
            box-shadow: 0 0 20px #00d4ff, inset 0 0 10px #00d4ff;
            background-color: #000;
            border-radius: 10px;
        }}
        #score-board {{
            position: absolute;
            top: 10px;
            left: 20px;
            color: #00d4ff;
            font-size: 24px;
            text-shadow: 0 0 5px #00d4ff;
        }}
    </style>
</head>
<body>
    <div id="score-board">分数: 0</div>
    <canvas id="snakeGame" width="400" height="400"></canvas>

    <script>
        const canvas = document.getElementById("snakeGame");
        const ctx = canvas.getContext("2d");
        const scoreElement = document.getElementById("score-board");

        const gridSize = 20;
        const tileCount = canvas.width / gridSize;

        let score = 0;
        let dx = 0;
        let dy = 0;
        let snake = [{{x: 10, y: 10}}];
        let food = {{x: 5, y: 5}};
        let nextDx = 0;
        let nextDy = 0;

        // 监听按键
        document.addEventListener("keydown", changeDirection);

        function main() {{
            if (didGameEnd()) {{
                ctx.fillStyle = "white";
                ctx.font = "30px Arial";
                ctx.fillText("游戏结束!", 120, 200);
                ctx.font = "20px Arial";
                ctx.fillText("按 F5 重新开始", 130, 240);
                return;
            }}

            setTimeout(function onTick() {{
                clearCanvas();
                drawFood();
                advanceSnake();
                drawSnake();
                main();
            }}, {speed});
        }}

        function clearCanvas() {{
            ctx.fillStyle = "black";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制网格线（可选，增加美感）
            ctx.strokeStyle = "#111";
            for(let i=0; i<canvas.width; i+=gridSize) {{
                ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(canvas.width,i); ctx.stroke();
            }}
        }}

        function drawSnake() {{
            snake.forEach((part, index) => {{
                // 头部颜色略有不同
                ctx.fillStyle = index === 0 ? "#00d4ff" : "#008fb3";
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00d4ff";
                ctx.fillRect(part.x * gridSize, part.y * gridSize, gridSize-2, gridSize-2);
            }});
        }}

        function advanceSnake() {{
            dx = nextDx;
            dy = nextDy;
            const head = {{x: snake[0].x + dx, y: snake[0].y + dy}};
            snake.unshift(head);
            if (snake[0].x === food.x && snake[0].y === food.y) {{
                score += 10;
                scoreElement.innerHTML = "分数: " + score;
                createFood();
            }} else {{
                snake.pop();
            }}
        }}

        function didGameEnd() {{
            for (let i = 4; i < snake.length; i++) {{
                if (snake[i].x === snake[0].x && snake[i].y === snake[0].y) return true;
            }}
            const hitLeftWall = snake[0].x < 0;
            const hitRightWall = snake[0].x > tileCount - 1;
            const hitTopWall = snake[0].y < 0;
            const hitBottomWall = snake[0].y > tileCount - 1;
            return hitLeftWall || hitRightWall || hitTopWall || hitBottomWall;
        }}

        function createFood() {{
            food.x = Math.floor(Math.random() * tileCount);
            food.y = Math.floor(Math.random() * tileCount);
        }}

        function drawFood() {{
            ctx.fillStyle = "#ff0055";
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#ff0055";
            ctx.beginPath();
            ctx.arc(food.x * gridSize + gridSize/2, food.y * gridSize + gridSize/2, gridSize/2 - 2, 0, Math.PI * 2);
            ctx.fill();
        }}

        function changeDirection(event) {{
            const LEFT_KEY = 37; const RIGHT_KEY = 39; const UP_KEY = 38; const DOWN_KEY = 40;
            const W = 87; const A = 65; const S = 83; const D = 68;

            const keyPressed = event.keyCode;
            const goingUp = dy === -1;
            const goingDown = dy === 1;
            const goingRight = dx === 1;
            const goingLeft = dx === -1;

            if ((keyPressed === LEFT_KEY || keyPressed === A) && !goingRight) {{ nextDx = -1; nextDy = 0; }}
            if ((keyPressed === UP_KEY || keyPressed === W) && !goingDown) {{ nextDx = 0; nextDy = -1; }}
            if ((keyPressed === RIGHT_KEY || keyPressed === D) && !goingLeft) {{ nextDx = 1; nextDy = 0; }}
            if ((keyPressed === DOWN_KEY || keyPressed === S) && !goingUp) {{ nextDx = 0; nextDy = 1; }}
        }}

        createFood();
        main();
    </script>
</body>
</html>
"""

# 渲染游戏组件
components.html(game_html, height=500)

# 底部信息
st.markdown("---")
st.write("🛠️ **技术栈**: Streamlit, HTML5 Canvas, JavaScript")
