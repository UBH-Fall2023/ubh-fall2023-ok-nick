import logging
import random
import sys
from typing import Any, Dict, cast

from synapse.api.errors import SynapseError
from synapse.module_api import JsonDict, ModuleApi

import navigate

ADMIN_NAME = "admin"

logger = logging.getLogger("MY_LOGGER")
logger.info("TEST WHAT")


class Navigate:
    def __init__(self, config: Any, api: ModuleApi):
        logger.info("YES WORK")
        self.api = api
        self.class_id_to_room_id = {}  # TODO: needs to be persistent

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
        logger.info(f"TEST2 {login_type}")

        if login_type != "m.login.password":
            return None

        # get classes, return None if password is invalid
        # TODO: use self.http_client
        classes = await navigate.classes(self.api.http_client, username)
        logger.info("FINDING3")
        if classes is None:
            return None

        logger.info("FINDING2")
        # TODO: improve

        user_id = self.api.get_qualified_user_id(username)
        # await self.api.account_data_manager.put_global(
        # user_id, "access", {"classes": classes}
        # )

        logger.info("FINDING")

        for info in classes:
            # TODO create class for general class names, not just ids
            try:
                room_id = (
                    await self.api.lookup_room_alias(f"#{info.id}:localhost:8080")
                )[0]
                logger.info(f"ROOM ID: {room_id}")
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
                self.class_id_to_room_id[info.id] = room_id

            logger.info("INVITE TO ROOM")

            await self.api.update_room_membership(
                self.admin_id, user_id, room_id, "invite"
            )

        return (user_id, None)

    async def on_user_registration(self, username: str):
        logger.info("TEST4")

        user_id = self.api.get_qualified_user_id(username)
        classes = cast(
            Dict[str, list[navigate.Section]],
            await self.api.account_data_manager.get_global(user_id, "access"),
        )["classes"]

        for info in classes:
            # TODO create class for general class names, not just ids
            room_id = (await self.api.lookup_room_alias(info.id))[0]
            if room_id is not None:
                room_id = (
                    await self.api.create_room(
                        self.admin_id,
                        {
                            "name": info.name,
                            "preset": "trusted_private_chat",  # TODO: or regular private?
                            "room_alias_name": info.id,
                            # "visibility": "private", # default
                        },
                    )
                )[0]

            await self.api.update_room_membership(
                self.admin_id, username, room_id, "join"
            )

    async def get_username_for_registration(
        self,
        uia_results: Dict[str, Any],
        params: Dict[str, Any],
    ):
        # TODO: improve
        # names cannot be only ids, otherwise error
        return "user" + str(random.randint(0, sys.maxsize))

    async def is_user_expired(self, username: str):
        # TODO: verify user token still works
        pass
