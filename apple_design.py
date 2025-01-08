fig, ax = plt.subplots(figsize=(6, 6))

#Apple design
apple_x, apple_y = 5.5, 5.5  # Center position of the apple
apple = patches.Circle((apple_x, apple_y), 0.4, color="crimson", zorder=2)
ax.add_patch(apple)

#Gloss
highlight = patches.Ellipse((apple_x + 0.1, apple_y + 0.2), 0.2, 0.1, color="white", alpha=0.6, zorder=3)
ax.add_patch(highlight)

#Shadow
shadow = patches.Ellipse((apple_x, apple_y - 0.3), 0.6, 0.15, color="black", alpha=0.3, zorder=1)
ax.add_patch(shadow)

#Leaf
leaf_x, leaf_y = apple_x + 0.2, apple_y + 0.3
leaf = patches.Polygon([[leaf_x, leaf_y], [leaf_x - 0.1, leaf_y + 0.2], [leaf_x + 0.2, leaf_y + 0.1]], color="forestgreen")
ax.add_patch(leaf)

#Stem
stem_x, stem_y = apple_x, apple_y + 0.4
ax.plot([stem_x, stem_x], [stem_y, stem_y + 0.2], color="saddlebrown", linewidth=2, zorder=3)

ax.set_xlim(0, grid_size)
ax.set_ylim(0, grid_size)
ax.set_xticks(np.arange(0, grid_size, 1))
ax.set_yticks(np.arange(0, grid_size, 1))
ax.grid(color='black', linestyle='--', linewidth=0.5)
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_aspect('equal', 'box')

plt.title("Realistic Apple Design with Gloss and Shadow", fontsize=16)
plt.show()
