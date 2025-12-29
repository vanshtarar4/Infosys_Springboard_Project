"""
Model Registry
Phase 5 of Continuous Learning System

Central registry for model management, versioning, and deployment.
"""

import joblib
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Central registry for fraud detection models.
    Handles loading, versioning, promotion, and rollback.
    """
    
    def __init__(self, registry_path: str = 'models'):
        self.registry_path = Path(registry_path)
        self.production_path = self.registry_path / 'production'
        self.candidates_path = self.registry_path / 'candidates'
        self.current_symlink = self.registry_path / 'current'
        
        # Ensure directories exist
        self.production_path.mkdir(parents=True, exist_ok=True)
        self.candidates_path.mkdir(parents=True, exist_ok=True)
    
    def load_production_model(self) -> Any:
        """
        Load current production model.
        
        Returns:
            Loaded model object
        """
        if not self.current_symlink.exists():
            logger.warning("No production model found, using fallback")
            # Load best_model.pkl as fallback
            fallback = self.registry_path / 'best_model.pkl'
            if fallback.exists():
                return joblib.load(fallback)
            raise FileNotFoundError("No model available")
        
        # Follow symlink to actual model
        model_dir = self.current_symlink.resolve() if self.current_symlink.is_symlink() else self.current_symlink
        model_file = model_dir / 'model.pkl'
        
        logger.info(f"Loading production model from {model_dir.name}")
        return joblib.load(model_file)
    
    def get_production_metadata(self) -> Dict:
        """Get metadata for current production model."""
        if not self.current_symlink.exists():
            return {}
        
        model_dir = self.current_symlink.resolve() if self.current_symlink.is_symlink() else self.current_symlink
        metadata_file = model_dir / 'metadata.json'
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        
        return {}
    
    def list_candidates(self) -> list:
        """List all candidate models."""
        if not self.candidates_path.exists():
            return []
        
        candidates = []
        for model_dir in self.candidates_path.iterdir():
            if model_dir.is_dir():
                metadata_file = model_dir / 'metadata.json'
                perf_file = model_dir / 'performance.json'
                
                info = {'name': model_dir.name}
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        info['metadata'] = json.load(f)
                
                if perf_file.exists():
                    with open(perf_file, 'r') as f:
                        info['performance'] = json.load(f)
                
                candidates.append(info)
        
        return candidates
    
    def promote_candidate(self, candidate_version: str) -> bool:
        """
        Promote candidate model to production.
        
        Args:
            candidate_version: Version name of candidate to promote
            
        Returns:
            True if successful
        """
        candidate_path = self.candidates_path / candidate_version
        
        if not candidate_path.exists():
            logger.error(f"Candidate {candidate_version} not found")
            return False
        
        logger.info(f"Promoting {candidate_version} to production...")
        
        # Backup current production if exists
        if self.current_symlink.exists():
            self._backup_production()
        
        # Move candidate to production
        production_path = self.production_path / candidate_version
        shutil.move(str(candidate_path), str(production_path))
        
        # Update 'current' symlink
        if self.current_symlink.exists():
            self.current_symlink.unlink()
        
        # Create new symlink
        try:
            self.current_symlink.symlink_to(production_path, target_is_directory=True)
        except OSError:
            # Windows may require different approach
            shutil.copy(str(production_path / 'model.pkl'), str(self.registry_path / 'best_model.pkl'))
        
        logger.info(f"✓ {candidate_version} promoted to production")
        
        # Log promotion
        self._log_deployment(candidate_version, 'promotion')
        
        return True
    
    def rollback(self, to_version: Optional[str] = None) -> bool:
        """
        Rollback to previous version.
        
        Args:
            to_version: Specific version to rollback to (or None for previous)
            
        Returns:
            True if successful
        """
        if to_version is None:
            # Get previous version from deployment log
            to_version = self._get_previous_version()
        
        if not to_version:
            logger.error("No previous version to rollback to")
            return False
        
        production_path = self.production_path / to_version
        
        if not production_path.exists():
            logger.error(f"Version {to_version} not found in production")
            return False
        
        logger.warning(f"Rolling back to {to_version}...")
        
        # Update symlink
        if self.current_symlink.exists():
            self.current_symlink.unlink()
        
        try:
            self.current_symlink.symlink_to(production_path, target_is_directory=True)
        except OSError:
            shutil.copy(str(production_path / 'model.pkl'), str(self.registry_path / 'best_model.pkl'))
        
        logger.warning(f"✓ Rolled back to {to_version}")
        
        # Log rollback
        self._log_deployment(to_version, 'rollback')
        
        return True
    
    def _backup_production(self):
        """Create backup of current production model."""
        if not self.current_symlink.exists():
            return
        
        current_dir = self.current_symlink.resolve() if self.current_symlink.is_symlink() else self.current_symlink
        backup_dir = self.registry_path / 'backups' / f"backup_{datetime.now():%Y%m%d_%H%M%S}"
        backup_dir.parent.mkdir(exist_ok=True)
        
        shutil.copytree(current_dir, backup_dir)
        logger.info(f"✓ Backed up current production to {backup_dir.name}")
    
    def _get_previous_version(self) -> Optional[str]:
        """Get previous production version from deployment log."""
        log_file = self.registry_path / 'deployment_log.json'
        
        if not log_file.exists():
            return None
        
        with open(log_file, 'r') as f:
            log = json.load(f)
        
        if len(log) < 2:
            return None
        
        # Return second-to-last entry
        return log[-2]['version']
    
    def _log_deployment(self, version: str, action: str):
        """Log deployment action."""
        log_file = self.registry_path / 'deployment_log.json'
        
        entry = {
            'version': version,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                log = json.load(f)
        else:
            log = []
        
        log.append(entry)
        
        with open(log_file, 'w') as f:
            json.dump(log, f, indent=2)
