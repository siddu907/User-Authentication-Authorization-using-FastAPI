from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

class Task(Base):

    # Table Name
    __tablename__ = "tasks"

    # Primary Key
    id = Column(Integer,primary_key=True,index=True)

    # Task Title
    title = Column(String(150),nullable=False)

    # Task Description
    description = Column(String(500),nullable=False )

    # Task Status
    status = Column(String(20),default="Pending")

    # Foreign Key Connects Task Table with User Table.
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)

    # Task Creation Time
    created_at = Column( DateTime(timezone=True),default=lambda: datetime.now(UTC),nullable=False)

    # Many Tasks One User
    owner = relationship("User",back_populates="tasks" )