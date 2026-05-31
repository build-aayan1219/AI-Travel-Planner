#!/bin/bash
# ============================================================
#  train_all.sh  —  Train all ML models in one command
#
#  HOW TO RUN:
#  chmod +x ml/train_all.sh
#  ./ml/train_all.sh
# ============================================================
echo "======================================================"
echo "  Training ALL ML Models"
echo "======================================================"

source venv/bin/activate 2>/dev/null || true

echo ""
echo "[1/4] Training Trip Cost Predictor..."
python ml/train_model.py

echo ""
echo "[2/4] Training Flight Price Predictor..."
python ml/train_flight_model.py

echo ""
echo "[3/4] Training Destination Recommender..."
python ml/train_destination_model.py

echo ""
echo "[4/4] Training Hotel Price Predictor..."
python ml/train_hotel_model.py

echo ""
echo "======================================================"
echo "  ALL MODELS TRAINED SUCCESSFULLY"
echo "  Run: streamlit run app.py"
echo "======================================================"