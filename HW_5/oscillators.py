import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation, PillowWriter
import os


class CellAgent:
	def __init__(self,
				 counter,
				 T,
				 k):
		self.state = 0
		self.counter = counter
		self.T = T
		self.k = k

	def step_agent(self,neighbor_flash):
		self.counter = self.counter+1

		if(neighbor_flash == True):
			self.counter = self.counter + (self.k*self.counter)

		if(self.counter >= self.T):
			self.state =1
			self.counter =0

		else:
			self.state =0

		return


# grid of cell agents
class CellGrid:
	def __init__(self,
				 rows,
				 columns,
				 sim_steps,
				 k,
				 **kwargs):
		self.rows = rows
		self.columns = columns
		self.sim_steps = sim_steps
		self.k = k
		self.grid = np.empty((self.rows, self.columns), dtype=object)
		self.T =100

	def populate_grid(self):
	#populate the grid with the agents

		# Store the populated grid
		for i in range(self.rows):
			for j in range(self.columns):
				cell_counter = np.random.randint(0, self.T)
				self.grid[i, j] = CellAgent(cell_counter, self.T, self.k)

		return self.grid

	def simulation_run(self):
		# store grid history for animation
		initial_state = np.zeros((self.rows, self.columns))

		for i in range(self.rows):
			for j in range(self.columns):
				initial_state[i, j] = self.grid[i, j].state

		self.grid_history = [initial_state]
		self.t = 0

		while self.t < self.sim_steps:
			self.check_grid()
			self.render_grid()
		return

	def check_grid(self):
	# step through all cells in the grid and update agents

		neighbor_flash_grid = np.zeros((self.rows, self.columns), dtype=bool)

		for i in range(self.rows):
			for j in range(self.columns):
				neighbor_flash_grid[i, j] = self.check_if_flashed(i, j)

		for i in range(self.rows):
			for j in range(self.columns):
				self.grid[i, j].step_agent(neighbor_flash_grid[i, j])

		return

	def check_if_flashed(self, row, col):
	# check if north, east, south, or west neighbor has state 1

		neighbors = [
			(row - 1, col),
			(row + 1, col),
			(row, col - 1),
			(row, col + 1)
		]

		for neighbor_row, neighbor_col in neighbors:
			if neighbor_row < 0 or neighbor_row >= self.rows:
				continue

			if neighbor_col < 0 or neighbor_col >= self.columns:
				continue

			if self.grid[neighbor_row, neighbor_col].state == 1:
				return True

		return False

	def render_grid(self):
		# Convert the grid of CellAgent objects into a numeric grid of states
		current_state = np.zeros((self.rows, self.columns))

		for i in range(self.rows):
			for j in range(self.columns):
				current_state[i, j] = self.grid[i, j].state

		self.grid_history.append(current_state.copy())
		self.t += 1

		# Only save the gif after the final simulation step
		if self.t < self.sim_steps:
			return

		os.makedirs("output", exist_ok=True)

		colors = ["tab:blue", "tab:orange"]
		cmap = ListedColormap(colors)

		fig, ax = plt.subplots()

		grid_image = ax.imshow(
			self.grid_history[0],
			cmap=cmap,
			vmin=0,
			vmax=1
		)

		ax.set_title("Coupled Oscillators")

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

		time_text = ax.text(
			0.5,
			-0.08,
			"step = 0",
			transform=ax.transAxes,
			ha="center",
			va="top",
			fontsize=12
		)

		plt.subplots_adjust(bottom=0.15)

		def update(frame):
			grid_image.set_data(self.grid_history[frame])
			time_text.set_text(f"step = {frame}")
			return grid_image, time_text

		anim = FuncAnimation(
			fig,
			update,
			frames=len(self.grid_history),
			interval=200,
			blit=False
		)

		anim.save("output/cell.gif", writer=PillowWriter(fps=50))

		plt.close(fig)

		print("Saved animation to output/cell.gif")

		return

