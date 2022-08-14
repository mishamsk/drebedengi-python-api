from attrs import fields_dict, has
from lxml import etree
from zeep import xsd
from zeep.helpers import guess_xsd_type

from typing import Any, List, Type, TypeVar

T = TypeVar("T")

_get_xmlmap_value_by_key = etree.XPath("item/key[text() = $key]/../value/text()")
""" Gets value by key from an XML ns2:Map. """


def xmlmap_to_model(xmlmap: etree.Element, model_type: Type[T], *, strict: bool = True) -> T:
    """Converts XML ns2:Map to a model of type `model_type`.

    Args:
        xmlmap (etree.Element): xml subtree (ns2:Map) representing a model
        model_type (Type[T]): model type to map data into
        strict (bool, optional): fail if the returned data doesn't match the model. Defaults to True.

    Raises:
        ValueError: if `strict` is True and the returned data doesn't match the model.
        ValueError: if the model_type is not an attrs-based model.

    Returns:
        T: generated model instance
    """
    if not has(model_type):
        raise ValueError(f"{model_type} is not a model")

    model_fields = fields_dict(model_type)  # type: ignore # (until https://github.com/python-attrs/attrs/pull/997)

    vals = {}
    for name, field in model_fields.items():
        # If a name is defined in the metadata => it has a different xml key, otherwise just use model field name
        key = field.metadata.get("xml", {}).get("name", name)
        value = _get_xmlmap_value_by_key(xmlmap, key=key)
        if value:
            vals[name] = value[0]
        elif strict and not (field.type and isinstance(None, field.type)):
            raise ValueError(f"Key: {name} was not found in the element {etree.dump(xmlmap)}")

    try:
        ret = model_type(**vals)
    except ValueError:
        raise ValueError(f"Could not convert values from {etree.dump(xmlmap)} to {model_type}")

    return ret


def generate_xml_array(values: List[Any]) -> xsd.ComplexType:
    """Generates an SOAP Array from a list of values."""
    Array = xsd.ComplexType(
        xsd.Sequence([xsd.Element("item", xsd.AnyType(), min_occurs=1, max_occurs="unbounded")]),  # type: ignore
        qname=etree.QName("{http://schemas.xmlsoap.org/soap/encoding/}Array"),
    )

    return Array(item=[xsd.AnyObject(guess_xsd_type(value), value) for value in values])  # type: ignore
