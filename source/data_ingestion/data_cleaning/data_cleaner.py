from .utils import *
from .abstract import *

DEBUG = False  # Global debug switch


def enable_debug():
    global DEBUG
    DEBUG = True


def debug_log(field, before, after):
    if DEBUG:
        if before != after:
            print(f"Field: {field}, Update: {before} >>>> To >>>  {after}")


class FieldCleaner:
    field_key = ""

    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        return value


class TimeFieldCleaner(FieldCleaner):
    field_key = "Time"

    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        before = value
        if key == self.field_key and isinstance(value, str):
            value = convert_to_24h(value)
        after = value
        debug_log(self.field_key, before, after)
        return value


class DateFieldCleaner(FieldCleaner):
    field_key = "Date"

    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        before = value
        if key == self.field_key and isinstance(value, str):
            value = clean_date(value)
        after = value
        debug_log(self.field_key, before, after)
        return value


class ConductorNameFieldCleaner(FieldCleaner):
    field_key = "conductorName"

    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        before = value
        if key == self.field_key and isinstance(value, str):
            value = value.lstrip(";").strip()
            value = clean_string_common(value)
        after = value
        debug_log(self.field_key, before, after)
        return value


class GenericStringFieldCleaner(FieldCleaner):
    field_key = ""

    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        before = value
        if isinstance(value, str):
            value = clean_string_common(value)
        after = value
        debug_log(self.field_key or key, before, after)
        return value


class SoloistFieldCleaner(FieldCleaner):
    field_key = "soloists"

    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        before = value
        if key == self.field_key:
            if not isinstance(value, list) or value is None or not value:
                value = []
        after = value
        debug_log(self.field_key, before, after)
        return value


class DataFieldProcessor:
    def __init__(self):
        self.cleaner_map = {
            "Time": [TimeFieldCleaner()],
            "Date": [DateFieldCleaner()],
            "conductorName": [GenericStringFieldCleaner(), ConductorNameFieldCleaner()],
            "soloistName": [GenericStringFieldCleaner()],
            "soloists": [SoloistFieldCleaner()],
            "soloistInstrument": [GenericStringFieldCleaner()],
            "soloistRoles": [GenericStringFieldCleaner()],
            "composerName": [GenericStringFieldCleaner()],
            "workTitle": [GenericStringFieldCleaner()],
            "orchestra": [GenericStringFieldCleaner()],
            "season": [GenericStringFieldCleaner()],
            "eventType": [GenericStringFieldCleaner()],
            "Location": [GenericStringFieldCleaner()],
            "Venue": [GenericStringFieldCleaner()],
            "interval": [GenericStringFieldCleaner()],
            "movement": [GenericStringFieldCleaner()],
            "programID": [GenericStringFieldCleaner()],
            "ID": [GenericStringFieldCleaner()],
        }

    def clean_field(self, key: str, value: Any, context: Dict = None) -> Any:
        cleaners = self.cleaner_map.get(key, [GenericStringFieldCleaner()])
        before = value
        for cleaner in cleaners:
            value = cleaner.clean(key, value, self)
        after = value
        debug_log(key, before, after)
        return value

    def clean(self, path: List[str], data: Any) -> Any:
        """Recursively clean data while tracking the path."""
        if isinstance(data, dict):
            cleaned = {}
            for k, v in data.items():
                current_path = path + [k]  # Extend the path
                cleaned[k] = self.clean(current_path, v)
            return cleaned
        elif isinstance(data, list):
            cleaned = []
            for i, item in enumerate(data):
                # Extend the path with the index
                current_path = path + [str(i)]
                cleaned.append(self.clean(current_path, item))
            return cleaned
        else:
            # For base fields, use the path's last element as the key
            key = path[-1] if path else None
            return self.clean_field(key, data, path)
