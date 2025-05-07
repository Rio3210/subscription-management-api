from datetime import datetime
from app.core.database import db

class SubscriptionHistory(db.Model):
    __tablename__ = 'subscription_history'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    old_plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    new_plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=True)
    change_type = db.Column(db.String(20), nullable=False)  # 'create', 'upgrade', 'downgrade', 'cancel'
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    

    subscription = db.relationship('Subscription', backref='history')
    user = db.relationship('User')
    old_plan = db.relationship('SubscriptionPlan', foreign_keys=[old_plan_id])
    new_plan = db.relationship('SubscriptionPlan', foreign_keys=[new_plan_id])
    
    __table_args__ = (
        db.Index('idx_subscription_history_user_date', 'user_id', 'changed_at'),
    ) 