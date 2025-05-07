from datetime import datetime, timedelta
from app.models import Subscription, SubscriptionPlan, User, SubscriptionHistory
from app.core.database import db
from sqlalchemy import desc, and_
from sqlalchemy.orm import joinedload, contains_eager
from typing import Dict, List
from itertools import groupby

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

    def _record_subscription_history(self, subscription, change_type, old_plan_id=None, new_plan_id=None, old_status=None, new_status=None):
        history = SubscriptionHistory(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            old_plan_id=old_plan_id,
            new_plan_id=new_plan_id,
            old_status=old_status,
            new_status=new_status,
            change_type=change_type
        )
        db.session.add(history)
        db.session.commit()

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
        
        self._record_subscription_history(
            subscription=subscription,
            change_type='create',
            new_plan_id=plan_id,
            new_status='active'
        )
        
        return subscription

    def update_subscription(self, subscription_id, user_id, status=None, plan_id=None):
        subscription = Subscription.query.get(subscription_id)

        if not subscription or subscription.user_id != int(user_id):
            raise ValueError("Subscription not found")

        old_status = subscription.status
        old_plan_id = subscription.plan_id
        change_type = None

        if status:
            subscription.status = status
            change_type = 'cancel' if status == 'cancelled' else 'status_change'
            
        if plan_id:
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan:
                raise ValueError("Invalid subscription plan")
                
            subscription.plan_id = plan_id
            subscription.updated_at = datetime.utcnow()
            
            # Determine if this is an upgrade or downgrade
            old_plan = SubscriptionPlan.query.get(old_plan_id)
            change_type = 'upgrade' if plan.price > old_plan.price else 'downgrade'
            
        db.session.commit()
        
        # Record the change in history
        self._record_subscription_history(
            subscription=subscription,
            change_type=change_type,
            old_plan_id=old_plan_id if plan_id else None,
            new_plan_id=plan_id if plan_id else None,
            old_status=old_status if status else None,
            new_status=status if status else None
        )
        
        return subscription

    def cancel_subscription(self, subscription_id, user_id):
        subscription = Subscription.query.get(subscription_id)
        if not subscription or subscription.user_id != int(user_id):
            raise ValueError("Subscription not found")

        subscription.status = 'cancelled'
        db.session.commit()

    def get_subscription_history_by_id(self, subscription_id: int) -> List[SubscriptionHistory]:
        return (
            SubscriptionHistory.query
            .join(SubscriptionHistory.subscription)
            .options(
                contains_eager(SubscriptionHistory.subscription),
                joinedload(SubscriptionHistory.old_plan),
                joinedload(SubscriptionHistory.new_plan)
            )
            .filter(SubscriptionHistory.subscription_id == subscription_id)
            .order_by(desc(SubscriptionHistory.changed_at))
            .all()
        )

    def get_all_user_subscription_history(self, user_id: int) -> Dict[int, List[SubscriptionHistory]]:
        history_entries = (
            SubscriptionHistory.query
            .join(Subscription, and_(
                Subscription.id == SubscriptionHistory.subscription_id,
                Subscription.user_id == user_id
            ))
            .options(
                joinedload(SubscriptionHistory.old_plan),
                joinedload(SubscriptionHistory.new_plan),
                joinedload(SubscriptionHistory.subscription)
            )
            .order_by(
                SubscriptionHistory.subscription_id,
                desc(SubscriptionHistory.changed_at)
            )
            .all()
        )
        
        return {
            subscription_id: list(entries)
            for subscription_id, entries in 
            groupby(history_entries, key=lambda x: x.subscription_id)
        } 