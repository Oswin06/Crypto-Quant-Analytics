"""
Alert management system for monitoring conditions on real-time data.
"""
from typing import List, Dict, Callable, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Alert:
    """Represents a single alert rule."""
    
    def __init__(self, condition: str, callback: Callable = None):
        """
        Initialize alert.
        
        Args:
            condition: Condition string (e.g., 'zscore > 2', 'price > 50000')
            callback: Function to call when alert triggers
        """
        self.condition = condition
        self.callback = callback
        self.triggered = False
        self.triggered_at = None
        self.trigger_count = 0
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate alert condition.
        
        Args:
            context: Dictionary containing variables for condition evaluation
        
        Returns:
            True if alert should trigger
        """
        try:
            # Simple evaluation using eval (in production, use a proper expression parser)
            # This is a simplified version - in production, use AST parsing
            result = eval(self.condition, {"__builtins__": {}, **context})
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating alert condition: {e}")
            return False
    
    def trigger(self, data: Dict[str, Any]):
        """Trigger the alert."""
        self.triggered = True
        self.triggered_at = datetime.now().isoformat()
        self.trigger_count += 1
        
        if self.callback:
            self.callback(self, data)
        
        logger.info(f"Alert triggered: {self.condition}")


class AlertManager:
    """Manages multiple alert rules."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_history: List[Dict[str, Any]] = []
    
    def add_alert(self, condition: str, callback: Callable = None) -> Alert:
        """
        Add a new alert rule.
        
        Args:
            condition: Alert condition string
            callback: Optional callback function
        
        Returns:
            Created Alert object
        """
        alert = Alert(condition, callback)
        self.alerts.append(alert)
        logger.info(f"Added alert: {condition}")
        return alert
    
    def remove_alert(self, condition: str):
        """Remove an alert rule."""
        self.alerts = [a for a in self.alerts if a.condition != condition]
        logger.info(f"Removed alert: {condition}")
    
    def evaluate_alerts(self, context: Dict[str, Any]):
        """
        Evaluate all alerts against a context.
        
        Args:
            context: Dictionary containing variables for condition evaluation
        """
        for alert in self.alerts:
            try:
                if alert.evaluate(context):
                    if not alert.triggered:
                        alert.trigger(context)
                        self._record_alert(alert, context)
            except Exception as e:
                logger.error(f"Error evaluating alert {alert.condition}: {e}")
    
    def _record_alert(self, alert: Alert, data: Dict[str, Any]):
        """Record alert in history."""
        self.alert_history.append({
            'condition': alert.condition,
            'triggered_at': alert.triggered_at,
            'trigger_count': alert.trigger_count,
            'context': data
        })
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        return self.alert_history[-limit:]
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts with their status."""
        return [
            {
                'condition': alert.condition,
                'triggered': alert.triggered,
                'triggered_at': alert.triggered_at,
                'trigger_count': alert.trigger_count
            }
            for alert in self.alerts
        ]


