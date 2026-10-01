"""
    Main decompaction script

"""

import logging

import numpy as np
import pandas as pd
from io import StringIO

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def main(data_df: pd.DataFrame):
    """
        Main script to run the layer decompaction
        
    """
    
    # =============================== FOR USER ============================== #
    logging.basicConfig(filename='decopro.log', level=logging.DEBUG)

    # ================================  Workflow ============================= #

    # TODO: Datum correction
    # subtract datum to z1 and z2, if not specified, defaults to 0

    z2_solutions: list = []
    solved_layers: list = []
    layer_porosity_dict: dict = dict()
    layer_name_dict: dict = dict()
    stage_dict: dict = dict()
    for i, layer in enumerate(data_df.iterrows()):
        logger.info(f"Solving for Stage {i + 1}")

        # Get my current layer
        current_layer = layer[1]
        stage_dict[f"stage_{i + 1}"] = []
        layer_porosity_dict[f"stage_{i + 1}"] = []
        layer_name_dict[f"stage_{i + 1}"] = []
        
        logger.debug("==================")
        logger.debug(f"stage_{i + 1}")  
        logger.debug(f"Current Layer is {current_layer.id}")
        logger.debug(current_layer)
        logger.debug("==================")

        # Solve for z2 prime (current layer)
        z2_prime = solve_layer(
            my_layer=current_layer, 
            z1_prime=0
            )
        z2_solutions.append(z2_prime)

        # Solve for average porosity (current layer)
        phi = average_layer_porosity(
            z1_prime=0, 
            z2_prime=z2_prime, 
            phi_0=current_layer.phi_0, 
            c=current_layer.c
        )
        layer_porosity_dict[f"stage_{i + 1}"].append(phi)

        # Storing layer name
        layer_name_dict[f"stage_{i + 1}"].append(current_layer.id)
        
        # update stage dictionary
        stage_dict[f"stage_{i + 1}"].append(z2_prime)
        
        # Go and solve update for previous layers, if any    
        if solved_layers:
            idx = np.arange(1, len(z2_solutions))[::-1]
            # Solve progress of previously computed layers
            prev_sol = z2_solutions[-1]
            for j in idx:   
                logger.info(f"Now solving for {solved_layers[j - 1].id}")
                # print(j, len(z2_solutions) - 1)    
                if j == len(z2_solutions) - 1:
                    
                    # Solve for z2 prime (past layers)
                    new_z2_prime = solve_layer(
                        my_layer=solved_layers[j - 1], 
                        z1_prime=prev_sol
                        )

                        # Solve for porosity (past layers)
                    new_phi = average_layer_porosity(
                        z1_prime=prev_sol, 
                        z2_prime=new_z2_prime, 
                        phi_0=solved_layers[j - 1].phi_0, 
                        c=solved_layers[j - 1].c
                    )

                else:
                    temp = new_z2_prime

                    # Solve for z2 prime (past layers)
                    # This re assigment of new_z2_prime is critical. becomes the one for nex iter
                    new_z2_prime = solve_layer(
                        my_layer=solved_layers[j - 1], 
                        z1_prime=temp
                        )

                    # Solve for porosity (past layers)
                    new_phi = average_layer_porosity(
                        z1_prime=temp, 
                        z2_prime=new_z2_prime, 
                        phi_0=solved_layers[j - 1].phi_0, 
                        c=solved_layers[j - 1].c
                    )

                # Storing layer name
                layer_name_dict[f"stage_{i + 1}"].append(solved_layers[j - 1].id)

                stage_dict[f"stage_{i + 1}"].append(new_z2_prime)
                layer_porosity_dict[f"stage_{i + 1}"].append(new_phi)
    
        # Add solution of current layer to list
        solved_layers.append(current_layer)
    

    # Print results.
    digs = 5  # Digits to show. may need to be adjusted?
    out = StringIO()
    for key in stage_dict.keys():
        print('====================', file=out)
        print(" ".join(key.split("_")).upper(), file=out)
        for k, lay in enumerate(stage_dict[key]):
            print(
                f"layer {layer_name_dict[key][k]} base: {np.round(lay, digs)} km", file=out
            )
            print(
                f"layer {layer_name_dict[key][k]} average porosity: {np.round(layer_porosity_dict[key][k], digs)}",
                file=out
            )
        print('====================', file=out)
        print('\n', file=out)
    text_output = out.getvalue()
    return text_output

def func(zi, zj, phi_0, c):
    """
        A function to compact term of the main equation for readability
        
    """
    return (phi_0 / c) * (np.exp(- c * zi) - np.exp(- c * zj))
    

def iterative_solver(
    lower_bound: float | int,
    z2: float | int,
    z1: float | int,
    z1_prime: float | int,
    phi_0: float | int,
    c: float | int
) -> float:
    """
        This function solves iteratively for the past layer base z2_prime: New depth of Z_2 after the
        sediments above the layer have been removed (km).
        solves this eq. [A56.7] from Allen & Allen (2013)
            
        z2_prime = (z2 - z1) - func(z1, z2, phi_0, c) + func(z1_prime, z2_prime, phi_0, c) + z1_prime

        :param lower_bound: The lower bound taken as initial guess for the iterations
        :type lower_bound: float | int
        :param z2: Present-day depth to the base of the sedimentary layer (km).
        :type z2: float
        :param z1: Present-day depth to the top of the sedimentary layer (km).
        :type z1: float
        :param z1_prime: New depth of Z_1 after the sediments above the layer have been removed (km).
        :type z1_prime: float
        :param phi_0: Initial (surface) porosity of the sediment. It is a constant that depends on the lithology.
        :type phi_0: float
        :param c: Porosity–depth coefficient km-1. It is a constant that depends on the lithology and controls the
            rate at which porosity decreases with increasing burial depth.
        :type c: float

        :return: Guess for depth of Z_2 after the sediments above the layer have been removed (km).
        :rtype: float

    """
    
    delta = 1e-4  # km - if you need more refinement may need to be adjusted?
    z2_prime_guess = lower_bound
    while True:
        z2_prime = (z2 - z1) - func(z1, z2, phi_0, c) + func(z1_prime, z2_prime_guess, phi_0, c) + z1_prime
        if z2_prime < z2_prime_guess:
            break
        else:
            z2_prime_guess = z2_prime_guess + delta
            
    return float(z2_prime_guess)


def solve_layer(my_layer, z1_prime: float | int):
    """
        Solver z2_prime for a layer: New depth of Z_2 after the sediments above the layer have been removed (km).

        :param z1_prime: New depth of Z_1 after the sediments above the layer have been removed (km).
        :type z1_prime: float
        :my_layer: that contains parameters that define a given layer
        :type my_layer:

    """
    
    # Solving equation iteratively
    h = my_layer.z2 - my_layer.z1
    z2_prime = iterative_solver(
        lower_bound=h, 
        z2=my_layer.z2, 
        z1=my_layer.z1, 
        z1_prime=z1_prime, 
        phi_0=my_layer.phi_0, 
        c=my_layer.c
    )
    return z2_prime


def average_layer_porosity(z1_prime, z2_prime, phi_0, c):
    """
        An equation to calculate the average porosity of a given layer at any depth.
        Base on eq. A56.8 of "Basin analysis principles"

        calculates the average porosity of a sedimentary layer at a given burial depth.
        It describes how porosity progressively decreases through time as the sediment is buried and compacted
        due to the increasing load of overlying sediments, from the time of deposition to the present day.

        :param z2_prime: New depth of Z_2 after the sediments above the layer have been removed (km).
        :type z2_prime: float
        :param z1_prime: New depth of Z_1 after the sediments above the layer have been removed (km).
        :type z1_prime: float
        :param phi_0: Initial (surface) porosity of the sediment. It is a constant that depends on the lithology.
        :type phi_0: float
        :param c: Porosity–depth coefficient km-1. It is a constant that depends on the lithology and controls the
            rate at which porosity decreases with increasing burial depth.
        :type c: float


    """
    logger.debug("z1p:", z1_prime, "z2p:", z2_prime, "phi0:", phi_0, "c:", c)
    phi = (phi_0 / c) * (np.exp(-c * z1_prime) - np.exp(-c * z2_prime)) / (z2_prime - z1_prime)
    logger.debug("Average phi result:", phi)
    if np.isnan(phi):
        logger.error("z1p:", z1_prime, "z2p:", z2_prime, "phi0:", phi_0, "c:", c)
        raise ValueError("The values look weird, check your inputs!!!")
    return phi
 