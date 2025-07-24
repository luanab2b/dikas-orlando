# utils/logger.py
import logging
import json
from typing import Any

import logging
import json
from typing import Any

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Cria o logger
logger = logging.getLogger('dikas-orlando')

def to_json_dump(data: Any) -> str:
    try:
        return json.dumps(data, indent=2, default=str)
    except:
        return str(data)