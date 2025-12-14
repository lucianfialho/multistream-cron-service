from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    type = Column(String)
    prize_pool = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    matches = relationship("Match", back_populates="event")
    player_stats = relationship("EventPlayerStat", back_populates="event")
    team_stats = relationship("EventTeamStat", back_populates="event")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    team1_name = Column(String)
    team1_logo = Column(String)
    team2_name = Column(String)
    team2_logo = Column(String)
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    date = Column(DateTime, index=True)
    map = Column(String)
    status = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    event = relationship("Event", back_populates="matches")

class EventPlayerStat(Base):
    __tablename__ = "event_player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    player_name = Column(String, nullable=False)
    team_name = Column(String)
    kills = Column(Integer)
    deaths = Column(Integer)
    rating = Column(Numeric(4, 2))
    hs_percent = Column(Numeric(5, 2))
    kd_ratio = Column(Numeric(4, 2))
    maps_played = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    event = relationship("Event", back_populates="player_stats")

class EventTeamStat(Base):
    __tablename__ = "event_team_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    team_name = Column(String, nullable=False)
    team_logo = Column(String)
    wins = Column(Integer)
    losses = Column(Integer)
    win_rate = Column(Numeric(5, 2))
    maps_played = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    event = relationship("Event", back_populates="team_stats")
