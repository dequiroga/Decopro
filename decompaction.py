"""
    This is a tiny little code to calculate decompaction :)

"""

import logging

import numpy as np
import pandas as pd
import pathlib

# logger = logging.getLogger(__name__)

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

# fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
# fileHandler.setFormatter(logFormatter)
# logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def main():
    """
        Main script to run the layer decompaction
        
    """
    
    # =============================== FOR USER ============================== # 

    # root_path = r"D:\DATA\2nd paper_Chapter 2_sediment_supply_volcanic\Bibliography sediment supply\Decompaction"
    # file_name = "data_table.csv"

    logging.basicConfig(filename='decopro.log', level=logging.DEBUG)

    # ================================ SOFWTARE ============================= #
    
    # root_path = pathlib.Path(root_path)
    while True:
        input_path = input('Please type the data csv path: ')
        data_path = pathlib.Path(input_path.strip('"').strip("'"))
        logger.info(data_path)
        if data_path.exists():
            break
        else:
            logger.error("Input path not valid... Try again")
            
        #root_path.joinpath(file_name)
    data = pd.read_csv(data_path)

    # TODO: Datum correction
    # subtract datum to z1 and z2, if not specified, defaults to 0

    z2_solutions: list = []
    solved_layers: list = []
    layer_porosity_dict: dict = dict()
    layer_name_dict: dict = dict()
    stage_dict: dict = dict()
    for i, layer in enumerate(data.iterrows()):
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
                    temp = new_z2_prime  # THIS IS A HACK

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
    

    # Show results. TODO: clean this
    digs = 5
    for key in stage_dict.keys():
        print('====================')
        print(" ".join(key.split("_")).upper())
        for k, lay in enumerate(stage_dict[key]):
            print(f"layer {layer_name_dict[key][k]} base: {np.round(lay, digs)} km")
            print(f"layer {layer_name_dict[key][k]} average porosity: {np.round(layer_porosity_dict[key][k], digs)}")
        print('====================')
        print('\n')


def func(zi, zj, phi_0, c):
    """
        A function to compact a term of the main equation for readability
        
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
        This function solves iteratively for the past layer base z2_prime
    
        solves this equation:
            
        z2_prime = (z2 - z1) - func(z1, z2, phi_0, c) + func(z1_prime, z2_prime, phi_0, c) + z1_prime

        TODO: eq. x from __ cite

        :param lower_bound: The
        :type lower_bound: float | int
        :param z2:
        :type z2:
        :param z1:
        :type z1:
        :param z1_prime:
        :type z1_prime:
        :param phi_0:
        :type phi_0:
        :param c:
        :type c:

        :return: Guess for ...
        :rtype: float

    """
    
    delta = 1e-4  # km
    z2_prime_guess = lower_bound
    while True:
        z2_prime = (z2 - z1) - func(z1, z2, phi_0, c) + func(z1_prime, z2_prime_guess, phi_0, c) + z1_prime
        if z2_prime < z2_prime_guess:
            break
        else:
            z2_prime_guess = z2_prime_guess + delta
            
    return float(z2_prime_guess)


def solve_layer(my_layer, z1_prime):
    """
        Solver z2_prime for a layer
        
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
        Base on eq. A56.8 of "Basin analysis priciples..."


    """
    logger.debug("z1p:", z1_prime, "z2p:", z2_prime, "phi0:", phi_0, "c:", c)
    phi = (phi_0 / c) * (np.exp(-c * z1_prime) - np.exp(-c * z2_prime)) / (z2_prime - z1_prime)
    logger.debug("Average phi result:", phi)
    if np.isnan(phi):
        logger.error("z1p:", z1_prime, "z2p:", z2_prime, "phi0:", phi_0, "c:", c)
        raise ValueError("The values look weird, check your inputs!!!")
    return phi




if __name__ == "__main__":
    main()


 