class QISError(RuntimeError):
    """Base framework exception."""


class ConfigurationError(QISError):
    """Invalid or inconsistent configuration."""


class EventFormatError(QISError):
    """Malformed LHE/HepMC event record."""


class ReconstructionError(QISError):
    """No physically acceptable reconstruction solution."""
