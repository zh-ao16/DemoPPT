#!/bin/bash
# DemoPPT 一键启动脚本

echo "🎯 DemoPPT 启动中..."

# 创建输出目录
mkdir -p output

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
pip install -q -r requirements.txt 2>/dev/null

# 启动后端
echo "🚀 启动后端服务 (http://localhost:8000)..."
python main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务 (http://localhost:3000)..."
cd ../frontend
npm install -q 2>/dev/null
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ DemoPPT 已启动！"
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务"
