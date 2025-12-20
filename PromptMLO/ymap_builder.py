import uuid
from typing import Dict, List


def _entity_xml(archetype: str, position: Dict, rotation: Dict) -> str:
    guid = str(uuid.uuid4())
    return (
        "    <Item type=\"CEntityDef\">\n"
        f"      <archetypeName>{archetype}</archetypeName>\n"
        f"      <position x=\"{position['x']:.3f}\" y=\"{position['y']:.3f}\" z=\"{position['z']:.3f}\" />\n"
        f"      <rotation x=\"{rotation['x']:.3f}\" y=\"{rotation['y']:.3f}\" z=\"{rotation['z']:.3f}\" w=\"{rotation['w']:.3f}\" />\n"
        "      <scaleXY value=\"1.000\" />\n"
        "      <scaleZ value=\"1.000\" />\n"
        "      <flags value=\"0\" />\n"
        f"      <guid>{guid}</guid>\n"
        "    </Item>\n"
    )


def build_ymap(layout: Dict, furnishings: List[Dict]) -> str:
    entities = []
    for module in layout["modules"]:
        entities.append(_entity_xml(module["archetype"], module["position"], module["rotation"]))

    for prop in furnishings:
        entities.append(_entity_xml(prop["archetype"], prop["position"], prop["rotation"]))

    entities_xml = "".join(entities)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<mapData>\n"
        "  <name>promptmlo_generated</name>\n"
        "  <parent/>\n"
        "  <contentFlags value=\"131072\"/>\n"
        "  <entities>\n"
        f"{entities_xml}"
        "  </entities>\n"
        "  <streamingExtentsMin x=\"-200.0\" y=\"-200.0\" z=\"-50.0\" />\n"
        "  <streamingExtentsMax x=\"200.0\" y=\"200.0\" z=\"150.0\" />\n"
        "</mapData>\n"
    )
