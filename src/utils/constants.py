# import third-party libraries
from argon2 import (
    PasswordHasher, 
    Type as Argon2Type,
)

# import Python's standard libraries
import pathlib

DEBUG_MODE = True
APP_ROOT_PATH = pathlib.Path(__file__).parent.parent.resolve()
STATIC_PATH = APP_ROOT_PATH.joinpath("static")
FAVICON_PATH = STATIC_PATH.joinpath("favicon.ico")

PASSWORD_HASHER = PasswordHasher(
    encoding="utf-8",
    time_cost=4,         # 4 count of iterations
    salt_len=64,         # 64 bytes salt
    hash_len=64,         # 64 bytes hash
    parallelism=4,       # 4 threads
    memory_cost=64*1024, # 64MiB
    type=Argon2Type.ID   # using hybrids of Argon2i and Argon2d
)

# Application constants
DOMAIN = "https://localhost:8080" if DEBUG_MODE else "https://deployed.live"
FLASH_MESSAGES = "_messages"
SESSION_COOKIE = "session"
