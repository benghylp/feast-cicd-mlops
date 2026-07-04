from feast import FeatureService
from feature_views import metricas_rf_fv, metricas_throughput_fv

interferencia_4g_service = FeatureService(
    name="interferencia_4g_service",
    features=[metricas_rf_fv, metricas_throughput_fv],
    description="Features para el modelo de detección de interferencia 4G",
    tags={"model": "InterferenciaDetector", "team": "red-movil", "version": "v1"},
)

rf_analysis_service = FeatureService(
    name="rf_analysis_service",
    features=[metricas_rf_fv],
    description="Solo métricas RF para análisis rápido",
    tags={"model": "rf-analysis", "team": "red-movil", "version": "v1"},
)