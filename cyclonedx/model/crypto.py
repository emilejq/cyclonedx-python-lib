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


class AssetType(str, Enum):
    """
    Enum object that defines the permissible 'types' for a crypto asset according to the CBOM schema.

    .. note::
        See the CycloneDX Schema definition: https://github.com/IBM/CBOM/blob/main/bom-1.4-cbom-1.0.schema.json#L484
    """
    ALGORITHM = 'algorithm'
    CERTIFICATE = 'certificate'
    RELATED_CRYPTO_MATERIAL = 'relatedCryptoMaterial'
    PROTOCOL = 'protocol'


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
    def __init__(self, *, file_path: Optional[str] = None, additional_context: Optional[str] = None) -> None:
        self.file_path = file_path
        self.additional_context = additional_context

    @property
    def file_path(self) -> Optional[str]:
        """
        Get any declared mime-type for this Component.

        When used on file components, the mime-type can provide additional context about the kind of file being
        represented such as an image, font, or executable. Some library or framework components may also have an
        associated mime-type.

        Returns:
            `str` if set else `None`
        """
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: Optional[str]) -> None:
        self._file_path = file_path

    @property
    def additional_context(self) -> Optional[str]:
        """
        Get any declared mime-type for this Component.

        When used on file components, the mime-type can provide additional context about the kind of file being
        represented such as an image, font, or executable. Some library or framework components may also have an
        associated mime-type.

        Returns:
            `str` if set else `None`
        """
        return self._additional_context

    @additional_context.setter
    def additional_context(self, additional_context: Optional[str]) -> None:
        self._additional_context = additional_context

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DetectionContext):
            return hash(other) == hash(self)
        return False

    def __hash__(self) -> int:
        return hash((
            self.file_path, self.additional_context
        ))


@serializable.serializable_class
class CryptoProperties:
    """
    Our internal representation of the `cryptoProperties` complex type.

    .. note::
        See the CBOM Schema definition: https://github.com/IBM/CBOM/blob/main/bom-1.4-cbom-1.0.schema.json#L478
    """

    def __init__(self, *, asset_type: AssetType = None, classical_security_level: Optional[int] = None,
                 nist_quantum_security_level: Optional[int] = None, oid: Optional[str] = None,
                 scanner: Optional[str] = None, detection_context: Optional[Iterable[DetectionContext]]) -> None:
        if classical_security_level < 0:
            raise ValueError('Classical security level cannot be less than 0')
        if nist_quantum_security_level < 0 or nist_quantum_security_level > 6:
            raise ValueError('NIST quantum security level must be between 0 and 6')

        self.asset_type = asset_type
        self.classical_security_level = classical_security_level
        self.nist_quantum_security_level = nist_quantum_security_level
        self.oid = oid
        self.scanner = scanner
        self.detection_context = detection_context or []

    @property  # type: ignore[misc]
    @serializable.xml_attribute()
    def asset_type(self) -> AssetType:
        """
        Get the type of this Component.

        Returns:
            Declared type of this Component as `ComponentType`.
        """
        return self._asset_type

    @asset_type.setter
    def asset_type(self, asset_type: AssetType) -> None:
        self._asset_type = asset_type

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

    @property
    def scanner(self) -> Optional[str]:
        """
        Get any declared mime-type for this Component.

        When used on file components, the mime-type can provide additional context about the kind of file being
        represented such as an image, font, or executable. Some library or framework components may also have an
        associated mime-type.

        Returns:
            `str` if set else `None`
        """
        return self._scanner

    @scanner.setter
    def scanner(self, scanner: Optional[str]) -> None:
        self._scanner = scanner

    @property
    def classical_security_level(self) -> Optional[int]:
        """
        Get any declared mime-type for this Component.

        When used on file components, the mime-type can provide additional context about the kind of file being
        represented such as an image, font, or executable. Some library or framework components may also have an
        associated mime-type.

        Returns:
            `str` if set else `None`
        """
        return self._classical_security_level

    @classical_security_level.setter
    def classical_security_level(self, classical_security_level: Optional[int]) -> None:
        self._classical_security_level = classical_security_level

    @property
    def nist_quantum_security_level(self) -> Optional[int]:
        """
        Get any declared mime-type for this Component.

        When used on file components, the mime-type can provide additional context about the kind of file being
        represented such as an image, font, or executable. Some library or framework components may also have an
        associated mime-type.

        Returns:
            `str` if set else `None`
        """
        return self._nist_quantum_security_level

    @nist_quantum_security_level.setter
    def nist_quantum_security_level(self, nist_quantum_security_level: Optional[int]) -> None:
        self._nist_quantum_security_level = nist_quantum_security_level

    @property  # type: ignore[misc]
    @serializable.xml_array(serializable.XmlArraySerializationType.NESTED, 'detectionContext')
    @serializable.xml_sequence(9)
    def detection_context(self) -> "SortedSet[DetectionContext]":
        """
        Optional list of hashes that help specify the integrity of this Component.

        Returns:
             Set of `HashType`
        """
        return self._detection_context

    @detection_context.setter
    def detection_context(self, detection_context: Iterable[DetectionContext]) -> None:
        self._detection_context = SortedSet(detection_context)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CryptoProperties):
            return hash(other) == hash(self)
        return False

    def __hash__(self) -> int:
        return hash((
            self.asset_type, self.classical_security_level, self.nist_quantum_security_level, self.oid, self.scanner
        ))

    def __repr__(self) -> str:
        return (f'<CryptoProperties assetType={self.asset_type}, classicalSecurityLevel={self.classical_security_level},'
                f'oid={self.oid}, scanner={self.scanner}, nistQuantumSecurityLevel={self.nist_quantum_security_level}>')
