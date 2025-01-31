from typing import Any, Generic, Type, TypeVar

import json

T = TypeVar('T')

datatypes:dict[Type, str] = {
    str: "TEXT",
    int: "INTEGER",
    float: "REAL",
    bytes: "BLOB"
}

class Column(Generic[T]):
    '''PythonSQL Database Table Column'''

    def __init__(self, name:str, sqlType:str, pyType:Type[T], *, nullable:bool=True, primaryKey:bool=False) -> None:
        self._name:str = name
        self._sql_type:str = sqlType
        self._py_type:Type[T] = pyType

        self._nullable:bool = nullable
        self._primary_key:bool = primaryKey
    
    def export_sql(self) -> str:
        ...

    def validate(self, value:Any) -> None:
        if value is None and not self._nullable:
            error:str = f"Column '{self._name}' cannot be 'None'/'null'"
            raise ValueError(error)
    
        if value is not None and not isinstance(value, self._py_type):
            error:str = f"Column '{self._name}' expects {self._py_type}, got {type(value)}"
            raise TypeError(error)

class BytesColumn(Column[bytes]):
    '''PythonSQL Database Table Bytes Column'''

    def __init__(self, name:str, *, nullable:bool=True, primaryKey:bool=False) -> None:
        '''
        Create a database table bytes column
        
        Parameters
        ----------
        name : `str`
            The name of this column
        nullable : `bool`
            If rows can insert `None`/`null` values into this column - Default `True`
        primaryKey : `bool`
            If this column serves as a primary key to the table - Default `False`
        '''

        super().__init__(name, "BLOB", bytes, nullable=nullable, primaryKey=primaryKey)

    def export_sql(self) -> str:
        '''
        Export column data into a string that SQL queries can understand
        '''

        return f"{self._name} {datatypes[bytes]}{" NOT NULL" if not self._nullable else ""}{" PRIMARY KEY" if self._primary_key else ""}"

class FloatColumn(Column[float]):
    '''PythonSQL Database Table Float Column'''

    def __init__(self, name:str, *, nullable:bool=True, primaryKey:bool=False) -> None:
        '''
        Create a database table float column
        
        Parameters
        ----------
        name : `str`
            The name of this column
        nullable : `bool`
            If rows can insert `None`/`null` values into this column - Default `True`
        primaryKey : `bool`
            If this column serves as a primary key to the table - Default `False`
        '''

        super().__init__(name, "REAL", float, nullable=nullable, primaryKey=primaryKey)

    def export_sql(self) -> str:
        '''
        Export column data into a string that SQL queries can understand
        '''

        return f"{self._name} {datatypes[float]}{" NOT NULL" if not self._nullable else ""}{" PRIMARY KEY" if self._primary_key else ""}"

class IntColumn(Column[int]):
    '''PythonSQL Database Table Integer Column'''

    def __init__(self, name:str, *, nullable:bool=True, primaryKey:bool=False) -> None:
        '''
        Create a database table integer column
        
        Parameters
        ----------
        name : `str`
            The name of this column
        nullable : `bool`
            If rows can insert `None`/`null` values into this column - Default `True`
        primaryKey : `bool`
            If this column serves as a primary key to the table - Default `False`
        '''

        super().__init__(name, "INTEGER", int, nullable=nullable, primaryKey=primaryKey)

    def export_sql(self) -> str:
        '''
        Export column data into a string that SQL queries can understand
        '''

        return f"{self._name} {datatypes[int]}{" NOT NULL" if not self._nullable else ""}{" PRIMARY KEY" if self._primary_key else ""}"

class StringColumn(Column[str]):
    '''PythonSQL Database Table String Column'''

    def __init__(self, name:str, *, nullable:bool=True, primaryKey:bool=False, default:str=None) -> None:
        '''
        Create a database table string column
        
        Parameters
        ----------
        name : `str`
            The name of this column
        nullable : `bool`
            If rows can insert `None`/`null` values into this column - Default `True`
        primaryKey : `bool`
            If this column serves as a primary key to the table - Default `False`
        default : `str`
            The default value of this column if not manually provided - Default `None` (empty)
        '''

        super().__init__(name, "TEXT", str, nullable=nullable, primaryKey=primaryKey)

        self._default:str = default

    def export_sql(self) -> str:
        '''
        Export column data into a string that SQL queries can understand
        '''

        return f"{self._name} {datatypes[str]}{" NOT NULL" if not self._nullable else ""}{" PRIMARY KEY" if self._primary_key else ""}{f" DEFAULT {self._default}" if self._default else ""}"

class ListColumn(StringColumn):
    '''PythonSQL Database Table List Column'''

    def __init__(self, name:str, *, nullable:bool=True, primaryKey:bool=False, default:list=None) -> None:
        '''
        Create a database table list column
        
        Parameters
        ----------
        name : `str`
            The name of this column
        nullable : `bool`
            If rows can insert `None`/`null` values into this column - Default `True`
        primaryKey : `bool`
            If this column serves as a primary key to the table - Default `False`
        default : `list`
            The default value of this column if not manually provided - Default `None` (`[]`)
        '''

        super().__init__(name, nullable=nullable, primaryKey=primaryKey, default=default)

        self._default:list = default if default else []
    
    def export_sql(self) -> str:
        '''
        Export column data into a string that SQL queries can understand
        '''

        return f"{self._name} {datatypes[str]}{" NOT NULL" if not self._nullable else ""}{" PRIMARY KEY" if self._primary_key else ""}"

    def validate(self, value:Any) -> None:
        if value is None and not self._nullable:
            error:str = f"Column '{self._name}' cannot be 'None'/'null'"
            raise ValueError(error)
        
        if value is not None and not isinstance(value, list):
            error:str = f"Column '{self._name}' expects a list, got {type(value)}"
            raise TypeError(error)

class DictColumn(StringColumn):
    '''PythonSQL Database Table Dictionary Column'''

    def __init__(self, name:str, *, nullable:bool=True, primaryKey:bool=False, default:dict=None) -> None:
        '''
        Create a database table dictionary column
        
        Parameters
        ----------
        name : `str`
            The name of this column
        nullable : `bool`
            If rows can insert `None`/`null` values into this column - Default `True`
        primaryKey : `bool`
            If this column serves as a primary key to the table - Default `False`
        default : `dict`
            The default value of this column if not manually provided - Default `None` (`{}`)
        '''

        super().__init__(name, nullable=nullable, primaryKey=primaryKey, default=default)

        self._default:dict = default if default else {}
    
    def export_sql(self) -> str:
        '''
        Export column data into a string that SQL queries can understand
        '''

        return f"{self._name} {datatypes[str]}{" NOT NULL" if not self._nullable else ""}{" PRIMARY KEY" if self._primary_key else ""}"

    def validate(self, value:Any) -> None:
        if value is None and not self._nullable:
            error:str = f"Column '{self._name}' cannot be 'None'/'null'"
            raise ValueError(error)
        
        if value is not None and not isinstance(value, dict):
            error:str = f"Column '{self._name}' expects a dict, got {type(value)}"
            raise TypeError(error)