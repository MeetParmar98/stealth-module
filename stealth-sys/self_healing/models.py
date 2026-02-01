"""
Data models for self-healing stealth system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class DetectionType(Enum):
    """Types of bot detection encountered"""

    CAPTCHA = "captcha"
    RATE_LIMIT = "rate_limit"
    FINGERPRINT_MISMATCH = "fingerprint_mismatch"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    IP_BLOCK = "ip_block"
    UNKNOWN = "unknown"


class StrategyType(Enum):
    """Available healing strategies"""

    CHANGE_FINGERPRINT = "change_fingerprint"
    CHANGE_BEHAVIOR_PROFILE = "change_behavior_profile"
    ADD_DELAYS = "add_delays"
    ROTATE_PROFILE = "rotate_profile"
    RESET_SESSION = "reset_session"
    CHANGE_IP = "change_ip"


@dataclass
class DetectionResult:
    """Result of bot detection check"""

    detected: bool
    detection_type: Optional[DetectionType] = None
    confidence: float = 0.0  # 0.0 to 1.0
    indicators: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "detected": self.detected,
            "detection_type": self.detection_type.value
            if self.detection_type
            else None,
            "confidence": self.confidence,
            "indicators": self.indicators,
            "timestamp": self.timestamp.isoformat(),
            "raw_data": self.raw_data,
        }


@dataclass
class StealthProfile:
    """Complete stealth profile combining fingerprint and behavior"""

    profile_id: str
    fingerprint: Dict[str, Any]
    behavior_config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "profile_id": self.profile_id,
            "fingerprint": self.fingerprint,
            "behavior_config": self.behavior_config,
            "created_at": self.created_at.isoformat(),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass
class HealingStrategy:
    """Strategy to apply when detection occurs"""

    strategy_type: StrategyType
    priority: int  # Lower = higher priority
    parameters: Dict[str, Any] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "strategy_type": self.strategy_type.value,
            "priority": self.priority,
            "parameters": self.parameters,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
        }

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass
class FailureReport:
    """Detailed report of detection failure and healing attempt"""

    report_id: str
    timestamp: datetime
    detection_result: DetectionResult
    profile_used: StealthProfile
    strategies_attempted: List[HealingStrategy]
    final_outcome: str  # 'success', 'failed', 'retry'
    error_messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp.isoformat(),
            "detection_result": self.detection_result.to_dict(),
            "profile_used": self.profile_used.to_dict(),
            "strategies_attempted": [s.to_dict() for s in self.strategies_attempted],
            "final_outcome": self.final_outcome,
            "error_messages": self.error_messages,
            "metadata": self.metadata,
        }

    def save_to_json(self, filepath: str) -> None:
        """Save report to JSON file"""
        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
