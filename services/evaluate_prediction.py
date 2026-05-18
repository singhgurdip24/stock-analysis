from database import SessionLocal
from models.prediction import Prediction
from services.fetch_signals_alpha import get_current_price


def evaluate_prediction(prediction, current_price: float) -> str:
    change_pct = (
        (current_price - prediction.price_at_prediction)
        / prediction.price_at_prediction
    ) * 100

    if prediction.short_term == "bullish":
        return "correct" if change_pct > 3 else "incorrect"
    elif prediction.short_term == "bearish":
        return "correct" if change_pct < -3 else "incorrect"
    return "correct" if abs(change_pct) <= 3 else "incorrect"


def evaluate_all_predictions():
    db = SessionLocal()
    try:
        pending = db.query(Prediction).filter(Prediction.actual_price == None).all()
        print(f"[evaluate] {len(pending)} predictions to evaluate")

        for prediction in pending:
            try:
                current_price = get_current_price(prediction.ticker)
                prediction.actual_price = current_price
                prediction.evaluation_result = evaluate_prediction(prediction, current_price)
            except Exception as e:
                print(f"[evaluate] skipping {prediction.ticker} (id={prediction.id}): {e}")

        db.commit()
        print("[evaluate] done")
    finally:
        db.close()
