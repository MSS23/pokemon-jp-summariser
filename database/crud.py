"""
CRUD operations for VGC Team Analysis application
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta

from .models import Team, Pokemon, Tag, Bookmark, SpeedTier, DamageCalculation, get_session


class TeamCRUD:
    """CRUD operations for teams"""
    
    @staticmethod
    def create_team_from_analysis(analysis_result: Dict[str, Any], article_url: str = "") -> Team:
        """Create a team from analysis result"""
        session = get_session()
        try:
            # Create team
            team = Team(
                name=analysis_result.get('title', 'Untitled Team'),
                regulation=analysis_result.get('regulation', ''),
                article_url=article_url,
                article_title=analysis_result.get('title', ''),
                tournament_context=analysis_result.get('tournament_context', ''),
                strategy_summary=analysis_result.get('overall_strategy', ''),
                strengths=analysis_result.get('strengths', []),
                weaknesses=analysis_result.get('weaknesses', []),
                meta_relevance=analysis_result.get('meta_relevance', ''),
                is_bookmarked=True  # Auto-bookmark analyzed teams
            )
            
            session.add(team)
            session.flush()  # Get the team ID
            
            # Create Pokemon
            pokemon_team = analysis_result.get('pokemon_team', [])
            for poke_data in pokemon_team:
                # Parse EV spread
                ev_spread = poke_data.get('ev_spread', '0/0/0/0/0/0')
                evs = [0, 0, 0, 0, 0, 0]  # Default
                
                if '/' in ev_spread:
                    try:
                        evs = [int(x.strip()) for x in ev_spread.split('/')][:6]
                        evs += [0] * (6 - len(evs))  # Pad if needed
                    except:
                        pass
                
                pokemon = Pokemon(
                    team_id=team.id,
                    name=poke_data.get('name', ''),
                    ability=poke_data.get('ability', ''),
                    held_item=poke_data.get('held_item', ''),
                    nature=poke_data.get('nature', ''),
                    tera_type=poke_data.get('tera_type', ''),
                    moves=poke_data.get('moves', []),
                    hp_ev=evs[0],
                    atk_ev=evs[1],
                    def_ev=evs[2],
                    spa_ev=evs[3],
                    spd_ev=evs[4],
                    spe_ev=evs[5],
                    ev_source=poke_data.get('ev_source', 'article'),
                    role=poke_data.get('role', ''),
                    ev_explanation=poke_data.get('ev_explanation', '')
                )
                session.add(pokemon)
            
            session.commit()
            return team
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_all_teams(limit: int = 100, offset: int = 0) -> List[Team]:
        """Get all teams with pagination"""
        session = get_session()
        try:
            teams = session.query(Team).order_by(desc(Team.created_at)).limit(limit).offset(offset).all()
            return teams
        finally:
            session.close()
    
    @staticmethod
    def get_team_by_id(team_id: int) -> Optional[Team]:
        """Get team by ID"""
        session = get_session()
        try:
            return session.query(Team).filter(Team.id == team_id).first()
        finally:
            session.close()
    
    @staticmethod
    def search_teams(
        query: str = "",
        regulation: str = "",
        archetype: str = "",
        pokemon_name: str = "",
        limit: int = 100
    ) -> List[Team]:
        """Search teams with filters"""
        session = get_session()
        try:
            q = session.query(Team)
            
            if query:
                q = q.filter(or_(
                    Team.name.ilike(f'%{query}%'),
                    Team.article_title.ilike(f'%{query}%'),
                    Team.author.ilike(f'%{query}%'),
                    Team.strategy_summary.ilike(f'%{query}%')
                ))
            
            if regulation:
                q = q.filter(Team.regulation == regulation)
                
            if archetype:
                q = q.filter(Team.archetype.ilike(f'%{archetype}%'))
                
            if pokemon_name:
                q = q.join(Pokemon).filter(Pokemon.name.ilike(f'%{pokemon_name}%'))
            
            return q.order_by(desc(Team.created_at)).limit(limit).all()
            
        finally:
            session.close()
    
    @staticmethod
    def get_team_statistics() -> Dict[str, Any]:
        """Get team database statistics"""
        session = get_session()
        try:
            total_teams = session.query(Team).count()
            total_pokemon = session.query(Pokemon).count()
            
            # Most common regulations
            regulations = session.query(Team.regulation, func.count(Team.regulation))\
                .group_by(Team.regulation)\
                .order_by(desc(func.count(Team.regulation)))\
                .limit(5).all()
            
            # Most popular Pokemon
            popular_pokemon = session.query(Pokemon.name, func.count(Pokemon.name))\
                .group_by(Pokemon.name)\
                .order_by(desc(func.count(Pokemon.name)))\
                .limit(10).all()
            
            return {
                'total_teams': total_teams,
                'total_pokemon': total_pokemon,
                'regulations': dict(regulations),
                'popular_pokemon': dict(popular_pokemon)
            }
            
        finally:
            session.close()
    
    @staticmethod
    def delete_team(team_id: int) -> bool:
        """Delete a team"""
        session = get_session()
        try:
            team = session.query(Team).filter(Team.id == team_id).first()
            if team:
                session.delete(team)
                session.commit()
                return True
            return False
        except:
            session.rollback()
            return False
        finally:
            session.close()


class BookmarkCRUD:
    """CRUD operations for bookmarks"""
    
    @staticmethod
    def create_bookmark(
        article_url: str,
        title: str = "",
        summary: str = "",
        category: str = "General"
    ) -> Bookmark:
        """Create a bookmark"""
        session = get_session()
        try:
            # Check if bookmark already exists
            existing = session.query(Bookmark).filter(Bookmark.article_url == article_url).first()
            if existing:
                return existing
            
            bookmark = Bookmark(
                article_url=article_url,
                title=title,
                summary=summary,
                category=category
            )
            session.add(bookmark)
            session.commit()
            return bookmark
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_all_bookmarks(limit: int = 100) -> List[Bookmark]:
        """Get all bookmarks"""
        session = get_session()
        try:
            return session.query(Bookmark).order_by(desc(Bookmark.created_at)).limit(limit).all()
        finally:
            session.close()
    
    @staticmethod
    def update_bookmark_rating(bookmark_id: int, rating: float, notes: str = "") -> bool:
        """Update bookmark rating and notes"""
        session = get_session()
        try:
            bookmark = session.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
            if bookmark:
                bookmark.rating = rating
                bookmark.notes = notes
                session.commit()
                return True
            return False
        except:
            session.rollback()
            return False
        finally:
            session.close()


class SpeedTierCRUD:
    """CRUD operations for speed tiers"""
    
    @staticmethod
    def get_speed_tiers(regulation: str = "") -> List[SpeedTier]:
        """Get speed tier data"""
        session = get_session()
        try:
            q = session.query(SpeedTier)
            if regulation:
                q = q.filter(SpeedTier.regulation == regulation)
            return q.order_by(desc(SpeedTier.common_speed_positive)).all()
        finally:
            session.close()
    
    @staticmethod
    def create_speed_tier(pokemon_name: str, base_speed: int, **kwargs) -> SpeedTier:
        """Create speed tier entry"""
        session = get_session()
        try:
            speed_tier = SpeedTier(
                pokemon_name=pokemon_name,
                base_speed=base_speed,
                **kwargs
            )
            session.add(speed_tier)
            session.commit()
            return speed_tier
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class DamageCalculationCRUD:
    """CRUD operations for damage calculations"""
    
    @staticmethod
    def create_calculation(
        attacker: str,
        defender: str,
        move: str,
        attacker_stat: int,
        defender_stat: int,
        defender_hp: int,
        damage_range: tuple,
        **modifiers
    ) -> DamageCalculation:
        """Create damage calculation"""
        session = get_session()
        try:
            calc = DamageCalculation(
                attacker_name=attacker,
                defender_name=defender,
                move_name=move,
                attacker_attack_stat=attacker_stat,
                defender_defense_stat=defender_stat,
                defender_hp_stat=defender_hp,
                min_damage=damage_range[0],
                max_damage=damage_range[1],
                min_percentage=damage_range[0] / defender_hp * 100,
                max_percentage=damage_range[1] / defender_hp * 100,
                **modifiers
            )
            session.add(calc)
            session.commit()
            return calc
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_calculations_for_pokemon(pokemon_name: str, as_attacker: bool = True) -> List[DamageCalculation]:
        """Get damage calculations involving a Pokemon"""
        session = get_session()
        try:
            if as_attacker:
                return session.query(DamageCalculation)\
                    .filter(DamageCalculation.attacker_name == pokemon_name)\
                    .order_by(desc(DamageCalculation.created_at)).all()
            else:
                return session.query(DamageCalculation)\
                    .filter(DamageCalculation.defender_name == pokemon_name)\
                    .order_by(desc(DamageCalculation.created_at)).all()
        finally:
            session.close()


# Utility functions
def initialize_database():
    """Initialize database with sample data"""
    from .models import init_database
    
    # Create tables
    init_database()
    
    # Add sample speed tiers for common VGC Pokemon
    sample_speed_tiers = [
        ("Dragapult", 142, 216, 196, 176, "A"),
        ("Miraidon", 135, 209, 189, 169, "S"),
        ("Koraidon", 135, 209, 189, 169, "S"),
        ("Flutter Mane", 135, 209, 189, 169, "S"),
        ("Iron Valiant", 116, 184, 167, 150, "S"),
        ("Chien-Pao", 135, 209, 189, 169, "A"),
        ("Raging Bolt", 75, 139, 127, 115, "A"),
        ("Urshifu-Rapid", 97, 161, 146, 131, "A"),
        ("Landorus-T", 91, 155, 141, 127, "S"),
        ("Incineroar", 60, 124, 112, 101, "S"),
    ]
    
    session = get_session()
    try:
        for name, base, pos, neu, neg, tier in sample_speed_tiers:
            existing = session.query(SpeedTier).filter(SpeedTier.pokemon_name == name).first()
            if not existing:
                speed_tier = SpeedTier(
                    pokemon_name=name,
                    base_speed=base,
                    common_speed_positive=pos,
                    common_speed_neutral=neu,
                    common_speed_negative=neg,
                    usage_tier=tier,
                    regulation="A"
                )
                session.add(speed_tier)
        
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()