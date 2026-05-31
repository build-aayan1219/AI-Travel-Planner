#!/bin/bash
# ============================================================
#  run_all_training.sh
#  Trains ALL 5 ML models in one go
#
#  HOW TO RUN:
#  cd travel-planner
#  chmod +x ml/run_all_training.sh
#  ./ml/run_all_training.sh
# ============================================================

echo ""
echo "======================================================"
echo "   AI Group Travel Planner — Train All ML Models"
echo "======================================================"
echo ""

# Activate virtual environment if not already active
source venv/bin/activate 2>/dev/null || true

PASS=0
FAIL=0

run_script() {
    local name=$1
    local script=$2
    echo "------------------------------------------------------"
    echo "  Training: $name"
    echo "------------------------------------------------------"
    python $script
    if [ $? -eq 0 ]; then
        echo "  ✅ $name — SUCCESS"
        PASS=$((PASS+1))
    else
        echo "  ❌ $name — FAILED (check error above)"
        FAIL=$((FAIL+1))
    fi
    echo ""
}

run_script "Trip Cost Predictor"       "ml/train_model.py"
run_script "Flight Price Predictor"    "ml/train_flight_model.py"
run_script "Destination Recommender"   "ml/train_destination_model.py"
run_script "Hotel Price Predictor"     "ml/train_hotel_model.py"
run_script "Best Season Predictor"     "ml/train_season_model.py"

echo "======================================================"
echo "  TRAINING COMPLETE"
echo "  Passed : $PASS / 5"
echo "  Failed : $FAIL / 5"
echo ""
echo "  Saved model files in ml/ folder:"
ls ml/*.pkl 2>/dev/null | sed 's/^/    /'
echo ""
echo "  Run your app:"
echo "  streamlit run app.py"
echo "======================================================"