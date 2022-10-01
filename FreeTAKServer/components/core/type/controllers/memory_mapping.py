from .mapping_interface import MappingInterface
from ..configuration.type_constants import PERSISTENCE_PATH
from digitalpy.routing.controller import Controller
import json
import os


class MemoryMapping(MappingInterface, Controller):
    def __init__(self, request, response, sync_action_mapper, configuration):
        super().__init__(
            request=request,
            response=response,
            action_mapper=sync_action_mapper,
            configuration=configuration,
        )
        self._persistence = {
            "machine_to_human_mapping": {},
            "human_to_machine_mapping": {},
        }

        # create the mapping persistence if it doesn't exist already
        if not os.path.exists(PERSISTENCE_PATH):
            with open(PERSISTENCE_PATH, mode="w+", encoding="utf-8") as f:
                json.dump(self._persistence, f)

        # load the mapping persistence into memory
        with open(PERSISTENCE_PATH, mode="r+", encoding="utf-8") as f:
            self._persistence = json.load(f)
            self.machine_to_human_mapping = self._persistence[
                "machine_to_human_mapping"
            ]
            self.human_to_machine_mapping = self._persistence[
                "human_to_machine_mapping"
            ]

    def execute(self, method=None):
        getattr(self, method)(**self.request.get_values())

    def get_machine_readable_type(self, human_readable_type, default=None, **kwargs):
        self.response.set_value(
            "machine_readable_type",
            self.human_to_machine_mapping.get(human_readable_type, default),
        )

    def get_human_readable_type(self, machine_readable_type, default=None, **kwargs):
        self.response.set_value(
            "human_readable_type",
            self.machine_to_human_mapping.get(machine_readable_type, default),
        )

    def register_machine_to_human_mapping(
        self, machine_to_human_mapping: dict, **kwargs
    ):
        self.machine_to_human_mapping.update(machine_to_human_mapping)
        self._update_persistence()

    def register_human_to_machine_mapping(
        self, human_to_machine_mapping: dict, **kwargs
    ):
        self.human_to_machine_mapping.update(human_to_machine_mapping)
        self._update_persistence()

    def _update_persistence(self):
        with open(PERSISTENCE_PATH, mode="w", encoding="utf-8") as f:
            json.dump(self._persistence, f)
