from typing import Any, Dict, Optional, Tuple, Union

import ConfigSpace as CS
from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace.hyperparameters import (
    CategoricalHyperparameter,
    UniformFloatHyperparameter,
)

import imgaug.augmenters as iaa
from imgaug.augmenters.meta import Augmenter

import numpy as np

from autoPyTorch.pipeline.components.setup.augmentation.image.base_image_augmenter import BaseImageAugmenter
from autoPyTorch.utils.common import HyperparameterSearchSpace, add_hyperparameter, get_hyperparameter


class GaussianBlur(BaseImageAugmenter):
    def __init__(self, use_augmenter: bool = True, sigma_min: float = 0, sigma_offset: float = 0.5,
                 random_state: Optional[Union[int, np.random.RandomState]] = None):
        super().__init__(use_augmenter=use_augmenter)
        self.random_state = random_state
        self.sigma = (sigma_min, sigma_min + sigma_offset)

    def fit(self, X: Dict[str, Any], y: Any = None) -> BaseImageAugmenter:
        if self.use_augmenter:
            self.augmenter: Augmenter = iaa.GaussianBlur(sigma=self.sigma, name=self.get_properties()['name'])

        return self

    @staticmethod
    def get_hyperparameter_search_space(
        dataset_properties: Optional[Dict[str, str]] = None,
        use_augmenter: HyperparameterSearchSpace = HyperparameterSearchSpace(hyperparameter="use_augmenter",
                                                                             value_range=(True, False),
                                                                             default_value=True,
                                                                             log=False),
        sigma_min: HyperparameterSearchSpace = HyperparameterSearchSpace(hyperparameter="sigma_min",
                                                                         value_range=(0, 3),
                                                                         default_value=0,
                                                                         log=False),
        sigma_offset: HyperparameterSearchSpace = HyperparameterSearchSpace(hyperparameter="sigma_min",
                                                                            value_range=(0.0, 3.0),
                                                                            default_value=0.5,
                                                                            log=False),
    ) -> ConfigurationSpace:
        cs = ConfigurationSpace()
        use_augmenter = get_hyperparameter(use_augmenter, CategoricalHyperparameter)
        sigma_min = get_hyperparameter(sigma_min, UniformFloatHyperparameter)
        sigma_offset = get_hyperparameter(sigma_offset, UniformFloatHyperparameter)
        cs.add_hyperparameters([use_augmenter, sigma_min, sigma_offset])
        # only add hyperparameters to configuration space if we are using the augmenter
        cs.add_condition(CS.EqualsCondition(sigma_min, use_augmenter, True))
        cs.add_condition(CS.EqualsCondition(sigma_offset, use_augmenter, True))

        return cs

    @staticmethod
    def get_properties(dataset_properties: Optional[Dict[str, str]] = None
                       ) -> Dict[str, Any]:
        return {'name': 'GaussianBlur'}
