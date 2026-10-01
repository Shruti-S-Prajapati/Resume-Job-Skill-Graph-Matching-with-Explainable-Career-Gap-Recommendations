import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score


def compute_evaluation_metrics(annotated_csv: str = "data/annotation_template.csv"):
    df = pd.read_csv(annotated_csv)

    # sirf "missing" wali rows pe evaluate karte hain (gap detection ka core kaam)
    gap_rows = df[df["system_label"] == "missing"].copy()
    gap_rows = gap_rows.dropna(subset=["correct_gap"])

    y_true = gap_rows["correct_gap"].astype(int)   # human ne kaha ye sahi gap hai ya nahi
    y_pred = [1] * len(gap_rows)                     # system ne inhe "missing/gap" bola tha (all 1)

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"Total annotated gap predictions: {len(gap_rows)}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 Score: {f1:.3f}")

    human_agreement = y_true.mean()
    print(f"\nHuman agreement rate (system correct per annotator): {human_agreement:.2%}")

    return {"precision": precision, "recall": recall, "f1": f1, "human_agreement": human_agreement}


if __name__ == "__main__":
    compute_evaluation_metrics()