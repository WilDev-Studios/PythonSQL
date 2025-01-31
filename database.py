from pythonsql.common import Schema
from pythonsql.column import Column
from pythonsql.table import Table

from typing import Type

import sqlite3

class Database:
    '''PythonSQL Database Instance'''

    def __init__(self, filepath:str, *, autocommit:bool=False) -> None:
        '''
        Create a database instance
        
        Parameters
        ----------
        filepath : `str`
            The absolute/relative path to the database file (or to create one)
        autocommit : `bool`
            If the database should save after every SQL query execution
        '''

        self._connection:sqlite3.Connection = sqlite3.connect(filepath, autocommit=autocommit)
        self._tables:dict[str, Table] = {}

        self._autosave:bool = autocommit

    def create_table(self, name:str, schema:Type[Schema], columns:list[Column]) -> Table: # type: ignore
        '''
        Creates/opens a table inside this database
        
        Parameters
        ----------
        name : `str`
            The name of this database table
        schema : `type[pythonsql.Schema]`
            The table schema - A subclass of `Schema` that defines the types of the table columns
        columns : `list[pythonsql.Column]`
            The columns in this table
        
        Returns
        -------
        table : `pythonsql.Table`
            The database table instance connected to this database
        '''

        table:Table = Table(name, schema, columns, self)
        self._tables[name] = table

        return table

    def drop_table(self, name:str) -> None:
        '''
        Drops/deletes a table from the database
        
        Parameters
        ----------
        name : `str`
            The name of the table to delete
        '''

        try:
            del self._tables[name]
        except KeyError:
            error:str = f"Table with name '{name}' does not exist"
            raise KeyError(error)

        self.sql.execute(f"DROP TABLE IF EXISTS {name}")
        self.save()

    def save(self) -> None:
        '''
        Save/commit all changes to the database instance connection file
        '''

        if self._autosave:
            return
        
        self.sql.commit()

    @property
    def sql(self) -> sqlite3.Connection:
        '''The internal database connection'''

        return self._connection