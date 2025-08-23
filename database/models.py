"""
Database models for VGC Team Analysis application
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Table,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Association table for many-to-many relationship between teams and tags
team_tags = Table(
    "team_tags",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class Team(Base):
    """Team model for storing analyzed teams"""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    regulation = Column(String(10))  # e.g., "A", "B", "C"
    format = Column(String(50))  # e.g., "VGC2024", "VGC2025"
    archetype = Column(String(100))  # e.g., "Trick Room", "Rain", "Hyper Offense"
    article_url = Column(String(500))
    article_title = Column(String(500))
    author = Column(String(255))
    tournament_context = Column(String(500))
    tournament_result = Column(String(100))
    strategy_summary = Column(Text)
    strengths = Column(JSON)  # List of strengths
    weaknesses = Column(JSON)  # List of weaknesses
    meta_relevance = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rating = Column(Float, default=0.0)  # User rating 0-5
    notes = Column(Text)  # User notes
    is_bookmarked = Column(Boolean, default=False)

    # Relationships
    pokemon = relationship(
        "Pokemon", back_populates="team", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=team_tags, back_populates="teams")


class Pokemon(Base):
    """Pokemon model for individual team members"""

    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Basic Pokemon data
    name = Column(String(100), nullable=False)
    species = Column(String(100))  # Base species name
    form = Column(String(100))  # Form variation if any
    ability = Column(String(100))
    held_item = Column(String(100))
    nature = Column(String(20))
    tera_type = Column(String(20))

    # Moves (stored as JSON array)
    moves = Column(JSON)  # List of 4 moves

    # EV spread data
    hp_ev = Column(Integer, default=0)
    atk_ev = Column(Integer, default=0)
    def_ev = Column(Integer, default=0)
    spa_ev = Column(Integer, default=0)
    spd_ev = Column(Integer, default=0)
    spe_ev = Column(Integer, default=0)
    ev_source = Column(String(50))  # 'article', 'default_missing', etc.

    # Role and explanation
    role = Column(String(100))
    ev_explanation = Column(Text)

    # Calculated stats at level 50
    hp_stat = Column(Integer)
    atk_stat = Column(Integer)
    def_stat = Column(Integer)
    spa_stat = Column(Integer)
    spd_stat = Column(Integer)
    spe_stat = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="pokemon")


class Tag(Base):
    """Tag model for categorizing teams"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))  # 'regulation', 'archetype', 'author', 'custom'
    color = Column(String(7))  # Hex color code
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teams = relationship("Team", secondary=team_tags, back_populates="tags")


class Bookmark(Base):
    """Bookmark model for saved articles"""

    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True)
    article_url = Column(String(500), nullable=False)
    title = Column(String(500))
    author = Column(String(255))
    summary = Column(Text)
    content_preview = Column(Text)
    category = Column(String(100))  # e.g., "Tournament Report", "Team Building"
    rating = Column(Float, default=0.0)
    notes = Column(Text)
    is_favorite = Column(Boolean, default=False)
    read_status = Column(String(20), default="unread")  # 'unread', 'reading', 'read'
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Analysis data if available
    pokemon_count = Column(Integer, default=0)
    regulation = Column(String(10))
    tournament_context = Column(String(500))


class SpeedTier(Base):
    """Speed tier data for common VGC Pokemon"""

    __tablename__ = "speed_tiers"

    id = Column(Integer, primary_key=True)
    pokemon_name = Column(String(100), nullable=False)
    base_speed = Column(Integer, nullable=False)
    common_speed_positive = Column(Integer)  # Speed with positive nature + EVs
    common_speed_neutral = Column(Integer)  # Speed with neutral nature + EVs
    common_speed_negative = Column(Integer)  # Speed with negative nature + EVs
    regulation = Column(String(10))
    usage_tier = Column(String(20))  # 'S', 'A', 'B', 'C', 'D'
    created_at = Column(DateTime, default=datetime.utcnow)


class DamageCalculation(Base):
    """Stored damage calculations for reference"""

    __tablename__ = "damage_calculations"

    id = Column(Integer, primary_key=True)
    attacker_name = Column(String(100), nullable=False)
    defender_name = Column(String(100), nullable=False)
    move_name = Column(String(100), nullable=False)

    # Attacker stats
    attacker_attack_stat = Column(Integer)
    attacker_level = Column(Integer, default=50)

    # Defender stats
    defender_defense_stat = Column(Integer)
    defender_hp_stat = Column(Integer)

    # Calculation modifiers
    is_critical = Column(Boolean, default=False)
    weather_modifier = Column(Float, default=1.0)
    terrain_modifier = Column(Float, default=1.0)
    ability_modifier = Column(Float, default=1.0)
    item_modifier = Column(Float, default=1.0)

    # Results
    min_damage = Column(Integer)
    max_damage = Column(Integer)
    min_percentage = Column(Float)
    max_percentage = Column(Float)
    ko_chance = Column(Float)  # 0.0 to 1.0

    created_at = Column(DateTime, default=datetime.utcnow)


# Database engine and session setup
def get_database_url():
    """Get database URL, defaulting to SQLite"""
    db_path = os.path.join(os.path.dirname(__file__), "..", "vgc_analyzer.db")
    return f"sqlite:///{db_path}"


def create_engine_and_session():
    """Create database engine and session"""
    engine = create_engine(get_database_url(), echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def init_database():
    """Initialize database tables"""
    engine, _ = create_engine_and_session()
    Base.metadata.create_all(bind=engine)
    return engine


def get_session():
    """Get database session"""
    _, SessionLocal = create_engine_and_session()
    return SessionLocal()
