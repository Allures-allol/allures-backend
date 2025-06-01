# from gql import Client, gql
# from gql.transport.aiohttp import AIOHTTPTransport
#
# TODO: Замените на URL внешнего GraphQL сервера, когда он будет доступен
# EXTERNAL_GRAPHQL_URL = "https://external-graphql-server.com/graphql/"
#
# # Настройка транспорта и клиента
# transport = AIOHTTPTransport(url=EXTERNAL_GRAPHQL_URL)
# client = Client(transport=transport, fetch_schema_from_transport=True)

# async def fetch_allures_products():
#     pass  # Заглушка или возврат пустого списка
#     query = gql("""
#     query {
#         products(first: 10) {
#             edges {
#                 node {
#                     id
#                     name
#                     description
#                     pricing {
#                         priceRange {
#                             start {
#                                 gross {
#                                     amount
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }
#     """)
# async with client as session:
#     try:
#         result = await session.execute(query)
#         products = [edge["node"] f except Exception as e:
#         print(f"Ошибка при выполнении GraphQL запроса: {e}")
#         return [or edge in result["products"]["edges"]]
#         return products
#    ]
