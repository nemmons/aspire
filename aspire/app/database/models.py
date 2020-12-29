from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from typing import List
from .engine import Base


class RatingManual(Base):
    __tablename__ = 'rating_manuals'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created = Column(DateTime)

    rating_steps = relationship("RatingStep", back_populates="rating_manual")
    rating_factors = relationship("RatingFactor", back_populates="rating_manual")
    rating_variables = relationship("RatingVariable", back_populates="rating_manual")

    def __str__(self):
        return str(self.id) + ": " + self.name


class RatingStep(Base):
    __tablename__ = 'rating_steps'

    id = Column(Integer, primary_key=True)
    rating_manual_id = Column(Integer, ForeignKey('rating_manuals.id'))
    rating_step_type_id = Column(Integer, ForeignKey('rating_step_types.id'))  # type: int
    name = Column(String(50))
    description = Column(String(255))
    step_order = Column(Integer)
    target = Column(String(50))
    conditions = Column(String(512))
    created = Column(DateTime)

    rating_manual = relationship("RatingManual", back_populates="rating_steps")
    rating_step_type = relationship("RatingStepType")
    rating_step_parameters = relationship("RatingStepParameter",
                                          back_populates="rating_step")  # type: List[RatingStepParameter]

    def __str__(self):
        return str(self.id) + ": " + self.name


class RatingVariable(Base):
    __tablename__ = 'rating_variables'

    id = Column(Integer, primary_key=True)
    rating_manual_id = Column(Integer, ForeignKey('rating_manuals.id'))
    name = Column(String(50))
    description = Column(String(255))
    variable_type = Column(String(10))
    is_input = Column(Boolean)
    is_required = Column(Boolean)
    default = Column(String(25))
    constraints = Column(String(255))
    length = Column(String(10))
    created = Column(DateTime)

    rating_manual = relationship("RatingManual", back_populates="rating_variables")

    def __str__(self):
        return str(self.id) + ": " + self.name


class RatingStepParameter(Base):
    __tablename__ = 'rating_step_parameters'

    id = Column(Integer, primary_key=True)
    rating_manual_id = Column(Integer, ForeignKey('rating_manuals.id'))
    rating_step_id = Column(Integer, ForeignKey('rating_steps.id'))
    parameter_order = Column(Integer)
    label = Column(String(50))
    value = Column(String(50))
    parameter_type = Column(Integer)  # type: int
    created = Column(DateTime)

    rating_step = relationship("RatingStep")

    def __str__(self):
        return str(self.id) + ": " + (self.label or "")


class RatingStepType(Base):
    __tablename__ = 'rating_step_types'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __str__(self):
        return str(self.id) + ": " + self.name


class RatingFactor(Base):
    __tablename__ = 'rating_factors'

    id = Column(Integer, primary_key=True)
    rating_manual_id = Column(Integer, ForeignKey('rating_manuals.id'))
    type = Column(String(50))
    num_col_1 = Column(Numeric(12, 4))
    num_col_2 = Column(Numeric(12, 4))
    num_col_3 = Column(Numeric(12, 4))
    str_col_1 = Column(String(20))
    str_col_2 = Column(String(20))
    str_col_3 = Column(String(20))
    value = Column(String)

    rating_manual = relationship("RatingManual")
