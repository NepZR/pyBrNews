news_config = {
    "regions": {
        "ac": "e8d0f515-2a44-4c1d-a1da-2cfe2dc4f4bb",
        "al": "29c4b0c2-3d9f-4ffa-8ab1-0ac257ecd59b",
        "ap": "6e58d0ce-52e4-4690-9dbd-9951036be64a",
        "am": "7d75c568-f473-4c74-809b-284d976cb722",
        "ba": "32e4b000-bdad-48d6-bb7b-d1d9fc837640",
        "ce": "a8167ef5-7787-4607-986b-c940e2210e43",
        "df": "cdcc6d5c-58f0-42e9-9fdc-05de78d1ceb1",
        "es": "7f81dda1-de93-48ec-b94e-ccede2dcdf5e",
        "go": "5de8a589-29a6-4e3b-add5-8cb4040717f4",
        "ma": "3c206fcc-cc62-49fb-9907-9439586db007",
        "mt": "97ab2493-d388-4449-83f1-97a47b23759a",
        "ms": "d63532db-cc19-49e0-95c1-f614b1204cd8",
        "mg": "5ba946e9-149f-441d-8395-daf08548d190",
        "pa": "8a76398d-79bf-4c43-8c40-07ef3d22c6cd",
        "pb": "fcbd74d5-4032-486a-ae38-47eaaad71878",
        "pr": "2f91854d-39e3-4860-a56e-1efd49eb8ef9",
        "pe": "7a01cb02-567e-45d6-b5fd-19c94d815c59",
        "pi": "60123655-4c2a-4f65-bdf2-78cbe55bf30b",
        "rj": "f51f667a-9477-40d4-b71e-59170811edc4",
        "rn": "18c7ceca-1653-4629-929f-87f2a84a957f",
        "rs": "17f7d4ee-89c7-4bc9-ae47-3cef4d5ce05c",
        "ro": "c985b52b-3d5b-41fa-88d1-e44e5c4b3e05",
        "rr": "9afcb63b-0d86-4423-b2d4-1591d2842d05",
        "sc": "0df58c7c-0afd-4e7a-a5ac-a552ba85c0ff",
        "sp": "f5a0d89b-0492-4980-a31c-e88fa3ed9f1c",
        "se": "7b272429-d94c-4224-a972-b5abe70bb1d4",
        "to": "6d2ae7ab-5008-408c-b102-6e98dbad025c",
        "brasil": "4af56893-1f9a-4504-9531-74458e481f91"
    },
    "api_url": {
        "news_engine": "https://falkor-cda.bastian.globo.com/tenants/g1/instances/{}/posts/page/{}",
        "search_engine": "https://g1.globo.com/busca/?q={}&page={}&ajax=1"
    }
}

comments_config = {
    "api_url": {
        "comments_engine": "https://ge.comentarios.globo.com/api/graphql",
        "count_engine": "https://g1.comentarios.globo.com/api/story/count?url="
    },

    "params": {
        "query": "",
        "id": "cf0bfa0e60dd576a3908cde9a42cd1f0",
        "variables": "{\"storyURL\":\"@\",\"commentsOrderBy\":\"CREATED_AT_DESC\",\"storyMode\":"
                     "\"COMMENTS\",\"flattenReplies\":true}"
    }
}