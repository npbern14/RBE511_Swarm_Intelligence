from oscillators import CellAgent , CellGrid
import argparse


if __name__ == "__main__":
	Cell_Experiment = CellGrid(rows=10,
							   columns= 10,
							   sim_steps=3000,
							   k = 0.1,
								   )
	Cell_Experiment.populate_grid()
	Cell_Experiment.simulation_run()

