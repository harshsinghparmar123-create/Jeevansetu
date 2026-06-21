import os
import joblib
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.ai.train import train_model


class AISeverityService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is not None:
            return cls._model

        model_path = settings.MODEL_PATH
        if not os.path.exists(model_path):
            logger.warning(
                f"Model file not found at {model_path}. Running model training script..."
            )
            try:
                train_model()
            except Exception as e:
                logger.error(f"Failed to auto-train model: {e}")

        if os.path.exists(model_path):
            try:
                cls._model = joblib.load(model_path)
                logger.info(f"AI Model successfully loaded from {model_path}")
            except Exception as e:
                logger.error(f"Error loading model file: {e}")
        else:
            logger.error("Could not find or load AI Model. Predictions will use hardcoded rules.")

        return cls._model

    @classmethod
    def predict_severity(
        cls,
        impact_force: float,
        speed: float,
        orientation_change: float,
        response_delay: float,
    ) -> dict:
        clf = cls.get_model()
        classes = ["safe", "minor", "moderate", "critical"]

        if clf is not None:
            try:
                # Prepare features
                features = np.array(
                    [[impact_force, speed, orientation_change, response_delay]]
                )

                # Class probabilities and prediction
                prediction = int(clf.predict(features)[0])
                probabilities = clf.predict_proba(features)[0]

                # Score is computed as a weighted sum of classes:
                # safe=0, minor=25, moderate=60, critical=100
                weights = np.array([0, 25, 60, 100])
                score = int(np.dot(probabilities, weights))

                # Ensure score matches the output classification boundaries
                severity_str = classes[prediction]
                logger.info(
                    f"AI severity prediction: {severity_str} (Score: {score}) for features: {features.tolist()}"
                )

                return {"severity": severity_str, "score": score}

            except Exception as e:
                logger.error(f"Model prediction error: {e}. Falling back to rule-based classification.")

        # Fallback Rule-based classification if model loading/execution fails
        if impact_force >= 9.0 or (impact_force >= 6.0 and speed >= 70.0):
            severity_str = "critical"
            score = int(min(70 + (impact_force * 2), 100))
        elif impact_force >= 5.0 or speed >= 45.0:
            severity_str = "moderate"
            score = int(45 + (impact_force * 2.5))
        elif impact_force >= 2.5:
            severity_str = "minor"
            score = int(20 + (impact_force * 3))
        else:
            severity_str = "safe"
            score = int(impact_force * 5)

        return {"severity": severity_str, "score": score}
