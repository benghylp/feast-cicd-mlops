from datetime import timedelta
from feast import FeatureView, Field
from feast.types import Float32, Int64, String
from entities import celda
from sources import metricas_rf_source, metricas_throughput_source

metricas_rf_fv = FeatureView(
    name="metricas_rf",
    entities=[celda],
    ttl=timedelta(hours=1),
    schema=[
        Field(name="rsrp_dbm", dtype=Float32, description="Reference Signal Received Power (dBm)"),
        Field(name="rsrq_db", dtype=Float32, description="Reference Signal Received Quality (dB)"),
        Field(name="sinr_db", dtype=Float32, description="Signal to Interference plus Noise Ratio (dB)"),
        Field(name="cqi_mean", dtype=Float32, description="Channel Quality Indicator promedio (0-15)"),
        Field(name="pci", dtype=Int64, description="Physical Cell ID (0-503)"),
        Field(name="earfcn", dtype=Int64, description="E-UTRA Absolute Radio Frequency Channel Number"),
        Field(name="banda", dtype=String, description="Banda de frecuencia (B2, B4, B7, B28)"),

    ],
    source=metricas_rf_source,
    online=True,
    description="Métricas de señal RF por celda",
    tags={"domain": "radio", "refresh": "15min", "owner": "red-movil"},
)

metricas_throughput_fv = FeatureView(
    name="metricas_throughput",
    entities=[celda],
    ttl=timedelta(hours=1),
    schema=[
        Field(name="throughput_dl_mbps", dtype=Float32, description="Throughput downlink (Mbps)"),
        Field(name="throughput_ul_mbps", dtype=Float32, description="Throughput uplink (Mbps)"),
        Field(name="latencia_ms", dtype=Float32, description="Latencia promedio (ms)"),
        Field(name="packet_loss_pct", dtype=Float32, description="Pérdida de paquetes (%)"),
        Field(name="usuarios_conectados", dtype=Int64, description="Usuarios conectados"),
        Field(name="prb_usage_dl_pct", dtype=Float32, description="Uso de PRBs downlink (%)"),
        Field(name="prb_usage_ul_pct", dtype=Float32, description="Uso de PRBs uplink (%)"),
    ],
    source=metricas_throughput_source,
    online=True,
    description="Métricas de throughput y capacidad por celda",
    tags={"domain": "performance", "refresh": "15min", "owner": "red-movil"},
)