"""
    This module contains readers for required datafile formats

"""

import pathlib
import pandas as pd
import logging

logger = logging.getLogger()


def read_layer_data(data_path: pathlib.Path) -> pd.DataFrame:
    """
        Reads the input layer data file. At the moment we support csv format. Other formats
        may be supported in the future.

        The file must contain the following columns:
            id -
            h -
            z2 -
            z1 -
            c -
            phi_0 -

        The rows contain information for the layers in the model

        :params data_path: Path to the input data file
        :type data_path: pathlib.Path

        :return data: Pandas DataFrame with the data table
        :rtype data: pd.DataFrame

    """

    required_columns: list = ["id", "h", "z2", "z1", "c", "phi_0"]

    if data_path.exists():
        if data_path.suffix == '.csv':
            logger.info(f"Reading data from {data_path}")
            data_df = pd.read_csv(data_path)
        else:
            msg = f"The file format {data_path.suffix} is not supported"
            logger.error(msg)
            raise ValueError(msg)
    else:
        msg = "Input data file not found."
        logger.error(msg)
        raise FileNotFoundError(msg)

    # TODO: Check for the required cols
    if sorted(data_df.columns) == sorted(required_columns):
        logger.info(f"Input data has the right format: {data_df.columns}")
    else:
        msg = f"The columns {required_columns} are not present in the input data file"
        logger.error(msg)
        raise ValueError(msg)

    return data_df
