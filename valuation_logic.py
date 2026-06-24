import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import category_encoders as ce


def predict_price(
    make, model, age, mileage, fuel="Gas", body="Sedan", gov="Cairo", trans="Automatic"
):
    model_clean = model if model_counts.get(model, 0) >= 10 else "Other"
    row = pd.DataFrame(
        [
            {
                "Make": make,
                "ModelClean": model_clean,
                "Fuel Type": fuel,
                "Body Type": body,
                "Governorate": gov,
                "Transmission": trans,
            }
        ]
    )

    Xcat1 = encoder1.transform(row[cat_cols1])
    Xcat2 = encoder2.transform(row[cat_cols2])
    Xcat = np.hstack([Xcat1, Xcat2])

    Xnum = np.array([[age, mileage]])
    X = np.hstack([Xnum, Xcat])

    # individual-tree spread = our confidence band
    tree_preds = np.array([t.predict(X)[0] for t in rf.estimators_])
    log_p10, log_p50, log_p90 = np.percentile(tree_preds, [10, 50, 90])
    return {
        "predicted": np.expm1(log_p50),
        "low": np.expm1(log_p10),
        "high": np.expm1(log_p90),
    }


def vrs_for(make, model=None):
    if model and "model_curves" in globals():
        matched_model = model_curves[
            (model_curves["Make"] == make) & (model_curves["Model"] == model)
        ]
        if not matched_model.empty:
            vrs = float(matched_model["VRS"].values[0])
            return vrs, "model-level"

    if "model_curves" in globals():
        market_median = float(model_curves["VRS"].median())
        return market_median, "market-median fallback"

    return None, "insufficient data"


def grade(vrs):
    if vrs is None:
        return "Unrated"
    if vrs >= 90:
        return "A+ Elite Retention (Loses ~5% per year)"
    if vrs >= 80:
        return "A Strong Retention (Loses ~6% per year)"
    if vrs >= 70:
        return "B Good Retention (Loses ~7% per year)"
    if vrs >= 50:
        return "C Average Retention (Loses ~8-9% per year)"
    return "D High Depreciation Risk (Loses >10% per year)"


def future_value(make, model, current_age, mileage_now, horizons=(3, 5, 10), **kwargs):
    out = {}
    for h in horizons:
        future_age = current_age + h
        future_mileage = mileage_now + h * KM_PER_YEAR
        out[h] = predict_price(make, model, future_age, future_mileage, **kwargs)
    return out


def investment_rating(make, model, listing_price, age, mileage, **kwargs):

    pred = predict_price(make, model, age, mileage, **kwargs)
    vrs, basis = vrs_for(make, model)
    price_gap = (listing_price - pred["predicted"]) / pred["predicted"]

    if vrs is None:
        rating = "Insufficient data to rate"
    elif vrs >= 75 and price_gap <= -0.05:
        rating = "Buy"
    elif vrs < 45 or price_gap >= 0.15:
        rating = "Avoid"
    elif vrs >= 60 and abs(price_gap) < 0.10:
        rating = "Buy"
    else:
        rating = "Hold"

    return {
        "rating": rating,
        "grade": grade(vrs),
        "VRS": round(vrs, 1) if vrs is not None else None,
        "VRS_basis": basis,
        "fair_value_estimate": round(pred["predicted"]),
        "listing_vs_fair_value_%": round(price_gap * 100, 1),
    }


def explain(make, model, lang="en"):
    vrs, basis = vrs_for(make, model)
    g = grade(vrs)
    vrs_txt = f"{vrs:.0f}/100" if vrs is not None else "not available"

    if vrs is not None:
        annual_ret = 85 + (vrs / 100) * (97 - 85)  # reverse the VRS scaling
        annual_loss = round(100 - annual_ret, 1)
        loss_txt = f"loses roughly {annual_loss}% of its value per year"
        loss_ar = f"تخسر نحو {annual_loss}% من قيمتها سنوياً"
    else:
        loss_txt = "insufficient data to estimate annual depreciation"
        loss_ar = "لا تتوفر بيانات كافية لتقدير الاستهلاك السنوي"

    commentary = {
        "A+ Elite Retention": "It consistently commands high demand on Hatla2ee and spare parts are widely available at competitive Egyptian prices.",
        "A Strong Retention": "It enjoys strong local demand and is among the easier models to resell quickly on Hatla2ee.",
        "B Good Retention": "It holds moderate demand in the Egyptian market with a reasonable resale timeline.",
        "C Average Retention": "Resale can take longer in the Egyptian market; buyers are more price-sensitive for this model.",
        "D High Depreciation Risk": "Weak local demand and/or high maintenance costs make this a slow reseller on Hatla2ee.",
        "Unrated (insufficient data)": "Too few listings across age bands to compute a reliable retention score for this model.",
    }
    note = commentary.get(g, "")

    model_str = model if model else ""

    if lang == "ar":
        commentary_ar = {
            "A+ Elite Retention": "تحظى بطلب مرتفع باستمرار على هتلاقي وقطع غيارها متاحة بأسعار تنافسية في السوق المصري.",
            "A Strong Retention": "تتمتع بطلب محلي قوي وتُعدّ من أسهل الموديلات إعادةً للبيع على هتلاقي.",
            "B Good Retention": "تحافظ على طلب معقول في السوق المصري مع جدول زمني مقبول لإعادة البيع.",
            "C Average Retention": "قد تستغرق إعادة بيعها وقتاً أطول في السوق المصري والمشترون أكثر حساسية للسعر.",
            "D High Depreciation Risk": "ضعف الطلب المحلي و/أو ارتفاع تكاليف الصيانة يجعلانها بطيئة البيع على هتلاقي.",
            "Unrated (insufficient data)": "عدد الإعلانات عبر الفئات العمرية غير كافٍ لحساب درجة احتفاظ موثوقة لهذا الموديل.",
        }
        note_ar = commentary_ar.get(g, "")
        return (
            f'{make} {model_str} حصلت على تقييم "{g}" '
            f"بمعدل VRS {vrs_txt} ({basis}). "
            f"هذا يعني أن السيارة {loss_ar}. "
            f"{note_ar}"
        )

    return (
        f'{make} {model_str} received a "{g}" rating '
        f"with a VRS of {vrs_txt} ({basis}). "
        f"This means the car {loss_txt}. "
        f"{note}"
    )


rf = None
encoder1 = None
encoder2 = None

cat_cols1 = None
cat_cols2 = None

model_counts = None
model_curves = None

KM_PER_YEAR = None
