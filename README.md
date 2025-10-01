# FastAPI Auth

I created this template to satisfy a requirement for basic user auth. This template implements the JWT approach outlined [here](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=jwt), but with (arguably) improved organization as well as the ability to refresh auth tokens.

This template implements a very basic placeholder user class, where the user authenticates with a username and password. The password is hashed, compared to what's in the database and, if successful,
the user is granted an access token, with a configurable expiration time. The user can get a new access token by logging in again, or making a call to `/refresh`

## Requirements

1. create a virtual environment
2. `pip install -r requirements.txt`

### Environment Variables

| Key          | Value                                            |
| ------------ | ------------------------------------------------ |
| `SECRET_KEY` | output of `openssl rand -hex 32` or similar      |
| `DB_URL`     | `sqlite:///auth.db` any db supported by sqlmodel |

## Running the Server

Run `make` or modify the dev command therein.

## Tests

`make test`
