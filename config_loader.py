"""
config_loader.py — Loads YAML event profiles and merges them with global defaults.
"""
import yaml
import os
import logging

logger = logging.getLogger(__name__)

class EventConfig:
    def __init__(self, config_path=None):
        # Default Values (The fallback)
        self.event_name = "SNITC Event"
        self.event_date = "TBD"
        self.event_type = "Nightlife / Cultural"
        self.capacity_min = 150
        self.capacity_max = 400
        self.capacity_ideal_min = 200
        self.capacity_ideal_max = 300
        self.priority_neighborhoods = []
        self.search_queries = []
        self.sponsor_search_queries = []
        self.target_vibe = []

        if config_path and os.path.exists(config_path):
            self.load_from_yaml(config_path)

    def load_from_yaml(self, path):
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
                # Manual map to avoid nested dict issues
                e = data.get('event', {})
                self.event_name = e.get('name', self.event_name)
                self.event_date = e.get('date', self.event_date)
                self.event_type = e.get('type', self.event_type)
                
                c = data.get('capacity', {})
                self.capacity_min = c.get('min', self.capacity_min)
                self.capacity_max = c.get('max', self.capacity_max)
                self.capacity_ideal_min = c.get('ideal_min', self.capacity_ideal_min)
                self.capacity_ideal_max = c.get('ideal_max', self.capacity_ideal_max)
                
                self.priority_neighborhoods = data.get('priority_neighborhoods', [])
                self.search_queries = data.get('search_queries', [])
                self.sponsor_search_queries = data.get('sponsor_search_queries', [])
                self.target_vibe = data.get('target_vibe', [])
                
                logger.info(f"Successfully loaded event profile: {path}")
        except Exception as e:
            logger.error(f"Failed to load config at {path}: {e}")

# Global instance for easy access if needed (singleton-ish)
_current_config = None

def get_config(path=None):
    global _current_config
    if path or _current_config is None:
        _current_config = EventConfig(path)
    return _current_config
