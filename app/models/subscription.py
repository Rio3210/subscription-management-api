from datetime import datetime
from enum import Enum
from app.core.database import db

class SubscriptionStatus(Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, index=True)  # Uses SubscriptionStatus enum values
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='subscriptions')
    plan = db.relationship('SubscriptionPlan', back_populates='subscriptions')
    
    __table_args__ = (
        db.Index('idx_subscription_status_dates', 'status', 'start_date', 'end_date'),
    )
    
    @property
    def is_active(self):
        return self.status == SubscriptionStatus.ACTIVE.value
    
    @property
    def is_cancelled(self):
        return self.status == SubscriptionStatus.CANCELLED.value 