from feast import FileSource

metricas_rf_source = FileSource(
    name="metricas_rf_source",
    path="az://features/interferencia_4g/metricas_rf.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
    description="Métricas RF por celda. Actualización: cada 15 min.",
)

metricas_throughput_source = FileSource(
    name="metricas_throughput_source",
    path="az://features/interferencia_4g/metricas_throughput.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
    description="Métricas de throughput por celda. Actualización: cada 15 min.",
)