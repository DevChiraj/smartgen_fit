"""Daily meal log entries - a real user-logged food diary. Ties each entry
to a real sri_lankan_foods row rather than free text; calories and protein
are computed at log time from that food's nutrition data times the servings
eaten, so the numbers stay traceable to real data (rule 2's spirit).
"""

from app.extensions import db
from app.models.mixins import utcnow

MEAL_TYPES = ("breakfast", "morning_snack", "lunch", "evening_snack", "dinner")


class MealLog(db.Model):
    __tablename__ = "meal_logs"

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("sri_lankan_foods.food_id"), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    quantity_servings = db.Column(db.Numeric(4, 2), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein_g = db.Column(db.Numeric(6, 2), nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="meal_logs")
    food = db.relationship("SriLankanFood")

    def __repr__(self) -> str:
        return f"<MealLog {self.log_id}>"
