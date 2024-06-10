import shutil
import yaml
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.base_dir = '/home/test'
        self.base_path = Path.cwd() / self.base_dir
        self.config_path = self.base_path / 'config'
        self.subfolder_paths = []

    def create_directory_structure(self):
        # create config folder inside the test_path
        self.config_path.mkdir(parents=True, exist_ok=True)

        # create subfolders for sbts inside config
        subfolders = ['SK1', 'SK2', 'SK3']
        self.subfolder_paths = [self.config_path / subfolder for subfolder in subfolders]
        for subfolder_path in self.subfolder_paths:
            subfolder_path.mkdir(parents=True, exist_ok=True)
        print(f"Directory structure created at {self.config_path}")

    def load_config(self, source_path):
        # Define the path to the source folder and config.yaml file
        self.source_path = Path(source_path)
        yaml_file_path = self.source_path / 'config.yaml'

        # check if config.yaml exists in the source path
        if not yaml_file_path.exists():
            raise FileNotFoundError(f"{yaml_file_path} does not exist")

        # Load the Yaml file
        with yaml_file_path.open('r') as yaml_file:
            self.config_data = yaml.safe_load(yaml_file)

    def validate_default(self):
        # check for default True or true in the yaml
        self.default_match = None
        for match in self.config_data.get('variants', []):
            if match.get('default') in [True, "true"]:
                self.default_match = match
                break
            if self.default_match is None:
                raise ValueError("No 'default: true' or 'default: True' found in the config file.")

    def copy_files(self):
        # Ensure validate_default() has been called and found a default match
        if not self.default_match:
            raise RuntimeError("validate_default() must be called before copy_files()")

        for node in self.default_match.get('nodes', []):
            for file in node.get('files', []):
                file_type = file.get('file_type')
                file_path = file.get('file_path')
                if file_type and file_path:
                    full_file_path = self.source_path / file_path
                    if file_type == 'config_1':
                        self._copy_file(full_file_path, [self.config_path])
                        self._update_daemon_value(self.config_path / full_file_path.name)
                    elif file_type == 'config_2':
                        self._copy_file(full_file_path, [self.config_path])
                    elif file_type == 'config_3':
                        self._copy_file(full_file_path, self.subfolder_paths)

    def _copy_file(self, source_file, destination_paths):
        source_file_path = Path(source_file)
        if not source_file_path.exists():
            raise FileNotFoundError(f"The file specified in file_path ({source_file_path}) does not exist.")
        for dest_path in destination_paths:
            shutil.copy(source_file_path, dest_path)
        print(f"{source_file_path} copied to {', '.join(map(str, destination_paths))}")

    def _update_daemon_value(self, file_path):
        # check the  port value to update it to 200.
        with open(file_path, 'r') as file:
            lines = file.readlines()

        updated_lines = []
        for line in lines:
            if line.startswith('set PORT=') or line.startswith('set EPORT='):
                parts = line.split('=')
                if len(parts) == 2 and parts[1].strip() != '"200"':
                    updated_lines.append(f'{parts[0]}="200"\n')
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)


# Removed clean up because the files need to be retained for commissioning.
    #def cleanup(self):
        #shutil.rmtree(self.config_path)
        #print(f"Temporary directory {self.config_path} cleaned up")
