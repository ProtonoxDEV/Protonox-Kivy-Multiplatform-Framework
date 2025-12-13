"""Shared dataclasses for Protonox device-layer requests/results.

All payloads are kept simple and serializable so they can be logged or used by
Protonox Studio without altering the runtime. Everything here is optional and
only loaded when the device layer is explicitly used.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CameraRequest:
    """High-level camera intent for modern Android pipelines (e.g., CameraX)."""

    lens_facing: str = "back"  # back | front
    resolution: Optional[Tuple[int, int]] = None
    fps: Optional[int] = None
    autofocus: bool = True
    exposure_compensation: Optional[float] = None
    stabilize: bool = True


@dataclass
class AudioRequest:
    """Minimal audio capture intent that prefers modern audio paths."""

    sample_rate: int = 48000
    noise_suppression: bool = True
    preferred_device: str = "default"  # default | headset | bluetooth


@dataclass
class LocationRequest:
    """Location intent targeting fused/high-accuracy providers when possible."""

    priority: str = "balanced"  # balanced | high | low
    require_newest: bool = False


@dataclass
class PermissionResult:
    granted: List[str] = field(default_factory=list)
    denied: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, List[str]]:
        return {"granted": self.granted, "denied": self.denied}


@dataclass
class DeviceCapabilities:
    """Lightweight discovery of what the host can support."""

    camera: bool = False
    microphone: bool = False
    gps: bool = False
    bluetooth: bool = False
    storage: bool = False
    contacts: bool = False
    network: bool = False
    api_level: Optional[int] = None

    def as_dict(self) -> Dict[str, Optional[bool]]:
        return {
            "camera": self.camera,
            "microphone": self.microphone,
            "gps": self.gps,
            "bluetooth": self.bluetooth,
            "storage": self.storage,
            "contacts": self.contacts,
            "network": self.network,
            "api_level": self.api_level,
        }


@dataclass
class ConnectivitySnapshot:
    """Simple connectivity probe for Wi-Fi / cellular diagnostics."""

    is_connected: bool
    transport: str  # wifi | cellular | unknown
    ssid: Optional[str] = None
    down_kbps: Optional[float] = None
    up_kbps: Optional[float] = None


@dataclass
class SensorSnapshot:
    """Small representation of sensor readings for debugging only."""

    location: Optional[Tuple[float, float]] = None
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    acceleration: Optional[Tuple[float, float, float]] = None
    rotation: Optional[Tuple[float, float, float]] = None


@dataclass
class StorageHandle:
    uri: Optional[str] = None
    path: Optional[str] = None
    description: Optional[str] = None
