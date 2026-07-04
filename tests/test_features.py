"""Tests de convenciones — feast-ci.yml los ejecuta automáticamente."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "feast_repo"))


def test_entity_has_value_type():
    from entities import celda
    assert celda.value_type is not None


def test_entity_has_description():
    from entities import celda
    assert celda.description


def test_feature_views_have_ttl():
    from feature_views import metricas_rf_fv, metricas_throughput_fv
    for fv in [metricas_rf_fv, metricas_throughput_fv]:
        assert fv.ttl is not None, f"{fv.name} falta TTL"
        assert fv.ttl.total_seconds() > 0, f"{fv.name} TTL debe ser > 0"


def test_feature_views_have_schema():
    from feature_views import metricas_rf_fv, metricas_throughput_fv
    for fv in [metricas_rf_fv, metricas_throughput_fv]:
        assert len(fv.schema) > 0, f"{fv.name} sin schema"
        for field in fv.schema:
            assert field.dtype is not None, f"Field {field.name} en {fv.name} falta dtype"


def test_feature_views_have_required_tags():
    from feature_views import metricas_rf_fv, metricas_throughput_fv
    for fv in [metricas_rf_fv, metricas_throughput_fv]:
        for tag in ["domain", "refresh", "owner"]:
            assert tag in fv.tags, f"{fv.name} falta tag '{tag}'"


def test_feature_services_have_tags():
    from feature_services import interferencia_4g_service
    for tag in ["model", "team"]:
        assert tag in interferencia_4g_service.tags, f"Service falta tag '{tag}'"


def test_online_enabled():
    from feature_views import metricas_rf_fv, metricas_throughput_fv
    for fv in [metricas_rf_fv, metricas_throughput_fv]:
        assert fv.online is True, f"{fv.name} debe tener online=True"