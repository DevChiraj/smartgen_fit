"""Sri Lankan food / nutrition lookup table."""

from app.extensions import db


class SriLankanFood(db.Model):
    __tablename__ = "sri_lankan_foods"

    food_id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    serving_size = db.Column(db.String(50), nullable=True)

    calories = db.Column(db.Integer, nullable=False)
    protein_g = db.Column(db.Numeric(6, 2), nullable=False)
    carbs_g = db.Column(db.Numeric(6, 2), nullable=False)
    fat_g = db.Column(db.Numeric(6, 2), nullable=False)
    fiber_g = db.Column(db.Numeric(6, 2), nullable=True)
    vitamins = db.Column(db.String(255), nullable=True)
    minerals = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<SriLankanFood {self.food_name}>"
