import os
import yaml
import logging

class ConfigManager:
    """Reads and manages configuration and environment variables, including loading architecture manual."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.config = {}
        self.architecture_manual_text = ""
        # Setup logger
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger("ConfigManager")
        self.load_config()

    def load_config(self):
        if self.config_path and self.config_path.endswith(('.yml', '.yaml')):
            try:
                self.logger.debug(f"Loading config file: {self.config_path}")
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.debug(f"Config keys loaded: {list(self.config.keys())}")
            except Exception as e:
                self.logger.error(f"Config file load error: {e}")
        else:
            self.logger.warning("No config_path provided or not a yaml file, skipping file load.")

        # Load .env overrides if present (project root)
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as env_file:
                    for raw_line in env_file:
                        line = raw_line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key:
                            # Ensure this process sees the override.
                            os.environ[key] = value
                self.logger.debug("Loaded .env overrides.")
            except Exception as e:
                self.logger.error(f"Error loading .env: {e}")

        # Load environment variables to override
        for key, value in os.environ.items():
            self.config[key] = value

        self.logger.debug(f"Config keys after environment override: {list(self.config.keys())}")

        # Load architecture manual if path provided in config
        manual_path = self.config.get('ARCHITECTURE_MANUAL_PATH')
        if manual_path:
            try:
                with open(manual_path, 'r', encoding='utf-8') as f:
                    self.architecture_manual_text = f.read()
                    # Optionally store the manual text in config as well
                    self.config['ARCHITECTURE_MANUAL_TEXT'] = self.architecture_manual_text
                self.logger.debug(f"Loaded architecture manual from {manual_path}")
            except Exception as e:
                self.logger.error(f"Error loading architecture manual from {manual_path}: {e}")

    def get(self, key, default=None):
        value = self.config.get(key, default)
        self.logger.debug(f"Config get: {key} = {value}")
        return value

    def get_architecture_manual(self):
        return self.architecture_manual_text
