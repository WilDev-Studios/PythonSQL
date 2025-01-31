# PythonSQL Documentation
This is the official documentation page for the `PythonSQL` module

## Basic Information
`PythonSQL` was designed to make managing databases easier and more understandable. While Python isn't meant to be a completely type-safe language, it's imperative that databases maintain data integrity, especially data type integrity. `PythonSQL` instead replaces standard `SQL` syntax with a syntax that is object-oriented, rather than relying on pure `SQL` query language.
<br>
- Minimum Python Version: `3.6.0`
- As of `v1.0.0`, only supports `sqlite3`

## Getting Started
### Installation
- PyPI: `pip install wildev-pysql`

### Basic Objects
- `Database`: Handles each database file. One for each `database1.db`, `database2.db`, etc.
- `Table`: Stores all rows and columns needed for data storage
- `Column`: A basic `Table` column that has basic attributes built-in like `PRIMARY KEY`, `DEFAULT` (if using defaultable column types), and `NULL`
- `Schema`: Alias for `typing`'s `TypedDict`. This is required for IDEs and the program itself to enforce type safety and enhance readability

*Note:* The `Column` isn't directly accessible, as all subclassed `Column` types are used when creating `Table` schemas (`StringColumn` for `str`, `IntColumn` for `int`, etc.)

### Basic Setup
For our example, we are going to maintain a database that keeps track of citizens' names, ages, and social security numbers.

```python
from pythonsql import *

# Create the type-safe schema for readability
class CitizenSchema(Schema):
  ssn:str # Would be an integer, but Python doesn't support integers leading with 0's
  first_name:str
  last_name:str
  age:int

# If autocommit = False, every change in the database must be followed by `database.save()`
database:Database = Database("usa.db", autocommit=True)

# Note that `CitizenSchema` is referenced in the type annotation and table creation
citizenTable:Table[CitizenSchema] = database.create_table("citizens", CitizenSchema, [
  StringColumn("ssn", nullable=False, primaryKey=True),
  StringColumn("first_name", nullable=False),
  StringColumn("last_name", nullable=False),
  IntColumn("age", nullable=False)
])

print(citizenTable.select()) # Will print every row of the `citizens` table
```
If this is a brand new table, it should print `[]`. The return type of the `.select()` method is a `list` of populated `CitizenSchema` `dict` objects.

If we would like to add a new person to the table with a new social security number, we just get all previous numbers and increase.
```python
highestSSN:int = 0

# The datatype of `citizen` is `CitizenSchema` and IDEs will autofill, acknowledge, and recommend types based on this
for citizen in citizenTable.select():
    if int(citizen["ssn"]) <= highestSSN:
        continue

    highestSSN = int(citizen["ssn"])

# The `:09d` leads the highestSSN with x9 0's if not filled
citizenTable.insert({"ssn": f"{highestSSN + 1:09d}", "first_name": "John", "last_name": "Doe", "age": 40})

print(citizenTable.select())
```
Assuming an empty `citizens` table originally, the new output should be:
`[{'ssn': '000000001', 'first_name': 'John', 'last_name': 'Doe', 'age': 40}]`

## Deep Dive into Each Basic SQL Function
Basic manipulation of databases and tables is required to maintain a database. Below is a deep look into each of the common `Database` and `Table` methods.

### DATABASE create_table
- Purpose: Create a new table in the database. Will return the new table or an existing table if one with that name already exists
- Syntax: `database.create_table(tableName, tableSchema, tableColumns)`
- SQL Equivalent: `CREATE TABLE IF NOT EXISTS tableName (tableColumnsKeys)`

### DATABASE drop_table
- Purpose: Delete/drop a previously created table
- Syntax: `database.drop_table(tableName)`
- SQL Equivalent: `DROP TABLE IF EXISTS tableName`

### DATABASE save
- Purpose: Save any changes to the database - Not necessary if the `autocommit` option is `True` on `Database` instantiation
- Syntax: `database.save()`

### TABLE delete
- Purpose: Delete rows from the table
- Syntax: `table.delete(filters)`
- SQL Equivalent: `DELETE FROM tableName WHERE filterKey = filterValue`
- Note: `filters` is optional, but not using it will **delete** every row

### TABLE insert
- Purpose: Insert/create a new row into the table
- Syntax: `table.insert(values)`
- SQL Equivalent: `INSERT INTO tableName (tableColumns) VALUES (values)`

### TABLE select
- Purpose: Retrieve all/specific rows from the table
- Syntax: `table.select(filters)`
- SQL Equivalent: `SELECT * FROM tableName WHERE filterKey = filterValue`
- Note: `filters` is optional, but not using it will return every row

### TABLE update
- Purpose: Update specified rows in the table
- Syntax: `table.update(values, filters)`
- SQL Equivalent: `UPDATE tableName SET valueName = valueValue WHERE filterName = filterValue`
- Note: `filters` is optional, but not using it will update every row

### COLUMN `PRIMARY KEY`
- Purpose: Designate this column in a specific row as a unique identifier for that row specifically. Usually an ID
- Syntax: `~Column(columnName, primaryKey=True/False)`

### COLUMN NULLABLE
- Purpose: Tell the table that this specific column can contain `null`/`None`/empty fields
- Syntax: `~Column(columnName, nullable=True/False)`

### COLUMN DEFAULT
- Purpose: If no value is provided for this column when a new row is inserted, insert this default value automatically
- Syntax: `~Column(columnName, default=...)`
- Note: The `DEFAULT` flag is only available of defaultable datatypes, which is (as of `v1.0.0`) only `TEXT` (`StringColumn`, `ListColumn`, `DictColumn`)
