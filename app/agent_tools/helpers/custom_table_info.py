# app/agent_tools/custom_table_info.py

CUSTOM_TABLE_INFO_RESERVATIONS = {
    "reservations" : """
    Tabla princial de reservas (header de reservas). 
    Columnas: 
        reservation_id (PK), confirmation_no, reservation_no, parent_reservation_no,
        hotel_code, status, 
        arrival_date, departure_date, nights, checked_out_date, booking_date,
        guest_country_id, num_rooms,
        travel_agent_id, travel_agent_name,
        created_at, modified_at,
        loaded_at, raw_json (original data)
    """,

    "reservation_external_refs" : """
    Tabla que registra los codigos de referencia del perfil del huesped. 
    Columnas: 
        ref_id (PK), reservation_id (FK), ref_id_value, ref_extension, ref_context. 
    La tupla reservation_id, ref_id_value, ref_context es unica.
    """,

    "daily_rates" : """
    Tabla que muestra el revenue diario de cada habitacion en la reserva. (Solo toma en cuenta la tarifa de la reserva).
    Columnas:
        daily_rate_id (PK), reservation_id (FK),
        rate_date, date_id (FK),
        room_id (FK), room_type_id (FK),
        room_amount <- precio de la habitacion por noche,
        adults, children, 
        market_id (FK), source_id (FK), channel_id (FK),
        loaded_at
    """,

    "dim_dates" : """
    Tabla de dimension de fechas. Debido a su estructura, permite analisis de series de tiempo.
    Esta relacionada con daily_rates a traves de date_id.
    Columnas:
        date_id (PK), dt, weekday, weekday_name, is_weekend, month, month_name, quarter, year
    """,

    "dim_room_types" : """
    Tabla de dimension de tipos de habitacion. Si esta disponible (not null), usa description como el alias del tipo de cuarto. 
    Columnas:
        room_type_id (PK), room_type_code, description
    """,

    "dim_rooms": """
    Tabla de dimensiones de codigo de habitacion. No uses la columna description, ya que no tiene informacion relevante.
    Columnas:
        room_id (PK), room_code, room_type_id (FK), description
    """,

    "dim_market_segments": """
    Tabla de dimension de segmentos de mercado. Si esta disponible (not null), usa description como el alias del segmento de mercado.
    Columnas:
        market_id (PK), market_code, description
    """,

    "dim_channels": """
    Tabla de dimension de canales de venta. Si esta disponible (not null), usa description como el alias del canal.
    Columnas:
        channel_id (PK), channel_code, description
    """,

    "dim_sources": """
    Tabla de dimension de Proveedores. Si esta disponible (not null), usa description como el alias de la fuente.
    En otras palabras, de donde proviene la reserva. Puede ser un canal online, una agencia de viajes, etc.
    Columnas:
        source_id (PK), source_code, description
    """,

    "dim_countries": """
    Tabla de dimension de paises. Si esta disponible (not null), usa description como el alias del pais.
    Columnas:
        country_id (PK), country_code, description
    """,
}

CUSTOM_TABLE_INFO_FINANCIALS = {
    "fact_transactions" : """
    Tabla principal de transacciones financieras a asientos contables. Registra los movimientos financieros del hotel. Es el header de las transacciones.
    Columnas:
        transactionInternalId (PK), date_key (FK), account_number (FK), transaction_amount,
    """,
    "dim_dates" : """
    Tabla de dimension de fechas. Debido a su estructura, permite analisis de series de tiempo.
    Esta relacionada con fact_transactions a traves de date_key.
    Columnas:
        date_key (PK), year, quarter, month, day, day_of_week, is_weekend
    """,
    "dim_groups": """
    Tabla de dimensiones de grupos de cuenta. Cada cuenta en dim_accounts pertenece a un grupo. Tambien registra el tipo de cuenta (Income, Other Income, Cost of Goods Sold, Expense y Other Expense).
    Columnas:
        group_number (PK), group_name, account_type
    """,
    "dim_accounts": """
    Tabla de dimensiones de cuentas contables. Cada cuenta tiene un numero unico, el nombre de la cuenta y a que grupo pertenece (group_number).
    Columnas:
        account_number (PK), account_name, group_number (FK)
    """
}