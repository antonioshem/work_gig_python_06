import shutil
import yaml
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.base_dir = '/home/test/'
        self.base_path = Path.cwd() / self.base_dir
        self.config_path = self.base_path / 'config'
        self.subfolder_paths = []

    def create_directory_structure(self, subfolders):
        # create config folder inside the test_path
        self.config_path.mkdir(parents=True, exist_ok=True)

        # create subfolders for sbts inside config
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

    def _config_1(self, full_file_path):
        self._copy_file(full_file_path, [self.config_path])
        self._update_port_value(self.config_path / full_file_path.name)

    def _config_2(self, full_file_path):
        self._copy_file(full_file_path, [self.config_path])

    def _config_3(self, full_file_path):
        self._copy_file(full_file_path, self.subfolder_paths)

    def copy_files(self):
        # Ensure validate_default() has been called and found a default match
        self._validate_default()

        actions = {
            'config_1': self._config_1,
            'config_2': self._config_2,
            'config_3': self._config_3
        }

        for node in self.default_match.get('nodes', []):
            for file in node.get('files', []):
                file_type = file.get('file_type')
                file_path = file.get('file_path')
                if file_type and file_path:
                    full_file_path = self.source_path / file_path
                    action = actions.get(file_type)
                    if action:
                        action(full_file_path)

    def _validate_default(self):
        # check for default True or true in the yaml
        self.default_match = None
        for match in self.config_data.get('variants', []):
            if match.get('default') in [True, "true"]:
                self.default_match = match
                break
        if self.default_match is None:
            raise ValueError("No 'default: true' or 'default: True' found in the config file.")

    def _copy_file(self, source_file, destination_paths):
        source_file_path = Path(source_file)
        if not source_file_path.exists():
            raise FileNotFoundError(f"The file specified in file_path ({source_file_path}) does not exist.")
        for dest_path in destination_paths:
            shutil.copy(source_file_path, dest_path)
        print(f"{source_file_path} copied to {', '.join(map(str, destination_paths))}")

    def _update_port_value(self, file_path):
        lines = self._read_file_lines(file_path)
        updated_lines = self._update_lines(lines)
        self._write_file_lines(file_path, updated_lines)

    def _read_file_lines(self, file_path):
        with open(file_path, 'r') as file:
            return file.readlines()

    def _update_lines(self, lines):
        updated_lines = []
        for line in lines:
            updated_lines.append(self._update_port_line(line))
        return updated_lines

    def _update_port_line(self, line):
        if line.startswith('set PORT=') or line.startswith('set EPORT='):
            parts = line.split('=')
            if len(parts) == 2 and parts[1].strip() != '"200"':
                return f'{parts[0]}="200"\n'
        return line

    def _write_file_lines(self, file_path, lines):
        with open(file_path, 'w') as file:
            file.writelines(lines)
