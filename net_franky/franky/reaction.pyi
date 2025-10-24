from __future__ import annotations

from typing import List, Type

from ._franky import (
    BaseCartesianPoseMotion,
    BaseCartesianVelocityMotion,
    BaseJointPositionMotion,
    BaseJointVelocityMotion,
    BaseTorqueMotion,
    CartesianPoseReaction as _CartesianPoseReaction,
    CartesianVelocityReaction as _CartesianVelocityReaction,
    Condition,
    JointPositionReaction as _JointPositionReaction,
    JointVelocityReaction as _JointVelocityReaction,
    TorqueReaction as _TorqueReaction,
)

from .motion import Motion


class Reaction:
    _control_signal_type: None

    def __new__(cls, condition: Condition, motion: Motion) -> Reaction: ...


class CartesianPoseReaction(_CartesianPoseReaction, Reaction):
    _motion_type: Type[BaseCartesianPoseMotion]


class CartesianVelocityReaction(_CartesianVelocityReaction, Reaction):
    _motion_type: Type[BaseCartesianVelocityMotion]


class JointPositionReaction(_JointPositionReaction, Reaction):
    _motion_type: Type[BaseJointPositionMotion]


class JointVelocityReaction(_JointVelocityReaction, Reaction):
    _motion_type: Type[BaseJointVelocityMotion]


class TorqueReaction(_TorqueReaction, Reaction):
    _motion_type: Type[BaseTorqueMotion]


_REACTION_TYPES: List[Type[Reaction]]
