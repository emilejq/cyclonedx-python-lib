import warnings
from enum import Enum
from os.path import exists
from typing import Any, Iterable, Optional, Set, Union
from uuid import uuid4

# See https://github.com/package-url/packageurl-python/issues/65
import serializable
from packageurl import PackageURL
from sortedcontainers import SortedSet

from ..exception.model import NoPropertiesProvidedException
from ..schema.schema import (
    SchemaVersion1Dot0,
    SchemaVersion1Dot1,
    SchemaVersion1Dot2,
    SchemaVersion1Dot3,
    SchemaVersion1Dot4,
    SchemaVersion1Dot4CbomVersion1Dot0
)
from ..serialization import BomRefHelper, PackageUrl
from . import (
    AttachedText,
    ComparableTuple,
    Copyright,
    ExternalReference,
    HashAlgorithm,
    HashType,
    IdentifiableAction,
    LicenseChoice,
    OrganizationalEntity,
    Property,
    XsUri,
    sha1sum,
)
from .bom_ref import BomRef
from .dependency import Dependable
from .issue import IssueType
from .release_note import ReleaseNotes


# @serializable.serializable_class
# class IKEv2TransformTypes:
#     """
#     Our internal representation of the `ikev2TransformTypes` complex type.
#
#     .. note::
#         See the CBOM Schema definition: https://github.com/IBM/CBOM/blob/main/bom-1.4-cbom-1.0.schema.json#L747
#     """
#
#     def __init__(self, *, transform_type_1: Optional[Iterable[str]] = None,
#                  transform_type_2: Optional[Iterable[str]] = None, transform_type_3: Optional[Iterable[str]] = None,
#                  transform_type_4: Optional[Iterable[str]] = None) -> None:
#
#         self.transform_type_1 = transform_type_1
#         self.transform_type_2 = transform_type_2
#         self.transform_type_3 = transform_type_3
#         self.transform_type_4 = transform_type_4
#
#     @property  # type: ignore[misc]
#     @serializable.xml_attribute()
#     def transform_type_1(self) -> str:
#         """
#         Maps to the transformType1 of an IkeV2TransformType.
#
#         Returns:
#             `str`
#         """
#         return self._transform_type_1
#
#     @transform_type_1.setter
#     def transform_type_1(self, transform_type_1: str) -> None:
#         self._transform_type_1 = transform_type_1


@serializable.serializable_class
class AlgorithmProperties:
    """
    Our internal representation of the `algorithmProperties` complex type.

    .. note::
        See the CBOM Schema definition: https://github.com/IBM/CBOM/blob/main/bom-1.4-cbom-1.0.schema.json#L495
    """

    def __init__(self, *, primitive: Optional[str] = None, variant: Optional[str] = None,
                 implementation_level: Optional[str] = None, implementation_platform: Optional[str] = None,
                 certification_level: Optional[str] = None, mode: Optional[str] = None, padding: Optional[str] = None,
                 crypto_functions: Optional[Iterable[str]] = None) -> None:
        self.primitive = primitive
        self.variant = variant
        self.implementation_level = implementation_level
        self.implementation_platform = implementation_platform
        self.certification_level = certification_level
        self.mode = mode
        self.padding = padding
        self.crypto_functions = crypto_functions or []  # type: ignore


@serializable.serializable_class
class CertificateProperties:
    ...


@serializable.serializable_class
class RelatedCryptoMaterialProperties:
    ...


@serializable.serializable_class
class ConfidenceLevels:
    ...


@serializable.serializable_class
class DetectionContext:
    ...


@serializable.serializable_class
class CryptoProperties:
    """
    Our internal representation of the `cryptoProperties` complex type.

    .. note::
        See the CBOM Schema definition: https://github.com/IBM/CBOM/blob/main/bom-1.4-cbom-1.0.schema.json#L478
    """

    def __init__(self, *, oid: Optional[str] = None) -> None:
        self.oid = oid

    @property
    def oid(self) -> Optional[str]:
        """
        Get any declared mime-type for this Component.

        When used on file components, the mime-type can provide additional context about the kind of file being
        represented such as an image, font, or executable. Some library or framework components may also have an
        associated mime-type.

        Returns:
            `str` if set else `None`
        """
        return self._oid

    @oid.setter
    def oid(self, oid: Optional[str]) -> None:
        self._oid = oid

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CryptoProperties):
            return hash(other) == hash(self)
        return False

    def __hash__(self) -> int:
        return hash((
            self.oid
        ))

    def __repr__(self) -> str:
        return f'<CryptoProperties oid={self.oid}>'
