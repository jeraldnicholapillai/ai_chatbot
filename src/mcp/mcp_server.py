from mcp import Server
from schema_tool import get_schema
from sql_tool import run_sql_query
from file_tool import read_file

server = Server(name="Jerald_AI_Tools")

@server.tool()
def schema():
    return get_schema()

@server.tool()
def execute_sql(query: str):
    return run_sql_query(query)

@server.tool()
def read(path: str):
    return read_file(path)

if __name__ == "__main__":
    server.run()
