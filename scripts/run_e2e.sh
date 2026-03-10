#!/bin/bash
set -e

source .venv/bin/activate

echo "=== Starting Streamlit app ==="
streamlit run src/app.py --server.headless true --server.port 8501 &
STREAMLIT_PID=$!

trap "kill $STREAMLIT_PID 2>/dev/null || true" EXIT

echo "Waiting for app to start..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "App is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "=== Running E2E tests ==="
python -m pytest tests/e2e/ -v --screenshot=on --output=tests/e2e/screenshots/ 2>&1 || true

echo ""
echo "=== Screenshots saved to tests/e2e/screenshots/ ==="
ls -la tests/e2e/screenshots/*.png 2>/dev/null || echo "No screenshots found"
echo ""
echo "=== WCAG reports ==="
ls -la tests/e2e/screenshots/*.json 2>/dev/null || echo "No WCAG reports found"