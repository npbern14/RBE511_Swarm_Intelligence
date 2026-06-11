from schelling import SchellGrid
import argparse


if __name__ == "__main__":
	Schell_Experiment = SchellGrid(rows=100,
								   columns=100,
								   fill_percent=0.4,
								   satisfaction_threshold=3,
								   sim_steps=100,
								   num_groups=2,
								   )
	Schell_Experiment.populate_grid()
	Schell_Experiment.simulation_run()

