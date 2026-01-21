import json
from typing import Callable,Optional

class GridColumn:
    def __init__(self, field: str, headerName: str, filter: bool, editable: bool,
                valueFormatter: Optional[Callable[[str], str]] = None):
        if not isinstance(field, str):
            raise TypeError("field must be a string")
        if not isinstance(headerName, str):
            raise TypeError("headerName must be a string")
        if not isinstance(filter, bool):
            raise TypeError("filter must be a boolean")
        if not isinstance(editable, bool):
            raise TypeError("editable must be a boolean")
        if valueFormatter is not None and not callable(valueFormatter):
            raise TypeError("valueFormatter must be a callable function")
        
        self.field = field
        self.headerName = headerName
        self.filter = filter
        self.editable = editable
        self.valueFormatter= valueFormatter  

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "headerName": self.headerName,
            "filter": self.filter,
            "editable": self.editable,
            "valueFormatter":self.valueFormatter.__name__ if self.valueFormatter else None
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_str: str):
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON") from e

        required_keys = {"field", "headerName", "filter", "editable","valueFormatter"}
        if not required_keys.issubset(data):
            raise ValueError(f"Missing keys in JSON: {required_keys - data.keys()}")

        value_formatter_name = data.get("valueFormatter")
        value_formatter = None
        if value_formatter_name:
            raise NotImplementedError("Dynamic value formatter loading is not implemented.")

        return GridColumn(
            field=data["field"],
            headerName=data["headerName"],
            filter=data["filter"],
            editable=data["editable"],
            valueFormatter=data["valueFormatter"]
        )

    def format_value(self, value: str) -> str:
        if value is None: 
            return value
        if self.valueFormatter:
            return self.valueFormatter(value)
        return value


    def __repr__(self):
        return f"GridColumn({self.to_dict()})"


class GridColumnFactory:
    @staticmethod
    def create(field: str, headerName: str, filter: bool = False, editable: bool = False, valueFormatter= str) -> GridColumn:
        return GridColumn(field, headerName, filter, editable,valueFormatter)


class GridSchema:
    def __init__(self):
        self.columns = {}

    def add_column(self, column: GridColumn):
        if column.field in self.columns:
            raise ValueError(f"Column with field '{column.field}' already exists.")
        if not isinstance(column, GridColumn):
            raise TypeError(f"Expected a GridColumn object, got {type(column)}")
        self.columns[column.field] = column

    def get_columns_arrayObj(self) ->GridColumn:
        return [column  for column in self.columns.items()]


    def get_columns_array(self) -> list:
        # Return columns as an array of dictionaries
        return [column.to_dict() for column in self.columns.values()]

    def get_columns_dict(self) -> dict:
        return {field: column.to_dict() for field, column in self.columns.items()}

    def __repr__(self):
        return f"GridSchema(columns={self.get_columns_array()})"