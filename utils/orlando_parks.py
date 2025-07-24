def get_orlando_parks():
    """
    Retorna a lista de parques de Orlando com informações de ID
    
    Returns:
        tuple: (lista_parques, lista_numerada)
    """
    parks = [
        {"id": 1, "nome": "Magic Kingdom", "codigo": "magic-kingdom"},
        {"id": 2, "nome": "Animal Kingdom", "codigo": "animal-kingdom"},
        {"id": 5, "nome": "Hollywood Studios", "codigo": "hollywood-studios"},
        {"id": 6, "nome": "Epcot", "codigo": "epcot"},
        {"id": 3, "nome": "Universal Studios Florida", "codigo": "universal-studios"},
        {"id": 4, "nome": "Islands of Adventure", "codigo": "islands-of-adventure"},
        {"id": 7, "nome": "Volcano Bay", "codigo": "volcano-bay"},
        {"id": 8, "nome": "SeaWorld Orlando", "codigo": "seaworld"}
    ]
    
    # Cria a lista numerada
    lista_numerada = ""
    for i, park in enumerate(parks, 1):
        lista_numerada += f"{i}. {park['nome']}\n"
    
    return parks, lista_numerada