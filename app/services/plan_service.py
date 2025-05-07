from app.models import SubscriptionPlan
from app.core.database import db

class PlanService:
    def get_all_plans(self):
        return SubscriptionPlan.query.all()

    def create_plan(self, name, price, duration_days, features=None):
        plan = SubscriptionPlan(
            name=name,
            price=price,
            duration_days=duration_days,
            features=features or {}
        )
        db.session.add(plan)
        db.session.commit()
        return plan

    def get_plan_by_id(self, plan_id):
        return SubscriptionPlan.query.get(int(plan_id))

    def update_plan(self, plan_id, **kwargs):
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        for key, value in kwargs.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        
        db.session.commit()
        return plan

    def delete_plan(self, plan_id):
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        db.session.delete(plan)
        db.session.commit() 