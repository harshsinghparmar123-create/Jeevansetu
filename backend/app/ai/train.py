import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Ensure folder exists
os.makedirs(os.path.dirname(__file__), exist_ok=True)


def generate_synthetic_data(num_samples: int = 2000) -> pd.DataFrame:
    np.random.seed(42)

    # Generate random features
    impact_forces = np.random.uniform(0.5, 15.0, num_samples)  # G-force
    speeds = np.random.uniform(0.0, 140.0, num_samples)  # km/h
    orientation_changes = np.random.uniform(0.0, 180.0, num_samples)  # Degrees
    response_delays = np.random.uniform(0.0, 60.0, num_samples)  # Seconds

    data = pd.DataFrame(
        {
            "impact_force": impact_forces,
            "speed": speeds,
            "orientation_change": orientation_changes,
            "response_delay": response_delays,
        }
    )

    # Label generation logic
    labels = []
    for _, row in data.iterrows():
        force = row["impact_force"]
        spd = row["speed"]
        orient = row["orientation_change"]
        delay = row["response_delay"]

        if force >= 9.0 or (force >= 6.0 and spd >= 70.0) or (orient >= 110.0 and force >= 4.0):
            # Critical
            labels.append(3)
        elif force >= 5.0 or spd >= 45.0 or orient >= 60.0:
            # Moderate
            labels.append(2)
        elif force >= 2.5 or spd >= 20.0:
            # Minor
            labels.append(1)
        else:
            # Safe
            labels.append(0)

    data["severity"] = labels
    return data


def train_model():
    print("Generating synthetic crash data for training...")
    df = generate_synthetic_data()

    X = df[["impact_force", "speed", "orientation_change", "response_delay"]]
    y = df["severity"]

    print("Training RandomForestClassifier model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    clf.fit(X, y)

    model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
    print(f"Saving trained model to {model_path}...")
    joblib.dump(clf, model_path)
    print("Model training successfully completed.")


if __name__ == "__main__":
    train_model()
