"""
Self-Healing Engine
===================
Automatically heals from bot detection using adaptive strategies.
"""

import uuid
import json
import os
from typing import List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path

from .models import (
    DetectionResult,
    StealthProfile,
    HealingStrategy,
    StrategyType,
    FailureReport,
    DetectionType,
)
from .detector import BotDetector
from .profile_generator import ProfileGenerator


class SelfHealer:
    """Self-healing engine that adapts to bot detection"""

    def __init__(self, max_retries: int = 3, report_dir: str = "./healing_reports"):
        """
        Initialize self-healer

        Args:
            max_retries: Maximum retry attempts per detection
            report_dir: Directory to save failure reports
        """
        self.max_retries = max_retries
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.detector = BotDetector()
        self.profile_generator = ProfileGenerator()

        # Current active profile
        self.current_profile: Optional[StealthProfile] = None

        # Available healing strategies (ordered by priority)
        self.strategies = self._initialize_strategies()

        # History
        self.healing_history: List[FailureReport] = []

    def _initialize_strategies(self) -> List[HealingStrategy]:
        """Initialize available healing strategies"""
        return [
            HealingStrategy(
                strategy_type=StrategyType.ADD_DELAYS,
                priority=1,
                parameters={"min_delay": 1.0, "max_delay": 3.0},
            ),
            HealingStrategy(
                strategy_type=StrategyType.CHANGE_BEHAVIOR_PROFILE,
                priority=2,
                parameters={"profile_type": "conservative"},
            ),
            HealingStrategy(
                strategy_type=StrategyType.CHANGE_FINGERPRINT,
                priority=3,
                parameters={"regenerate": True},
            ),
            HealingStrategy(
                strategy_type=StrategyType.ROTATE_PROFILE,
                priority=4,
                parameters={"use_best": True},
            ),
            HealingStrategy(
                strategy_type=StrategyType.RESET_SESSION,
                priority=5,
                parameters={"clear_cookies": True},
            ),
        ]

    def check_and_heal(
        self,
        html_content: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[dict] = None,
        url: Optional[str] = None,
        action_callback: Optional[Callable] = None,
    ) -> tuple[bool, Optional[StealthProfile], Optional[FailureReport]]:
        """
        Check for bot detection and heal if detected

        Args:
            html_content: HTML response content
            status_code: HTTP status code
            headers: Response headers
            url: Current URL
            action_callback: Callback function to retry action after healing

        Returns:
            Tuple of (success, profile, report)
            - success: Whether healing succeeded
            - profile: Updated stealth profile to use
            - report: Failure report (if detection occurred)
        """
        # Check for detection
        detection = self.detector.check_response(
            html_content=html_content, status_code=status_code, headers=headers, url=url
        )

        if not detection.detected:
            # No detection, update success count
            if self.current_profile:
                self.current_profile.success_count += 1
                self.current_profile.last_used = datetime.now()
            return True, self.current_profile, None

        # Detection occurred - start healing process
        print(
            f"🚨 Bot detection detected! Type: {detection.detection_type}, Confidence: {detection.confidence:.2f}"
        )

        # Initialize profile if needed
        if not self.current_profile:
            self.current_profile = self.profile_generator.generate_profile()

        # Update failure count
        self.current_profile.failure_count += 1

        # Attempt healing
        success, report = self._attempt_healing(
            detection=detection, action_callback=action_callback
        )

        return success, self.current_profile, report

    def _attempt_healing(
        self, detection: DetectionResult, action_callback: Optional[Callable] = None
    ) -> tuple[bool, FailureReport]:
        """
        Attempt to heal from detection

        Args:
            detection: Detection result
            action_callback: Callback to retry action

        Returns:
            Tuple of (success, report)
        """
        strategies_attempted = []
        error_messages = []

        # Try strategies in order of priority
        sorted_strategies = sorted(self.strategies, key=lambda s: s.priority)

        for attempt in range(self.max_retries):
            print(f"🔧 Healing attempt {attempt + 1}/{self.max_retries}")

            # Select strategy based on detection type and past success
            strategy = self._select_strategy(detection, sorted_strategies)
            strategies_attempted.append(strategy)

            # Apply strategy
            try:
                success = self._apply_strategy(strategy, detection)

                if success:
                    print(f"✅ Strategy {strategy.strategy_type.value} succeeded!")
                    strategy.success_count += 1

                    # Test if healing worked
                    if action_callback:
                        try:
                            action_callback()
                            # If callback succeeds, healing worked
                            report = self._create_report(
                                detection=detection,
                                strategies=strategies_attempted,
                                outcome="success",
                                errors=error_messages,
                            )
                            return True, report
                        except Exception as e:
                            error_messages.append(f"Callback failed: {str(e)}")
                            strategy.failure_count += 1
                    else:
                        # No callback, assume success
                        report = self._create_report(
                            detection=detection,
                            strategies=strategies_attempted,
                            outcome="success",
                            errors=error_messages,
                        )
                        return True, report
                else:
                    error_messages.append(
                        f"Strategy {strategy.strategy_type.value} failed"
                    )
                    strategy.failure_count += 1

            except Exception as e:
                error_messages.append(f"Strategy error: {str(e)}")
                strategy.failure_count += 1

        # All attempts failed
        print(f"❌ All healing attempts failed")
        report = self._create_report(
            detection=detection,
            strategies=strategies_attempted,
            outcome="failed",
            errors=error_messages,
        )

        return False, report

    def _select_strategy(
        self, detection: DetectionResult, strategies: List[HealingStrategy]
    ) -> HealingStrategy:
        """Select best strategy based on detection type and history"""
        # Map detection types to preferred strategies
        preferred_strategies = {
            DetectionType.CAPTCHA: StrategyType.CHANGE_FINGERPRINT,
            DetectionType.RATE_LIMIT: StrategyType.ADD_DELAYS,
            DetectionType.FINGERPRINT_MISMATCH: StrategyType.CHANGE_FINGERPRINT,
            DetectionType.BEHAVIORAL_ANOMALY: StrategyType.CHANGE_BEHAVIOR_PROFILE,
            DetectionType.IP_BLOCK: StrategyType.RESET_SESSION,
        }

        # Try to find preferred strategy
        if detection.detection_type:
            preferred = preferred_strategies.get(detection.detection_type)
            for strategy in strategies:
                if strategy.strategy_type == preferred:
                    return strategy

        # Otherwise, use strategy with best success rate
        strategies_with_history = [
            s for s in strategies if s.success_count + s.failure_count > 0
        ]
        if strategies_with_history:
            return max(strategies_with_history, key=lambda s: s.success_rate)

        # Fallback to highest priority
        return strategies[0]

    def _apply_strategy(
        self, strategy: HealingStrategy, detection: DetectionResult
    ) -> bool:
        """
        Apply a healing strategy

        Args:
            strategy: Strategy to apply
            detection: Detection result

        Returns:
            True if strategy applied successfully
        """
        print(f"  Applying strategy: {strategy.strategy_type.value}")

        try:
            if strategy.strategy_type == StrategyType.CHANGE_FINGERPRINT:
                # Generate new fingerprint
                new_profile = self.profile_generator.generate_profile()
                self.current_profile.fingerprint = new_profile.fingerprint
                return True

            elif strategy.strategy_type == StrategyType.CHANGE_BEHAVIOR_PROFILE:
                # Generate new behavior config
                profile_type = strategy.parameters.get("profile_type", "random")
                new_profile = self.profile_generator.generate_profile(
                    profile_type=profile_type
                )
                self.current_profile.behavior_config = new_profile.behavior_config
                return True

            elif strategy.strategy_type == StrategyType.ADD_DELAYS:
                # Update behavior config with more delays
                min_delay = strategy.parameters.get("min_delay", 1.0)
                max_delay = strategy.parameters.get("max_delay", 3.0)
                self.current_profile.behavior_config["pause_frequency"] = max_delay
                return True

            elif strategy.strategy_type == StrategyType.ROTATE_PROFILE:
                # Switch to best performing profile
                best_profile = self.profile_generator.get_best_profile()
                if best_profile:
                    self.current_profile = best_profile
                    return True
                return False

            elif strategy.strategy_type == StrategyType.RESET_SESSION:
                # Generate completely new profile
                self.current_profile = self.profile_generator.generate_profile()
                return True

            return False

        except Exception as e:
            print(f"  ⚠️  Strategy application error: {e}")
            return False

    def _create_report(
        self,
        detection: DetectionResult,
        strategies: List[HealingStrategy],
        outcome: str,
        errors: List[str],
    ) -> FailureReport:
        """Create and save failure report"""
        report_id = str(uuid.uuid4())

        report = FailureReport(
            report_id=report_id,
            timestamp=datetime.now(),
            detection_result=detection,
            profile_used=self.current_profile,
            strategies_attempted=strategies,
            final_outcome=outcome,
            error_messages=errors,
            metadata={
                "max_retries": self.max_retries,
                "total_attempts": len(strategies),
            },
        )

        # Save to file
        report_path = self.report_dir / f"report_{report_id}.json"
        report.save_to_json(str(report_path))
        print(f"📄 Report saved: {report_path}")

        # Add to history
        self.healing_history.append(report)

        return report

    def get_current_profile(self) -> StealthProfile:
        """Get current active profile, generating one if needed"""
        if not self.current_profile:
            self.current_profile = self.profile_generator.generate_profile()
        return self.current_profile

    def get_statistics(self) -> dict:
        """Get healing statistics"""
        total_detections = len(self.healing_history)
        successful_healings = sum(
            1 for r in self.healing_history if r.final_outcome == "success"
        )

        return {
            "total_detections": total_detections,
            "successful_healings": successful_healings,
            "success_rate": successful_healings / total_detections
            if total_detections > 0
            else 0.0,
            "current_profile_success_rate": self.current_profile.success_rate
            if self.current_profile
            else 0.0,
            "strategies": [s.to_dict() for s in self.strategies],
        }
