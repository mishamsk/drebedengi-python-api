# Usage

To use Drebedengi Python API in a project

```py
from drebedengi import DrebedengiAPI
from drebedengi.model import TransactionType

api = DrebedengiAPI(
        api_key=api_key,
        login=login,
        password=password,
    )

print(api.get_transactions(include_types=TransactionType.TRANSFER)[0])
```
