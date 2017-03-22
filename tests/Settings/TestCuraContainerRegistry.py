# Copyright (c) 2017 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import os #To find the directory with test files and find the test files.
import pytest #This module contains unit tests.
import unittest.mock #To mock and monkeypatch stuff.

from cura.Settings.CuraContainerRegistry import CuraContainerRegistry #The class we're testing.
from cura.Settings.ExtruderStack import ExtruderStack #Testing for returning the correct types of stacks.
from cura.Settings.GlobalStack import GlobalStack #Testing for returning the correct types of stacks.
from UM.Resources import Resources #Mocking some functions of this.
import UM.Settings.ContainerRegistry #Making empty container stacks.
import UM.Settings.ContainerStack #Setting the container registry here properly.
from UM.Settings.DefinitionContainer import DefinitionContainer #Checking against the DefinitionContainer class.

##  Gives a fresh CuraContainerRegistry instance.
@pytest.fixture()
def container_registry():
    return CuraContainerRegistry()

##  Tests whether loading gives objects of the correct type.
@pytest.mark.parametrize("filename,                  output_class", [
                        ("ExtruderLegacy.stack.cfg", ExtruderStack),
                        ("MachineLegacy.stack.cfg",  GlobalStack),
                        ("Left.extruder.cfg",        ExtruderStack),
                        ("Global.global.cfg",        GlobalStack),
                        ("Global.stack.cfg",         GlobalStack)
])
def test_loadTypes(filename, output_class, container_registry):
    #Mock some dependencies.
    UM.Settings.ContainerStack.setContainerRegistry(container_registry)
    Resources.getAllResourcesOfType = unittest.mock.MagicMock(return_value = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "stacks", filename)]) #Return just this tested file.
    def findContainers(id, container_type = 0):
        if id == "some_instance" or id == "some_definition":
            return [UM.Settings.ContainerRegistry._EmptyInstanceContainer(id)]
        else:
            return []
    container_registry.findContainers = findContainers
    mock_definition = unittest.mock.MagicMock()
    def findContainer(container_id = "*", container_type = None, type = "*", category = None):
        return unittest.mock.MagicMock()

    with unittest.mock.patch("cura.Settings.GlobalStack.GlobalStack.findContainer", findContainer):
        with unittest.mock.patch("os.remove"):
            container_registry.load()

    #Check whether the resulting type was correct.
    stack_id = filename.split(".")[0]
    for container in container_registry._containers: #Stupid ContainerRegistry class doesn't expose any way of getting at this except by prodding the privates.
        if container.getId() == stack_id: #This is the one we're testing.
            assert type(container) == output_class
            break
    else:
        assert False #Container stack with specified ID was not loaded.
