import matplotlib.pyplot as plt
import numpy as np
from creature import emotion, creature
from io import BytesIO
from PIL import Image

# MOUTH 
# 0.1: left-down
# 0.2: sad
# 0.3: right-down
# 0.4: happy 
# ...repeat...

def generate_2d_creature(avatar:creature, filename:str, emote:emotion=None):
    eye_size=avatar.eye_size()
    num_legs=avatar.num_legs()
    leg_gap=avatar.leg_gap()
    if(emote==None):
        emote=avatar.default_emotion()
    mouth_type=emote.mouth_type()
    pupil_size=emote.pupil_size()
    if num_legs < 2:
        raise ValueError("The creature must have at least 2 legs.")

    fig, ax = plt.subplots()

    total_width = num_legs * 0.05 + (num_legs - 1) * leg_gap

    initial_x = 0.5 - total_width / 2

    body_width = total_width + 0.1
    background = plt.Rectangle((0, 0), 1, 1, color='grey', fill=True)
    body = plt.Rectangle((initial_x - 0.05, 0.2), body_width, 0.5, color='green', fill=True)
    head = plt.Circle((0.5, 0.7), 0.2, color='blue', fill=True)

    left_eye = plt.Circle((0.35, 0.8), 0.05 * eye_size, color='white', fill=True)
    right_eye = plt.Circle((0.65, 0.8), 0.05 * eye_size, color='white', fill=True)
    left_pupil = plt.Circle((0.35, 0.8), 0.05 * eye_size*pupil_size, color='black', fill=True)
    right_pupil = plt.Circle((0.65, 0.8), 0.05 * eye_size*pupil_size, color='black', fill=True)

    # Create a more interesting mouth with a curved shape
    mouth_x = np.linspace(0.4, 0.6, 100)
    mouth_y = 0.55 + 0.02 * np.sin(5 * np.pi * (mouth_x +1+mouth_type))
    plt.plot(mouth_x, mouth_y, color='red')

    leg_positions = []
    legs = []

    for i in range(num_legs):
        x = initial_x + i * (0.05 + leg_gap)
        y = 0.05
        leg_positions.append((x, y))

    for x, y in leg_positions:
        legs.append(plt.Rectangle((x, y), 0.05, 0.2, color='brown', fill=True))

    #angles = np.linspace(-arm_spread / 2, arm_spread / 2, num_arms)

    #arms = []

    #for angle in angles:
    #    x = 0.5 + 0.15 * np.cos(angle)
    #    y = 0.85 + 0.15 * np.sin(angle)
    #    arms.append(plt.Rectangle((x, y), 0.05, -0.2, angle=angle * 180 / np.pi, color='brown', fill=True))

    ax.add_patch(background)
    for leg in legs:
        ax.add_patch(leg)
    ax.add_patch(body)
    ax.add_patch(head)
    ax.add_patch(left_eye)
    ax.add_patch(right_eye)
    ax.add_patch(left_pupil)
    ax.add_patch(right_pupil)

    # No need to add the mouth as a patch, it's plotted directly
    ax.set_aspect('equal', adjustable='datalim')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    plt.show()
    #plt.savefig(filename)

avitar = creature(2, 2, 2, 0.02, emotion(0.4, 0.3))

generate_2d_creature(avitar, filename='my_creature.png')