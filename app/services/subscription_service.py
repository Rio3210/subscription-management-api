from datetime import datetime, timedelta
from app.models import Subscription, SubscriptionPlan, User
from app.core.database import db

class SubscriptionService:
    def get_user_subscriptions(self, user_id):
        return Subscription.query.filter_by(user_id=user_id).all()

    def get_subscriptions_by_status(self, status):
        return (
            Subscription.query
            .filter_by(status=status)
            .order_by(Subscription.created_at.desc())
            .all()
        )

    def get_subscription_by_id(self, subscription_id):
        return Subscription.query.get(subscription_id)

    def create_subscription(self, user_id, plan_id):
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        # Check if user already has an active subscription
        active_sub = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if active_sub:
            raise ValueError("User already has an active subscription")

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_days)

        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status='active',
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(subscription)
        db.session.commit()
        return subscription

    def update_subscription(self, subscription_id, user_id, status=None, plan_id=None):
        subscription = Subscription.query.get(subscription_id)

        if not subscription or subscription.user_id != int(user_id):
            raise ValueError("Subscription not found")

        if status:
            subscription.status = status
            
        if plan_id:
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan:
                raise ValueError("Invalid subscription plan")
                
            old_plan_id = subscription.plan_id
            subscription.plan_id = plan_id
            subscription.updated_at = datetime.utcnow()       
            
        db.session.commit()
        
        return subscription

    def cancel_subscription(self, subscription_id, user_id):
        subscription = Subscription.query.get(subscription_id)
        if not subscription or subscription.user_id != int(user_id):
            raise ValueError("Subscription not found")

        subscription.status = 'cancelled'
        db.session.commit() 