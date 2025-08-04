"""
OCIO Performance Analysis Configuration Module

Handles configuration settings, defaults, and validation
for the OCIO performance analysis toolkit.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Union

from .exceptions import ConfigurationError
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ChartConfig:
    """Configuration for chart generation."""
    
    # Chart styling
    figure_size: tuple = (12, 8)
    dpi: int = 300
    style: str = 'default'
    color_palette: str = 'husl'
    
    # Font settings
    font_size: int = 10
    title_font_size: int = 14
    label_font_size: int = 12
    
    # Output settings
    format: str = 'png'
    bbox_inches: str = 'tight'
    transparent: bool = False


@dataclass 
class AnalysisConfig:
    """Configuration for data analysis."""
    
    # Outlier detection
    outlier_threshold: float = 2.0
    outlier_method: str = 'zscore'  # 'zscore' or 'iqr'
    
    # Performance thresholds
    max_reasonable_time_ms: float = 100000.0
    min_reasonable_time_ms: float = 0.1
    
    # Data validation
    max_missing_data_pct: float = 10.0
    required_columns: List[str] = None
    
    # Statistical settings
    confidence_level: float = 0.95
    percentiles: List[float] = None
    
    def __post_init__(self):
        if self.required_columns is None:
            self.required_columns = ['avg_time', 'min_time', 'max_time', 'file_name', 'cpu_model']
        if self.percentiles is None:
            self.percentiles = [5, 10, 25, 50, 75, 90, 95, 99]


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_logging: bool = True
    console_logging: bool = True
    log_file: str = 'ocio_analysis.log'
    max_file_size_mb: int = 10
    backup_count: int = 3


@dataclass
class OCIOConfig:
    """Main configuration class combining all settings."""
    
    chart: ChartConfig = None
    analysis: AnalysisConfig = None
    logging: LoggingConfig = None
    
    # File paths
    default_data_dir: str = 'data'
    default_output_dir: str = 'analysis_results'
    
    # Processing settings
    enable_caching: bool = True
    parallel_processing: bool = False
    max_workers: int = 4
    
    def __post_init__(self):
        if self.chart is None:
            self.chart = ChartConfig()
        if self.analysis is None:
            self.analysis = AnalysisConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigurationManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or Path.cwd() / 'ocio_config.json'
        self._config = None
    
    def load_config(self) -> OCIOConfig:
        """
        Load configuration from file or create default.
        
        Returns:
            Configuration object
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            if self.config_file.exists():
                logger.info(f"Loading configuration from {self.config_file}")
                with open(self.config_file, 'r') as f:
                    config_dict = json.load(f)
                    
                # Convert dict to config objects
                self._config = self._dict_to_config(config_dict)
                logger.info("Configuration loaded successfully")
            else:
                logger.info("No configuration file found, using defaults")
                self._config = OCIOConfig()
                
            return self._config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, config: Optional[OCIOConfig] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current if None)
            
        Raises:
            ConfigurationError: If configuration saving fails
        """
        try:
            config_to_save = config or self._config
            if not config_to_save:
                raise ConfigurationError("No configuration to save")
                
            # Convert config to dict
            config_dict = self._config_to_dict(config_to_save)
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
                
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def get_config(self) -> OCIOConfig:
        """
        Get current configuration, loading if necessary.
        
        Returns:
            Current configuration
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration values.
        
        Args:
            **kwargs: Configuration values to update
        """
        if self._config is None:
            self._config = self.load_config()
            
        # Update configuration attributes
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def _dict_to_config(self, config_dict: Dict) -> OCIOConfig:
        """Convert dictionary to configuration object."""
        # Create sub-configs
        chart_config = ChartConfig(**config_dict.get('chart', {}))
        analysis_config = AnalysisConfig(**config_dict.get('analysis', {}))
        logging_config = LoggingConfig(**config_dict.get('logging', {}))
        
        # Create main config
        main_config_dict = {k: v for k, v in config_dict.items() 
                           if k not in ['chart', 'analysis', 'logging']}
        
        return OCIOConfig(
            chart=chart_config,
            analysis=analysis_config,
            logging=logging_config,
            **main_config_dict
        )
    
    def _config_to_dict(self, config: OCIOConfig) -> Dict:
        """Convert configuration object to dictionary."""
        return {
            'chart': asdict(config.chart),
            'analysis': asdict(config.analysis),
            'logging': asdict(config.logging),
            'default_data_dir': config.default_data_dir,
            'default_output_dir': config.default_output_dir,
            'enable_caching': config.enable_caching,
            'parallel_processing': config.parallel_processing,
            'max_workers': config.max_workers
        }
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = OCIOConfig()
        logger.info("Configuration reset to defaults")
    
    def validate_config(self, config: Optional[OCIOConfig] = None) -> List[str]:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration to validate (uses current if None)
            
        Returns:
            List of validation errors (empty if valid)
        """
        config_to_validate = config or self._config
        if not config_to_validate:
            return ["No configuration to validate"]
            
        errors = []
        
        # Validate chart config
        if config_to_validate.chart.dpi < 50 or config_to_validate.chart.dpi > 600:
            errors.append("Chart DPI should be between 50 and 600")
            
        # Validate analysis config  
        if config_to_validate.analysis.outlier_threshold <= 0:
            errors.append("Outlier threshold must be positive")
            
        if config_to_validate.analysis.max_reasonable_time_ms <= config_to_validate.analysis.min_reasonable_time_ms:
            errors.append("Max reasonable time must be greater than min reasonable time")
            
        # Validate logging config
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config_to_validate.logging.level not in valid_levels:
            errors.append(f"Logging level must be one of: {valid_levels}")
            
        return errors


# Global configuration manager instance
_config_manager = None

def get_config_manager(config_file: Optional[Path] = None) -> ConfigurationManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_file: Optional configuration file path
        
    Returns:
        Configuration manager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_file)
    return _config_manager


def get_config() -> OCIOConfig:
    """
    Get the current configuration.
    
    Returns:
        Current configuration object
    """
    return get_config_manager().get_config()
