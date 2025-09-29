from ..model.user import UserInDb
from src.errors import Duplicate

fake_users_db = {
   "steve": {
        "username": "steve",
        "email": "stv.mnr@gmail.com",
        "full_name": "steve minor",
        "disabled": False,
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$efC7Uca0zSdR/d16l7wenA$cBlA2vxc/nYqlm4qKMCn2tnJBmMBgq/YdBon8SZ7J5k"
        }
}

def add_user(username, full_name, email, hashed_password):
    if username in fake_users_db:
        raise Duplicate("Username already exists")
    fake_users_db[username] = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_password,
        "disabled": False
    } 
    return get_user(username)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDb(**user_dict).model_dump()