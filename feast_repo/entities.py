from feast import Entity
from feast.value_type import ValueType
 
celda = Entity(
    name="cell_id",
    value_type=ValueType.STRING,
    description="Identificador único de celda/sector 4G (e.g. ENB10000_S1)",
)