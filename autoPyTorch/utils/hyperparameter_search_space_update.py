import ast
import os
from typing import List, Optional, Tuple, Union

from autoPyTorch.pipeline.components.base_choice import autoPyTorchChoice
from autoPyTorch.pipeline.components.base_component import autoPyTorchComponent


class HyperparameterSearchSpaceUpdate:
    """
    Allows specifying update to the search space of a
    particular hyperparameter.

    Args:
        node_name (str):
            The name of the node in the pipeline
        hyperparameter (str):
            The name of the hyperparameter
        value_range (Union[List, Tuple]):
            In case of categorical hyperparameter, defines the new categorical choices.
            In case of numerical hyperparameter, defines the new range
            in the form of (LOWER, UPPER)
        default_value (Union[int, float, str]):
            New default value for the hyperparameter
        log (bool) (default=False):
            In case of numerical hyperparameters, whether to sample on a log scale
    """
    def __init__(self, node_name: str, hyperparameter: str, value_range: Union[List, Tuple],
                 default_value: Union[int, float, str], log: bool = False) -> None:
        self.node_name = node_name
        self.hyperparameter = hyperparameter
        self.value_range = value_range
        self.log = log
        self.default_value = default_value

    def apply(self, pipeline: List[Tuple[str, Union[autoPyTorchComponent, autoPyTorchChoice]]]) -> None:
        """
        Applies the update to the appropriate hyperparameter of the pipeline
        Args:
            pipeline (List[Tuple[str, Union[autoPyTorchComponent, autoPyTorchChoice]]]):
                The named steps of the current autopytorch pipeline
        Returns:
            None
        """
        [node[1]._apply_search_space_update(name=self.hyperparameter,
                                            new_value_range=self.value_range,
                                            log=self.log,
                                            default_value=self.default_value)
         for node in pipeline if node[0] == self.node_name]

    def __str__(self) -> str:
        return "{}, {}, {}, {}, {}".format(self.node_name, self.hyperparameter, str(self.value_range),
                                           self.default_value if isinstance(self.default_value,
                                                                            str) else self.default_value,
                                           (" log" if self.log else ""))


class HyperparameterSearchSpaceUpdates:
    """
    Contains a collection of HyperparameterSearchSpaceUpdate
    """
    def __init__(self, updates: Optional[List[HyperparameterSearchSpaceUpdate]] = None) -> None:
        self.updates = updates if updates is not None else []

    def apply(self, pipeline: List[Tuple[str, Union[autoPyTorchComponent, autoPyTorchChoice]]]) -> None:
        """
        Iteratively applies updates to the pipeline
        Args:
            pipeline: (List[Tuple[str, Union[autoPyTorchComponent, autoPyTorchChoice]]]):
                The named steps of the current autopytorch pipeline
        Returns:
            None
        """
        for update in self.updates:
            update.apply(pipeline)

    def append(self, node_name: str, hyperparameter: str, value_range: Union[List, Tuple],
               default_value: Union[int, float, str], log: bool = False) -> None:
        """
        Add a new update
        Args:
            node_name (str):
            The name of the node in the pipeline
        hyperparameter (str):
            The name of the hyperparameter
        value_range (Union[List, Tuple]):
            In case of categorical hyperparameter, defines the new categorical choices.
            In case of numerical hyperparameter, defines the new range
            in the form of (LOWER, UPPER)
        default_value (Union[int, float, str]):
            New default value for the hyperparameter
        log (bool) (default=False):
            In case of numerical hyperparameters, whether to sample on a log scale

        Returns:
            None
        """
        self.updates.append(HyperparameterSearchSpaceUpdate(node_name=node_name,
                                                            hyperparameter=hyperparameter,
                                                            value_range=value_range,
                                                            default_value=default_value,
                                                            log=log))

    def save_as_file(self, path: str) -> None:
        """
        Save the updates as a file to reuse later
        Args:
            path (str): path of the file

        Returns:
            None
        """
        with open(path, "w") as f:
            for update in self.updates:
                print(update.node_name, update.hyperparameter,  # noqa: T001
                      str(update.value_range), "'{}'".format(update.default_value)
                      if isinstance(update.default_value, str) else update.default_value,
                      (" log" if update.log else ""), file=f)


def parse_hyperparameter_search_space_updates(updates_file: Optional[str]
                                              ) -> Optional[HyperparameterSearchSpaceUpdates]:
    if updates_file is None or os.path.basename(updates_file) == "None":
        return None
    with open(updates_file, "r") as f:
        result = []
        for line in f:
            if line.strip() == "":
                continue
            line = line.split()  # type: ignore[assignment]
            node, hyperparameter, value_range = line[0], line[1], ast.literal_eval(line[2] + line[3])
            default_value = ast.literal_eval(line[4])
            assert isinstance(value_range, (tuple, list))
            log = len(line) == 6 and "log" == line[5]
            result.append(HyperparameterSearchSpaceUpdate(node, hyperparameter, value_range, default_value, log))
    return HyperparameterSearchSpaceUpdates(result)