import logging
import random
import sys
from typing import Any, Dict, cast

from synapse.api.errors import SynapseError
from synapse.module_api import JsonDict, ModuleApi

from . import navigate

ADMIN_NAME = "admin"

logger = logging.getLogger("navigate")


class Navigate:
    def __init__(self, config: Any, api: ModuleApi):
        self.api = api

        # TODO: it would be ideal to use global data functions
        self.username_to_token = {}  # TODO: needs to be persistent

        api.register_password_auth_provider_callbacks(
            auth_checkers={
                ("m.login.password", ("password",)): self.check_auth,
            },
            get_username_for_registration=self.get_username_for_registration,
        )

        # api.register_account_validity_callbacks(
        # on_user_registration=self.on_user_registration
        # )

        self.admin_id = self.api.get_qualified_user_id("nicky")

    async def check_auth(
        self,
        username: str,
        login_type: str,
        login_dict: JsonDict,
    ):
        if login_type != "m.login.password":
            return None

        user_id = self.api.get_qualified_user_id(username)
        # credentials = (
        # await self.api.account_data_manager.get_global(user_id, "credentials"),
        # )

        # get classes, return None if password is invalid
        classes = await navigate.classes(
            self.api.http_client, self.username_to_token[username]
        )
        if classes is None:
            return None

        # TODO: improve

        # await self.api.account_data_manager.put_global(
        # user_id, "access", {"classes": classes}
        # )

        for info in classes:
            # TODO create class for general class names, not just ids
            try:
                room_id = (
                    await self.api.lookup_room_alias(f"#{info.id}:localhost:8080")
                )[0]
            except SynapseError:
                room_id = (
                    await self.api.create_room(
                        self.admin_id,
                        {
                            "name": f"{info.name} ({info.section}) - {info.title}",
                            "topic": info.description,
                            "preset": "private_chat",  # TODO: or regular private?
                            "room_alias_name": info.id,
                            # "visibility": "private", # default
                        },
                    )
                )[0]

            await self.api.update_room_membership(
                self.admin_id, user_id, room_id, "invite"
            )

        return (user_id, None)

    async def get_username_for_registration(
        self,
        uia_results: Dict[str, Any],
        params: Dict[str, Any],
    ):
        # TODO: improve randomness
        username = "user" + str(random.randint(0, sys.maxsize))

        user_id = self.api.get_qualified_user_id(username)
        self.username_to_token[user_id] = params["username"]

        # await self.api.account_data_manager.put_global(
        #     user_id, "credentials", {"token": params["username"]}
        # )

        # names cannot be only ids, otherwise error
        return username

    async def is_user_expired(self, username: str):
        # TODO: verify user token still works
        pass
