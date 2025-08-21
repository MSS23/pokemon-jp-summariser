"""
Analytics system for Pokémon VGC Summariser
Tracks user behavior, trending teams, and search patterns
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import streamlit as st

ANALYTICS_PATH = "storage/analytics.json"


class AnalyticsManager:
    def __init__(self):
        self.ensure_storage_directory()

    def ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(ANALYTICS_PATH), exist_ok=True)

    def load_analytics(self) -> Dict:
        """Load analytics data from file"""
        try:
            if os.path.exists(ANALYTICS_PATH):
                with open(ANALYTICS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            return self.get_default_analytics()
        except (json.JSONDecodeError, FileNotFoundError):
            return self.get_default_analytics()

    def get_default_analytics(self) -> Dict:
        """Get default analytics structure"""
        return {
            "searches": [],  # List of search events
            "team_views": [],  # List of team view events
            "pokemon_searches": [],  # List of pokemon search events
            "article_summaries": [],  # List of article summary events
            "user_sessions": [],  # List of user session events
            "daily_stats": {},  # Daily aggregated statistics
            "trending_data": {
                "teams": {},  # Team popularity over time
                "pokemon": {},  # Pokemon popularity over time
                "articles": {},  # Article popularity over time
            },
        }

    def save_analytics(self, analytics: Dict) -> bool:
        """Save analytics data to file"""
        try:
            with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
                json.dump(analytics, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def track_search(
        self, username: str, search_term: str, search_type: str, results_count: int
    ):
        """Track a search event"""
        analytics = self.load_analytics()

        search_event = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "search_term": search_term.lower(),
            "search_type": search_type,
            "results_count": results_count,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        analytics["searches"].append(search_event)

        # Track pokemon searches separately
        if search_type in ["Pokémon Only", "All Fields"] and search_term:
            pokemon_event = {
                "timestamp": datetime.now().isoformat(),
                "username": username,
                "pokemon": search_term.lower(),
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            analytics["pokemon_searches"].append(pokemon_event)

        # Update trending data
        self.update_trending_pokemon(analytics, search_term.lower())

        # Keep only last 10000 search events to prevent file from growing too large
        if len(analytics["searches"]) > 10000:
            analytics["searches"] = analytics["searches"][-10000:]

        if len(analytics["pokemon_searches"]) > 10000:
            analytics["pokemon_searches"] = analytics["pokemon_searches"][-10000:]

        self.save_analytics(analytics)

    def track_team_view(
        self, username: str, team_pokemon: List[str], article_title: str
    ):
        """Track when a user views a team"""
        analytics = self.load_analytics()

        team_event = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "team_pokemon": [p.lower() for p in team_pokemon],
            "article_title": article_title,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        analytics["team_views"].append(team_event)

        # Update trending teams
        team_key = ",".join(sorted([p.lower() for p in team_pokemon]))
        self.update_trending_team(analytics, team_key, team_pokemon, article_title)

        # Keep only last 5000 team view events
        if len(analytics["team_views"]) > 5000:
            analytics["team_views"] = analytics["team_views"][-5000:]

        self.save_analytics(analytics)

    def track_article_summary(
        self, username: str, article_url: str, pokemon_found: List[str]
    ):
        """Track when a user summarizes an article"""
        analytics = self.load_analytics()

        summary_event = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "article_url": article_url,
            "pokemon_found": [p.lower() for p in pokemon_found],
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        analytics["article_summaries"].append(summary_event)

        # Update trending articles
        self.update_trending_article(analytics, article_url)

        # Keep only last 5000 summary events
        if len(analytics["article_summaries"]) > 5000:
            analytics["article_summaries"] = analytics["article_summaries"][-5000:]

        self.save_analytics(analytics)

    def track_user_session(self, username: str, action: str):
        """Track user session events (login, logout, etc.)"""
        analytics = self.load_analytics()

        session_event = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "action": action,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        analytics["user_sessions"].append(session_event)

        # Keep only last 5000 session events
        if len(analytics["user_sessions"]) > 5000:
            analytics["user_sessions"] = analytics["user_sessions"][-5000:]

        self.save_analytics(analytics)

    def update_trending_pokemon(self, analytics: Dict, pokemon: str):
        """Update trending Pokemon data"""
        today = datetime.now().strftime("%Y-%m-%d")

        if pokemon not in analytics["trending_data"]["pokemon"]:
            analytics["trending_data"]["pokemon"][pokemon] = {}

        if today not in analytics["trending_data"]["pokemon"][pokemon]:
            analytics["trending_data"]["pokemon"][pokemon][today] = 0

        analytics["trending_data"]["pokemon"][pokemon][today] += 1

    def update_trending_team(
        self,
        analytics: Dict,
        team_key: str,
        team_pokemon: List[str],
        article_title: str,
    ):
        """Update trending team data"""
        today = datetime.now().strftime("%Y-%m-%d")

        if team_key not in analytics["trending_data"]["teams"]:
            analytics["trending_data"]["teams"][team_key] = {
                "pokemon": team_pokemon,
                "article_title": article_title,
                "views": {},
            }

        if today not in analytics["trending_data"]["teams"][team_key]["views"]:
            analytics["trending_data"]["teams"][team_key]["views"][today] = 0

        analytics["trending_data"]["teams"][team_key]["views"][today] += 1

    def update_trending_article(self, analytics: Dict, article_url: str):
        """Update trending article data"""
        today = datetime.now().strftime("%Y-%m-%d")

        if article_url not in analytics["trending_data"]["articles"]:
            analytics["trending_data"]["articles"][article_url] = {}

        if today not in analytics["trending_data"]["articles"][article_url]:
            analytics["trending_data"]["articles"][article_url][today] = 0

        analytics["trending_data"]["articles"][article_url][today] += 1

    def get_trending_pokemon(
        self, days: int = 7, limit: int = 10
    ) -> List[Tuple[str, int]]:
        """Get trending Pokemon over the last N days"""
        analytics = self.load_analytics()
        cutoff_date = datetime.now() - timedelta(days=days)

        pokemon_counts = Counter()

        for search in analytics["pokemon_searches"]:
            try:
                search_date = datetime.fromisoformat(search["timestamp"])
                if search_date >= cutoff_date:
                    pokemon_counts[search["pokemon"]] += 1
            except (ValueError, KeyError):
                continue

        return pokemon_counts.most_common(limit)

    def get_trending_teams(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get trending teams over the last N days"""
        analytics = self.load_analytics()
        cutoff_date = datetime.now() - timedelta(days=days)

        team_scores = {}

        for team_key, team_data in analytics["trending_data"]["teams"].items():
            total_views = 0
            for date_str, views in team_data["views"].items():
                try:
                    view_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if view_date >= cutoff_date:
                        total_views += views
                except ValueError:
                    continue

            if total_views > 0:
                team_scores[team_key] = {
                    "pokemon": team_data["pokemon"],
                    "article_title": team_data["article_title"],
                    "views": total_views,
                }

        # Sort by views and return top teams
        sorted_teams = sorted(
            team_scores.items(), key=lambda x: x[1]["views"], reverse=True
        )
        return [team_data for _, team_data in sorted_teams[:limit]]

    def get_most_searched_pokemon(
        self, days: int = 30, limit: int = 15
    ) -> List[Tuple[str, int]]:
        """Get most searched Pokemon over the last N days"""
        return self.get_trending_pokemon(days, limit)

    def get_most_viewed_teams(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get most viewed teams over the last N days"""
        return self.get_trending_teams(days, limit)

    def get_search_statistics(self, username: str = None) -> Dict:
        """Get search statistics for a user or globally"""
        analytics = self.load_analytics()

        searches = analytics["searches"]
        if username:
            searches = [s for s in searches if s.get("username") == username]

        if not searches:
            return {
                "total_searches": 0,
                "unique_terms": 0,
                "avg_results": 0,
                "most_common_terms": [],
            }

        search_terms = [s["search_term"] for s in searches]
        results_counts = [s.get("results_count", 0) for s in searches]

        return {
            "total_searches": len(searches),
            "unique_terms": len(set(search_terms)),
            "avg_results": (
                round(sum(results_counts) / len(results_counts), 1)
                if results_counts
                else 0
            ),
            "most_common_terms": Counter(search_terms).most_common(10),
        }

    def get_daily_activity(self, days: int = 30) -> Dict:
        """Get daily activity statistics"""
        analytics = self.load_analytics()
        cutoff_date = datetime.now() - timedelta(days=days)

        daily_stats = defaultdict(
            lambda: {
                "searches": 0,
                "team_views": 0,
                "summaries": 0,
                "unique_users": set(),
            }
        )

        # Process searches
        for search in analytics["searches"]:
            try:
                search_date = datetime.fromisoformat(search["timestamp"])
                if search_date >= cutoff_date:
                    date_key = search_date.strftime("%Y-%m-%d")
                    daily_stats[date_key]["searches"] += 1
                    daily_stats[date_key]["unique_users"].add(
                        search.get("username", "anonymous")
                    )
            except (ValueError, KeyError):
                continue

        # Process team views
        for view in analytics["team_views"]:
            try:
                view_date = datetime.fromisoformat(view["timestamp"])
                if view_date >= cutoff_date:
                    date_key = view_date.strftime("%Y-%m-%d")
                    daily_stats[date_key]["team_views"] += 1
                    daily_stats[date_key]["unique_users"].add(
                        view.get("username", "anonymous")
                    )
            except (ValueError, KeyError):
                continue

        # Process summaries
        for summary in analytics["article_summaries"]:
            try:
                summary_date = datetime.fromisoformat(summary["timestamp"])
                if summary_date >= cutoff_date:
                    date_key = summary_date.strftime("%Y-%m-%d")
                    daily_stats[date_key]["summaries"] += 1
                    daily_stats[date_key]["unique_users"].add(
                        summary.get("username", "anonymous")
                    )
            except (ValueError, KeyError):
                continue

        # Convert sets to counts
        result = {}
        for date_key, stats in daily_stats.items():
            result[date_key] = {
                "searches": stats["searches"],
                "team_views": stats["team_views"],
                "summaries": stats["summaries"],
                "unique_users": len(stats["unique_users"]),
            }

        return result

    def get_user_activity_summary(self, username: str) -> Dict:
        """Get activity summary for a specific user"""
        analytics = self.load_analytics()

        user_searches = [
            s for s in analytics["searches"] if s.get("username") == username
        ]
        user_views = [
            v for v in analytics["team_views"] if v.get("username") == username
        ]
        user_summaries = [
            s for s in analytics["article_summaries"] if s.get("username") == username
        ]

        return {
            "total_searches": len(user_searches),
            "total_team_views": len(user_views),
            "total_summaries": len(user_summaries),
            "favorite_pokemon": self.get_user_favorite_pokemon(username),
            "recent_activity": self.get_user_recent_activity(username),
        }

    def get_user_favorite_pokemon(
        self, username: str, limit: int = 5
    ) -> List[Tuple[str, int]]:
        """Get user's most searched Pokemon"""
        analytics = self.load_analytics()

        user_pokemon_searches = [
            s["pokemon"]
            for s in analytics["pokemon_searches"]
            if s.get("username") == username
        ]

        return Counter(user_pokemon_searches).most_common(limit)

    def get_user_recent_activity(self, username: str, limit: int = 10) -> List[Dict]:
        """Get user's recent activity"""
        analytics = self.load_analytics()

        all_activities = []

        # Add searches
        for search in analytics["searches"]:
            if search.get("username") == username:
                all_activities.append(
                    {
                        "type": "search",
                        "timestamp": search["timestamp"],
                        "details": f"Searched for '{search['search_term']}'",
                    }
                )

        # Add team views
        for view in analytics["team_views"]:
            if view.get("username") == username:
                all_activities.append(
                    {
                        "type": "team_view",
                        "timestamp": view["timestamp"],
                        "details": f"Viewed team: {', '.join(view['team_pokemon'][:3])}{'...' if len(view['team_pokemon']) > 3 else ''}",
                    }
                )

        # Add summaries
        for summary in analytics["article_summaries"]:
            if summary.get("username") == username:
                all_activities.append(
                    {
                        "type": "summary",
                        "timestamp": summary["timestamp"],
                        "details": f"Summarized article with {len(summary['pokemon_found'])} Pokémon",
                    }
                )

        # Sort by timestamp and return recent activities
        all_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_activities[:limit]


# Global analytics manager instance
analytics_manager = AnalyticsManager()
