# RedMess
__version__ = "1.0.0"
__author__ = "harezadmm"
__license__ = "MIT"
__description__ = "RedMess BRUTAL MOD - Unrestricted Offensive Security AI"
__url__ = "https://github.com/harezadmm/RedMess"

# Export main components
from .core import RedMessAgent
from .skills import SecuritySkills
from .utils import Logger

__all__ = [
    "RedMessAgent",
    "SecuritySkills", 
    "Logger",
    "__version__",
]
