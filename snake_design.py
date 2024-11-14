#imports
import matplotlib.pyplot as plt
import numpy as np

# Set up the grid
grid_size = 10
snake_length = 5
grid = np.zeros((grid_size, grid_size))

# Initialize snake's position
snake_position = [(i, 5) for i in range(snake_length)]

# Plot the snake with a distinct head
plt.figure(figsize=(5, 5))

# Draw the snake's body
for pos in snake_position[1:]:
    plt.plot(pos[0] + 0.5, pos[1] + 0.5, 's', color="green", markersize=30)

# Draw the snake's head
head_position = snake_position[0]
plt.plot(head_position[0] + 0.5, head_position[1] + 0.5, 'o', color="darkgreen", markersize=35)

# Customizing the grid appearance
plt.xlim(0, grid_size)
plt.ylim(0, grid_size)
plt.gca().set_xticks(np.arange(0, grid_size, 1))
plt.gca().set_yticks(np.arange(0, grid_size, 1))
plt.grid(color='black')
plt.gca().set_xticklabels([])
plt.gca().set_yticklabels([])

plt.title("Snake Game Design with Snake Head", fontsize=16)
plt.show()