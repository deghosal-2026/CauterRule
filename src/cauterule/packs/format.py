"""Pack format specification and validation utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PackManifest:
    """Metadata for a versioned rule pack."""

    name: str = ""
    version: str = ""
    description: str = ""
    author: str = ""
    rules: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        pass

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "rules": list(self.rules),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PackManifest:
        """Create from a dict produced by :meth:`to_dict`."""
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            rules=tuple(data.get("rules", [])),
        )


def create_manifest(**kwargs: Any) -> PackManifest:
    """Create a :class:`PackManifest` from keyword arguments.

    Args:
        **kwargs: Passed directly to ``PackManifest(**kwargs)``.

    Returns:
        A new :class:`PackManifest` instance.
    """
    return PackManifest(**kwargs)


def validate_manifest(manifest: PackManifest) -> list[str]:
    """Validate a pack manifest, returning a list of error messages.

    An empty list means the manifest is valid.

    Args:
        manifest: The manifest to validate.

    Returns:
        List of human-readable error strings.
    """
    errors: list[str] = []
    if not manifest.name or not manifest.name.strip():
        errors.append("name must be non-blank")
    if not manifest.version or not manifest.version.strip():
        errors.append("version must be non-blank")
    if not manifest.description or not manifest.description.strip():
        errors.append("description must be non-blank")
    if not manifest.author or not manifest.author.strip():
        errors.append("author must be non-blank")
    if not manifest.rules:
        errors.append("rules must contain at least one rule ID")
    else:
        for i, r in enumerate(manifest.rules):
            if not r or not r.strip():
                errors.append(f"rules[{i}] must be non-blank")
    return errors
