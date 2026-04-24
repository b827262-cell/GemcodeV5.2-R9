FRONTEND_PORT ?= 3001
BACKEND_PORT  ?= 8000

LOG_DIR   := logs
PIDS_FILE := .pids
ENV_FILE  := frontend/.env

.PHONY: dev stop clean prepare restart logs

dev: clean prepare
	@echo "🚀 Starting FULL DEV environment..."
	@mkdir -p $(LOG_DIR)
	@rm -f $(PIDS_FILE)

	@echo "🐍 backend..."
	@cd backend && ../venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT) > ../$(LOG_DIR)/backend.log 2>&1 & echo $$! >> ../$(PIDS_FILE)

	@sleep 1

	@echo "⚛️ frontend..."
	@cd frontend && npx vite --port $(FRONTEND_PORT) > ../$(LOG_DIR)/frontend.log 2>&1 & echo $$! >> ../$(PIDS_FILE)

	@sleep 2

	@echo "🌐 tunnel..."
	@cloudflared tunnel --url http://localhost:$(FRONTEND_PORT) > $(LOG_DIR)/tunnel.log 2>&1 & echo $$! >> $(PIDS_FILE)

	@sleep 2

	@echo "🌍 Detect URL..."
	@URL=""; \
	for i in $$(seq 1 10); do \
		URL=$$(grep -o 'https://[^ ]*trycloudflare.com' $(LOG_DIR)/tunnel.log | head -n1 || true); \
		if [ ! -z "$$URL" ]; then break; fi; \
		sleep 1; \
	done; \
	echo "$$URL" > .public_url; \
	echo "👉 $$URL"

	@echo "⚙️ ENV..."
	@echo "VITE_API_URL=$$(cat .public_url)" > $(ENV_FILE)

	@echo "🔄 restart frontend..."
	@pkill -f "[v]ite" 2>/dev/null || true
	@sleep 1
	@cd frontend && npx vite --port $(FRONTEND_PORT) > ../$(LOG_DIR)/frontend.log 2>&1 & echo $$! >> ../$(PIDS_FILE)

	@echo "✅ DEMO READY"
	@echo "🌍 $$(cat .public_url)"

	@trap 'make stop; exit' INT TERM; \
	while true; do sleep 1; done


stop:
	@pkill -f "[u]vicorn" 2>/dev/null || true
	@pkill -f "[v]ite" 2>/dev/null || true
	@pkill -f "[c]loudflared" 2>/dev/null || true
	@echo "stopped"

clean:
	@rm -rf $(LOG_DIR) $(PIDS_FILE) .public_url frontend/.env

prepare:
	@mkdir -p $(LOG_DIR)

logs:
	@tail -f $(LOG_DIR)/*.log

