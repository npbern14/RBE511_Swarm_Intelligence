import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

#Store all parameters and behavior of the Schelling Segregation model
class SchellGrid:
	def __init__(self,
				 rows,
				 columns,
				 fill_percent,
				 satisfaction_threshold,
				 sim_steps,
				 num_groups,
				 **kwargs):
		self.rows = rows
		self.columns = columns
		self.fill_percent = fill_percent
		self.satisfaction_threshold = satisfaction_threshold
		self.sim_steps = sim_steps
		self.num_groups = num_groups

	def populate_grid(self):
	#populate the grid with the agents randomly
		rows_span = np.linspace(0,self.rows,self.rows)
		cols_span = np.linspace(0,self.columns,self.columns)
		rr,cc = np.meshgrid(rows_span,cols_span)

		total_cells = self.rows * self.columns


		fill_fraction = self.fill_percent

		num_occupied = int(round(fill_fraction * total_cells))
		num_empty = total_cells - num_occupied

		# Start with the empty cells
		cell_values = [0] * num_empty

		# Split occupied cells as evenly as possible among groups
		agents_per_group = num_occupied // self.num_groups
		leftover_agents = num_occupied % self.num_groups

		for group_id in range(1, self.num_groups + 1):
			num_agents = agents_per_group

			# if num_occupied is not perfectly divisible, give extras to early groups
			if group_id <= leftover_agents:
				num_agents += 1

			cell_values += [group_id] * num_agents

		# Randomize cell locations
		cell_values = np.array(cell_values)
		np.random.shuffle(cell_values)

		# Store the populated grid
		self.grid = cell_values.reshape((self.rows, self.columns))
		#print(f"Grid:\n{np.array2string(self.grid, separator=' ')}")

		return self.grid

	def simulation_run(self):
	#call satisfy grid, then render the grid for each time step. Repeat until max sim timesteps is reached
		t = 0

		while t <= self.sim_steps:
			self.satisfy_grid()
			self.render_grid(t)
			t += 1

		plt.show()
		return

	def satisfy_grid(self):
	#check the satisfaction of all agents by looping through the grid. If not satisfied, move agent to the closest position that leads to satisfaction then check next agent
		for i in range(self.rows):
			for j in range(self.columns):

				if self.grid[i, j] != 0 and self.check_if_satisfied(i, j) == False:
					satisfied_space = self.find_satisfied_space(i, j)

					if satisfied_space is not None:
						new_row = satisfied_space[0]
						new_col = satisfied_space[1]

						self.move_agent(i, j, new_row, new_col)

		return

	def check_if_satisfied(self, row, col, agent_type=None):
	#check if the cell is surrounded by a number of cells of the same type equal to the tolerance defined for the SchellGrid class
		d = 1

		# If no agent_type is provided, use the value already stored in the grid
		if agent_type is None:
			agent_type = self.grid[row, col]

		# Empty cells are never satisfied
		if agent_type == 0:
			return False

		row_min = max(0, row - d)
		row_max = min(self.rows, row + d + 1)

		col_min = max(0, col - d)
		col_max = min(self.columns, col + d + 1)

		match = 0

		for neighbor_row in range(row_min, row_max):
			for neighbor_col in range(col_min, col_max):

				# Skip the center cell itself
				if neighbor_row == row and neighbor_col == col:
					continue

				if self.grid[neighbor_row, neighbor_col] == agent_type:
					match += 1

		return match >= self.satisfaction_threshold

	def find_satisfied_space(self, row, col):
	#find the closest position that leads to the satisfaction of the agent using square shaped breadth first search
		#get the surrounding 8 cells of the cell in question, then expand the square of cells if no satisfying point is found
		agent_type = self.grid[row, col]

		# Empty cells do not need a satisfying space
		if agent_type == 0:
			return None

		max_distance = max(self.rows, self.columns)

		for d in range(1, max_distance + 1):
			row_min = max(0, row - d)
			row_max = min(self.rows, row + d + 1)

			col_min = max(0, col - d)
			col_max = min(self.columns, col + d + 1)

			surrounding_cells = self.grid[row_min:row_max, col_min:col_max]

			num_rows = surrounding_cells.shape[0]
			num_cols = surrounding_cells.shape[1]

			for local_row in range(num_rows):
				for local_col in range(num_cols):

					# only check border cells of the current search square
					if (
						local_row == 0 or
						local_row == num_rows - 1 or
						local_col == 0 or
						local_col == num_cols - 1
					):
						global_row = row_min + local_row
						global_col = col_min + local_col

						# Candidate space must be empty
						if self.grid[global_row, global_col] != 0:
							continue

						# Check whether the agent would be satisfied at this empty location
						if self.check_if_satisfied(global_row, global_col, agent_type):
							return (global_row, global_col)

		# no satisfying empty space found
		return None

	def move_agent(self, old_row, old_col, new_row, new_col):
	#change the value of the old cell to 0 and move the agent to the new cell
		agent_type = self.grid[old_row, old_col]

		# do not move empty cells
		if agent_type == 0:
			return False

		# only move into empty cells
		if self.grid[new_row, new_col] != 0:
			return False

		self.grid[new_row, new_col] = agent_type
		self.grid[old_row, old_col] = 0

		return True

	def render_grid(self, t):
	#render the grid with the current positions of all agents

		# Colors:
		# 0 = empty
		# 1 = group 1
		# 2 = group 2
		colors = ["white", "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
		cmap = ListedColormap(colors[:self.num_groups + 1])

		# Create the plot only the first time this function is called
		if not hasattr(self, "fig"):
			self.fig, self.ax = plt.subplots()

			self.grid_image = self.ax.imshow(
				self.grid,
				cmap=cmap,
				vmin=0,
				vmax=self.num_groups
			)

			self.ax.set_title("Schelling Model")

			# Draw grid lines between cells
			self.ax.set_xticks(np.arange(-0.5, self.columns, 1), minor=True)
			self.ax.set_yticks(np.arange(-0.5, self.rows, 1), minor=True)
			self.ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5)

			# Hide axis labels/ticks
			self.ax.tick_params(
				which="both",
				bottom=False,
				left=False,
				labelbottom=False,
				labelleft=False
			)

			# Display timestep at bottom of plot
			self.time_text = self.ax.text(
				0.5,
				-0.08,
				f"t = {t}",
				transform=self.ax.transAxes,
				ha="center",
				va="top",
				fontsize=12
			)

			plt.subplots_adjust(bottom=0.15)
			plt.show(block=False)

		# Update the existing plot on every later call
		else:
			self.grid_image.set_data(self.grid)
			self.time_text.set_text(f"t = {t}")

		plt.pause(0.1)

		return

