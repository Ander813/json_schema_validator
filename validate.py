import os
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json
import logging
import logging.handlers


class Meta:
    BASE_DIR = os.getcwd()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(f'{BASE_DIR}/log.log')
    logger.addHandler(file_handler)

    path_event = os.path.join(BASE_DIR, 'event')
    path_schema = os.path.join(BASE_DIR, 'schema')
    try:
        FILES = os.listdir(path_event)
    except FileNotFoundError:
        FILES = None
        logger.info(f'There is no "event" dir in {BASE_DIR} // please add folder "events"')

    try:
        SCHEMAS = os.listdir(path_schema)
    except FileNotFoundError:
        SCHEMAS = None
        logger.info(f'There is no "schema" dir in {BASE_DIR} // please add folder "schema"')

    events = [e.split('.')[0] for e in SCHEMAS]


class SchemasValidator:

    def __init__(self, meta=Meta):
        self.meta = meta

    def run_validation(self):
        for file_name in self.meta.FILES:
            schema_file = None
            file_path = os.path.join(self.meta.path_event, file_name)
            file_data, event = self.open_json_file(file_name, file_path)

            if event:
                if event in self.meta.events:
                    schema_file = f'{event}.schema'
                if schema_file is None:
                    self.meta.logger.info(f'{file_name} - wrong event: {event} allowed events: {self.meta.events}')

            if schema_file:
                schema_path = os.path.join(self.meta.path_schema, schema_file)
                self.validate_with_schema(schema_file, schema_path, file_data, file_name)

    def open_json_file(self, file_name, file_path):
        event = None
        with open(file_path, 'r') as f:
            file_data = json.load(f)
            if isinstance(file_data, type(None)):
                file_data = None
                self.meta.logger.info(f'{file_name} - problems with json file // please check if it if ok')
            else:
                try:
                    event = file_data['event']
                except KeyError:
                    self.meta.logger.info(f'{file_name} - no "event" key // add any of {self.meta.events} to file')
        return file_data, event

    def validate_with_schema(self, schema_file, schema_path, file_data, file_name):
        with open(schema_path, 'r') as s:
            schema_data = json.load(s)
            try:
                validate(file_data, schema_data)
            except ValidationError as e:
                self.meta.logger.info(f'{file_name} - validation error '
                                      f'error message: {e.message}, '
                                      f'schema: {schema_file} // '
                                      f'to fix it add required filed, to your json file')


if __name__ == '__main__':
    validator = SchemasValidator()
    validator.run_validation()
