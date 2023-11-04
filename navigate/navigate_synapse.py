from typing import Any

import synapse
from synapse.module_api import ModuleApi, cached

import navigate

ADMIN_ID = "ADMIN"


class Navigate:
    def __init__(self, config: Any, api: ModuleApi):
        self.api = api
        api.register_password_auth_provider_callbacks(
            # TODO
            auth_checkers={("m.login.registration_token", ("token")): self.check_auth}
        )
        api.register_account_validity_callbacks(
            on_user_registration=self.on_user_registration
        )

        api.register_user(ADMIN_ID, admin=True)

    async def check_auth(
        self,
        username: str,
        login_type: str,
        login_dict: "synapse.module_api.JsonDict",
    ):
        if login_type != "registration_token":
            return None

        token = login_dict.get("token")
        if token is None:
            return None

        # get classes, return None if token is invalid
        # TODO: use self.http_client
        classes = navigate.classes(token)
        if classes is None:
            return None

        user_id = self.api.get_qualified_user_id(username)
        self.api.put_global(user_id, "Classes", classes)

        return (user_id, None)

    def on_user_registration(self, username: str):
        user_id = self.api.get_qualified_user_id(username)
        classes = self.api.get_global(user_id, "Classes")

        for info in classes:
            # TODO create class for general class names, not just ids
            room_id = self.api.lookup_room_alias(info.class_id)
            if room_id is not None:
                room_id = self.api.create_room(
                    ADMIN_ID,
                    username,
                    {
                        "name": info.room,
                        "preset": "trusted_private_chat",  # TODO: or regular private?
                        "room_alias_name": info.id,
                        # "visibility": "private", # default
                    },
                )

            self.api.update_room_membership(
                ADMIN_ID, username, room_id, "m.room.member"
            )

    def is_user_expired(self, username: str):
        # TODO: verify user token still works
        pass
