import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation, PillowWriter
import os

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
		# Store grid history for animation
		self.grid_history = [self.grid.copy()]
		self.t = 0

		while self.t < self.sim_steps:
			moved_any_agent = self.satisfy_grid()
			'''
			if moved_any_agent == False:
				break
			'''
		self.render_grid()
		return

	def satisfy_grid(self):
	#check the satisfaction of all agents by looping through the grid. If not satisfied, move agent to the closest position that leads to satisfaction then check next agent
		moved_any_agent = False

		for i in range(self.rows):
			for j in range(self.columns):

				if self.grid[i, j] != 0 and self.check_if_satisfied(i, j) == False:
					satisfied_space = self.find_satisfied_space(i, j)

					if satisfied_space is not None:
						new_row = satisfied_space[0]
						new_col = satisfied_space[1]

						agent_moved = self.move_agent(i, j, new_row, new_col)

						if agent_moved:
							self.t += 1
							self.grid_history.append(self.grid.copy())
							moved_any_agent = True

							if self.t >= self.sim_steps:
								return moved_any_agent

		return moved_any_agent

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

	def render_grid(self):
		# Save animation of the grid history as a GIF

		os.makedirs("output", exist_ok=True)

		colors = ["white", "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
		cmap = ListedColormap(colors[:self.num_groups + 1])

		fig, ax = plt.subplots()

		grid_image = ax.imshow(
			self.grid_history[0],
			cmap=cmap,
			vmin=0,
			vmax=self.num_groups
		)

		ax.set_title("Schelling Model")

		ax.set_xticks(np.arange(-0.5, self.columns, 1), minor=True)
		ax.set_yticks(np.arange(-0.5, self.rows, 1), minor=True)
		ax.grid(which="minor", color="black", linestyle="-", linewidth=0.2)

		ax.tick_params(
			which="both",
			bottom=False,
			left=False,
			labelbottom=False,
			labelleft=False
		)
		P = str(self.fill_percent)
		t = str(self.satisfaction_threshold)

		time_text = ax.text(
			0.5,
			-0.08,
			f"P = {P} , t = {t}, step = 0",
			transform=ax.transAxes,
			ha="center",
			va="top",
			fontsize=12
		)

		plt.subplots_adjust(bottom=0.15)

		def update(frame):
			grid_image.set_data(self.grid_history[frame])
			time_text.set_text(f"P = {P} , t = {t}, step = {frame}")
			return grid_image, time_text

		anim = FuncAnimation(
			fig,
			update,
			frames=len(self.grid_history),
			interval=200,
			blit=False
		)

		anim.save("output/schelling.gif", writer=PillowWriter(fps=50))

		plt.close(fig)

		print("Saved animation to output/schelling.gif")

		return

