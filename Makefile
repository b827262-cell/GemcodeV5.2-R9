# Makefile
.PHONY: run-cloud stop logs clean

# 🚀 模擬 Cloud Run 單一容器運行
run-cloud:
	@echo "🚀 正在使用 Cloud Run 模式建構與啟動 (Port 8080)..."
	@docker-compose up --build -d
	@echo "========================================="
	@echo "✅ IDE 啟動完成！"
	@echo "🌍 請在瀏覽器開啟: http://localhost:8080"
	@echo "========================================="

# 🛑 停止容器
stop:
	@docker-compose down
	@echo "✅ 容器已停止。"

# 🔍 查看日誌
logs:
	@docker-compose logs -f

# 🧹 清理暫存與 Volumes
clean:
	@docker-compose down -v
	@rm -rf backend/workspaces/*
	@echo "✅ 環境已重置。"
