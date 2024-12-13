# stdlib
import os

# third party
from dbtc import dbtCloudClient
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()


client = dbtCloudClient(
    host=os.getenv("DBT_CLOUD_HOST"),
)
credentials = service_account.Credentials.from_service_account_file(
    "./service_account.json"
)
bigquery_client = bigquery.Client(credentials=credentials)


def get_upstream_column_descriptions(node: dict) -> tuple[bool, dict[str, dict]]:
    upstream_columns = {}
    columns = node.get("catalog", {}).get("columns", [])
    for column in columns:
        if column.get("descriptionOriginColumnName") is not None:
            upstream_columns[column["name"]] = column["description"]

    if upstream_columns:
        return True, upstream_columns

    return False, {}


def get_table_from_node(node: dict) -> str:
    table_id = f"{node['database']}.{node['schema']}.{node['alias']}"
    return bigquery_client.get_table(table_id)


QUERY = """
query Models($environmentId: BigInt!, $first: Int, $after: String) {
  environment(id: $environmentId) {
    applied {
      models(first: $first, after: $after) {
        pageInfo {
          endCursor
          hasNextPage
          hasPreviousPage
          startCursor
        }
        totalCount
        edges {
          node {
            database
            schema
            alias
            catalog {
              columns {
                description
                name
                descriptionOriginColumnName
              }
            }
          }
        }
      }
    }
  }
}
"""
VARIABLES = {
    "environmentId": int(os.environ["DBT_CLOUD_ENVIRONMENT_ID"]),
    "first": 500,
    "after": None,
}


if __name__ == "__main__":
    response_list = client.metadata.query(QUERY, VARIABLES)
    models = []
    for response in response_list:
        models.extend(
            response.get("data", {})
            .get("environment", {})
            .get("applied", {})
            .get("models", {})
            .get("edges", [])
        )
    if not models:
        print("No models found")
        exit(0)

    for model in models:
        node = model["node"]
        has_upstream_column_descriptions, columns = get_upstream_column_descriptions(
            node
        )
        if has_upstream_column_descriptions:
            table = get_table_from_node(node)
            table_repr = table.to_api_repr()
            fields = table_repr["schema"]["fields"].copy()
            for field in fields:
                if columns.get(field["name"]):
                    field["description"] = columns[field["name"]]

            table_repr["schema"]["fields"] = fields
            table = table.from_api_repr(table_repr)
            updated_table = bigquery_client.update_table(table, ["schema"])
            print(f"Updated table {updated_table.table_id}")
