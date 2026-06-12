from schelling import SchellGrid
import argparse


if __name__ == "__main__":
	Schell_Experiment = SchellGrid(rows=50,
								   columns= 50,
								   fill_percent=0.6,
								   satisfaction_threshold=4,
								   sim_steps=3000,
								   num_groups=3,
								   )
	Schell_Experiment.populate_grid()
	Schell_Experiment.simulation_run()

