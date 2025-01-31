from typing import Generic, Type, TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:
    from pythonsql.database import Database

from pythonsql.column import Column, DictColumn, ListColumn
from pythonsql.common import Schema

import json
import sqlite3

T_Schema = TypeVar("T_Schema", bound=Schema) # type: ignore

class Table(Generic[T_Schema]):
    '''PythonSQL Database Table Instance'''

    def __init__(self, name:str, schema:Type[T_Schema], columns:list[Column], database:'Database') -> None:
        '''
        Create a database table instance
        
        Note
        ----
        This is an internal instantiation, and should not be called elsewhere

        Parameters
        ----------
        name : `str`
            The name of the database table
        schema : `type[pythonsql.Schema]`
            The table schema type
        columns : `list[pythonsql.Column]`
            All table columns
        database : `pythonsql.Database`
            The database instance
        '''

        self._name:str = name
        self._columns:dict[str, Column] = {col._name: col for col in columns}
        self._schema:Type[T_Schema] = schema
        
        self.database:'Database' = database
        '''The table instance's database'''

        self.database.sql.execute(f"CREATE TABLE IF NOT EXISTS {self._name} ({', '.join([column.export_sql() for column in self._columns.values()])})")
        self.database.save()
    
    def _convert_row_to_dict(self, row:tuple) -> T_Schema:
        names:list[str] = list(self._columns.keys())
        data:dict[str] = {names[i]: row[i] for i in range(len(names))}

        for name, column in self._columns.items():
            if not isinstance(column, (ListColumn, DictColumn)):
                continue

            data[name] = json.loads(data[name]) if data[name] else column._default
        
        return data

    def delete(self, **filters) -> None:
        '''
        Deletes rows from the table
        
        Parameters
        ----------
        filters : `Any`
            The keyword-arguments for selecting specific columns and a row with a matching value
        '''

        filterClause:str = " AND ".join(f"{key} = ?" for key in filters.keys())
        values:tuple = tuple(filters.values())

        self.database.sql.execute(f"DELETE FROM {self._name}{f" WHERE {filterClause}" if filters else ""}", values)
        self.database.save()

    def insert(self, values:T_Schema) -> None:
        '''
        Insert/Create a row in this table

        Parameters
        ----------
        values : `pythonsql.Schema`
            The key-value pair(s) of the item(s) you wish to insert
        '''

        if not set(values.keys()).issubset(self._columns.keys()):
            error:str = f"Invalid columns. Expected {set(self._columns.keys())}, got {set(values.keys())}"
            raise ValueError(error)
        
        for columnName, column in self._columns.items():
            if columnName not in values and hasattr(column, "_default"):
                values[columnName] = column._default
        
        for name, value in values.items():
            self._columns[name].validate(value)
        
        valuesTuple:tuple[Union[str, object]] = tuple(json.dumps(v) if isinstance(v, (list, dict)) else v for v in values.values())

        placeholders:str = ", ".join('?' for _ in values)
        columnNames:str = ", ".join(values.keys())
        sql:str = f"INSERT INTO {self._name} ({columnNames}) VALUES ({placeholders})"

        self.database.sql.execute(sql, valuesTuple)
        self.database.save()
    
    def select(self, **filters) -> list[T_Schema]:
        '''
        Retrieves all/specific rows from the table
        
        Parameters
        ----------
        filters : `Any`
            The keyword-arguments for selecting specific columns and a row with a matching value

        Returns
        -------
        result : `list[pythonsql.Schema]`
            All rows retrieved - Empty list if none were found
        '''

        if not filters:
            cursor:sqlite3.Cursor = self.database.sql.execute(f"SELECT * FROM {self._name}")
            rows:list = cursor.fetchall()

            if not rows:
                return []

            return [self._convert_row_to_dict(row) for row in rows]
        
        conditions:str = " AND ".join(f"{key} = ?" for key in filters.keys())
        values:tuple = tuple(filters.values())

        cursor:sqlite3.Cursor = self.database.sql.execute(f"SELECT * FROM {self._name}{f" WHERE {conditions}" if filters else ""}", values)
        rows:list = cursor.fetchall()

        if not rows:
            return []
        
        return [self._convert_row_to_dict(row) for row in rows]
    
    def update(self, values:dict[str], **filters) -> None:
        '''
        Updates specified rows with new values
        
        Parameters
        ----------
        values : `dict[str, Any]`
            The 'column: new_value' pairs
        filters : `Any`
            The keyword-arguments for selecting specific columns and a row with a matching value
        '''

        if not values:
            error:str = "At least one column must be specified to update"
            raise ValueError(error)
        
        for key in values.keys():
            if key in self._columns:
                continue

            error:str = f"Invalid column: {key}"
            raise ValueError(error)
        
        setClause:str = ", ".join(f"{key} = ?" for key in values.keys())
        filterClause:str = " AND ".join(f"{key} = ?" for key in filters.keys())

        values:tuple = tuple(values.values()) + tuple(filters.values())

        self.database.sql.execute(f"UPDATE {self._name} SET {setClause}{f" WHERE {filterClause}" if filters else ""}", values)
        self.database.save()
